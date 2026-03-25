**Helper scripts** for YAML ↔ shell conversion, used by the examples.

- `gen_sh_from_yaml.py`  
  - Generate shell scripts (`*.sh`) from YAML configuration files.

- `gen_yaml_from_sh.py`  
  - Generate YAML configuration from existing shell scripts.

The `*.yaml` / `*.sh` files in each example subdirectory are meant to be generated and edited using these tools.

---

## Sample code

### gen_sh_from_yaml

[`gen_sh_from_yaml.py`](https://github.com/genice-dev/GenIce3/blob/main/examples/api/tools/gen_sh_from_yaml.py)

```python
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
```

### gen_yaml_from_sh

[`gen_yaml_from_sh.py`](https://github.com/genice-dev/GenIce3/blob/main/examples/api/tools/gen_yaml_from_sh.py)

```python
#!/usr/bin/env python3
"""
Read examples/api/*.sh, extract the option line, parse it via option_parser,
and generate a .yaml file with the same basename.
Run from the project root as: python examples/api/gen_yaml_from_sh.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# Add the project root to sys.path.
SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from genice3.cli.option_parser import (
    parse_options,
    structure_for_display,
    scalarize_single_item_lists,
)

try:
    import yaml
except ImportError:
    yaml = None


def _numeric_if_possible(s: str):
    """Convert string-like numbers to int/float so YAML can omit quotes."""
    if not isinstance(s, str):
        return s
    s = s.strip()
    if not s:
        return s
    try:
        if "." in s or "e" in s.lower():
            return float(s)
        return int(s)
    except ValueError:
        return s


def _coerce_numbers(obj):
    """Recursively convert scalar strings into numbers when possible."""
    if isinstance(obj, dict):
        return {k: _coerce_numbers(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_coerce_numbers(e) for e in obj]
    if isinstance(obj, str):
        return _numeric_if_possible(obj)
    return obj


def extract_option_line(sh_path: Path) -> str | None:
    """Extract the option string passed to genice3.cli.genice from a .sh file."""
    text = sh_path.read_text(encoding="utf-8")
    # Join lines with trailing backslashes into a single line.
    oneline = re.sub(r"\\\s*\n\s*", " ", text)
    m = re.search(r"genice3\.cli\.genice\s+(.+)", oneline)
    if not m:
        return None
    line = m.group(1).strip()
    if "#" in line:
        line = line.split("#", 1)[0].strip()
    return line if line else None


def main() -> None:
    if yaml is None:
        print("PyYAML is required: pip install pyyaml", file=sys.stderr)
        sys.exit(1)

    api_dir = SCRIPT_DIR
    for sh_path in sorted(api_dir.glob("*.sh")):
        if sh_path.name.startswith("_"):
            continue
        line = extract_option_line(sh_path)
        if not line:
            continue
        try:
            parsed = parse_options(line)
            display = structure_for_display(parsed)
            for_yaml = scalarize_single_item_lists(display)
            for_yaml = _coerce_numbers(for_yaml)
        except Exception as e:
            print(f"  skip {sh_path.name}: parse error: {e}", file=sys.stderr)
            continue
        yaml_path = sh_path.with_suffix(".yaml")
        yaml_str = yaml.dump(
            for_yaml,
            allow_unicode=True,
            default_flow_style=False,
            sort_keys=False,
        )
        yaml_path.write_text("# Generated from " + sh_path.name + "\n\n" + yaml_str, encoding="utf-8")
        print(f"  {sh_path.name} -> {yaml_path.name}")


if __name__ == "__main__":
    main()
```
