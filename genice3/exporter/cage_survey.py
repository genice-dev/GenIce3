# coding: utf-8
"""
Exporter that outputs cage positions and types as JSON.
Useful for understanding clathrate structures and reusing assessment data.
"""

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


def dump(genice: GenIce3, file: TextIOWrapper = sys.stdout, **options):
    """Write cage survey as JSON to file."""
    survey_result = genice.cage_survey
    file.write(survey_result)
    if not survey_result.endswith("\n"):
        file.write("\n")
