#!/usr/bin/env python3
"""
examples/api/*.yaml を読み、option_parser の structure_to_option_string で
オプション行に戻し、同じ basename の .sh を生成する。
見やすい位置（各 --option の前）で改行を入れる。
実行: プロジェクトルートで python examples/api/gen_sh_from_yaml.py
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
    """1行のオプション文字列を、各 ' --' の前で改行して返す。"""
    parts = re.split(r" (?=--)", line)
    if len(parts) <= 1:
        return line
    return " \\\n  ".join(parts)


def main() -> None:
    if yaml is None:
        print("PyYAML が必要です: pip install pyyaml", file=sys.stderr)
        sys.exit(1)

    api_dir = SCRIPT_DIR
    for yaml_path in sorted(api_dir.glob("*.yaml")):
        text = yaml_path.read_text(encoding="utf-8")
        # 先頭の # コメント行を除いてからパース
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
