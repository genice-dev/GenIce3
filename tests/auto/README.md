# tests/auto — 回帰テスト（参照出力比較）

GenIce3 のプラグイン・オプション組み合わせで、出力が参照と一致することを確認する回帰テストです。

## 概要

- **A**: 参照出力を `reference/` ディレクトリに保存し、Git にコミット
- **C**: `make update-reference` で参照を更新する運用

古い branch で prepare して参照を生成する方式から、参照をリポジトリに含める方式に変更しました。

## 前提条件

- プロジェクトルートで `pip install -e .` または `poetry install` 済み
- `genice3` および依存パッケージがインストール済み

## 使い方

### 初回セットアップ（参照がまだ無い場合）

```bash
cd tests/auto
make update-reference
git add reference/
git commit -m "Add regression test reference outputs"
```

### 回帰テストの実行

```bash
cd tests/auto
make test
```

現在の出力が `reference/` 内のファイルと一致するか `diff` で確認します。

### 参照の更新（意図した変更を行った場合）

```bash
cd tests/auto
make update-reference
git add reference/
git commit -m "Update regression reference outputs for ..."
```

## 生成されるテストケース

`mkmk.py` が以下から動的にテストケースを生成します。

- **unitcell**: `genice3.plugin.scan("unitcell")` の system プラグイン
- **exporter**: `genice3/exporter/*.py`（raw, null, __init__, _KG を除く）
- **オプション**: `--seed 1`, `--rep 1 1 1`, `--water 4site`, `--spot_cation 0=Na --spot_anion 2=Cl`

各 unitcell に対して、exporter とオプションの組み合わせで `reference/{ice}_{i}.{exporter}` を生成・比較します。

## 発見ベースの運用（discover / generate_rules）

従来の `mkmk.py` は固定的なオプションでテストケースを生成します。
一方、`discover.py` と `generate_rules.py` は、genice3 を実際に実行して成功した組み合わせのみを Makefile に含めます。

### ワークフロー

1. **option_sets.py** に試すオプションセットを定義する（物理的制約のためユーザーが設定）
2. **discover.py** を実行し、成功した (ice, options, formatter) を `discoveries.json` に記録
3. **generate_rules.py** で `discoveries.json` から `Makefile.rules` を生成

```bash
cd tests/auto
make discover                              # 全組み合わせ
make discover LIMIT=100                    # ランダムに 100 件だけ（formatter もランダム）
python generate_rules.py -o Makefile.rules # Makefile.rules を上書き
make update-reference
make test
```

`--limit` 指定時は (ice, option_set, formatter) をランダムサンプリング。`--seed 42` で再現可能。

`discoveries.json` は意図的な変更時のみ更新し、`reference/` と同様にコミット可能です。

## この先の予定（未着手）

1. **Makefile.rules の生成**
   - `discoveries.json` ができたら、`generate_rules.py` で `Makefile.rules` を生成
   - 例: `python generate_rules.py -o Makefile.rules`

2. **別 branch との結果の突き合わせ**
   - 別の branch（例: main / 別 feature）で同様に discover を実行し、`discoveries.json` と `reference/` を生成
   - 両 branch の discoveries や参照出力を比較し、差分を確認する作業が必要

## 除外

- `iceR` はテストから除外
- unitcell の `desc["test"]` に定義がある場合、そのオプション組み合わせも使用

## ログファイル

各出力に対して `.log` ファイルも記録されます。

- **update-reference** 時: `reference/{product}.log` に stderr を保存
- **test** 時: `{product}.log` に stderr を保存（カレントディレクトリ、`make clean` で削除）

エラーが出た場合、対応する `.log` を参照して原因を確認できます。

## クリーンアップ

```bash
make clean    # *.diff, *.log を削除
make distclean # 生成物一式を削除（reference/ は残す）
```
