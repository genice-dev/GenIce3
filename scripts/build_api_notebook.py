#!/usr/bin/env python3
"""
Build API.ipynb from examples/api: READMEs (markdown) and .py files (code) interleaved.

- Preserves the first 3 cells of the existing API.ipynb (Colab badge, Installation).
- Inserts a Setup cell so the working directory is the repo root (needed for paths like cif/MEP.cif).
- Skips the "tools" category (gen_sh_from_yaml, gen_yaml_from_sh use __file__ and are batch utilities).
- For each other category: one markdown cell with "## Category" + README body, then per .py a "### Script name" markdown + code cell.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
EXAMPLES_API = REPO_ROOT / "examples" / "api"
API_NB = REPO_ROOT / "API.ipynb"

# Order and display names (same as docs nav). Skip "tools" — those scripts use __file__ and are batch utilities.
CATEGORIES = [
    ("basic", "Basic"),
    ("cif_io", "CIF I/O"),
    ("doping", "Doping"),
    ("guest_occupancy", "Guest occupancy"),
    ("polarization", "Polarization"),
    ("unitcell_transform", "Unit cell transform"),
    ("topological_defects", "Topological defects"),
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


def setup_cells() -> list[dict]:
    """Cells to set cwd to repo root and reduce log noise (depol prints hundreds of INFO lines)."""
    md = make_md_cell(
        "## Setup\n\n"
        "Set the working directory to the project root so that paths like `cif/MEP.cif` "
        "used in the examples resolve correctly. Logging is set to WARNING so that "
        "depolarization retry messages (Attempt N/1000 failed) do not flood the output; "
        "set to INFO in a cell if you need to debug."
    )
    code = make_code_cell(
        "import os\n"
        "import logging\n"
        "from pathlib import Path\n\n"
        "# Use repo root so relative paths in examples (e.g. cif/MEP.cif) resolve\n"
        "REPO_ROOT = Path(\".\").resolve()\n"
        "if (REPO_ROOT / \"genice3\").is_dir() and (REPO_ROOT / \"examples\").is_dir():\n"
        "    os.chdir(REPO_ROOT)\n"
        "    print(\"Working directory:\", os.getcwd())\n"
        "else:\n"
        "    print(\"Not in repo root? Set REPO_ROOT and run os.chdir(REPO_ROOT)\")\n"
        "\n"
        "# Suppress INFO from depol loop (Attempt N/1000 failed, etc.) so notebook stays readable\n"
        "logging.getLogger().setLevel(logging.WARNING)\n"
    )
    return [md, code]


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
            # 11_ion_group_unitcell: increase depol_loop in notebook to reduce ConfigurationError
            if py_path.name == "11_ion_group_unitcell.py":
                code = code.replace(
                    "Exporter(\"gromacs\").dump(",
                    "genice.depol_loop = 5000  # notebook: more attempts\nExporter(\"gromacs\").dump(",
                )
            cells.append(make_code_cell(code))
    return cells


def main() -> None:
    intro, nb_meta = load_existing_intro_and_metadata(API_NB)
    setup = setup_cells()
    body_cells = build_cells_from_examples()
    all_cells = intro + setup + body_cells

    nb = {"cells": all_cells, **nb_meta}
    API_NB.write_text(json.dumps(nb, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {API_NB.relative_to(REPO_ROOT)} ({len(all_cells)} cells)")


if __name__ == "__main__":
    main()
