"""
Plugin handler.
"""

import difflib
import glob
import importlib
import os
import re
import sys
from collections import defaultdict
from logging import DEBUG, INFO, basicConfig, getLogger
from textwrap import fill
from typing import Any, Dict, List, Sequence, Tuple, Union

CATEGORIES = ("unitcell", "exporter", "molecule", "group")

# import pkg_resources as pr

if sys.version_info < (3, 10):
    from importlib_metadata import entry_points
else:
    from importlib.metadata import entry_points


def _normalize_unitcell_options(
    options: Sequence[Union[Tuple[str, str], Dict[str, Any]]],
) -> List[Dict[str, Any]]:
    """(name, help) or dict のリストを {name, help, required?, example?} のリストに統一。"""
    result = []
    for opt in options:
        if isinstance(opt, dict):
            result.append({
                "name": str(opt["name"]),
                "help": str(opt.get("help", opt.get("brief", ""))),
                "required": bool(opt.get("required", False)),
                "example": opt.get("example"),
            })
        else:
            name, help_ = opt[0], opt[1]
            required = opt[2] if len(opt) > 2 else False
            example = opt[3] if len(opt) > 3 else None
            result.append({
                "name": str(name),
                "help": str(help_),
                "required": bool(required),
                "example": example,
            })
    return result


def format_unitcell_usage(
    unitcell_name: str, options: Sequence[Union[Tuple[str, str], Dict[str, Any]]]
) -> Dict[str, str]:
    """
    options 構造体から CLI / API / YAML の 3 表記を生成する。
    Returns:
        {"cli": "...", "api": "...", "yaml": "..."}
    """
    opts = _normalize_unitcell_options(options)
    cli_parts = [f"genice3 {unitcell_name}"]
    api_args = []
    yaml_lines = [f"unitcell:", f"  name: {unitcell_name}"]
    for o in opts:
        ex = o.get("example")
        ex_str = str(ex) if ex is not None else "VALUE"
        cli_parts.append(f"--{o['name']} {ex_str}")
        if o.get("required"):
            cli_parts.append("(required)")
        api_args.append(f"{o['name']}={repr(ex)}" if ex is not None else f"{o['name']}=None")
        yaml_lines.append(f"  {o['name']}: {ex}" if ex is not None else f"  {o['name']}: ...")
    return {
        "cli": " ".join(cli_parts) + "\n  " + "\n  ".join(f"--{o['name']}: {o['help']}" for o in opts),
        "api": f'UnitCell("{unitcell_name}", ' + ", ".join(api_args) + ")",
        "yaml": "\n".join(yaml_lines),
    }


def _brief_of(module):
    """One-line description of a plugin, from ``desc`` or an exporter's ``format_desc``."""
    d = getattr(module, "desc", None)
    if isinstance(d, dict) and d.get("brief"):
        return str(d["brief"])
    fd = getattr(module, "format_desc", None)
    if isinstance(fd, dict):
        # "application" may carry a markdown link; the terminal wants the text.
        app = re.sub(r"\[([^]]+)\]\([^)]*\)", r"\1", str(fd.get("application", ""))).strip()
        parts = []
        if app:
            ext = str(fd.get("extension", "")).strip()
            parts.append(f"{app} format ({ext})" if ext else f"{app} format")
        remarks = str(fd.get("remarks", "")).strip()
        if remarks:
            parts.append(remarks if remarks.endswith(".") else remarks + ".")
        if parts:
            return " ".join(parts)
    return None


def _is_water_module(module, category):
    """Return True if the module is a water model (for molecule plugins)."""
    if category != "molecule":
        return False
    if "water" in module.__dict__:
        return True
    if hasattr(module, "Molecule"):
        try:
            m = module.Molecule()
            return getattr(m, "is_water", False)
        except Exception:
            pass
    return False


def scan(category):
    """
    Scan available plugins.
    """
    logger = getLogger()

    modules = {}
    desc = dict()
    iswater = dict()
    refs = dict()
    tests = dict()

    logger.info(f"\nPredefined {category}")
    module = importlib.import_module(f"genice3.{category}")
    mods = []
    for path in module.__path__:
        for mod in sorted(glob.glob(path + "/*.py")):
            mod = os.path.basename(mod)[:-3]
            if mod[:2] != "__":
                mods.append(mod)
    logger.info(mods)
    modules["system"] = mods

    for mod in modules["system"]:
        try:
            module = importlib.import_module(f"genice3.{category}.{mod}")
            brief = _brief_of(module)
            if brief is not None:
                desc[mod] = brief
            if "desc" in module.__dict__:
                if "ref" in module.desc:
                    refs[mod] = module.desc["ref"]
                if "test" in module.desc:
                    tests[mod] = module.desc["test"]
            iswater[mod] = _is_water_module(module, category)
        except BaseException:
            pass

    logger.info(f"Extra {category}")
    groupname = f"genice3_{category}"
    mods = []
    # for ep in pr.iter_entry_points(group=groupname):
    for ep in entry_points(group=groupname):
        mods.append(ep.name)
        try:
            module = ep.load()
            brief = _brief_of(module)
            if brief is not None:
                desc[ep.name] = brief
            if "desc" in module.__dict__:
                if "ref" in module.desc:
                    refs[ep.name] = module.desc["ref"]
                if "test" in module.desc:
                    tests[mod] = module.desc["test"]
            iswater[ep.name] = _is_water_module(module, category)
        except BaseException:
            pass
    logger.info(mods)
    modules["extra"] = mods

    logger.info(f"Local {category}")
    mods = [
        os.path.basename(mod)[:-3] for mod in sorted(glob.glob(f"./{category}/*.py"))
    ]
    logger.info(mods)
    for mod in mods:
        module = importlib.import_module(f"{category}.{mod}")
        brief = _brief_of(module)
        if brief is not None:
            desc[mod] = brief
        if "desc" in module.__dict__:
            if "ref" in module.desc:
                refs[mod] = module.desc["ref"]
            if "test" in module.desc:
                tests[mod] = module.desc["test"]
        iswater[mod] = _is_water_module(module, category)
    logger.info(mods)
    modules["local"] = mods
    modules["desc"] = desc
    modules["iswater"] = iswater
    modules["refs"] = refs
    modules["tests"] = tests

    return modules


def _molecule_kind_wanted(name, iswater, water):
    """Whether a molecule plugin belongs in this listing.

    water=None: all; True: water models only; False: guests only.
    """
    if water is None:
        return True
    flagged = iswater.get(name, False)
    return flagged if water else not flagged


def _format_plugin_table(names, desc, width):
    """Tab-aligned name / description table plus undocumented names."""
    desced = defaultdict(list)
    undesc = []
    for L in names:
        if L in desc:
            desced[desc[L]].append(L)
        else:
            undesc.append(L)
    for dd in desced:
        desced[dd] = ", ".join(desced[dd])
    table = ""
    for dd in sorted(desced, key=lambda x: desced[x]):
        table += f"{desced[dd]}\t{dd}\n"
    if table == "":
        table = "(None)\n"
    table = [
        fill(
            line,
            width=width,
            drop_whitespace=False,
            expand_tabs=True,
            tabsize=16,
            subsequent_indent=" " * 16,
        )
        for line in table.splitlines()
    ]
    table = "\n".join(table) + "\n"
    extra = " ".join(undesc)
    if extra:
        extra = "(Undocumented) " + extra
    return table + "----\n" + extra + "\n \n \n"


def descriptions(category, width=72, water=None, groups=("system", "extra", "local")):
    """
    Show the list of available plugins in the category.

    Options:
      width=72      Width of the output.
      water=None    For molecule plugins: None = water models and guests,
                    True = water models only, False = guests only.
    """
    nouns = {
        "unitcell": "unit cells",
        "exporter": "exporters",
        "molecule": "molecules",
        "group": "cation groups",
    }
    noun = nouns.get(category, f"{category} plugins")
    title = {
        "system": f"1. {noun.capitalize()} served with GenIce3",
        "extra": f"2. {noun.capitalize()} served by external plugins",
        "local": f"3. {noun.capitalize()} served locally",
        "title": f"[Available {noun}]",
    }
    mods = scan(category)
    catalog = f" \n \n{title['title']}\n \n"
    desc = mods["desc"]
    iswater = mods["iswater"]
    split_molecule = category == "molecule" and water is None
    for group in groups:
        catalog += f"{title[group]}\n \n"
        names = list(mods[group])
        if split_molecule:
            waters = [L for L in names if _molecule_kind_wanted(L, iswater, True)]
            guests = [L for L in names if _molecule_kind_wanted(L, iswater, False)]
            catalog += "Water models\n \n"
            catalog += _format_plugin_table(waters, desc, width)
            catalog += "Guest molecules\n \n"
            catalog += _format_plugin_table(guests, desc, width)
            continue
        if category == "molecule":
            names = [L for L in names if _molecule_kind_wanted(L, iswater, water)]
        catalog += _format_plugin_table(names, desc, width)
    return catalog


def plugin_descriptors(category, water=False, groups=("system", "extra", "local")):
    """
    Show the list of available plugins in the category.

    Options:
      water=False   For molecule plugins: True = water models only,
                    False = guests only.
    """
    mods = scan(category)
    catalog = dict()
    desc = mods["desc"]
    iswater = mods["iswater"]
    refs = mods["refs"]
    for group in groups:
        desced = defaultdict(list)
        undesc = []
        refss = defaultdict(set)
        for L in mods[group]:
            if category == "molecule":
                if L not in iswater:
                    iswater[L] = False
                if water and not iswater[L]:
                    continue
                if not water and iswater[L]:
                    continue
            if L in desc:
                # desc[L] is the brief description of the module
                # L is the name of module (name of ice)
                desced[desc[L]].append(L)
                if L in refs:
                    refss[desc[L]] |= set([label for key, label in refs[L].items()])
            else:
                undesc.append(L)
        catalog[group] = [desced, undesc, refss]
    return catalog


def available_plugin_names(category: str) -> List[str]:
    """Return the plugin names of a category without importing the modules.

    Cheap counterpart of :func:`scan`, meant for help messages and for the
    suggestions offered when a name is not found.
    """
    names = set()
    try:
        package = importlib.import_module(f"genice3.{category}")
    except ModuleNotFoundError:
        package = None
    if package is not None:
        for path in package.__path__:
            for mod in glob.glob(os.path.join(path, "*.py")):
                stem = os.path.basename(mod)[:-3]
                if not stem.startswith("__"):
                    names.add(stem)
    for ep in entry_points(group=f"genice3_{category}"):
        names.add(ep.name)
    for mod in glob.glob(f"./{category}/*.py"):
        stem = os.path.basename(mod)[:-3]
        if not stem.startswith("__"):
            names.add(stem)
    return sorted(names)


class PluginNotFoundError(ImportError):
    """No plugin of the requested category carries the requested name."""


def plugin_not_found_error(category: str, name: str) -> PluginNotFoundError:
    """Build an error that names the alternatives instead of only the failure."""
    names = available_plugin_names(category)
    by_lower = {n.lower(): n for n in names}
    lines = [f'Unknown {category} "{name}".']
    if name.lower() in by_lower:
        lines.append(
            f'Did you mean "{by_lower[name.lower()]}"? Plugin names are case-sensitive.'
        )
    else:
        close = difflib.get_close_matches(name, names, n=5, cutoff=0.5)
        if not close:
            close = [
                by_lower[c]
                for c in difflib.get_close_matches(
                    name.lower(), list(by_lower), n=5, cutoff=0.5
                )
            ]
        if close:
            lines.append("Did you mean: " + ", ".join(close) + "?")
    lines.append(
        f"{len(names)} {category} plugins are installed; "
        f"run `genice3 --list {category}` to see them all."
    )
    return PluginNotFoundError(" ".join(lines))


def audit_name(name: str, category: str = "plugin") -> str:
    """
    Audit the mol name to avoid the access to unexpected files
    """
    match = re.match("^[A-Za-z0-9-_]+$", name)
    if match is not None:
        return name
    match = re.match(r"^\[([A-Za-z0-9-_]+) .*\]$", name)
    if match is not None:
        return match.group(1)
    raise ValueError(f"Dubious {category} name: {name}")


def import_extra(category, name):
    logger = getLogger()
    logger.info(f"Extra {category} plugin: {name}")
    groupname = f"genice3_{category}"
    module = None
    # for ep in pr.iter_entry_points(group=groupname):
    for ep in entry_points(group=groupname):
        logger.debug(f"    Entry point: {ep}")
        if ep.name == name:
            logger.debug(f"      Loading {name}...")
            module = ep.load()
    if module is None:
        raise ImportError(f"Nonexistent or failed to load the {category} module: {name}")
    return module


def import_plugin_module(category: str, name: str):
    """プラグインモジュールを読み込む（``?`` や usage 表示による ``sys.exit`` は行わない）。

    Args:
        category: ``"unitcell"`` / ``"exporter"`` / ``"molecule"`` / ``"group"`` のいずれか。
        name: プラグイン名（末尾 ``?`` は含めない）。

    Raises:
        ValueError: ``category`` または ``name`` が不正。
        ImportError: いずれの経路でもモジュールが見つからない。
    """
    if category not in ("exporter", "molecule", "unitcell", "group"):
        raise ValueError(
            f"category must be 'exporter', 'molecule', 'unitcell', or 'group', got: {category}"
        )
    module_name = audit_name(name, category)

    logger = getLogger()
    module = None
    fullname = f"{category}.{module_name}"
    logger.debug(f"Try to Load a local module: {fullname}")
    cwd = os.getcwd()
    path_inserted = cwd not in sys.path
    if path_inserted:
        sys.path.insert(0, cwd)
    try:
        try:
            module = importlib.import_module(fullname)
            logger.debug("Succeeded (local from cwd or path).")
        except ModuleNotFoundError:
            logger.debug(f"Module not found: {fullname}")
            module = None
        except ImportError as e:
            logger.error(f"Error importing module {fullname}: {str(e)}")
            raise
    finally:
        if path_inserted and sys.path and sys.path[0] == cwd:
            sys.path.pop(0)
    if module is None:
        fullname = f"genice3.{category}.{module_name}"
        logger.debug(f"Try to load a system module: {fullname}")
        try:
            module = importlib.import_module(fullname)
            logger.debug("Succeeded.")
        except ModuleNotFoundError:
            logger.debug(f"Module not found: {fullname}")
            module = None
        except ImportError as e:
            logger.error(f"Error importing module {fullname}: {str(e)}")
            raise
    if module is None:
        logger.debug(f"Try to load an extra module: {fullname}")
        try:
            module = import_extra(category, module_name)
        except ImportError:
            raise plugin_not_found_error(category, name) from None
        logger.debug("Succeeded.")
    return module


def safe_import(category, name):
    """
    Load a plugin.

    The plugins can exist either in the system, as a extra plugin, or in the
    local folder.

    category: The type of the plugin; "lattice", "format", "molecule", or "loader".
    name:     The name of the plugin.
    """
    logger = getLogger()
    if category not in ("exporter", "molecule", "unitcell", "group"):
        raise ValueError(
            f"category must be 'exporter', 'molecule', 'unitcell', or 'group', got: {category}"
        )

    # single ? as a plugin name ==> show descriptions (list all)
    if name == "?":
        print(descriptions(category))
        sys.exit(0)

    # SYMBOL? ==> show usage for that plugin (then exit)
    usage = False
    clean_name = name
    if len(name) > 1 and name[-1] == "?":
        usage = True
        clean_name = name[:-1]

    module = import_plugin_module(category, clean_name)

    if usage:
        logger.info(f"Usage for '{clean_name}' plugin")
        d = getattr(module, "desc", None)
        if not isinstance(d, dict):
            d = {}
        brief = _brief_of(module)
        if brief:
            print(brief)
        fd = getattr(module, "format_desc", None)
        suboptions = fd.get("suboptions") if isinstance(fd, dict) else None
        if category == "unitcell" and d.get("options"):
            u = format_unitcell_usage(clean_name, d["options"])
            print("CLI:  ", u["cli"])
            print("API:  ", u["api"])
            print("YAML:\n", u["yaml"])
        elif d.get("usage"):
            print(d["usage"])
        elif suboptions:
            print(f'Suboptions (give as -e "{clean_name} :key value"): {suboptions}')
        else:
            print(f"{clean_name} takes no suboption.")
        sys.exit(0)

    return module


def UnitCell(name, **kwargs):
    """
    Shortcut for safe_import.
    """
    return safe_import("unitcell", name).UnitCell(**kwargs)


def Molecule(name, **kwargs):
    """
    Shortcut for safe_import.
    """
    return safe_import("molecule", name).Molecule(**kwargs)


def Exporter(name, **kwargs):
    """
    Shortcut for safe_import.
    """
    return safe_import("exporter", name)


def Group(name, **kwargs):
    """
    Shortcut for safe_import.
    """
    return safe_import("group", name).Group(**kwargs)


def get_exporter_format_rows(
    category="exporter", groups=("system", "extra", "local"), markdown_name=True
):
    """
    Collect format_desc from all exporter plugins and return rows for the README table.

    Each exporter module may define a ``format_desc`` dict with keys:
      aliases: list of option names (e.g. ["g", "gromacs"])
      application: str (markdown allowed)
      extension: str (e.g. ".gro")
      water: str (e.g. "Atomic positions")
      solute: str
      hb: str (e.g. "none", "o", "auto")
      remarks: str
      suboptions: str (optional; short description of :key value options, e.g. "water_model: 3site, 4site, 6site, tip4p")

    ``markdown_name=True`` のとき ``name`` は README 向けにバッククォート付きの
    エイリアス一覧文字列になる。False のとき ``name`` は生のプラグイン名になり、
    ``aliases`` にエイリアス配列を含める。

    Returns a list of dicts with keys name, aliases, application, extension, water, solute, hb, remarks, suboptions.
    """
    logger = getLogger()
    mods = scan(category)
    rows = []
    seen = set()

    for group in groups:
        for name in mods.get(group, []):
            if name in seen:
                continue
            try:
                if group == "system":
                    mod = importlib.import_module(f"genice3.{category}.{name}")
                elif group == "extra":
                    mod = None
                    for ep in entry_points(group=f"genice3_{category}"):
                        if ep.name == name:
                            mod = ep.load()
                            break
                    if mod is None:
                        continue
                else:
                    try:
                        mod = importlib.import_module(f"{category}.{name}")
                    except ModuleNotFoundError:
                        continue
                if not hasattr(mod, "format_desc"):
                    continue
                if getattr(mod, "alias_of", None):
                    # The module it aliases contributes the row, and the row
                    # already carries every alias in its name column.
                    continue
                fd = mod.format_desc
                aliases = fd.get("aliases", [name])
                if markdown_name:
                    name_col = ", ".join(f"`{a}`" for a in aliases)
                else:
                    name_col = name
                rows.append(
                    {
                        "name": name_col,
                        "aliases": aliases,
                        "application": fd.get("application", ""),
                        "extension": fd.get("extension", ""),
                        "water": fd.get("water", ""),
                        "solute": fd.get("solute", ""),
                        "hb": fd.get("hb", ""),
                        "remarks": fd.get("remarks", ""),
                        "suboptions": fd.get("suboptions", ""),
                    }
                )
                seen.add(name)
            except Exception as e:
                logger.debug(f"Skip {name} for format table: {e}")
    return rows


if __name__ == "__main__":
    basicConfig(level=INFO)
    if len(sys.argv) == 1:
        cats = ("lattice", "format", "molecule", "loader")
    else:
        cats = sys.argv[1:]
    modules = {cat: scan(cat) for cat in cats}
    print(modules)
