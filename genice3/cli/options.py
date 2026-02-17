"""
genice3 CLI のオプション定義と解釈

基底オプション（--seed, --rep 等）とプラグイン用オプション（-g, -G 等）をここで一元管理する。
pool_parser は汎用のパースのみ担当し、具体的なオプション名・短縮形・説明は持たない。

- GENICE3_OPTION_DEFS: CLI で認識するオプション一覧（PoolBasedParser に渡す）
- parse_base_options: パーサーから渡された辞書を型変換（pool_parser の base プラグインから呼ばれる）
- extract_genice_args: 基底オプション辞書から GenIce3(...) に渡す kwargs を組み立てる
"""

from logging import getLogger
from typing import Dict, Any, List, Optional, Set, Tuple
import numpy as np

from genice3.cli.pool_parser import (
    OptionDef,
    parse_options_generic,
    parse_bracketed_plugin,
    OPTION_TYPE_FLAG,
    OPTION_TYPE_STRING,
    OPTION_TYPE_TUPLE,
    OPTION_TYPE_KEYVALUE,
)
from genice3.cli.validator import (
    validate_seed,
    validate_replication_factors,
    validate_depol_loop,
    validate_target_polarization,
    validate_replication_matrix,
    validate_spot_ion_dict,
    validate_parsed_options as _validate_parsed_options,
)
from genice3.unitcell import ion_processor
from genice3.genice import ConfigurationError, ShowUsageError, GuestSpec
from genice3.plugin import safe_import
from genice3.molecule import Molecule


# =============================================================================
# genice3 のオプション定義（ヘルプ文・短縮形・メタ変数はここで一元管理）
# =============================================================================

_HELP_VERSION = "Show the version and exit."
_HELP_DEBUG = "Enable debug mode."
_HELP_DEPOL_LOOP = (
    "Number of iterations for the depolarization optimization loop. "
    "Larger values may improve the quality of the hydrogen bond network. Default is 1000."
)
_HELP_TARGET_POLARIZATION = (
    "Target polarization vector (three floats: Px Py Pz). "
    "The dipole optimization will aim to make the net polarization close to this value. "
    "Example: --target_polarization 0 0 0 (default)."
)
_HELP_REPLICATION_MATRIX = (
    "Replication matrix as 9 integers (3x3 matrix). "
    "This matrix defines how the unit cell is replicated to create the supercell. "
    "The first row (p, q, r) specifies that the new a' axis direction is represented as pa+qb+rc "
    "using the original unit cell's basis vectors (a, b, c). "
    "Similarly, the second row (s, t, u) specifies that the b' axis direction is sa+tb+uc, "
    "and the third row defines the c' axis. "
    "For example, --replication_matrix 0 1 0  1 0 0  0 0 1 swaps the a and b axes of the unit cell. "
    "Another example, --replication_matrix 1 1 0  1 -1 0  0 0 1 transforms the unit cell such that "
    "a'=a+b and b'=a-b. If not specified, replication_factors is used instead."
)
_HELP_REPLICATION_FACTORS = (
    "Repeat the unit cell along a, b, and c axes. "
    "For example, --rep 2 2 2 creates a 2x2x2 supercell. "
    "This is a convenient shortcut for diagonal replication matrices."
)
_HELP_SEED = (
    "Random seed for guest molecule placement and other stochastic processes. "
    "Using the same seed will produce reproducible results."
)
_HELP_EXPORTER = "Exporter plugin name (e.g., 'gromacs' or 'gromacs[options]')."
_HELP_SPOT_ANION = (
    "Specify anion replacing the specified water molecule. "
    "Format: WATER_INDEX=ION_NAME, where WATER_INDEX is the index of the water molecule and ION_NAME is the anion name. "
    "Examples: -a 13=Cl (place Cl- in cage 13), -a 32=Br (place Br- in cage 32). "
    "Multiple spot anions can be specified with multiple -a options."
)
_HELP_SPOT_CATION = (
    "Specify cation replacing the specified water molecule. "
    "Format: WATER_INDEX=ION_NAME, where WATER_INDEX is the index of the water molecule and ION_NAME is the cation name. "
    "Examples: -c 13=Na (place Na+ in cage 13), -c 32=K (place K+ in cage 32). "
    "Multiple spot cations can be specified with multiple -c options."
)
_HELP_CONFIG = (
    "Path to a YAML configuration file. "
    "Settings from the config file will be overridden by command-line arguments. "
    "See documentation for the config file format."
)
_HELP_GUEST = (
    "Specify guest molecules for each cage type. "
    "Format: CAGE_LABEL=GUEST_SPEC, e.g. A12=me, A12=me+et*0.5. "
    "Multiple cage types can be specified with multiple -g options."
)
_HELP_SPOT_GUEST = (
    "Specify guest molecule at a specific cage index. "
    "Format: CAGE_INDEX=MOLECULE_NAME, e.g. 0=me, 5=4site. "
    "Multiple spot guests can be specified with multiple -G options."
)


# 長い形式 (--xxx) はパーサーがすべて受け取り、base に無いキーは plugin_cmdline_options に回る。
# ここに載せるのは (1) 基底オプション と (2) 短縮形 (-x) を持つものだけ。
# ルール: プラグインでは短縮形は原則使わない（衝突しやすいため）。新規プラグインは --long_only でよい。
GENICE3_OPTION_DEFS: Tuple[OptionDef, ...] = (
    OptionDef(
        "debug",
        short="-D",
        is_flag=True,
        level="base",
        parse_type=OPTION_TYPE_FLAG,
        help_text=_HELP_DEBUG,
    ),
    OptionDef(
        "seed",
        short="-s",
        level="base",
        parse_type=OPTION_TYPE_STRING,
        metavar="INTEGER",
        help_text=_HELP_SEED,
        parse_validator=validate_seed,
    ),
    OptionDef(
        "spot_anion",
        short="-a",
        level="base",
        parse_type=OPTION_TYPE_KEYVALUE,
        metavar="TEXT",
        help_text=_HELP_SPOT_ANION,
        parse_validator=lambda v: validate_spot_ion_dict(v, "spot_anion"),
    ),
    OptionDef(
        "spot_cation",
        short="-c",
        level="base",
        parse_type=OPTION_TYPE_KEYVALUE,
        metavar="TEXT",
        help_text=_HELP_SPOT_CATION,
        parse_validator=lambda v: validate_spot_ion_dict(v, "spot_cation"),
    ),
    OptionDef(
        "config", short="-C", level="base", metavar="PATH", help_text=_HELP_CONFIG
    ),
    OptionDef(
        "exporter", short="-e", level="base", metavar="TEXT", help_text=_HELP_EXPORTER
    ),
    OptionDef(
        "guest",
        short="-g",
        level="base",
        parse_type=OPTION_TYPE_KEYVALUE,
        metavar="TEXT",
        help_text=_HELP_GUEST,
    ),
    OptionDef(
        "spot_guest",
        short="-G",
        level="base",
        parse_type=OPTION_TYPE_KEYVALUE,
        metavar="TEXT",
        help_text=_HELP_SPOT_GUEST,
    ),
    OptionDef(
        "help", short="-h", level="base", help_text="Show this message and exit."
    ),
    OptionDef("version", short="-V", level="base", help_text=_HELP_VERSION),
    OptionDef(
        "rep",
        max_values=3,
        level="base",
        parse_type=OPTION_TYPE_TUPLE,
        metavar="INT INT INT",
        help_text=_HELP_REPLICATION_FACTORS,
        help_format="--rep, --replication_factors INT INT INT",
        parse_validator=validate_replication_factors,
    ),
    OptionDef(
        "replication_factors",
        max_values=3,
        level="base",
        parse_type=OPTION_TYPE_TUPLE,
        metavar="INT INT INT",
        help_text=_HELP_REPLICATION_FACTORS,
        help_format="--rep, --replication_factors INT INT INT",
        parse_validator=validate_replication_factors,
    ),
    OptionDef(
        "replication_matrix",
        level="base",
        parse_type=OPTION_TYPE_TUPLE,
        metavar="INT INT INT INT INT INT INT INT INT",
        help_text=_HELP_REPLICATION_MATRIX,
        parse_validator=validate_replication_matrix,
    ),
    OptionDef(
        "depol_loop",
        level="base",
        parse_type=OPTION_TYPE_STRING,
        metavar="INTEGER",
        help_text=_HELP_DEPOL_LOOP,
        parse_validator=validate_depol_loop,
    ),
    OptionDef(
        "target_polarization",
        level="base",
        parse_type=OPTION_TYPE_TUPLE,
        metavar="FLOAT FLOAT FLOAT",
        help_text=_HELP_TARGET_POLARIZATION,
        parse_validator=validate_target_polarization,
    ),
)

BASE_HELP_ORDER: Tuple[str, ...] = (
    "help",
    "version",
    "debug",
    "depol_loop",
    "target_polarization",
    "replication_matrix",
    "replication_factors",
    "seed",
    "exporter",
    "guest",
    "spot_guest",
    "spot_anion",
    "spot_cation",
    "config",
)


def get_option_def(name: str) -> Optional[OptionDef]:
    """名前に対応する OptionDef を返す。無ければ None。"""
    for d in GENICE3_OPTION_DEFS:
        if d.name == name:
            return d
    return None


def format_option_for_help(def_: OptionDef) -> str:
    """ヘルプ用のオプション書式文字列を組み立てる（例: '-s, --seed INTEGER'）。"""
    if def_.help_format is not None:
        return def_.help_format
    if def_.short:
        opt = f"{def_.short}, --{def_.name}"
    else:
        opt = f"--{def_.name}"
    if def_.metavar:
        opt += " " + def_.metavar
    return opt


def get_base_level_options(option_defs: Tuple[OptionDef, ...]) -> Set[str]:
    """OptionDef の列から基底レベルで扱うキー集合を返す（unitcell / exporter を含む）。"""
    return {d.name for d in option_defs if d.level == "base"} | {
        "unitcell",
        "exporter",
    }


def validate_parsed_options(base_options: Dict[str, Any]) -> None:
    """パース済み base_options に対して parse_validator を実行する。"""
    _validate_parsed_options(base_options, GENICE3_OPTION_DEFS)


# =============================================================================
# spot_cation / spot_anion の角括弧形式パース（--group サブオプション対応）
# =============================================================================


def _parse_group_option(value: Any) -> Dict[int, str]:
    """--group の値を cage_id=group_name の辞書に変換する。"""
    result: Dict[int, str] = {}
    items = [value] if isinstance(value, str) else value
    if isinstance(items, dict):
        return {int(k): str(v) for k, v in items.items()}
    for item in items if isinstance(items, (list, tuple)) else [items]:
        if isinstance(item, str) and "=" in item:
            cage_id_str, group_name = item.split("=", 1)
            result[int(cage_id_str.strip())] = group_name.strip()
    return result


def _process_spot_ion_option(
    raw_value: Any,
) -> Tuple[Dict[str, str], Dict[int, Dict[int, str]]]:
    """
    spot_cation / spot_anion の生の値を処理。
    角括弧形式 [0=N --group 23=methyl 17=methyl] および単純形式 0=Na に対応。

    Returns:
        (ions_dict, groups_dict)
        ions_dict: {"0": "Na", "35": "K"}
        groups_dict: {0: {23: "methyl", 17: "methyl"}}  (site -> {cage_id -> group_name})
    """
    ions: Dict[str, str] = {}
    groups: Dict[int, Dict[int, str]] = {}

    def process_item(item: Any) -> None:
        if (
            isinstance(item, str)
            and item.strip().startswith("[")
            and item.strip().endswith("]")
        ):
            assignment, subopts = parse_bracketed_plugin(item.strip())
            label_str, ion_name = assignment.split("=", 1)
            label_str = label_str.strip()
            ions[label_str] = ion_name.strip()
            if "group" in subopts:
                group_dict = _parse_group_option(subopts["group"])
                if group_dict:
                    groups[int(label_str)] = group_dict
        elif isinstance(item, str) and "=" in item:
            label_str, ion_name = item.split("=", 1)
            ions[label_str.strip()] = ion_name.strip()

    if isinstance(raw_value, dict):
        for k, v in raw_value.items():
            if isinstance(v, dict) and "group" in v:
                ions[str(k)] = str(v.get("ion", v.get("name", v)))
                groups[int(k)] = _parse_group_option(v["group"])
            else:
                ions[str(k)] = str(v)
    else:
        items = [raw_value] if isinstance(raw_value, str) else raw_value
        for item in items if isinstance(items, (list, tuple)) else [items]:
            process_item(item)

    return ions, groups


# =============================================================================
# 基底オプションの型変換と GenIce3 引数への変換
# =============================================================================


def parse_guest_option(arg: dict) -> Dict[str, List[GuestSpec]]:
    """guest オプションの辞書を GuestSpec の辞書に変換する。"""
    logger = getLogger("guest_processor")
    logger.info(f"{arg=}")
    result: Dict[str, List[GuestSpec]] = {}
    for cage, guest_specs in arg.items():
        logger.info(f"{cage=} {guest_specs=}")
        result[cage] = []
        total_occupancy = 0.0
        for guest_spec in guest_specs.split("+"):
            if "*" in guest_spec:
                occupancy_str, molecule = guest_spec.split("*")
                occupancy = float(occupancy_str)
            else:
                molecule = guest_spec
                occupancy = 1.0
            mol = safe_import("molecule", molecule).Molecule()
            result[cage].append(GuestSpec(mol, occupancy))
            total_occupancy += occupancy
        if total_occupancy > 1.0:
            raise ConfigurationError(
                f"Total occupancy of cage {cage} is greater than 1.0"
            )
    logger.debug(f"{result=}")
    return result


def parse_spot_guest_option(arg: dict) -> Dict[int, Molecule]:
    """spot_guest オプションの辞書を Molecule の辞書に変換する。"""
    result: Dict[int, Molecule] = {}
    for label, molecule in arg.items():
        if label == "?":
            raise ShowUsageError(
                "Use '?' to display cage information. "
                "This option triggers a survey of cage positions and types."
            )
        result[int(label) if isinstance(label, str) else label] = safe_import(
            "molecule", molecule
        ).Molecule()
    return result


def parse_base_options(options: Dict[str, Any]) -> Dict[str, Any]:
    """
    基底レベルオプションを型変換して統合する。

    動的プラグインチェーン（pool_parser）の base プラグインとして呼ばれる。
    対象は GENICE3_OPTION_DEFS のうち level=="base" かつ parse_type が指定されている
    オプション（rep は build_options_dict で replication_factors に正規化されるため除外）。
    オプションの追加・削除は GENICE3_OPTION_DEFS の編集のみ行えばよい。

    Args:
        options: 基底レベルにマージ済みのオプション辞書（YAML やコマンドライン由来）。

    Returns:
        型変換済みオプションと未処理オプションを統合した辞書。
    """
    # もともと parse_base_options で型変換していた9個だけ渡す。rep は build_options_dict で replication_factors に正規化されるため含めない。
    # spot_cation, spot_anion は角括弧形式対応のため別処理
    option_specs = {
        d.name: d.parse_type
        for d in GENICE3_OPTION_DEFS
        if d.level == "base"
        and d.parse_type is not None
        and d.name not in ("rep", "spot_cation", "spot_anion")
    }

    def to_int(x):
        if isinstance(x, int):
            return x
        return int(x)

    def to_int_tuple(x):
        if isinstance(x, (tuple, list)):
            return tuple(int(v) for v in x)
        return (int(x),)

    def to_bool(x):
        if isinstance(x, bool):
            return x
        if isinstance(x, str):
            return x.lower() in ("true", "1", "yes", "on")
        return bool(x)

    def to_float3(x):
        if isinstance(x, np.ndarray) and x.shape == (3,):
            return np.asarray(x, dtype=float)
        if isinstance(x, (tuple, list)) and len(x) == 3:
            return np.array([float(v) for v in x])
        raise ValueError(f"target_polarization must be 3 numbers, got: {x}")

    post_processors = {
        "seed": to_int,
        "depol_loop": to_int,
        "replication_factors": to_int_tuple,
        "target_polarization": to_float3,
    }

    processed, unprocessed = parse_options_generic(
        options, option_specs, post_processors
    )

    # spot_cation, spot_anion の角括弧形式パース（--group サブオプション対応）
    for key in ("spot_cation", "spot_anion"):
        if key in options:
            ions, groups = _process_spot_ion_option(options[key])
            processed[key] = ions
            if groups:
                processed[f"{key}_groups"] = groups

    # guest, spot_guest を GuestSpec/Molecule の辞書に変換
    if "guest" in processed and processed["guest"]:
        processed["guest"] = parse_guest_option(processed["guest"])
    if "spot_guest" in processed and processed["spot_guest"]:
        processed["spot_guest"] = parse_spot_guest_option(processed["spot_guest"])

    # processed を後にマージして、spot_cation/spot_anion の処理結果が unprocessed を上書きする
    return {**unprocessed, **processed}


def extract_genice_args(base_options: Dict[str, Any]) -> Dict[str, Any]:
    """
    基底オプション辞書から GenIce3 コンストラクタに渡す kwargs を組み立てる。

    Args:
        base_options: parse_base_options 済みの基底オプション辞書（result["base_options"]）

    Returns:
        GenIce3 に渡す kwargs（depol_loop, replication_matrix, target_pol, seed, spot_anions, spot_cations, guests, spot_guests）
    """
    seed = base_options.get("seed", 1)
    depol_loop = base_options.get("depol_loop", 1000)
    target_polarization = base_options.get("target_polarization")
    if target_polarization is None:
        target_polarization = np.array([0.0, 0.0, 0.0])

    spot_anion_dict = base_options.get("spot_anion", {}) or {}
    spot_cation_dict = base_options.get("spot_cation", {}) or {}
    spot_anion_dict = ion_processor(spot_anion_dict)
    spot_cation_dict = ion_processor(spot_cation_dict)

    guests = base_options.get("guest", {}) or {}
    spot_guests = base_options.get("spot_guest", {}) or {}

    replication_matrix = base_options.get("replication_matrix")
    replication_factors = base_options.get("replication_factors", (1, 1, 1))
    if replication_matrix is None:
        if isinstance(replication_factors, list):
            replication_factors = tuple(replication_factors)
        replication_matrix = np.diag(replication_factors)
    else:
        replication_matrix = np.array(replication_matrix)

    spot_cation_groups = base_options.get("spot_cation_groups", {}) or {}

    return {
        "depol_loop": depol_loop,
        "replication_matrix": replication_matrix,
        "target_pol": target_polarization,
        "seed": seed,
        "spot_anions": spot_anion_dict,
        "spot_cations": spot_cation_dict,
        "guests": guests,
        "spot_guests": spot_guests,
        "spot_cation_groups": spot_cation_groups,
    }
