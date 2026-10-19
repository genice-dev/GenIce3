"""設定のパース（YAML 正、互換 TOML / JSON）→ CLI と同形の ``result``。"""

from __future__ import annotations

import json
import tomllib
from typing import Any, Dict, Mapping, Optional, Union

import yaml

from genice3.cli.runner import flatten_yaml_config, parsed_result_from_merged
from genice3.service.exceptions import ParseError, ValidationError

ConfigInput = Union[str, Mapping[str, Any]]


def normalize_content_type(content_type: Optional[str]) -> Optional[str]:
    """``application/json; charset=utf-8`` → ``application/json``。"""
    if not content_type:
        return None
    return content_type.split(";", 1)[0].strip().lower()


def detect_format(content_type: Optional[str], text: str) -> str:
    """返す値は ``yaml`` / ``toml`` / ``json``。"""
    ct = normalize_content_type(content_type)
    if ct in ("application/json", "text/json"):
        return "json"
    if ct in ("application/toml", "text/toml"):
        return "toml"
    if ct in ("application/x-yaml", "application/yaml", "text/yaml", "text/x-yaml"):
        return "yaml"
    # 判別不能: 先頭を軽く見て、だめなら yaml
    stripped = text.lstrip()
    if stripped.startswith("{") or stripped.startswith("["):
        return "json"
    return "yaml"


def _load_mapping(text: str, fmt: str) -> Dict[str, Any]:
    try:
        if fmt == "json":
            raw = json.loads(text)
        elif fmt == "toml":
            raw = tomllib.loads(text)
        else:
            raw = yaml.safe_load(text)
    except (json.JSONDecodeError, yaml.YAMLError, tomllib.TOMLDecodeError) as e:
        raise ParseError(f"Failed to parse {fmt}: {e}") from e
    except Exception as e:
        raise ParseError(f"Failed to parse {fmt}: {e}") from e

    if raw is None:
        raise ParseError(f"Empty {fmt} configuration")
    if not isinstance(raw, dict):
        raise ParseError(f"Configuration root must be a mapping, got {type(raw).__name__}")
    return raw


def config_dict_from_input(
    source: ConfigInput,
    *,
    content_type: Optional[str] = None,
) -> Dict[str, Any]:
    """文字列または dict から、セクション付き（またはフラット可）の設定 dict を得る。"""
    if isinstance(source, Mapping):
        return dict(source)
    if not isinstance(source, str):
        raise ParseError(f"Unsupported config type: {type(source).__name__}")
    fmt = detect_format(content_type, source)
    return _load_mapping(source, fmt)


def parsed_result_from_config(
    source: ConfigInput,
    *,
    content_type: Optional[str] = None,
) -> Dict[str, Any]:
    """設定 → CLI ``parse_argv`` 後と同形の ``result``。"""
    raw = config_dict_from_input(source, content_type=content_type)
    # すでにフラット（unitcell がスカラー）でも flatten は通る
    flat = flatten_yaml_config(raw)
    if not flat.get("unitcell"):
        # トップレベルに unitcell キーが無い場合、flatten 後も空
        raise ValidationError("unitcell is required")
    return parsed_result_from_merged(flat)
