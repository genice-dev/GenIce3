#!/usr/bin/env python3
"""
実行可能な (ice, options) 組み合わせを発見し、corpus.json に保存する。

オプションセットは option_sets.py で定義する（物理的制約によりユーザーが設定）。
genice3 を実際に実行し、成功した組み合わせのみを記録する。
--limit 指定時は層化サンプリングで ice / exporter / 各オプション次元を優先的にカバーする。

使い方:
  python discover.py                     # corpus.json に上書き（全組み合わせ）
  python discover.py --limit 100         # 成功 100 件まで層化サンプリング
  python discover.py --merge             # 既存 corpus に追記マージ
  python discover.py --reference         # 成功時に reference/ へ出力を保存
  python discover.py --output -          # 標準出力に JSON 出力
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import random
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(script_dir, "../.."))
sys.path.insert(0, script_dir)
from genice3 import plugin

from corpus_util import (  # noqa: E402
    STRUCTURE_SEED_DEFAULT,
    empty_corpus,
    extract_formatter,
    load_corpus,
    make_case,
    merge_cases,
    normalize_options,
    save_corpus,
)
from run_limited import DEFAULT_MEM_MB, DEFAULT_TIMEOUT_S, run_genice_limited  # noqa: E402

try:
    from option_sets import OPTION_SETS, OPTION_CHOICES
except ImportError:
    OPTION_SETS = []
    OPTION_CHOICES = []

SKIP_ICES = frozenset({"iceR"})
DEFAULT_DESC_TEST_EXPORTER = "--exporter gromacs :water_model 4site"


def formatter_list() -> dict[str, str]:
    """exporter プラグイン一覧（除外ルール付き）"""
    formatter_paths: dict[str, str] = {}
    exporter_dir = os.path.join(script_dir, "../../genice3/exporter")
    for filepath in glob.glob(os.path.join(exporter_dir, "*.py")):
        if os.path.islink(filepath):
            continue
        formatter_prefix = os.path.basename(filepath).split(".")[0]
        if formatter_prefix in ("raw", "null", "__init__", "_KG", "plotly"):
            continue
        formatter_paths[formatter_prefix] = os.path.relpath(filepath, script_dir)
    return formatter_paths


def args_to_cli(args: dict) -> str:
    """args 辞書を --key val 形式の CLI オプション文字列に変換"""
    if not args:
        return ""
    parts = []
    for k, v in args.items():
        parts.append(f"--{k}")
        if isinstance(v, (list, tuple)):
            parts.extend(str(x) for x in v)
        else:
            parts.append(str(v))
    return " ".join(parts)


def normalize_legacy_options(opts_str: str) -> str:
    """unitcell desc['test'] 由来の旧形式オプションを新形式に置換"""
    if not opts_str:
        return opts_str
    return opts_str.replace(" -r ", " --rep ").replace("-r ", "--rep ")


def run_genice(
    target: str,
    genice_options: str,
    timeout: int = DEFAULT_TIMEOUT_S,
    mem_mb: int = DEFAULT_MEM_MB,
    cwd: str | None = None,
    python_exe: str | None = None,
) -> tuple[bool, str, str]:
    """genice3 をメモリ・時間制限付きで実行する。"""
    return run_genice_limited(
        target,
        genice_options,
        timeout=timeout,
        mem_mb=mem_mb,
        cwd=cwd,
        python_exe=python_exe,
    )


def _option_picks(opts_str: str) -> tuple[str, ...]:
    """OPTION_CHOICES のどの選択肢が opts_str に含まれるかをタプルで返す。"""
    picks = []
    for dim in OPTION_CHOICES:
        matched = ""
        for choice in sorted(dim, key=len, reverse=True):
            if choice and choice in opts_str:
                matched = choice
                break
        picks.append(matched)
    return tuple(picks)


def _preview_id(cand: dict) -> str:
    return make_case(cand["ice"], cand["genice_options"], cand["formatter"])["id"]


def _desc_test_candidates(
    ices: list[str],
    tests: dict,
    formatters: dict[str, str],
    base_options: list[str],
) -> list[dict]:
    """desc['test'] 由来の必須候補。exporter が無ければ代表 exporter を付与。"""
    candidates = []
    base = " ".join(base_options)
    for ice in ices:
        if ice in SKIP_ICES:
            continue
        ice_tests = tests.get(ice)
        if not ice_tests:
            ice_tests = ({"options": ""},)
        for test in ice_tests:
            if isinstance(test, str):
                test = {"options": test}
            extras = []
            if test.get("args"):
                extras.append(args_to_cli(test["args"]))
            if test.get("options"):
                extras.append(normalize_legacy_options(test["options"]))
            for k, v in test.items():
                if k in ("options", "args"):
                    continue
                extras.append(args_to_cli({k: v}).strip())

            body = " ".join(p for p in extras if p).strip()
            if "--exporter " not in body:
                body = f"{body} {DEFAULT_DESC_TEST_EXPORTER}".strip()
            opts = normalize_options(f"{base} {body}".strip())
            formatter = extract_formatter(opts)
            if not formatter or formatter not in formatters:
                continue
            candidates.append(
                {
                    "ice": ice,
                    "genice_options": opts,
                    "formatter": formatter,
                    "source": "desc_test",
                    "_picks": _option_picks(opts),
                }
            )
    return candidates


def _option_set_candidates(
    ices: list[str],
    option_sets: list[dict],
    formatters: dict[str, str],
    base_options: list[str],
) -> list[dict]:
    """OPTION_SETS × ice の候補リスト。"""
    base = " ".join(base_options)
    candidates = []
    for ice in ices:
        if ice in SKIP_ICES:
            continue
        for opt_cfg in option_sets:
            opts_str = opt_cfg.get("options", "")
            args_cli = args_to_cli(opt_cfg.get("args") or {})
            formatter = extract_formatter(opts_str)
            if not formatter or formatter not in formatters:
                continue
            opts = normalize_options(f"{args_cli} {base} {opts_str}".strip())
            candidates.append(
                {
                    "ice": ice,
                    "genice_options": opts,
                    "formatter": formatter,
                    "source": "discover",
                    "_picks": _option_picks(opts_str),
                }
            )
    return candidates


def _coverage_score(
    cand: dict,
    covered_ices: set[str],
    covered_formatters: set[str],
    covered_dim_values: list[set[str]],
) -> tuple:
    ice_need = 0 if cand["ice"] in covered_ices else 1
    fmt_need = 0 if cand["formatter"] in covered_formatters else 1
    picks = cand.get("_picks") or ()
    dim_need = 0
    for i, val in enumerate(picks):
        if i < len(covered_dim_values) and val and val not in covered_dim_values[i]:
            dim_need += 1
    return (ice_need, fmt_need, dim_need, random.random())


def _mark_covered(
    cand: dict,
    covered_ices: set[str],
    covered_formatters: set[str],
    covered_dim_values: list[set[str]],
) -> None:
    covered_ices.add(cand["ice"])
    covered_formatters.add(cand["formatter"])
    for i, val in enumerate(cand.get("_picks") or ()):
        if val and i < len(covered_dim_values):
            covered_dim_values[i].add(val)


def _build_trial_order(
    desc_cands: list[dict],
    opt_cands: list[dict],
    existing_ids: set[str],
    limit: int | None,
) -> list[dict]:
    """
    試行順を決める。
    1. desc_test を先頭（シャッフル）
    2. 残りを層化貪欲（未カバー ice/exporter/次元を優先）→ ランダム
    同一 id・既存 id は除外。
    """
    seen: set[str] = set(existing_ids)
    ordered: list[dict] = []

    def accept(c: dict) -> bool:
        cid = _preview_id(c)
        if cid in seen:
            return False
        seen.add(cid)
        c["_id"] = cid
        ordered.append(c)
        return True

    desc = list(desc_cands)
    random.shuffle(desc)
    for c in desc:
        accept(c)

    covered_ices: set[str] = set()
    covered_formatters: set[str] = set()
    covered_dim_values: list[set[str]] = [set() for _ in OPTION_CHOICES]
    for c in ordered:
        _mark_covered(c, covered_ices, covered_formatters, covered_dim_values)

    pool = []
    for c in opt_cands:
        cid = _preview_id(c)
        if cid in seen:
            continue
        c["_id"] = cid
        pool.append(c)

    if limit is None:
        # 全件: desc の後に option_set をそのまま（決定的）
        for c in pool:
            if c["_id"] not in seen:
                seen.add(c["_id"])
                ordered.append(c)
        return ordered

    # 層化: 毎回サンプル上の最良を取り、カバーを更新
    while pool:
        sample_n = min(len(pool), 500)
        indices = (
            list(range(len(pool)))
            if len(pool) <= sample_n
            else random.sample(range(len(pool)), sample_n)
        )
        best_i = max(
            indices,
            key=lambda i: _coverage_score(
                pool[i], covered_ices, covered_formatters, covered_dim_values
            ),
        )
        nxt = pool.pop(best_i)
        if nxt["_id"] in seen:
            continue
        seen.add(nxt["_id"])
        ordered.append(nxt)
        _mark_covered(nxt, covered_ices, covered_formatters, covered_dim_values)

        # 十分候補を積んだら残りはランダムで後ろへ
        if len(ordered) >= max(limit * 8, 200):
            random.shuffle(pool)
            for c in pool:
                if c["_id"] not in seen:
                    seen.add(c["_id"])
                    ordered.append(c)
            break

    return ordered


def discover(
    ices: list[str],
    formatters: dict[str, str],
    option_sets: list[dict],
    base_options: list[str],
    tests: dict | None = None,
    limit: int | None = None,
    seed: int | None = None,
    write_reference: bool = False,
    reference_dir: str = "reference",
    timeout: int = DEFAULT_TIMEOUT_S,
    mem_mb: int = DEFAULT_MEM_MB,
    existing_ids: set[str] | None = None,
) -> list[dict]:
    """成功した組み合わせを case dict のリストで返す。"""
    if seed is not None:
        random.seed(seed)

    tests = tests or {}
    existing_ids = existing_ids or set()

    desc_cands = _desc_test_candidates(ices, tests, formatters, base_options)
    opt_cands = _option_set_candidates(ices, option_sets, formatters, base_options)
    ordered = _build_trial_order(desc_cands, opt_cands, existing_ids, limit)

    if limit is not None:
        print(
            f"Finding {limit} successes "
            f"(desc_test candidates={len(desc_cands)}, "
            f"trial queue={len(ordered)}, seed={seed}, "
            f"timeout={timeout}s, mem={mem_mb}MiB)"
        )
    else:
        print(
            f"Trying all {len(ordered)} unique candidates "
            f"(timeout={timeout}s, mem={mem_mb}MiB)"
        )

    discoveries: list[dict] = []
    tried = 0
    for c in ordered:
        if limit is not None and len(discoveries) >= limit:
            print(f"Reached {limit} successes after {tried} attempts")
            break

        ice = c["ice"]
        opts = c["genice_options"]
        formatter_name = c["formatter"]
        case = make_case(
            ice=ice,
            genice_options=opts,
            formatter=formatter_name,
            formatter_path=formatters.get(formatter_name, ""),
            source=c.get("source", "discover"),
        )
        product = case["product"]
        print(f"  $ {sys.executable} -m genice3.cli.genice {ice} {opts}")
        ok, stdout, stderr = run_genice(
            ice, opts, timeout=timeout, mem_mb=mem_mb
        )
        tried += 1
        if ok:
            status = "ok"
        elif "Timeout" in (stderr or ""):
            status = "timeout"
        elif "MemoryLimit" in (stderr or "") or "MemoryError" in (stderr or ""):
            status = "oom"
        else:
            status = "fail"
        prog = f" [{len(discoveries)}/{limit}]" if limit else ""
        print(f"    {status}: {product}{prog}")

        if ok:
            if write_reference:
                ref_path = os.path.join(reference_dir, product)
                os.makedirs(reference_dir, exist_ok=True)
                with open(ref_path, "w", encoding="utf-8") as f:
                    f.write(stdout)
                print(f"    -> {ref_path}")
            discoveries.append(case)

    return discoveries


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Discover valid genice3 combinations into corpus.json."
    )
    parser.add_argument(
        "-o",
        "--output",
        default="corpus.json",
        help="Output corpus file (default: corpus.json). Use '-' for stdout.",
    )
    parser.add_argument(
        "-l",
        "--limit",
        type=int,
        default=None,
        help="Stop when N successful combinations are found (stratified)",
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
        default=DEFAULT_TIMEOUT_S,
        help=f"Timeout per run in seconds (default: {DEFAULT_TIMEOUT_S})",
    )
    parser.add_argument(
        "--mem-mb",
        type=int,
        default=DEFAULT_MEM_MB,
        help=f"Address-space limit per process in MiB (default: {DEFAULT_MEM_MB})",
    )
    parser.add_argument(
        "-r",
        "--reference",
        action="store_true",
        help="Write reference output to reference/ for each successful run",
    )
    parser.add_argument(
        "--merge",
        action="store_true",
        help="Merge into existing corpus instead of overwriting",
    )
    parser.add_argument(
        "--no-desc-test",
        action="store_true",
        help="Skip unitcell desc['test'] candidates",
    )
    args = parser.parse_args()

    if not OPTION_SETS:
        print("option_sets.py に OPTION_CHOICES を定義してください。", file=sys.stderr)
        sys.exit(1)

    result = plugin.scan("unitcell")
    ices = result["system"]
    tests = {} if args.no_desc_test else result.get("tests", {})
    formatters = formatter_list()
    base_options = ["--seed", str(STRUCTURE_SEED_DEFAULT)]

    out_path = None
    if args.output != "-":
        out_path = (
            args.output
            if os.path.isabs(args.output)
            else os.path.join(script_dir, args.output)
        )

    existing = empty_corpus()
    existing_ids: set[str] = set()
    if args.merge and out_path and os.path.exists(out_path):
        existing = load_corpus(out_path)
        existing_ids = {c["id"] for c in existing["cases"]}
        print(f"Merging into existing corpus ({len(existing_ids)} cases)")

    n_ices = len([i for i in ices if i not in SKIP_ICES])
    print(
        f"Discovering: {n_ices} ices × {len(OPTION_SETS)} option sets "
        f"(+ desc_test); merge={args.merge}"
    )

    new_cases = discover(
        ices,
        formatters,
        OPTION_SETS,
        base_options,
        tests=tests,
        limit=args.limit,
        seed=args.seed if args.limit else None,
        write_reference=args.reference,
        timeout=args.timeout,
        mem_mb=args.mem_mb,
        existing_ids=existing_ids if args.merge else set(),
    )
    print(f"Found {len(new_cases)} new valid combinations.")

    corpus = empty_corpus(structure_seed=STRUCTURE_SEED_DEFAULT)
    if args.merge:
        corpus["cases"] = merge_cases(existing["cases"], new_cases)
    else:
        corpus["cases"] = new_cases

    if args.output == "-":
        print(json.dumps(corpus, indent=2, ensure_ascii=False))
    else:
        save_corpus(corpus, out_path)
        print(f"Wrote {out_path} ({len(corpus['cases'])} cases)")


if __name__ == "__main__":
    main()
