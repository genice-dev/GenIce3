# Another plan of reactive GenIce3 (リアクティブプロパティによる実装).

from genice3 import ConfigurationError
from genice3.group import Group
from genice3.molecule import Molecule
from genice3.plugin import safe_import
from genice3.util import (
    replicate_positions,
    grandcell_wrap,
    assume_tetrahedral_vectors,
)
from genice3.cage import CageSpecs, CageSpec
from cif2ice import cellshape
import genice_core
import networkx as nx
import numpy as np
from dataclasses import dataclass
from logging import getLogger
from typing import Any, Dict, Generator, List, Tuple
from enum import Enum
import inspect

from genice3.dependencyengine import DependencyEngine, get_reactive_tasks, reactive
from genice3.unitcell import UnitCell


class ShowUsageError(Exception):
    """Usage表示を要求する例外

    Args:
        flag_name: フラグ名（例: "?", "help?", "cage?"）
    """

    def __init__(self, flag_name: str, message: str = ""):
        self.flag_name = flag_name
        super().__init__(message or f"Show usage for flag: {flag_name}")


# enumのようなものはどう定義する?
class MoleculeType(Enum):
    WATER = "water"
    GUEST = "guest"
    DOPANT = "dopant"
    GROUP = "group"


@dataclass
class GuestSpec:
    """
    ゲストの情報を表すデータクラス。
    """

    molecule: Molecule
    occupancy: float

    def __repr__(self) -> str:
        return (
            f"GuestSpec(molecule={self.molecule.name!r}, "
            f"occupancy={self.occupancy:.3f})"
        )


@dataclass
class AtomicStructure:
    """
    原子構造データを統合的に保持するデータクラス。
    exporterプラグインが使用するための統一インターフェース。
    """

    waters: Dict[int, Molecule]
    guests: List[Molecule]
    ions: Dict[int, Molecule]
    cell: np.ndarray

    def __repr__(self) -> str:
        return (
            f"AtomicStructure(n_waters={len(self.waters)}, "
            f"n_guests={len(self.guests)}, "
            f"n_ions={len(self.ions)}, "
            f"cell_shape={self.cell.shape})"
        )


def _assume_water_orientations(
    coord: np.ndarray, digraph: nx.DiGraph, cellmat: np.ndarray, dopants: Dict[int, str]
) -> np.ndarray:
    """有向グラフと座標から各水分子の配向行列（Nx3x3）を計算する。

    2本のOHが一直線上にある場合は正しく動作しない。

    Args:
        coord: 各ノードの分数座標（Nx3）。
        digraph: 水素結合の向きが決まった有向グラフ。
        cellmat: セル行列（分数→直交変換に使用）。
        dopants: ドーパントが占めるサイト（ノード番号→イオン名）。

    Returns:
        各水分子の配向行列（Nx3x3）。直交座標系での回転行列。
    """

    logger = getLogger()
    # just for a test of pure water
    if len(coord) != digraph.number_of_nodes():
        raise ValueError(
            f"coord length ({len(coord)}) must match digraph node count "
            f"({digraph.number_of_nodes()})"
        )
    if len(dopants):
        logger.info(f"  {dopants} dopants")
    # 通常の氷であればアルゴリズムを高速化できる。

    nnode = len(list(digraph))
    neis = np.zeros([nnode, 2], dtype=int)

    # 仮想ノード用の配列。第0要素は実際には第nnode要素を表す。
    extended_coord = []

    celli = np.linalg.inv(cellmat)
    # v0 = np.zeros([nnode, 3])
    # v1 = np.zeros([nnode, 3])
    for node in digraph:
        if node in dopants:
            h1 = np.array([0.0, 1, 1]) / (2**0.5)
            h2 = np.array([0.0, -1, 1]) / (2**0.5)
            r1 = h1 @ celli
            r2 = h2 @ celli
            # 仮想ノードにさしかえる
            neis[node] = [nnode + len(extended_coord), nnode + len(extended_coord) + 1]
            extended_coord += [coord[node] + r1, coord[node] + r2]
            continue
        succ = list(digraph.successors(node))
        if len(succ) < 2:
            vsucc = (coord[succ] - coord[node]) @ cellmat
            pred = list(digraph.predecessors(node))
            vpred = (coord[pred] - coord[node]) @ cellmat
            vsucc /= np.linalg.norm(vsucc, axis=1)[:, np.newaxis]
            vpred /= np.linalg.norm(vpred, axis=1)[:, np.newaxis]
            if len(vpred) > 2:
                # number of incoming bonds should be <= 2
                vpred = vpred[:2]
            vcomp = assume_tetrahedral_vectors(np.vstack([vpred, vsucc]))
            logger.debug(f"Node {node} vcomp {vcomp} vsucc {vsucc} vpred {vpred}")
            vsucc = np.vstack([vsucc, vcomp])[:2]
            rsucc = vsucc @ celli
            # 仮想ノードにさしかえる
            neis[node] = [nnode + len(extended_coord), nnode + len(extended_coord) + 1]
            extended_coord += [coord[node] + rsucc[0], coord[node] + rsucc[1]]
        else:
            neis[node] = succ

    if len(extended_coord) == 0:
        extended_coord = coord
    else:
        extended_coord = np.vstack([coord, extended_coord])

    # array of donating vectors
    v0 = extended_coord[neis[:, 0]] - coord[:]
    v0 -= np.floor(v0 + 0.5)
    v0 = v0 @ cellmat
    v0 /= np.linalg.norm(v0, axis=1)[:, np.newaxis]
    v1 = extended_coord[neis[:, 1]] - coord[:]
    v1 -= np.floor(v1 + 0.5)
    v1 = v1 @ cellmat
    v1 /= np.linalg.norm(v1, axis=1)[:, np.newaxis]
    # intramolecular axes
    y = v1 - v0
    y /= np.linalg.norm(y, axis=1)[:, np.newaxis]
    z = v0 + v1
    z /= np.linalg.norm(z, axis=1)[:, np.newaxis]
    x = np.cross(y, z, axisa=1, axisb=1)

    rotmatrices = np.zeros([nnode, 3, 3])

    rotmatrices[:, 0, :] = x
    rotmatrices[:, 1, :] = y
    rotmatrices[:, 2, :] = z
    return rotmatrices


def _replicate_lattice_node(
    lattice_site_node: int, nmol: int, replication_matrix: np.ndarray
) -> Generator[int, None, None]:
    """1つの格子サイトを拡大単位胞内で複製したときのノード番号を列挙する。

    Args:
        lattice_site_node: 複製前の単位胞内での格子サイト（ノード）番号。
        nmol: 単位胞内の水分子数（ノード数）。
        replication_matrix: 拡大倍率（行列式）の計算に用いる3x3行列。通常は replication_matrix を渡す。

    Yields:
        拡大単位胞内でのノード番号（lattice_site_node + nmol * i for i in 0..倍率-1）。
    """
    multiple = int(np.floor(np.linalg.det(replication_matrix) + 0.5))
    for i in range(multiple):
        yield lattice_site_node + nmol * i


def _replicate_graph(
    graph1: nx.Graph,
    cell1frac_coords: np.ndarray,
    replica_vectors: np.ndarray,
    replica_vector_index: Dict[Tuple[int, ...], int],
    reshape: np.ndarray,
) -> nx.Graph:
    """
    指定されたレプリカベクトルと形状に基づいてグラフを複製する。

    2つの座標系がいりみだれているので注意。
    cell1frac: 複製前の単位胞における小数座標
    grandfrac: 複製後の大きな単位胞における小数座標

    Args:
      graph1: 元のグラフ。
      cell1frac_coords: 元のグラフ内の節点の分数座標 (Nx3)。
      replica_vectors: レプリカベクトルの配列。
      replica_vector_index: レプリカベクトル座標タプル → 一意のインデックス。
      reshape: 拡大単位胞の積み重ね方を表す行列。

    Returns:
      複製された無向グラフ。fixed の複製は行わない。
    """
    # repgraph = dg.IceGraph()
    repgraph = nx.Graph()
    nmol = cell1frac_coords.shape[0]

    # 正の行列式の値(倍率)。整数。
    det = np.linalg.det(reshape)
    if det < 0:
        det = -det
    det = np.floor(det + 0.5).astype(int)
    # 逆行列に行列式をかけたもの。整数行列。
    invdet = np.floor(np.linalg.inv(reshape) * det + 0.5).astype(int)

    for i, j in graph1.edges(data=False):
        # positions in the original small cell
        cell1_delta = cell1frac_coords[j] - cell1frac_coords[i]
        cell1_delta = np.floor(cell1_delta + 0.5).astype(int)

        for a, cell1frac_a in enumerate(replica_vectors):
            cell1frac_b = cell1frac_a + cell1_delta
            cell1frac_b = np.floor(
                grandcell_wrap(cell1frac_b, reshape, invdet, det)
            ).astype(int)
            b = replica_vector_index[tuple(cell1frac_b)]
            newi = nmol * b + i
            newj = nmol * a + j

            repgraph.add_edge(newi, newj)

    return repgraph


def _replicate_fixed_edges(
    repgraph: nx.Graph, fixed: nx.DiGraph, nmol: int
) -> nx.DiGraph:
    """単位胞の固定エッジを拡大単位胞のグラフ上に複製した有向グラフを返す。

    Args:
        repgraph: 拡大単位胞全体の無向グラフ。
        fixed: 単位胞内の固定エッジ（有向グラフ）。
        nmol: 単位胞内のノード数。

    Returns:
        拡大単位胞全体での固定エッジを表す有向グラフ。
    """
    logger = getLogger("replicate_fixed_edges")
    rep_fixed_edges = nx.DiGraph()
    for repi, repj in repgraph.edges():
        i = repi % nmol
        j = repj % nmol
        if fixed.has_edge(i, j):
            rep_fixed_edges.add_edge(repi, repj)
        elif fixed.has_edge(j, i):
            rep_fixed_edges.add_edge(repj, repi)
    for edge in rep_fixed_edges.edges():
        logger.debug(f"* {edge=}")
    return rep_fixed_edges


def replicate_subgraph(
    repgraph: nx.Graph, subgraph: nx.Graph, nmol: int
) -> Generator[nx.Graph, None, None]:
    """単位胞内の subgraph の各レプリカを repgraph から取り出して yield する。

    Args:
        repgraph: 拡大単位胞全体の無向グラフ。
        subgraph: 単位胞内の部分グラフ（例: 1ケージを構成するノードと辺）。
        nmol: 単位胞内のノード数。

    Yields:
        拡大単位胞内の各レプリカに対応する部分グラフ（nx.Graph）。
    """
    origin = list(subgraph.nodes())[0]
    nrep = len(repgraph) // nmol  # number of replicas

    def _next(_reporigin):
        for _repnei in nx.neighbors(repgraph, _reporigin):
            _origin = _reporigin % nmol
            _nei = _repnei % nmol
            if _nei in nx.neighbors(subgraph, _origin) and not replica.has_edge(
                _reporigin, _repnei
            ):
                replica.add_edge(_reporigin, _repnei)
                _next(_repnei)

    for rep in range(nrep):
        reporigin = origin + nmol * rep
        replica = nx.Graph()
        _next(reporigin)
        yield replica


# ============================================================================
# DependencyEngineタスク関数定義: 依存関係は引数名から自動推論される
# 各関数には @reactive を付ける。関数名がそのまま genice.<名前> になるので名詞で書く。
# ============================================================================

_genice3_logger = getLogger("GenIce3")


@reactive
def cell(unitcell: UnitCell, replication_matrix: np.ndarray) -> np.ndarray:
    """拡大単位胞のセル行列"""
    return unitcell.cell @ replication_matrix


@reactive
def replica_vectors(replication_matrix: np.ndarray) -> np.ndarray:
    """レプリカベクトルを計算する。

    拡大単位胞を構成するために必要な、元の単位胞のグリッド位置を表す
    整数ベクトルのリストを生成します。各ベクトルは、拡大単位胞内での
    単位胞の相対位置を表します。

    Args:
        replication_matrix: 単位胞を複製するための3x3整数行列

    Returns:
        np.ndarray: レプリカベクトルの配列（Nx3配列、Nは拡大単位胞内の単位胞数）
    """
    i, j, k = np.array(replication_matrix)
    corners = np.array(
        [a * i + b * j + c * k for a in (0, 1) for b in (0, 1) for c in (0, 1)]
    )

    mins = np.min(corners, axis=0)
    maxs = np.max(corners, axis=0)
    _genice3_logger.debug(f"  {mins=}, {maxs=}")

    det = abs(np.linalg.det(replication_matrix))
    det = np.floor(det + 0.5).astype(int)
    invdet = np.floor(np.linalg.inv(replication_matrix) * det + 0.5).astype(int)

    vecs = set()
    for a in range(mins[0], maxs[0] + 1):
        for b in range(mins[1], maxs[1] + 1):
            for c in range(mins[2], maxs[2] + 1):
                abc = np.array([a, b, c])
                rep = grandcell_wrap(abc, replication_matrix, invdet, det).astype(int)
                if tuple(rep) not in vecs:
                    vecs.add(tuple(rep))

    vecs = np.array(list(vecs))
    vol = abs(np.linalg.det(replication_matrix))
    if not np.allclose(vol, len(vecs)):
        raise ValueError(
            f"replication_matrix determinant ({vol}) must equal number of "
            f"replica vectors ({len(vecs)})"
        )
    return vecs


@reactive
def replica_vector_labels(replica_vectors: np.ndarray) -> Dict[Tuple[int, ...], int]:
    """レプリカベクトル座標タプル → 一意のインデックス の辞書を返す。

    拡大単位胞内での単位胞の位置を、グラフ複製などで参照するために使う。

    Args:
        replica_vectors: レプリカベクトルの配列（Nx3）。

    Returns:
        座標タプル (a, b, c) を 0..N-1 のインデックスにマッピングする辞書。
    """
    return {tuple(xyz): i for i, xyz in enumerate(replica_vectors)}


@reactive
def graph(
    unitcell: UnitCell,
    replica_vectors: np.ndarray,
    replica_vector_labels: Dict[Tuple[int, ...], int],
    replication_matrix: np.ndarray,
) -> nx.Graph:
    """拡大単位胞に対応するグラフを生成する。

    基本単位胞のグラフ（水分子間の水素結合ネットワーク）を、
    拡大単位胞全体に複製して統合したグラフを生成します。
    このグラフは、拡大単位胞内のすべての水分子間の接続関係を表します。

    Args:
        unitcell: 基本単位胞オブジェクト
        replica_vectors: レプリカベクトルの配列
        replica_vector_labels: レプリカベクトル座標タプル→インデックスの辞書（replica_vector_labels タスクの戻り値）
        replication_matrix: 単位胞を複製するための3x3整数行列

    Returns:
        nx.Graph: 拡大単位胞全体の水素結合ネットワークを表す無向グラフ
    """
    g = _replicate_graph(
        unitcell.graph,
        unitcell.lattice_sites,
        replica_vectors,
        replica_vector_index=replica_vector_labels,
        reshape=replication_matrix,
    )
    return g


@reactive
def lattice_sites(
    unitcell: UnitCell,
    replica_vectors: np.ndarray,
    replication_matrix: np.ndarray,
) -> np.ndarray:
    """格子サイト位置を拡大単位胞全体に複製する。

    基本単位胞内の水分子の座標を、拡大単位胞全体に複製します。
    各水分子の位置は、単位胞の周期境界条件に従って配置されます。

    Args:
        unitcell: 基本単位胞オブジェクト
        replica_vectors: レプリカベクトルの配列
        replication_matrix: 単位胞を複製するための3x3整数行列

    Returns:
        np.ndarray: 拡大単位胞内のすべての水分子の座標（Nx3配列、Nは水分子数）
    """
    return replicate_positions(
        unitcell.lattice_sites, replica_vectors, replication_matrix
    )


@reactive
def anions(
    unitcell: UnitCell, replica_vectors: np.ndarray, spot_anions: Dict[int, str]
) -> Dict[int, str]:
    """アニオンイオンの配置情報を拡大単位胞全体に複製する。

    基本単位胞内で定義されたアニオンイオンと、spot_anionsで指定された
    特定位置のアニオンを統合し、拡大単位胞全体でのアニオン配置を返します。

    Args:
        unitcell: 基本単位胞オブジェクト
        replica_vectors: レプリカベクトルの配列
        spot_anions: 特定の格子サイト位置に配置するアニオンの辞書（サイトインデックス -> イオン名）

    Returns:
        Dict[int, str]: 拡大単位胞全体でのアニオン配置（サイトインデックス -> イオン名）
    """
    anion_dict: Dict[int, str] = {}
    Z = len(unitcell.lattice_sites)
    for site_index, ion_name in unitcell.anions.items():
        for i in range(len(replica_vectors)):
            site = i * Z + site_index
            anion_dict[site] = ion_name
    for site_index, ion_name in spot_anions.items():
        anion_dict[site_index] = ion_name
    return anion_dict


@reactive
def cations(
    unitcell: UnitCell, replica_vectors: np.ndarray, spot_cations: Dict[int, str]
) -> Dict[int, str]:
    """カチオンイオンの配置情報を拡大単位胞全体に複製する。

    基本単位胞内で定義されたカチオンイオンと、spot_cationsで指定された
    特定位置のカチオンを統合し、拡大単位胞全体でのカチオン配置を返します。

    Args:
        unitcell: 基本単位胞オブジェクト
        replica_vectors: レプリカベクトルの配列
        spot_cations: 特定の格子サイト位置に配置するカチオンの辞書（サイトインデックス -> イオン名）

    Returns:
        Dict[int, str]: 拡大単位胞全体でのカチオン配置（サイトインデックス -> イオン名）
    """
    cation_dict: Dict[int, str] = {}
    Z = len(unitcell.lattice_sites)
    for site_index, ion_name in unitcell.cations.items():
        for i in range(len(replica_vectors)):
            site = i * Z + site_index
            cation_dict[site] = ion_name
    for site_index, ion_name in spot_cations.items():
        cation_dict[site_index] = ion_name
    return cation_dict


@reactive
def site_occupants(
    anions: Dict[int, str], cations: Dict[int, str], lattice_sites: np.ndarray
) -> List[str]:
    """各格子サイトの占有種（水分子またはイオン）のリストを生成する。

    各格子サイトが水分子、アニオン、カチオンのいずれで占有されているかを
    判定し、サイトインデックス順にリストとして返します。

    Args:
        anions: アニオン配置の辞書
        cations: カチオン配置の辞書
        lattice_sites: 格子サイト位置の配列

    Returns:
        List[str]: 各サイトの占有種のリスト（"water"またはイオン名）
    """
    occupants = ["water"] * len(lattice_sites)
    for site, ion_name in anions.items():
        occupants[site] = ion_name
    for site, ion_name in cations.items():
        occupants[site] = ion_name
    return occupants


@reactive
def fixed_edges(
    graph: nx.Graph,
    unitcell: UnitCell,
    spot_anions: Dict[int, str],
    spot_cations: Dict[int, str],
) -> nx.DiGraph:
    """固定エッジ（水素結合の方向が固定されたエッジ）を拡大単位胞全体に複製する。

    基本単位胞で定義された固定エッジと、spot_anions/spot_cationsで指定された
    イオン位置に基づく固定エッジを統合し、拡大単位胞全体での固定エッジを返します。
    固定エッジは、水素結合の方向が既に決定されている（プロトンが固定されている）
    エッジを表します。

    Args:
        graph: 拡大単位胞全体のグラフ
        unitcell: 基本単位胞オブジェクト
        spot_anions: 特定位置のアニオン配置
        spot_cations: 特定位置のカチオン配置

    Returns:
        nx.DiGraph: 拡大単位胞全体での固定エッジを表す有向グラフ
    """
    if (spot_anions or spot_cations) and not unitcell.SUPPORTS_ION_DOPING:
        raise ConfigurationError(
            "Ion doping (spot_anion/spot_cation) is not supported for "
            "hydrogen-ordered ices."
        )
    dg = _replicate_fixed_edges(graph, unitcell.fixed, len(unitcell.lattice_sites))
    for site_index in spot_anions:
        for nei in graph.neighbors(site_index):
            if dg.has_edge(site_index, nei):
                raise ConfigurationError(
                    f"矛盾する辺の固定 at {site_index}; すでに({site_index} --> {nei})が固定されています。"
                )
            else:
                dg.add_edge(nei, site_index)
    for site_index in spot_cations:
        for nei in graph.neighbors(site_index):
            if dg.has_edge(nei, site_index):
                raise ConfigurationError(
                    f"矛盾する辺の固定 at {site_index}; すでに({nei} --> {site_index})が固定されています。"
                )
            else:
                dg.add_edge(site_index, nei)
    return dg


@reactive
def digraph(
    graph: nx.Graph,
    depol_loop: int,
    lattice_sites: np.ndarray,
    fixed_edges: nx.DiGraph,
    target_pol: np.ndarray,
) -> nx.DiGraph:
    """水素結合ネットワークの有向グラフを生成する。

    無向グラフ（水素結合ネットワーク）から、各水素結合の方向（プロトンの向き）
    を決定して有向グラフを生成します。固定エッジで指定された方向は維持され、
    それ以外のエッジは双極子最適化アルゴリズムにより方向が決定されます。

    Args:
        graph: 拡大単位胞全体の無向グラフ
        depol_loop: 双極子最適化の反復回数
        lattice_sites: 格子サイト位置の配列
        fixed_edges: 拡大単位胞全体での固定エッジの有向グラフ
        target_pol: 分極の目標値

    Returns:
        nx.DiGraph: 水素結合の方向が決定された有向グラフ
    """
    for edge in fixed_edges.edges():
        _genice3_logger.debug(f"+ {edge=}")
    dg = genice_core.ice_graph(
        graph,
        vertex_positions=lattice_sites,
        is_periodic_boundary=True,
        dipole_optimization_cycles=depol_loop,
        fixed_edges=fixed_edges,
        pairing_attempts=1000,
        target_pol=target_pol,
    )
    if not dg:
        raise ConfigurationError("Failed to generate a directed graph.")
    return dg


@reactive
def orientations(
    lattice_sites: np.ndarray,
    digraph: nx.DiGraph,
    cell: np.ndarray,
    anions: Dict[int, str],
    cations: Dict[int, str],
) -> np.ndarray:
    """各水分子の配向行列を計算する。

    有向グラフで決定された水素結合の方向に基づいて、各水分子の
    配向（回転行列）を計算します。水分子のOHベクトルの方向から
    分子全体の配向を決定します。

    Args:
        lattice_sites: 格子サイト位置の配列
        digraph: 水素結合の方向が決定された有向グラフ
        cell: 拡大単位胞のセル行列
        anions: アニオン配置の辞書
        cations: カチオン配置の辞書

    Returns:
        np.ndarray: 各水分子の配向行列（Nx3x3配列、Nは水分子数）
    """
    return _assume_water_orientations(
        lattice_sites,
        digraph,
        cell,
        anions | cations,
    )


@reactive
def cages(
    unitcell: UnitCell,
    replica_vectors: np.ndarray,
    replication_matrix: np.ndarray,
    graph: nx.Graph,
) -> CageSpecs | None:
    """ケージ位置とタイプを拡大単位胞全体に複製する。

    基本単位胞内で定義されたゲスト分子を配置するためのケージ（空隙）の
    位置とタイプを、拡大単位胞全体に複製する。

    Args:
        unitcell: 基本単位胞オブジェクト。
        replica_vectors: レプリカベクトルの配列。
        replication_matrix: 単位胞を複製するための3x3整数行列。
        graph: 拡大単位胞全体の無向グラフ（サブグラフ複製に使用）。

    Returns:
        CageSpecs: 拡大単位胞全体でのケージ位置とタイプ。
        unitcell.cages が None の場合は None。
    """
    if unitcell.cages is None:
        return None
    # ケージが存在しない場合（空の配列）の処理
    if len(unitcell.cages.positions) == 0:
        return CageSpecs(positions=np.array([]).reshape(0, 3), specs=[])
    repcagepos = replicate_positions(
        unitcell.cages.positions, replica_vectors, replication_matrix
    )
    num_cages_in_unitcell = len(unitcell.cages.positions)

    # replicate_subgraphはケージ一個ずつをreplicateするが、repcagespecsの並び順は単位胞単位。
    repcagespecs = [None] * len(repcagepos)
    for i, cage in enumerate(unitcell.cages.specs):
        for j, repgraph in enumerate(
            replicate_subgraph(graph, cage.graph, unitcell.lattice_sites.shape[0])
        ):
            repcagespecs[i + j * num_cages_in_unitcell] = CageSpec(
                cage_type=cage.cage_type, faces=cage.faces, graph=repgraph
            )
    # unit cellのcagesと同じ構造。
    _genice3_logger.debug(f"{repcagepos=}, {repcagespecs=}")
    return CageSpecs(positions=repcagepos, specs=repcagespecs)


def place_groups_on_lattice(
    genice: "GenIce3",
    spot_cation_groups: Dict[int, Dict[int, str]],
) -> None:
    """
    格子点に group を配置する。

    Args:
        genice: GenIce3 インスタンス
        spot_cation_groups: サイト -> {ケージID -> group名} の辞書
    """
    _genice3_logger.info(
        f"place_groups_on_lattice: dummy implementation (group assignment not yet applied) {spot_cation_groups=}"
    )


def log_spot_cation_cages(genice: "GenIce3") -> None:
    """spot_cation ごとに属するケージのID・cage_type・facesをログ表示する。"""
    if not genice.spot_cations or genice.cages is None or len(genice.cages.specs) == 0:
        return
    num_replicas = int(np.round(np.linalg.det(genice.replication_matrix)))
    num_cages_in_unitcell = len(genice.cages.specs) // max(1, num_replicas)
    for site, ion_name in genice.spot_cations.items():
        cage_indices = genice.cages.node_to_cage_indices.get(site, [])
        for cage_id in cage_indices:
            spec = genice.cages.specs[cage_id]
            genice.logger.info(
                f"spot_cation {site}={ion_name} belongs to cage {cage_id} ({spec.cage_type} {spec.faces}) in the supercell."
            )


def log_cation_cages(genice: "GenIce3") -> None:
    """単位胞内のカチオンごとに、属するケージのID・cage_type・faces をログ表示する。"""
    if (
        not genice.cations
        or genice.unitcell.cages is None
        or len(genice.unitcell.cages.specs) == 0
    ):
        return
    for site, ion_name in genice.cations.items():
        cage_indices = genice.unitcell.cages.node_to_cage_indices.get(site, [])
        for cage_id in cage_indices:
            spec = genice.unitcell.cages.specs[cage_id]
            genice.logger.info(
                f"cation {site}={ion_name} belongs to cage {cage_id} ({spec.cage_type} {spec.faces}) in the unit cell."
            )


def place_group(direction: np.ndarray, bondlen: float, group_name: str) -> Group:
    """指定方向・結合長で group プラグインを読み込み、配置した Group を返す。

    置換イオンから group のアンカー原子までが direction 方向に bondlen の長さで並ぶ。
    TODO: 将来は2個以上のアンカーを持つ group を扱う可能性がある。

    Args:
        direction: 配置方向（直交座標、正規化される）。
        bondlen: アンカーまでの結合長。
        group_name: group プラグイン名（例: "ammonia"）。

    Returns:
        回転・並進を適用した Group インスタンス。
    """
    # logger = getLogger("GenIce3")
    group = safe_import("group", group_name).Group()
    # logger.info(f"{group_name=} {group=}")
    direction /= np.linalg.norm(direction)
    offset = direction * bondlen
    # Z軸をdirection方向に傾ける行列
    ex, ey, ez = direction
    r = (ex**2 + ey**2) ** 0.5
    Ry = np.array([[ez, 0, -r], [0, 1, 0], [r, 0, ez]])
    Rz = np.array([[ex / r, ey / r, 0], [-ey / r, ex / r, 0], [0, 0, 1]])
    rotmat = Ry @ Rz
    sites = group.sites @ rotmat + offset
    return Group(
        sites=sites,
        labels=group.labels,
        bonds=group.bonds,
        name=group.name,
    )


# ============================================================================
# GenIce3クラス: DependencyEngineをラップ
# ============================================================================


class GenIce3:
    """GenIce3のメインクラス：リアクティブプロパティによる氷構造生成システム

    GenIce3は、依存関係エンジン（DependencyEngine）を使用して、必要な時に
    自動的に計算されるリアクティブプロパティを提供します。これにより、ユーザーは
    必要なプロパティにアクセスするだけで、そのプロパティに依存するすべての
    計算が自動的に実行されます。

    リアクティブプロパティの仕組み:
        - 各プロパティ（digraph, graph, lattice_sitesなど）は、アクセス時に
          必要に応じて自動的に計算されます
        - 依存関係は関数の引数名から自動的に推論されます
        - 一度計算されたプロパティはキャッシュされ、依存する入力が変更されるまで
          再利用されます
        - 入力プロパティ（unitcell, replication_matrix, depol_loopなど）が
          変更されると、それに依存するすべてのプロパティのキャッシュが自動的に
          クリアされます

    使用例:
        >>> genice = GenIce3(unitcell=my_unitcell)
        >>> digraph = genice.digraph  # 自動的に必要な計算が実行される
        >>> orientations = genice.orientations  # digraphに依存するため、digraphが先に計算される

    Attributes:
        digraph (nx.DiGraph): 水素結合の方向が決定された有向グラフ。
            無向グラフから双極子最適化アルゴリズムにより各水素結合の方向を決定した
            有向グラフです。固定エッジで指定された方向は維持され、それ以外のエッジは
            最適化により決定されます。このプロパティにアクセスすると、必要な依存関係
            （graph, lattice_sites, fixed_edges など）が自動的に計算されます。

        graph (nx.Graph): 水素結合ネットワークの無向グラフ。
            拡大単位胞全体の水分子間の水素結合ネットワークを表す無向グラフです。
            基本単位胞のグラフを拡大単位胞全体に複製して統合したものです。

        lattice_sites (np.ndarray): 格子サイト位置の配列。
            拡大単位胞内のすべての水分子の座標を表すNx3配列です（Nは水分子数）。
            基本単位胞内の水分子の座標を、単位胞の周期境界条件に従って拡大単位胞全体に
            複製したものです。

        orientations (np.ndarray): 各水分子の配向行列。
            各水分子の配向（回転行列）を表すNx3x3配列です（Nは水分子数）。
            有向グラフで決定された水素結合の方向に基づいて、各水分子のOHベクトルの
            方向から分子全体の配向を決定します。

        unitcell (UnitCell): 基本単位胞オブジェクト。
            氷構造の基本単位胞を表すオブジェクトです。格子構造、水分子の配置、
            水素結合ネットワーク、固定エッジなどの情報を含みます。

        replication_matrix (np.ndarray): 単位胞複製行列。
            基本単位胞をどのように積み重ねて拡大単位胞を作成するかを指定する3x3整数行列です。
            単位行列の場合は基本単位胞のみを使用します。

        depol_loop (int): 双極子最適化の反復回数。
            有向グラフを生成する際の双極子最適化アルゴリズムの反復回数です。
            値が大きいほどより最適化された構造が得られますが、計算時間も増加します。

        seed (int): 乱数シード。
            乱数生成器のシード値です。digraphの生成などで使用される乱数の初期化に使用されます。
            このプロパティを変更すると、それに依存するすべてのリアクティブプロパティの
            キャッシュが自動的にクリアされます。

        spot_anions (Dict[int, str]): 特定の格子サイト位置に配置するアニオンイオンの辞書。
            サイトインデックスからイオン名へのマッピングです。このプロパティを変更すると、
            それに依存するすべてのリアクティブプロパティのキャッシュが自動的にクリアされます。

        spot_cations (Dict[int, str]): 特定の格子サイト位置に配置するカチオンイオンの辞書。
            サイトインデックスからイオン名へのマッピングです。このプロパティを変更すると、
            それに依存するすべてのリアクティブプロパティのキャッシュが自動的にクリアされます。

        cages (CageSpecs): 拡大単位胞全体でのケージ位置・タイプ。
            単位胞のケージを replica_vectors に従って複製したもので、ゲスト配置や cage_survey 出力に利用します。

        fixed_edges (nx.DiGraph): 拡大単位胞全体での固定エッジの有向グラフ。
            単位胞の固定エッジと spot_anion/spot_cation に基づく固定を統合したもので、digraph の生成に利用します。
    """

    # Class名でlog表示したい。
    logger = getLogger("GenIce3")

    # ユーザー向けAPIとして公開するpropertyのリスト
    # このリストに含まれるpropertyのみAPIドキュメントを作成する
    PUBLIC_API_PROPERTIES = [
        "digraph",
        "graph",
        "lattice_sites",
        "orientations",
        "unitcell",
        "replication_matrix",
        "depol_loop",
        "target_pol",
        "seed",
        "spot_anions",
        "spot_cations",
    ]

    def __init__(
        self,
        depol_loop: int = 1000,
        replication_matrix: np.ndarray = np.eye(3, dtype=int),
        target_pol: np.ndarray = np.array([0.0, 0.0, 0.0]),
        seed: int = 1,
        spot_anions: Dict[int, str] = {},
        spot_cations: Dict[int, str] = {},
        guests: Dict[str, List["GuestSpec"]] = None,
        spot_guests: Dict[int, Molecule] = None,
        spot_cation_groups: Dict[int, Dict[int, str]] = None,
        **kwargs: Any,
    ) -> None:
        """GenIce3インスタンスを初期化する。

        Args:
            depol_loop: 双極子最適化の反復回数（デフォルト: 1000）
            replication_matrix: 単位胞複製行列（デフォルト: 単位行列）
            target_pol: 分極の目標値（デフォルト: [0, 0, 0]）
            seed: 乱数シード（デフォルト: 1）
            spot_anions: 特定位置のアニオン配置（デフォルト: {}）
            spot_cations: 特定位置のカチオン配置（デフォルト: {}）
            guests: ケージタイプごとのゲスト分子指定（デフォルト: {}）
            spot_guests: 特定ケージ位置へのゲスト分子指定（デフォルト: {}）
            spot_cation_groups: spot_cation の --group 指定（サイト -> {ケージID -> group名}）（デフォルト: {}）
            **kwargs: その他のリアクティブプロパティ（unitcellなど）

        Raises:
            ConfigurationError: 無効なキーワード引数が指定された場合
        """
        # DependencyEngineインスタンスを作成
        self.engine = DependencyEngine()

        # Default値が必要なもの
        self.seed = (
            seed  # reactive propertyとして設定（setterでnp.random.seed()も実行される）
        )
        self.depol_loop = depol_loop
        self.replication_matrix = replication_matrix
        self.target_pol = target_pol
        self.spot_anions = spot_anions
        self.spot_cations = spot_cations
        self.guests = guests if guests is not None else {}
        self.spot_guests = spot_guests if spot_guests is not None else {}
        self.spot_cation_groups = (
            spot_cation_groups if spot_cation_groups is not None else {}
        )

        # タスクを登録（モジュールレベルの関数を登録）
        self._register_tasks()

        # Default値が不要なもの
        for key in self.list_settable_reactive_properties():
            if key in kwargs:
                setattr(self, key, kwargs.pop(key))
        if kwargs:
            raise ConfigurationError(f"Invalid keyword arguments: {kwargs}.")

    def _register_tasks(self):
        """DependencyEngine に @reactive を付けたタスク関数を登録する"""
        for func in get_reactive_tasks(__name__):
            self.engine.task(func)

    # spot_anions
    @property
    def spot_anions(self):
        """特定の格子サイト位置に配置するアニオンイオンの辞書。

        Returns:
            Dict[int, str]: サイトインデックスからイオン名へのマッピング
        """
        if not hasattr(self, "_spot_anions"):
            self._spot_anions = {}
        return self._spot_anions

    @spot_anions.setter
    def spot_anions(self, spot_anions):
        """特定の格子サイト位置に配置するアニオンイオンを設定する。

        このプロパティを変更すると、それに依存するすべてのリアクティブプロパティの
        キャッシュが自動的にクリアされます。

        Args:
            spot_anions: サイトインデックスからイオン名へのマッピング
        """
        self._spot_anions = spot_anions
        self.logger.debug(f"  {spot_anions=}")
        self.engine.cache.clear()

    # spot_cations
    @property
    def spot_cations(self):
        """特定の格子サイト位置に配置するカチオンイオンの辞書。

        Returns:
            Dict[int, str]: サイトインデックスからイオン名へのマッピング
        """
        if not hasattr(self, "_spot_cations"):
            self._spot_cations = {}
        return self._spot_cations

    @spot_cations.setter
    def spot_cations(self, spot_cations):
        """特定の格子サイト位置に配置するカチオンイオンを設定する。

        このプロパティを変更すると、それに依存するすべてのリアクティブプロパティの
        キャッシュが自動的にクリアされます。

        Args:
            spot_cations: サイトインデックスからイオン名へのマッピング
        """
        self._spot_cations = spot_cations
        self.logger.debug(f"  {spot_cations=}")
        self.engine.cache.clear()

    @property
    def seed(self):
        """乱数シード。

        Returns:
            int: 乱数シード値
        """
        return self._seed

    @seed.setter
    def seed(self, seed):
        """乱数シードを設定する。

        このプロパティを変更すると、それに依存するすべてのリアクティブプロパティの
        キャッシュが自動的にクリアされます。

        Args:
            seed: 乱数シード値
        """
        self._seed = seed
        np.random.seed(seed)
        self.logger.debug(f"  {seed=}")
        # キャッシュをクリア（seedに依存するすべてのタスクを再計算させる）
        self.engine.cache.clear()

    @property
    def depol_loop(self):
        """双極子最適化の反復回数。

        Returns:
            int: 双極子最適化アルゴリズムの反復回数
        """
        return self._depol_loop

    @depol_loop.setter
    def depol_loop(self, depol_loop):
        """双極子最適化の反復回数を設定する。

        このプロパティを変更すると、それに依存するすべてのリアクティブプロパティの
        キャッシュが自動的にクリアされます。

        Args:
            depol_loop: 双極子最適化アルゴリズムの反復回数
        """
        self._depol_loop = depol_loop
        self.logger.debug(f"  {depol_loop=}")
        # キャッシュをクリア（depol_loopに依存するすべてのタスクを再計算させる）
        self.engine.cache.clear()

    @property
    def target_pol(self):
        """分極の目標値（3要素のベクトル）。"""
        return self._target_pol

    @target_pol.setter
    def target_pol(self, target_pol):
        """分極の目標値を設定する。変更時は依存するキャッシュをクリアする。"""
        self._target_pol = np.asarray(target_pol, dtype=float).reshape(3)
        self.logger.debug(f"  {target_pol=}")
        self.engine.cache.clear()

    @property
    def unitcell(self):
        """基本単位胞オブジェクト。

        Returns:
            UnitCell: 基本単位胞オブジェクト

        Raises:
            ConfigurationError: 単位胞が設定されていない場合
        """
        if not hasattr(self, "_unitcell") or self._unitcell is None:
            raise ConfigurationError("Unitcell is not set.")
        return self._unitcell

    @unitcell.setter
    def unitcell(self, unitcell):
        """基本単位胞オブジェクトを設定する。

        このプロパティを変更すると、それに依存するすべてのリアクティブプロパティの
        キャッシュが自動的にクリアされます。

        Args:
            unitcell: 基本単位胞オブジェクト
        """
        self._unitcell = unitcell
        self.logger.debug(f"  {unitcell=}")
        self.logger.debug(f"  {unitcell.lattice_sites=}")
        self.logger.debug(f"  {unitcell.graph=}")
        self.logger.debug(f"  {unitcell.fixed=}")

        a, b, c, A, B, C = cellshape(self.replication_matrix @ self.unitcell.cell)
        self.logger.debug("  Reshaped cell:")
        self.logger.debug(f"    {a=:.4f}, {b=:.4f}, {c=:.4f}")
        self.logger.debug(f"    {A=:.3f}, {B=:.3f}, {C=:.3f}")
        # キャッシュをクリア（unitcellに依存するすべてのタスクを再計算させる）
        self.engine.cache.clear()

    @property
    def replication_matrix(self):
        """単位胞を複製するための3x3整数行列。

        この行列により、基本単位胞をどのように積み重ねて拡大単位胞を
        作成するかを指定します。

        Returns:
            np.ndarray: 3x3整数行列
        """
        return self._replication_matrix

    @replication_matrix.setter
    def replication_matrix(self, replication_matrix):
        """単位胞複製行列を設定する。

        このプロパティを変更すると、それに依存するすべてのリアクティブプロパティの
        キャッシュが自動的にクリアされます。

        Args:
            replication_matrix: 3x3整数行列
        """
        self._replication_matrix = np.array(replication_matrix).reshape(3, 3)
        i, j, k = self._replication_matrix
        self.logger.debug(f"    {i=}")
        self.logger.debug(f"    {j=}")
        self.logger.debug(f"    {k=}")
        # キャッシュをクリア（replication_matrixに依存するすべてのタスクを再計算させる）
        self.engine.cache.clear()

    def _get_inputs(self) -> Dict[str, Any]:
        """engine.resolve()に渡すinputs辞書を取得"""
        return {
            "unitcell": self.unitcell,
            "replication_matrix": self.replication_matrix,
            "depol_loop": self.depol_loop,
            "target_pol": self.target_pol,
            "spot_anions": self.spot_anions,
            "spot_cations": self.spot_cations,
        }

    def __getattr__(self, name: str):
        """リアクティブプロパティへのアクセスを自動解決する。

        このメソッドにより、DependencyEngineに登録されたタスク関数が
        プロパティとしてアクセス可能になります。プロパティにアクセスすると、
        依存関係が自動的に解決され、必要な計算が実行されます。

        例:
            >>> genice = GenIce3(unitcell=my_unitcell)
            >>> digraph = genice.digraph  # この時点でdigraphとその依存関係が計算される

        Args:
            name: アクセスするプロパティ名（タスク関数名）

        Returns:
            計算されたプロパティの値

        Raises:
            AttributeError: 指定された名前のプロパティが存在しない場合
            ConfigurationError: 必要な入力が設定されていない場合
        """
        # DependencyEngineに登録されているタスクかチェック
        if name in self.engine.registry:
            return self.engine.resolve(name, self._get_inputs())

        # それ以外は通常のAttributeErrorを発生
        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute '{name}'"
        )

    def water_molecules(self, water_model: Molecule) -> Dict[int, Molecule]:
        """格子サイトが水のサイトについて、配向・位置を適用した水分子の辞書を返す。

        Args:
            water_model: 水分子のテンプレート（sites, labels など）。

        Returns:
            サイト番号（ノード番号）→ Molecule の辞書。イオンサイトは含まない。
        """
        mols = {}
        for site in range(len(self.lattice_sites)):
            if "water" == self.site_occupants[site]:
                rel_position = self.lattice_sites[site]
                orientation = self.orientations[site]

                sites = water_model.sites @ orientation + rel_position @ self.cell
                mols[site] = Molecule(
                    name=water_model.name,
                    sites=sites,
                    labels=water_model.labels,
                    is_water=True,
                )
        return mols

    def guest_molecules(self) -> List[Molecule]:
        """GenIce3に設定されたguestsとspot_guestsからゲスト分子リストを生成する。"""
        # 通常の氷（ゲストなし）ではケージ不要 → assess_cages を呼ばない
        if not self.guests and not self.spot_guests:
            return []

        all_cage_types = [spec.cage_type for spec in self.cages.specs]
        available = sorted(set(all_cage_types))
        # guest_specで指定されているのに存在しない種類のケージはエラーにする。
        for cage_type in self.guests:
            if cage_type not in all_cage_types:
                raise ConfigurationError(
                    f"Cage type {cage_type} is not defined. "
                    f"Available cage types in this structure: {available}."
                )

        randoms = np.random.random(len(self.cages.positions))

        mols = []
        for pos, spec, probability in zip(
            self.cages.positions, self.cages.specs, randoms
        ):
            accum = 0.0
            if spec.cage_type in self.guests:
                for guest_spec in self.guests[spec.cage_type]:
                    molecule = guest_spec.molecule
                    occupancy = guest_spec.occupancy
                    accum += occupancy
                    if accum > probability:
                        mols.append(
                            Molecule(
                                name=molecule.name,
                                sites=molecule.sites + pos @ self.cell,
                                labels=molecule.labels,
                                is_water=molecule.is_water,
                            )
                        )
                        break

        # spot guestの配置
        for cage_index, guest in self.spot_guests.items():
            mols.append(
                Molecule(
                    name=guest.name,
                    sites=guest.sites + self.cages.positions[cage_index] @ self.cell,
                    labels=guest.labels,
                    is_water=False,
                )
            )
        return mols

    def build_molecular_ion(
        self,
        site_index: int,
        molecule: str,
        groups: Dict[int, str] | None = None,
    ) -> Molecule:
        """サイト site_index（格子サイトのノード番号）に分子イオン（および spot cation 用の修飾 group）を構築する。

        Args:
            site_index: 格子サイトのノード番号。
            molecule: 分子イオンのプラグイン名（例: "ammonium"）。
            groups: 当該サイトに隣接するケージID → group名。spot cation の修飾用。

        Returns:
            直交座標で配置された Molecule（原子名は labels）。
        """
        groups = groups or {}
        ion_center = self.lattice_sites[site_index] @ self.cell
        try:
            ion = safe_import("molecule", molecule).Molecule()
            name = ion.name
            sites = ion.sites + ion_center
            atom_names: List[str] = list(ion.labels)
        except ImportError:
            name = molecule
            sites = np.array([ion_center])
            atom_names = [molecule]
        # 修飾グループを置いていく（--group 指定があったサイトのみ）
        for cage, group_name in groups.items():
            direction = self.cages.positions[cage] - self.lattice_sites[site_index]
            direction -= np.floor(direction + 0.5)
            group = place_group(
                direction @ self.cell,
                0.13,  # あとでなんとかする。N-H結合距離
                group_name,
            )
            sites = np.concatenate([sites, group.sites + ion_center])
            atom_names += group.labels
            self.logger.info(f"{atom_names=}")
        return Molecule(
            name=name,
            sites=sites,
            labels=atom_names,
            is_water=False,
        )

    def _effective_spot_cation_groups(self) -> Dict[int, Dict[int, str]]:
        """spot_cation_groups に単位胞由来の cation_groups を展開してマージした辞書を返す（on-demand）。"""
        # ベースは CLI/API で指定された spot_cation_groups
        effective: Dict[int, Dict[int, str]] = {
            k: dict(v) for k, v in self.spot_cation_groups.items()
        }
        # number of nodes in the unitcell
        nuc_nodes = len(self.unitcell.lattice_sites)
        # number of cages in the unitcell
        nuc_cages = len(self.unitcell.cages.specs)
        for un_node, uc_group in self.unitcell.cation_groups.items():
            for node in _replicate_lattice_node(
                un_node, nuc_nodes, self.replication_matrix
            ):
                # 拡大胞のノードに隣接する4つのケージのインデックス
                cage_indices = self.cages.node_to_cage_indices.get(node, [])
                for cage_index in cage_indices:
                    # ケージのインデックスを単位胞でのインデックスになおし、そこに入るグループを取得
                    self.logger.info(f"{cage_index=} {nuc_cages=} {uc_group=} {node=}")
                    uc_cage_index = cage_index % nuc_cages
                    if uc_cage_index in uc_group:
                        group = uc_group[cage_index % nuc_cages]
                        # 拡大胞のノードに隣接する4つのケージのインデックスに、グループをマッピング
                        effective.setdefault(node, {}).setdefault(cage_index, group)
        return effective

    def substitutional_ions(self) -> Dict[int, Molecule]:
        """単位胞・spot 由来のイオンを統合し、サイト番号→分子の辞書を返す。"""
        # 単位胞由来の group 指定も含めた「実効的な」spot_cation_groups をここで on-demand に組み立てて使う
        effective_groups = self._effective_spot_cation_groups()
        ions: Dict[int, Molecule] = {}
        # ならべかえはここではしない。formatterにまかせる。
        for site_index, molecule in self.anions.items():
            ions[site_index] = self.build_molecular_ion(site_index, molecule)
        for site_index, molecule in self.cations.items():
            # cationには腕がつく可能性がある。
            groups = effective_groups.get(site_index, {})
            ions[site_index] = self.build_molecular_ion(site_index, molecule, groups)
        self.logger.info(f"{ions=}")
        return ions

    def dope_anions(self, anions: Dict[int, Molecule]) -> None:
        """サイト番号→分子の辞書でアニオン配置を上書きする（主に API/テスト用）。"""
        for site_index, molecule in anions.items():
            self.anions[site_index] = molecule

    def dope_cations(self, cations: Dict[int, Molecule]) -> None:
        """サイト番号→分子の辞書でカチオン配置を上書きする（主に API/テスト用）。"""
        for site_index, molecule in cations.items():
            self.cations[site_index] = molecule

    # def get_atomic_structure(
    #     self,
    #     water_model: Optional[Molecule] = None,
    #     guests: Optional[Dict[str, List[GuestSpec]]] = None,
    #     spot_guests: Optional[Dict[int, Molecule]] = None,
    # ) -> AtomicStructure:
    #     """
    #     原子構造データを統合的に取得する。
    #     exporterプラグインが使用するための統一インターフェース。

    #     Args:
    #         water_model: 水分子モデル（デフォルト: FourSiteWater()）
    #         guests: ケージタイプごとのゲスト分子の指定（デフォルト: {}）
    #         spot_guests: 特定ケージ位置へのゲスト分子の指定（デフォルト: {}）

    #     Returns:
    #         AtomicStructure: 水分子、ゲスト分子、イオン、セル行列を含む統合データ構造
    #     """

    #     return AtomicStructure(
    #         waters=self.water_molecules(water_model=water_model),
    #         guests=self.guest_molecules(
    #             guests=guests or {}, spot_guests=spot_guests or {}
    #         ),
    #         ions=self.substitutional_ions(),
    #         cell=self.cell,
    #     )

    @classmethod
    def get_public_api_properties(cls):
        """
        ユーザー向けAPIとして公開されているpropertyのリストを返す。

        Returns:
            list: 公開API property名のリスト
        """
        return cls.PUBLIC_API_PROPERTIES.copy()

    def list_all_reactive_properties(self):
        """
        すべてのリアクティブプロパティ（DependencyEngineに登録されたタスク）を列挙する。

        Returns:
            dict: property名をキー、タスク関数を値とする辞書
        """
        return self.engine.registry.copy()

    def list_public_reactive_properties(self):
        """
        ユーザー向けAPIとして公開されているリアクティブプロパティのみを列挙する。

        Returns:
            dict: property名をキー、タスク関数を値とする辞書
        """
        all_reactive = self.list_all_reactive_properties()
        public_names = set(self.PUBLIC_API_PROPERTIES)
        return {
            name: func for name, func in all_reactive.items() if name in public_names
        }

    @classmethod
    def list_settable_reactive_properties(cls):
        """setterを持つリアクティブな変数を列挙する"""
        return {
            name: prop
            for name, prop in inspect.getmembers(
                cls, lambda x: isinstance(x, property) and x.fset is not None
            )
        }

    @classmethod
    def list_public_settable_reactive_properties(cls):
        """公開APIのうち、setter を持つリアクティブプロパティのみを列挙する。"""
        return {
            name: prop
            for name, prop in cls.list_settable_reactive_properties().items()
            if name in cls.PUBLIC_API_PROPERTIES
        }
