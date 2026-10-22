# Example: Yaplot 5.5 inline viewer

This category is included in **`API.ipynb`** via the `CATEGORIES` list in `scripts/build_api_notebook.py` (run `make api-notebook`). In the notebook, run the **Optional: Yaplot 5.5** cell after **Installation**, then **Setup** and the cells below.

GenIce3’s built-in **`yaplot`** exporter writes `.yap` text (needs **`yaplotlib` ≥ 1.0**). **Yaplot 5.5** is the WebAssembly viewer: <https://vitroid.github.io/Yaplot/>.

Recommended setup (same as the [Yaplot README](https://github.com/vitroid/Yaplot#web-browser-and-google-colab)):

```python
%pip install -q --force-reinstall --no-deps git+https://github.com/vitroid/yaplotlib.git
!wget -q -N https://vitroid.github.io/Yaplot/yaplot_view.py
from yaplotlib import Yaplot
from yaplot_view import show
```

[`yaplot_view.show`](https://vitroid.github.io/Yaplot/yaplot_view.py) embeds the viewer in Jupyter / Colab. It is meant for notebooks; running the `.py` from a plain terminal will not open a window unless IPython is available.

## Running standalone

From the repository root:

```bash
# once: helper for inline display
curl -fsSL -o yaplot_view.py https://vitroid.github.io/Yaplot/yaplot_view.py
python examples/api/yaplot/17_yaplot55.py
```
