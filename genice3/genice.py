# Another plan of reactive GenIce3 (リアクティブプロパティによる実装).

from genice3 import ConfigurationError
from genice3.group import Group
from genice3.molecule import Molecule
from genice3.plugin import UnitCell as UnitCellPlugin, safe_import
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

from dependency_engine import DependencyEngine, get_reactive_tasks, reactive
from genice3.unitcell import UnitCell


def _graph_degree_stats(g: nx.Graph) -> str:
    """Return a string that summarizes the degree distribution of a graph.

    The summary includes the number and fraction of nodes with degrees
    0, 1, 2, 3, 4, and >4.
    """
    n = g.number_of_nodes()
    if n == 0:
        return "nodes=0"
    deg = [g.degree(v) for v in g]
    buckets = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, ">4": 0}
    for d in deg:
        if d <= 4:
            buckets[d] += 1
        else:
            buckets[">4"] += 1
    parts = [f"deg{k}:{c}({100*c/n:.1f}%)" for k, c in buckets.items() if c]
    return f"nodes={n} " + " ".join(parts)


class ShowUsageError(Exception):
    """Exception raised to request that usage information be shown.

    Args:
        flag_name: Flag name (for example: "?", "help?", "cage?").
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
    """Dataclass that stores information about a guest molecule."""

    molecule: Molecule
    occupancy: float

    def __repr__(self) -> str:
        return (
            f"GuestSpec(molecule={self.molecule.name!r}, "
            f"occupancy={self.occupancy:.3f})"
        )


@dataclass
class AtomicStructure:
    """Dataclass that holds atomic-structure data in an integrated form.

    Provides a unified interface to be used by exporter plugins.
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
    """Compute orientation matrices (Nx3x3) for each water molecule.

    The computation uses the directed hydrogen-bond graph and the node
    coordinates. It does not work correctly when two OH bonds are collinear.

    Args:
        coord: Fractional coordinates of each node (Nx3).
        digraph: Directed graph whose edges give the directions of hydrogen bonds.
        cellmat: Cell matrix used to convert fractional to Cartesian coordinates.
        dopants: Mapping from node index to ion name for dopant sites.

    Returns:
        Orientation matrices (Nx3x3) as rotation matrices in Cartesian coordinates.
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
    """Yield node indices for replicas of a lattice site in the expanded cell.

    Args:
        lattice_site_node: Node index of the lattice site in the original unit cell.
        nmol: Number of water molecules (nodes) in the unit cell.
        replication_matrix: 3x3 integer matrix whose determinant gives the
            replication factor. Normally the replication matrix itself.

    Yields:
        Node indices in the expanded unit cell
        (``lattice_site_node + nmol * i`` for ``i`` in ``0..factor-1``).
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
    Replicate a graph according to the given replica vectors and shape.

    Two coordinate systems are involved:
    ``cell1frac`` for fractional coordinates in the original unit cell, and
    ``grandfrac`` for fractional coordinates in the expanded cell.

    Args:
        graph1: Original graph.
        cell1frac_coords: Fractional coordinates of nodes in the original graph (Nx3).
        replica_vectors: Array of replica vectors.
        replica_vector_index: Mapping from replica-vector coordinate tuple to unique index.
        reshape: Matrix that describes how unit cells are stacked to form the expanded cell.

    Returns:
        Replicated undirected graph. Fixed edges are not replicated here.
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
    """Replicate fixed edges from the unit cell onto the expanded-cell graph.

    Args:
        repgraph: Undirected graph for the whole expanded unit cell.
        fixed: Directed graph of fixed edges in the unit cell.
        nmol: Number of nodes in the unit cell.

    Returns:
        Directed graph representing fixed edges over the entire expanded unit cell.
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
    """Yield each replica of a unit-cell subgraph from the expanded-cell graph.

    Args:
        repgraph: Undirected graph for the whole expanded unit cell.
        subgraph: Subgraph within the unit cell (e.g., nodes and edges forming one cage).
        nmol: Number of nodes in the unit cell.

    Yields:
        For each replica, an ``nx.Graph`` corresponding to that replica in the expanded cell.
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
    """Cell matrix of the expanded unit cell."""
    return unitcell.cell @ replication_matrix


@reactive
def replica_vectors(replication_matrix: np.ndarray) -> np.ndarray:
    """Compute replica vectors from a replication matrix.

    These vectors represent the grid positions of original unit cells needed
    to construct the expanded unit cell. Each vector gives the relative
    position of a unit cell within the expanded cell.

    Args:
        replication_matrix: 3x3 integer matrix used to replicate the unit cell.

    Returns:
        np.ndarray: Array of replica vectors (Nx3, where N is the number of
        unit cells in the expanded cell).
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
    """Return a mapping from replica-vector coordinate tuples to indices.

    This mapping is used to refer to unit-cell positions in the expanded
    unit cell, for example when replicating graphs.

    Args:
        replica_vectors: Array of replica vectors (Nx3).

    Returns:
        Dict that maps coordinate tuples ``(a, b, c)`` to indices ``0..N-1``.
    """
    return {tuple(xyz): i for i, xyz in enumerate(replica_vectors)}


@reactive
def graph(
    unitcell: UnitCell,
    replica_vectors: np.ndarray,
    replica_vector_labels: Dict[Tuple[int, ...], int],
    replication_matrix: np.ndarray,
) -> nx.Graph:
    """Generate the graph corresponding to the expanded unit cell.

    The graph of the basic unit cell (hydrogen-bond network between water
    molecules) is replicated over the expanded unit cell and merged into a
    single graph that represents all connectivity.

    Args:
        unitcell: Basic unit-cell object.
        replica_vectors: Array of replica vectors.
        replica_vector_labels: Mapping from replica-vector coordinate tuples
            to indices (returned by ``replica_vector_labels``).
        replication_matrix: 3x3 integer matrix used to replicate the unit cell.

    Returns:
        ``nx.Graph`` representing the hydrogen-bond network over the whole expanded unit cell.
    """
    g = _replicate_graph(
        unitcell.graph,
        unitcell.lattice_sites,
        replica_vectors,
        replica_vector_index=replica_vector_labels,
        reshape=replication_matrix,
    )
    getLogger(__name__).info("  graph: %s", _graph_degree_stats(g))
    return g


@reactive
def lattice_sites(
    unitcell: UnitCell,
    replica_vectors: np.ndarray,
    replication_matrix: np.ndarray,
) -> np.ndarray:
    """Replicate lattice-site positions over the expanded unit cell.

    The coordinates of water molecules in the basic unit cell are
    replicated over the entire expanded cell. Each water molecule is
    placed according to periodic boundary conditions.

    Args:
        unitcell: Basic unit-cell object.
        replica_vectors: Array of replica vectors.
        replication_matrix: 3x3 integer matrix used to replicate the unit cell.

    Returns:
        np.ndarray: All water-molecule coordinates in the expanded cell
        (Nx3 array, where N is the number of molecules).
    """
    return replicate_positions(
        unitcell.lattice_sites, replica_vectors, replication_matrix
    )


@reactive
def anions(
    unitcell: UnitCell, replica_vectors: np.ndarray, spot_anions: Dict[int, str]
) -> Dict[int, str]:
    """Replicate anion placement information over the expanded unit cell.

    Anions defined in the basic unit cell and those specified by
    ``spot_anions`` are combined to produce the full anion configuration
    in the expanded cell.

    Args:
        unitcell: Basic unit-cell object.
        replica_vectors: Array of replica vectors.
        spot_anions: Mapping from lattice-site index to anion name.

    Returns:
        Dict[int, str]: Anion configuration over the expanded unit cell
        (site index -> ion name).
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
    """Replicate cation placement information over the expanded unit cell.

    Cations defined in the basic unit cell and those specified by
    ``spot_cations`` are combined to produce the full cation configuration
    in the expanded cell.

    Args:
        unitcell: Basic unit-cell object.
        replica_vectors: Array of replica vectors.
        spot_cations: Mapping from lattice-site index to cation name.

    Returns:
        Dict[int, str]: Cation configuration over the expanded unit cell
        (site index -> ion name).
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
    anions: Dict[int, str],
    cations: Dict[int, str],
    spot_hydroniums: List[int],
    spot_hydroxides: List[int],
    lattice_sites: np.ndarray,
) -> List[str]:
    """Generate the list of occupants at each lattice site.

    Each lattice site is classified as water, anion, cation, H3O+, or OH-,
    and the occupant type is returned in site-index order.

    Args:
        anions: Anion configuration dictionary.
        cations: Cation configuration dictionary.
        spot_hydroniums: List of sites with H3O+.
        spot_hydroxides: List of sites with OH-.
        lattice_sites: Array of lattice-site positions.

    Returns:
        List[str]: Occupant type for each site (``"water"`` or ion name).
    """
    occupants = ["water"] * len(lattice_sites)
    for site, ion_name in anions.items():
        occupants[site] = ion_name
    for site, ion_name in cations.items():
        occupants[site] = ion_name
    for site in spot_hydroniums:
        occupants[site] = "H3O+"
    for site in spot_hydroxides:
        occupants[site] = "OH-"
    return occupants


@reactive
def fixed_edges(
    graph: nx.Graph,
    unitcell: UnitCell,
    spot_anions: Dict[int, str],
    spot_cations: Dict[int, str],
    spot_hydroniums: List[int],
    spot_hydroxides: List[int],
    bjerrum_L_edges: List[Tuple[int, int]],
    bjerrum_D_edges: List[Tuple[int, int]],
) -> nx.DiGraph:
    """Replicate fixed edges (hydrogen-bond directions) over the expanded unit cell.

    Fixed edges defined in the unit cell and those implied by
    ``spot_anions`` / ``spot_cations`` / ``spot_hydroniums`` /
    ``spot_hydroxides`` are combined into a directed graph of fixed
    edges over the whole expanded unit cell.

    - Anions: accept 4 bonds.
    - Cations: donate 4 bonds.
    - H3O+ (``spot_hydroniums``): accept 1 bond and donate 3.
    - OH- (``spot_hydroxides``): accept 3 bonds and donate 1.

    Args:
        graph: Graph of the whole expanded unit cell.
        unitcell: Basic unit-cell object.
        spot_anions: Explicit anion configuration.
        spot_cations: Explicit cation configuration.
        spot_hydroniums: List of sites with H3O+ (1 acceptor, 3 donors).
        spot_hydroxides: List of sites with OH- (3 acceptors, 1 donor).

    Returns:
        ``nx.DiGraph`` representing fixed edges over the expanded unit cell.
    """
    if (
        spot_anions
        or spot_cations
        or spot_hydroniums
        or spot_hydroxides
        or bjerrum_L_edges
        or bjerrum_D_edges
    ) and not unitcell.SUPPORTS_ION_DOPING:
        raise ConfigurationError(
            "Ion doping (spot_anion/spot_cation/spot_hydronium/spot_hydroxide) "
            "is not supported for hydrogen-ordered ices."
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
    for site_index in spot_hydroniums:
        neis = sorted(graph.neighbors(site_index))
        if len(neis) != 4:
            raise ConfigurationError(
                f"spot_hydronium at {site_index} must have 4 neighbors, got {len(neis)}."
            )
        dg.add_edge(neis[0], site_index)
        for nei in neis[1:]:
            dg.add_edge(site_index, nei)
    for site_index in spot_hydroxides:
        neis = sorted(graph.neighbors(site_index))
        if len(neis) != 4:
            raise ConfigurationError(
                f"spot_hydroxide at {site_index} must have 4 neighbors, got {len(neis)}."
            )
        dg.add_edge(site_index, neis[0])
        for nei in neis[1:]:
            dg.add_edge(nei, site_index)
    # Bjerrum L 欠陥: i ノードを hydronium と同様に扱う。
    for i, j in bjerrum_L_edges or []:
        neis = sorted(graph.neighbors(i))
        if len(neis) != 4:
            raise ConfigurationError(
                f"bjerrum_L at {i} must have 4 neighbors, got {len(neis)}."
            )
        if j not in neis:
            raise ConfigurationError(
                f"bjerrum_L edge ({i}, {j}) is not an edge in the graph."
            )
        # 受容側となる隣接ノードを j 以外から 1 つ選ぶ
        acceptor = next((nei for nei in neis if nei != j), None)
        if acceptor is None:
            raise ConfigurationError(
                f"bjerrum_L at {i} cannot choose acceptor neighbor distinct from {j}."
            )
        # hydronium と同様のチェック・追加ロジック
        for nei in neis:
            if nei == acceptor:
                # nei -> i （受容）
                if dg.has_edge(i, nei):
                    raise ConfigurationError(
                        f"矛盾する辺の固定 at {i}; すでに({i} --> {nei})が固定されています。"
                    )
                dg.add_edge(nei, i)
            else:
                # i -> nei （供与）
                if dg.has_edge(nei, i):
                    raise ConfigurationError(
                        f"矛盾する辺の固定 at {i}; すでに({nei} --> {i})が固定されています。"
                    )
                dg.add_edge(i, nei)
    # Bjerrum D 欠陥: i ノードを hydroxide と同様に扱う（ただし j は供与側にしない）。
    for i, j in bjerrum_D_edges or []:
        neis = sorted(graph.neighbors(i))
        if len(neis) != 4:
            raise ConfigurationError(
                f"bjerrum_D at {i} must have 4 neighbors, got {len(neis)}."
            )
        if j not in neis:
            raise ConfigurationError(
                f"bjerrum_D edge ({i}, {j}) is not an edge in the graph."
            )
        # 供与側となる隣接ノードを j 以外から 1 つ選ぶ
        donor = next((nei for nei in neis if nei != j), None)
        if donor is None:
            raise ConfigurationError(
                f"bjerrum_D at {i} cannot choose donor neighbor distinct from {j}."
            )
        for nei in neis:
            if nei == donor:
                # i -> nei （供与）
                if dg.has_edge(nei, i):
                    raise ConfigurationError(
                        f"矛盾する辺の固定 at {i}; すでに({nei} --> {i})が固定されています。"
                    )
                dg.add_edge(i, nei)
            else:
                # nei -> i （受容）
                if dg.has_edge(i, nei):
                    raise ConfigurationError(
                        f"矛盾する辺の固定 at {i}; すでに({i} --> {nei})が固定されています。"
                    )
                dg.add_edge(nei, i)
    return dg


@reactive
def digraph(
    graph: nx.Graph,
    pol_loop_1: int,
    pol_loop_2: int,
    lattice_sites: np.ndarray,
    fixed_edges: nx.DiGraph,
    target_pol: np.ndarray,
    bjerrum_L_edges: List[Tuple[int, int]],
    bjerrum_D_edges: List[Tuple[int, int]],
    seed: int,
) -> nx.DiGraph:
    """Generate the directed hydrogen-bond network.

    Starting from the undirected hydrogen-bond graph, this function
    determines the direction (proton orientation) of each bond to build
    a directed graph. Directions specified by fixed edges are preserved,
    while the rest are decided by a polarization-convergence algorithm
    (stage 1 then stage 2 if needed).

    Args:
        graph: Undirected graph over the expanded unit cell.
        pol_loop_1: Max iterations for polarization convergence stage 1.
        pol_loop_2: Max iterations for polarization convergence stage 2.
        lattice_sites: Array of lattice-site positions.
        fixed_edges: Directed graph of fixed edges over the expanded cell.
        target_pol: Target polarization vector.

    Returns:
        ``nx.DiGraph`` whose edges give the directions of hydrogen bonds.
    """
    for edge in fixed_edges.edges():
        _genice3_logger.debug(f"+ {edge=}")
    dg = genice_core.ice_graph(
        graph,
        vertex_positions=lattice_sites,
        is_periodic_boundary=True,
        dipole_optimization_cycles=pol_loop_1,
        dipole_optimization_cycles2=pol_loop_2,
        fixed_edges=fixed_edges,
        pairing_attempts=1000,
        target_pol=target_pol,
        seed=seed,
    )
    if not dg:
        raise ConfigurationError("Failed to generate a directed graph.")
    # Bjerrum L 欠陥: 対応するエッジを削除する（両方向とも取り除く）
    for edge in bjerrum_L_edges or []:
        i, j = edge
        if dg.has_edge(i, j):
            dg.remove_edge(i, j)
        if dg.has_edge(j, i):
            dg.remove_edge(j, i)
    # Bjerrum D 欠陥: 対応するエッジを両方向とも存在させる
    for edge in bjerrum_D_edges or []:
        i, j = edge
        if not dg.has_edge(i, j):
            dg.add_edge(i, j)
        if not dg.has_edge(j, i):
            dg.add_edge(j, i)
    return dg


@reactive
def orientations(
    lattice_sites: np.ndarray,
    digraph: nx.DiGraph,
    cell: np.ndarray,
    anions: Dict[int, str],
    cations: Dict[int, str],
    spot_hydroniums: List[int],
    spot_hydroxides: List[int],
) -> np.ndarray:
    """Compute orientation matrices for all water molecules.

    The orientations (rotation matrices) are computed from the directions
    of hydrogen bonds in the directed graph. The OH vectors determine the
    molecular orientation.

    Args:
        lattice_sites: Array of lattice-site positions.
        digraph: Directed hydrogen-bond network.
        cell: Cell matrix of the expanded unit cell.
        anions: Anion configuration dictionary.
        cations: Cation configuration dictionary.
        spot_hydroniums: List of sites with H3O+.
        spot_hydroxides: List of sites with OH-.

    Returns:
        np.ndarray: Orientation matrices (Nx3x3, where N is the number of molecules).
    """
    return _assume_water_orientations(
        lattice_sites,
        digraph,
        cell,
        set(anions) | set(cations) | set(spot_hydroniums) | set(spot_hydroxides),
    )


@reactive
def cages(
    unitcell: UnitCell,
    replica_vectors: np.ndarray,
    replication_matrix: np.ndarray,
    graph: nx.Graph,
) -> CageSpecs | None:
    """Replicate cage positions and types over the expanded unit cell.

    Cages (voids) defined in the basic unit cell for placing guest
    molecules are replicated over the entire expanded unit cell.
    Here, a cage means a quasipolyhedron surrounded by cycles of
    hydrogen bonds [Matsumoto 2007].

    Args:
        unitcell: Basic unit-cell object.
        replica_vectors: Array of replica vectors.
        replication_matrix: 3x3 integer matrix used to replicate the unit cell.
        graph: Undirected graph over the expanded unit cell (used to replicate subgraphs).

    Returns:
        ``CageSpecs`` describing cage positions and types in the expanded unit cell,
        or ``None`` if ``unitcell.cages`` is ``None``.
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
    Place group plugins on lattice sites.

    Args:
        genice: ``GenIce3`` instance.
        spot_cation_groups: Mapping from site index to
            {cage ID -> group name}.
    """
    _genice3_logger.info(
        f"place_groups_on_lattice: dummy implementation (group assignment not yet applied) {spot_cation_groups=}"
    )


def log_spot_cation_cages(genice: "GenIce3") -> None:
    """Log cage IDs, cage_type, and faces for each ``spot_cation``."""
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
    """Log cage IDs, cage_type, and faces for each cation in the unit cell."""
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
    """Load a group plugin, place it in the given direction, and return the ``Group``.

    The anchor atom of the group is placed at a distance ``bondlen`` from
    the substitutional ion along ``direction``. In the future, groups with
    multiple anchors may be supported.

    Args:
        direction: Placement direction in Cartesian coordinates (will be normalized).
        bondlen: Bond length from the substitutional ion to the group anchor.
        group_name: Group plugin name (for example, ``"ammonia"``).

    Returns:
        ``Group`` instance after rotation and translation.
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
    """Main GenIce3 class: ice-structure generator based on reactive properties.

    GenIce3 uses a dependency engine (``DependencyEngine``) to provide
    reactive properties that are computed automatically on demand. By
    accessing a property, the user triggers all computations that the
    property depends on.

    How reactive properties work:
        - Each property (``digraph``, ``graph``, ``lattice_sites``, etc.) is
          computed lazily when accessed.
        - Dependencies are inferred automatically from function argument names.
        - Once computed, properties are cached and reused until their inputs change.
        - When an input property (``unitcell``, ``replication_matrix``,
          ``pol_loop_1``, ``pol_loop_2``, etc.) is modified, the cache of all dependent
          properties is automatically cleared.

    Example:
        >>> genice = GenIce3(unitcell=my_unitcell)
        >>> digraph = genice.digraph  # required computations are executed automatically
        >>> orientations = genice.orientations  # depends on digraph, so digraph is computed first

    Attributes:
        digraph (nx.DiGraph): Directed hydrogen-bond network.
            Created from the undirected graph by a dipole-optimization
            algorithm, while preserving fixed edges. Accessing this property
            automatically computes all required dependencies (``graph``,
            ``lattice_sites``, ``fixed_edges``, etc.).

        graph (nx.Graph): Undirected hydrogen-bond network over the expanded unit cell.
            Obtained by replicating the basic-unit-cell graph over the whole supercell.

        lattice_sites (np.ndarray): Array of lattice-site positions.
            Nx3 array (N is the number of water molecules) giving coordinates
            of all molecules in the expanded unit cell.

        orientations (np.ndarray): Orientation matrices for each water molecule.
            Nx3x3 array whose elements are rotation matrices derived from the
            directed graph and OH vectors.

        unitcell (UnitCell): Basic unit-cell object describing the ice structure.
            Includes lattice, water positions, hydrogen-bond network, and fixed edges.

        replication_matrix (np.ndarray): 3x3 integer matrix specifying how the
            basic unit cell is stacked to construct the expanded unit cell.
            If it is the identity matrix, only the basic unit cell is used.

        pol_loop_1 (int): Max iterations for polarization convergence stage 1.
        pol_loop_2 (int): Max iterations for polarization convergence stage 2 (0 = disabled).

        seed (int): Random seed.
            Used for operations such as directed-graph generation. Changing this
            property clears the cache of all dependent reactive properties.

        spot_anions (Dict[int, str]): Mapping from lattice-site index to anion name.
            Changing this property clears the cache of dependent reactive properties.

        spot_cations (Dict[int, str]): Mapping from lattice-site index to cation name.
            Changing this property clears the cache of dependent reactive properties.

        spot_hydroniums (List[int]): List of sites that host H3O+ (1 acceptor, 3 donors).

        spot_hydroxides (List[int]): List of sites that host OH- (3 acceptors, 1 donor).

        cages (CageSpecs): Cage positions and types in the expanded unit cell.
            Obtained by replicating unit-cell cages according to the replica
            vectors; used for guest placement and ``cage_survey`` output.

        fixed_edges (nx.DiGraph): Directed graph of fixed edges over the expanded unit cell.
            Combines unit-cell fixed edges with those implied by
            ``spot_anion`` / ``spot_cation`` / ``spot_hydronium`` /
            ``spot_hydroxide`` and is used when generating ``digraph``.
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
        "pol_loop_1",
        "pol_loop_2",
        "target_pol",
        "seed",
        "spot_anions",
        "spot_cations",
        "spot_hydroniums",
        "spot_hydroxides",
    ]

    def __init__(
        self,
        pol_loop_1: int = 1000,
        pol_loop_2: int = 0,
        replication_matrix: np.ndarray = np.eye(3, dtype=int),
        target_pol: np.ndarray = np.array([0.0, 0.0, 0.0]),
        seed: int = 1,
        spot_anions: Dict[int, str] = None,
        spot_cations: Dict[int, str] = None,
        spot_hydroniums: List[int] = None,
        spot_hydroxides: List[int] = None,
        bjerrum_L_edges: List[Tuple[int, int]] | None = None,
        bjerrum_D_edges: List[Tuple[int, int]] | None = None,
        guests: Dict[str, List["GuestSpec"]] = None,
        spot_guests: Dict[int, Molecule] = None,
        spot_cation_groups: Dict[int, Dict[int, str]] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize a ``GenIce3`` instance.

        Args:
            pol_loop_1: Max iterations for polarization convergence stage 1
                (default: 1000).
            pol_loop_2: Max iterations for polarization convergence stage 2
                (default: 0, disabled).
            replication_matrix: Unit-cell replication matrix (default: identity).
            target_pol: Target polarization vector (default: ``[0, 0, 0]``).
            seed: Random seed (default: 1).
            spot_anions: Explicit anion configuration (default: ``{}``).
            spot_cations: Explicit cation configuration (default: ``{}``).
            spot_hydroniums: List of sites hosting H3O+ (default: ``[]``).
            spot_hydroxides: List of sites hosting OH- (default: ``[]``).
            guests: Guest specification per cage type (default: ``{}``).
            spot_guests: Guest specification per specific cage index (default: ``{}``).
            spot_cation_groups: ``--group`` specification for spot cations
                (site -> {cage ID -> group name}) (default: ``{}``).
            **kwargs: Other reactive properties (such as ``unitcell``).

        Raises:
            ConfigurationError: If unknown keyword arguments are given.
        """
        # DependencyEngineインスタンスを作成
        self.engine = DependencyEngine()

        # Default値が必要なもの
        self.seed = (
            seed  # reactive propertyとして設定（setterでnp.random.seed()も実行される）
        )
        self.pol_loop_1 = pol_loop_1
        self.pol_loop_2 = pol_loop_2
        self.replication_matrix = replication_matrix
        self.target_pol = target_pol
        self.spot_anions = spot_anions if spot_anions is not None else {}
        self.spot_cations = spot_cations if spot_cations is not None else {}
        self.spot_hydroniums = spot_hydroniums if spot_hydroniums is not None else []
        self.spot_hydroxides = spot_hydroxides if spot_hydroxides is not None else []
        self.bjerrum_L_edges = bjerrum_L_edges if bjerrum_L_edges is not None else []
        self.bjerrum_D_edges = bjerrum_D_edges if bjerrum_D_edges is not None else []
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
        """Register ``@reactive`` task functions in the ``DependencyEngine``."""
        for func in get_reactive_tasks(__name__):
            self.engine.task(func)

    # spot_anions
    @property
    def spot_anions(self):
        """Dictionary of anions placed at specific lattice sites.

        Returns:
            Dict[int, str]: Mapping from site index to ion name.
        """
        if not hasattr(self, "_spot_anions"):
            self._spot_anions = {}
        return self._spot_anions

    @spot_anions.setter
    def spot_anions(self, spot_anions):
        """Set the anion configuration at specific lattice sites.

        Changing this property clears the cache of all dependent reactive properties.

        Args:
            spot_anions: Mapping from site index to ion name.
        """
        self._spot_anions = spot_anions
        self.logger.debug(f"  {spot_anions=}")
        self.engine.cache.clear()

    # spot_cations
    @property
    def spot_cations(self):
        """Dictionary of cations placed at specific lattice sites.

        Returns:
            Dict[int, str]: Mapping from site index to ion name.
        """
        if not hasattr(self, "_spot_cations"):
            self._spot_cations = {}
        return self._spot_cations

    @spot_cations.setter
    def spot_cations(self, spot_cations):
        """Set the cation configuration at specific lattice sites.

        Changing this property clears the cache of all dependent reactive properties.

        Args:
            spot_cations: Mapping from site index to ion name.
        """
        self._spot_cations = spot_cations
        self.logger.debug(f"  {spot_cations=}")
        self.engine.cache.clear()

    # spot_hydroniums (H3O+: 1受容・3供与)
    @property
    def spot_hydroniums(self):
        """List of sites that host H3O+ (1 acceptor, 3 donors).

        Returns:
            List[int]: List of site indices.
        """
        if not hasattr(self, "_spot_hydroniums"):
            self._spot_hydroniums = []
        return self._spot_hydroniums

    @spot_hydroniums.setter
    def spot_hydroniums(self, spot_hydroniums):
        self._spot_hydroniums = (
            list(spot_hydroniums) if spot_hydroniums is not None else []
        )
        self.logger.debug(f"  {spot_hydroniums=}")
        self.engine.cache.clear()

    # spot_hydroxides (OH-: 3受容・1供与)
    @property
    def spot_hydroxides(self):
        """List of sites that host OH- (3 acceptors, 1 donor).

        Returns:
            List[int]: List of site indices.
        """
        if not hasattr(self, "_spot_hydroxides"):
            self._spot_hydroxides = []
        return self._spot_hydroxides

    @spot_hydroxides.setter
    def spot_hydroxides(self, spot_hydroxides):
        self._spot_hydroxides = (
            list(spot_hydroxides) if spot_hydroxides is not None else []
        )
        self.logger.debug(f"  {spot_hydroxides=}")
        self.engine.cache.clear()

    # Bjerrum L 欠陥に対応するエッジ集合（(i, j) のリスト）
    @property
    def bjerrum_L_edges(self) -> List[Tuple[int, int]]:
        if not hasattr(self, "_bjerrum_L_edges"):
            self._bjerrum_L_edges = []
        return self._bjerrum_L_edges

    @bjerrum_L_edges.setter
    def bjerrum_L_edges(self, edges: List[Tuple[int, int]] | None):
        self._bjerrum_L_edges = list(edges) if edges is not None else []
        self.logger.debug(f"  {self._bjerrum_L_edges=}")
        self.engine.cache.clear()

    # Bjerrum D 欠陥に対応するエッジ集合（(i, j) のリスト）
    @property
    def bjerrum_D_edges(self) -> List[Tuple[int, int]]:
        if not hasattr(self, "_bjerrum_D_edges"):
            self._bjerrum_D_edges = []
        return self._bjerrum_D_edges

    @bjerrum_D_edges.setter
    def bjerrum_D_edges(self, edges: List[Tuple[int, int]] | None):
        self._bjerrum_D_edges = list(edges) if edges is not None else []
        self.logger.debug(f"  {self._bjerrum_D_edges=}")
        self.engine.cache.clear()

    def add_spot_hydronium(self, sites):
        """Helper to add sites that host H3O+.

        Args:
            sites: Site index (int) or an iterable of indices.
        """
        if sites is None:
            return
        # numpy のスカラーも受け付ける
        if isinstance(sites, (int, np.integer)):
            new_sites = [int(sites)]
        else:
            new_sites = list(sites)
        # setter を経由してキャッシュを無効化する
        self.spot_hydroniums = list(self.spot_hydroniums) + new_sites

    def add_spot_hydroxide(self, sites):
        """Helper to add sites that host OH-.

        Args:
            sites: Site index (int) or an iterable of indices.
        """
        if sites is None:
            return
        if isinstance(sites, (int, np.integer)):
            new_sites = [int(sites)]
        else:
            new_sites = list(sites)
        self.spot_hydroxides = list(self.spot_hydroxides) + new_sites

    def add_bjerrum_L(self, edges):
        """Helper to add Bjerrum L defects.

        Args:
            edges: Single ``(i, j)`` tuple or an iterable of such tuples.
        """
        if edges is None:
            return
        # 単一タプル (i, j) も許容する
        if isinstance(edges, tuple) and len(edges) == 2:
            new_edges = [edges]
        else:
            new_edges = list(edges)
        self.bjerrum_L_edges = list(self.bjerrum_L_edges) + new_edges

    def add_bjerrum_D(self, edges):
        """Helper to add Bjerrum D defects.

        Args:
            edges: Single ``(i, j)`` tuple or an iterable of such tuples.
        """
        if edges is None:
            return
        if isinstance(edges, tuple) and len(edges) == 2:
            new_edges = [edges]
        else:
            new_edges = list(edges)
        self.bjerrum_D_edges = list(self.bjerrum_D_edges) + new_edges

    @property
    def seed(self):
        """Random seed.

        Returns:
            int: Seed value.
        """
        return self._seed

    @seed.setter
    def seed(self, seed):
        """Set the random seed.

        Changing this property clears the cache of all dependent reactive properties.

        Args:
            seed: Seed value.
        """
        self._seed = seed
        np.random.seed(seed)
        self.logger.debug(f"  {seed=}")
        # キャッシュをクリア（seedに依存するすべてのタスクを再計算させる）
        self.engine.cache.clear()

    @property
    def pol_loop_1(self):
        """Max iterations for polarization convergence (stage 1).

        Returns:
            int: Number of iterations.
        """
        return self._pol_loop_1

    @pol_loop_1.setter
    def pol_loop_1(self, pol_loop_1):
        """Set max iterations for polarization convergence stage 1.

        Changing this property clears the cache of all dependent reactive properties.

        Args:
            pol_loop_1: Number of iterations.
        """
        self._pol_loop_1 = pol_loop_1
        self.logger.debug(f"  {pol_loop_1=}")
        self.engine.cache.clear()

    @property
    def pol_loop_2(self):
        """Max iterations for polarization convergence (stage 2).

        Returns:
            int: Number of iterations (0 = disabled).
        """
        return self._pol_loop_2

    @pol_loop_2.setter
    def pol_loop_2(self, pol_loop_2):
        """Set max iterations for polarization convergence stage 2.

        Changing this property clears the cache of all dependent reactive properties.

        Args:
            pol_loop_2: Number of iterations (0 = disabled).
        """
        self._pol_loop_2 = pol_loop_2
        self.logger.debug(f"  {pol_loop_2=}")
        self.engine.cache.clear()

    @property
    def target_pol(self):
        """Target polarization vector (3 elements)."""
        return self._target_pol

    @target_pol.setter
    def target_pol(self, target_pol):
        """Set the target polarization vector and clear dependent caches."""
        self._target_pol = np.asarray(target_pol, dtype=float).reshape(3)
        self.logger.debug(f"  {target_pol=}")
        self.engine.cache.clear()

    @property
    def unitcell(self):
        """Basic unit-cell object.

        Returns:
            UnitCell: Basic unit cell.

        Raises:
            ConfigurationError: If the unit cell has not been set.
        """
        if not hasattr(self, "_unitcell") or self._unitcell is None:
            raise ConfigurationError("Unitcell is not set.")
        return self._unitcell

    def _log_expanded_cell_dimensions(self) -> None:
        """Log lattice parameters of the expanded cell (``rep @ unitcell.cell``).

        Called when ``unitcell`` or ``replication_matrix`` changes so INFO-level
        output stays aligned with the configuration used by reactive tasks.
        """
        if not hasattr(self, "_unitcell") or self._unitcell is None:
            return
        a, b, c, A, B, C = cellshape(self.replication_matrix @ self._unitcell.cell)
        self.logger.info("Expanded cell dimensions:")
        self.logger.info(f"  a= {a:.4f} nm")
        self.logger.info(f"  b= {b:.4f} nm")
        self.logger.info(f"  c= {c:.4f} nm")
        self.logger.info(f"  A= {A:.3f} deg")
        self.logger.info(f"  B= {B:.3f} deg")
        self.logger.info(f"  C= {C:.3f} deg")

    @unitcell.setter
    def unitcell(self, unitcell):
        """Set the basic unit-cell object.

        Changing this property clears the cache of all dependent reactive properties.

        Args:
            unitcell: Basic unit-cell object.
        """
        self._unitcell = unitcell
        self.logger.debug(f"  {unitcell=}")
        self.logger.debug(f"  {unitcell.lattice_sites=}")
        self.logger.debug(f"  {unitcell.graph=}")
        self.logger.debug(f"  {unitcell.fixed=}")

        self._log_expanded_cell_dimensions()
        # キャッシュをクリア（unitcellに依存するすべてのタスクを再計算させる）
        self.engine.cache.clear()

    def set_unitcell(self, unitcell_or_name, **kwargs):
        """Set the basic unit cell (reactive-property-friendly wrapper).

        Using this method instead of assignment (``genice.unitcell = ...``)
        makes it explicit that the unit cell is a reactive configuration.

        Args:
            unitcell_or_name: A ``UnitCell`` instance or unit-cell name (string).
                If a string is given, ``UnitCell(name, **kwargs)`` is created.
            **kwargs: Options forwarded to ``UnitCell(...)`` when a name is given.
        """
        if isinstance(unitcell_or_name, UnitCell):
            self.unitcell = unitcell_or_name
        else:
            self.unitcell = UnitCellPlugin(unitcell_or_name, **kwargs)

    @property
    def replication_matrix(self):
        """3x3 integer matrix used to replicate the unit cell.

        This matrix specifies how the basic unit cell is stacked to form
        the expanded unit cell.

        Returns:
            np.ndarray: 3x3 integer matrix.
        """
        return self._replication_matrix

    @replication_matrix.setter
    def replication_matrix(self, replication_matrix):
        """Set the unit-cell replication matrix.

        Changing this property clears the cache of all dependent reactive properties.
        If ``unitcell`` is already set, expanded-cell dimensions are logged at INFO
        (same as when assigning ``unitcell``).

        Args:
            replication_matrix: 3x3 integer matrix.
        """
        self._replication_matrix = np.array(replication_matrix).reshape(3, 3)
        i, j, k = self._replication_matrix
        self.logger.debug(f"    {i=}")
        self.logger.debug(f"    {j=}")
        self.logger.debug(f"    {k=}")
        self._log_expanded_cell_dimensions()
        # キャッシュをクリア（replication_matrixに依存するすべてのタスクを再計算させる）
        self.engine.cache.clear()

    def set_replication_matrix(self, replication_matrix):
        """Set the replication matrix (reactive-property-friendly wrapper).

        Using this method instead of assignment (``genice.replication_matrix = ...``)
        makes it explicit that the replication matrix is part of the reactive
        configuration.

        Args:
            replication_matrix: 3x3 integer matrix (list-of-lists or ``ndarray``).
        """
        self.replication_matrix = replication_matrix

    def _get_inputs(self) -> Dict[str, Any]:
        """Return the ``inputs`` dictionary passed to ``engine.resolve()``."""
        return {
            "unitcell": self.unitcell,
            "replication_matrix": self.replication_matrix,
            "pol_loop_1": self.pol_loop_1,
            "pol_loop_2": self.pol_loop_2,
            "target_pol": self.target_pol,
            "seed": self.seed,
            "spot_anions": self.spot_anions,
            "spot_cations": self.spot_cations,
            "spot_hydroniums": self.spot_hydroniums,
            "spot_hydroxides": self.spot_hydroxides,
            "bjerrum_L_edges": self.bjerrum_L_edges,
            "bjerrum_D_edges": self.bjerrum_D_edges,
        }

    def __getattr__(self, name: str):
        """Resolve access to reactive properties automatically.

        This method exposes task functions registered in ``DependencyEngine``
        as properties. Accessing such a property automatically resolves its
        dependencies and executes the required computations.

        Example:
            >>> genice = GenIce3(unitcell=my_unitcell)
            >>> digraph = genice.digraph  # digraph and its dependencies are computed here

        Args:
            name: Property name (task-function name) to access.

        Returns:
            Computed value of the requested property.

        Raises:
            AttributeError: If the requested property does not exist.
            ConfigurationError: If required inputs are not configured.
        """
        # DependencyEngineに登録されているタスクかチェック
        if name in self.engine.registry:
            return self.engine.resolve(name, self._get_inputs())

        # それ以外は通常のAttributeErrorを発生
        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute '{name}'"
        )

    def water_molecules(self, water_model: Molecule) -> Dict[int, Molecule]:
        """Return oriented and positioned water molecules for water-like sites.

        Args:
            water_model: Template water molecule (sites, labels, etc.).

        Returns:
            Dict[int, Molecule]: Mapping from site index (node index) to
            ``Molecule``. Ion sites are not included.
        """
        mols = {}
        for site in range(len(self.lattice_sites)):
            occ = self.site_occupants[site]
            # hydroniumやhydroxideはwater-likeではない。
            is_water_like = occ == "water"
            if is_water_like:
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
        """Generate the list of guest molecules from ``guests`` and ``spot_guests``."""
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
        """Build a molecular ion (and optional modifier groups) at a given lattice site.

        Args:
            site_index: Lattice-site node index.
            molecule: Name of the molecular-ion plugin (for example, ``"ammonium"``).
            groups: Mapping from adjacent cage ID to group name (for spot-cation modifiers).

        Returns:
            ``Molecule`` placed in Cartesian coordinates (atom names are in ``labels``).
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
        """Return the merged spot-cation group mapping (on demand).

        Expands unit-cell ``cation_groups`` to the supercell and merges them
        with ``spot_cation_groups`` provided via CLI/API.
        """
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

    def build_hydronium(self, site_index: int) -> Molecule:
        """Build an H3O+ molecule at the given site."""
        sites = []
        labels = ["Cn", "Hn", "Hn", "Hn"]
        OH = 0.1
        sites.append(np.zeros(3))
        neighbors = list(self.digraph.successors(site_index))
        if len(neighbors) != 3:
            raise ValueError("H3O+ must have 3 neighbors.")
        for neighbor in neighbors:
            direction = self.lattice_sites[neighbor] - self.lattice_sites[site_index]
            direction -= np.floor(direction + 0.5)
            direction = direction @ self.cell
            direction *= OH / np.linalg.norm(direction)
            sites.append(direction)
        return Molecule(
            name="H3O",
            sites=np.array(sites) + self.lattice_sites[site_index] @ self.cell,
            labels=labels,
            is_water=False,
        )

    def build_hydroxide(self, site_index: int) -> Molecule:
        """Build an OH- molecule at the given site."""
        sites = []
        labels = ["Nx", "Hx"]
        OH = 0.1
        sites.append(np.zeros(3))
        neighbors = list(self.digraph.successors(site_index))
        if len(neighbors) != 1:
            raise ValueError(f"OH- must have 1 neighbor. {site_index=} {neighbors=}")
        direction = self.lattice_sites[neighbors[0]] - self.lattice_sites[site_index]
        direction -= np.floor(direction + 0.5)
        direction = direction @ self.cell
        direction *= OH / np.linalg.norm(direction)
        sites.append(direction)
        return Molecule(
            name="OH",
            sites=np.array(sites) + self.lattice_sites[site_index] @ self.cell,
            labels=labels,
            is_water=False,
        )

    def substitutional_ions(self) -> Dict[int, Molecule]:
        """Merge unit-cell and spot ions into a site-index -> molecule mapping."""
        # 単位胞由来の group 指定も含めた「実効的な」spot_cation_groups をここで on-demand に組み立てて使う

        # 前提条件: anions, cations, hydroniums, hydroxidesのサイトに重複がないこと。
        # そうでない場合は、エラーを返す。
        if len(set(self.spot_hydroniums) & set(self.spot_hydroxides)) > 0:
            raise ValueError("hydroniums and hydroxides must not have the same site.")
        if len(set(self.anions) & set(self.cations)) > 0:
            raise ValueError("anions and cations must not have the same site.")
        if len(set(self.spot_hydroniums) & set(self.cations)) > 0:
            raise ValueError("hydroniums and cations must not have the same site.")
        if len(set(self.spot_hydroxides) & set(self.cations)) > 0:
            raise ValueError("hydroxides and cations must not have the same site.")

        ions: Dict[int, Molecule] = {}
        for site_index in self.spot_hydroniums:
            ions[site_index] = self.build_hydronium(site_index)
        for site_index in self.spot_hydroxides:
            ions[site_index] = self.build_hydroxide(site_index)
        # ならべかえはここではしない。formatterにまかせる。
        for site_index, molecule in self.anions.items():
            ions[site_index] = self.build_molecular_ion(site_index, molecule)
        effective_groups = self._effective_spot_cation_groups()
        for site_index, molecule in self.cations.items():
            # cationには腕がつく可能性がある。
            groups = effective_groups.get(site_index, {})
            ions[site_index] = self.build_molecular_ion(site_index, molecule, groups)
        self.logger.info(f"{ions=}")
        return ions

    def dope_anions(self, anions: Dict[int, Molecule]) -> None:
        """Overwrite anion configuration with a site-index -> molecule mapping (API/test use)."""
        for site_index, molecule in anions.items():
            self.anions[site_index] = molecule

    def dope_cations(self, cations: Dict[int, Molecule]) -> None:
        """Overwrite cation configuration with a site-index -> molecule mapping (API/test use)."""
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
        """Return the list of properties exposed as public API.

        Returns:
            list: List of public API property names.
        """
        return cls.PUBLIC_API_PROPERTIES.copy()

    def list_all_reactive_properties(self):
        """List all reactive properties (tasks registered in ``DependencyEngine``).

        Returns:
            dict: Mapping from property name to task function.
        """
        return self.engine.registry.copy()

    def list_public_reactive_properties(self):
        """List only reactive properties that are part of the public API.

        Returns:
            dict: Mapping from property name to task function.
        """
        all_reactive = self.list_all_reactive_properties()
        public_names = set(self.PUBLIC_API_PROPERTIES)
        return {
            name: func for name, func in all_reactive.items() if name in public_names
        }

    @classmethod
    def list_settable_reactive_properties(cls):
        """List reactive properties that have a setter."""
        return {
            name: prop
            for name, prop in inspect.getmembers(
                cls, lambda x: isinstance(x, property) and x.fset is not None
            )
        }

    @classmethod
    def list_public_settable_reactive_properties(cls):
        """List public reactive properties that have a setter."""
        return {
            name: prop
            for name, prop in cls.list_settable_reactive_properties().items()
            if name in cls.PUBLIC_API_PROPERTIES
        }
