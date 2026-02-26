# Alias for xFAU. Usage: genice3 aeroice --length 3

from genice3.unitcell.xFAU import UnitCell, parse_options, desc

# brief だけ別名用に上書き（任意）
desc = dict(desc)
desc["brief"] = "Aeroice (alias of xFAU)."
