#!/usr/bin/env python3
"""
実行可能な (ice, options, formatter) 組み合わせを発見し、discoveries.json に保存する。

オプションセットは option_sets.py で定義する（物理的制約によりユーザーが設定）。
genice3 を実際に実行し、成功した組み合わせのみを記録する。

使い方:
  python discover.py              # discoveries.json に上書き保存（全組み合わせ）
  python discover.py --limit 100  # 成功が 100 件になるまでランダムに試す
  python discover.py --reference  # 成功時に reference/ へ出力を保存
  python discover.py --output -   # 標準出力に JSON 出力
"""
import argparse
import glob
import json
import os
import random
import subprocess
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(script_dir, "../.."))
sys.path.insert(0, script_dir)
from genice3 import plugin

try:
    from option_sets import OPTION_SETS, OPTION_CHOICES
except ImportError:
    OPTION_SETS = []
    OPTION_CHOICES = []


def formatter_list():
    """exporter プラグイン一覧（mkmk.py と同じ除外ルール）"""
    formatter_paths = {}
    script_dir = os.path.dirname(os.path.abspath(__file__))
    exporter_dir = os.path.join(script_dir, "../../genice3/exporter")
    for filepath in glob.glob(os.path.join(exporter_dir, "*.py")):
        if not os.path.islink(filepath):
            formatter_prefix = os.path.basename(filepath).split(".")[0]
            if formatter_prefix in ("raw", "null", "__init__", "_KG", "plotly"):
                continue
            # Makefile 用に tests/auto からの相対パスを保存
            formatter_paths[formatter_prefix] = os.path.relpath(filepath, script_dir)
    return formatter_paths


def options_to_bracket_str(args: dict) -> str:
    """args 辞書を [key=val:key2=val2] 形式の文字列に変換"""
    if not args:
        return ""
    return "[" + ":".join(f"{k}={v}" for k, v in args.items()) + "]"


def run_genice(
    target: str, genice_options: str, timeout: int = 60
) -> tuple[bool, str, str]:
    """
    genice3 を実行する。
    Returns:
        (success, stdout_output, stderr_output)
    """
    genice_cmd = [
        sys.executable,
        "-m",
        "genice3.cli.genice",
        target,
    ] + genice_options.split()
    try:
        result = subprocess.run(
            genice_cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=os.path.dirname(os.path.abspath(__file__)),
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Timeout"
    except Exception as e:
        return False, "", str(e)


def _extract_formatter(opts_str: str) -> str | None:
    """opts_str から -e formatter を抽出"""
    parts = opts_str.split()
    for i, p in enumerate(parts):
        if p == "-e" and i + 1 < len(parts):
            return parts[i + 1]
    return None


def _all_combinations(
    ices: list[str], option_sets: list[dict], formatters: dict
) -> list[tuple]:
    """
    (ice, opt_idx) の全組み合わせを返す。
    option_sets の options に -e formatter が含まれる形式を想定。
    """
    combos = []
    for ice in ices:
        if ice in ("iceR",):
            continue
        for opt_idx in range(len(option_sets)):
            opts = option_sets[opt_idx].get("options", "")
            formatter = _extract_formatter(opts)
            if formatter and formatter in formatters:
                combos.append((ice, opt_idx))
    return combos


def discover(
    ices: list[str],
    formatters: dict[str, str],
    option_sets: list[dict],
    base_options: list[str],
    limit: int | None = None,
    seed: int | None = None,
    write_reference: bool = False,
    reference_dir: str = "reference",
) -> list[dict]:
    """
    各 (ice, option_set) で genice3 を実行し、成功した組み合わせを返す。
    option_set の options に -e formatter が含まれる形式（OPTION_CHOICES 由来）。
    limit 指定時は成功が N 件になるまで試す（成功数を指定）。
    write_reference が True の場合、成功時に reference_dir/{product} へ出力を保存する。
    """
    if seed is not None:
        random.seed(seed)

    combos = _all_combinations(ices, option_sets, formatters)
    if limit is not None:
        random.shuffle(combos)
        print(
            f"Finding {limit} successes from {len(combos)} combinations (seed={seed})"
        )

    discoveries = []
    tried = 0
    for ice, opt_idx in combos:
        if limit is not None and len(discoveries) >= limit:
            print(f"Reached {limit} successes after {tried} attempts")
            break

        opt_cfg = option_sets[opt_idx]
        opts_str = opt_cfg.get("options", "")
        args = opt_cfg.get("args") or {}
        bracket = options_to_bracket_str(args)
        target = f"{ice}{bracket}"
        base = " ".join(base_options)
        formatter_name = _extract_formatter(opts_str)
        formatter_path = formatters.get(formatter_name, "")
        product = f"{ice}_{opt_idx}.{formatter_name}"
        genice_opts = f"{base} {opts_str}".strip()
        genice_cmd = f"{sys.executable} -m genice3.cli.genice {target} {genice_opts}"

        print(f"  $ {genice_cmd}")
        ok, stdout, stderr = run_genice(target, genice_opts)
        tried += 1
        status = "ok" if ok else "fail"
        prog = f" [{len(discoveries)}/{limit}]" if limit else ""
        print(f"    {status}: {product}{prog}")

        if ok:
            if write_reference:
                ref_path = os.path.join(reference_dir, product)
                os.makedirs(reference_dir, exist_ok=True)
                with open(ref_path, "w", encoding="utf-8") as f:
                    f.write(stdout)
                print(f"    -> {ref_path}")
            discoveries.append(
                {
                    "ice": ice,
                    "target": target,
                    "genice_options": genice_opts,
                    "formatter": formatter_name,
                    "formatter_path": formatter_path,
                    "product": product,
                    "option_set_index": opt_idx,
                }
            )

    return discoveries


def main():
    parser = argparse.ArgumentParser(
        description="Discover valid genice3 (ice, options, formatter) combinations."
    )
    parser.add_argument(
        "-o",
        "--output",
        default="discoveries.json",
        help="Output file (default: discoveries.json). Use '-' for stdout.",
    )
    parser.add_argument(
        "-l",
        "--limit",
        type=int,
        default=None,
        help="Stop when N successful combinations are found",
    )
    parser.add_argument(
        "-s",
        "--seed",
        type=int,
        default=42,
        help="Random seed for sampling (default: 42)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=60,
        help="Timeout per run in seconds (default: 60)",
    )
    parser.add_argument(
        "-r",
        "--reference",
        action="store_true",
        help="Write reference output to reference/ for each successful run",
    )
    args = parser.parse_args()

    if not OPTION_SETS:
        print("option_sets.py に OPTION_CHOICES を定義してください。", file=sys.stderr)
        print(
            "OPTION_SETS は OPTION_CHOICES の直積から自動生成されます。",
            file=sys.stderr,
        )
        sys.exit(1)

    result = plugin.scan("unitcell")
    ices = result["system"]
    formatters = formatter_list()

    # 決定的な出力のための基本オプション（OPTION_CHOICES で上書き可能）
    base_options = ["--seed", "1"]

    n_ices = len([i for i in ices if i != "iceR"])
    total = n_ices * len(OPTION_SETS)
    print(
        f"Discovering: {n_ices} ices × {len(OPTION_SETS)} option sets (= {total} combos)"
    )
    discoveries = discover(
        ices,
        formatters,
        OPTION_SETS,
        base_options,
        limit=args.limit,
        seed=args.seed if args.limit else None,
        write_reference=args.reference,
    )
    print(f"Found {len(discoveries)} valid combinations.")

    out = json.dumps(discoveries, indent=2, ensure_ascii=False)
    if args.output == "-":
        print(out)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out)
        print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
