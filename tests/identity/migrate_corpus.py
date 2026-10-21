#!/usr/bin/env python3
"""
旧 discoveries.json（リスト）を corpus.json に移行する。

必要なら reference/ 内のファイル名も新 product 名へリネームする。

使い方:
  python migrate_corpus.py
  python migrate_corpus.py --input discoveries.json --output corpus.json
  python migrate_corpus.py --rename-reference
"""
from __future__ import annotations

import argparse
import json
import os
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

from corpus_util import (  # noqa: E402
    load_corpus,
    migrate_legacy_list,
    rename_reference_files,
    save_corpus,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Migrate discoveries.json to corpus.json with content-based IDs."
    )
    parser.add_argument(
        "-i",
        "--input",
        default="discoveries.json",
        help="Input discoveries/corpus JSON (default: discoveries.json)",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="corpus.json",
        help="Output corpus JSON (default: corpus.json)",
    )
    parser.add_argument(
        "--rename-reference",
        action="store_true",
        help="Rename files under reference/ to new product names",
    )
    parser.add_argument(
        "--reference-dir",
        default="reference",
        help="Reference directory (default: reference)",
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
        print(f"Input not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    with open(input_path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    if isinstance(raw, list):
        old_for_rename = list(raw)
        corpus = migrate_legacy_list(raw)
    else:
        corpus = load_corpus(input_path)
        old_for_rename = []

    save_corpus(corpus, output_path)
    print(f"Wrote {output_path} ({len(corpus['cases'])} cases)")

    if args.rename_reference and old_for_rename:
        renamed, missing = rename_reference_files(
            old_for_rename,
            corpus["cases"],
            (
                args.reference_dir
                if os.path.isabs(args.reference_dir)
                else os.path.join(script_dir, args.reference_dir)
            ),
        )
        print(f"Renamed reference files: {renamed} (missing: {missing})")


if __name__ == "__main__":
    main()
