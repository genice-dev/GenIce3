# coding: utf-8
"""
Generate a hydrogen-disordered ice I with stacking disorder.

CLI example: genice3 one --layers ccchchc
"""

import genice3.unitcell
import numpy as np
from cif2ice import cellvectors
from logging import getLogger
from typing import Any, Dict, Tuple

desc = {
    "ref": {},
    "brief": "Ice I w/ stacking disorder.",
    "options": [
        {
            "name": "layers",
            "help": "Stacking pattern. 'c'=cubic, 'h'=hexagonal (e.g. ccchchc, hh, ccc).",
            "required": True,
            "example": "ccchchc",
        },
    ],
    "test": (
        {"options": "--layers ccchchc"},
        {"options": "--layers hh"},
        {"options": "--layers ccc"},
    ),
}


def _scalar(v: Any) -> Any:
    if isinstance(v, (list, tuple)) and len(v) == 1:
        return v[0]
    return v


def parse_options(options: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    one 固有: layers。
    残りは基底 UnitCell.parse_options に渡す。
    """
    processed: Dict[str, Any] = {}
    unprocessed = dict(options)
    if "layers" in unprocessed:
        raw = _scalar(unprocessed.pop("layers"))
        layers = str(raw).strip().lower()
        if not layers or not all(c in "ch" for c in layers):
            raise ValueError(
                "one unitcell --layers must be a non-empty string of 'c' (cubic) and 'h' (hexagonal), e.g. ccchchc"
            )
        processed["layers"] = layers
    base_processed, base_unprocessed = genice3.unitcell.UnitCell.parse_options(
        unprocessed
    )
    processed.update(base_processed)
    return processed, base_unprocessed


lat = [
    [[0, 0], [2, 0], [1, 3], [3, 3]],
    [[0, 2], [2, 2], [1, 5], [3, 5]],
    [[0, 4], [2, 4], [1, 1], [3, 1]],
]


class UnitCell(genice3.unitcell.UnitCell):
    def __init__(self, **kwargs):
        logger = getLogger()
        layers = kwargs.get("layers")
        if layers is None:
            # 旧形式: 単一キーが "ch" の並びで値が True のとき
            for k, v in kwargs.items():
                if v is True and isinstance(k, str) and all(c in "CcHh" for c in k):
                    layers = k.lower()
                    break
        if layers is None or layers == "":
            raise ValueError(
                "one unitcell requires --layers PATTERN (e.g. genice3 one --layers ccchchc)"
            )
        layers = str(layers).strip().lower()

        layer = 0
        height = 0
        dir = 1
        L = []
        for ch in layers:
            for x, y in lat[layer]:
                L.append([x, y, height])
            layer = (layer + dir + 3) % 3
            height += 1
            for x, y in lat[layer]:
                L.append([x, y, height])
            height += 3
            assert ch in "CcHh"
            if ch in "Hh":
                # hexagonal = alternative
                dir = -dir
                # cubic = progressive
        assert layer == 0 and dir == 1, "Incompatible number of layers."
        assert len(L) > 0, "Stacking pattern must be specified."
        waters = np.array(L) / np.array([4.0, 6.0, height])
        coord = "relative"
        LHB = 0.276
        bondlen = 0.3
        y = LHB * (8**0.5 / 3) * 3
        x = y * 2 / 3**0.5
        z = LHB * height / 3
        cell = cellvectors(x, y, z)
        density = 0.92

        super().__init__(
            cell=cell,
            lattice_sites=waters,
            coord=coord,
            bondlen=bondlen,
            density=density,
            # **kwargs,
        )
