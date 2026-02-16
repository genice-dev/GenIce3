"""
発見フェーズで試すオプションの定義。

OPTION_CHOICES: 各次元から1つずつ選んで組み合わせる。
  各要素は [choice1, choice2, ...] で、空文字 "" はその次元を付加しない。
  "-e gromacs" など formatter を含む次元が必須（出力形式を決める）。
"""

import itertools

OPTION_CHOICES = [
    [
        "",
        "--spot_cation 0=Na --spot_anion 2=Cl",
        "--spot_cation 0=Na --spot_anion 3=Cl",
    ],
    ["", "--guest A12=Me", "--guest A14=Et"],
    ["-e gromacs", "-e lammps", "-e cif", "-e yaplot", "-e _pol", "-e cage_survey"],
    ["--water 4site", "--water 6site"],
    ["", "--spot_guest 0=Me"],
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
        if "-e " not in opts:
            continue  # formatter がない combo はスキップ
        sets.append({"options": opts, "args": {}})
    return sets


# discover.py 互換の OPTION_SETS（全組み合わせ）
OPTION_SETS = build_option_sets()
