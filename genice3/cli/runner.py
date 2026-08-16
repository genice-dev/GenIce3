"""
option_parser を使った CLI 実行フロー。
argv → パース → プラグイン dispatch → result（genice.py が期待する形）。
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Tuple

from genice3.cli.option_parser import (
    looks_like_option,
    parse_options,
    scalarize_single_item_lists,
    structure_for_display,
)
from genice3.cli.options import (
    base_options_from_new_structure,
    get_common_unitcell_option_names,
    get_short_to_long_option_names,
    missing_argument_message,
    validate_required_option_arguments,
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
        "pol_loop_1",
        "pol_loop_2",
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


def flatten_yaml_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """トップに unitcell / genice3 等がある YAML 根オブジェクトを、CLI と同じフラット構造に正規化する。"""
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
    # 上で展開済みのセクション名は載せない（genice3 が残ると unitcell の未処理扱いになる）
    _section_keys = frozenset({"unitcell", "genice3", "exporter"})
    for k, v in config.items():
        if k in _section_keys:
            continue
        if k not in out:
            out[k] = v
    return out


def load_config_file(yaml_path: str) -> Dict[str, Any]:
    """YAML 設定を読み、option_parser と同じ構造で返す。"""
    if yaml is None:
        return {}
    p = Path(yaml_path)
    if not p.exists():
        return {}
    with open(p, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f) or {}
    return flatten_yaml_config(config if isinstance(config, dict) else {})


def load_config_text(text: str) -> Dict[str, Any]:
    """YAML 文字列を読み、:func:`load_config_file` と同じフラット構造で返す（Web API 等用）。"""
    if yaml is None:
        return {}
    raw = yaml.safe_load(text)
    if not raw:
        return {}
    if not isinstance(raw, dict):
        return {}
    return flatten_yaml_config(raw)


def parsed_result_from_yaml_text(yaml_text: str) -> Dict[str, Any]:
    """YAML 本文から CLI の :func:`parse_argv` 後と同形の ``result`` を返す（Web API 用の短縮形）。"""
    return parsed_result_from_merged(load_config_text(yaml_text))


def _merge_config_cmdline(config: Dict[str, Any], cmdline: Dict[str, Any]) -> Dict[str, Any]:
    """設定ファイルをコマンドラインで上書き。"""
    out = dict(config)
    for k, v in cmdline.items():
        if v is not None and (k != "unitcell" or v != ""):
            out[k] = v
    return out


_EXPORTER_NAME_REQUIRED = (
    "-e / --exporter にはプラグイン名が必要です（例: -e gromacs）"
)


def _exporter_plugin_name(name: Any) -> str:
    """exporter プラグイン名を正規化する。空なら ValueError。"""
    text = str(name).strip()
    if not text:
        raise ValueError(_EXPORTER_NAME_REQUIRED)
    return text


def _get_exporter_name_and_options(data: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
    """data["exporter"] から (name, subopts_dict) を返す。

    未指定（キーなし / None）なら既定の gromacs。
    ``-e`` / ``--exporter`` を書いたのに名前が空なら ValueError。
    """
    raw = data.get("exporter")
    if raw is None:
        return "gromacs", {}
    items = raw if isinstance(raw, list) else [raw]
    if not items:
        raise ValueError(_EXPORTER_NAME_REQUIRED)
    first = items[0]
    if isinstance(first, dict):
        if not first:
            raise ValueError(_EXPORTER_NAME_REQUIRED)
        (name, subopts), = first.items()
        return _exporter_plugin_name(name), dict(subopts)
    return _exporter_plugin_name(first), {}


def parsed_result_from_merged(merged: Dict[str, Any]) -> Dict[str, Any]:
    """フラットなマージ済み設定（CLI の display 相当）から、genice が使う result 辞書を組み立てる。

    CLI（:func:`parse_argv`）と Web 等（YAML → flatten → ここ）で共有する。
    """
    unitcell_name = str(merged.get("unitcell", ""))
    if not unitcell_name:
        return {
            "base_options": {},
            "unitcell": {"name": None, "options": {}, "processed": {}},
            "exporter": {"name": "gromacs", "options": {}, "processed": {}},
            "plugin_chain": [],
        }

    base_options = base_options_from_new_structure(merged)

    unitcell_options = {
        k: merged[k]
        for k in merged
        if k not in _BASE_KEYS and k not in ("unitcell", "exporter") and k != "H"
    }

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
            common = get_common_unitcell_option_names()
            unitcell_processed = {
                k: v for k, v in unitcell_options.items() if k in common
            }
            unitcell_unprocessed = {
                k: v for k, v in unitcell_options.items() if k not in common
            }
    except Exception:
        common = get_common_unitcell_option_names()
        unitcell_processed = {
            k: v for k, v in unitcell_options.items() if k in common
        }
        unitcell_unprocessed = {
            k: v for k, v in unitcell_options.items() if k not in common
        }

    exporter_name, exporter_subopts = _get_exporter_name_and_options(merged)
    if "H" in merged:
        exporter_subopts = {**exporter_subopts, "H": merged["H"]}
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
            if (
                i >= len(args)
                or looks_like_option(args[i])
                or args[i].startswith(":")
            ):
                raise RuntimeError(
                    f"オプションのパースに失敗しました: {missing_argument_message('config')}"
                )
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
            # 短いオプション名 (-e → exporter 等) を long 名に正規化
            for short, long_name in get_short_to_long_option_names().items():
                if short in parsed:
                    parsed.setdefault(long_name, parsed.pop(short))
            validate_required_option_arguments(parsed)
        except ValueError as e:
            raise RuntimeError(f"オプションのパースに失敗しました: {e}") from e
        display = structure_for_display(parsed)
        merged = _merge_config_cmdline(config, display)

    try:
        return parsed_result_from_merged(merged)
    except ValueError as e:
        raise RuntimeError(f"オプションのパースに失敗しました: {e}") from e


def validate_result(result: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """unitcell 名が指定されているか検証。"""
    errors = []
    if not result.get("unitcell", {}).get("name"):
        errors.append("unitcell名が指定されていません")
    return (len(errors) == 0, errors)
