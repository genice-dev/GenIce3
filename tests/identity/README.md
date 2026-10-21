# tests/identity — 回帰テスト（構造再現性）

同じ `(ice, options, --seed)` から、過去と同じ構造が出ることを確認する回帰テストです。
論文で使った氷構造の再現性を守るのが主目的です。

不正なオプション組み合わせでのエラー検証は対象外です。旧版で成功した組み合わせだけをコーパスに入れ、それを再実行します。

## 設計の要点

| 項目 | 方針 |
|------|------|
| コーパス | `corpus.json`（内容ベース ID）。リポジトリにコミットする |
| 参照出力 | `reference/`（ローカルのみ、gitignore） |
| ケース ID | `sha1(ice + options)[:12]`。`OPTION_CHOICES` の並び替えで壊れない |
| サンプリング | `discover` は層化（ice / exporter / 各オプション次元を優先） |
| 版間比較 | `make compare OLD=...`（reference 無しでも可） |
| 資源上限 | 1 プロセスあたり **1 GiB**（`MEM_MB=1024`）、timeout 60s。`-j8` 想定 |

タイムアウトやメモリ上限超えは成功扱いしません（コーパスに入れない／テスト失敗）。
大量メモリを食う組み合わせは、identity の対象外として自然に落ちます。

## 前提条件

- プロジェクトルートで `pip install -e .` または `poetry install` 済み
- `genice3` および依存パッケージがインストール済み

## ワークフロー

```bash
cd tests/identity

# 1. 成功組み合わせを発見・拡張（層化。既存にマージするなら MERGE=1）
make discover LIMIT=1000
make discover LIMIT=200 MERGE=1

# 2. 信頼できる版で参照を生成（ローカルのみ）
make update-reference

# 3. 開発中の回帰
make test

# 4. リリース前・大きな変更時の版間比較
make compare OLD=/path/to/old/GenIce3
make compare OLD=/path/to/old/GenIce3 LIMIT=50
```

初回だけ旧 `discoveries.json` がある場合:

```bash
make migrate   # → corpus.json + reference/ のリネーム
```

## コーパス形式（corpus.json）

```json
{
  "schema_version": 1,
  "structure_seed": 1,
  "cases": [
    {
      "id": "7e7fbaba22cf",
      "ice": "NON",
      "target": "NON",
      "genice_options": "--seed 1 --exporter yaplot ...",
      "formatter": "yaplot",
      "formatter_path": "../../genice3/exporter/yaplot.py",
      "product": "NON_7e7fbaba22cf.yaplot",
      "source": "discover",
      "structure_seed": 1
    }
  ]
}
```

- `source`: `desc_test`（unitcell の `desc["test"]`） / `discover` / `manual`
- `product`: `{ice}_{id}.{formatter}`

## オプション空間

[`option_sets.py`](option_sets.py) の `OPTION_CHOICES` が試行空間です。
物理的に意味のある組み合わせだけをユーザーが定義します。
`discover` は実際に `genice3` を走らせ、成功したものだけをコーパスに残します。

## Makefile ターゲット

| ターゲット | 意味 |
|------------|------|
| `make discover` | 層化 discover → `corpus.json` |
| `make update-reference` | `reference/` を並列生成 |
| `make test` | 現行出力 vs `reference/` |
| `make compare OLD=...` | 旧チェックアウトと現行を同じコーパスで比較 |
| `make migrate` | 旧 `discoveries.json` → `corpus.json` |
| `make clean` / `distclean` | 生成物の削除（`distclean` は `reference/` も削除） |

資源上限の変更例: `make test MEM_MB=1024 NTHREADS=8`（`Makefile.rules` を再生成してから）。
macOS では `RLIMIT_AS` が効かないことがあり、その場合は timeout が主な安全弁です。

失敗した `update-reference` は空の参照ファイルを残しません（一時ファイル経由で確定）。
もし古い空ファイルが残っている場合:

```bash
make prune-empty-reference
make update-reference -k
```

イオン近接などで ice-rule `AssertionError` になるケースはコーパスから外す:

```bash
make prune-failed              # assertion のみ
make prune-failed REASON=all   # 欠落 reference を広く除外
```

個別の参照だけ作り直す場合:

```bash
make reference/Struct64_470d0be5b7d1.gromacs
# または明示的に:
make -f Makefile.rules reference/Struct64_470d0be5b7d1.gromacs
```

## アルゴリズム変更時

意図したアルゴリズム変更で出力が変わる場合は:

1. 差分を目視確認する（`make test` または `make compare`）
2. 問題なければ `make update-reference` でローカル参照を更新

同じ seed でも構造が変わる変更は、論文再現の観点で破壊的変更です。

## exporter の決定性

同一構造ならテキストも一致するよう、主要 exporter は waters / ions / edges をソートして出力します。
順序だけ揺れる差分はバグとして扱います。

## 除外

- `iceR` はテストから除外

## 関連ドキュメント

- [失敗分類（別目的）](docs/FAILURE_CLASSIFICATION.md) — バグ洗い出し用。identity 回帰とは別系統
