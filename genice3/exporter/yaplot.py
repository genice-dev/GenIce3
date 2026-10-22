# coding: utf-8

import itertools as it
import sys
from collections import defaultdict
from logging import getLogger
from io import TextIOWrapper
from typing import Any, Dict, List, Mapping, Optional, Tuple

import numpy as np
from yaplotlib import YaplotDocument, YaplotFrame

from genice3.genice import GenIce3
from genice3.exporter import parse_water_model_option
from genice3.util import serialize


# Bondi van der Waals radii (Å), normalized so O == 1.0.
# Ref: Bondi, A. (1964). J. Phys. Chem. 68, 441–451.
_VDW_ANGSTROM = {
    "H": 1.20,
    "He": 1.40,
    "Li": 1.82,
    "C": 1.70,
    "N": 1.55,
    "O": 1.52,
    "F": 1.47,
    "Ne": 1.54,
    "Na": 2.27,
    "Mg": 1.73,
    "Si": 2.10,
    "P": 1.80,
    "S": 1.80,
    "Cl": 1.75,
    "Ar": 1.88,
    "K": 2.75,
    "Ca": 2.31,
    "Br": 1.85,
    "Kr": 2.02,
    "I": 1.98,
    "Xe": 2.16,
}

BUILTIN_RELATIVE_RADII: Dict[str, float] = {
    el: r / _VDW_ANGSTROM["O"] for el, r in _VDW_ANGSTROM.items()
}

# yaplot Size for relative radius 1.0 (O at multiplier 1): half Bondi VdW in nm.
# Full VdW (space-filling) is too bulky; ~1/5 is network-oriented; 1/2 is the default.
DEFAULT_SCALE = (_VDW_ANGSTROM["O"] / 10.0) / 2.0  # 1.52 Å → 0.076 nm

# Yaplot 既定 fov は 45°。分子を見やすくするため 1/4。
_DEFAULT_FOV_DEG = 45.0
_EXPORT_FOV_DEG = _DEFAULT_FOV_DEG / 4.0
_EXPORT_SPLAT = 3

# Two-letter symbols we recognize when parsing atom labels (Na, Cl, …).
_TWO_LETTER_ELEMENTS = {el for el in BUILTIN_RELATIVE_RADII if len(el) == 2}

# Squared cutoffs (nm²) for HB arrow / guest bond heuristics.
_HB_ARROW_CUTOFF2 = 0.245**2
_GUEST_BOND_CUTOFF2 = 0.16**2


def _scalar(v: Any) -> Any:
    """ネストしたリスト1要素ならスカラーに。"""
    while isinstance(v, (list, tuple)) and len(v) == 1:
        v = v[0]
    return v


def element_symbol(atom_name: str) -> str:
    """
    原子ラベル（OW, HW1, Na, CL, …）から元素記号を推定する。
    """
    letters = "".join(c for c in atom_name if c.isalpha())
    if not letters:
        return "?"
    if len(letters) >= 2 and letters[1].islower():
        return letters[0].upper() + letters[1]
    pair = letters[:2].capitalize()
    if pair in _TWO_LETTER_ELEMENTS:
        return pair
    return letters[0].upper()


def atom_size(
    element: str,
    scale: float = DEFAULT_SCALE,
    relatives: Optional[Mapping[str, float]] = None,
) -> float:
    """
    表示半径 = scale × 内蔵相対半径 × ユーザー相対倍率。
    未知元素の内蔵相対半径は 1.0 とする。
    """
    rel_map = relatives or {}
    builtin = BUILTIN_RELATIVE_RADII.get(element, 1.0)
    user = float(rel_map.get(element, 1.0))
    return round(float(scale) * builtin * user, 12)


def parse_options(options: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    yaplot 固有: scale, 元素ごとの相対倍率 (H, O, C, …), radii dict, water_model。
    残りは unprocessed として返す。
    """
    processed: Dict[str, Any] = {}
    unprocessed = options.copy()

    if "scale" in unprocessed:
        processed["scale"] = float(_scalar(unprocessed.pop("scale")))

    relatives: Dict[str, float] = {}
    if "radii" in unprocessed:
        raw = _scalar(unprocessed.pop("radii"))
        if isinstance(raw, dict):
            for key, val in raw.items():
                relatives[str(key)] = float(_scalar(val))
        else:
            raise ValueError("yaplot option 'radii' must be a mapping of element → float")

    for el in list(unprocessed.keys()):
        if el in BUILTIN_RELATIVE_RADII:
            relatives[el] = float(_scalar(unprocessed.pop(el)))

    if relatives:
        processed["radii"] = relatives

    if "water_model" in unprocessed:
        processed["water_model"] = _scalar(unprocessed.pop("water_model"))
    if "water" in unprocessed and "water_model" not in processed:
        processed["water_model"] = _scalar(unprocessed.pop("water"))
    return processed, unprocessed


desc = {
    "ref": {"Codes": "https://github.com/vitroid/Yaplot"},
    "brief": "Yaplot.",
    "usage": """
Usage: genice3 UNITCELL --exporter yaplot [:option value ...]

options:
    scale=x   Overall size unit (default: half Bondi VdW of O in nm ≈ 0.076).
              Display radius = scale × built-in relative VdW × element multiplier.
              Use scale≈0.152 for space-filling; smaller (e.g. 0.03) for HB networks.
    H=x       Relative multiplier for H (also enables atomic water drawing
              when x != 0). Built-in H/O ratio is used when x=1.
    O=x       Relative multiplier for O (default 1).
    C=x,N=x,… Relative multipliers for other elements (guests/ions).
    radii={…} YAML-friendly dict of element multipliers (merged with above).
    water_model=name
              Water model (e.g. 4site, tip4p). Implies atomic water drawing.

Built-in relative radii are Bondi VdW radii normalized so O == 1.
Without H (or with H=0) and without water_model, only oxygen sites and the
HB network are drawn (lattice overview).
""",
}

format_desc = {
    "aliases": ["y", "yaplot"],
    "application": "[Yaplot](https://github.com/vitroid/Yaplot)",
    "extension": ".yap",
    "media_type": "text/plain",
    "water": "Atomic positions",
    "solute": "Atomic positions",
    "hb": "o",
    "remarks": "It renders molecular configurations and the HB network.",
    "suboptions": (
        "scale: overall size; H/O/C/…: relative to built-in VdW radii (O=1); "
        "radii: dict of multipliers; water_model: water model name. "
        "H!=0 or water_model enables atomic water drawing."
    ),
}


def _resolve_draw_options(options: Mapping[str, Any]) -> Tuple[
    float, Dict[str, float], bool, float, float, Optional[str]
]:
    """Return (scale, relatives, show_atoms, size_O, size_H, water_model_name)."""
    scale = float(options.get("scale", DEFAULT_SCALE))
    relatives: Dict[str, float] = dict(options.get("radii") or {})

    # Direct dump(..., H=1, O=1.2) でも動くよう、元素キーを radii に取り込む。
    for el in BUILTIN_RELATIVE_RADII:
        if el in options and el not in relatives:
            relatives[el] = float(_scalar(options[el]))

    h_rel = relatives.get("H")
    water_model_name = options.get("water_model") or options.get("water")
    # Atomic water when H is a non-zero multiplier, or water_model is given.
    show_atoms = (h_rel is not None and h_rel != 0.0) or (water_model_name is not None)

    size_O = atom_size("O", scale=scale, relatives=relatives)
    # H omitted with water_model → use built-in ratio (multiplier 1).
    size_H = (
        atom_size("H", scale=scale, relatives=relatives)
        if show_atoms and (h_rel is None or h_rel != 0.0)
        else 0.0
    )
    return scale, relatives, show_atoms, size_O, size_H, water_model_name


def _new_document() -> Tuple[YaplotDocument, YaplotFrame]:
    doc = YaplotDocument()
    doc.globals.splat = _EXPORT_SPLAT
    doc.globals.fov = _EXPORT_FOV_DEG
    doc.globals.messages.append("Command line: " + " ".join(sys.argv))
    return doc, doc.new_frame()


def _draw_cell_edges(frame: YaplotFrame, cell: np.ndarray) -> None:
    x, y, z = cell
    for p, q, r in ((x, y, z), (y, z, x), (z, x, y)):
        for a in (np.zeros(3), p, q, p + q):
            frame.add("line", a, a + r, layer=2)


def _draw_lattice_overview(
    frame: YaplotFrame, genice: GenIce3, size_O: float
) -> None:
    """Oxygen sites and undirected HB network (no atomic water)."""
    pos = genice.lattice_sites
    for p in pos:
        frame.add("circle", p @ genice.cell, layer=4, color=3, radius=size_O)
    for i, j in sorted(genice.graph.edges(data=False)):
        O1, O2 = pos[i], pos[j]
        d = O2 - O1
        d -= np.floor(d + 0.5)
        O2 = O1 + d
        frame.add("line", O1 @ genice.cell, O2 @ genice.cell, layer=5, color=4)


def _index_water_sites(waters: Mapping[int, Any]) -> Dict[int, Dict[str, np.ndarray]]:
    """Map water index → {'O', 'H0', 'H1'} absolute positions."""
    water_sites: Dict[int, Dict[str, np.ndarray]] = defaultdict(dict)
    for water_index, water in sorted(waters.items()):
        for atom_name, position in zip(water.labels, water.sites):
            if "O" in atom_name:
                water_sites[water_index]["O"] = position
            elif "H" in atom_name:
                if "H0" not in water_sites[water_index]:
                    water_sites[water_index]["H0"] = position
                else:
                    water_sites[water_index]["H1"] = position
    return water_sites


def _draw_waters(
    frame: YaplotFrame,
    water_sites: Mapping[int, Mapping[str, np.ndarray]],
    size_O: float,
    size_H: float,
) -> None:
    for water_index, water in sorted(water_sites.items()):
        O = water["O"]
        H0 = water["H0"]
        H1 = water["H1"]
        frame.add("circle", O, layer=4, color=3, radius=size_O)
        frame.add("line", O, H0, layer=4, color=3)
        frame.add("line", O, H1, layer=4, color=3)
        if size_H > 0:
            frame.add("circle", H0, layer=4, color=3, radius=size_H)
            frame.add("circle", H1, layer=4, color=3, radius=size_H)
        frame.add("text", O, text=f"{water_index}", layer=1, color=2)


def _draw_hb_arrows(
    frame: YaplotFrame,
    genice: GenIce3,
    waters: Mapping[int, Any],
    water_sites: Mapping[int, Mapping[str, np.ndarray]],
    size_O: float,
) -> None:
    for i, j in sorted(genice.digraph.edges(data=False)):
        if i not in waters or j not in waters:
            continue  # edge may connect to the dopant
        O = water_sites[j]["O"]
        H0 = water_sites[i]["H0"]
        H1 = water_sites[i]["H1"]
        d0 = H0 - O
        d1 = H1 - O
        rr0 = d0 @ d0
        rr1 = d1 @ d1
        if rr0 < rr1 and rr0 < _HB_ARROW_CUTOFF2:
            frame.add("stick", H0, O, layer=3, color=4, radius=size_O, arrow=1)
        if rr1 < rr0 and rr1 < _HB_ARROW_CUTOFF2:
            frame.add("stick", H1, O, layer=3, color=4, radius=size_O, arrow=1)


def _draw_guests_and_ions(
    frame: YaplotFrame,
    gatoms: List[Tuple[Any, Any, np.ndarray]],
    scale: float,
    relatives: Mapping[str, float],
) -> None:
    palettes: Dict[str, int] = {}
    for _molecule_name, atom_name, position in gatoms:
        if atom_name in palettes:
            pal = palettes[atom_name]
        else:
            pal = 4 + len(palettes)
            palettes[atom_name] = pal
        el = element_symbol(atom_name)
        frame.add(
            "circle",
            position,
            layer=4,
            color=pal,
            radius=atom_size(el, scale=scale, relatives=relatives),
            arrow=1,
        )
    for a, b in it.combinations(gatoms, 2):
        _resname, _atomname, position1 = a
        _resname, _atomname, position2 = b
        d = position1 - position2
        if d @ d < _GUEST_BOND_CUTOFF2:
            frame.add("line", position1, position2, layer=4)


def _draw_cages(frame: YaplotFrame, genice: GenIce3, size_O: float) -> None:
    cagespecs = genice.cages
    for i, (_cagespec, position) in enumerate(
        zip(cagespecs.specs, cagespecs.positions)
    ):
        center = position @ genice.cell
        frame.add("circle", center, layer=6, color=5, radius=size_O * 3)
        frame.add("text", center, text=f"{i}", layer=6, color=2)


def _draw_atomic(
    frame: YaplotFrame,
    genice: GenIce3,
    *,
    scale: float,
    relatives: Mapping[str, float],
    size_O: float,
    size_H: float,
    water_model_name: Optional[str],
) -> None:
    logger = getLogger()
    water_model = parse_water_model_option(water_model_name or "4site")
    waters = genice.water_molecules(water_model=water_model)
    guests = genice.guest_molecules()
    ions = genice.substitutional_ions()

    atoms = serialize([w for _, w in sorted(waters.items())])
    logger.info("  Total number of atoms: {0}".format(len(atoms)))

    water_sites = _index_water_sites(waters)
    _draw_waters(frame, water_sites, size_O, size_H)
    _draw_hb_arrows(frame, genice, waters, water_sites, size_O)

    gatoms = serialize(guests) + serialize([ion for _, ion in sorted(ions.items())])
    _draw_guests_and_ions(frame, gatoms, scale, relatives)
    _draw_cages(frame, genice, size_O)


def dumps(genice: GenIce3, **options) -> str:
    """Return the cell as Yaplot text (``.yap``)."""
    scale, relatives, show_atoms, size_O, size_H, water_model_name = (
        _resolve_draw_options(options)
    )
    doc, frame = _new_document()
    _draw_cell_edges(frame, genice.cell)

    if show_atoms:
        _draw_atomic(
            frame,
            genice,
            scale=scale,
            relatives=relatives,
            size_O=size_O,
            size_H=size_H,
            water_model_name=water_model_name,
        )
    else:
        _draw_lattice_overview(frame, genice, size_O)

    return doc.dumps()


def dump(genice: GenIce3, file: TextIOWrapper = sys.stdout, **options) -> None:
    """Write the cell in Yaplot format."""
    file.write(dumps(genice, **options))
