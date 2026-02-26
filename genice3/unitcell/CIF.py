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
    "brief": "Load a CIF file and create a unit cell.",
    "options": [
        {"name": "file", "help": "Path to CIF file.", "required": True, "example": "path/to/structure.cif"},
        {"name": "osite", "help": "O site label or regex.", "required": False, "example": "O"},
        {"name": "hsite", "help": "H site label or regex (omit to let GenIce3 place H).", "required": False, "example": None},
    ],
    "test": ({"options": "--file ../../cif/MEP.cif --osite T"},),
}


def _scalar(v: Any) -> Any:
    if isinstance(v, (list, tuple)) and len(v) == 1:
        return v[0]
    return v


def parse_options(options: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    CIF プラグインのオプションを処理する（file, osite, hsite, water_model）。
    残りは基底 UnitCell.parse_options に渡し、共通オプション（shift, density 等）をマージする。
    """
    processed: Dict[str, Any] = {}
    unprocessed = dict(options)
    for key in ("file", "osite", "hsite", "water_model"):
        if key in options:
            processed[key] = _scalar(options[key])
            unprocessed.pop(key, None)
    base_processed, base_unprocessed = genice3.unitcell.UnitCell.parse_options(unprocessed)
    processed.update(base_processed)
    return processed, base_unprocessed


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

        # 共通 unitcell オプション（shift, density, anion, cation 等）は kwargs から親に渡す
        uc_kwargs = {
            k: v for k, v in kwargs.items()
            if k in ("shift", "density", "anion", "cation", "cation_groups")
        }
        if hsite is None:
            # 水素位置は指定されていないので、genice3にまかせる。
            super().__init__(
                cell=cell,  # nm
                lattice_sites=oatoms,
                coord="relative",
                **uc_kwargs,
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
                **uc_kwargs,
            )
