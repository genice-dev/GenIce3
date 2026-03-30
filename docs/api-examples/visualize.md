# Example: GRO structure in py3Dmol

This category is included in **`API.ipynb`** via the `CATEGORIES` list in `scripts/build_api_notebook.py` (run `make api-notebook`). In the notebook, install **`py3dmol`** using the **Optional: py3Dmol** cell after **Installation**, then run **Setup** and the cells below.

**`py3dmol`** is **not** a core dependency of GenIce3. Install it explicitly when you use this example:

```bash
pip install py3dmol
```

Or use the one-line list under `examples/api`:

```bash
pip install -r ../requirements-py3dmol.txt
```

(from `examples/api`)

The sample builds a `.gro` string with GenIce3, loads it into a **py3Dmol** viewer (stick style, unit cell), and calls `show()` so the view appears in Jupyter / Colab. It is meant for notebooks; running the `.py` file from a plain terminal may not display a window.

## Running standalone

From the repository root (with `py3dmol` installed in the same environment as `genice3`):

```bash
python examples/api/visualize/16_py3dmol.py
```

Or from `examples/api`:

```bash
make visualize
```

`make visualize` uses the Poetry venv’s Python from the repo root; install `py3dmol` into that venv first (e.g. `poetry run pip install py3dmol`).

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
