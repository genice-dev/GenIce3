from logging import basicConfig, DEBUG, INFO
import numpy as np
from genice3.genice import GenIce3
from genice3.plugin import UnitCell, Exporter, Molecule

# corresponding command:
# genice3 "A15[shift=(0.1,0.1,0.1), anion.0=Cl, cation.6=Na, density=0.8]" \
#   --rep 2 2 2 \
#   --spot_anion 1=Cl --spot_anion 35=Br \
#   --spot_cation 1=Na --spot_cation 35=K \
#   --exporter "gromacs[water_model=4site]" \
#   --seed 42 --depol_loop 2000 -D

basicConfig(level=INFO)

# GenIce3インスタンスを作成
# seed: 乱数シード
# depol_loop: 分極ループの反復回数
# replication_matrix: 複製行列（2x2x2の対角行列）
# spot_anions: 特定の水分子をアニオンで置換（インデックス: イオン名の文字列）
# spot_cations: 特定の水分子をカチオンで置換（インデックス: イオン名の文字列）
# 注意: debugはGenIce3のコンストラクタでは受け付けられない（ログレベルの設定はbasicConfigで行う）
genice = GenIce3(
    seed=42,
    depol_loop=2000,
    replication_matrix=np.array([[2, 0, 0], [0, 2, 0], [0, 0, 2]]),
    spot_anions={
        1: "Cl",
    },
    spot_cations={
        51: "Na",
    },
)

# 単位セルを設定
# shift: シフト（分数座標）
# anions: アニオンで置換する水分子（インデックス: イオン名）
# cations: カチオンで置換する水分子（インデックス: イオン名）
# density: 密度（g/cm³）
# ケージ情報が必要な場合は Exporter("cage_survey").dump(genice, file) でJSON出力可能
genice.unitcell = UnitCell(
    "A15",
    shift=(0.1, 0.1, 0.1),
    anion={15: "Cl"},
    cation={21: "Na"},
    density=0.8,
)


# エクスポーターで出力
Exporter("gromacs").dump(
    genice,
    water_model="4site",
)
