# coding: utf-8
"""
Generate a (twisted) periodic hydrogen-ordered prism ice. (Cylindrical ice)

正方格子をまるめて角柱を作る。周方向と長手方向のそれぞれの周期を、それぞれ2つの整数で指示する。また、正方格子のx方向とy方向の水素結合の配向を、同向と対向のいずれかから選べる。

CLI example: genice3 prism --circum 6 1 --axial -1 10 --x f --y a

--circum x y          Two integers that specify a chiral vector on the square lattice; defaults to 6 0
--axial x y           Two integers that specify a translational vector on the square lattice; defaults to 0 2
--x (f|a), --y (f|a)  orientation of the hydrogen bonds in the x and y directions; f for ferroelectric, a for antiferroelectric; defaults to "a" for both
"""

from typing import Any, Dict, Tuple

import genice3.unitcell
from cif2ice import cellvectors
from logging import getLogger
from math import sin, pi, cos
import networkx as nx
import numpy as np


desc = {
    "ref": {"cylindrical": "Miao 2026"},
    "brief": "Twisted hydrogen-ordered ice nanotubes.",
    "options": [
        {
            "name": "circum",
            "help": "Chiral vector on the square lattice; defaults to 6 2.",
            "required": False,
            "example": "6 1",
        },
        {
            "name": "axial",
            "help": "Translational vector on the square lattice; defaults to -2 6.",
            "required": False,
            "example": "-1 10",
        },
        {
            "name": "x",
            "help": "Orientation of the hydrogen bonds in the x direction; f for ferroelectric, a for antiferroelectric.",
            "required": False,
            "example": "f",
        },
        {
            "name": "y",
            "help": "Orientation of the hydrogen bonds in the y direction; f for ferroelectric, a for antiferroelectric.",
            "required": False,
            "example": "a",
        },
    ],
    "test": ({"options": "--circum 6 1 --axial -2 10 --x f --y a"},),
}


def _scalar(v: Any) -> Any:
    if isinstance(v, (list, tuple)) and len(v) == 1:
        return v[0]
    return v


def _parse_vec2(raw: Any, optname: str) -> list[int]:
    if isinstance(raw, (list, tuple)):
        parts = list(raw)
    else:
        parts = str(raw).replace(",", " ").split()
    if len(parts) != 2:
        raise ValueError(f"prism --{optname} requires two integers (e.g. 6 1).")
    try:
        return [int(parts[0]), int(parts[1])]
    except (TypeError, ValueError) as e:
        raise ValueError(f"prism --{optname} requires two integers (e.g. 6 1).") from e


def parse_options(options: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    prism 固有: circum, axial, x, y。
    残りは基底 UnitCell.parse_options に渡す。
    """
    processed: Dict[str, Any] = {}
    unprocessed = dict(options)
    if "circum" in unprocessed:
        raw = unprocessed.pop("circum")
        processed["circum"] = _parse_vec2(raw, "circum")
    if "axial" in unprocessed:
        raw = unprocessed.pop("axial")
        processed["axial"] = _parse_vec2(raw, "axial")
    if "x" in unprocessed:
        x = str(_scalar(unprocessed.pop("x"))).strip().lower()
        if x not in ("f", "a"):
            raise ValueError("prism --x must be 'f' or 'a'.")
        processed["x"] = x
    if "y" in unprocessed:
        y = str(_scalar(unprocessed.pop("y"))).strip().lower()
        if y not in ("f", "a"):
            raise ValueError("prism --y must be 'f' or 'a'.")
        processed["y"] = y
    base_processed, base_unprocessed = genice3.unitcell.UnitCell.parse_options(
        unprocessed
    )
    processed.update(base_processed)
    return processed, base_unprocessed


def fractional_coordinates(circum, axial):
    logger = getLogger()
    logger.info(
        f"Calculating fractional coordinates for circum {circum} and axial {axial}."
    )

    circum = np.array(circum, dtype=int)
    axial = np.array(axial, dtype=int)

    matrix = np.array([circum, axial])
    # くりかえし単位のなかの分子数(正方格子の格子点数)
    N = matrix[0, 0] * matrix[1, 1] - matrix[0, 1] * matrix[1, 0]
    # 格子座標から分数座標に変換する、整数化逆行列(行列式で割ってない)
    imat = np.array(
        [[matrix[1, 1], -matrix[0, 1]], [-matrix[1, 0], matrix[0, 0]]], dtype=int
    )
    if N < 0:
        N = -N
        imat = -imat
    # 格子点を列挙する。同時に、隣接グラフも作っておく?
    corners = np.array([np.zeros(2, dtype=int), circum, axial, circum + axial])
    xrange = np.min(corners[:, 0]), np.max(corners[:, 0] + 1)
    yrange = np.min(corners[:, 1]), np.max(corners[:, 1] + 1)
    coords = dict()  # x, y to fx, fy
    labels = dict()  # fx, fy to order
    for y in range(yrange[0], yrange[1]):
        for x in range(xrange[0], xrange[1]):
            f = (x, y) @ imat
            fx, fy = f
            # out of bounds
            if not (0 <= fx < N and 0 <= fy < N):
                continue
            labels[fx, fy] = len(labels)
            coords[x, y] = fx, fy
    return coords, labels, imat


def make_digraph(coords, labels, imat, orix, oriy):
    N = len(labels)
    # unit vectors on the square lattice, in fractional coordinates
    dfx = np.array([1, 0], dtype=int) @ imat
    dfy = np.array([0, 1], dtype=int) @ imat
    dg = nx.DiGraph()
    for (x, y), f in coords.items():
        jx, jy = (f + dfx + N) % N
        i = labels[f]
        j = labels[int(jx), int(jy)]
        if orix == "a" and y % 2 == 1:
            dg.add_edge(j, i)
        else:
            dg.add_edge(i, j)

        jx, jy = (f + dfy + N) % N
        i = labels[f]
        j = labels[int(jx), int(jy)]
        if oriy == "a" and x % 2 == 1:
            dg.add_edge(j, i)
        else:
            dg.add_edge(i, j)

    return dg


class UnitCell(genice3.unitcell.UnitCell):
    SUPPORTS_ION_DOPING = False  # 水素秩序氷（六角柱など全辺固定）

    def __init__(self, **kwargs):
        logger = getLogger()
        circum = kwargs.get("circum")
        axial = kwargs.get("axial")
        orix = kwargs.get("x")
        oriy = kwargs.get("y")
        if circum is None:
            circum = [6, 2]
        if axial is None:
            axial = [-2, 6]
        if orix is None:
            orix = "a"
        if oriy is None:
            oriy = "a"

        coords, labels, imat = fractional_coordinates(circum, axial)
        dg = make_digraph(coords, labels, imat, orix, oriy)

        for node in dg:
            if len(list(dg.successors(node))) != 2:
                raise ValueError(f"Node {node} violates the ice rules.")

        # 2つの単位ベクトル方向の変位がどちらも2.75になるように、半径と長手方向のスケールを決める。これが面倒。
        N = len(labels)
        cx, ax = (
            np.array([1, 0], dtype=int) @ imat / N
        )  # unit vector on the square lattice, in fractional coordinates
        cy, ay = np.array([0, 1], dtype=int) @ imat / N
        matrix = np.array(
            [
                [
                    (1 - np.cos(2 * np.pi * cx)) ** 2 + np.sin(2 * np.pi * cx) ** 2,
                    ax**2,
                ],
                [
                    (1 - np.cos(2 * np.pi * cy)) ** 2 + np.sin(2 * np.pi * cy) ** 2,
                    ay**2,
                ],
            ]
        )
        R2, L2 = np.linalg.solve(matrix, [1, 1])
        R = np.sqrt(R2) * 2.75 / 10
        L = np.sqrt(L2) * 2.75 / 10

        cellx = max(L, R * 6)
        celly = max(L, R * 6)
        cell = cellvectors(a=cellx, b=celly, c=L)

        waters = [None] * N
        for f, label in labels.items():
            c = f[0] / N
            a = f[1] / N
            waters[label] = (
                R * np.cos(2 * np.pi * c) + cellx / 2,
                R * np.sin(2 * np.pi * c) + celly / 2,
                a * L,
            )

        super().__init__(
            cell=cell,
            lattice_sites=waters,
            coord="absolute",
            # bondlen=bondlen,
            fixed=dg,
            graph=dg,
        )
