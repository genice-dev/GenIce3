from logging import getLogger
import numpy as np
import networkx as nx
import pairlist as pl
from genice3 import ConfigurationError
from genice3.util import shortest_distance, density_in_g_cm3
from genice3.cage import assess_cages
from typing import Dict, Any, Tuple
from genice3.molecule.one import Molecule
from genice3.cli.pool_parser import (
    OptionDef,
    parse_options_generic,
    OPTION_TYPE_STRING,
    OPTION_TYPE_TUPLE,
    OPTION_TYPE_KEYVALUE,
)


# unitcell 共通オプション定義。追加・削除はここだけ行えばよい。
UNITCELL_OPTION_DEFS = (
    OptionDef("shift", parse_type=OPTION_TYPE_TUPLE),
    OptionDef("density", parse_type=OPTION_TYPE_STRING),
    OptionDef("anion", parse_type=OPTION_TYPE_KEYVALUE),
    OptionDef("cation", parse_type=OPTION_TYPE_KEYVALUE),
)

# 型変換後の後処理（shift→floatタプル、density→float）
UNITCELL_POST_PROCESSORS = {
    "shift": lambda x: tuple(float(v) for v in x),
    "density": lambda x: float(x) if isinstance(x, str) else x,
}


def _is_subgraph(G: nx.Graph, H: nx.DiGraph) -> bool:
    """H（有向）の全辺がG（無向）に含まれるかチェックする。"""
    return all(G.has_edge(u, v) for u, v in H.edges())


def ion_processor(arg: dict) -> Dict[int, Molecule]:
    # keyとvalueを変換するのみ
    result: Dict[int, Molecule] = {}
    for label, molecule in arg.items():
        result[int(label)] = molecule
    return result


class UnitCell:
    """
    単位胞を定義する基底クラス。

    Reactiveではないので、GenIce3に与えたあとで内容を変更しても、GenIce3の依存関係に影響しない。
    もし内容を変更したいなら、新たなUnitCellオブジェクトを作成して、GenIce3に与える。
    """

    # 水素秩序氷（全水素結合の向きが固定）では False に上書き。イオンドープ不可。
    SUPPORTS_ION_DOPING: bool = True

    # 単位胞タイプごとに必要なパラメータのセットを定義
    # このセットに含まれるパラメータは既知として扱われる
    REQUIRED_CELL_PARAMS: set[str] = set()

    logger = getLogger()

    @staticmethod
    def parse_options(options: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        unitcell 共通オプションを型変換して処理する。

        対象は UNITCELL_OPTION_DEFS で定義。shift / density / anion / cation。
        後処理は UNITCELL_POST_PROCESSORS で shift→float タプル、density→float に変換。

        Args:
            options: プラグインに渡されたオプション辞書。

        Returns:
            (処理したオプション, 処理しなかったオプション)。未処理は次のプラグインへ。
        """
        option_specs = {
            d.name: d.parse_type
            for d in UNITCELL_OPTION_DEFS
            if d.parse_type is not None
        }
        return parse_options_generic(options, option_specs, UNITCELL_POST_PROCESSORS)

    def __init__(
        self,
        cell: np.ndarray,
        lattice_sites: np.ndarray,
        bondlen: float = None,  # graphが与えられていればbondlenは不要
        coord: str = "relative",
        density: float = None,
        graph: nx.Graph = None,
        fixed: nx.DiGraph = nx.DiGraph(),
        shift: tuple = (0.0, 0.0, 0.0),
        anion: dict = {},
        cation: dict = {},
        assess_cages: bool = False,
        name: str = "",  # dummy
    ):
        anion = ion_processor(anion)
        cation = ion_processor(cation)
        if type(density) == str:
            density = float(density)

        self.cell = cell
        celli = np.linalg.inv(cell)

        # 格子点の位置をfractional coordinateにする。
        if coord == "absolute":
            self.lattice_sites = lattice_sites @ celli
        else:
            self.lattice_sites = lattice_sites

        self.logger.debug(f"  {shift=}")
        self.lattice_sites += np.array(shift)
        self.lattice_sites -= np.floor(self.lattice_sites)

        nmol = len(lattice_sites)
        volume = np.linalg.det(self.cell)
        original_density = density_in_g_cm3(nmol, self.cell)
        self.logger.info(f"{original_density=}")

        # bondlenとgraphを同時に指定した場合はErrorとする。
        if bondlen is not None and graph is not None:
            raise ValueError("bondlen and graph cannot be specified at the same time.")

        if bondlen is None:
            short = shortest_distance(self.lattice_sites, self.cell)
            bondlen = 1.1 * short

            # densityが指定されていない場合は、ここで推定するが、採用はしない。(cellが正しいと信じる)
            if density is None:
                estimated_density = original_density * (short / 0.276) ** 3
                self.logger.info(
                    f"Neither bond length nor density is specified. Estimated density: {estimated_density}"
                )

        if graph is None:
            self.graph = nx.Graph(
                [
                    (i, j)
                    for i, j in pl.pairs_iter(
                        self.lattice_sites, bondlen, self.cell, distance=False
                    )
                ]
            )
            self.logger.info(
                f"The HB graph is generated from the bond length: {bondlen}"
            )
        else:
            self.graph = graph
        self.logger.debug(f"  {self.graph.size()=} {self.graph.number_of_nodes()=}")

        # 密度を指定した場合は、セルサイズを調整する。
        if density is not None:
            self.logger.info(f"{density=} specified.")
            scale = (density / original_density) ** (1 / 3)
            self.logger.info(f"{scale=}")
            self.cell /= scale

        self.fixed = fixed
        if not _is_subgraph(self.graph, fixed):
            raise ConfigurationError(
                "All edges in fixed must be contained in graph. "
                "Found fixed edge not in graph."
            )

        # ケージの調査は遅延評価（reactive）にする
        self._cages = None  # 遅延評価用

        # anion, cationは単位胞内でのイオンの位置を示すので、番号が単位胞の水分子数未満でなければならない。
        if (anion or cation) and not self.SUPPORTS_ION_DOPING:
            raise ConfigurationError(
                "Ion doping is not supported for hydrogen-ordered ices."
            )
        if any(label >= len(self.lattice_sites) for label in anion):
            raise ValueError(
                "Anion labels must be less than the number of water molecules."
            )
        if any(label >= len(self.lattice_sites) for label in cation):
            raise ValueError(
                "Cation labels must be less than the number of water molecules."
            )
        self.anions = anion
        self.cations = cation
        # ionは水素結合の向きを固定する。
        for label in anion:
            for nei in self.graph[label]:
                if self.fixed.has_edge(label, nei):
                    raise ConfigurationError(f"Impossible to dope an anion at {label}.")
                else:
                    self.fixed.add_edge(nei, label)
        for label in cation:
            for nei in self.graph[label]:
                if self.fixed.has_edge(nei, label):
                    raise ConfigurationError(f"Impossible to dope a cation at {label}.")
                else:
                    self.fixed.add_edge(label, nei)
        for edge in self.fixed.edges():
            self.logger.debug(f"  {edge=}")

    @property
    def cages(self):
        """
        ケージ位置とタイプを取得する（遅延評価）。

        初回アクセス時にケージの調査が行われる。
        """
        if self._cages is None:
            # ケージの調査が必要になったときに実行
            # lattice_sitesは既にshift済みなので、ケージ位置も既にshift済みの座標系で計算される
            self.logger.info("Assessing cages...")
            self._cages = assess_cages(self.graph, self.lattice_sites)

            # ケージ情報をログ出力
            if self._cages is not None:
                for i, (pos, label) in enumerate(
                    zip(self._cages.positions, self._cages.specs)
                ):
                    self.logger.info(f"cage {i}: {label} @ {pos}")

        return self._cages
