"""unitcell / exporter の一覧とオプションスキーマ。"""

from __future__ import annotations

from typing import Any, Dict

from genice3.cli.meta_schema import exporter_options_schema, unitcell_options_schema
from genice3.plugin import get_exporter_format_rows, scan
from genice3.service.exceptions import UnknownPluginError, ValidationError


def list_unitcells() -> Dict[str, Any]:
    data = scan("unitcell")
    return {
        "unitcells": {
            "system": data.get("system", []),
            "extra": data.get("extra", []),
            "local": data.get("local", []),
        },
        "descriptions": data.get("desc", {}),
    }


def list_exporters() -> Dict[str, Any]:
    rows = get_exporter_format_rows(markdown_name=False)
    return {"exporters": rows}


def get_unitcell_options(name: str) -> Dict[str, Any]:
    try:
        return unitcell_options_schema(name)
    except ValueError as e:
        raise ValidationError(str(e)) from e
    except ImportError as e:
        raise UnknownPluginError(str(e)) from e


def get_exporter_options(name: str) -> Dict[str, Any]:
    try:
        return exporter_options_schema(name)
    except ValueError as e:
        raise ValidationError(str(e)) from e
    except ImportError as e:
        raise UnknownPluginError(str(e)) from e
