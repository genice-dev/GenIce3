import io

import numpy as np

try:
    import MDAnalysis as mda
    from MDAnalysis.analysis.rdf import InterRDF
    import matplotlib.pyplot as plt
except ModuleNotFoundError as e:
    raise ModuleNotFoundError(
        "This example needs MDAnalysis and matplotlib. Install with: pip install MDAnalysis matplotlib "
    ) from e

from genice3.genice import GenIce3
from genice3.plugin import Exporter

genice = GenIce3(
    seed=114,
)
genice.set_unitcell("CRN1")

gro = Exporter("gromacs").dumps(genice, water_model="3site")

# use MDAnalysis
universe = mda.Universe(io.StringIO(gro), format="GRO")

# RDF (O–O; ice/water oxygen)

o = universe.select_atoms("name O")
h = universe.select_atoms("name H")
rdf_oo = InterRDF(o, o, nbins=100, range=(1.1, 6.0))
rdf_oh = InterRDF(o, h, nbins=100, range=(1.1, 6.0))
rdf_hh = InterRDF(h, h, nbins=100, range=(1.1, 6.0))
rdf_oo.run()
rdf_oh.run()
rdf_hh.run()
plt.plot(rdf_oo.results.bins, rdf_oo.results.rdf)
plt.plot(rdf_oh.results.bins, rdf_oh.results.rdf)
plt.plot(rdf_hh.results.bins, rdf_hh.results.rdf)
plt.legend(["O–O", "O–H", "H–H"])
plt.savefig("rdf.png")
plt.close()

# Save as PDB
universe.atoms.write("1h_unit.pdb")
