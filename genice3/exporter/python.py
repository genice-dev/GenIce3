# coding: utf-8
"""
Exporter that outputs a unitcell plugin (Python module) whose unit cell
is the current supercell. The generated plugin can be used as
a GenIce3 unitcell with rep=1x1x1 to reproduce the same structure.
"""

import importlib
import json
import sys
from io import TextIOWrapper
from typing import Any, Dict, Optional, Tuple
import types

import numpy as np
import networkx as nx

from genice3.genice import GenIce3

format_desc = {
    "aliases": ["py", "python"],
    "application": "Python unitcell plugin",
    "extension": ".py",
    "water": "none",
    "solute": "none",
    "hb": "graph",
    "remarks": "Outputs a unitcell plugin where the supercell becomes the new unit cell; desc documents base plugin, replication matrix, and invoking CLI when available.",
    "suboptions": (
        "name: optional label stored in desc (e.g. match the saved .py stem); "
        "omit when redirecting stdout—nothing is invented by default."
    ),
}


def parse_options(options: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """exporter サブオプション ``name`` をスカラー文字列に正規化する。"""
    processed: Dict[str, Any] = {}
    unprocessed = dict(options)
    if "name" in unprocessed:
        raw = unprocessed.pop("name")
        while isinstance(raw, (list, tuple)) and len(raw) == 1:
            raw = raw[0]
        if raw is not None and str(raw).strip() != "":
            processed["name"] = str(raw)
    return processed, unprocessed


def _format_array(arr: np.ndarray, indent: str = "    ") -> str:
    """Format numpy array as Python list of lists for source code."""
    lst = arr.tolist()
    lines = [
        "np.array([",
        *[f"{indent}[{', '.join(repr(x) for x in row)}]," for row in lst],
        f"{indent}])",
    ]
    return "\n".join(lines)


def _unitcell_plugin_name(uc: Any) -> str:
    """unitcell インスタンスからプラグイン名（例: 1c, DOH）を推定する。"""
    mod = type(uc).__module__
    prefix = "genice3.unitcell."
    return mod[len(prefix) :] if mod.startswith(prefix) else mod


def _try_base_unitcell_catalog_brief(plugin_name: str) -> Optional[str]:
    """基底プラグインの desc['brief'] が取れれば返す（失敗時は None）。"""
    try:
        m = importlib.import_module(f"genice3.unitcell.{plugin_name}")
    except Exception:
        return None
    d = getattr(m, "desc", None)
    if not isinstance(d, dict):
        return None
    b = d.get("brief")
    if b is None:
        return None
    s = str(b).strip()
    return s or None


def _build_export_desc(
    genice: GenIce3,
    name: Optional[str],
    command_line: Optional[str],
) -> Tuple[str, str]:
    """生成モジュールの desc 用 (brief, usage) を組み立てる。

    ``name`` は exporter の明示オプションのみ（未指定なら desc に出力名を捏造しない）。
    """
    uc = genice.unitcell
    plugin_name = _unitcell_plugin_name(uc)
    base_brief = _try_base_unitcell_catalog_brief(plugin_name)
    rm = np.asarray(genice.replication_matrix, dtype=int).reshape(3, 3)
    n_rep = int(round(abs(float(np.linalg.det(rm)))))
    n_sites = len(genice.lattice_sites)
    n_edges = genice.graph.number_of_edges()
    n_prim = len(uc.lattice_sites)

    if name:
        brief = (
            f"Expanded supercell saved as a unitcell module (declared name {name!r}); "
            f"built from unitcell {plugin_name!r}; "
            f"{n_rep} primitive cells, {n_sites} lattice sites."
        )
    else:
        brief = (
            f"Expanded supercell saved as a unitcell module; "
            f"built from unitcell {plugin_name!r}; "
            f"{n_rep} primitive cells, {n_sites} lattice sites."
        )

    usage_lines = [
        "Expanded supercell from GenIce3, saved as a standalone unitcell "
        "(use replication 1×1×1 to recover this structure).",
        f"Source unitcell plugin: {plugin_name!r} "
        f"(module {type(uc).__module__!r}, class {type(uc).__name__!r}).",
    ]
    if not name:
        usage_lines.append(
            "No exporter :name was given (typical for stdout redirection). "
            "The saved filename is unknown to GenIce3; pass "
            "`--exporter python :name STEM` if you want that label recorded in desc."
        )
    if base_brief:
        usage_lines.append(f"Catalog brief of the source unitcell: {base_brief}")
    usage_lines.append(
        f"Replication matrix (3×3 integers; |det| = {n_rep} = number of "
        "primitive cells in the supercell):"
    )
    for row in rm.tolist():
        usage_lines.append(f"  {row!r}")
    usage_lines.append(
        f"Expanded HB graph: {n_sites} nodes, {n_edges} edges "
        f"({n_prim} sites per primitive cell)."
    )
    if command_line:
        usage_lines.append(f"genice3 command line when exported: {command_line}")

    usage = "\n".join(usage_lines)
    return brief, usage


def _desc_to_python_source(brief: str, usage: str) -> str:
    """desc 辞書を、ソースに埋め込み安全な形で文字列化する。"""
    obj = {"ref": {}, "brief": brief, "usage": usage}
    return "desc = " + json.dumps(obj, ensure_ascii=False, indent=4)


def _format_graph_edges(G: nx.Graph) -> str:
    """Format graph edges as Python list of tuples."""
    edges = list(G.edges())
    if not edges:
        return "[]"
    # 1 line per edge if many, else one line
    if len(edges) <= 4:
        return repr(edges)
    parts = [f"        {repr(e)}," for e in edges]
    return "[\n" + "\n".join(parts) + "\n    ]"


def dumps(genice: GenIce3, name: Optional[str] = None, **kwargs: Any) -> str:
    """
    Generate Python source code for a unitcell plugin that defines
    the current supercell as the new unit cell.

    Args:
        genice: GenIce3 instance (after structure is built).
        name: Optional label recorded in ``desc`` (e.g. match the ``.py`` file stem).
            If omitted, ``desc`` does not claim an output filename (stdout use case).
        **kwargs: Optional ``command_line`` (str) is embedded in ``desc["usage"]``
            when present (as set by the genice3 CLI).

    Returns:
        Python source code as a string.

    Raises:
        ValueError: If anion, cation, or guest is defined (this exporter does not output them).
    """
    anions = getattr(genice, "anions", {}) or {}
    cations = getattr(genice, "cations", {}) or {}
    guests = getattr(genice, "guests", {}) or {}
    spot_guests = getattr(genice, "spot_guests", {}) or {}

    if anions or cations:
        raise ValueError(
            "python exporter does not support anion/cation. "
            "Export without spot_anion/spot_cation and without unitcell anion/cation."
        )
    if guests or spot_guests:
        raise ValueError(
            "python exporter does not support guest. "
            "Export without guest/spot_guest."
        )

    # Trigger reactive computation of extended-cell data
    cell = genice.cell
    lattice_sites = genice.lattice_sites
    graph = genice.graph
    fixed = genice.fixed_edges

    cell_str = _format_array(cell)
    sites_str = _format_array(lattice_sites)
    graph_edges_str = _format_graph_edges(graph)
    fixed_edges = list(fixed.edges())
    fixed_str = _format_graph_edges(nx.DiGraph(fixed_edges)) if fixed_edges else "[]"

    cmd = kwargs.get("command_line")
    if cmd is not None and not isinstance(cmd, str):
        cmd = str(cmd)
    export_brief, export_usage = _build_export_desc(genice, name, cmd)
    desc_block = _desc_to_python_source(export_brief, export_usage)
    plugin_name = _unitcell_plugin_name(genice.unitcell)
    rm = np.asarray(genice.replication_matrix, dtype=int).reshape(3, 3)
    n_rep = int(round(abs(float(np.linalg.det(rm)))))

    lines = [
        "# coding: utf-8",
        "# Auto-generated unitcell plugin: supercell as new unit cell",
        "# Generated by GenIce3 exporter python.py",
        f"# Base unitcell plugin: {plugin_name}  |  replication |det| = {n_rep}",
        "",
        "import genice3.unitcell",
        "import numpy as np",
        "import networkx as nx",
        "",
        desc_block,
        "",
        "",
        "class UnitCell(genice3.unitcell.UnitCell):",
        '    """Unit cell identical to the exported supercell (use rep 1×1×1)."""',
        "",
        "    def __init__(self, **kwargs):",
        "        cell = " + cell_str.replace("\n", "\n        "),
        "",
        "        lattice_sites = " + sites_str.replace("\n", "\n        "),
        "",
        "        graph = nx.Graph()",
        "        graph.add_edges_from(" + graph_edges_str + ")",
        "",
        "        fixed = nx.DiGraph()",
        "        fixed.add_edges_from(" + fixed_str + ")",
        "",
        "        super().__init__(",
        "            cell=cell,",
        "            lattice_sites=lattice_sites,",
        '            coord="relative",',
        "            graph=graph,",
        "            fixed=fixed,",
        "            **kwargs,",
        "        )",
        "",
    ]
    return "\n".join(lines)


def supercell_as_unitcell(
    genice: GenIce3, name: Optional[str] = None, **kwargs: Any
) -> Any:
    """
    Create and return a ``UnitCell`` instance whose unit cell is the current supercell.

    The source code generated by the python exporter is not written to a file.
    Instead, it is executed in a temporary in-memory module, and the
    ``UnitCell`` class defined there is used to construct and return the instance.

    Example::

        from genice3.genice import GenIce3
        from genice3.plugin import safe_import

        unitcell = safe_import("unitcell", "A15").UnitCell()
        genice = GenIce3(unitcell=unitcell)
        genice.set_replication_matrix([[1, 1, 0], [-1, 1, 0], [0, 0, 1]])
        reshaped = supercell_as_unitcell(genice, name="A15e")
    """
    # 既存の dumps をそのまま利用してソースコードを得る
    src = dumps(genice, name=name, **kwargs)

    # メモリ上のモジュールを作り、その中で exec する
    suffix = name if name else "supercell"
    module_name = f"_genice3_exported_{suffix}"
    mod = types.ModuleType(module_name)
    exec(src, mod.__dict__)

    if not hasattr(mod, "UnitCell"):
        raise RuntimeError("Generated plugin does not define UnitCell.")

    # 生成された UnitCell をインスタンスとして返す（GenIce3(unitcell=...) で利用可能）
    return mod.UnitCell()


def dump(genice: GenIce3, file: TextIOWrapper = sys.stdout, **options: Any) -> None:
    """Write ``dumps(...)`` to ``file`` (often ``sys.stdout``).

    Equivalent to ``file.write(dumps(genice, **options))``; ``name`` defaults to
    unset so ``desc`` does not invent a label unless ``:name`` was given.
    """
    file.write(dumps(genice, **options))

