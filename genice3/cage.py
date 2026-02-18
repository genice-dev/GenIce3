"""
Utility functions for genice3
"""

import numpy as np
from dataclasses import dataclass
import string
from logging import getLogger

import networkx as nx
from cycless import center_of_graph
from cycless.cycles import cycles_iter
from cycless.polyhed import cage_to_graph, polyhedra_iter
from graphstat import GraphStat


@dataclass
class CageSpec:
    label: str  # A12, etc.
    faces: str  # 5^12 6^2, etc.
    graph: nx.Graph  # labels of water constituting the cage

    def to_json_capable_data(self):
        return {
            "label": self.label,
            "faces": self.faces,
            "nodes": [int(x) for x in self.graph],
        }

    def __repr__(self) -> str:
        return (
            f"CageSpec(label={self.label!r}, "
            f"faces={self.faces!r}, "
            f"n_nodes={self.graph.number_of_nodes()})"
        )

    def __str__(self) -> str:
        return f"{self.label} ({self.faces}) {self.graph.number_of_nodes()} nodes"


@dataclass
class CageSpecs:
    specs: list[CageSpec]
    positions: np.ndarray  # in fractional coordinates

    def to_json_capable_data(self):
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

    def site_to_cage_indices(self, site: int) -> list[int]:
        """
        格子サイトが属するケージのインデックスリストを返す。
        水分子は通常4つのケージに属する。
        """
        return [i for i, spec in enumerate(self.specs) if site in spec.graph]


def _assign_label(basename, labels):
    enum = 0
    label = f"A{basename}"
    while label in labels:
        char = string.ascii_lowercase[enum]
        label = f"A{basename}{char}"
        enum += 1
    return label


def _make_cage_expression(ring_ids, ringlist):
    ringcount = [0 for i in range(9)]
    for ring in ring_ids:
        ringcount[len(ringlist[ring])] += 1
    index = []
    for i in range(9):
        if ringcount[i] > 0:
            index.append(f"{i}^{ringcount[i]}")
    index = " ".join(index)
    return index


def assess_cages(graph, node_frac):
    """Assess cages from  the graph topology.

    Args:
        graph (graph-like): HB network
        node_frac (np.Array): Fractional positions of the nodes
    """
    logger = getLogger()

    # Prepare the list of rings
    # taking the positions in PBC into account.
    ringlist = [
        [int(x) for x in ring]
        for ring in cycles_iter(nx.Graph(graph), 8, pos=node_frac)
    ]

    MaxCageSize = 22
    cage_fracs = []
    # data storage of the found cages
    db = GraphStat()
    labels = set()
    g_id2label = dict()

    # Detect cages and classify
    cages = [cage for cage in polyhedra_iter(ringlist, MaxCageSize)]
    cage_graphs = [cage_to_graph(cage, ringlist) for cage in cages]
    cage_fracs = [center_of_graph(g, node_frac) for g in cage_graphs]
    if len(cage_fracs) == 0:
        logger.info("    No cages detected.")

    cagespecs = []
    for cage, g in zip(cages, cage_graphs):
        cagesize = len(g)
        graph_id = db.query_id(g)
        # if it is a new cage type
        if graph_id < 0:
            # new type!
            # register the last query
            graph_id = db.register()

            # prepare a new label
            label = _assign_label(cagesize, labels)
            g_id2label[graph_id] = label
            labels.add(label)

            # cage expression
        else:
            label = g_id2label[graph_id]
        faces = _make_cage_expression(cage, ringlist)
        cagespecs.append(CageSpec(label=label, faces=faces, graph=g))
        # print(f"{label=}, {faces=}, {ringlist=}")
        # print([len(ringlist[ring]) for ring in cage])

    return CageSpecs(specs=cagespecs, positions=np.array(cage_fracs))
