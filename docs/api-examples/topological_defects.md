**Topological defects** (Bjerrum defects, H3O⁺, OH⁻).

- `12_topological_defect.py`  
  - Introduce hydronium (H3O⁺) and hydroxide (OH⁻) defects at specified coordinates.

- `13_topological_defect2.py`  
  - Introduce Bjerrum L and D defects at specified coordinates.

Additional implementations for the same topics (e.g., CLI- or config-file–driven variants) may be added here in the future.

---

## Sample code

### 12_topological_defect

[`12_topological_defect.py`](https://github.com/genice-dev/GenIce3/blob/main/examples/api/topological_defects/12_topological_defect.py)

```python
"""
トポロジカル欠陥（Hydronium/Hydroxide）を座標指定で埋め込むサンプル。
"""

from __future__ import annotations

from logging import basicConfig, INFO

import numpy as np

from genice3.genice import GenIce3
from genice3.plugin import Exporter
from genice3.util import find_nearest_sites_pbc

# -----------------------------------------------------------------------------
# サンプル本体
# -----------------------------------------------------------------------------

basicConfig(level=INFO)

genice = GenIce3(
    replication_matrix=np.array([[2, 0, 0], [0, 2, 0], [0, 0, 2]]),
)
genice.set_unitcell("A15")

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
```

### 13_topological_defect2

[`13_topological_defect2.py`](https://github.com/genice-dev/GenIce3/blob/main/examples/api/topological_defects/13_topological_defect2.py)

```python
"""
トポロジカル欠陥（Bjerrum）を座標指定で埋め込むサンプル。
"""

from __future__ import annotations

from logging import basicConfig, INFO

import numpy as np

from genice3.genice import GenIce3
from genice3.plugin import Exporter
from genice3.util import find_nearest_edges_pbc

# -----------------------------------------------------------------------------
# サンプル本体
# -----------------------------------------------------------------------------

basicConfig(level=INFO)

genice = GenIce3(
    replication_matrix=np.array([[2, 0, 0], [0, 2, 0], [0, 0, 2]]),
)
genice.set_unitcell("A15")

# 欠陥を置きたい位置を分数座標で指定（各 2 点ずつ）セル座標に変換して。
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
```
