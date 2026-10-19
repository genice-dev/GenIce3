"""
GenIce3 の stdio MCP サーバ。共有ロジックは ``genice3.service``。

依存: ``pip install "genice3[mcp]"`` 後に ``genice3-mcp``。
Cursor 等のクライアントが子プロセスとして起動し、stdin/stdout で話す。
常時 HTTP サーバは不要。
"""

from __future__ import annotations

import json
from typing import Any, Optional, Union

from genice3.service import (
    ServiceError,
    generate as service_generate,
    get_exporter_options,
    get_unitcell_options,
    list_exporters,
    list_unitcells,
)

try:
    from mcp.server.mcpserver import MCPServer
except ModuleNotFoundError as e:  # pragma: no cover
    raise ModuleNotFoundError(
        "The MCP server needs the mcp package. Install it with: pip install 'genice3[mcp]'"
    ) from e


mcp = MCPServer(
    "genice3",
    instructions=(
        "GenIce3 builds hydrogen-disordered ice and clathrate hydrate structures. "
        "Use list_unitcells / list_exporters, then get_*_options, then generate with "
        "the same YAML (or JSON object) schema as the CLI `-Y` file. "
        "Omitted seed defaults to 1. Topological defects are not available via MCP."
    ),
)


def _error_payload(exc: ServiceError) -> dict[str, Any]:
    return {
        "error": True,
        "error_type": type(exc).__name__,
        "message": exc.message,
        "detail": exc.detail,
        "http_status_hint": exc.http_status,
    }


@mcp.tool(
    name="list_unitcells",
    description="List available unit cell (lattice) plugin names and descriptions.",
)
def list_unitcells_tool() -> dict[str, Any]:
    return list_unitcells()


@mcp.tool(
    name="list_exporters",
    description="List available exporter plugins (output formats).",
)
def list_exporters_tool() -> dict[str, Any]:
    return list_exporters()


@mcp.tool(
    name="get_unitcell_options",
    description="Option schema for one unit cell (specific + common options, examples).",
)
def get_unitcell_options_tool(name: str) -> dict[str, Any]:
    try:
        return get_unitcell_options(name)
    except ServiceError as e:
        return _error_payload(e)


@mcp.tool(
    name="get_exporter_options",
    description="Metadata for one exporter, including media_type of dumps() output.",
)
def get_exporter_options_tool(name: str) -> dict[str, Any]:
    try:
        return get_exporter_options(name)
    except ServiceError as e:
        return _error_payload(e)


@mcp.tool(
    name="generate",
    description=(
        "Generate a structure. `config` is either a YAML/TOML/JSON string or a dict "
        "with the same keys as the CLI `-Y` file (unitcell / genice3 / exporter). "
        "Returns {meta, content, media_type}. seed defaults to 1 when omitted."
    ),
)
def generate_tool(
    config: Union[str, dict[str, Any]],
    content_type: Optional[str] = None,
) -> dict[str, Any]:
    try:
        return dict(
            service_generate(
                config,
                content_type=content_type,
                command_line="mcp.generate",
            )
        )
    except ServiceError as e:
        return _error_payload(e)


def main() -> None:
    """``genice3-mcp`` コンソールスクリプト（stdio）。"""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
