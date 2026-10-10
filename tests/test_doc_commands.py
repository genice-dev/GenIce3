"""
AI 向け文書に載せた genice3 のコマンド例が、そのまま実行できることを確かめる。

docs/for-ai-assistants.md と temp_skill/SKILL.md は同じようなコマンド例を別々に載せている。
make skill-check は生成物の鮮度しか見ないので、オプションを変えたときに片方だけ古くなっても気づけない。
ここでは両方の文書から genice3 コマンドを拾い出し、終了コード 0 で終わることを確認する。

拾うのは shell/bash/sh のコードブロック内の行と、本文中の `genice3 ...` というインラインコード。
UNITCELL や <name> のようなプレースホルダを含む行と、外部ファイルを要する -Y は除く。
"""

import os
import re
import shlex
import subprocess
import sys
from pathlib import Path

import pytest

project_root = Path(__file__).resolve().parent.parent

DOCUMENTS = ["docs/for-ai-assistants.md", "temp_skill/SKILL.md"]
SHELL_FENCES = {"```shell", "```bash", "```sh"}
INLINE = re.compile(r"`(genice3 [^`]+)`")
PLACEHOLDER = re.compile(r"[<\[]|\b[A-Z]{5,}\b")
NEEDS_FILE = {"-Y", "--config"}


def _extract(text: str) -> list[str]:
    found = []
    fence = None
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("```"):
            fence = stripped if fence is None else None
            continue
        if fence in SHELL_FENCES:
            if stripped.startswith("genice3 "):
                found.append(stripped)
        elif fence is None:
            found.extend(INLINE.findall(line))
    return found


def _argv(command: str) -> list[str] | None:
    if PLACEHOLDER.search(command):
        return None
    tokens = shlex.split(command, comments=True)
    args = []
    for token in tokens[1:]:
        if token.startswith(">") or token in {"2>&1", "|"}:
            break
        args.append(token)
    if NEEDS_FILE & set(args):
        return None
    return args


def _collect() -> list[list[str]]:
    seen = {}
    for doc in DOCUMENTS:
        for command in _extract((project_root / doc).read_text(encoding="utf-8")):
            args = _argv(command)
            if args is not None:
                seen.setdefault(shlex.join(args), args)
    return list(seen.values())


COMMANDS = _collect()


def test_commands_found():
    assert len(COMMANDS) >= 10, f"Too few commands extracted from {DOCUMENTS}: {COMMANDS}"


@pytest.mark.parametrize("args", COMMANDS, ids=shlex.join)
def test_documented_command_runs(args):
    result = subprocess.run(
        [sys.executable, "-m", "genice3.cli.genice", *args],
        cwd=project_root,
        capture_output=True,
        text=True,
        timeout=300,
        env={**os.environ, "PYTHONPATH": str(project_root)},
    )
    assert result.returncode == 0, f"genice3 {shlex.join(args)} failed:\n{result.stderr[-2000:]}"
