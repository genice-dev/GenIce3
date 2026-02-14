# It is a dummy unitcell to load a cif file.
# usage: genice3 CIF[file=diamond.cif, site=C]


import genice3.unitcell
import numpy as np
from typing import Dict, List, Any, Tuple
import networkx as nx
from cif2ice import cellvectors, read_cif
from genice3.util import atoms_to_waters, shortest_distance
import re
from logging import getLogger

from genice3.cli.pool_parser import (
    OptionDef,
    parse_options_generic,
    OPTION_TYPE_STRING,
)


# CIF unitcell プラグインが受け取るオプション定義。追加・削除はここだけ行えばよい。
CIF_OPTION_DEFS = (
    OptionDef("osite", parse_type=OPTION_TYPE_STRING),
    OptionDef("hsite", parse_type=OPTION_TYPE_STRING),
    OptionDef("file", parse_type=OPTION_TYPE_STRING),
    OptionDef("water_model", parse_type=OPTION_TYPE_STRING),
)


def parse_options(options: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    unitcell.cif プラグインのオプションを型変換して処理する。

    対象は CIF_OPTION_DEFS で定義（osite, hsite, file, water_model）。

    Args:
        options: プラグインに渡されたオプション辞書。

    Returns:
        (処理したオプション, 処理しなかったオプション)。未処理は次のプラグインへ。
    """
    option_specs = {
        d.name: d.parse_type
        for d in CIF_OPTION_DEFS
        if d.parse_type is not None
    }
    return parse_options_generic(options, option_specs)


class UnitCell(genice3.unitcell.UnitCell):
    """
    cif単位胞を定義するクラス。
    """

    def __init__(self, **kwargs):
        logger = getLogger("CIF")
        file = kwargs.get("file")
        osite = kwargs.get("osite")
        hsite = kwargs.get("hsite")
        if file is None:
            raise ValueError("file is required")
        if osite is None:
            osite = "O"

        # download(URL, fNameIn)

        atoms, box = read_cif.read_and_process(file, make_rect_box=False)
        # pattern matching
        oatoms = np.array([a[1:] for a in atoms if re.match(osite, a[0])])
        logger.info(f"{osite=} {oatoms.shape=} {atoms}")
        cell = cellvectors(*box) / 10  # nm
        shortest_OO = shortest_distance(oatoms, cell)
        cell *= 0.276 / shortest_OO

        if hsite is None:
            # 水素位置は指定されていないので、genice3にまかせる。
            super().__init__(
                cell=cell,  # nm
                lattice_sites=oatoms,
                coord="relative",
            )
        else:
            hatoms = np.array([a[1:] for a in atoms if re.match(hsite, a[0])])
            waters, pairs, oo_pairs = atoms_to_waters(
                oatoms, hatoms, cell, partial_order=True
            )
            super().__init__(
                cell=cell,
                lattice_sites=waters,
                graph=nx.Graph(oo_pairs),
                fixed=nx.DiGraph(pairs),
                coord="relative",
            )
