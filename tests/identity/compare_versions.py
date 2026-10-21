#!/usr/bin/env python3
"""
同じコーパスを旧版・現行で実行し、出力の一致を検証する。

reference/ が無くても版間の同一性を確認できる。

使い方:
  python compare_versions.py --corpus corpus.json \\
    --old-cwd /path/to/old/GenIce3

  python compare_versions.py --corpus corpus.json \\
    --old-cmd 'python -m genice3.cli.genice' --old-cwd ../GenIce3-baseline \\
    --new-cmd 'python -m genice3.cli.genice' --limit 50
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from dataclasses import asdict, dataclass

script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

from corpus_util import cases_list, load_corpus  # noqa: E402
from run_limited import (  # noqa: E402
    DEFAULT_MEM_MB,
    DEFAULT_TIMEOUT_S,
    _make_preexec,
)


@dataclass
class CaseResult:
    product: str
    ice: str
    id: str
    status: str  # match | mismatch | old_fail | new_fail | both_fail
    old_ok: bool
    new_ok: bool
    detail: str = ""


def _run_cmd(
    cmd: list[str],
    cwd: str | None,
    timeout: int,
    mem_mb: int = DEFAULT_MEM_MB,
) -> tuple[bool, str, str]:
    mem_bytes = max(1, int(mem_mb)) * 1024 * 1024
    preexec = _make_preexec(mem_bytes) if mem_mb > 0 else None
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout if timeout and timeout > 0 else None,
            cwd=cwd,
            preexec_fn=preexec,
        )
        stderr = result.stderr or ""
        if result.returncode != 0:
            if result.returncode in (-9, 137) or "MemoryError" in stderr:
                stderr = (stderr + "\nMemoryLimit\n").lstrip()
            return False, result.stdout or "", stderr
        return True, result.stdout or "", stderr
    except subprocess.TimeoutExpired:
        return False, "", "Timeout"
    except Exception as e:
        return False, "", str(e)


def _build_cmd(cmd_template: str, ice: str, options: str) -> list[str]:
    """
    cmd_template が 'python -m genice3.cli.genice' のような場合、
    末尾に ice と options を付ける。
    """
    parts = cmd_template.split()
    parts.append(ice)
    if options:
        parts.extend(options.split())
    return parts


def compare_case(
    case: dict,
    old_cmd: str,
    new_cmd: str,
    old_cwd: str | None,
    new_cwd: str | None,
    timeout: int,
    mem_mb: int = DEFAULT_MEM_MB,
) -> CaseResult:
    ice = case["ice"]
    opts = case["genice_options"]
    product = case["product"]
    cid = case["id"]

    old_ok, old_out, old_err = _run_cmd(
        _build_cmd(old_cmd, ice, opts), old_cwd, timeout, mem_mb=mem_mb
    )
    new_ok, new_out, new_err = _run_cmd(
        _build_cmd(new_cmd, ice, opts), new_cwd, timeout, mem_mb=mem_mb
    )

    if not old_ok and not new_ok:
        return CaseResult(
            product, ice, cid, "both_fail", old_ok, new_ok, (old_err or new_err)[:200]
        )
    if not old_ok:
        return CaseResult(
            product, ice, cid, "old_fail", old_ok, new_ok, old_err[:200]
        )
    if not new_ok:
        return CaseResult(
            product, ice, cid, "new_fail", old_ok, new_ok, new_err[:200]
        )
    if old_out == new_out:
        return CaseResult(product, ice, cid, "match", old_ok, new_ok)
    # 簡易差分サイズ
    return CaseResult(
        product,
        ice,
        cid,
        "mismatch",
        old_ok,
        new_ok,
        f"stdout bytes old={len(old_out)} new={len(new_out)}",
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compare genice3 outputs across two versions using the same corpus."
    )
    parser.add_argument(
        "--corpus",
        default="corpus.json",
        help="Corpus JSON (default: corpus.json)",
    )
    parser.add_argument(
        "--old-cmd",
        default=f"{sys.executable} -m genice3.cli.genice",
        help="Command prefix for the old version",
    )
    parser.add_argument(
        "--new-cmd",
        default=f"{sys.executable} -m genice3.cli.genice",
        help="Command prefix for the new version",
    )
    parser.add_argument(
        "--old-cwd",
        default=None,
        help="Working directory (and usually repo root) for the old version",
    )
    parser.add_argument(
        "--new-cwd",
        default=script_dir,
        help="Working directory for the new version (default: tests/identity)",
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
        "-l",
        "--limit",
        type=int,
        default=None,
        help="Compare only the first N cases",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=None,
        help="Write JSON report to this path (default: stdout summary only)",
    )
    args = parser.parse_args()

    corpus_path = (
        args.corpus
        if os.path.isabs(args.corpus)
        else os.path.join(script_dir, args.corpus)
    )
    if not os.path.exists(corpus_path):
        print(f"Corpus not found: {corpus_path}", file=sys.stderr)
        sys.exit(1)

    cases = cases_list(load_corpus(corpus_path))
    if args.limit is not None:
        cases = cases[: args.limit]

    if not args.old_cwd:
        print("--old-cwd is required (path to old GenIce3 checkout)", file=sys.stderr)
        sys.exit(1)

    results: list[CaseResult] = []
    counts = {
        "match": 0,
        "mismatch": 0,
        "old_fail": 0,
        "new_fail": 0,
        "both_fail": 0,
    }

    print(f"Comparing {len(cases)} cases")
    print(f"  old: cwd={args.old_cwd} cmd={args.old_cmd}")
    print(f"  new: cwd={args.new_cwd} cmd={args.new_cmd}")
    print(f"  limits: timeout={args.timeout}s mem={args.mem_mb}MiB")

    for i, case in enumerate(cases, 1):
        r = compare_case(
            case,
            args.old_cmd,
            args.new_cmd,
            args.old_cwd,
            args.new_cwd,
            args.timeout,
            mem_mb=args.mem_mb,
        )
        results.append(r)
        counts[r.status] += 1
        mark = {
            "match": "OK",
            "mismatch": "DIFF",
            "old_fail": "OLD!",
            "new_fail": "NEW!",
            "both_fail": "FAIL",
        }[r.status]
        extra = f" ({r.detail})" if r.detail and r.status != "match" else ""
        print(f"  [{i}/{len(cases)}] {mark} {r.product}{extra}")

    print("\nSummary:")
    for k, v in counts.items():
        print(f"  {k}: {v}")

    report = {
        "total": len(cases),
        "counts": counts,
        "results": [asdict(r) for r in results],
    }
    if args.output:
        out_path = (
            args.output
            if os.path.isabs(args.output)
            else os.path.join(script_dir, args.output)
        )
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
            f.write("\n")
        print(f"Wrote {out_path}")

    # mismatch または new_fail があれば非ゼロ終了
    if counts["mismatch"] or counts["new_fail"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
