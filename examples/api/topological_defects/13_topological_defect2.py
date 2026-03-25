"""
Example of embedding topological defects (Bjerrum defects) by specifying positions.
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

# Specify the desired defect positions in fractional coordinates (two points each)
# and convert them into cell coordinates.
celli = np.linalg.inv(genice.cell)
D_positions = np.array([[0.0, 0.0, 0.0], [1.0, 1.0, 1.0]]) @ celli
L_positions = np.array([[1.0, 0.0, 0.0], [2.0, 1.0, 1.0]]) @ celli
D_edges = find_nearest_edges_pbc(
    D_positions, genice.graph, genice.lattice_sites, genice.cell
)
L_edges = find_nearest_edges_pbc(
    L_positions, genice.graph, genice.lattice_sites, genice.cell
)

genice.add_bjerrum_D(D_edges)
genice.add_bjerrum_L(L_edges)

Exporter("gromacs").dump(
    genice,
    water_model="3site",
)
