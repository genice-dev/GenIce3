# Example: GRO to PDB and analysis via MDAnalysis

This category is included in **`API.ipynb`** through the `CATEGORIES` list in `scripts/build_api_notebook.py` (run `make api-notebook`). In the notebook, install **`MDAnalysis`** and **`matplotlib`** using the **Optional: MDAnalysis** cell after **Installation**, then run **Setup** and the cells below.

**`MDAnalysis`** and **`matplotlib`** (for plotting) are **not** core dependencies of GenIce3. Install them only when you use the scripts here, for example:

- From the repository root (recommended): `pip install ".[mdanalysis]"`
- If you installed `genice3` from PyPI: `pip install "genice3[mdanalysis]"`
- Standalone: `pip install MDAnalysis matplotlib`
- One-line list for `examples/api`: `pip install -r ../requirements-mdanalysis.txt` (from `examples/api`)

To use MDAnalysis as a GenIce3 **exporter** (e.g. `Exporter("pdb")`), install **[genice3-mdanalysis](https://github.com/genice-dev/genice3-mdanalysis)** separately. The examples in this repository use MDAnalysis’ standard `Universe.write` only.

## Running standalone (under `examples/api`)

After installing dependencies from the repository root, either:

```bash
# Repo root as cwd (e.g. 1h_unit.pdb written to cwd)
python examples/api/mdanalysis/15_mdanalysis.py
```

```bash
cd examples/api
make mdanalysis
```

`make mdanalysis` uses the Poetry environment’s Python from the repo root; install `MDAnalysis` into that venv first (e.g. `pip install '.[mdanalysis]'` via Poetry’s pip, or `poetry run pip install MDAnalysis`).

To enable the extra with Poetry: from the repo root, `poetry install --extras mdanalysis` (if your Poetry version reads `[project.optional-dependencies]`).

---

## Sample code

### 15_mdanalysis

[`15_mdanalysis.py`](https://github.com/genice-dev/GenIce3/blob/main/examples/api/mdanalysis/15_mdanalysis.py)

```python
import io

import numpy as np

try:
    import MDAnalysis as mda
    from MDAnalysis.analysis.rdf import InterRDF
except ModuleNotFoundError as e:
    raise ModuleNotFoundError(
        "This example needs MDAnalysis. Install with: pip install MDAnalysis "
        "or pip install 'genice3[mdanalysis]' (from PyPI) / pip install '.[mdanalysis]' (from repo root)."
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
import matplotlib.pyplot as plt

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
```
