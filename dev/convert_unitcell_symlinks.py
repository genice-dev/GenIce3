#!/usr/bin/env python3
"""
Replace genice3/unitcell symlinks with dummy .py files that import the real module.
- Poetry does not install symlinks, so aliases must be real files.
- Digit-starting or invalid module names cannot be used in 'from x import y';
  those are loaded via importlib in the dummy.
"""
import os
import re

UNITCELL_DIR = os.path.join(os.path.dirname(__file__), "genice3", "unitcell")
PACKAGE = "genice3.unitcell"

# Valid Python identifier for module name in import statement
VALID_MODNAME = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")


def resolve_to_real_module(link_path: str) -> str:
    """Follow symlink chain and return the real module name (no .py)."""
    path = link_path
    seen = set()
    while os.path.islink(path):
        if path in seen:
            raise RuntimeError(f"Symlink loop: {path}")
        seen.add(path)
        t = os.readlink(path)
        if not os.path.isabs(t):
            t = os.path.normpath(os.path.join(os.path.dirname(path), t))
        path = t
    path = os.path.realpath(link_path)
    return os.path.splitext(os.path.basename(path))[0]


def dummy_content(real_module: str) -> str:
    """Generate content for the dummy .py file."""
    if VALID_MODNAME.match(real_module):
        return f'''"""Alias for {real_module} (Poetry does not install symlinks)."""
from {PACKAGE}.{real_module} import UnitCell, desc
'''
    # Invalid identifier (e.g. 151_2_4949650): use importlib
    return f'''"""Alias for {real_module} (Poetry does not install symlinks)."""
import importlib
_real = importlib.import_module("{PACKAGE}.{real_module}")
UnitCell = _real.UnitCell
desc = _real.desc
'''


def main():
    os.chdir(UNITCELL_DIR)
    base = os.path.abspath(".")
    converted = []
    for f in sorted(os.listdir(".")):
        if not f.endswith(".py"):
            continue
        path = os.path.join(base, f)
        if not os.path.islink(path):
            continue
        real_module = resolve_to_real_module(path)
        os.unlink(path)
        with open(path, "w") as out:
            out.write(dummy_content(real_module))
        converted.append((f, real_module))
    for f, mod in converted:
        print(f"  {f} -> from {mod}")


if __name__ == "__main__":
    main()
