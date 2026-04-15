from genice3.genice import GenIce3
from genice3.plugin import Exporter

# Corresponding command:
# python3 -m genice3.cli.genice prism \
#   --circum 6 1 \
#   --axial -2 10 \
#   --x f \
#   --y a \
#   --exporter gromacs :water_model 4site \
#   --seed 42
genice = GenIce3(seed=42)
genice.set_unitcell(
    "prism",
    circum=(6, 1),
    axial=(-2, 10),
    x="f",
    y="a",
)

Exporter("gromacs").dump(genice, water_model="4site")
