"""
genice3/exporter/yaplot.py の parse_options / 原子半径ヘルパのテスト。
"""

import sys
from pathlib import Path

import pytest

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from genice3.exporter.yaplot import (
    BUILTIN_RELATIVE_RADII,
    DEFAULT_SCALE,
    atom_size,
    element_symbol,
    parse_options,
)


def test_builtin_oxygen_is_unity():
    assert BUILTIN_RELATIVE_RADII["O"] == pytest.approx(1.0)
    assert BUILTIN_RELATIVE_RADII["H"] < 1.0
    assert BUILTIN_RELATIVE_RADII["Cl"] > 1.0


def test_default_scale_is_half_oxygen_vdw_nm():
    # Bondi O = 1.52 Å → 0.152 nm; default display = half of that.
    assert DEFAULT_SCALE == pytest.approx(0.076)


def test_atom_size_defaults():
    assert atom_size("O") == pytest.approx(DEFAULT_SCALE)
    assert atom_size("H") == pytest.approx(
        DEFAULT_SCALE * BUILTIN_RELATIVE_RADII["H"]
    )


def test_atom_size_relative_multiplier():
    assert atom_size("O", relatives={"O": 2.0}) == pytest.approx(DEFAULT_SCALE * 2.0)
    assert atom_size("H", scale=0.04, relatives={"H": 0.5}) == pytest.approx(
        0.04 * BUILTIN_RELATIVE_RADII["H"] * 0.5
    )


def test_element_symbol():
    assert element_symbol("OW") == "O"
    assert element_symbol("HW1") == "H"
    assert element_symbol("Na") == "Na"
    assert element_symbol("CL") == "Cl"
    assert element_symbol("CH4") == "C"


def test_parse_options_h_and_scale():
    processed, unprocessed = parse_options({"H": 0.8, "scale": 0.05, "guest": "A12=me"})
    assert processed["scale"] == pytest.approx(0.05)
    assert processed["radii"] == {"H": 0.8}
    assert "guest" in unprocessed
    assert "H" not in unprocessed


def test_parse_options_element_keys_and_radii_dict():
    processed, unprocessed = parse_options(
        {
            "O": 1.2,
            "radii": {"H": 0.5, "Cl": 1.1},
            "C": 0.9,
            "water_model": "tip4p",
        }
    )
    assert processed["water_model"] == "tip4p"
    assert processed["radii"]["O"] == pytest.approx(1.2)
    assert processed["radii"]["H"] == pytest.approx(0.5)
    assert processed["radii"]["Cl"] == pytest.approx(1.1)
    assert processed["radii"]["C"] == pytest.approx(0.9)
    assert unprocessed == {}


def test_parse_options_water_alias():
    processed, unprocessed = parse_options({"water": "4site"})
    assert processed == {"water_model": "4site"}


def test_parse_options_empty():
    processed, unprocessed = parse_options({})
    assert processed == {}
    assert unprocessed == {}
