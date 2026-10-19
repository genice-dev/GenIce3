"""genice3.mcp（stdio MCP）。依存が無い環境ではスキップ。"""

import pytest

pytest.importorskip("mcp")

from genice3.mcp import (
    generate_tool,
    get_exporter_options_tool,
    list_unitcells_tool,
)


def test_list_unitcells_tool():
    data = list_unitcells_tool()
    assert "1h" in data["unitcells"]["system"]


def test_get_exporter_options_tool():
    data = get_exporter_options_tool("gromacs")
    assert data.get("error") is not True
    assert data["media_type"] == "text/plain"


def test_generate_tool_yaml():
    result = generate_tool(
        """unitcell: 1h
genice3:
  rep: [1, 1, 1]
exporter: gromacs
"""
    )
    assert result.get("error") is not True
    assert result["meta"]["seed"] == 1
    assert len(result["content"]) > 200


def test_generate_tool_dict():
    result = generate_tool(
        {
            "unitcell": "1h",
            "genice3": {"rep": [1, 1, 1], "seed": 2},
            "exporter": "gromacs",
        }
    )
    assert result["meta"]["seed"] == 2


def test_generate_tool_validation_error():
    result = generate_tool("genice3:\n  rep: [1, 1, 1]\n")
    assert result.get("error") is True
    assert result["error_type"] == "ValidationError"
