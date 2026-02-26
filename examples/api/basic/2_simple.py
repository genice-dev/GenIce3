from genice3.genice import GenIce3
from genice3.plugin import Exporter

# corresponding command:
# genice3 A15 --exporter gromacs
genice = GenIce3()
genice.set_unitcell("A15")
Exporter("gromacs").dump(genice)
