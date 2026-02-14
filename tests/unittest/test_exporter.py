"""
Exporter プラグイン単体テスト。

全 exporter プラグインをスキャンし、モジュールが dumps または dump を提供していることを検証する。
実際の出力（dumps の実行）は統合テストに任せる。
"""

import pytest

from genice3.plugin import scan, safe_import


def _list_exporter_plugins():
    """exporter プラグイン名のリストを返す。"""
    mods = scan("exporter")
    return mods["system"]


def _exporter_plugin_ids():
    names = _list_exporter_plugins()
    return names or [None]


@pytest.fixture(params=_exporter_plugin_ids())
def exporter_plugin_name(request):
    if request.param is None:
        pytest.skip("no exporter plugins available")
    return request.param


@pytest.fixture
def exporter_module(exporter_plugin_name):
    return safe_import("exporter", exporter_plugin_name)


def test_exporter_has_dumps_or_dump(exporter_module):
    """Exporter モジュールは dumps / dump / figure のいずれかを提供する。"""
    has_dumps = hasattr(exporter_module, "dumps") and callable(exporter_module.dumps)
    has_dump = hasattr(exporter_module, "dump") and callable(exporter_module.dump)
    has_figure = hasattr(exporter_module, "figure") and callable(exporter_module.figure)
    assert has_dumps or has_dump or has_figure, (
        "exporter module must define callable 'dumps', 'dump', or 'figure'"
    )


def test_exporter_scan_finds_plugins():
    """scan('exporter') が少なくとも1件の system プラグインを返す。"""
    mods = scan("exporter")
    assert "system" in mods
    assert isinstance(mods["system"], list)
    assert len(mods["system"]) >= 1, "at least one exporter plugin should be available"
