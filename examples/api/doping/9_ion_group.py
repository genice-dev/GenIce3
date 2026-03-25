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
# pol_loop_1: maximum number of iterations for the first polarization convergence stage.
# replication_matrix: replication matrix (here a 2x2x2 diagonal matrix).
# spot_anions / spot_cations: water-molecule index -> ion name. CLI: -A / --spot_anion, -C / --spot_cation
# spot_cation_groups: group suboption (site -> {cage ID -> group name}).
# The nested \"ion\" key used in YAML/CLI is not needed in the Python API (it is passed as a separate argument).
genice = GenIce3(
    seed=42,
    pol_loop_1=2000,
    replication_matrix=np.array([[2, 0, 0], [0, 2, 0], [0, 0, 2]]),
    spot_anions={1: "Cl"},
    spot_cations={51: "N"},
    spot_cation_groups={
        51: {12: "methyl", 48: "methyl", 49: "methyl", 50: "methyl"},
    },
)

# Set the unit cell.
# anion / cation: replace lattice sites in the unit cell with ions (site index -> ion name). CLI: -a / --anion, -c / --cation
# density: density in g/cm³.
# If cage information is needed, you can use Exporter("cage_survey").dump(genice, file) to output JSON.
genice.set_unitcell("A15", shift=(0.1, 0.1, 0.1), density=0.8)


# Output using the exporter.
Exporter("yaplot").dump(
    genice,
)
