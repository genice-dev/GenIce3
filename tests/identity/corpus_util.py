"""
Identity コーパスの共通ユーティリティ。

ケース ID は (ice, 正規化済み genice_options) の内容ハッシュ。
option_set_index には依存しない。
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from typing import Any, Iterable

SCHEMA_VERSION = 1
STRUCTURE_SEED_DEFAULT = 1
ID_HEX_LEN = 12

_WS_RE = re.compile(r"\s+")


def normalize_options(opts: str) -> str:
    """オプション文字列を比較・ID 用に正規化する。"""
    if not opts:
        return ""
    return _WS_RE.sub(" ", opts.strip())


def case_id(ice: str, genice_options: str) -> str:
    """内容ベースの短いケース ID を返す。"""
    key = f"{ice}\0{normalize_options(genice_options)}"
    return hashlib.sha1(key.encode("utf-8")).hexdigest()[:ID_HEX_LEN]


def product_name(ice: str, case_id_hex: str, formatter: str) -> str:
    return f"{ice}_{case_id_hex}.{formatter}"


def extract_formatter(opts_str: str) -> str | None:
    """opts_str から --exporter NAME の NAME を抽出（: サブオプションの前まで）"""
    parts = opts_str.split()
    for i, p in enumerate(parts):
        if p == "--exporter" and i + 1 < len(parts):
            name = parts[i + 1]
            if name.startswith(":"):
                return None
            return name
    return None


def make_case(
    ice: str,
    genice_options: str,
    formatter: str,
    formatter_path: str = "",
    source: str = "discover",
    structure_seed: int = STRUCTURE_SEED_DEFAULT,
    **extra: Any,
) -> dict:
    """コーパス 1 件分の dict を組み立てる。"""
    opts = normalize_options(genice_options)
    cid = case_id(ice, opts)
    case = {
        "id": cid,
        "ice": ice,
        "target": ice,
        "genice_options": opts,
        "formatter": formatter,
        "formatter_path": formatter_path,
        "product": product_name(ice, cid, formatter),
        "source": source,
        "structure_seed": structure_seed,
    }
    case.update(extra)
    return case


def empty_corpus(structure_seed: int = STRUCTURE_SEED_DEFAULT) -> dict:
    return {
        "schema_version": SCHEMA_VERSION,
        "structure_seed": structure_seed,
        "cases": [],
    }


def load_corpus(path: str) -> dict:
    """corpus.json または旧 discoveries.json（リスト）を読み込む。"""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, list):
        return migrate_legacy_list(data)
    if not isinstance(data, dict) or "cases" not in data:
        raise ValueError(f"Unrecognized corpus format: {path}")
    data.setdefault("schema_version", SCHEMA_VERSION)
    data.setdefault("structure_seed", STRUCTURE_SEED_DEFAULT)
    data.setdefault("cases", [])
    return data


def migrate_legacy_list(
    discoveries: list[dict],
    structure_seed: int = STRUCTURE_SEED_DEFAULT,
) -> dict:
    """旧 discoveries.json（リスト）を corpus 形式へ変換する。"""
    corpus = empty_corpus(structure_seed=structure_seed)
    seen: set[str] = set()
    for d in discoveries:
        ice = d["ice"]
        opts = d.get("genice_options", "")
        formatter = d.get("formatter") or extract_formatter(opts) or "unknown"
        case = make_case(
            ice=ice,
            genice_options=opts,
            formatter=formatter,
            formatter_path=d.get("formatter_path", ""),
            source=d.get("source", "discover"),
            structure_seed=structure_seed,
        )
        if case["id"] in seen:
            continue
        seen.add(case["id"])
        corpus["cases"].append(case)
    return corpus


def save_corpus(corpus: dict, path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(corpus, f, indent=2, ensure_ascii=False)
        f.write("\n")


def merge_cases(existing: Iterable[dict], new_cases: Iterable[dict]) -> list[dict]:
    """id でマージ。既存を優先し、新規は末尾に追加。"""
    by_id: dict[str, dict] = {}
    order: list[str] = []
    for c in existing:
        cid = c["id"]
        if cid not in by_id:
            order.append(cid)
        by_id[cid] = c
    for c in new_cases:
        cid = c["id"]
        if cid not in by_id:
            order.append(cid)
            by_id[cid] = c
    return [by_id[cid] for cid in order]


def cases_list(corpus_or_list: dict | list) -> list[dict]:
    if isinstance(corpus_or_list, list):
        return corpus_or_list
    return list(corpus_or_list.get("cases", []))


def rename_reference_files(
    old_cases: list[dict],
    new_cases: list[dict],
    reference_dir: str,
) -> tuple[int, int]:
    """
    旧 product 名 → 新 product 名へ reference をリネームする。
    対応は (ice, normalize(genice_options)) で取る。
    Returns: (renamed, missing)
    """
    new_by_key = {
        (c["ice"], normalize_options(c["genice_options"])): c for c in new_cases
    }
    renamed = 0
    missing = 0
    if not os.path.isdir(reference_dir):
        return 0, len(old_cases)

    for old in old_cases:
        key = (old["ice"], normalize_options(old.get("genice_options", "")))
        new = new_by_key.get(key)
        if not new:
            continue
        old_path = os.path.join(reference_dir, old["product"])
        new_path = os.path.join(reference_dir, new["product"])
        if old_path == new_path:
            continue
        if not os.path.exists(old_path):
            missing += 1
            continue
        if os.path.exists(new_path):
            os.remove(old_path)
            continue
        os.rename(old_path, new_path)
        old_log = old_path + ".log"
        new_log = new_path + ".log"
        if os.path.exists(old_log) and not os.path.exists(new_log):
            os.rename(old_log, new_log)
        renamed += 1
    return renamed, missing
