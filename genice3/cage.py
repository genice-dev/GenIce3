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
    """ケージの仕様。cage_type は "A12" などのケージ種別を表す文字列。"""

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
    """拡大単位胞内の全ケージの位置と仕様。

    specs: 各ケージの CageSpec（cage_type, faces, graph）。
    positions: 分数座標の配列（Nx3）。specs と同順。
    node_to_cage_indices: __post_init__ で生成。ノード番号 → そのノードを含むケージのインデックスリスト。
    """

    specs: list[CageSpec]
    positions: np.ndarray  # in fractional coordinates

    def __post_init__(self) -> None:
        """ノード番号 → ケージ番号の逆引き辞書を生成。"""
        self.node_to_cage_indices: dict[int, list[int]] = {}
        for cage_idx, spec in enumerate(self.specs):
            for node in spec.graph:
                self.node_to_cage_indices.setdefault(int(node), []).append(cage_idx)

    def to_json_capable_data(self) -> dict:
        """JSON シリアライズ用の辞書を返す。キーはケージインデックス、値は frac_pos と specs。"""
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
    """未使用のケージタイプ名（A12, A12a など）を生成する。"""
    enum = 0
    cage_type = f"A{basename}"
    while cage_type in existing_types:
        char = string.ascii_lowercase[enum]
        cage_type = f"A{basename}{char}"
        enum += 1
    return cage_type


def _make_cage_expression(ring_ids: list, ringlist: list) -> str:
    """ケージを構成するリングのサイズから "5^12 6^2" のような面表現文字列を生成する。"""
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
    graph: nx.Graph, node_frac: np.ndarray
) -> CageSpecs:
    """水素結合グラフとノードの分数座標からケージを検出・分類し、CageSpecs を返す。

    Args:
        graph: 水素結合ネットワーク（無向グラフ）。
        node_frac: ノードの分数座標（Nx3）。

    Returns:
        検出されたケージの位置（分数座標）と仕様（CageSpec のリスト）。
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
    existing_cage_types: set[str] = set()
    g_id_to_cage_type: dict[int, str] = {}

    # Detect cages and classify
    cages = [cage for cage in polyhedra_iter(ringlist, MaxCageSize)]
    cage_graphs = [cage_to_graph(cage, ringlist) for cage in cages]
    cage_fracs = [center_of_graph(g, node_frac) for g in cage_graphs]
    if len(cage_fracs) == 0:
        logger.info("    No cages detected.")

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
