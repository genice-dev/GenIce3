"""DOH 構造で cage_survey を使う例（Python API）"""
from genice3.genice import GenIce3
from genice3.plugin import Exporter
from logging import basicConfig, INFO

# 対応するコマンド:
#   genice3 DOH -e cage_survey
basicConfig(level=INFO)
genice = GenIce3()
genice.set_unitcell("DOH")
Exporter("cage_survey").dump(genice)
