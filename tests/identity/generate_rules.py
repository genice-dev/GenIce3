#!/usr/bin/env python3
"""
corpus.json を読み、Makefile.rules を生成する。

discover.py で発見した成功組み合わせのみをルールに含める。
各実行は run_limited.py 経由（既定 1 GiB / プロセス、timeout 付き）。

使い方:
  python generate_rules.py                     # Makefile.rules に出力
  python generate_rules.py corpus.json         # 入力ファイル指定
  python generate_rules.py --mem-mb 1024 -o Makefile.rules
"""
from __future__ import annotations

import argparse
import os
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

from corpus_util import cases_list, load_corpus  # noqa: E402
from run_limited import DEFAULT_MEM_MB, DEFAULT_TIMEOUT_S  # noqa: E402


def compose_long_line_from_list(items: list, N: int = 70) -> list:
    """Makefile の長い変数を折り返す"""
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


def generate_rules(
    cases: list[dict],
    *,
    mem_mb: int = DEFAULT_MEM_MB,
    timeout: int = DEFAULT_TIMEOUT_S,
) -> str:
    """cases リストから Makefile.rules の内容を生成"""
    products = [d["product"] for d in cases]
    targets_lines = compose_long_line_from_list(products)

    # 並列 -j8 想定: 1 プロセスあたり mem_mb MiB
    limited = (
        f"python run_limited.py --mem-mb {mem_mb} --timeout {timeout} --"
    )

    rules = []
    rules.append(f"GENICE={limited}")
    rules.append(f"# resource limits: {mem_mb} MiB AS / process, timeout {timeout}s")
    # 失敗したレシピの中途ターゲットを残さない（再 make で素通りするのを防ぐ）
    rules.append(".DELETE_ON_ERROR:")
    rules.append("TARGETS=" + "".join(targets_lines))
    rules.append("# 参照出力を更新（意図した変更時のみ。reference/ は git 管理外）")
    rules.append("update-reference: $(addprefix reference/,$(TARGETS))")
    rules.append("# 現在の出力を参照と比較")
    rules.append("test: $(foreach file,$(TARGETS),$(file).diff)")
    rules.append("")

    for d in cases:
        product = d["product"]
        target = d["target"]
        genice_options = d["genice_options"]
        formatter_path = d.get("formatter_path", "")
        ice = d["ice"]
        unitcell_path = f"../../genice3/unitcell/{ice}.py"

        # test: pipefail で genice 失敗を隠さない。成功時のみ .diff を touch
        rules.append(f"{product}.diff: reference/{product}")
        rules.append("\t@mkdir -p reference")
        rules.append(
            f"\tset -o pipefail; $(GENICE) {target} {genice_options} "
            f"2> {product}.log | diff - reference/{product}"
        )
        rules.append("\t@touch $@")
        rules.append("")

        # update-reference: 一時ファイルへ書いて成功かつ非空のときだけ $@ に確定
        # （失敗時に空の $@ が残り、次回 make がスキップするのを防ぐ）
        rules.append(f"reference/{product}: {unitcell_path} {formatter_path}")
        rules.append("\t@mkdir -p reference")
        rules.append(
            f"\t$(GENICE) {target} {genice_options} > $@.tmp 2> $@.log; "
            f"ec=$$?; "
            f"if [ $$ec -ne 0 ] || [ ! -s $@.tmp ]; then "
            f"rm -f $@.tmp; exit 1; fi; "
            f"mv $@.tmp $@"
        )
        rules.append("")

    return "\n".join(rules)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate Makefile.rules from corpus.json"
    )
    parser.add_argument(
        "input",
        nargs="?",
        default="corpus.json",
        help="Input corpus JSON (default: corpus.json)",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="Makefile.rules",
        help="Output Makefile.rules (default: Makefile.rules)",
    )
    parser.add_argument(
        "--mem-mb",
        type=int,
        default=DEFAULT_MEM_MB,
        help=f"Per-process memory limit in MiB (default: {DEFAULT_MEM_MB})",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=DEFAULT_TIMEOUT_S,
        help=f"Per-run timeout in seconds (default: {DEFAULT_TIMEOUT_S})",
    )
    args = parser.parse_args()

    input_path = (
        args.input if os.path.isabs(args.input) else os.path.join(script_dir, args.input)
    )
    output_path = (
        args.output
        if os.path.isabs(args.output)
        else os.path.join(script_dir, args.output)
    )

    if not os.path.exists(input_path):
        legacy = os.path.join(script_dir, "discoveries.json")
        if args.input == "corpus.json" and os.path.exists(legacy):
            input_path = legacy
            print(
                f"corpus.json が無いため discoveries.json を読みます。"
                f" migrate_corpus.py の実行を推奨します。",
                file=sys.stderr,
            )
        else:
            print(
                f"コーパスが見つかりません: {input_path}\n"
                f"  python discover.py  または  python migrate_corpus.py",
                file=sys.stderr,
            )
            sys.exit(1)

    corpus = load_corpus(input_path)
    cases = cases_list(corpus)
    content = generate_rules(cases, mem_mb=args.mem_mb, timeout=args.timeout)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(
        f"Wrote {output_path} ({len(cases)} rules; "
        f"mem={args.mem_mb}MiB timeout={args.timeout}s)"
    )


if __name__ == "__main__":
    main()
