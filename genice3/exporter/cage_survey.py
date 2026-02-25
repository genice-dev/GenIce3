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

from genice3.genice import GenIce3

format_desc = {
    "aliases": ["cage_survey"],
    "application": "JSON",
    "extension": ".json",
    "water": "none",
    "solute": "none",
    "hb": "none",
    "remarks": "Cage positions and types (fractional coords, labels, faces). Replaces -A/--assess_cages.",
}


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
    logger.info("Cage types: %s", cage_types)
    for ct in cage_types:
        indices = by_type[ct]
        logger.info("Cage type %s: %s", ct, set(indices))


def dumps(genice: GenIce3, **options) -> str:
    """Return cage survey as JSON string."""
    cages = genice.cages
    data = cages.to_json_capable_data()
    s = json.dumps(data, indent=4)
    return s if s.endswith("\n") else s + "\n"


def dump(genice: GenIce3, file: TextIOWrapper = sys.stdout, **options):
    """Write cage survey as JSON to file."""
    _brief_report(genice)
    file.write(dumps(genice, **options))
