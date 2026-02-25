"""
option_parser を使った CLI 実行フロー。
argv → パース → プラグイン dispatch → result（genice.py が期待する形）。
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Tuple

from genice3.cli.option_parser import (
    parse_options,
    scalarize_single_item_lists,
    structure_for_display,
)
from genice3.cli.options import (
    base_options_from_new_structure,
    get_common_unitcell_option_names,
    get_short_to_long_option_names,
)
from genice3.plugin import safe_import

try:
    import yaml
except ImportError:
    yaml = None

# 基底オプションのキー（runner で unitcell/exporter に渡さない）
_BASE_KEYS = frozenset(
    {
        "debug",
        "seed",
        "rep",
        "replication_factors",
        "replication_matrix",
        "depol_loop",
        "target_polarization",
        "config",
        "exporter",
        "guest",
        "spot_guest",
        "spot_anion",
        "spot_cation",
    }
)


def load_config_file(yaml_path: str) -> Dict[str, Any]:
    """YAML 設定を読み、option_parser と同じ構造で返す。"""
    if yaml is None:
        return {}
    p = Path(yaml_path)
    if not p.exists():
        return {}
    with open(p, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f) or {}
    # トップに unitcell / genice3 等がある形式を、フラットな option 構造に正規化
    out: Dict[str, Any] = {}
    if "unitcell" in config:
        uc = config["unitcell"]
        if isinstance(uc, dict):
            out["unitcell"] = uc.get("name", "")
            for k, v in uc.items():
                if k != "name":
                    out[k] = v
        else:
            out["unitcell"] = uc
    if "genice3" in config:
        out.update(config["genice3"])
    if "exporter" in config:
        out["exporter"] = config["exporter"]
    # その他のトップレベルキー（unitcell 用 file, osite や shift, density 等）も渡す
    for k, v in config.items():
        if k not in out:
            out[k] = v
    return out


def _merge_config_cmdline(config: Dict[str, Any], cmdline: Dict[str, Any]) -> Dict[str, Any]:
    """設定ファイルをコマンドラインで上書き。"""
    out = dict(config)
    for k, v in cmdline.items():
        if v is not None and (k != "unitcell" or v != ""):
            out[k] = v
    return out


def _get_exporter_name_and_options(data: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
    """data["exporter"] から (name, subopts_dict) を返す。"""
    raw = data.get("exporter")
    if raw is None:
        return "gromacs", {}
    items = raw if isinstance(raw, list) else [raw]
    if not items:
        return "gromacs", {}
    first = items[0]
    if isinstance(first, dict):
        (name, subopts), = first.items()
        return str(name), dict(subopts)
    return str(first), {}


def parse_argv(argv: List[str]) -> Dict[str, Any]:
    """
    argv（sys.argv[1:]）をパースし、genice.py の get_result() と同じ形の辞書を返す。
    """
    args = list(argv)
    config: Dict[str, Any] = {}
    i = 0
    while i < len(args):
        if args[i] in ("--config", "-Y"):
            i += 1
            if i < len(args):
                config = load_config_file(args[i])
            i += 1
        else:
            i += 1

    # --config 以外を並べて option_parser に渡す
    line_parts = []
    i = 0
    while i < len(argv):
        if argv[i] in ("--config", "-Y"):
            i += 2
            continue
        line_parts.append(argv[i])
        i += 1
    line = " ".join(line_parts)

    if not line_parts or line_parts[0].startswith("-") or line_parts[0].startswith(":"):
        # コマンドラインに unitcell が無くても --config で読んだ設定があれば使う
        if config and config.get("unitcell"):
            merged = _merge_config_cmdline(config, {})
        else:
            return {
                "base_options": {},
                "unitcell": {"name": None, "options": {}, "processed": {}},
                "exporter": {"name": "gromacs", "options": {}, "processed": {}},
                "plugin_chain": [],
            }
    else:
        try:
            parsed = parse_options(line)
        except ValueError as e:
            raise RuntimeError(f"オプションのパースに失敗しました: {e}") from e
        # 短いオプション名 (-e → exporter 等) を long 名に正規化
        for short, long_name in get_short_to_long_option_names().items():
            if short in parsed:
                parsed.setdefault(long_name, parsed.pop(short))
        display = structure_for_display(parsed)
        merged = _merge_config_cmdline(config, display)

    unitcell_name = str(merged.get("unitcell", ""))
    if not unitcell_name:
        return {
            "base_options": {},
            "unitcell": {"name": None, "options": {}, "processed": {}},
            "exporter": {"name": "gromacs", "options": {}, "processed": {}},
            "plugin_chain": [],
        }

    # 基底オプション
    base_options = base_options_from_new_structure(merged)

    # unitcell に渡すオプション（新構造のまま）
    unitcell_options = {
        k: merged[k]
        for k in merged
        if k not in _BASE_KEYS and k not in ("unitcell", "exporter")
    }

    # unitcell プラグインの parse_options（新構造を受け取る）
    # モジュール級 parse_options を優先（CIF の file/osite 等はこちらで処理）
    unitcell_processed: Dict[str, Any] = {}
    unitcell_unprocessed: Dict[str, Any] = {}
    try:
        uc_module = safe_import("unitcell", unitcell_name)
        if hasattr(uc_module, "parse_options"):
            unitcell_processed, unitcell_unprocessed = uc_module.parse_options(
                unitcell_options
            )
        elif hasattr(uc_module, "UnitCell") and hasattr(
            uc_module.UnitCell, "parse_options"
        ):
            unitcell_processed, unitcell_unprocessed = uc_module.UnitCell.parse_options(
                unitcell_options
            )
        else:
            # parse_options がない unitcell: 共通オプションのみ消費、残りは unprocessed（警告対象）
            common = get_common_unitcell_option_names()
            unitcell_processed = {
                k: v for k, v in unitcell_options.items() if k in common
            }
            unitcell_unprocessed = {
                k: v for k, v in unitcell_options.items() if k not in common
            }
    except Exception:
        # 読み込み失敗時も同様に共通のみ消費、残りは unprocessed
        common = get_common_unitcell_option_names()
        unitcell_processed = {
            k: v for k, v in unitcell_options.items() if k in common
        }
        unitcell_unprocessed = {
            k: v for k, v in unitcell_options.items() if k not in common
        }

    # exporter
    exporter_name, exporter_subopts = _get_exporter_name_and_options(merged)
    exporter_processed: Dict[str, Any] = {}
    exporter_unprocessed: Dict[str, Any] = {}
    try:
        ex_module = safe_import("exporter", exporter_name)
        if hasattr(ex_module, "parse_options"):
            exporter_processed, exporter_unprocessed = ex_module.parse_options(
                exporter_subopts
            )
    except Exception:
        pass

    return {
        "base_options": base_options,
        "unitcell": {
            "name": unitcell_name,
            "options": unitcell_options,
            "processed": unitcell_processed,
            "unprocessed": unitcell_unprocessed,
        },
        "exporter": {
            "name": exporter_name,
            "options": exporter_subopts,
            "processed": exporter_processed,
            "unprocessed": exporter_unprocessed,
        },
        "plugin_chain": [],
    }


def validate_result(result: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """unitcell 名が指定されているか検証。"""
    errors = []
    if not result.get("unitcell", {}).get("name"):
        errors.append("unitcell名が指定されていません")
    return (len(errors) == 0, errors)
