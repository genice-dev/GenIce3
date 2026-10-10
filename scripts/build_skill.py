#!/usr/bin/env python3
"""Build the GenIce3 agent skill (skills/genice3/) from temp_skill/ and docs/.

- temp_skill/SKILL.md is rendered with Jinja2 (version and manual URL from
  pyproject.toml / mkdocs.yml) into skills/genice3/SKILL.md.
- Selected pages of docs/ are copied into skills/genice3/reference/.
  Relative links to copied pages are rewritten to point inside the skill;
  links to other pages point to the published manual.
- The result is validated against the Agent Skills specification
  (https://agentskills.io/specification).

Usage (from the repository root):
    python scripts/build_skill.py           # (re)generate skills/genice3/
    python scripts/build_skill.py --check   # exit 1 if skills/genice3/ is stale
"""

from __future__ import annotations

import argparse
import posixpath
import re
import sys
import tomllib
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = ROOT / "temp_skill"
DOCS = ROOT / "docs"
SKILL_NAME = "genice3"
OUT = ROOT / "skills" / SKILL_NAME

# docs-relative source -> skill-relative destination
REFERENCES = {
    "for-ai-assistants.md": "reference/overview.md",
    "cli.md": "reference/cli.md",
    "basics.md": "reference/basics.md",
    "unitcells.md": "reference/unitcells.md",
    "clathrate-hydrates.md": "reference/clathrate-hydrates.md",
    "guest-molecules.md": "reference/guest-molecules.md",
    "water-models.md": "reference/water-models.md",
    "output-formats.md": "reference/output-formats.md",
    "doping-and-defects.md": "reference/doping-and-defects.md",
    "plugins.md": "reference/plugins.md",
    "citation.md": "reference/citation.md",
    "api-examples/basic.md": "reference/api/basic.md",
    "api-examples/polarization.md": "reference/api/polarization.md",
    "api-examples/guest_occupancy.md": "reference/api/guest_occupancy.md",
    "api-examples/doping.md": "reference/api/doping.md",
    "api-examples/topological_defects.md": "reference/api/topological_defects.md",
    "api-examples/cif_io.md": "reference/api/cif_io.md",
    "api-examples/unitcell_transform.md": "reference/api/unitcell_transform.md",
    "api-examples/exotic_ice.md": "reference/api/exotic_ice.md",
}

LINK = re.compile(r"(!?\[[^\]]*\])\(([^)\s]+)((?:\s+\"[^\"]*\")?)\)")
FENCE = re.compile(r"^\s*(```|~~~)")
NAME_RULE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def manual_url() -> str:
    with open(ROOT / "mkdocs.yml", encoding="utf-8") as f:
        for line in f:
            if line.startswith("site_url:"):
                return line.split(":", 1)[1].strip().rstrip("/")
    raise RuntimeError("site_url not found in mkdocs.yml")


def page_url(base: str, docs_path: str) -> str:
    """URL of a docs/ page on the MkDocs site (use_directory_urls)."""
    if not docs_path.endswith(".md"):
        return f"{base}/{docs_path}"
    stem = docs_path[: -len(".md")]
    if stem == "index":
        return f"{base}/"
    if stem.endswith("/index"):
        stem = stem[: -len("/index")]
    return f"{base}/{stem}/"


def rewrite_link(target: str, src: str, dest: str, base: str) -> str:
    if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target) or target.startswith("#"):
        return target
    path, _, anchor = target.partition("#")
    anchor = f"#{anchor}" if anchor else ""
    docs_path = posixpath.normpath(posixpath.join(posixpath.dirname(src), path))
    if docs_path in REFERENCES:
        rel = posixpath.relpath(REFERENCES[docs_path], posixpath.dirname(dest))
        return rel + anchor
    return page_url(base, docs_path) + anchor


def convert_reference(src: str, dest: str, base: str) -> str:
    text = (DOCS / src).read_text(encoding="utf-8")
    lines = [f"<!-- Generated from docs/{src} by scripts/build_skill.py. Do not edit. -->", ""]
    in_fence = False
    for line in text.splitlines():
        if FENCE.match(line):
            in_fence = not in_fence
        elif not in_fence:
            line = LINK.sub(
                lambda m: f"{m.group(1)}({rewrite_link(m.group(2), src, dest, base)}{m.group(3)})",
                line,
            )
        lines.append(line)
    return "\n".join(lines).rstrip() + "\n"


def render_skill(base: str) -> str:
    with open(ROOT / "pyproject.toml", "rb") as f:
        project = tomllib.load(f)["project"]
    env = Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        undefined=StrictUndefined,
        keep_trailing_newline=True,
    )
    return env.get_template("SKILL.md").render(
        version=project["version"],
        manual_url=base,
    )


def build() -> dict[str, str]:
    """Return {skill-relative path: content} for every generated file."""
    base = manual_url()
    files = {"SKILL.md": render_skill(base)}
    for src, dest in REFERENCES.items():
        files[dest] = convert_reference(src, dest, base)
    return files


def validate(files: dict[str, str]) -> list[str]:
    errors = []
    skill = files["SKILL.md"]
    m = re.match(r"^---\n(.*?)\n---\n", skill, re.DOTALL)
    if not m:
        return ["SKILL.md: YAML frontmatter not found"]
    meta = yaml.safe_load(m.group(1))
    name = meta.get("name", "")
    if not NAME_RULE.match(name) or len(name) > 64:
        errors.append(f"name {name!r}: lowercase letters, digits, single hyphens; at most 64 chars")
    if name != OUT.name:
        errors.append(f"name {name!r} must match the directory name {OUT.name!r}")
    desc = meta.get("description", "")
    if not desc or len(desc) > 1024:
        errors.append(f"description must be 1-1024 chars (got {len(desc)})")
    if len(meta.get("compatibility", "")) > 500:
        errors.append("compatibility must be at most 500 chars")
    for k, v in (meta.get("metadata") or {}).items():
        if not isinstance(v, str):
            errors.append(f"metadata.{k} must be a string (quote it)")
    body_lines = skill[m.end():].count("\n")
    if body_lines > 500:
        errors.append(f"SKILL.md body has {body_lines} lines; keep it under 500")
    for path, text in files.items():
        for target in re.findall(r"\]\((reference/[^)#\s]+)", text):
            resolved = posixpath.normpath(posixpath.join(posixpath.dirname(path), target))
            if resolved not in files:
                errors.append(f"{path}: broken link to {target}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="fail if skills/genice3/ is out of date")
    args = parser.parse_args()

    files = build()
    errors = validate(files)
    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        return 1

    existing = {p.relative_to(OUT).as_posix() for p in OUT.rglob("*") if p.is_file()} if OUT.exists() else set()
    stale = sorted(
        p for p in files if p not in existing or (OUT / p).read_text(encoding="utf-8") != files[p]
    )
    extra = sorted(existing - files.keys())

    if args.check:
        for p in stale:
            print(f"out of date: skills/{SKILL_NAME}/{p}", file=sys.stderr)
        for p in extra:
            print(f"not generated: skills/{SKILL_NAME}/{p}", file=sys.stderr)
        if stale or extra:
            print("Run `make skill` to regenerate.", file=sys.stderr)
            return 1
        print(f"skills/{SKILL_NAME} is up to date.", file=sys.stderr)
        return 0

    for p in extra:
        (OUT / p).unlink()
    for p in stale:
        dest = OUT / p
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(files[p], encoding="utf-8")
    for d in sorted((p for p in OUT.rglob("*") if p.is_dir()), reverse=True):
        if not any(d.iterdir()):
            d.rmdir()
    print(
        f"skills/{SKILL_NAME}: {len(stale)} file(s) written, {len(extra)} removed, "
        f"{len(files) - len(stale)} unchanged.",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
