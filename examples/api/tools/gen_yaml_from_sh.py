#!/usr/bin/env python3
"""
examples/api/*.sh からオプション行を抽出し、option_parser でパースして
同じ basename の .yaml を生成する。
実行: プロジェクトルートで python examples/api/gen_yaml_from_sh.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# プロジェクトルートを path に追加
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
    """数値に見える文字列は int/float に変換（YAML で引用符なしで出すため）。"""
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
    """再帰的にスカラー文字列を数値に変換する。"""
    if isinstance(obj, dict):
        return {k: _coerce_numbers(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_coerce_numbers(e) for e in obj]
    if isinstance(obj, str):
        return _numeric_if_possible(obj)
    return obj


def extract_option_line(sh_path: Path) -> str | None:
    """.sh から genice3.cli.genice に渡しているオプション文字列を抽出する。"""
    text = sh_path.read_text(encoding="utf-8")
    # 行継続 \ を空白に
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
        print("PyYAML が必要です: pip install pyyaml", file=sys.stderr)
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
