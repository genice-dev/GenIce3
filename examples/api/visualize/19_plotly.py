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
