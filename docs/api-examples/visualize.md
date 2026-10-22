# Example: Visualization (py3Dmol / Plotly / Yaplot)

This category is included in **`API.ipynb`** via the `CATEGORIES` list in `scripts/build_api_notebook.py` (run `make api-notebook`). In the notebook, install the optional viewers you need (**Optional: py3Dmol**, **Optional: Plotly**, and/or **Optional: Yaplot**) after **Installation**, then run **Setup** and the cells below.

Three ways to look at a generated structure (all optional beyond GenIce3 core):

| Script | Viewer | Extra install |
|--------|--------|---------------|
| `16_py3dmol.py` | [py3Dmol](https://3dmol.csb.pitt.edu/) in Jupyter | `pip install py3dmol` |
| `19_plotly.py` | [Plotly](https://plotly.com/python/) 3D HB network | `pip install plotly` |
| `20_yaplot.py` | [Yaplot](https://vitroid.github.io/Yaplot/) WASM | `yaplot_view.py` helper only (`yaplotlib` is a GenIce3 core dep) |

Or from `examples/api`:

```bash
pip install -r requirements-py3dmol.txt
pip install -r requirements-plotly.txt
```

These samples call `show()` / embed a viewer so the scene appears in Jupyter / Colab. Running the `.py` files from a plain terminal may not open a window.

## Running standalone

From the repository root:

```bash
python examples/api/visualize/16_py3dmol.py
python examples/api/visualize/19_plotly.py

# Yaplot: fetch the notebook helper once
curl -fsSL -o yaplot_view.py https://vitroid.github.io/Yaplot/yaplot_view.py
python examples/api/visualize/20_yaplot.py
```

Or from `examples/api`:

```bash
make visualize
```

`make visualize` uses the Poetry venv’s Python from the repo root; install optional packages into that venv first.

---

## Sample code

### 16_py3dmol

[`16_py3dmol.py`](https://github.com/genice-dev/GenIce3/blob/main/examples/api/visualize/16_py3dmol.py)

```python
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
```

### 19_plotly

[`19_plotly.py`](https://github.com/genice-dev/GenIce3/blob/main/examples/api/visualize/19_plotly.py)

```python
"""Generate ice and show the HB network with the plotly exporter.

In the notebook, run the Optional: Plotly cell first (``pip install plotly``).

Standalone::

    pip install plotly
    python examples/api/visualize/19_plotly.py
"""

try:
    import plotly  # noqa: F401
except ModuleNotFoundError as e:
    raise ModuleNotFoundError(
        "This example needs plotly. Install with: pip install plotly"
    ) from e

from genice3.genice import GenIce3
from genice3.plugin import Exporter

genice = GenIce3(seed=42)
genice.set_unitcell("1h")

# type=full|digraph|fixed|frame|graph — see genice3 --exporter plotly?
fig = Exporter("plotly").figure(genice, type="full")
fig.show()
```

### 20_yaplot

[`20_yaplot.py`](https://github.com/genice-dev/GenIce3/blob/main/examples/api/visualize/20_yaplot.py)

```python
"""Generate ice with the yaplot exporter and show it with Yaplot (WASM).

``yaplotlib`` ships with GenIce3. In the notebook, run the Optional: Yaplot cell
first (downloads ``yaplot_view.py`` if missing).

Standalone: place ``yaplot_view.py`` in cwd, or::

    curl -fsSL -o yaplot_view.py https://vitroid.github.io/Yaplot/yaplot_view.py
"""

from genice3.genice import GenIce3
from genice3.plugin import Exporter
from yaplot_view import show

genice = GenIce3(seed=42)
genice.set_unitcell("1h")

# H=1 enables atomic water (built-in H/O VdW ratio); omit H for lattice-only view
# Yaplot WebAssembly viewer (click the canvas for keyboard focus)
show(Exporter("yaplot").dumps(genice, H=1), height=480)
```
