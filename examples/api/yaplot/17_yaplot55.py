"""Generate ice with the yaplot exporter and show it with Yaplot (WASM).

In the notebook, run the Optional: Yaplot cell first::

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

# H=1 enables atomic water (built-in H/O VdW ratio); omit H for lattice-only view
# Yaplot WebAssembly viewer (click the canvas for keyboard focus)
show(Exporter("yaplot").dumps(genice, H=1), height=480)
