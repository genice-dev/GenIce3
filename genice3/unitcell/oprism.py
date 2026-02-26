# coding: utf-8
"""
Generate a hydrogen-ordered prism ice. (Cylindrical ice)

CLI example: genice3 oprism --sides 6 --rows 10
             genice3 oprism --sides 8 --rows 6
"""

import re
from typing import Any, Dict, Tuple

import genice3.unitcell
from cif2ice import cellvectors
from logging import getLogger
from math import sin, pi, cos
import networkx as nx


desc = {
    "ref": {"prism": "Koga 2001"},
    "brief": "Hydrogen-ordered ice nanotubes.",
    "options": [
        {"name": "sides", "help": "Number of sides.", "required": True, "example": "6"},
        {"name": "rows", "help": "Number of rows (must be even).", "required": True, "example": "10"},
    ],
    "test": (
        {"options": "--sides 6 --rows 10"},
        {"options": "--sides 5 --rows 10"},
        {"options": "--sides 8 --rows 6"},
    ),
}


def _scalar(v: Any) -> Any:
    if isinstance(v, (list, tuple)) and len(v) == 1:
        return v[0]
    return v


def parse_options(options: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    oprism 固有: sides, rows。
    残りは基底 UnitCell.parse_options に渡す。
    """
    processed: Dict[str, Any] = {}
    unprocessed = dict(options)
    default_rows = 10
    if "sides" in unprocessed:
        raw = _scalar(unprocessed.pop("sides"))
        try:
            sides = int(raw)
        except (TypeError, ValueError) as e:
            raise ValueError("oprism --sides must be an integer.") from e
        if sides < 3:
            raise ValueError("oprism --sides must be >= 3.")
        processed["sides"] = sides
    if "rows" in unprocessed:
        raw = _scalar(unprocessed.pop("rows"))
        try:
            rows = int(raw)
        except (TypeError, ValueError) as e:
            raise ValueError("oprism --rows must be an integer.") from e
        if rows % 2 != 0:
            raise ValueError("oprism --rows must be even.")
        processed["rows"] = rows
    elif "sides" in processed:
        processed["rows"] = default_rows
    base_processed, base_unprocessed = genice3.unitcell.UnitCell.parse_options(
        unprocessed
    )
    processed.update(base_processed)
    return processed, base_unprocessed


def _parse_sides_rows(legacy: str) -> Tuple[int, int]:
    parts = re.split(r"[\s,]+", str(legacy).strip())
    if len(parts) == 1:
        return int(parts[0]), 10
    if len(parts) == 2:
        return int(parts[0]), int(parts[1])
    raise ValueError("oprism legacy args must be 'sides' or 'sides,rows' (e.g. 5 or 8,6)")


class UnitCell(genice3.unitcell.UnitCell):
    SUPPORTS_ION_DOPING = False  # 水素秩序氷（六角柱など全辺固定）

    def __init__(self, **kwargs):
        logger = getLogger()
        sides = kwargs.get("sides")
        rows = kwargs.get("rows")
        if sides is None or rows is None:
            # 旧形式: 単一キー "5" または "8,6" で値が True
            for k, v in kwargs.items():
                if v is True and isinstance(k, str) and re.match(r"^\d+(,\d+)?$", k.strip()):
                    sides, rows = _parse_sides_rows(k)
                    break
            if sides is None:
                sides = 6
            if rows is None:
                rows = 10
        sides = int(sides)
        rows = int(rows)
        if sides < 3:
            raise ValueError("oprism --sides must be >= 3.")
        if rows % 2 != 0:
            raise ValueError("oprism --rows must be even.")

        logger.info("Prism ice with {0} sides and {1} rows.".format(sides, rows))

        L = 2.75
        bondlen = 3
        R = L / 2 / sin(pi / sides)
        density = sides * rows / (L**3 * 400 * rows) * 18 / 6.022e23 * 1e24

        waters = []
        fixed = []
        for j in range(rows):
            for i in range(sides):
                x = R * cos(i * pi * 2 / sides)
                y = R * sin(i * pi * 2 / sides)
                z = j * L
                waters.append([x, y, z])
            for i in range(sides):
                p = j * sides + i
                q = j * sides + (i + 1) % sides
                if j % 2 == 0:
                    fixed.append([p, q])
                else:
                    fixed.append([q, p])
                q = ((j + 1) % rows) * sides + i
                if i % 2 == 0:
                    fixed.append([p, q])
                else:
                    fixed.append([q, p])

        coord = "absolute"

        cell = cellvectors(a=L * 20, b=L * 20, c=L * rows)

        super().__init__(
            cell=cell,
            lattice_sites=waters,
            coord=coord,
            # bondlen=bondlen,
            density=density,
            fixed=nx.DiGraph(fixed),
            graph=nx.Graph(fixed),
        )
