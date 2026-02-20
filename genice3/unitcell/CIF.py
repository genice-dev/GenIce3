# It is a dummy unitcell to load a cif file.
# usage: genice3 CIF[file=diamond.cif, site=C]


import genice3.unitcell
import numpy as np
from typing import Any, Dict, List, Tuple
import networkx as nx
from cif2ice import cellvectors, read_cif
from genice3.util import atoms_to_waters, shortest_distance
import re
from logging import getLogger

desc = {
    "ref": {},
    "usage": "file=CIF file, osite=O site, hsite=H site",
    "brief": "Load a CIF file and create a unit cell.",
    "test": ({"options": "--file ../../cif/MEP.cif --osite T"},),
}


def _scalar(v: Any) -> Any:
    if isinstance(v, (list, tuple)) and len(v) == 1:
        return v[0]
    return v


def parse_options(options: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    CIF プラグインのオプションを処理する（file, osite, hsite, water_model）。
    option_parser 由来の辞書（値はスカラーまたはリスト）を受け取る。
    """
    processed: Dict[str, Any] = {}
    unprocessed = dict(options)
    for key in ("file", "osite", "hsite", "water_model"):
        if key in options:
            processed[key] = _scalar(options[key])
            unprocessed.pop(key, None)
    return processed, unprocessed


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
        # cif2ice はファイルを開けない場合に sys.exit(0) を呼ぶため、
        # SystemExit(0) を補足して例外に変換（exit code 1 にする）
        try:
            atoms, box = read_cif.read_and_process(file, make_rect_box=False)
        except SystemExit as e:
            if e.code in (0, None):
                raise ValueError(f"Failed to open CIF file '{file}'") from e
            raise
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
