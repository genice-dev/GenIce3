from logging import getLogger
import numpy as np
import networkx as nx
import pairlist as pl
from genice3 import ConfigurationError
from genice3.util import shortest_distance, density_in_g_cm3
from genice3.cage import assess_cages
from typing import Dict, Any, Tuple, Union
from genice3.molecule.one import Molecule
# unitcell 共通オプション: shift, density, anion, cation, cation_groups
# option_parser の新構造（リスト of スカラー or {arg: subopts}）を __init__ 用に変換する。

def _parse_cation_groups(raw: Dict[str, Union[str, dict]]) -> Dict[int, Dict[int, str]]:
    """
    単位胞オプション cation_groups の生値を site -> {cage_id -> group_name} に変換する。
    値は "1=methyl,17=methyl" 形式の文字列、または YAML 由来の {cage_id: group_name} 辞書。
    """
    result: Dict[int, Dict[int, str]] = {}
    for site_str, val in raw.items():
        site = int(site_str)
        if isinstance(val, dict):
            result[site] = {int(k): str(v) for k, v in val.items()}
        else:
            result[site] = {}
            for part in str(val).split(","):
                part = part.strip()
                if "=" in part:
                    cage_str, group_name = part.split("=", 1)
                    result[site][int(cage_str.strip())] = group_name.strip()
    return result


def _option_parser_list_to_ion_dicts(
    items: Any,
) -> Tuple[Dict[str, str], Dict[int, Dict[int, str]]]:
    """
    option_parser の cation/anion リストを (ions_dict, groups_dict) に変換。
    items: [ "0=N", { "4=N": { "group": [ "1=methyl" ] } } ]
    """
    ions: Dict[str, str] = {}
    groups: Dict[int, Dict[int, str]] = {}
    if items is None:
        return ions, groups
    lst = items if isinstance(items, (list, tuple)) else [items]
    for item in lst:
        if isinstance(item, dict):
            (arg, subopts), = item.items()
            k, v = str(arg).split("=", 1)
            ions[k.strip()] = v.strip()
            if subopts and "group" in subopts:
                g = subopts["group"]
                grp_list = g if isinstance(g, (list, tuple)) else [g]
                groups[int(k.strip())] = {}
                for part in grp_list:
                    if isinstance(part, str) and "=" in part:
                        c, name = part.split("=", 1)
                        groups[int(k.strip())][int(c.strip())] = name.strip()
        elif isinstance(item, str) and "=" in item:
            k, v = item.split("=", 1)
            ions[k.strip()] = v.strip()
    return ions, groups


def _is_subgraph(G: nx.Graph, H: nx.DiGraph) -> bool:
    """H（有向）の全辺がG（無向）に含まれるかチェックする。"""
    return all(G.has_edge(u, v) for u, v in H.edges())


def _label_to_cage_id(label: Any) -> int:
    """'51=N' や 51 からケージ番号を整数で返す。"""
    s = str(label).strip()
    if "=" in s:
        s = s.split("=", 1)[0].strip()
    return int(s)


def ion_processor(arg: dict) -> Dict[int, Molecule]:
    # keyとvalueを変換するのみ。キーは整数または '51=N' 形式（= の前がケージ番号）
    result: Dict[int, Molecule] = {}
    for label, molecule in arg.items():
        result[_label_to_cage_id(label)] = molecule
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
        option_parser の新構造（リスト of スカラー or {arg: subopts}）を
        UnitCell.__init__ が受け取る形に変換する。

        Returns:
            (処理したオプション, 処理しなかったオプション)。
        """
        processed: Dict[str, Any] = {}
        unprocessed = dict(options)

        if "cation" in options:
            ions, groups = _option_parser_list_to_ion_dicts(options["cation"])
            processed["cation"] = ions
            if groups:
                processed["cation_groups"] = groups
            unprocessed.pop("cation", None)
        if "anion" in options:
            ions, _ = _option_parser_list_to_ion_dicts(options["anion"])
            processed["anion"] = ions
            unprocessed.pop("anion", None)
        if "cation_groups" in options:
            processed["cation_groups"] = _parse_cation_groups(options["cation_groups"])
            unprocessed.pop("cation_groups", None)
        if "shift" in options:
            v = options["shift"]
            v = v if isinstance(v, (list, tuple)) else [v]
            processed["shift"] = tuple(float(x) for x in v)
            unprocessed.pop("shift", None)
        if "density" in options:
            v = options["density"]
            if isinstance(v, (list, tuple)) and v:
                processed["density"] = float(v[0])
            elif isinstance(v, str):
                processed["density"] = float(v)
            elif isinstance(v, (int, float)):
                processed["density"] = float(v)
            else:
                processed["density"] = v
            unprocessed.pop("density", None)

        return processed, unprocessed

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
        cation_groups: dict = None,
        name: str = "",  # dummy
    ):
        anion = ion_processor(anion)
        cation = ion_processor(cation)
        if cation_groups is None:
            cation_groups = {}
        else:
            # parse_options を通っていない生指定（str の値）の場合は正規化
            sample = next(iter(cation_groups.values()), None)
            if sample is not None and not isinstance(sample, dict):
                cation_groups = _parse_cation_groups(cation_groups)
        if isinstance(density, str):
            density = float(density)
        elif isinstance(density, (list, tuple)) and len(density) == 1:
            density = float(density[0])

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
        self.cation_groups = cation_groups  # サイト -> {ケージID -> group名}（単位胞内カチオン用）
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
            self.logger.debug("Assessing cages...")
            self._cages = assess_cages(self.graph, self.lattice_sites)

            # # ケージ情報をログ出力
            # if self._cages is not None:
            #     for i, (pos, label) in enumerate(
            #         zip(self._cages.positions, self._cages.specs)
            #     ):
            #         self.logger.info(f"cage {i}: {label} @ {pos}")

        return self._cages
