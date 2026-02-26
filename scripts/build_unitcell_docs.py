#!/usr/bin/env python3
"""
Unitcell 一覧とサブオプション付きプラグインの表を生成し、docs/unitcells.md を更新する。

実行: リポジトリルートで poetry run python scripts/build_unitcell_docs.py
"""

import re
import sys
from pathlib import Path

# リポジトリルートを path に追加
repo_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo_root))

from genice3.plugin import scan, format_unitcell_usage, _normalize_unitcell_options


def ref_label_to_anchor(label: str) -> str:
    """references.md のアンカー形式へ変換（例: 'Russo 2014' -> 'russo-2014'）。"""
    s = label.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s or "ref"


def format_refs(ref_dict: dict) -> str:
    """desc['ref'] の辞書から References 列用の文字列を生成。"""
    if not ref_dict:
        return ""
    labels = sorted(set(ref_dict.values()))
    result = []
    for lb in labels:
        if lb.startswith("http://") or lb.startswith("https://"):
            continue  # URL は references.md のアンカーにならないのでスキップ
        result.append(f"[[{lb}](references.md#{ref_label_to_anchor(lb)})]")
    return " ".join(result)


def _parse_usage_key_value(usage: str) -> list:
    """usage 文字列から key=value のリストを抽出（表用）。括弧内のカンマでは分割しない。"""
    if not usage or not isinstance(usage, str):
        return []
    one_line = " ".join(usage.splitlines()).strip()
    # 括弧の深さが0のカンマでのみ分割（value に "0:SOD, 1:FAU" があっても1つに保つ）
    parts = []
    start = 0
    depth = 0
    for i, c in enumerate(one_line):
        if c in "([{":
            depth += 1
        elif c in ")]}":
            depth -= 1
        elif c == "," and depth == 0:
            parts.append(one_line[start:i].strip())
            start = i + 1
    parts.append(one_line[start:].strip())
    result = []
    for p in parts:
        if "=" in p:
            k, v = p.split("=", 1)
            result.append((k.strip(), v.strip()))
        elif p:
            result.append((p, ""))
    return result


def main():
    mods = scan("unitcell")
    system = mods["system"]
    desc = mods["desc"]
    refs = mods.get("refs", {})

    # 説明（brief）ごとにシンボルを束ねる（plugin_descriptors と同様）
    from collections import defaultdict
    desced = defaultdict(list)  # brief -> [name, ...]
    refss = defaultdict(set)    # brief -> set of ref labels
    undesc = []
    for name in system:
        brief = desc.get(name)
        if brief:
            desced[brief].append(name)
            if name in refs:
                for label in refs[name].values():
                    if not (label.startswith("http://") or label.startswith("https://")):
                        refss[brief].add(label)
        else:
            undesc.append(name)

    # 行: (symbols カンマ区切り, description, ref_str)。ソートは先頭シンボルで
    rows = []
    for brief, names in desced.items():
        names_sorted = sorted(names)
        symbols = ", ".join(names_sorted)
        ref_str = format_refs({lb: lb for lb in refss[brief]})
        rows.append((symbols, brief, ref_str))
    rows.sort(key=lambda r: r[0].split(",")[0].strip() if r[0] else "")
    # Undocumented は末尾に
    for name in sorted(undesc):
        rows.append((name, "(Undocumented)", ""))

    # サブオプション付きプラグイン（CIF, zeolite 等）
    import importlib
    suboption = []
    for name in sorted(system):
        try:
            mod = importlib.import_module(f"genice3.unitcell.{name}")
            d = getattr(mod, "desc", {})
            usage = d.get("usage", "")
            opts_list = d.get("options")
            has_opts = isinstance(opts_list, list) and len(opts_list) > 0
            if has_opts or (isinstance(usage, str) and "=" in usage):
                brief = d.get("brief", "")
                suboption.append((name, usage.strip() if isinstance(usage, str) else "", brief, opts_list))
        except Exception:
            pass
    suboption_names = {name for name, _, _, _ in suboption}

    # Markdown 出力
    out = []
    out.append("# Unit cells（単位胞一覧）")
    out.append("")
    out.append("第一引数で指定する単位胞名（シンボル）の一覧です。説明が同じ構造は同一行にまとめています。")
    out.append("")
    out.append("<div class=\"unitcell-symbol-table\" markdown=\"1\">")
    out.append("")
    out.append("| Symbol | Description | References |")
    out.append("| ------ | ----------- | ---------- |")
    for symbols, brief, ref_str in rows:
        names_in_row = [s.strip() for s in symbols.split(",")]
        if any(n in suboption_names for n in names_in_row):
            brief = brief + "（オプションあり）"
        brief_esc = brief.replace("|", "\\|")
        out.append(f"| {symbols} | {brief_esc} | {ref_str} |")
    out.append("</div>")
    out.append("")
    out.append("## Unit cell プラグイン（サブオプション付き）")
    out.append("")
    out.append("以下の単位胞は、追加のオプション（ファイルパス・IZAコードなど）が必須です。")
    out.append("")
    out.append("- **CLI:** `--オプション名 値` の形式（例: `genice3 CIF --file MEP.cif`）")
    out.append("- **YAML:** 設定ファイルでは `unitcell:` 配下に `name` とオプションをキーで書く（各プラグインの下に例を示す）")
    out.append("- `genice3 SYMBOL?` でプラグインの usage を表示できます。")
    out.append("")
    for name, usage, brief, opts_raw in suboption:
        out.append(f"### {name}")
        out.append("")
        out.append(brief)
        out.append("")
        # options 構造体からオプション表と 3 表記（CLI/API/YAML）を生成
        if isinstance(opts_raw, list) and opts_raw:
            opts_norm = _normalize_unitcell_options(opts_raw)
            valid_opts = [(o["name"], o["help"]) for o in opts_norm]
            # 3 表記を構造体から合成
            u = format_unitcell_usage(name, opts_raw)
            out.append("**CLI:**")
            out.append("")
            out.append("```")
            out.append(u["cli"])
            out.append("```")
            out.append("")
            out.append("**API:**")
            out.append("")
            out.append("```python")
            out.append(u["api"])
            out.append("```")
            out.append("")
            out.append("**YAML:**")
            out.append("")
            out.append("```yaml")
            out.append(u["yaml"])
            out.append("```")
            out.append("")
            out.append("| CLI オプション | 説明 |")
            out.append("| -------------- | ---- |")
            for k, v in valid_opts:
                v_esc = v.replace("|", "\\|")
                out.append(f"| `--{k}` | {v_esc} |")
            out.append("")
        else:
            # 旧形式: usage から key=value を解析
            opts = _parse_usage_key_value(usage)
            valid_opts = [
                (k, v)
                for k, v in opts
                if k and v and len(k) <= 20 and " " not in k and "\n" not in k
            ]
            if valid_opts:
                out.append("| CLI オプション | 説明 |")
                out.append("| -------------- | ---- |")
                for k, v in valid_opts:
                    v_esc = v.replace("|", "\\|")
                    out.append(f"| `--{k}` | {v_esc} |")
                out.append("")
                _yaml_placeholders = {"file": "path/to/structure.cif", "code": "LTA", "length": "3", "osite": "O", "hsite": "H"}
                out.append("**YAML での指定例:**")
                out.append("")
                out.append("```yaml")
                out.append("unitcell:")
                out.append(f"  name: {name}")
                for k, _ in valid_opts:
                    out.append(f"  {k}: {_yaml_placeholders.get(k, '...')}")
                out.append("```")
                out.append("")
    out.append("---")
    out.append("")
    out.append("Names in quotation marks have not been experimentally verified.")
    out.append("")
    out.append("You can add custom unit cells by placing unit-cell plugins in a `unitcell` directory. [cif2ice](https://github.com/vitroid/cif2ice) can fetch CIF files from the [IZA structure database](http://www.iza-structure.org/databases) and help you create a unitcell module.")
    out.append("")
    out.append("Note: Different naming conventions are used in the literature.")
    out.append("")
    out.append("| CH/FI | CH  | ice | FK    | Zeo | Foam          |")
    out.append("| ----- | --- | --- | ----- | --- | ------------- |")
    out.append("| sI    | CS1 | -   | A15   | MEP | Weaire-Phelan |")
    out.append("| sII   | CS2 | 16  | C15   | MTN |               |")
    out.append("| sIII  | TS1 | -   | sigma | -   |               |")
    out.append("| sIV   | HS1 | -   | Z     | -   |               |")
    out.append("| sV    | HS2 | -   | \\*    | -   |               |")
    out.append("| sVII  | CS4 | -   | \\*    | SOD | Kelvin        |")
    out.append("| sH    | HS3 | -   | \\*    | DOH |               |")
    out.append("| C0    | -   | 17  | \\*    | -   |               |")
    out.append("| C1    | -   | 2   | \\*    | -   |               |")
    out.append("| C2    | -   | 1c  | \\*    | -   |               |")
    out.append("")
    out.append("FI: Filled ices; CH: Clathrate hydrates; FK: Frank-Kasper duals; Zeo: Zeolites; Foam: foam crystals [[Weaire 1994](references.md#weaire-1994)].")
    out.append("")
    out.append("-: No correspondence; \\*: Non-FK types.")
    out.append("")
    out.append("To request new unit cells, contact [vitroid@gmail.com](mailto:vitroid@gmail.com).")

    dest = repo_root / "docs" / "unitcells.md"
    dest.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"Wrote {dest}")


if __name__ == "__main__":
    main()
