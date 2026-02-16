# coding: utf-8
"""
Exporter that outputs cage positions and types as JSON.
Useful for understanding clathrate structures and reusing assessment data.
"""

import json
import sys
from io import TextIOWrapper

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


def dumps(genice: GenIce3, **options) -> str:
    """Return cage survey as JSON string."""
    cages = genice.cages
    data = cages.to_json_capable_data()
    s = json.dumps(data, indent=4)
    return s if s.endswith("\n") else s + "\n"


def dump(genice: GenIce3, file: TextIOWrapper = sys.stdout, **options):
    """Write cage survey as JSON to file."""
    file.write(dumps(genice, **options))
