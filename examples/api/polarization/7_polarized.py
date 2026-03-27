# How to build a polarized ice sample (1): specify target_pol in the constructor.
# Corresponding command: 7_polarized_1.sh or 7_polarized_1_flat.sh

import numpy as np
from genice3.genice import GenIce3
from genice3.plugin import Exporter

genice = GenIce3(
    seed=114,
    pol_loop_1=1000,
    pol_loop_2=10000,
    replication_matrix=np.diag([6, 6, 6]),
    target_pol=np.array([0.0, 0.0, 72.0]),
)
genice.set_unitcell("one", layers="hh")

Exporter("_pol").dump(genice)
