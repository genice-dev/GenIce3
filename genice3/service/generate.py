"""設定 → 構造テキスト + メタ情報。"""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version
from io import StringIO
from typing import Any, Dict, Optional, TypedDict

from genice3.cli.engine import run_parsed_result
from genice3.cli.options import extract_genice_args, validate_parsed_options
from genice3.cli.runner import validate_result
from genice3.plugin import PluginNotFoundError
from genice3.service.config import ConfigInput, parsed_result_from_config
from genice3.service.exceptions import (
    GenerationError,
    ParseError,
    ServiceError,
    UnknownPluginError,
    ValidationError,
)
from genice3.service.media_type import media_type_for_exporter


class GenerateMeta(TypedDict, total=False):
    seed: int
    unitcell: str
    exporter: str
    media_type: str
    genice3_version: str
    genice_core_version: Optional[str]
    warnings: list


class GenerateResult(TypedDict):
    meta: GenerateMeta
    content: str
    media_type: str


def _pkg_version(name: str) -> Optional[str]:
    try:
        return version(name)
    except PackageNotFoundError:
        return None


def _prepare_result(result: Dict[str, Any]) -> Dict[str, Any]:
    ok, errors = validate_result(result)
    if not ok:
        raise ValidationError("validation failed", detail={"errors": errors})

    uc_u = result.get("unitcell", {}).get("unprocessed") or {}
    ex_u = result.get("exporter", {}).get("unprocessed") or {}
    if uc_u or ex_u:
        raise ValidationError(
            "Some options were not recognized",
            detail={
                "message": "Some options were not recognized",
                "unitcell_unprocessed": list(uc_u.keys()),
                "exporter_unprocessed": list(ex_u.keys()),
            },
        )

    base = result["base_options"]
    try:
        validate_parsed_options(base)
    except ValueError as e:
        raise ValidationError(str(e)) from e

    unitcell_name = result["unitcell"].get("name")
    if not unitcell_name:
        raise ValidationError("unitcell is required")

    return result


def generate(
    source: ConfigInput | Dict[str, Any],
    *,
    content_type: Optional[str] = None,
    command_line: str = "service.generate",
) -> GenerateResult:
    """設定から構造を生成し、JSON ラップ相当の結果を返す。

    ``source`` がすでに CLI 同形の ``result``（``base_options`` キーあり）ならそれを使う。
    それ以外は YAML/TOML/JSON 文字列または設定 dict として解釈する。
    """
    if isinstance(source, dict) and "base_options" in source and "unitcell" in source:
        result = source
    else:
        try:
            result = parsed_result_from_config(source, content_type=content_type)
        except ServiceError:
            raise
        except Exception as e:
            raise ParseError(str(e)) from e

    result = _prepare_result(result)

    unitcell_name = str(result["unitcell"]["name"])
    exporter_name = result["exporter"]["name"] or "gromacs"
    seed = int(extract_genice_args(result["base_options"]).get("seed", 1))
    media_type = media_type_for_exporter(exporter_name)

    buf = StringIO()
    try:
        run_parsed_result(result, buf, command_line=command_line)
    except PluginNotFoundError as e:
        raise UnknownPluginError(str(e)) from e
    except ImportError as e:
        # safe_import 経由の別名
        raise UnknownPluginError(str(e)) from e
    except (ValueError, TypeError, KeyError) as e:
        raise GenerationError(str(e)) from e
    except ServiceError:
        raise
    except Exception as e:
        raise GenerationError(str(e)) from e

    meta: GenerateMeta = {
        "seed": seed,
        "unitcell": unitcell_name,
        "exporter": exporter_name,
        "media_type": media_type,
        "genice3_version": _pkg_version("genice3") or "unknown",
        "genice_core_version": _pkg_version("genice-core"),
        "warnings": [],
    }
    return {
        "meta": meta,
        "content": buf.getvalue(),
        "media_type": media_type,
    }
