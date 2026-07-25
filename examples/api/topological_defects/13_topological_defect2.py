"""
Example of embedding topological defects (Bjerrum defects) by specifying positions.

Six D/L pairs (12 defects) in a 2×2×2 A15 supercell — harder than the original
2-pair case for path pairing in ``genice_core.ice_graph`` (MCF connect_engine since 1.6.0).
Positions are chosen so each defect sits on a distinct water site (no duplicate i).
"""

from __future__ import annotations

from logging import basicConfig, INFO

import numpy as np

from genice3.genice import GenIce3
from genice3.plugin import Exporter
from genice3.util import find_nearest_edges_pbc

# -----------------------------------------------------------------------------
# Main example
# -----------------------------------------------------------------------------

basicConfig(level=INFO)

genice = GenIce3(
    replication_matrix=np.array([[2, 0, 0], [0, 2, 0], [0, 0, 2]]),
)
genice.set_unitcell("A15")

# Supercell coordinates (same convention as the original 2-pair example).
celli = np.linalg.inv(genice.cell)

# Six D sources and six L sinks, spread through the cell.
D_frac = np.array(
    [
        [0.0, 0.0, 0.0],
        [1.0, 1.0, 1.0],
        [0.5, 0.0, 1.0],
        [1.5, 0.5, 0.5],
        [0.0, 1.5, 1.5],
        [1.0, 0.5, 1.5],
    ]
)
L_frac = np.array(
    [
        [1.0, 0.0, 0.0],
        [2.0, 1.0, 1.0],
        [0.0, 1.0, 0.0],
        [2.0, 0.0, 2.0],
        [1.5, 1.5, 0.0],
        [0.5, 1.0, 2.0],
    ]
)

D_positions = D_frac @ celli
L_positions = L_frac @ celli

D_edges = find_nearest_edges_pbc(
    D_positions, genice.graph, genice.lattice_sites, genice.cell
)
L_edges = find_nearest_edges_pbc(
    L_positions, genice.graph, genice.lattice_sites, genice.cell
)

print(f"Bjerrum D: {len(D_edges)} edges")
for k, e in enumerate(D_edges):
    print(f"  D[{k}] frac={D_frac[k]} -> {e}")
print(f"Bjerrum L: {len(L_edges)} edges")
for k, e in enumerate(L_edges):
    print(f"  L[{k}] frac={L_frac[k]} -> {e}")

genice.add_bjerrum_D(D_edges)
genice.add_bjerrum_L(L_edges)

Exporter("gromacs").dump(
    genice,
    water_model="3site",
)
