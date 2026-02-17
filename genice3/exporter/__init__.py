from genice3.plugin import safe_import
from genice3.molecule import Molecule


def parse_water_model_option(arg: str) -> Molecule:
    # オプション文字列は今のところないのでこれで動く。
    return safe_import("molecule", arg).Molecule()
