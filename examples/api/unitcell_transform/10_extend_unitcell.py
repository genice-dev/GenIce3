#!/usr/bin/env python3
"""
拡大胞を新たに単位胞とする unitcell プラグインを出力する例。

対応する CLI: examples/api/10_extend_unitcell.sh
対応する YAML: examples/api/10_extend_unitcell.yaml

生成された A15e.py は、rep=1 1 1 で同じ構造を再現する unitcell プラグインです。
"""

from pathlib import Path

from genice3.genice import GenIce3
from genice3.plugin import safe_import

# A15 単位胞、複製行列で拡大
unitcell = safe_import("unitcell", "A15").UnitCell()
genice = GenIce3(unitcell=unitcell)
genice.set_replication_matrix([[1, 1, 0], [-1, 1, 0], [0, 0, 1]])

# python exporter で unitcell プラグインのソースを取得
exporter = safe_import("exporter", "python")
exporter.dump(genice)
