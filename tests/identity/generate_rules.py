#!/usr/bin/env python3
"""
discoveries.json を読み、Makefile.rules を生成する。

discover.py で発見した成功組み合わせのみをルールに含める。
mkmk.py と同様の Makefile.rules 形式を出力する。

使い方:
  python generate_rules.py                     # Makefile.rules に出力
  python generate_rules.py discoveries.json    # 入力ファイル指定
  python generate_rules.py -o Makefile.rules   # 出力ファイル指定
"""
import argparse
import json
import os
import sys


def compose_long_line_from_list(items: list, N: int = 70) -> list:
    """mkmk.py と同じ改行ロジック"""
    items = list(items)
    lines = []
    while items:
        line = ""
        while len(line) < N and items:
            line += " " + items.pop(0)
        lines.append(line + "\\\n")
    if not lines:
        lines.append("\\\n")
    return lines


def generate_rules(discoveries: list[dict]) -> str:
    """ discoveries リストから Makefile.rules の内容を生成"""
    products = [d["product"] for d in discoveries]
    targets_lines = compose_long_line_from_list(products)

    rules = []
    rules.append("GENICE=python -m genice3.cli.genice")
    rules.append("TARGETS=" + "".join(targets_lines))
    rules.append("# 参照出力を更新（意図した変更時のみ実行し、git add してコミット）")
    rules.append("update-reference: $(addprefix reference/,$(TARGETS))")
    rules.append("# 現在の出力を参照と比較（参照が無ければ自動生成してから比較）")
    rules.append("test: $(foreach file,$(TARGETS),$(file).diff)")
    rules.append("")

    for d in discoveries:
        product = d["product"]
        target = d["target"]
        genice_options = d["genice_options"]
        formatter_path = d.get("formatter_path", "")

        # test ルール
        rules.append(f"{product}.diff: reference/{product}")
        rules.append("\t@mkdir -p reference")
        rules.append(f"\t$(GENICE) {target} {genice_options} 2> $*.log | diff - reference/{product}")
        rules.append("\t@touch $@")
        rules.append("")

        # update-reference ルール（unitcell と formatter への依存）
        ice = d["ice"]
        unitcell_path = f"../../genice3/unitcell/{ice}.py"
        rules.append(f"reference/{product}: {unitcell_path} {formatter_path}")
        rules.append("\t@mkdir -p reference")
        rules.append(f"\t$(GENICE) {target} {genice_options} > $@ 2> $@.log")
        rules.append("")

    return "\n".join(rules)


def main():
    parser = argparse.ArgumentParser(description="Generate Makefile.rules from discoveries.json")
    parser.add_argument("input", nargs="?", default="discoveries.json",
                        help="Input discoveries JSON (default: discoveries.json)")
    parser.add_argument("-o", "--output", default="Makefile.rules",
                        help="Output Makefile.rules (default: Makefile.rules)")
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(script_dir, args.input) if not os.path.isabs(args.input) else args.input
    output_path = os.path.join(script_dir, args.output) if not os.path.isabs(args.output) else args.output

    if not os.path.exists(input_path):
        print(f"discoveries.json が見つかりません。先に discover.py を実行してください。", file=sys.stderr)
        print(f"  python discover.py", file=sys.stderr)
        sys.exit(1)

    with open(input_path, "r", encoding="utf-8") as f:
        discoveries = json.load(f)

    content = generate_rules(discoveries)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"Wrote {output_path} ({len(discoveries)} rules)")


if __name__ == "__main__":
    main()
