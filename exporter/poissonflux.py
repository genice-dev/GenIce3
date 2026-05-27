# coding: utf-8
"""
Dirac fractional web on the hydrogen-bond digraph.

Default: minimum-cost flow (non-negative flux, respects H-bond orientation).
Optional: Poisson / minimum L2 norm on the undirected graph (bidirectional arcs).
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from io import TextIOWrapper
from logging import DEBUG, getLogger
from typing import Any, Dict, List, Literal, Sequence, Tuple

import networkx as nx
import numpy as np
from scipy import sparse
from scipy.sparse.linalg import spsolve

from genice3.genice import GenIce3

logger = getLogger(__name__)

SolverName = Literal["mcf", "poisson"]

desc = {
    "brief": "Visualize Dirac fractional web (min-cost flow on digraph, or Poisson).",
    "usage": """
Usage: genice3 UNITCELL -e poissonflux [:option value ...]

options:
    solver=mcf       mcf (default): min-cost flow on genice.digraph, w >= 0.
                     poisson: L phi = rho on undirected graph (bidirectional arcs).
    arc_capacity=inf capacity per directed arc for mcf (default: inf).
                     Set to 1 to forbid arc overlap (unit flow per arc).
    w_min=0.05       Minimum |w|/max|w| to draw an arc (default 0.05).
    width_scale=8    Line width scale for fractional-web arcs.
    show_frame=1     Draw undirected H-bond frame (0 or 1, default 1).
    show_digraph=0   Overlay ice-rule digraph in green (0 or 1, default 0).
""",
}

format_desc = {
    "aliases": ["poissonflux", "fractionalweb", "fweb"],
    "application": "[Plotly](https://plotly.com/python/)",
    "extension": ".html",
    "water": "none",
    "solute": "none",
    "hb": "o",
    "suboptions": "solver, arc_capacity, w_min, width_scale, show_frame, show_digraph.",
    "remarks": "Fractional web: default min-cost flow on digraph; optional Poisson on graph.",
}


@dataclass(frozen=True)
class FractionalWebResult:
    """Flow solution on directed arcs."""

    solver: SolverName
    nodes: List[int]
    arcs: List[Tuple[int, int]]
    rho: np.ndarray
    phi: np.ndarray
    w: np.ndarray
    residual_norm: float


def _sorted_nodes(graph: nx.Graph) -> List[int]:
    return sorted(graph.nodes())


def build_arcs_from_digraph(digraph: nx.DiGraph) -> Tuple[List[int], List[Tuple[int, int]]]:
    """Stable list of directed arcs present in the hydrogen-bond digraph."""
    nodes = _sorted_nodes(digraph)
    arcs = [(int(i), int(j)) for i, j in sorted(digraph.edges())]
    return nodes, arcs


def build_arcs_from_graph(graph: nx.Graph) -> Tuple[List[int], List[Tuple[int, int]]]:
    """Both orientations per undirected edge (Poisson solver)."""
    nodes = _sorted_nodes(graph)
    arcs: List[Tuple[int, int]] = []
    for i, j in sorted(graph.edges()):
        if i > j:
            i, j = j, i
        arcs.extend([(int(i), int(j)), (int(j), int(i))])
    return nodes, arcs


def build_incidence(
    nodes: Sequence[int], arcs: Sequence[Tuple[int, int]]
) -> sparse.csr_matrix:
    """B (n_nodes x n_arcs): (B @ w)[i] = net outflow at node i."""
    index = {node: k for k, node in enumerate(nodes)}
    n = len(nodes)
    m = len(arcs)
    rows: List[int] = []
    cols: List[int] = []
    data: List[float] = []
    for e, (tail, head) in enumerate(arcs):
        rows.extend([index[tail], index[head]])
        cols.extend([e, e])
        data.extend([-1.0, 1.0])
    return sparse.csr_matrix((data, (rows, cols)), shape=(n, m))


def build_rho(
    nodes: Sequence[int],
    bjerrum_D_edges: Sequence[Tuple[int, int]],
    bjerrum_L_edges: Sequence[Tuple[int, int]],
) -> np.ndarray:
    """Node outflow source: Bjerrum D at i -> +1, Bjerrum L at i -> -1."""
    index = {node: k for k, node in enumerate(nodes)}
    rho = np.zeros(len(nodes), dtype=float)
    for i, _j in bjerrum_D_edges or []:
        rho[index[i]] += 1.0
    for i, _j in bjerrum_L_edges or []:
        rho[index[i]] -= 1.0
    return rho


def build_mcf_demand(
    bjerrum_D_edges: Sequence[Tuple[int, int]],
    bjerrum_L_edges: Sequence[Tuple[int, int]],
) -> Dict[int, int]:
    """NetworkX demand: negative = send, positive = receive."""
    demand: Dict[int, int] = {}
    for i, _j in bjerrum_D_edges or []:
        demand[int(i)] = demand.get(int(i), 0) - 1
    for i, _j in bjerrum_L_edges or []:
        demand[int(i)] = demand.get(int(i), 0) + 1
    return demand


def _check_charge_neutrality(rho: np.ndarray) -> None:
    total = float(np.sum(rho))
    if abs(total) > 1e-10:
        raise ValueError(
            f"Charge neutrality violated: sum(rho)={total}. "
            "Bjerrum D (+1) and L (-1) counts must balance."
        )


def _net_outflow(
    nodes: Sequence[int], arcs: Sequence[Tuple[int, int]], w: np.ndarray
) -> np.ndarray:
    """outflow[i] = sum_{i->j} w_ij - sum_{j->i} w_ji."""
    index = {node: k for k, node in enumerate(nodes)}
    out = np.zeros(len(nodes), dtype=float)
    for e, (tail, head) in enumerate(arcs):
        out[index[tail]] += w[e]
        out[index[head]] -= w[e]
    return out


def _flow_residual(
    nodes: Sequence[int],
    arcs: Sequence[Tuple[int, int]],
    w: np.ndarray,
    rho: np.ndarray,
    *,
    solver: SolverName,
) -> float:
    if solver == "mcf":
        return float(np.linalg.norm(_net_outflow(nodes, arcs, w) - rho))
    B = build_incidence(nodes, arcs)
    return float(np.linalg.norm(B @ w - rho))


def solve_poisson(
    graph: nx.Graph,
    rho: np.ndarray,
    *,
    anchor: int | None = None,
) -> Tuple[np.ndarray, np.ndarray, float, List[int], List[Tuple[int, int]]]:
    """L phi = rho on undirected graph; w = B^T phi (may be negative on some arcs)."""
    nodes, arcs = build_arcs_from_graph(graph)
    if anchor is None:
        anchor = nodes[0]
    B = build_incidence(nodes, arcs)
    L = (B @ B.T).tocsr()
    n = len(nodes)
    anchor_idx = nodes.index(anchor)
    free = [k for k in range(n) if k != anchor_idx]
    Lf = L[free, :][:, free]
    rhof = rho[free]
    phif = spsolve(Lf, rhof)
    phi = np.zeros(n, dtype=float)
    phi[free] = np.asarray(phif, dtype=float).ravel()
    w = np.asarray(B.T @ phi).ravel()
    residual = _flow_residual(nodes, arcs, w, rho, solver="poisson")
    return phi, w, residual, nodes, arcs


def solve_min_cost_flow(
    digraph: nx.DiGraph,
    demand: Dict[int, int],
    rho: np.ndarray,
    *,
    cost: int = 1,
    arc_capacity: float = float("inf"),
) -> Tuple[np.ndarray, float, List[int], List[Tuple[int, int]]]:
    """Non-negative min-cost flow on digraph; unit cost per arc by default."""
    nodes, arcs = build_arcs_from_digraph(digraph)
    G = nx.DiGraph()
    for i, j in arcs:
        G.add_edge(i, j, weight=cost, capacity=arc_capacity)
    nx.set_node_attributes(
        G, {n: demand.get(n, 0) for n in nodes}, "demand"
    )
    if abs(sum(demand.values())) > 1e-10:
        raise ValueError(f"MCF demands must sum to 0, got {sum(demand.values())}.")
    try:
        flow_dict = nx.min_cost_flow(G)
    except nx.NetworkXError as exc:
        raise ValueError(
            "Minimum-cost flow is infeasible on genice.digraph "
            "(no oriented path from D sources to L sinks?)."
        ) from exc
    w = np.zeros(len(arcs), dtype=float)
    arc_index = {arc: e for e, arc in enumerate(arcs)}
    for u, nbrs in flow_dict.items():
        for v, f in nbrs.items():
            e = arc_index.get((int(u), int(v)))
            if e is not None:
                w[e] = float(f)
    residual = _flow_residual(nodes, arcs, w, rho, solver="mcf")
    return w, residual, nodes, arcs


def log_all_arc_weights(result: FractionalWebResult) -> None:
    """Log every directed arc weight at DEBUG."""
    root = getLogger()
    if not (logger.isEnabledFor(DEBUG) or root.isEnabledFor(DEBUG)):
        return
    w = result.w
    w_max = float(np.max(np.abs(w))) if len(w) else 0.0
    logger.debug(
        "Fractional web [%s] arc weights (%d arcs, max|w|=%.6g):",
        result.solver,
        len(result.arcs),
        w_max,
    )
    for e, (tail, head) in enumerate(result.arcs):
        wt = float(w[e])
        rel = abs(wt) / w_max if w_max > 0 else 0.0
        logger.debug(
            "  arc[%4d] %d -> %d  w=%+.8g  |w|/max|w|=%.6g",
            e,
            tail,
            head,
            wt,
            rel,
        )


def compute_fractional_web(
    genice: GenIce3,
    *,
    solver: SolverName = "mcf",
    arc_capacity: float | None = None,
) -> FractionalWebResult:
    """Build rho from Bjerrum defects and solve for edge fluxes."""
    solver = str(solver).lower()  # type: ignore[assignment]
    if solver not in ("mcf", "poisson"):
        raise ValueError(f"Unknown solver: {solver!r} (use mcf or poisson).")

    if solver == "mcf":
        digraph = genice.digraph
        nodes, arcs = build_arcs_from_digraph(digraph)
        rho = build_rho(nodes, genice.bjerrum_D_edges, genice.bjerrum_L_edges)
        _check_charge_neutrality(rho)
        demand = build_mcf_demand(genice.bjerrum_D_edges, genice.bjerrum_L_edges)
        w, residual, nodes, arcs = solve_min_cost_flow(
            digraph,
            demand,
            rho,
            arc_capacity=float("inf") if arc_capacity is None else float(arc_capacity),
        )
        phi = np.full(len(nodes), np.nan)
        result = FractionalWebResult(
            solver="mcf",
            nodes=nodes,
            arcs=arcs,
            rho=rho,
            phi=phi,
            w=w,
            residual_norm=residual,
        )
    else:
        graph = genice.graph
        nodes, arcs = build_arcs_from_graph(graph)
        rho = build_rho(nodes, genice.bjerrum_D_edges, genice.bjerrum_L_edges)
        _check_charge_neutrality(rho)
        phi, w, residual, nodes, arcs = solve_poisson(graph, rho, anchor=nodes[0])
        result = FractionalWebResult(
            solver="poisson",
            nodes=nodes,
            arcs=arcs,
            rho=rho,
            phi=phi,
            w=w,
            residual_norm=residual,
        )

    w_max = float(np.max(np.abs(result.w))) if len(result.w) else 0.0
    n_pos = int(np.sum(result.w > 1e-12))
    n_neg = int(np.sum(result.w < -1e-12))
    logger.info(
        "Fractional web [%s]: %d nodes, %d arcs, ||Bw-rho||=%.3e, "
        "max|w|=%.4f, positive=%d negative=%d",
        result.solver,
        len(nodes),
        len(arcs),
        result.residual_norm,
        w_max,
        n_pos,
        n_neg,
    )
    log_all_arc_weights(result)
    return result


def _bool_option(value: Any, default: bool) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    return str(value).lower() not in ("0", "false", "no", "")


def draw_fractional_web(
    genice: GenIce3,
    result: FractionalWebResult,
    *,
    w_min: float = 0.05,
    width_scale: float = 8.0,
    show_frame: bool = True,
    show_digraph: bool = False,
):
    """Plotly 3D figure: nodes, optional frame/digraph, weighted fractional-web arcs."""
    import plotly.graph_objects as go

    graph = genice.graph
    pos = np.array([genice.lattice_sites[i] for i in result.nodes])
    w = result.w
    w_max = float(np.max(np.abs(w))) if len(w) else 1.0
    if w_max < 1e-15:
        w_max = 1.0

    defect_D = {i for i, _j in genice.bjerrum_D_edges or []}
    defect_L = {i for i, _j in genice.bjerrum_L_edges or []}

    traces: List[Any] = []

    if show_frame:
        for i, j in sorted(graph.edges()):
            if i > j:
                i, j = j, i
            pi = result.nodes.index(i)
            pj = result.nodes.index(j)
            d = pos[pj] - pos[pi]
            d -= np.floor(d + 0.5)
            seg = np.array([pos[pi], pos[pi] + d])
            traces.append(
                go.Scatter3d(
                    x=seg[:, 0],
                    y=seg[:, 1],
                    z=seg[:, 2],
                    mode="lines",
                    line=dict(color="lightgray", width=1),
                    hoverinfo="skip",
                    showlegend=False,
                )
            )

    if show_digraph and result.solver != "mcf":
        dg = genice.digraph
        for i, j in dg.edges():
            if i not in result.nodes or j not in result.nodes:
                continue
            pi, pj = result.nodes.index(i), result.nodes.index(j)
            d = pos[pj] - pos[pi]
            d -= np.floor(d + 0.5)
            seg = np.array([pos[pi], pos[pi] + d])
            traces.append(
                go.Scatter3d(
                    x=seg[:, 0],
                    y=seg[:, 1],
                    z=seg[:, 2],
                    mode="lines",
                    line=dict(color="green", width=2),
                    hoverinfo="skip",
                    showlegend=False,
                )
            )

    for e, (tail, head) in enumerate(result.arcs):
        wt = w[e]
        if wt <= 0 and result.solver == "mcf":
            continue
        if abs(wt) < w_min * w_max:
            continue
        pi, pj = result.nodes.index(tail), result.nodes.index(head)
        d = pos[pj] - pos[pi]
        d -= np.floor(d + 0.5)
        seg = np.array([pos[pi], pos[pi] + d])
        width = max(1.0, width_scale * abs(wt) / w_max)
        if result.solver == "mcf":
            color = "crimson"
        else:
            color = "crimson" if wt > 0 else "dodgerblue"
        traces.append(
            go.Scatter3d(
                x=seg[:, 0],
                y=seg[:, 1],
                z=seg[:, 2],
                mode="lines",
                line=dict(color=color, width=width),
                name=f"w={wt:.3f} ({tail}->{head})",
                hovertext=f"{tail}->{head}: w={wt:.4f}",
                hoverinfo="text",
                showlegend=False,
            )
        )

    colors = []
    sizes = []
    for node in result.nodes:
        if node in defect_D:
            colors.append("orange")
            sizes.append(5)
        elif node in defect_L:
            colors.append("purple")
            sizes.append(5)
        else:
            colors.append("blue")
            sizes.append(2)

    traces.append(
        go.Scatter3d(
            x=pos[:, 0],
            y=pos[:, 1],
            z=pos[:, 2],
            mode="markers",
            marker=dict(size=sizes, color=colors),
            text=[str(n) for n in result.nodes],
            hoverinfo="text",
            name="nodes",
        )
    )

    title = (
        f"Fractional web [{result.solver}] "
        f"(||Bw-rho||={result.residual_norm:.2e}, D={len(defect_D)}, L={len(defect_L)})"
    )
    return go.Figure(data=traces, layout=dict(title=title))


def figure(genice: GenIce3, **options):
    """Compute fractional web and return a Plotly figure."""
    solver = str(options.get("solver", "mcf")).lower()
    arc_capacity_opt = options.get("arc_capacity", None)
    arc_capacity: float | None
    if arc_capacity_opt is None:
        arc_capacity = None
    elif isinstance(arc_capacity_opt, (int, float)):
        arc_capacity = float(arc_capacity_opt)
    else:
        s = str(arc_capacity_opt).strip().lower()
        none_tokens = {"", "none", "inf", "infinity"}
        arc_capacity = None if s in none_tokens else float(s)

    result = compute_fractional_web(  # type: ignore[arg-type]
        genice, solver=solver, arc_capacity=arc_capacity
    )
    return draw_fractional_web(
        genice,
        result,
        w_min=float(options.get("w_min", 0.05)),
        width_scale=float(options.get("width_scale", 8)),
        show_frame=_bool_option(options.get("show_frame"), True),
        show_digraph=_bool_option(options.get("show_digraph"), False),
    )


def dump(genice: GenIce3, file: TextIOWrapper = sys.stdout, **options):
    """Write interactive HTML."""
    fig = figure(genice, **options)
    fig.write_html(file, include_plotlyjs="cdn")
