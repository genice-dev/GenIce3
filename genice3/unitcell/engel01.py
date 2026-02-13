"""Alias for 207_1_4435 (Poetry does not install symlinks)."""
import importlib
_real = importlib.import_module("genice3.unitcell.207_1_4435")
UnitCell = _real.UnitCell
desc = _real.desc
