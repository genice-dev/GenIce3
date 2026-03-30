import io

import numpy as np

try:
    import py3Dmol
except ModuleNotFoundError as e:
    raise ModuleNotFoundError(
        "This example needs py3dmol. Install with: pip install py3dmol "
    ) from e

from genice3.genice import GenIce3
from genice3.plugin import Exporter

genice = GenIce3(
    seed=114,
)
genice.set_unitcell("CS2")

gro = Exporter("gromacs").dumps(genice, water_model="3site")

view = py3Dmol.view()
view.addModel(gro, "gro")
view.setStyle({"stick": {}})
view.addUnitCell()
view.zoomTo()
view.show()
