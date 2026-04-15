"""
Web / GUI 向け: unitcell・exporter のオプションスキーマ（CLI の desc / format_desc に基づく）。
"""

from __future__ import annotations

from typing import Any, Dict, List

from genice3.cli.options import get_common_unitcell_option_names
from genice3.plugin import (
    format_unitcell_usage,
    import_plugin_module,
    _normalize_unitcell_options,
)

# get_common_unitcell_option_names と整合させ、ブラウザ用の入力ヒントを付ける
_COMMON_UNITCELL_FIELDS: List[Dict[str, Any]] = [
    {
        "name": "density",
        "kind": "float",
        "help": "Target density (e.g. g/cm³). Supported by many unit cells.",
        "yaml_key": "density",
    },
    {
        "name": "shift",
        "kind": "tuple3",
        "help": "Shift in fractional coordinates (three numbers).",
        "yaml_key": "shift",
    },
    {
        "name": "anion",
        "kind": "keyvalue",
        "help": "Anion at a lattice site in the unit cell (site index → ion).",
        "yaml_key": "anion",
    },
    {
        "name": "cation",
        "kind": "keyvalue",
        "help": "Cation at a lattice site in the unit cell (site index → ion).",
        "yaml_key": "cation",
    },
    {
        "name": "cation_groups",
        "kind": "nested",
        "help": "Group suboption for spot/cell cations when applicable.",
        "yaml_key": "cation_groups",
    },
    {
        "name": "file",
        "kind": "path",
        "help": "File path (e.g. CIF input) when the unit cell plugin uses it.",
        "yaml_key": "file",
    },
    {
        "name": "osite",
        "kind": "string",
        "help": "Oxygen site label or regex (e.g. CIF plugin).",
        "yaml_key": "osite",
    },
]


def common_unitcell_fields_for_ui() -> List[Dict[str, Any]]:
    """多くの unitcell で使える共通オプション（YAML フラット層のキー）。"""
    allowed = get_common_unitcell_option_names()
    return [f for f in _COMMON_UNITCELL_FIELDS if f["name"] in allowed]


def unitcell_options_schema(unitcell_name: str) -> Dict[str, Any]:
    """指定 unitcell の UI 用メタデータ（プラグイン固有 + 共通）。"""
    mod = import_plugin_module("unitcell", unitcell_name)
    desc = getattr(mod, "desc", None) or {}
    brief = str(desc.get("brief", ""))
    raw_opts = desc.get("options") or []
    specific = _normalize_unitcell_options(raw_opts)
    examples = format_unitcell_usage(unitcell_name, raw_opts)
    return {
        "unitcell": unitcell_name,
        "brief": brief,
        "specific_options": specific,
        "common_options": common_unitcell_fields_for_ui(),
        "examples": examples,
    }


def exporter_options_schema(exporter_name: str) -> Dict[str, Any]:
    """指定 exporter の format_desc 等（UI の説明文・サブオプション文字列）。"""
    mod = import_plugin_module("exporter", exporter_name)
    fd = getattr(mod, "format_desc", None)
    format_desc: Dict[str, Any] = dict(fd) if isinstance(fd, dict) else {}
    usage = getattr(mod, "desc", None) or {}
    usage_text = str(usage.get("usage", "")) if isinstance(usage, dict) else ""
    return {
        "exporter": exporter_name,
        "format_desc": format_desc,
        "usage": usage_text,
    }
