#!/usr/bin/env python3
"""
Run examples under examples/api: .py (default), optionally .sh and .yaml.

Usage (from repo root):
  python scripts/run_api_examples.py              # .py only
  python scripts/run_api_examples.py --sh        # .py + .sh
  python scripts/run_api_examples.py --yaml      # .py + .yaml
  python scripts/run_api_examples.py --all       # .py + .sh + .yaml
  python scripts/run_api_examples.py --dry-run

.sh are run with bash (cwd=repo root, PYTHONPATH=repo root).
.yaml are run as: python -m genice3.cli.genice --config <path>.

On failure, stdout/stderr are written to run_api_examples.log.
Exit code: 0 if all passed, 1 if any failed.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
EXAMPLES_API = REPO_ROOT / "examples" / "api"
LOG_FILE = REPO_ROOT / "run_api_examples.log"

# env so that .sh scripts and genice3 CLI find the package when run from repo
_ENV = {**os.environ, "PYTHONPATH": str(REPO_ROOT)}


def collect_tasks(*, py: bool, sh: bool, yaml: bool) -> list[tuple[Path, str]]:
    """Return list of (path, fmt) with fmt in ('py','sh','yaml'), sorted."""
    tasks: list[tuple[Path, str]] = []
    for subdir in sorted(EXAMPLES_API.iterdir()):
        if not subdir.is_dir():
            continue
        if py:
            for p in sorted(subdir.glob("*.py")):
                tasks.append((p, "py"))
        if sh:
            for p in sorted(subdir.glob("*.sh")):
                tasks.append((p, "sh"))
        if yaml:
            for p in sorted(subdir.glob("*.yaml")):
                tasks.append((p, "yaml"))
    return tasks


def run_one(path: Path, fmt: str) -> subprocess.CompletedProcess:
    if fmt == "py":
        return subprocess.run(
            [sys.executable, str(path)],
            cwd=REPO_ROOT,
            capture_output=True,
            timeout=60,
            text=True,
            env=_ENV,
        )
    if fmt == "sh":
        return subprocess.run(
            ["bash", str(path)],
            cwd=REPO_ROOT,
            capture_output=True,
            timeout=60,
            text=True,
            env=_ENV,
        )
    if fmt == "yaml":
        return subprocess.run(
            [sys.executable, "-m", "genice3.cli.genice", "--config", str(path)],
            cwd=REPO_ROOT,
            capture_output=True,
            timeout=60,
            text=True,
            env=_ENV,
        )
    raise ValueError(fmt)


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Run examples under examples/api (.py and optionally .sh / .yaml)"
    )
    ap.add_argument("--dry-run", action="store_true", help="Only list entries, do not run")
    ap.add_argument("--sh", action="store_true", help="Also run .sh scripts (bash)")
    ap.add_argument("--yaml", action="store_true", help="Also run .yaml configs (genice3 --config)")
    ap.add_argument("--all", dest="all_formats", action="store_true", help="Run .py, .sh, and .yaml")
    ap.add_argument("-o", "--log", type=Path, default=LOG_FILE, help="Log file for failed runs")
    args = ap.parse_args()

    py = True
    sh = args.sh or args.all_formats
    yaml = args.yaml or args.all_formats
    tasks = collect_tasks(py=py, sh=sh, yaml=yaml)

    if not tasks:
        print("No files to run under examples/api", file=sys.stderr)
        sys.exit(1)

    if args.dry_run:
        for path, fmt in tasks:
            print(path.relative_to(REPO_ROOT), f"  [{fmt}]")
        sys.exit(0)

    failed = []
    log_path = args.log.resolve()
    for path, fmt in tasks:
        rel = path.relative_to(REPO_ROOT)
        try:
            result = run_one(path, fmt)
            if result.returncode != 0:
                raise subprocess.CalledProcessError(
                    result.returncode, result.args, result.stdout, result.stderr
                )
            print(f"OK   {rel}  [{fmt}]")
        except subprocess.CalledProcessError as e:
            print(f"FAIL {rel}  [{fmt}]")
            failed.append((rel, fmt, e))
        except subprocess.TimeoutExpired as e:
            print(f"TIME {rel}  [{fmt}]")
            failed.append((rel, fmt, e))

    if failed:
        with open(log_path, "w", encoding="utf-8") as f:
            f.write(f"run_api_examples: {len(failed)} failed\n\n")
            for rel, fmt, err in failed:
                f.write(f"{'='*60}\n{rel}  [{fmt}]\n{'='*60}\n\n")
                if isinstance(err, subprocess.CalledProcessError):
                    if err.stdout:
                        f.write("--- stdout ---\n")
                        f.write(err.stdout)
                        f.write("\n")
                    if err.stderr:
                        f.write("--- stderr ---\n")
                        f.write(err.stderr)
                        f.write("\n")
                else:
                    f.write("Timed out after 60s\n")
                f.write("\n")
        print(f"\n{len(failed)} failed. Log written to {log_path}", file=sys.stderr)
        for rel, fmt, _ in failed:
            print(f"  {rel}  [{fmt}]", file=sys.stderr)
        sys.exit(1)
    print(f"\nAll {len(tasks)} runs passed.")


if __name__ == "__main__":
    main()
