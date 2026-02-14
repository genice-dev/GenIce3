"""
Molecule プラグイン単体テスト。

全 molecule プラグインをスキャンし、インスタンス化できるものについて
必須属性（sites, labels, name）の存在と型を検証する。
"""

import numpy as np
import pytest

from genice3.plugin import scan, safe_import


def _list_molecule_plugins():
    """引数なしでインスタンス化を試し、成功するプラグイン名のリストを返す。"""
    result = []
    mods = scan("molecule")
    for name in mods["system"]:
        try:
            module = safe_import("molecule", name)
            cls = getattr(module, "Molecule", None)
            if cls is None:
                continue
            instance = cls()
            result.append((name, instance))
        except (ValueError, TypeError, FileNotFoundError, ImportError, UnboundLocalError):
            # 必須引数あり・ファイル依存・未実装などでインスタンス化できないプラグインはスキップ
            continue
    return result


_plugins = None


def get_molecule_plugins():
    global _plugins
    if _plugins is None:
        _plugins = _list_molecule_plugins()
    return _plugins


def _molecule_plugin_ids():
    names = [p[0] for p in get_molecule_plugins()]
    return names or [None]


@pytest.fixture(params=_molecule_plugin_ids())
def molecule_plugin_name(request):
    if request.param is None:
        pytest.skip("no molecule plugins could be instantiated with no args")
    return request.param


@pytest.fixture
def molecule_instance(molecule_plugin_name):
    module = safe_import("molecule", molecule_plugin_name)
    return module.Molecule()


def test_molecule_has_required_attributes(molecule_instance):
    """Molecule インスタンスは sites, labels, name を持つ。"""
    mol = molecule_instance
    assert hasattr(mol, "sites"), "Molecule must have attribute 'sites'"
    assert hasattr(mol, "labels"), "Molecule must have attribute 'labels'"
    assert hasattr(mol, "name"), "Molecule must have attribute 'name'"


def test_molecule_sites_is_Nx3_array(molecule_instance):
    """sites は Nx3 の配列（numpy または list）。空の場合は 0 要素。"""
    sites = molecule_instance.sites
    arr = np.asarray(sites, dtype=float)
    if arr.size == 0:
        assert arr.ndim in (1, 2), "empty sites must be 0-dim or (0,3)"
    else:
        assert arr.ndim == 2 and arr.shape[1] == 3, "sites must be Nx3"


def test_molecule_labels_matches_sites_length(molecule_instance):
    """labels の長さは sites の行数と一致。"""
    mol = molecule_instance
    assert len(mol.labels) == len(mol.sites), (
        f"labels length ({len(mol.labels)}) must equal sites length ({len(mol.sites)})"
    )


def test_molecule_name_is_non_empty_string(molecule_instance):
    """name は非空文字列。"""
    name = molecule_instance.name
    assert isinstance(name, str), "name must be str"
    assert len(name) >= 1, "name must be non-empty"


def test_molecule_scan_finds_plugins():
    """scan('molecule') が少なくとも1件の system プラグインを返す。"""
    mods = scan("molecule")
    assert "system" in mods
    assert isinstance(mods["system"], list)
    assert len(mods["system"]) >= 1, "at least one molecule plugin should be available"
