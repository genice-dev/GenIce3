"""Generate ice with the yaplot exporter and show it with Yaplot 5.5 (WASM).

In the notebook, run the Optional: Yaplot 5.5 cell first::

    %pip install -q --force-reinstall --no-deps git+https://github.com/vitroid/yaplotlib.git
    !wget -q -N https://vitroid.github.io/Yaplot/yaplot_view.py
    from yaplot_view import show

Standalone: place ``yaplot_view.py`` in cwd before running this file.
"""

from genice3.genice import GenIce3
from genice3.plugin import Exporter
from yaplot_view import show

genice = GenIce3(seed=42)
genice.set_unitcell("1h")

# Yaplot 5.5 WebAssembly viewer (click the canvas for keyboard focus)
show(Exporter("yaplot").dumps(genice), height=480)
