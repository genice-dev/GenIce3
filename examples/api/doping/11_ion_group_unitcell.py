from logging import basicConfig, INFO
import numpy as np
from genice3.genice import GenIce3
from genice3.plugin import Exporter

# corresponding command:
# genice3 A15 --cation 0=N :group 1=methyl 6=methyl 3=methyl 4=methyl \
#   --anion 2=Cl --rep 2 2 2 --exporter gromacs :water_model 4site

basicConfig(level=INFO)

genice = GenIce3(
    replication_matrix=np.array([[2, 0, 0], [0, 2, 0], [0, 0, 2]]),
    seed=43,
)

# 単位胞内の anion/cation と cation_groups（カチオンの腕の group 指定）
genice.set_unitcell(
    "A15",
    anion={2: "Cl"},
    cation={0: "N"},
    cation_groups={0: {1: "methyl", 6: "methyl", 3: "methyl", 4: "methyl"}},
)

Exporter("gromacs").dump(
    genice,
    water_model="4site",
)
