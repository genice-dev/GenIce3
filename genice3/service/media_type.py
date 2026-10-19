"""exporter ``format_desc`` の media_type 宣言と extension からの推定。"""

from __future__ import annotations

from typing import Any, Dict, Mapping, Optional

_EXTENSION_MEDIA_TYPES: Dict[str, str] = {
    ".gro": "text/plain",
    ".cif": "chemical/x-cif",
    ".json": "application/json",
    ".html": "text/html",
    ".htm": "text/html",
    ".xyz": "chemical/x-xyz",
    ".pdb": "chemical/x-pdb",
    ".yap": "text/plain",
    ".py": "text/x-python",
    ".lmp": "text/plain",
    ".data": "text/plain",
}

DEFAULT_MEDIA_TYPE = "text/plain"


def media_type_from_extension(extension: Optional[str]) -> str:
    """ファイル拡張子（先頭ドット付き推奨）から MIME を推定する。"""
    if not extension:
        return DEFAULT_MEDIA_TYPE
    ext = extension if extension.startswith(".") else f".{extension}"
    return _EXTENSION_MEDIA_TYPES.get(ext.lower(), DEFAULT_MEDIA_TYPE)


def resolve_media_type(format_desc: Optional[Mapping[str, Any]]) -> str:
    """``format_desc['media_type']`` があればそれを、なければ ``extension`` から推定。"""
    if not format_desc:
        return DEFAULT_MEDIA_TYPE
    explicit = format_desc.get("media_type")
    if isinstance(explicit, str) and explicit.strip():
        return explicit.strip()
    return media_type_from_extension(
        format_desc.get("extension") if isinstance(format_desc.get("extension"), str) else None
    )


def media_type_for_exporter(exporter_name: str) -> str:
    """exporter プラグイン名から media_type を返す（未ロード時は text/plain）。"""
    try:
        from genice3.plugin import import_plugin_module

        mod = import_plugin_module("exporter", exporter_name)
        fd = getattr(mod, "format_desc", None)
        return resolve_media_type(fd if isinstance(fd, dict) else None)
    except Exception:
        return DEFAULT_MEDIA_TYPE
