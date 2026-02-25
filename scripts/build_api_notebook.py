#!/usr/bin/env python3
"""
Build API.ipynb from examples/api: READMEs (markdown) and .py files (code) interleaved.

- Preserves the first 3 cells of the existing API.ipynb (Colab badge, Installation).
- For each category subdir (basic, cif_io, doping, ...): one markdown cell with
  "## Category" + README body, then for each .py a "### Script name" markdown + code cell.
- Category order matches docs nav. Only .py under examples/api/*/ are included.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
EXAMPLES_API = REPO_ROOT / "examples" / "api"
API_NB = REPO_ROOT / "API.ipynb"

# Order and display names for category directories (same as mkdocs nav)
CATEGORIES = [
    ("basic", "Basic"),
    ("cif_io", "CIF I/O"),
    ("doping", "Doping"),
    ("guest_occupancy", "Guest occupancy"),
    ("polarization", "Polarization"),
    ("unitcell_transform", "Unit cell transform"),
    ("topological_defects", "Topological defects"),
    ("tools", "Tools"),
]


def stem_to_title(stem: str) -> str:
    """e.g. 1_reactive_properties -> Reactive properties."""
    # drop leading digits and underscore
    s = re.sub(r"^\d+_", "", stem)
    return s.replace("_", " ").strip() or stem


def make_md_cell(source: str | list[str]) -> dict:
    if isinstance(source, str):
        source = [s + "\n" for s in source.splitlines()] if source else []
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": source if source else [""],
    }


def make_code_cell(source: str | list[str]) -> dict:
    if isinstance(source, str):
        source = [s + "\n" for s in source.splitlines()] if source else []
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": source if source else [""],
    }


def load_existing_intro_and_metadata(nb_path: Path) -> tuple[list[dict], dict]:
    """First 3 cells + notebook metadata (kernelspec etc.)."""
    raw = json.loads(nb_path.read_text(encoding="utf-8"))
    cells = raw.get("cells", [])
    intro = cells[:3] if len(cells) >= 3 else cells
    meta = {k: v for k, v in raw.items() if k != "cells"}
    return intro, meta


def build_cells_from_examples() -> list[dict]:
    cells = []
    for dir_name, display_name in CATEGORIES:
        subdir = EXAMPLES_API / dir_name
        if not subdir.is_dir():
            continue
        readme = subdir / "README.md"
        if readme.exists():
            body = readme.read_text(encoding="utf-8", errors="replace").strip()
            cells.append(make_md_cell(f"## {display_name}\n\n{body}"))
        py_files = sorted(subdir.glob("*.py"))
        for py_path in py_files:
            title = stem_to_title(py_path.stem)
            cells.append(make_md_cell(f"### {title}\n\n`{py_path.name}`"))
            code = py_path.read_text(encoding="utf-8", errors="replace").rstrip()
            cells.append(make_code_cell(code))
    return cells


def main() -> None:
    intro, nb_meta = load_existing_intro_and_metadata(API_NB)
    body_cells = build_cells_from_examples()
    all_cells = intro + body_cells

    nb = {"cells": all_cells, **nb_meta}
    API_NB.write_text(json.dumps(nb, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {API_NB.relative_to(REPO_ROOT)} ({len(all_cells)} cells)")


if __name__ == "__main__":
    main()
