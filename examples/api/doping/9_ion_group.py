from logging import basicConfig, DEBUG, INFO
import numpy as np
from genice3.genice import GenIce3
from genice3.plugin import UnitCell, Exporter, Molecule

# corresponding command:
# genice3 "A15[shift=(0.1,0.1,0.1), anion.0=Cl, cation.6=Na, density=0.8]" \
#   --rep 2 2 2 \
#   --spot_anion 1=Cl --spot_anion 35=Br \
#   --spot_cation 1=Na --spot_cation 35=K \
#   --exporter gromacs :water_model 4site \
#   --seed 42 --depol_loop 2000 -D

basicConfig(level=INFO)

# GenIce3インスタンスを作成
# seed: 乱数シード
# depol_loop: 分極ループの反復回数
# replication_matrix: 複製行列（2x2x2の対角行列）
# spot_anions / spot_cations: 水分子インデックス -> イオン名。CLI は -A / --spot_anion, -C / --spot_cation
# spot_cation_groups: group サブオプション（サイト -> {ケージID -> group名}）。
# YAML/CLI のネスト形式で使う "ion" キーは Python API では不要（別引数で渡す）。
genice = GenIce3(
    seed=42,
    depol_loop=2000,
    replication_matrix=np.array([[2, 0, 0], [0, 2, 0], [0, 0, 2]]),
    spot_anions={1: "Cl"},
    spot_cations={51: "N"},
    spot_cation_groups={
        51: {12: "methyl", 48: "methyl", 49: "methyl", 50: "methyl"},
    },
)

# 単位セルを設定
# anion / cation: 単位胞内の格子サイトをイオンで置換（サイトインデックス: イオン名）。CLI は -a / --anion, -c / --cation
# density: 密度（g/cm³）
# ケージ情報が必要な場合は Exporter("cage_survey").dump(genice, file) でJSON出力可能
genice.unitcell = UnitCell(
    "A15",
    shift=(0.1, 0.1, 0.1),
    density=0.8,
)


# エクスポーターで出力
Exporter("yaplot").dump(
    genice,
)
