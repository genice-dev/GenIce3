"""genice3.webapi（FastAPI）。依存が無い環境ではスキップ。"""

import json

import pytest

pytest.importorskip("fastapi")

from fastapi.testclient import TestClient

from genice3.webapi import create_app


@pytest.fixture
def client():
    return TestClient(create_app())


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_meta_unitcells(client):
    r = client.get("/v1/meta/unitcells")
    assert r.status_code == 200
    data = r.json()
    assert "unitcells" in data
    assert "system" in data["unitcells"]
    assert "1h" in data["unitcells"]["system"]


def test_meta_exporters(client):
    r = client.get("/v1/meta/exporters")
    assert r.status_code == 200
    rows = r.json()["exporters"]
    assert isinstance(rows, list)
    assert any("gromacs" in str(row).lower() for row in rows)


def test_meta_unitcell_options_cif(client):
    r = client.get("/v1/meta/unitcells/CIF/options")
    assert r.status_code == 200
    data = r.json()
    assert data["unitcell"] == "CIF"
    names = {o["name"] for o in data["specific_options"]}
    assert "file" in names
    assert "examples" in data and "yaml" in data["examples"]


def test_meta_unitcell_options_unknown(client):
    r = client.get("/v1/meta/unitcells/__no_such_plugin__/options")
    assert r.status_code == 404


def test_meta_exporter_options_gromacs(client):
    r = client.get("/v1/meta/exporters/gromacs/options")
    assert r.status_code == 200
    data = r.json()
    assert data["exporter"] == "gromacs"
    assert "format_desc" in data
    assert "suboptions" in data["format_desc"]
    assert data["media_type"] == "text/plain"


def test_meta_exporter_options_unknown(client):
    r = client.get("/v1/meta/exporters/__no_such_exporter__/options")
    assert r.status_code == 404


def test_generate_minimal_yaml(client):
    yaml = """unitcell: 1h
genice3:
  rep: [1, 1, 1]
exporter: gromacs
"""
    r = client.post(
        "/v1/generate",
        content=yaml.encode("utf-8"),
        headers={"Content-Type": "application/x-yaml"},
    )
    assert r.status_code == 200, r.text
    assert r.headers.get("content-type", "").startswith("application/json")
    data = r.json()
    assert data["meta"]["seed"] == 1
    assert data["meta"]["unitcell"] == "1h"
    assert data["media_type"] == "text/plain"
    assert len(data["content"]) > 200


def test_generate_json_object_same_content(client):
    yaml = """unitcell: 1h
genice3:
  rep: [1, 1, 1]
exporter: gromacs
"""
    r = client.post("/v1/generate/json", json={"config_yaml": yaml})
    assert r.status_code == 200, r.text
    r2 = client.post(
        "/v1/generate",
        content=yaml.encode("utf-8"),
        headers={"Content-Type": "text/plain"},
    )
    # GRO 先頭行に command_line が入るので座標部分だけ比較
    body1 = "\n".join(r.json()["content"].splitlines()[1:])
    body2 = "\n".join(r2.json()["content"].splitlines()[1:])
    assert body1 == body2
    assert r.json()["meta"]["seed"] == r2.json()["meta"]["seed"]


def test_generate_json_config_object(client):
    r = client.post(
        "/v1/generate/json",
        json={
            "config": {
                "unitcell": "1h",
                "genice3": {"rep": [1, 1, 1], "seed": 9},
                "exporter": "gromacs",
            }
        },
    )
    assert r.status_code == 200, r.text
    assert r.json()["meta"]["seed"] == 9


def test_generate_raw_json_body(client):
    body = {
        "unitcell": "1h",
        "genice3": {"rep": [1, 1, 1]},
        "exporter": "gromacs",
    }
    r = client.post(
        "/v1/generate",
        content=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    assert r.status_code == 200, r.text
    assert r.json()["meta"]["seed"] == 1


def test_generate_toml(client):
    toml = """
unitcell = "1h"
exporter = "gromacs"
[genice3]
rep = [1, 1, 1]
seed = 5
"""
    r = client.post(
        "/v1/generate",
        content=toml.encode("utf-8"),
        headers={"Content-Type": "application/toml"},
    )
    assert r.status_code == 200, r.text
    assert r.json()["meta"]["seed"] == 5


def test_generate_invalid_missing_unitcell(client):
    r = client.post("/v1/generate", content=b"genice3:\n  rep: [1,1,1]\n")
    assert r.status_code == 400
