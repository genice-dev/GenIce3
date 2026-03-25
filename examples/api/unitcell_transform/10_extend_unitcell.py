#!/usr/bin/env python3
"""
Example that outputs a unitcell plugin whose unit cell is a reshaped supercell.

Corresponding CLI: examples/api/10_extend_unitcell.sh
Corresponding YAML: examples/api/10_extend_unitcell.yaml

The generated ``A15e.py`` is a unitcell plugin that reproduces the same structure
with ``rep=1 1 1``.
"""

from pathlib import Path

from genice3.genice import GenIce3
from genice3.plugin import safe_import

# Start from the A15 unit cell and enlarge it using a replication matrix.
unitcell = safe_import("unitcell", "A15").UnitCell()
genice = GenIce3(unitcell=unitcell)
genice.set_replication_matrix([[1, 1, 0], [-1, 1, 0], [0, 0, 1]])

# Use the python exporter to obtain the source code of a unitcell plugin.
exporter = safe_import("exporter", "python")
exporter.dump(genice)
