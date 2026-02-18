from dataclasses import dataclass
import numpy as np


@dataclass
class Group:
    """
    Base class of a group

    - 置換イオンと単結合を持つものに限る。
    - 置換イオンから直結する原子への結合はz軸正方向を向いている。
    - 置換イオンに直結する原子の位置を原点とする。
    """

    sites: np.ndarray  # 原子の位置
    labels: list[str]  # 原子のラベル
    bonds: list[tuple[int, int]]  # 結合のリスト
    name: str  # グループの名前
