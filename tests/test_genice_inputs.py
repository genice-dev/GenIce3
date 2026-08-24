"""Regression tests for GenIce3 Input wrapping (setters, cache, list_*)."""

import numpy as np
import pytest

from genice3 import ConfigurationError
from genice3.genice import GenIce3
from genice3.plugin import UnitCell
from genice3.unitcell import UnitCell as UnitCellBase


def test_unset_unitcell_raises():
    genice = GenIce3()
    with pytest.raises(ConfigurationError, match="Unitcell is not set"):
        _ = genice.unitcell


def test_unitcell_constructor_kwarg():
    uc = UnitCell("1h")
    genice = GenIce3(unitcell=uc)
    assert genice.unitcell is uc


def test_set_unitcell_by_name():
    genice = GenIce3()
    genice.set_unitcell("A15")
    assert isinstance(genice.unitcell, UnitCellBase)
    graph = genice.graph
    assert graph.number_of_nodes() > 0


def test_unitcell_string_assignment_rejected():
    genice = GenIce3()
    with pytest.raises(ConfigurationError, match="must be a UnitCell instance"):
        genice.unitcell = "A15"


def test_invalid_kwargs():
    with pytest.raises(ConfigurationError, match="Invalid keyword arguments"):
        GenIce3(invalid_option="test")


def test_setter_clears_cache():
    genice = GenIce3(unitcell=UnitCell("1h"))
    _ = genice.graph
    assert "graph" in genice.engine.cache
    genice.seed = 2
    assert genice.engine.cache == {}


def test_list_reactive_properties_keys():
    genice = GenIce3()
    all_derived = set(genice.list_all_reactive_properties())
    public_derived = set(genice.list_public_reactive_properties())
    settable = set(genice.list_settable_reactive_properties())
    public_settable = set(genice.list_public_settable_reactive_properties())

    assert {"graph", "digraph", "lattice_sites", "orientations"} <= all_derived
    assert public_derived == {
        "graph",
        "digraph",
        "lattice_sites",
        "orientations",
    }
    assert "replica_vector_labels" in all_derived
    assert "replica_vector_labels" not in public_derived

    assert "unitcell" in settable
    assert "bjerrum_L_edges" in settable
    assert "unitcell" in public_settable
    assert "bjerrum_L_edges" not in public_settable
    assert "graph" not in settable

    public_api = set(GenIce3.get_public_api_properties())
    assert public_derived <= public_api
    assert public_settable <= public_api
    assert public_api == public_derived | public_settable


def test_set_replication_matrix_matches_assignment():
    genice = GenIce3()
    genice.set_replication_matrix([[2, 0, 0], [0, 2, 0], [0, 0, 2]])
    np.testing.assert_array_equal(
        genice.replication_matrix, np.array([[2, 0, 0], [0, 2, 0], [0, 0, 2]])
    )
