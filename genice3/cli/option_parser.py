"""
option_handling.md のルールに従うオプション文字列パーサー。

- 第一引数 = unitcell、以降は -- / : で第一・第二階層を区別。
- 引数は文字列のまま（= で分割しない）。各オプションはリストで、
  要素はスカラー（引数1個のみ）または 1 キーの辞書 { 引数: サブオプション辞書 }。
- 構造体 ↔ オプション文字列 ↔ YAML 表現の往復が可能。

CLI は runner.parse_argv がこのモジュールを利用する。
"""

from __future__ import annotations

from typing import Any, Dict, List, Union


def parse_options(line: str) -> Dict[str, Any]:
    """
    空白で分割し、先頭を unitcell、以降を -- / : のルールで構造体に格納する。

    - 第一引数 = unitcell（省略不可）
    - -- で始まる = 第一階層オプション名、直後からが引数
    - : で始まる = 第二階層（直前の第一階層に引数が1個だけのときのみ）
    - 引数はすべて文字列のまま。= で分割しない。

    Raises:
        ValueError: unitcell が空、または第二階層を引数が1個でない第一階層に付けた場合。
    """
    tokens = line.split()
    if not tokens or tokens[0].startswith("-") or tokens[0].startswith(":"):
        raise ValueError("unitcell が必要（先頭に単位胞名を指定してください）")
    unitcell = tokens[0]
    i = 1
    result: Dict[str, Any] = {"unitcell": unitcell}

    while i < len(tokens):
        if not tokens[i].startswith("--"):
            i += 1
            continue
        opt_name = tokens[i][2:]
        i += 1
        args: List[str] = []
        subopts: Dict[str, List[str]] = {}

        while i < len(tokens) and not tokens[i].startswith("--"):
            if tokens[i].startswith(":"):
                if len(args) != 1:
                    raise ValueError(
                        f"第二階層は第一階層の引数が1個のときのみ: {opt_name} の引数数={len(args)}"
                    )
                sub_name = tokens[i][1:]
                i += 1
                sub_args: List[str] = []
                while i < len(tokens) and not tokens[i].startswith("--") and not tokens[i].startswith(":"):
                    sub_args.append(tokens[i])
                    i += 1
                subopts[sub_name] = sub_args
            else:
                args.append(tokens[i])
                i += 1

        if opt_name not in result:
            result[opt_name] = []

        if subopts:
            result[opt_name].append({args[0]: subopts})
        else:
            for a in args:
                result[opt_name].append([a])

    return result


def _normalize_item(item: Union[list, dict]) -> Union[list, dict, str]:
    """要素1個のリストはスカラーに置き換えてよい、の正規化（表示用）。辞書はそのまま。"""
    if isinstance(item, list) and len(item) == 1 and isinstance(item[0], str):
        return item[0]
    return item


def structure_for_display(data: Dict[str, Any]) -> Dict[str, Any]:
    """構造体を「要素1個のリスト→スカラー」で表示用に整える。"""
    out: Dict[str, Any] = {"unitcell": data["unitcell"]}
    for k, v in data.items():
        if k == "unitcell":
            continue
        if isinstance(v, list):
            out[k] = [_normalize_item(e) for e in v]
        else:
            out[k] = v
    return out


def scalarize_single_item_lists(
    obj: Union[Dict[str, Any], List[Any], str, int, float]
) -> Union[Dict[str, Any], List[Any], str, int, float]:
    """
    再帰的に、要素が1個だけのリストをそのスカラーに置き換える。
    YAML 出力前に適用すると、water: ['4site^ice'] → water: 4site^ice のようになる。
    """
    if isinstance(obj, list):
        if len(obj) == 1:
            return scalarize_single_item_lists(obj[0])
        return [scalarize_single_item_lists(e) for e in obj]
    if isinstance(obj, dict):
        return {k: scalarize_single_item_lists(v) for k, v in obj.items()}
    return obj


def structure_to_option_string(data: Dict[str, Any]) -> str:
    """
    YAML 表現で使った構造体（単成分リストをスカラーにしたもの）を、
    オプション文字列に戻して 1 行で返す。
    サブオプションがない要素ばかりの場合は、--key を1回だけ出して引数を連続で並べる。
    """
    parts: List[str] = [str(data["unitcell"])]
    for key, value in data.items():
        if key == "unitcell":
            continue
        items: List[Any] = value if isinstance(value, list) else [value]
        run: List[str] = []  # サブオプションなしの連続要素
        for item in items:
            if isinstance(item, dict):
                if run:
                    parts.append(f"--{key}")
                    parts.extend(run)
                    run = []
                (arg, subopts), = item.items()
                parts.append(f"--{key}")
                parts.append(str(arg))
                for subk, subv in subopts.items():
                    parts.append(f":{subk}")
                    if isinstance(subv, list):
                        parts.extend(str(x) for x in subv)
                    else:
                        parts.append(str(subv))
            else:
                run.append(str(item))
        if run:
            parts.append(f"--{key}")
            parts.extend(run)
    return " ".join(parts)
