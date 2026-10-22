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
