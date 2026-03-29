"""
Utility functions for genice3
"""

from __future__ import annotations

import numpy as np
from dataclasses import dataclass
import string
from logging import getLogger
from typing import TYPE_CHECKING

import networkx as nx
from cycless import center_of_graph
from cycless.cycles import cycles_iter
from cycless.polyhed import cage_to_graph, polyhedra_iter
from graphstat import GraphStat

if TYPE_CHECKING:
    from genice3.genice import GenIce3


@dataclass
class CageSpec:
    """Specification of a cage.

    ``cage_type`` is a string such as "A12" that represents the cage type.
    """

    cage_type: str  # A12, 1b, etc.
    faces: str  # 5^12 6^2, etc.
    graph: nx.Graph  # ケージを構成する水分子ノードのグラフ

    def to_json_capable_data(self) -> dict:
        return {
            "cage_type": self.cage_type,
            "faces": self.faces,
            "nodes": [int(x) for x in self.graph],
        }

    def __repr__(self) -> str:
        return (
            f"CageSpec(cage_type={self.cage_type!r}, "
            f"faces={self.faces!r}, "
            f"n_nodes={self.graph.number_of_nodes()})"
        )

    def __str__(self) -> str:
        return f"{self.cage_type} ({self.faces}) {self.graph.number_of_nodes()} nodes"


@dataclass
class CageSpecs:
    """Positions and specifications of all cages in the expanded unit cell.

    specs: A list of ``CageSpec`` (cage_type, faces, graph) for each cage.
    positions: Array of fractional coordinates (Nx3), in the same order as ``specs``.
    node_to_cage_indices: Mapping generated in ``__post_init__``; node index -> list of cage indices that contain the node.
    """

    specs: list[CageSpec]
    positions: np.ndarray  # in fractional coordinates

    def __post_init__(self) -> None:
        """Build a reverse lookup dictionary from node index to cage indices."""
        self.node_to_cage_indices: dict[int, list[int]] = {}
        for cage_idx, spec in enumerate(self.specs):
            for node in spec.graph:
                self.node_to_cage_indices.setdefault(int(node), []).append(cage_idx)

    def to_json_capable_data(self) -> dict:
        """Return a dict suitable for JSON serialization.

        Keys are cage indices; values contain ``frac_pos`` and ``specs``.
        """
        data = []
        for position, specs in zip(self.positions, self.specs):
            data.append(
                {
                    "frac_pos": position.tolist(),
                    "specs": specs.to_json_capable_data(),
                }
            )
        return dict(enumerate(data))

    def __repr__(self) -> str:
        return (
            f"CageSpecs(n_cages={len(self.specs)}, "
            f"positions_shape={self.positions.shape})"
        )


def _assign_cage_type(basename: int, existing_types: set[str]) -> str:
    """Generate an unused cage type name (e.g., A12, A12a)."""
    enum = 0
    cage_type = f"A{basename}"
    while cage_type in existing_types:
        char = string.ascii_lowercase[enum]
        cage_type = f"A{basename}{char}"
        enum += 1
    return cage_type


def _make_cage_expression(ring_ids: list, ringlist: list) -> str:
    """Generate a face-expression string such as "5^12 6^2".

    The expression is built from the sizes of the rings that form the cage.
    """
    ringcount = [0 for i in range(9)]
    for ring in ring_ids:
        ringcount[len(ringlist[ring])] += 1
    index = []
    for i in range(9):
        if ringcount[i] > 0:
            index.append(f"{i}^{ringcount[i]}")
    index = " ".join(index)
    return index


def assess_cages(
    graph: nx.Graph,
    node_frac: np.ndarray,
    *,
    max_cage_rings: int = 16,
) -> CageSpecs:
    """Detect and classify cages from a hydrogen-bond graph.

    Cages are defined here as quasipolyhedra surrounded by cycles of
    hydrogen bonds [Matsumoto 2007].

    Args:
        graph: Undirected graph representing the hydrogen-bond network.
        node_frac: Fractional coordinates of nodes (Nx3).
        max_cage_rings: Upper bound on the number of rings (faces) per cage
            passed to ``polyhedra_iter`` (default 16, historical GenIce used 22).

    Returns:
        A ``CageSpecs`` object containing the positions (fractional
        coordinates) and specifications (list of ``CageSpec``) of the
        detected cages.
    """
    logger = getLogger()

    # Prepare the list of rings
    # taking the positions in PBC into account.
    ringlist = [
        [int(x) for x in ring]
        for ring in cycles_iter(nx.Graph(graph), 8, pos=node_frac)
    ]
    # logger.info(f"{len(ringlist)=} {graph.number_of_nodes()=}")
    cage_fracs = []
    # data storage of the found cages
    db = GraphStat()
    existing_cage_types: set[str] = set()
    g_id_to_cage_type: dict[int, str] = {}

    # Detect cages and classify
    cages = [cage for cage in polyhedra_iter(ringlist, max_cage_rings)]
    cage_graphs = [cage_to_graph(cage, ringlist) for cage in cages]
    cage_fracs = [center_of_graph(g, node_frac) for g in cage_graphs]
    if len(cage_fracs) == 0:
        logger.info("  No cages detected.")

    cagespecs = []
    for cage, g in zip(cages, cage_graphs):
        cagesize = len(cage)
        graph_id = db.query_id(g)
        # if it is a new cage type
        if graph_id < 0:
            # new type!
            # register the last query
            graph_id = db.register()

            cage_type = _assign_cage_type(cagesize, existing_cage_types)
            g_id_to_cage_type[graph_id] = cage_type
            existing_cage_types.add(cage_type)
        else:
            cage_type = g_id_to_cage_type[graph_id]
        faces = _make_cage_expression(cage, ringlist)
        cagespecs.append(CageSpec(cage_type=cage_type, faces=faces, graph=g))
        # print(f"{label=}, {faces=}, {ringlist=}")
        # print([len(ringlist[ring]) for ring in cage])

    return CageSpecs(specs=cagespecs, positions=np.array(cage_fracs))


def apply_max_cage_rings(genice: GenIce3, max_cage_rings: int | None) -> None:
    """単位胞のケージ検出のリング数上限を変え、GenIce3 のリアクティブキャッシュを無効化する。

    CIF 等で既に ``_cages`` が埋まっている単位胞（``_cages_lazy`` が False）では何もしない。
    """
    if max_cage_rings is None:
        return
    uc = genice.unitcell
    if not getattr(uc, "_cages_lazy", True):
        return
    v = int(max_cage_rings)
    if v < 1:
        raise ValueError(f"max_cage_rings must be >= 1, got {v}")
    uc._max_cage_rings = v
    uc._cages = None
    genice.engine.cache.clear()
