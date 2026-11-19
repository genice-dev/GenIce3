"""
c軸方向に分極した強誘電体氷11の単位胞を、a軸方向に上向き(u)または下向き(d)に並べ、a軸方向に長い単位胞を生成する。
uとdを切りかえるために、間に自動的に遷移層が挿入される。

CLI example: genice3 11alt --layers uuuddd

例えば、--layers uuuddd と指定すると、実際にはuとdの間に分極のない遷移層をはさんだ /uuu\\ddd という形の結晶が生成する。
"""
import genice3.unitcell
import numpy as np
from cif2ice import cellvectors
from genice3.util import density_in_g_cm3
from logging import getLogger
import networkx as nx
from typing import Any, Dict, Tuple

desc = {
    "ref": {},
    "brief": "A layered ferroelectric Ice XI.",
    "options": [
        {
            "name": "layers",
            "help": "Polarization stacking. 'u'=up, 'd'=down (e.g. uuu, uuuddd, udud). Default: uu.",
            "required": False,
            "example": "uuu",
        },
    ],
    "test": ({"options": "--layers udud"},),
}


def _scalar(v: Any) -> Any:
    if isinstance(v, (list, tuple)) and len(v) == 1:
        return v[0]
    return v


def parse_options(options: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    11alt 固有: layers。
    残りは基底 UnitCell.parse_options に渡す。
    """
    processed: Dict[str, Any] = {}
    unprocessed = dict(options)
    if "layers" in unprocessed:
        raw = _scalar(unprocessed.pop("layers"))
        layers = str(raw).strip().lower()
        if not layers or not all(c in "ud" for c in layers):
            raise ValueError(
                "11alt unitcell --layers must be a non-empty string of 'u' (up) and 'd' (down), e.g. uuu"
            )
        processed["layers"] = layers
    base_processed, base_unprocessed = genice3.unitcell.UnitCell.parse_options(
        unprocessed
    )
    processed.update(base_processed)
    return processed, base_unprocessed


class UnitCell(genice3.unitcell.UnitCell):
    SUPPORTS_ION_DOPING = False  # 水素秩序氷
    def __init__(self, **kwargs):
        logger = getLogger()

        sites = np.array(
            [
                [1 / 2, 0, 1 / 8],
                [1 / 2, 1 / 3, 0],
                [0, 1 / 2, 1 / 8],
                [0, 5 / 6, 0],
                [1 / 2, 0, 1 / 2],
                [1 / 2, 1 / 3, 5 / 8],
                [0, 1 / 2, 1 / 2],
                [0, 5 / 6, 5 / 8],
            ]
        )
        # c軸方向に上向きまたは下向きに分極した単位胞をa軸方向に重ねる。

        _layers = kwargs.get("layers")
        if _layers is None:
            # 旧形式: 単一キーが "ud" の並びで値が True のとき
            for k, v in kwargs.items():
                if v is True and isinstance(k, str) and all(c in "udUD" for c in k):
                    _layers = k.lower()
                    break
        if _layers is None or _layers == "":
            _layers = "uu"
        _layers = str(_layers).strip().lower()
        if not _layers or not all(c in "ud" for c in _layers):
            raise ValueError(
                "11alt unitcell --layers must be a non-empty string of 'u' (up) and 'd' (down), e.g. uuu"
            )

        # parse options
        last = _layers[-1]
        layers = ""
        for layer in _layers:
            if last != layer:
                if layer == "u":
                    layers += "/"
                else:
                    layers += "\\"
            layers += layer
            last = layer
        logger.info(f"{layers}; {len(layers)} layers along the 'a' axis.")

        N_layers = len(layers)

        assert N_layers > 1, "More than one layer must be specified."

        edges = []
        waters = []
        last = layers[-1]
        for i, layer in enumerate(layers):
            waters.append(sites + np.array([i, 0, 0]))
            offset = i * 8
            right = (i + 1) * 8
            if i + 1 == N_layers:
                right = 0
            if layer == "u":
                assert last in ("u", "/"), "Incompatible u layer."
                edges.append([offset + 0, offset + 1])
                edges.append([offset + 1, offset + 2])
                edges.append([offset + 2, offset + 3])
                edges.append([offset + 3, offset + 0])
                edges.append([offset + 1, right + 2])
                edges.append([right + 3, offset + 0])
                edges.append([offset + 0, offset + 4])
                edges.append([offset + 2, offset + 6])
                edges.append([offset + 4, offset + 7])
                edges.append([offset + 7, offset + 6])
                edges.append([offset + 6, offset + 5])
                edges.append([offset + 5, offset + 4])
                edges.append([offset + 4, right + 7])
                edges.append([right + 6, offset + 5])
                edges.append([offset + 5, offset + 1])
                edges.append([offset + 7, offset + 3])
            elif layer == "d":
                assert last in ("d", "\\"), "Incompatible d layer."
                edges.append([offset + 0, offset + 3])
                edges.append([offset + 3, offset + 2])
                edges.append([offset + 2, offset + 1])
                edges.append([offset + 1, offset + 0])
                edges.append([right + 2, offset + 1])
                edges.append([offset + 0, right + 3])
                edges.append([offset + 4, offset + 0])
                edges.append([offset + 6, offset + 2])
                edges.append([offset + 7, offset + 4])
                edges.append([offset + 6, offset + 7])
                edges.append([offset + 5, offset + 6])
                edges.append([offset + 4, offset + 5])
                edges.append([right + 7, offset + 4])
                edges.append([offset + 5, right + 6])
                edges.append([offset + 1, offset + 5])
                edges.append([offset + 3, offset + 7])
            elif layer == "/":
                assert last in ("d", "\\"), "Incompatible d2u layer."
                edges.append([offset + 0, offset + 3])
                edges.append([offset + 3, offset + 2])
                edges.append([offset + 2, offset + 1])
                edges.append([offset + 0, offset + 1])
                edges.append([offset + 1, right + 2])
                edges.append([right + 3, offset + 0])
                edges.append([offset + 4, offset + 0])
                edges.append([offset + 6, offset + 2])

                edges.append([offset + 5, offset + 4])
                edges.append([offset + 5, offset + 6])
                edges.append([offset + 6, offset + 7])
                edges.append([offset + 7, offset + 4])
                edges.append([offset + 4, right + 7])
                edges.append([right + 6, offset + 5])
                edges.append([offset + 1, offset + 5])
                edges.append([offset + 3, offset + 7])
            elif layer == "\\":
                assert last in ("u", "/"), "Incompatible u2d layer."
                edges.append([offset + 1, offset + 0])
                edges.append([offset + 1, offset + 2])
                edges.append([offset + 2, offset + 3])
                edges.append([offset + 3, offset + 0])
                edges.append([right + 2, offset + 1])
                edges.append([offset + 0, right + 3])
                edges.append([offset + 0, offset + 4])
                edges.append([offset + 2, offset + 6])

                edges.append([offset + 4, offset + 7])
                edges.append([offset + 7, offset + 6])
                edges.append([offset + 6, offset + 5])
                edges.append([offset + 4, offset + 5])
                edges.append([right + 7, offset + 4])
                edges.append([offset + 5, right + 6])
                edges.append([offset + 5, offset + 1])
                edges.append([offset + 7, offset + 3])
            last = layer

        waters = np.vstack(waters) / np.array([N_layers, 1, 1])
        N_waters = N_layers * 8
        logger.debug(waters.shape)

        a = 4.4923 / 10 * N_layers
        b = 7.7808 / 10
        c = 7.3358 / 10

        cell = cellvectors(a, b, c)

        density = density_in_g_cm3(N_waters, cell)

        coord = "relative"

        super().__init__(
            cell=cell,
            lattice_sites=waters,
            density=density,
            coord=coord,
            graph=nx.Graph(edges),
            fixed=nx.DiGraph(edges),
        )
