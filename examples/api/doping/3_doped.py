from logging import basicConfig, DEBUG, INFO
import numpy as np
from genice3.genice import GenIce3
from genice3.plugin import Exporter, Molecule

# Corresponding CLI command:
# genice3 "A15[shift=(0.1,0.1,0.1), anion.0=Cl, cation.6=Na, density=0.8]" \
#   --rep 2 2 2 \
#   --spot_anion 1=Cl --spot_anion 35=Br \
#   --spot_cation 1=Na --spot_cation 35=K \
#   --exporter gromacs :water_model 4site \
#   --seed 42 --pol_loop_1 2000 -D

basicConfig(level=INFO)

# Create a GenIce3 instance.
# seed: random seed.
# pol_loop_1: number of depolarization loop iterations.
# replication_matrix: replication matrix (here a 2x2x2 diagonal matrix).
# spot_anions: replace specific water molecules with anions (water index -> ion name). CLI: -A / --spot_anion
# spot_cations: replace specific water molecules with cations (water index -> ion name). CLI: -C / --spot_cation
# Note: the GenIce3 constructor does not take a debug flag (logging level is set via basicConfig).
genice = GenIce3(
    seed=42,
    pol_loop_1=2000,
    replication_matrix=np.array([[2, 0, 0], [0, 2, 0], [0, 0, 2]]),
    spot_anions={
        1: "Cl",
    },
    spot_cations={
        51: "Na",
    },
)

# Set the unit cell.
# shift: shift in fractional coordinates.
# anion: replace lattice sites in the unit cell with anions (site index -> ion name). CLI: -a / --anion
# cation: replace lattice sites in the unit cell with cations (site index -> ion name). CLI: -c / --cation
# density: density in g/cm³.
# If cage information is needed, you can use Exporter("cage_survey").dump(genice, file) to output JSON.
genice.set_unitcell(
    "A15",
    shift=(0.1, 0.1, 0.1),
    anion={15: "Cl"},
    cation={21: "Na"},
    density=0.8,
)


# Output using the exporter.
Exporter("gromacs").dump(
    genice,
    water_model="4site",
)
