# pool_parser から option_parser への乗りかえ作業範囲

## 現状の役割

| 役割 | 場所 | 内容 |
|------|------|------|
| エントリポイント | `genice3/cli/genice.py` | `PoolBasedParser(GENICE3_OPTION_DEFS).parse_args(argv)` → `get_result()` → `validate()` → unitcell/exporter 実行 |
| オプション定義 | `genice3/cli/options.py` | `GENICE3_OPTION_DEFS`（OptionDef の列）、`parse_base_options`、`extract_genice_args` |
| パース・実行 | `genice3/cli/pool_parser.py` | `parse_args` → `parse_command_line_to_dict` → `build_options_dict`（YAML マージ）→ `execute_plugin_chain` → `build_result` |
| 型変換・解釈 | `pool_parser.parse_options_generic` | OptionDef に従い KEYVALUE / TUPLE / STRING / FLAG に変換。unitcell / exporter / molecule が利用。 |
| プラグイン API | unitcell / exporter / molecule | `parse_options(options: OptionPool)` で「消費」し、`processed` を返す。 |

## 参照しているファイル（乗りかえで触る可能性があるもの）

| ファイル | 参照内容 | 作業の方向性 |
|----------|----------|----------------|
| **genice3/cli/genice.py** | `PoolBasedParser`, `GENICE3_OPTION_DEFS`, `extract_genice_args`, `validate_parsed_options` | 新パーサー＋アダプタを呼ぶか、`get_result()` の形を維持するアダプタに差し替え |
| **genice3/cli/options.py** | `OptionDef`, `parse_options_generic`, `parse_bracketed_plugin`；`parse_base_options` | 新構造を受け取る版に変更するか、アダプタ側で現行の「フラット辞書」を組み立てる |
| **genice3/cli/pool_parser.py** | `parse_args`, `build_options_dict`, `load_config_file`, `execute_plugin_chain`, `build_result`, `OptionPool`, `OptionDef`, `parse_options_generic` | 新パスを追加するか、中身を option_parser ベースに置き換え |
| **genice3/cli/validator.py** | `OptionDef` | 検証だけなら OptionDef を残すか、新構造用の検証に変更 |
| **genice3/unitcell/__init__.py** | `OptionDef`, `parse_options_generic`（UNITCELL_OPTION_DEFS） | `parse_options` の引数を「新構造 or 従来どおりの辞書」に合わせる |
| **genice3/unitcell/CIF.py** | `OptionDef`, `parse_options_generic`（CIF_OPTION_DEFS） | 上に同じ |
| **genice3/exporter/gromacs.py** | `OptionDef`, `parse_options_generic` | 上に同じ |
| **genice3/exporter/lammps.py** | `OptionDef`, `parse_options_generic` | 上に同じ |
| **genice3/molecule/__init__.py** | `parse_options_generic` | 上に同じ |
| **tests/test_optionparser_integration.py** | `PoolBasedParser`, `GENICE3_OPTION_DEFS` | 新パーサー経由のテストに拡張 or 置き換え |
| **tests/test_option_parser/** | `PoolBasedParser` 等 | 同上（参照パスは `genice3.cli.pool_parser` 等に合わせる） |

※ `prototype/`, `tests/test_option_parser/pool_parser.py` は別体系のため、乗りかえ対象からは外してよい。

## 作業範囲の目安

### 案A: アダプタで現行 API を維持（変更を少なくする）

1. **新規: アダプタ層（1ファイル）**  
   - 入力: `option_parser.parse_options(line)` の結果（＋必要なら YAML を `option_parser` と同じ構造で読み込みマージ）。  
   - 出力: 現在の `build_result(...)` と同じ形の辞書（`base_options`, `unitcell`, `exporter`, `plugin_chain`）。
2. **genice3/cli/genice.py**  
   - argv を 1 行文字列にし、`option_parser.parse_options` → アダプタ → 得た辞書を現行の `get_result()` の代わりに使用。  
   - `--config` の扱いだけ、YAML 読み込みを新構造対応に変更。
3. **genice3/cli/options.py**  
   - `parse_base_options` がアダプタから渡される「フラットな base_options」を受けられるよう、引数形を合わせる（必要なら少しだけ手を入れる）。
4. **pool_parser.py**  
   - `parse_args` / `build_result` は呼ばない新パスを genice.py に作るだけにし、中身は当面そのまま残す。  
   - 必要なら `load_config_file` を「新構造の YAML」用に別関数として追加し、アダプタから使う。
5. **unitcell / exporter / molecule**  
   - 変更なし。アダプタが「従来どおりの OptionPool 的な辞書」を組み立て、既存の `parse_options(OptionPool)` に渡す。

**想定: 新規 1 ファイル ＋ genice.py の分岐 ＋ options の微調整。unitcell/exporter/molecule は触らない。**

---

### 案B: 新構造をプラグインまで貫く（設計を揃える）

1. **option_parser の出力を「正」とする**  
   - パース結果は常に「unitcell + リストのリスト（スカラー or {arg: サブオプション}）」の形で保持。
2. **アダプタ**  
   - その構造 → `build_result` と互換の辞書に変換（YAML マージも新構造で行う）。
3. **unitcell / exporter / molecule の `parse_options`**  
   - 引数を「新構造の当該部分」（例: cation のリスト、exporter のリスト要素＋サブオプション）を受け取るように変更。  
   - 必要に応じて `parse_options_generic` に相当する「型変換」をプラグイン内 or 共通ヘルパに移動。
4. **OptionDef / parse_options_generic**  
   - 新構造向けに整理するか、プラグインごとの「解釈」に吸収。
5. **options.py**  
   - `parse_base_options` / `extract_genice_args` を新構造対応に書き換え。

**想定: アダプタ ＋ genice.py ＋ options.py ＋ pool_parser の一部 ＋ unitcell/__init__.py, CIF, gromacs, lammps, molecule の `parse_options` とその呼び出し。テストの更新も含む。**

---

## まとめ

| 方針 | 変更ファイル数目安 | 主な作業 |
|------|---------------------|-----------|
| **案A（アダプタで現行維持）** | 少（2〜3） | アダプタ 1 本、genice.py のパース経路の差し替え、必要なら YAML/options の軽い変更 |
| **案B（新構造を貫く）** | 多（10 前後） | 上に加え、全プラグインの `parse_options` と OptionDef/parse_options_generic の見直し |

まずは **案A** で「option_parser → 現行の result 形」に変換するアダプタと、genice.py の切り替えだけ実装し、動作を揃えたうえで、必要なら **案B** に寄せていくのが現実的です。
