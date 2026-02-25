#!/usr/bin/env python3
import sys
import os

# Ensure project root is on sys.path so "import genice3" works when run from repo without pip install -e .
_repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

# from genice3.tool import line_replacer
# import distutils.core
from logging import getLogger, INFO, basicConfig
from jinja2 import Environment, FileSystemLoader
import json
import re
import genice3
from genice3.plugin import plugin_descriptors, get_exporter_format_rows, scan
import toml


def citation_slug(key: str) -> str:
    """Citation key -> anchor slug for references.md (e.g. 'Russo 2014' -> 'russo-2014')."""
    s = key.lower().strip()
    s = re.sub(r"[^a-z0-9\s-]", "", s)
    s = re.sub(r"[-\s]+", "-", s).strip("-")
    return s or "ref"


def make_citations(r, link_base=None, citation_keys=None):
    """Format citation keys as a bracketed list.

    - If link_base and key is in citation_keys (i.e. defined in citations.json),
      link to the References page anchor: references.md#slug.
    - If key looks like a URL (starts with http:// or https://), link directly to it.
    - Otherwise, render as plain text (no link).
    """
    if len(r) == 0:
        return ""
    sorted_refs = sorted(r, key=lambda x: (x.split()[-1], x[0]))
    parts = []
    for k in sorted_refs:
        if link_base and citation_keys and k in citation_keys:
            slug = citation_slug(k)
            target = f"{link_base}#{slug}"
            logger.info("Citation link (refs): %s -> %s", k, target)
            parts.append(f"[{k}]({target})")
        elif k.startswith("http://") or k.startswith("https://"):
            logger.info("Citation link (URL): %s -> %s", k, k)
            parts.append(f"[{k}]({k})")
        else:
            parts.append(k)
    return " [" + ", ".join(parts) + "]"


def system_ices(markdown=True, citations=None, link_refs=True):
    desc = plugin_descriptors("unitcell", groups=["system"])
    documented, undocumented, refss = desc["system"]
    link_base = "references.md" if link_refs else None

    header = "| Symbol | Description |\n| ------ | ----------- |\n"
    s = ""
    for description, ices in documented.items():
        citation = make_citations(
            refss[description],
            link_base=link_base,
            citation_keys=citations,
        )
        s += "| " + ", ".join(ices) + " | " + description + citation + " |\n"
    s += "| " + ", ".join(undocumented) + " | (Undocumented) |\n"
    return header + s


def system_molecules(markdown=True, water=False, citations=None, link_refs=True):
    desc = plugin_descriptors("molecule", water=water, groups=["system"])
    documented, undocumented, refss = desc["system"]
    link_base = "references.md" if link_refs else None

    header = "| symbol | type |\n| ------ | ---- |\n"
    s = ""
    for description, ices in documented.items():
        citation = make_citations(
            refss[description],
            link_base=link_base,
            citation_keys=citations,
        )
        s += "| " + ", ".join(ices) + " | " + description + citation + " |\n"
    s += "| " + ", ".join(undocumented) + " | (Undocumented) |\n"
    return header + s


def _plugin_file_path(category: str, group: str, mod: str) -> str:
    """Return a human-readable file path or location for the plugin."""
    if group == "system":
        return f"genice3/{category}/{mod}.py"
    if group == "extra":
        return f"{mod}.py (extra plugin)"
    return f"{category}/{mod}.py (local)"


def collect_missing_citation_refs(citation_keys):
    """Collect refs used in plugins that are not in citations.json and not URLs.
    Returns list of (file_path, ref) for each missing ref.
    """
    missing = []
    for category, water in [("unitcell", None), ("molecule", True), ("molecule", False)]:
        mods = scan(category)
        refs = mods.get("refs", {})
        iswater = mods.get("iswater", {})
        for group in ("system", "extra", "local"):
            for L in mods.get(group, []):
                if category == "molecule":
                    if water is not None and iswater.get(L, False) != water:
                        continue
                if L not in refs:
                    continue
                for ref in refs[L].values():
                    if ref in citation_keys or ref.startswith("http://") or ref.startswith("https://"):
                        continue
                    path = _plugin_file_path(category, group, L)
                    missing.append((path, ref))
    return missing


basicConfig(level=INFO, format="%(levelname)s %(message)s")
logger = getLogger()
logger.debug("Debug mode.")

with open("citations.json") as f:
    citations = json.load(f)

citationlist = [f"[{key}] {desc}" for key, doi, desc in citations]
citation_keys = {key for key, doi, desc in citations}


def format_reference_entry(key: str, doi: str, desc: str, anchor=True) -> str:
    """One reference line: optional HTML anchor for in-doc links, key linked to DOI when available."""
    slug = citation_slug(key)
    anchor_html = f'<span id="{slug}"></span>\n\n' if anchor else ""
    if doi and doi.strip():
        return anchor_html + f"- **[{key}](https://doi.org/{doi})**: {desc.strip()}"
    return anchor_html + f"- **[{key}]**: {desc.strip()}"


def prefix(L, pre):
    return pre + ("\n" + pre).join(L) + "\n"


def format_table_markdown(rows):
    """Build markdown table from exporter format_desc rows."""
    if not rows:
        return ""
    header = "| Name | Application | extension | water | solute | HB | remarks |"
    sep = "| --- | --- | --- | --- | --- | --- | --- |"
    line_rows = [
        "| {name} | {application} | {extension} | {water} | {solute} | {hb} | {remarks} |".format(**r)
        for r in rows
    ]
    return "\n".join([header, sep] + line_rows)


project = toml.load("pyproject.toml")

# Prefer [project] for version and dependencies (single source of truth); fall back to [tool.poetry].
_proj = project.get("project", {})
_poetry = project.get("tool", {}).get("poetry", {})


def _parse_dependency(s: str) -> tuple:
    """Parse PEP 508 dependency string into (name, constraint)."""
    s = s.strip()
    # Match package name (alphanumeric, underscore, hyphen) then optional specifier
    m = re.match(r"^([a-zA-Z0-9_-]+)\s*(\S*)$", s)
    if m:
        name, spec = m.groups()
        return (name, spec.strip() or "*")
    return (s, "*")


if _proj.get("dependencies"):
    _deps_list = _proj["dependencies"]
    _deps_dict = dict(_parse_dependency(d) for d in _deps_list)
    # Template expects tool.poetry.dependencies as dict; inject so existing templates work.
    if "tool" not in project:
        project["tool"] = {}
    if "poetry" not in project["tool"]:
        project["tool"]["poetry"] = {}
    project["tool"]["poetry"]["dependencies"] = _deps_dict

version = _proj.get("version") or _poetry.get("version", "")
citationlist_str = prefix(citationlist, "- ")

# Build template context: merge project with generated values so that
# {{ ices }}, {{ waters }}, {{ guests }}, {{ usage }}, etc. are always set.
try:
    usage_lines = [x.rstrip() for x in os.popen("./genice3.x -h").readlines()]
    usage = "```text\n" + "\n".join(usage_lines) + "\n```"
except Exception as e:
    logger.warning("Failed to get usage: %s", e)
    usage = "```text\n(run ./genice3.x -h for usage)\n```"

try:
    ices = system_ices(citations=citation_keys)
except Exception as e:
    logger.warning("Failed to get ices: %s", e)
    ices = ""

try:
    waters = system_molecules(water=True, citations=citation_keys)
except Exception as e:
    logger.warning("Failed to get waters: %s", e)
    waters = ""

try:
    guests = system_molecules(water=False, citations=citation_keys)
except Exception as e:
    logger.warning("Failed to get guests: %s", e)
    guests = ""

exporter = format_table_markdown(get_exporter_format_rows())

# Build references body from citations.json (written only to docs/references.md when --docs)
_ref_lines = [format_reference_entry(key, doi, desc) for key, doi, desc in citations]
references_md = "# References\n\n" + "\n\n".join(_ref_lines) + "\n"

# Extra plugins from EXTRA.yaml (optional)
_extra_plugins = []
if os.path.exists("EXTRA.yaml"):
    try:
        import yaml
        with open("EXTRA.yaml", "r", encoding="utf-8") as f:
            _ed = yaml.safe_load(f) or {}
        for cat, items in (_ed.get("plugins") or _ed.get("extra_plugins") or {}).items():
            for item in (items if isinstance(items, list) else [items]):
                if isinstance(item, str):
                    _extra_plugins.append({"category": cat, "name": item, "package": item, "note": ""})
                else:
                    n = item.get("name", "")
                    p = item.get("package", n)
                    _extra_plugins.append({"category": cat, "name": n, "package": p, "note": item.get("note", "")})
    except Exception as e:
        logger.warning("Could not load EXTRA.yaml: %s", e)

context = {
    **project,
    "usage": usage,
    "ices": ices,
    "waters": waters,
    "guests": guests,
    "citationlist": citationlist_str,
    "version": version,
    "exporter": exporter,
    "extra_plugins": _extra_plugins,
    "references_md": references_md,
}

env = Environment(loader=FileSystemLoader("."))

if "--docs" in sys.argv:
    # Ensure every ref used in plugins is in citations.json (or is a URL); abort if not
    missing = collect_missing_citation_refs(citation_keys)
    if missing:
        for path, ref in missing:
            logger.error("Missing citation: %s — in %s (add to citations.json or use a URL)", ref, path)
        logger.error("make docs aborted: %d ref(s) missing from citations.json", len(missing))
        sys.exit(1)

    # Render temp_docs/*.md -> docs/*.md with same context as README
    import pathlib
    temp_docs = pathlib.Path("temp_docs")
    docs_out = pathlib.Path("docs")
    docs_out.mkdir(exist_ok=True)
    for stem in [
        "cli",
        "getting-started",
        "output-formats",
        "ice-structures",
        "water-models",
        "guest-molecules",
        "plugins",
    ]:
        path = temp_docs / f"{stem}.md"
        if not path.exists():
            logger.warning("temp_docs/%s.md not found, skip", stem)
            continue
        content = path.read_text(encoding="utf-8")
        t = env.from_string(content)
        out = docs_out / f"{stem}.md"
        out.write_text(t.render(**context), encoding="utf-8")
        logger.info("  %s -> docs/%s.md", stem, stem)
    # Full references list (with DOI links) for the manual
    ref_out = docs_out / "references.md"
    ref_out.write_text(context.get("references_md", "# References\n\n(not generated)\n"), encoding="utf-8")
    logger.info("  references -> docs/references.md")
else:
    template_content = sys.stdin.read()
    t = env.from_string(template_content)
    markdown_en = t.render(**context)
    print(markdown_en)
