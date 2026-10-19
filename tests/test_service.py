"""genice3.service（HTTP/MCP 非依存）。"""

import json

import pytest

from genice3.service import (
    ValidationError,
    UnknownPluginError,
    generate,
    get_exporter_options,
    list_unitcells,
    parsed_result_from_config,
)
from genice3.service.media_type import resolve_media_type


def test_list_unitcells_has_1h():
    data = list_unitcells()
    assert "1h" in data["unitcells"]["system"]


def test_exporter_media_type_gromacs():
    data = get_exporter_options("gromacs")
    assert data["media_type"] == "text/plain"
    assert data["format_desc"].get("media_type") == "text/plain"


def test_resolve_media_type_from_extension():
    assert resolve_media_type({"extension": ".json"}) == "application/json"
    assert resolve_media_type({"media_type": "text/html", "extension": ".json"}) == "text/html"


def test_parse_yaml_and_generate():
    yaml = """unitcell: 1h
genice3:
  rep: [1, 1, 1]
exporter: gromacs
"""
    result = generate(yaml)
    assert result["meta"]["seed"] == 1
    assert result["meta"]["unitcell"] == "1h"
    assert result["meta"]["exporter"] == "gromacs"
    assert result["media_type"] == "text/plain"
    assert len(result["content"]) > 200


def test_parse_json_dict():
    cfg = {
        "unitcell": "1h",
        "genice3": {"rep": [1, 1, 1], "seed": 7},
        "exporter": "gromacs",
    }
    result = generate(cfg)
    assert result["meta"]["seed"] == 7


def test_parse_json_text():
    text = json.dumps(
        {
            "unitcell": "1h",
            "genice3": {"rep": [1, 1, 1]},
            "exporter": "gromacs",
        }
    )
    result = generate(text, content_type="application/json")
    assert result["meta"]["seed"] == 1


def test_parse_toml_text():
    text = """
unitcell = "1h"
exporter = "gromacs"
[genice3]
rep = [1, 1, 1]
seed = 3
"""
    result = generate(text, content_type="application/toml")
    assert result["meta"]["seed"] == 3


def test_missing_unitcell():
    with pytest.raises(ValidationError):
        parsed_result_from_config("genice3:\n  rep: [1, 1, 1]\n")


def test_unknown_exporter_options():
    with pytest.raises(UnknownPluginError):
        get_exporter_options("__no_such_exporter__")
