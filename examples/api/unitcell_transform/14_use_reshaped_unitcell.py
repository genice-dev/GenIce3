#!/usr/bin/env python3
"""
拡大胞を新たに単位胞とする unitcell プラグインを出力する例。

対応する CLI: examples/api/10_extend_unitcell.sh
対応する YAML: examples/api/10_extend_unitcell.yaml

生成された A15e.py は、rep=1 1 1 で同じ構造を再現する unitcell プラグインです。
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
