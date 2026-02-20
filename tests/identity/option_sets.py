"""
発見フェーズで試すオプションの定義。

OPTION_CHOICES: 各次元から1つずつ選んで組み合わせる。
  各要素は [choice1, choice2, ...] で、空文字 "" はその次元を付加しない。
  "--exporter gromacs" など exporter を含む次元が必須（出力形式を決める）。
  新形式: 括弧なし、--exporter name、サブオプションは :key val。
"""

import itertools

OPTION_CHOICES = [
    [
        "",
        "--spot_cation 0=Na --spot_anion 2=Cl",
        "--spot_cation 0=Na --spot_anion 3=Cl",
    ],
    ["", "--guest A12=me", "--guest A14=et"],
    [
        "--exporter gromacs",
        "--exporter gromacs :water_model 4site",
        "--exporter gromacs :water_model 6site",
        "--exporter lammps",
        "--exporter cif",
        "--exporter yaplot",
        "--exporter _pol",
        "--exporter cage_survey",
    ],
    ["", "--spot_guest 0=me"],
    ["", "", "", "--anion 0=Cl --cation 2=Na"],
    ["", "--depol_loop 2000"],
    ["", "--rep 2 2 2", "--replication_matrix 1 1 1  1 -1 0  1 1 -2"],
    ["", "--target_polarization 0 0 4"],
    ["", "--density 1.1"],
]


def build_option_sets():
    """OPTION_CHOICES の直積から OPTION_SETS を生成（discover.py 互換）"""
    sets = []
    for picks in itertools.product(*OPTION_CHOICES):
        opts = " ".join(s for s in picks if s).strip()
        if "--exporter " not in opts:
            continue  # exporter がない combo はスキップ
        sets.append({"options": opts, "args": {}})
    return sets


# discover.py 互換の OPTION_SETS（全組み合わせ）
OPTION_SETS = build_option_sets()
