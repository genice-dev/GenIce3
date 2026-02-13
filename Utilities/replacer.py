#!/usr/bin/env python3
import sys
import os

# from genice3.tool import line_replacer
# import distutils.core
from logging import getLogger, INFO, basicConfig
from jinja2 import Environment, FileSystemLoader
import json
import genice3
from genice3.plugin import plugin_descriptors, get_exporter_format_rows
import toml


def make_citations(r):
    if len(r) > 0:
        # sort by year, then the initial letter
        return " [" + ", ".join(sorted(r, key=lambda x: (x.split()[-1], x[0]))) + "]"
    return ""


def system_ices(markdown=True, citations=None):
    desc = plugin_descriptors("unitcell", groups=["system"])
    documented, undocumented, refss = desc["system"]

    header = "| Symbol | Description |\n| ------ | ----------- |\n"
    s = ""
    for description, ices in documented.items():
        citation = make_citations(refss[description])
        s += "| " + ", ".join(ices) + " | " + description + citation + " |\n"
        if citations is not None:
            for ref in refss[description]:
                assert ref in citations, f"{ref} in {ices}"
    s += "| " + ", ".join(undocumented) + " | (Undocumented) |\n"
    return header + s


def system_molecules(markdown=True, water=False, citations=None):
    desc = plugin_descriptors("molecule", water=water, groups=["system"])
    documented, undocumented, refss = desc["system"]

    header = "| symbol | type |\n| ------ | ---- |\n"
    s = ""
    for description, ices in documented.items():
        citation = make_citations(refss[description])
        s += "| " + ", ".join(ices) + " | " + description + citation + " |\n"
        if citations is not None:
            for ref in refss[description]:
                assert ref in citations, f"{ref} in {ices}"
    s += "| " + ", ".join(undocumented) + " | (Undocumented) |\n"
    return header + s


basicConfig(level=INFO, format="%(levelname)s %(message)s")
logger = getLogger()
logger.debug("Debug mode.")

with open("citations.json") as f:
    citations = json.load(f)

citationlist = [f"[{key}] {desc}" for key, doi, desc in citations]


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

# Build template context: merge project with generated values so that
# {{ ices }}, {{ waters }}, {{ guests }}, {{ usage }}, etc. are always set.
try:
    usage_lines = [x.rstrip() for x in os.popen("./genice3.x -h").readlines()]
    usage = "```text\n" + "\n".join(usage_lines) + "\n```"
except Exception as e:
    logger.warning("Failed to get usage: %s", e)
    usage = "```text\n(run ./genice3.x -h for usage)\n```"

try:
    ices = system_ices()
except Exception as e:
    logger.warning("Failed to get ices: %s", e)
    ices = ""

try:
    waters = system_molecules(water=True)
except Exception as e:
    logger.warning("Failed to get waters: %s", e)
    waters = ""

try:
    guests = system_molecules(water=False)
except Exception as e:
    logger.warning("Failed to get guests: %s", e)
    guests = ""

citationlist_str = prefix(citationlist, "- ")
version = project["tool"]["poetry"]["version"]
exporter = format_table_markdown(get_exporter_format_rows())

# Auto-generate references.md (full citation list)
with open("references.md", "w", encoding="utf-8") as f:
    f.write("# References\n\n")
    f.write(citationlist_str)

context = {
    **project,
    "usage": usage,
    "ices": ices,
    "waters": waters,
    "guests": guests,
    "citationlist": citationlist_str,
    "version": version,
    "exporter": exporter,
}

env = Environment(loader=FileSystemLoader("."))
template_content = sys.stdin.read()
t = env.from_string(template_content)
markdown_en = t.render(**context)
print(markdown_en)
