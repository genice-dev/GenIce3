#!/usr/bin/env python3
"""
update-reference に失敗したケースを corpus.json から除外する。

reference/{product} が無い（または空）で、対応する .log があるものを対象にする。
--reason assertion なら ice-rule AssertionError（イオン近接など）だけを外す。

使い方:
  python prune_failed.py --reason assertion
  python prune_failed.py --reason all
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

from corpus_util import load_corpus, save_corpus  # noqa: E402


def _is_assertion_ice_rule(log_text: str) -> bool:
    return "AssertionError" in log_text and (
        "out_degree" in log_text or "in_degree" in log_text
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Remove failed reference cases from corpus.json"
    )
    parser.add_argument(
        "--corpus",
        default="corpus.json",
        help="Corpus path (default: corpus.json)",
    )
    parser.add_argument(
        "--reference-dir",
        default="reference",
        help="Reference directory (default: reference)",
    )
    parser.add_argument(
        "--reason",
        choices=("assertion", "all"),
        default="assertion",
        help="assertion=ice-rule AssertionError only; all=any missing reference with log",
    )
    parser.add_argument(
        "-n",
        "--dry-run",
        action="store_true",
        help="Show what would be removed without writing",
    )
    args = parser.parse_args()

    corpus_path = (
        args.corpus
        if os.path.isabs(args.corpus)
        else os.path.join(script_dir, args.corpus)
    )
    ref_dir = (
        args.reference_dir
        if os.path.isabs(args.reference_dir)
        else os.path.join(script_dir, args.reference_dir)
    )

    corpus = load_corpus(corpus_path)
    remove: list[str] = []
    for case in corpus["cases"]:
        product = case["product"]
        ref = Path(ref_dir) / product
        log = Path(ref_dir) / f"{product}.log"
        if ref.exists() and ref.stat().st_size > 0:
            continue
        if not log.exists():
            continue
        text = log.read_text(encoding="utf-8", errors="replace")
        if args.reason == "assertion":
            if not _is_assertion_ice_rule(text):
                continue
        remove.append(product)

    remove_set = set(remove)
    print(f"Candidates to remove ({args.reason}): {len(remove)}")
    for p in remove:
        print(f"  {p}")

    if args.dry_run or not remove:
        return

    before = len(corpus["cases"])
    corpus["cases"] = [c for c in corpus["cases"] if c["product"] not in remove_set]
    save_corpus(corpus, corpus_path)
    print(f"Wrote {corpus_path} ({before} -> {len(corpus['cases'])})")

    for p in remove:
        for path in (
            Path(ref_dir) / p,
            Path(ref_dir) / f"{p}.log",
            Path(ref_dir) / f"{p}.tmp",
            Path(script_dir) / f"{p}.diff",
            Path(script_dir) / f"{p}.log",
        ):
            if path.exists():
                path.unlink()


if __name__ == "__main__":
    main()
