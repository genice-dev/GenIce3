"""
option_handling.md のルールに従い、
文字列を空白で分割して構造体に格納するサンプル。

別案: A=B は文字列のまま。各オプションはリスト。
要素はスカラー（引数1個のみ）または 1 キーの辞書 { 引数: サブオプション辞書 }。
"""

from __future__ import annotations

try:
    import yaml
except ImportError:
    yaml = None


def parse_options(line: str) -> dict:
    """
    空白で分割し、先頭を unitcell、以降を -- / : のルールで構造体に格納する。
    - 第一引数 = unitcell（省略不可）
    - -- で始まる = 第一階層オプション名、直後からが引数
    - : で始まる = 第二階層（直前の第一階層に引数が1個だけのときのみ）
    - 引数はすべて文字列のまま。= で分割しない。
    """
    tokens = line.split()
    if not tokens:
        raise ValueError("unitcell が必要")
    unitcell = tokens[0]
    i = 1
    result: dict = {"unitcell": unitcell}

    while i < len(tokens):
        if not tokens[i].startswith("--"):
            i += 1
            continue
        opt_name = tokens[i][2:]
        i += 1
        args: list[str] = []
        subopts: dict[str, list[str]] = {}

        while i < len(tokens) and not tokens[i].startswith("--"):
            if tokens[i].startswith(":"):
                if len(args) != 1:
                    raise ValueError(
                        f"第二階層は第一階層の引数が1個のときのみ: {opt_name} の引数数={len(args)}"
                    )
                sub_name = tokens[i][1:]
                i += 1
                sub_args: list[str] = []
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


def normalize_item(item: list | dict) -> list | dict | str:
    """要素1個のリストはスカラーに置き換えてよい、の正規化（表示用）。辞書はそのまま。"""
    if isinstance(item, list) and len(item) == 1 and isinstance(item[0], str):
        return item[0]
    return item


def structure_for_display(data: dict) -> dict:
    """構造体を「要素1個のリスト→スカラー」で表示用に整える。"""
    out = {"unitcell": data["unitcell"]}
    for k, v in data.items():
        if k == "unitcell":
            continue
        if isinstance(v, list):
            out[k] = [normalize_item(e) for e in v]
        else:
            out[k] = v
    return out


def scalarize_single_item_lists(obj: dict | list | str) -> dict | list | str:
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


def structure_to_option_string(data: dict) -> str:
    """
    YAML 表現で使った構造体（単成分リストをスカラーにしたもの）を、
    オプション文字列に戻して 1 行で返す。
    サブオプションがない要素ばかりの場合は、--key を1回だけ出して引数を連続で並べる。
    """
    parts: list[str] = [str(data["unitcell"])]
    for key, value in data.items():
        if key == "unitcell":
            continue
        items: list = value if isinstance(value, list) else [value]
        run: list[str] = []  # サブオプションなしの連続要素
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


def main() -> None:
    example = (
        "A15 --cation 0=N :group 1=methyl 6=methyl "
        "--cation 4=N :group 3=methyl "
        "--anion 2=Cl 8=Br "
        "--rep 2 2 2 "
        "--seed 99 "
        "--exporter svg :shadow :rotate x=5 y=2 x=3 :size O=0.3 H=0.1 HB=0.05 :water 4site^ice"
    )

    parsed = parse_options(example)
    display = structure_for_display(parsed)

    print("=== 解釈結果（内部構造） ===\n")
    for k, v in parsed.items():
        print(f"  {k}: {v}")

    print("\n=== 表示用（要素1個のリストはスカラーに置換） ===\n")
    for k, v in display.items():
        print(f"  {k}: {v}")

    for_yaml = scalarize_single_item_lists(display)
    if yaml is not None:
        print("\n=== YAML で表示（単成分リストはスカラーに置換後） ===\n")
        yaml_str = yaml.dump(
            for_yaml,
            allow_unicode=True,
            default_flow_style=False,
            sort_keys=False,
        )
        print(yaml_str)
    else:
        print("\n=== YAML で表示 ===\n  (PyYAML 未インストール: pip install pyyaml)")

    print("\n=== オプション文字列に戻す（1行） ===\n")
    print(structure_to_option_string(for_yaml))


if __name__ == "__main__":
    main()
