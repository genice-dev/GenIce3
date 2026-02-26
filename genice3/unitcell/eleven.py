# coding: utf-8
"""
Generate a hydrogen-ordered ice XI with stacking faults.

CLI example: genice3 eleven --layers ccchchc
"""

import genice3.unitcell
import numpy as np
from cif2ice import cellvectors
from logging import getLogger
import networkx as nx
from typing import Any, Dict, Tuple

desc = {
    "ref": {},
    "brief": "Ice XI w/ stacking faults.",
    "options": [
        {
            "name": "layers",
            "help": "Stacking pattern. 'c'=cubic, 'h'=hexagonal (e.g. ccchchc).",
            "required": True,
            "example": "ccchchc",
        },
    ],
    "test": ({"options": "--layers ccchchc"},),
}


def _scalar(v: Any) -> Any:
    if isinstance(v, (list, tuple)) and len(v) == 1:
        return v[0]
    return v


def parse_options(options: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    eleven 固有: layers。
    残りは基底 UnitCell.parse_options に渡す。
    """
    processed: Dict[str, Any] = {}
    unprocessed = dict(options)
    if "layers" in unprocessed:
        raw = _scalar(unprocessed.pop("layers"))
        layers = str(raw).strip().lower()
        if not layers or not all(c in "ch" for c in layers):
            raise ValueError(
                "eleven unitcell --layers must be a non-empty string of 'c' (cubic) and 'h' (hexagonal), e.g. ccchchc"
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
    SUPPORTS_ION_DOPING = False  # 水素秩序氷

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
                "eleven unitcell requires --layers PATTERN (e.g. genice3 eleven --layers ccchchc)"
            )
        arg = layers

        layer = 0
        height = 0
        dir = 1
        L = []
        N = 0  # number of molecules
        edges = []  # hydrogen bonds to be fixed
        for ch in arg:
            grid = dict()
            right, left = None, None
            for x, y in lat[layer]:
                L.append([x, y, height])
                if right is None:
                    right = (x, y)
                grid[x, y] = N
                N += 1
            layer = (layer + dir + 3) % 3
            height += 1
            for x, y in lat[layer]:
                L.append([x, y, height])
                if left is None:
                    left = (x, y)
                grid[x, y] = N
                N += 1
            height += 3
            # connection along x axis
            x, y = right
            dy = +1
            if (x + 1, y + dy) not in grid:
                dy = -1
            for i in range(4):
                A = grid[x, y]
                y0 = (y - dy * 2 + 6) % 6
                C = grid[x, y0]
                edges.append((A, C))
                x = (x + 1) % 4
                y = (y + dy + 6) % 6
                B = grid[x, y]
                edges.append((A, B))
                dy = -dy
            x, y = left
            dy = -dy
            for i in range(4):
                A = grid[x, y]
                x = (x - 1 + 4) % 4
                y = (y + dy + 6) % 6
                B = grid[x, y]
                edges.append((A, B))
                dy = -dy
            # connection along z
            edges.append((N - 4, N))
            edges.append((N - 3, N + 1))
            edges.append((N + 2, N - 2))
            edges.append((N + 3, N - 1))
            assert ch in "CcHh"
            if ch in "Hh":
                # hexagonal = alternative
                dir = -dir
                # cubic = progressive
        assert layer == 0 and dir == 1, "Incompatible number of layers."
        fixed = [(A % N, B % N) for A, B in edges]
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
            density=density,
            coord=coord,
            fixed=nx.DiGraph(fixed),
            graph=nx.Graph(fixed),
        )
