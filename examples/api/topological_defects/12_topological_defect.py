"""
Example of embedding topological defects (hydronium/hydroxide) by specifying positions.
"""

from __future__ import annotations

from logging import basicConfig, INFO

import numpy as np

from genice3.genice import GenIce3
from genice3.plugin import Exporter
from genice3.util import find_nearest_sites_pbc

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
H3O_positions = np.array([[0.0, 0.0, 0.0], [1.0, 1.0, 1.0]]) @ celli
OH_positions = np.array([[1.0, 0.0, 0.0], [2.0, 1.0, 1.0]]) @ celli
H3O_sites = find_nearest_sites_pbc(H3O_positions, genice.lattice_sites, genice.cell)
OH_sites = find_nearest_sites_pbc(OH_positions, genice.lattice_sites, genice.cell)

genice.add_spot_hydronium(H3O_sites)
genice.add_spot_hydroxide(OH_sites)

Exporter("gromacs").dump(
    genice,
    water_model="3site",
)
