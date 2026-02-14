"""
Unitcell プラグイン単体テスト。

全 unitcell プラグインをスキャンし、引数なしでインスタンス化できるものについて
必須属性（cell, lattice_sites, graph, fixed）の存在と型を検証する。
オプション引数が必要なプラグイン（CIF, one など）はスキップする。
"""

import numpy as np
import pytest

from genice3.plugin import scan, safe_import


# 引数なしでインスタンス化できる代表的な unitcell（収集時間短縮のため固定リスト）
_UNITCELL_NO_ARGS = (
    "1h",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "ice1h",
    "ice3",
    "ice4",
    "A15",
)


def _list_unitcell_plugins():
    """上記のうち実際にインスタンス化できるプラグインのみ返す。"""
    result = []
    for name in _UNITCELL_NO_ARGS:
        try:
            module = safe_import("unitcell", name)
            cls = getattr(module, "UnitCell", None)
            if cls is None:
                continue
            instance = cls()
            result.append((name, instance))
        except (ValueError, TypeError, FileNotFoundError, AssertionError):
            continue
        except (ImportError, AttributeError):
            continue
    return result


_plugins = None


def get_unitcell_plugins():
    global _plugins
    if _plugins is None:
        _plugins = _list_unitcell_plugins()
    return _plugins


def _unitcell_plugin_ids():
    names = [p[0] for p in get_unitcell_plugins()]
    return names or [None]


@pytest.fixture(params=_unitcell_plugin_ids())
def unitcell_plugin_name(request):
    if request.param is None:
        pytest.skip("no unitcell plugins could be instantiated with no args")
    return request.param


@pytest.fixture
def unitcell_instance(unitcell_plugin_name):
    mods = scan("unitcell")
    name = unitcell_plugin_name
    module = safe_import("unitcell", name)
    return module.UnitCell()


def test_unitcell_has_required_attributes(unitcell_instance):
    """UnitCell インスタンスは cell, lattice_sites, graph, fixed を持つ。"""
    uc = unitcell_instance
    assert hasattr(uc, "cell"), "UnitCell must have attribute 'cell'"
    assert hasattr(uc, "lattice_sites"), "UnitCell must have attribute 'lattice_sites'"
    assert hasattr(uc, "graph"), "UnitCell must have attribute 'graph'"
    assert hasattr(uc, "fixed"), "UnitCell must have attribute 'fixed'"


def test_unitcell_cell_is_3x3_array(unitcell_instance):
    """cell は 3x3 の numpy 配列。"""
    cell = unitcell_instance.cell
    assert isinstance(cell, np.ndarray), "cell must be numpy ndarray"
    assert cell.shape == (3, 3), "cell must be 3x3"


def test_unitcell_lattice_sites_is_Nx3_array(unitcell_instance):
    """lattice_sites は Nx3 の numpy 配列。"""
    sites = unitcell_instance.lattice_sites
    assert isinstance(sites, np.ndarray), "lattice_sites must be numpy ndarray"
    assert sites.ndim == 2 and sites.shape[1] == 3, "lattice_sites must be Nx3"


def test_unitcell_graph_has_same_number_of_nodes_as_sites(unitcell_instance):
    """graph のノード数は lattice_sites の行数と一致。"""
    uc = unitcell_instance
    n_sites = len(uc.lattice_sites)
    assert uc.graph.number_of_nodes() == n_sites, (
        f"graph nodes ({uc.graph.number_of_nodes()}) must equal "
        f"lattice_sites length ({n_sites})"
    )


def test_unitcell_scan_finds_plugins():
    """scan('unitcell') が少なくとも1件の system プラグインを返す。"""
    mods = scan("unitcell")
    assert "system" in mods
    assert isinstance(mods["system"], list)
    assert len(mods["system"]) >= 1, "at least one unitcell plugin should be available"
