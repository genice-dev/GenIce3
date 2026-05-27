"""
Bjerrum D/L defects (same setup as 13_topological_defect2.py) and poisson-flux visualization.
"""

from __future__ import annotations

from logging import DEBUG, basicConfig
from pathlib import Path

# genice3 インポート前に DEBUG を有効化（import 時の INFO 初期化を上書き）
basicConfig(level=DEBUG, force=True)

import numpy as np

from genice3.genice import GenIce3
from genice3.plugin import Exporter
from genice3.util import find_nearest_edges_pbc

genice = GenIce3(
    replication_matrix=np.array([[2, 0, 0], [0, 2, 0], [0, 0, 2]]),
)
genice.set_unitcell("A15")

celli = np.linalg.inv(genice.cell)
D_positions = np.array([[0.1, 0.1, 0.1], [1.0, 1.0, 1.0]]) @ celli
L_positions = np.array([[1.0, 0.1, 0.1], [2.0, 1.0, 1.0]]) @ celli
D_edges = find_nearest_edges_pbc(
    D_positions, genice.graph, genice.lattice_sites, genice.cell
)
L_edges = find_nearest_edges_pbc(
    L_positions, genice.graph, genice.lattice_sites, genice.cell
)

genice.add_bjerrum_D(D_edges)
genice.add_bjerrum_L(L_edges)

out = Path(__file__).resolve().parent / "poissonflux_a15_2x2x2.html"
with open(out, "w", encoding="utf-8") as f:
    Exporter("poissonflux").dump(genice, f, w_min=0.02, solver="mcf")

print(f"Wrote {out}")
