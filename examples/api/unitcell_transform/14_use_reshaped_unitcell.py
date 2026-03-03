#!/usr/bin/env python3
"""
Example that outputs a unitcell plugin whose unit cell is a reshaped supercell.

Corresponding CLI: examples/api/10_extend_unitcell.sh
Corresponding YAML: examples/api/10_extend_unitcell.yaml

The generated ``A15e.py`` is a unitcell plugin that reproduces the same structure
with ``rep=1 1 1``.
"""

from genice3.genice import GenIce3
from genice3.unitcell import ice1c
from genice3.exporter import python as py_exporter, cage_survey

# ice1c 単位胞、複製行列で拡大
unitcell = ice1c.UnitCell()
genice = GenIce3(unitcell=unitcell)
genice.set_replication_matrix([[2, 2, 0], [-2, 2, 0], [0, 0, 2]])

reshaped = py_exporter.supercell_as_unitcell(genice, name="ice1c_reshaped")

genice2 = GenIce3(unitcell=reshaped)
print(cage_survey.dumps(genice2))
