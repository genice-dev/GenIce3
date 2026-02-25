"""
トポロジカル欠陥（Hydronium/Hydroxide）を座標指定で埋め込むサンプル。
"""

from __future__ import annotations

from logging import basicConfig, INFO

import numpy as np

from genice3.genice import GenIce3
from genice3.plugin import UnitCell, Exporter
from genice3.util import find_nearest_sites_pbc

# -----------------------------------------------------------------------------
# サンプル本体
# -----------------------------------------------------------------------------

basicConfig(level=INFO)

genice = GenIce3(
    replication_matrix=np.array([[2, 0, 0], [0, 2, 0], [0, 0, 2]]),
)
genice.unitcell = UnitCell("A15")

# 欠陥を置きたい位置を分数座標で指定（各 2 点ずつ）セル座標に変換して。
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
