#!/usr/bin/env python3
"""Emit CHANGES.md: one line per commit since the GenIce3 fork point."""

from __future__ import annotations

import subprocess
import sys

FORK_COMMIT = "a7e63b652a2cc324e84a55dced9892eba907ce84"
HEADER = f"""# CHANGES

Auto-generated commit list (run `make changes` to refresh).

GenIce3 fork point (last shared commit with the GenIce2 line): `{FORK_COMMIT}`

"""


def main() -> int:
    try:
        subprocess.run(
            ["git", "rev-parse", "--verify", FORK_COMMIT],
            check=True,
            capture_output=True,
        )
    except subprocess.CalledProcessError:
        print(f"error: fork commit {FORK_COMMIT} not found", file=sys.stderr)
        return 1

    log = subprocess.run(
        [
            "git",
            "log",
            f"--format=- %ad %h %s",
            "--date=short",
            f"{FORK_COMMIT}..HEAD",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    sys.stdout.write(HEADER)
    sys.stdout.write(log.stdout)
    if not log.stdout.endswith("\n"):
        sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
