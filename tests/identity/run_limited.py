#!/usr/bin/env python3
"""
メモリ・時間に上限を付けて genice3 を実行する。

並列 make -j8 を想定し、既定のアドレス空間上限は 1 GiB/プロセス。
RLIMIT_AS が効かない環境（一部 macOS）では timeout のみが頼りになる。

使い方（CLI ラッパ）:
  python run_limited.py [--mem-mb 1024] [--timeout 60] -- ICE [options...]

使い方（ライブラリ）:
  from run_limited import run_genice_limited
  ok, out, err = run_genice_limited("1h", "--seed 1 --exporter gromacs")
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys

# 並列 8 本を想定した既定上限（GiB 単位ではなく MiB）
DEFAULT_MEM_MB = 1024
DEFAULT_TIMEOUT_S = 60

script_dir = os.path.dirname(os.path.abspath(__file__))


def _make_preexec(mem_bytes: int):
    """子プロセスで RLIMIT_AS を掛ける preexec_fn を返す。"""

    def _preexec() -> None:
        try:
            import resource

            soft, hard = resource.getrlimit(resource.RLIMIT_AS)
            # hard が無制限でない場合はそれを超えない
            limit = mem_bytes
            if hard != resource.RLIM_INFINITY:
                limit = min(limit, hard)
            resource.setrlimit(resource.RLIMIT_AS, (limit, hard))
        except (ValueError, OSError, AttributeError):
            # 非対応 OS / 権限不足 → 上限なしで続行
            pass

    return _preexec


def run_genice_limited(
    target: str,
    genice_options: str = "",
    *,
    timeout: int = DEFAULT_TIMEOUT_S,
    mem_mb: int = DEFAULT_MEM_MB,
    cwd: str | None = None,
    python_exe: str | None = None,
) -> tuple[bool, str, str]:
    """
    genice3 を資源制限付きで実行する。

    Returns:
        (success, stdout, stderr)
        失敗理由は stderr に Timeout / MemoryLimit / 本体メッセージなど。
    """
    exe = python_exe or sys.executable
    cmd = [exe, "-m", "genice3.cli.genice", target]
    if genice_options:
        cmd.extend(genice_options.split())

    mem_bytes = max(1, int(mem_mb)) * 1024 * 1024
    preexec = _make_preexec(mem_bytes) if mem_mb > 0 else None
    # パイプ先だと stderr がブロックバッファされ、Timeout 時に空ログになりやすい
    env = os.environ.copy()
    env.setdefault("PYTHONUNBUFFERED", "1")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout if timeout and timeout > 0 else None,
            cwd=cwd or script_dir,
            preexec_fn=preexec,
            env=env,
        )
    except subprocess.TimeoutExpired as e:
        # 実行はされている。打ち切りまでに出たログを捨てない。
        out = e.stdout.decode() if isinstance(e.stdout, (bytes, bytearray)) else (e.stdout or "")
        err = e.stderr.decode() if isinstance(e.stderr, (bytes, bytearray)) else (e.stderr or "")
        if err and not err.endswith("\n"):
            err += "\n"
        err += f"Timeout after {timeout}s\n"
        return False, out, err
    except Exception as e:
        return False, "", str(e)

    stderr = result.stderr or ""
    if result.returncode != 0:
        # SIGKILL(-9) や MemoryError はメモリ上限の可能性が高い
        if result.returncode in (-9, 137) or "MemoryError" in stderr:
            if "MemoryLimit" not in stderr:
                stderr = (stderr + "\nMemoryLimit\n").lstrip()
        return False, result.stdout or "", stderr
    return True, result.stdout or "", stderr


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run genice3 with memory and time limits."
    )
    parser.add_argument(
        "--mem-mb",
        type=int,
        default=DEFAULT_MEM_MB,
        help=f"Address-space limit per process in MiB (default: {DEFAULT_MEM_MB})",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=DEFAULT_TIMEOUT_S,
        help=f"Timeout in seconds (default: {DEFAULT_TIMEOUT_S}; 0=none)",
    )
    parser.add_argument(
        "genice_args",
        nargs=argparse.REMAINDER,
        help="Arguments after -- are passed to genice3 (ICE [options...])",
    )
    args = parser.parse_args()

    genice_args = list(args.genice_args)
    if genice_args and genice_args[0] == "--":
        genice_args = genice_args[1:]
    if not genice_args:
        print("Usage: run_limited.py [options] -- ICE [genice options...]", file=sys.stderr)
        sys.exit(2)

    target = genice_args[0]
    options = " ".join(genice_args[1:])
    ok, stdout, stderr = run_genice_limited(
        target,
        options,
        timeout=args.timeout,
        mem_mb=args.mem_mb,
    )
    if stderr:
        sys.stderr.write(stderr)
        if not stderr.endswith("\n"):
            sys.stderr.write("\n")
    sys.stdout.write(stdout)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
