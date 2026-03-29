# coding: utf-8
"""
Exporter that outputs cage positions and types as JSON.
Useful for understanding clathrate structures and reusing assessment data.
"""

import json
import sys
from collections import defaultdict
from io import TextIOWrapper
from logging import getLogger
from typing import Any, Dict, Tuple

from genice3.cage import apply_max_cage_rings
from genice3.genice import GenIce3

format_desc = {
    "aliases": ["cage_survey"],
    "application": "JSON",
    "extension": ".json",
    "water": "none",
    "solute": "none",
    "hb": "none",
    "remarks": "Cage positions and types (fractional coords, labels, faces). Replaces -A/--assess_cages. Optional :max_cage_rings N (max rings per cage, default 16).",
}


def _scalar(v: Any) -> Any:
    while isinstance(v, (list, tuple)) and len(v) == 1:
        v = v[0]
    return v


def parse_options(options: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """cage_survey: max_cage_rings（1 ケージあたりのリング数の上限）。"""
    processed: Dict[str, Any] = {}
    unprocessed = dict(options)
    if "max_cage_rings" in unprocessed:
        raw = _scalar(unprocessed.pop("max_cage_rings"))
        processed["max_cage_rings"] = int(raw)
    return processed, unprocessed


def _brief_report(genice: GenIce3) -> None:
    """Log a brief summary of cage types and indices at INFO (for CLI)."""
    logger = getLogger()
    cages = genice.cages
    if cages is None or not cages.specs:
        return
    by_type: dict[str, list[int]] = defaultdict(list)
    for idx, spec in enumerate(cages.specs):
        by_type[spec.cage_type].append(idx)
    cage_types = sorted(by_type.keys())
    logger.info("  Cage types: %s", cage_types)
    for ct in cage_types:
        indices = by_type[ct]
        logger.info("  Cage type %s: %s", ct, set(indices))


def _cages_to_json(genice: GenIce3) -> str:
    cages = genice.cages
    data = cages.to_json_capable_data()
    if data is None:
        return ""
    s = json.dumps(data, indent=4)
    return s if s.endswith("\n") else s + "\n"


def dumps(genice: GenIce3, **options) -> str:
    """Return cage survey as JSON string."""
    apply_max_cage_rings(genice, options.get("max_cage_rings"))
    return _cages_to_json(genice)


def dump(genice: GenIce3, file: TextIOWrapper = sys.stdout, **options):
    """Write cage survey as JSON to file."""
    apply_max_cage_rings(genice, options.get("max_cage_rings"))
    _brief_report(genice)
    file.write(_cages_to_json(genice))
