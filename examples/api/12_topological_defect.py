"""
トポロジカル欠陥（Bjerrum / イオン欠陥）を座標指定で埋め込むサンプル。

ユーザーがグラフ操作を直接行う形で、欠陥位置を分数座標で指定する。
「座標に一番近い辺（水素結合）を選び、その隣接辺の向きを固定し、残りは GenIce に決めてもらう」
という流れを、以下のヘルパー関数で実現する。

必要な関数（提案）:
  - edge_closeto(frac_pos, graph, lattice_sites, cell) -> (i, j)
      分数座標に最も近い辺（水素結合）を 1 本返す。周期境界を考慮。
  - edges_closeto(frac_positions, graph, lattice_sites, cell) -> list[tuple[int,int]]
      複数座標それぞれについて最も近い辺を返す。frac_positions は (x,y,z) または Nx3。
  - embed_L(graph, edge, fixed) -> None
      L 欠陥を edge に埋め込む。隣接辺の向きを fixed に追加（in-place）。
  - embed_D(graph, edge, fixed) -> None
      D 欠陥を edge に埋め込む。隣接辺の向きを fixed に追加（in-place）。
  - get_base_fixed_edges(genice) -> nx.DiGraph
      単位胞由来の固定エッジを拡大単位胞上で返す。ここに defect 分を足してから
      override_fixed_edges として渡す想定。

注意: GenIce3 の fixed_edges は現在リアクティブ計算のみで、ユーザーが直接代入する
      経路がない。そのため、いずれ __init__(..., override_fixed_edges=...) のような
      オプションを追加するか、fixed_edges タスク内で extra_fixed_edges をマージする
      形の実装が必要。
"""

from __future__ import annotations

from dataclasses import dataclass
from logging import basicConfig, INFO
from typing import List, Tuple, Union

import numpy as np
import networkx as nx
import pairlist as pl

from genice3.genice import GenIce3
from genice3.plugin import UnitCell, Exporter

# -----------------------------------------------------------------------------
# 座標 → 辺
# -----------------------------------------------------------------------------


def edge_closeto(
    frac_pos: Union[Tuple[float, float, float], np.ndarray],
    graph: nx.Graph,
    lattice_sites: np.ndarray,
    cell: np.ndarray,
) -> Tuple[int, int]:
    """分数座標に最も近い辺（水素結合）を 1 本返す。周期境界を考慮。

    「近い」は辺の中点への周期境界付き最短距離で比較する。

    Args:
        frac_pos: 分数座標 (x, y, z) または shape (3,) の配列。
        graph: 拡大単位胞の無向グラフ。
        lattice_sites: 各ノードの分数座標 (Nx3)。
        cell: セル行列（分数→直交）。周期境界の距離計算に使用。

    Returns:
        最も近い辺の (i, j)。i < j の順に正規化して返すかは実装次第。
    """
    p = np.asarray(frac_pos).reshape(3)
    best_edge = None
    best_d2 = np.inf
    for i, j in graph.edges():
        mid = (lattice_sites[i] + lattice_sites[j]) * 0.5
        d = mid - p
        d -= np.floor(d + 0.5)
        d_orth = d @ cell
        d2 = np.dot(d_orth, d_orth)
        if d2 < best_d2:
            best_d2 = d2
            best_edge = (i, j)
    if best_edge is None:
        raise ValueError("graph has no edges")
    return best_edge


def _closest_node_bruteforce(
    frac_pos: np.ndarray,
    lattice_sites: np.ndarray,
    cell: np.ndarray,
) -> int:
    """1 点 frac_pos に周期境界で最も近い格子点のインデックスを返す。総当り。"""
    p = np.asarray(frac_pos).reshape(3)
    best_j = 0
    best_d2 = np.inf
    for j in range(len(lattice_sites)):
        d = lattice_sites[j] - p
        d -= np.floor(d + 0.5)
        d_orth = d @ cell
        d2 = np.dot(d_orth, d_orth)
        if d2 < best_d2:
            best_d2 = d2
            best_j = j
    return best_j


def nodes_closeto(
    frac_pos: Union[Tuple[float, float, float], np.ndarray],
    lattice_sites: np.ndarray,
    cell: np.ndarray,
) -> Union[int, List[int]]:
    """分数座標に最も近いノードを返す。周期境界を考慮。pairs_iter で近傍を絞り、見つからなければ総当り。

    1 点のときは int、複数点のときは list[int] を返す。
    """
    p = np.atleast_2d(frac_pos)  # (1,3) または (N,3)
    n_query = len(p)

    @dataclass
    class Neighbor:
        distance: float
        node: int

    neighbors: dict[int, Neighbor] = {}
    for i, j, d in pl.pairs_iter(p, 0.5, cell, pos2=lattice_sites, distance=True):
        if i not in neighbors or d < neighbors[i].distance:
            neighbors[i] = Neighbor(distance=d, node=j)

    out = []
    for i in range(n_query):
        if i in neighbors:
            out.append(neighbors[i].node)
        else:
            out.append(_closest_node_bruteforce(p[i], lattice_sites, cell))

    return out[0] if n_query == 1 else out


def edges_closeto(
    frac_positions: Union[List[Tuple[float, float, float]], np.ndarray],
    graph: nx.Graph,
    lattice_sites: np.ndarray,
    cell: np.ndarray,
) -> List[Tuple[int, int]]:
    """複数の分数座標それぞれについて、最も近い辺を返す。

    各座標に対して「最も近いノード」を求め、そのノードに接続する辺のうち、
    もう一方の端点がクエリに一番近い辺を選ぶ（辺の中点ではなく、隣接ノードで比較）。
    """
    pos = np.atleast_2d(frac_positions)
    nodes = nodes_closeto(pos, lattice_sites, cell)
    if not isinstance(nodes, list):
        nodes = [nodes]

    edges = []
    for i in range(len(pos)):
        node = nodes[i]
        edge = None
        dd_min = np.inf
        for neighbor in graph.neighbors(node):
            d = lattice_sites[neighbor] - lattice_sites[node]
            d -= np.floor(d + 0.5)
            d /= 2
            center = lattice_sites[node] + d
            d_orth = center - pos[i]
            d_orth -= np.floor(d_orth + 0.5)
            d_orth = d_orth @ cell
            dd = np.dot(d_orth, d_orth)
            if dd < dd_min:
                dd_min = dd
                edge = (node, neighbor)
        if edge is None:
            raise ValueError(f"node {node} has no neighbors")
        edges.append(edge)
    return edges


# -----------------------------------------------------------------------------
# 欠陥の埋め込み（隣接辺の向きを fixed に追加）
# -----------------------------------------------------------------------------


def embed_L(graph: nx.Graph, edge: Tuple[int, int], fixed: nx.DiGraph) -> None:
    """L 欠陥を指定辺に埋め込む。その辺にはプロトンが来ないように隣接辺の向きを fixed に追加する。

    辺 (i, j) の両端 i, j について、i から出る 2 本・j から出る 2 本の水素結合を
    (i,j) を除く形で固定し、(i,j) が空になるようにする。既存の fixed に in-place で追加する。

    Args:
        graph: 拡大単位胞の無向グラフ。
        edge: 欠陥を置く辺 (i, j)。
        fixed: 固定エッジの有向グラフ。ここに隣接辺の向きを追加する。
    """
    i, j = edge
    # i の隣接点のうち j 以外を 2 つ選び、i → それら を fixed に追加
    neis_i = [n for n in graph.neighbors(i) if n != j]
    neis_j = [n for n in graph.neighbors(j) if n != i]
    if len(neis_i) >= 2:
        for n in neis_i[:2]:
            fixed.add_edge(i, n)
    if len(neis_j) >= 2:
        for n in neis_j[:2]:
            fixed.add_edge(j, n)
    # 注: L 欠陥では (i,j) にプロトンを置かないので、(i,j)/(j,i) は fixed に含めない


def embed_D(graph: nx.Graph, edge: Tuple[int, int], fixed: nx.DiGraph) -> None:
    """D 欠陥を指定辺に埋め込む。その辺にプロトンが 2 つ乗るように隣接辺の向きを fixed に追加する。

    通常の有向グラフでは 1 辺に 1 方向しか持てないため、D 欠陥は「両端からその辺に向かう」
    ように隣接辺を固定する形で表現する。すなわち、i の他隣接から i へ、j の他隣接から j へ
    を固定し、結果として (i,j) と (j,i) の両方にプロトンがあるように見える。
    genice_core が 1 辺 2 プロトンを許すかは要確認。許さない場合は別表現が必要。

    Args:
        graph: 拡大単位胞の無向グラフ。
        edge: 欠陥を置く辺 (i, j)。
        fixed: 固定エッジの有向グラフ。ここに隣接辺の向きを追加する。
    """
    i, j = edge
    # D: この辺に「2 本」プロトンがあるようにする → (i,j) と (j,i) を両方 fixed に
    fixed.add_edge(i, j)
    fixed.add_edge(j, i)
    # 隣接辺は、i 側で i に受け入れ 2 本・j 側で j に受け入れ 2 本になるように固定
    neis_i = [n for n in graph.neighbors(i) if n != j]
    neis_j = [n for n in graph.neighbors(j) if n != i]
    if len(neis_i) >= 2:
        for n in neis_i[:2]:
            fixed.add_edge(n, i)
    if len(neis_j) >= 2:
        for n in neis_j[:2]:
            fixed.add_edge(n, j)


# -----------------------------------------------------------------------------
# ベース固定エッジの取得（単位胞由来を拡大単位胞で複製したもの）
# -----------------------------------------------------------------------------


def get_base_fixed_edges(genice: GenIce3) -> nx.DiGraph:
    """単位胞由来の固定エッジを、拡大単位胞のグラフ上に複製した有向グラフを返す。

    ここに embed_L / embed_D で得た固定を足し、GenIce3 に渡す想定。
    GenIce3 に override_fixed_edges が無い場合は、unitcell.fixed を拡大したものだけ返す。

    Args:
        genice: GenIce3 インスタンス（graph, unitcell が利用可能な状態）。

    Returns:
        拡大単位胞全体でのベース固定エッジの有向グラフ。
    """
    from genice3.genice import _replicate_fixed_edges

    g = genice.graph
    uc = genice.unitcell
    nmol = len(uc.lattice_sites)
    return _replicate_fixed_edges(g, uc.fixed, nmol)


# -----------------------------------------------------------------------------
# サンプル本体
# -----------------------------------------------------------------------------

basicConfig(level=INFO)

genice = GenIce3(
    replication_matrix=np.array([[2, 0, 0], [0, 2, 0], [0, 0, 2]]),
)
genice.unitcell = UnitCell("A15")

# グラフ・座標は genice のリアクティブプロパティに依存するので、参照するだけで計算される
g = genice.graph
pos = genice.lattice_sites
cell = genice.cell
celli = np.linalg.inv(cell)

# 欠陥を置きたい位置を分数座標で指定（各 2 点ずつ）
H3O_positions = np.array([[0.0, 0.0, 0.0], [1.0, 1.0, 1.0]]) @ celli  # 2 点 → L を 2 本
OH_positions = np.array([[1.0, 0.0, 0.0], [2.0, 1.0, 1.0]]) @ celli  # 2 点 → D を 2 本

genice.spot_hydroniums = nodes_closeto(H3O_positions, genice.lattice_sites, genice.cell)
genice.spot_hydroxides = nodes_closeto(OH_positions, genice.lattice_sites, genice.cell)

Exporter("gromacs").dump(
    genice,
    water_model="3site",
)
