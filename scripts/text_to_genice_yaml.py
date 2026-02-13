#!/usr/bin/env python3
"""
平文の要望から genice3 用 YAML 設定を生成するプロトタイプ。

使い方:
  # プロンプトを表示（これを LLM に貼って使う）
  python scripts/text_to_genice_yaml.py "Ice Ih を 2x2x2 で GROMACS 形式で出力して"

  # 出力先ファイルを指定（プロンプトのみ書き出し。LLM は手動で呼ぶ）
  python scripts/text_to_genice_yaml.py "..." --prompt-out prompt.txt

  # OpenAI API で YAML を生成（要: pip install openai, 環境変数 OPENAI_API_KEY）
  python scripts/text_to_genice_yaml.py "..." --output config.yaml --openai
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# プロジェクトルートを path に追加（genice3 を import する場合）
_SCRIPT_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _SCRIPT_DIR.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

YAML_SCHEMA = """
## genice3 設定 YAML のスキーマ

- **genice3** (本体オプション):
  - seed: 整数（乱数シード）
  - depol_loop: 整数（分極ループ反復回数）
  - replication_factors: [a, b, c]（単位セルを a,b,c 方向に繰り返し）
  - replication_matrix: 9個の整数のリスト（3x3 複製行列）
  - target_polarization: [Px, Py, Pz]
  - assess_cages: true/false（ケージ評価）
  - debug: true/false
  - spot_anion: キーが水分子インデックス（文字列）、値がイオン名。例 {"1": "Cl"}
  - spot_cation: 同上。例 {"5": "Na"}

- **unitcell** (単位セル):
  - name: 必須。例 1h, Ih, 1c, 2, A15, CIF, sI, sII, ...
  - shift: [x, y, z] 分数座標でのシフト
  - density: 数値 (g/cm³)
  - file: CIF を使う場合のファイルパス
  - anion / cation: 単位セル内のイオン置換

- **exporter** (出力形式):
  - name: 必須。例 gromacs, cif, lammps, yaplot, ...
  - guest: ケージタイプごとのゲスト。例 A12: me, A14: "0.5*co2+0.3*et"
  - spot_guest: ケージ番号ごとのゲスト。例 "0": "4site"
  - water_model: 例 "spce", "4site"
"""

EXAMPLE_1 = """
入力例: 「Ice Ih を 2x2x2 で GROMACS で出力して」
出力YAML:
---
genice3:
  replication_factors: [2, 2, 2]
unitcell:
  name: 1h
exporter:
  name: gromacs
"""

EXAMPLE_2 = """
入力例: 「A15 のクラスレートにメタンを入れて、4site 水モデルで GROMACS 出力。シードは42」
出力YAML:
---
genice3:
  seed: 42
unitcell:
  name: A15
exporter:
  name: gromacs
  guest:
    A12: me
  water_model: "4site"
"""


def get_plugin_lists() -> tuple[list[str], list[str]]:
    """利用可能な unitcell / exporter 名の一覧を取得（genice3 が import できる場合のみ）"""
    try:
        from genice3.plugin import scan
        uc = scan("unitcell")
        ex = scan("exporter")
        unitcells = list(uc.get("system", [])) + list(uc.get("extra", [])) + list(uc.get("local", []))
        exporters = list(ex.get("system", [])) + list(ex.get("extra", [])) + list(ex.get("local", []))
        return (sorted(set(unitcells)), sorted(set(exporters)))
    except Exception:
        return ([], [])


def build_system_prompt(include_plugin_list: bool = True) -> str:
    schema = YAML_SCHEMA.strip()
    if include_plugin_list:
        unitcells, exporters = get_plugin_lists()
        if unitcells or exporters:
            schema += "\n\n利用可能な unitcell 名の例: " + ", ".join(unitcells[:40])
            if len(unitcells) > 40:
                schema += f", ... (計{len(unitcells)}個)"
            schema += "\n利用可能な exporter 名の例: " + ", ".join(exporters[:20])
            if len(exporters) > 20:
                schema += f", ... (計{len(exporters)}個)"
    return schema


def build_full_prompt(user_text: str, include_plugin_list: bool = True) -> str:
    system = build_system_prompt(include_plugin_list=include_plugin_list)
    return f"""あなたは genice3 という氷構造生成プログラムの設定を、利用者の平文の要望に従って YAML で出力するアシスタントです。

## ルール
- 出力は YAML のみとし、説明文は付けない。必要なら先頭に # コメントで短く補足してよい。
- 指定されていない項目は省略する（デフォルトでよい）。
- unitcell.name と exporter.name は必須。要望から推測できない場合は 1h と gromacs をデフォルトとする。

## スキーマとオプション
{system}

## 例
{EXAMPLE_1.strip()}
{EXAMPLE_2.strip()}

---
上記のスキーマと例を参考に、次の利用者の要望を満たす genice3 用 YAML を1つだけ出力してください。
要望: {user_text}
"""


def extract_yaml_from_response(text: str) -> str:
    """LLM の返答から YAML ブロックを抽出する"""
    # ```yaml ... ``` または ``` ... ```
    m = re.search(r"```(?:yaml)?\s*\n(.*?)```", text, re.DOTALL)
    if m:
        return m.group(1).strip()
    # 先頭の --- から続く YAML らしい部分
    if "---" in text:
        parts = text.split("---", 1)
        if len(parts) == 2:
            return parts[1].strip()
    return text.strip()


def call_openai(user_text: str, model: str = "gpt-4o-mini") -> str:
    """OpenAI API で YAML を生成（openai がインストールされていれば）"""
    try:
        from openai import OpenAI
    except ImportError:
        raise SystemExit("OpenAI を使うには pip install openai と環境変数 OPENAI_API_KEY が必要です。")

    client = OpenAI()
    prompt = build_full_prompt(user_text)
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": prompt},
        ],
    )
    content = resp.choices[0].message.content or ""
    return extract_yaml_from_response(content)


def main() -> None:
    ap = argparse.ArgumentParser(description="平文から genice3 用 YAML を生成する（プロンプト出力 or OpenAI）")
    ap.add_argument("text", nargs="?", default="", help="利用者の平文の要望")
    ap.add_argument("--prompt-out", metavar="FILE", help="プロンプトをこのファイルに書き出す")
    ap.add_argument("--output", "-o", metavar="FILE", help="生成 YAML の出力先（--openai 時など）")
    ap.add_argument("--openai", action="store_true", help="OpenAI API で YAML を生成する")
    ap.add_argument("--model", default="gpt-4o-mini", help="OpenAI モデル名（デフォルト: gpt-4o-mini）")
    ap.add_argument("--no-plugin-list", action="store_true", help="プロンプトにプラグイン一覧を含めない")
    args = ap.parse_args()

    user_text = args.text.strip()
    if not user_text:
        # 標準入力から読み取り
        user_text = sys.stdin.read().strip()
    if not user_text:
        ap.print_help()
        sys.exit(0)

    if args.openai:
        yaml_str = call_openai(user_text, model=args.model)
        if args.output:
            Path(args.output).write_text(yaml_str, encoding="utf-8")
            print(f"Wrote: {args.output}", file=sys.stderr)
        print(yaml_str)
        return

    # プロンプトのみ
    prompt = build_full_prompt(user_text, include_plugin_list=not args.no_plugin_list)
    if args.prompt_out:
        Path(args.prompt_out).write_text(prompt, encoding="utf-8")
        print(f"Wrote prompt: {args.prompt_out}", file=sys.stderr)
    else:
        print(prompt)


if __name__ == "__main__":
    main()
