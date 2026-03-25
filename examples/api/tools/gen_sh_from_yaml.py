#!/usr/bin/env python3
"""
Read examples/api/*.yaml, convert them back to a single option line using
option_parser.structure_to_option_string, and generate a .sh file with the same
basename. Insert line breaks before each '--option' to keep the command readable.
Run from the project root as: python examples/api/gen_sh_from_yaml.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from genice3.cli.option_parser import structure_to_option_string

try:
    import yaml
except ImportError:
    yaml = None


def _option_line_with_breaks(line: str) -> str:
    """Split a single option line and insert line breaks before each ' --'."""
    parts = re.split(r" (?=--)", line)
    if len(parts) <= 1:
        return line
    return " \\\n  ".join(parts)


def main() -> None:
    if yaml is None:
        print("PyYAML is required: pip install pyyaml", file=sys.stderr)
        sys.exit(1)

    api_dir = SCRIPT_DIR
    for yaml_path in sorted(api_dir.glob("*.yaml")):
        text = yaml_path.read_text(encoding="utf-8")
        # Strip leading comment lines before parsing.
        body = re.sub(r"^#.*\n?", "", text).strip()
        if not body:
            continue
        try:
            data = yaml.safe_load(body)
        except Exception as e:
            print(f"  skip {yaml_path.name}: load error: {e}", file=sys.stderr)
            continue
        if not data or "unitcell" not in data:
            continue
        try:
            line = structure_to_option_string(data)
        except Exception as e:
            print(f"  skip {yaml_path.name}: {e}", file=sys.stderr)
            continue
        opt_line = _option_line_with_breaks(line)
        sh_path = yaml_path.with_suffix(".sh")
        content = f"""#!/bin/bash
# Generated from {yaml_path.name}

python3 -m genice3.cli.genice {opt_line}
"""
        sh_path.write_text(content, encoding="utf-8")
        print(f"  {yaml_path.name} -> {sh_path.name}")


if __name__ == "__main__":
    main()
