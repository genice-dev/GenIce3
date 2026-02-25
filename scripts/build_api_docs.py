#!/usr/bin/env python3
"""
Generate docs/api-examples/*.md from examples/api READMEs and sample code.

- Each page contains the README body plus a "Sample code" section.
- When multiple extensions (.py, .sh, .yaml) share the same base name, they are
  shown in Material content tabs.
- File names link to the file on GitHub (repo_url + branch + path).
"""
from __future__ import annotations

import re
from pathlib import Path

# Paths relative to repo root (script is in scripts/)
REPO_ROOT = Path(__file__).resolve().parent.parent
EXAMPLES_API = REPO_ROOT / "examples" / "api"
DOCS_API_EXAMPLES = REPO_ROOT / "docs" / "api-examples"
REPO_URL = "https://github.com/genice-dev/GenIce3"
BRANCH = "main"
CODE_EXTENSIONS = (".py", ".sh", ".yaml")


def get_language(ext: str) -> str:
    if ext == ".py":
        return "python"
    if ext == ".sh":
        return "bash"
    if ext == ".yaml":
        return "yaml"
    return "text"


def group_files_by_stem(dir_path: Path) -> dict[str, list[Path]]:
    """Group code files by stem (name without extension). Only .py, .sh, .yaml."""
    groups: dict[str, list[Path]] = {}
    for f in dir_path.iterdir():
        if f.suffix.lower() in CODE_EXTENSIONS and f.is_file():
            stem = f.stem
            groups.setdefault(stem, []).append(f)
    for stem in groups:
        groups[stem].sort(key=lambda p: (p.suffix.lower(), p.name))
    return dict(sorted(groups.items()))


def github_file_url(category: str, filename: str) -> str:
    return f"{REPO_URL}/blob/{BRANCH}/examples/api/{category}/{filename}"


def build_sample_code_section(category: str, groups: dict[str, list[Path]]) -> str:
    """Build Markdown for Sample code section with tabs and links."""
    lines = ["## Sample code", ""]
    for stem, files in groups.items():
        if not files:
            continue
        # Links to GitHub (one line per file or comma-separated)
        link_parts = [f"[`{f.name}`]({github_file_url(category, f.name)})" for f in files]
        lines.append(f"### {stem}")
        lines.append("")
        lines.append(" | ".join(link_parts))
        lines.append("")
        if len(files) == 1:
            f = files[0]
            content = f.read_text(encoding="utf-8", errors="replace")
            lang = get_language(f.suffix)
            lines.append(f"```{lang}")
            lines.append(content.rstrip())
            lines.append("```")
        else:
            for f in files:
                content = f.read_text(encoding="utf-8", errors="replace").rstrip()
                lang = get_language(f.suffix)
                # Material content tabs: === "Title" then indented body (4 spaces)
                lines.append(f'=== "{f.name}"')
                lines.append("")
                lines.append("    ```" + lang)
                for line in content.splitlines():
                    lines.append("    " + line)
                lines.append("    ```")
                lines.append("")
        lines.append("")
    return "\n".join(lines).rstrip()


def build_page(category: str, readme_path: Path, out_path: Path) -> None:
    """Build one api-examples page: README content + Sample code."""
    readme_content = readme_path.read_text(encoding="utf-8", errors="replace").strip()
    groups = group_files_by_stem(readme_path.parent)
    if not groups:
        # No code files (e.g. only README) – output README only
        out_path.write_text(readme_content + "\n", encoding="utf-8")
        return
    sample_section = build_sample_code_section(category, groups)
    out_path.write_text(readme_content + "\n\n---\n\n" + sample_section + "\n", encoding="utf-8")


def main() -> None:
    DOCS_API_EXAMPLES.mkdir(parents=True, exist_ok=True)

    # Index (overview): examples/api/README.md only
    index_readme = EXAMPLES_API / "README.md"
    if index_readme.exists():
        out = DOCS_API_EXAMPLES / "index.md"
        if out.exists():
            out.unlink()  # remove symlink so we don't overwrite the target
        out.write_text(index_readme.read_text(encoding="utf-8", errors="replace"), encoding="utf-8")
        print(f"  {out.relative_to(REPO_ROOT)}")

    # Each subdir: README + sample code
    for subdir in sorted(EXAMPLES_API.iterdir()):
        if not subdir.is_dir():
            continue
        readme = subdir / "README.md"
        if not readme.exists():
            continue
        category = subdir.name
        out_path = DOCS_API_EXAMPLES / f"{category}.md"
        # Remove existing symlink so we write a real file
        if out_path.exists():
            out_path.unlink()
        build_page(category, readme, out_path)
        print(f"  {out_path.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    print("Generating docs/api-examples/*.md ...")
    main()
    print("Done.")
