"""
genice3/exporter/gromacs.py の parse_options のテスト。

ゲスト指定（guest / spot_guest）は GenIce3 / CLI 側の責務。
gromacs プラグインが処理するのは water_model（別名 water）のみ。
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from genice3.exporter.gromacs import parse_options


def test_parse_options_basic():
    options = {
        "guest": "A12=me",
        "spot_guest": "0=foursite",
        "water_model": "foursite",
        "type": "ice",
    }
    processed, unprocessed = parse_options(options)

    assert processed == {"water_model": "foursite"}
    assert "guest" in unprocessed
    assert "spot_guest" in unprocessed
    assert "type" in unprocessed
    assert "water_model" not in unprocessed


def test_parse_options_water_alias():
    processed, unprocessed = parse_options({"water": "tip4p"})
    assert processed == {"water_model": "tip4p"}
    assert "water" in unprocessed or "water_model" not in unprocessed


def test_parse_options_unprocessed():
    options = {
        "guest": "A12=me",
        "water_model": "foursite",
        "type": "ice",
        "shift": ("0.1", "0.1", "0.1"),
    }
    processed, unprocessed = parse_options(options)

    assert processed == {"water_model": "foursite"}
    assert "guest" in unprocessed
    assert "type" in unprocessed
    assert "shift" in unprocessed


def test_parse_options_empty():
    processed, unprocessed = parse_options({})
    assert processed == {}
    assert unprocessed == {}


def test_parse_options_with_yaml_format():
    """YAML 由来の dict でも water_model のみ処理し、guest は未処理に残す。"""
    options = {
        "guest": {"A12": "me", "A14": "et"},
        "spot_guest": {"0": "foursite"},
        "water_model": "foursite",
    }
    processed, unprocessed = parse_options(options)

    assert processed == {"water_model": "foursite"}
    assert unprocessed["guest"] == {"A12": "me", "A14": "et"}
    assert unprocessed["spot_guest"] == {"0": "foursite"}
