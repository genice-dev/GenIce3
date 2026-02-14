# genice3 失敗分類と「バグのみ」抽出

## 失敗の分類

| 種別 | 説明 | 例 | 出所 |
|------|------|-----|------|
| **1. ユーザー誤り** | オプションの誤り・未定義 | タイポ、存在しない unitcell/exporter 名、パース/バリデーション失敗 | CLI パース・validate |
| **2. 物理的に矛盾した組み合わせ** | 仕様上あり得ないオプションの組み合わせ | 水素秩序氷に doping、ケージなしで guest、rep 未指定で xFAU | `ConfigurationError` / 特定の `ValueError` |
| **3. 収束しない・実質失敗** | 物理的には矛盾なしだが終わらない／意図と違う結果 | dopant 過多、2重ネットワーク双方にドープ、アルゴリズム未収束 | Timeout / 成功だが結果が不正（検出は別途） |
| **4. バグ** | 想定外の例外・クラッシュ | 未処理の AttributeError, KeyError, TypeError、traceback が出る終了 | 本体・プラグインの実装ミス |
| **5. 環境・リソース**（任意） | 実行環境起因 | メモリ不足、モジュール未インストール、ディスク不足、権限 | システム・Python 環境 |

**補足**

- 2 と 4 の境界: 2 は「意図したチェック」で `ConfigurationError` や特定メッセージの `ValueError` を投げているケース。4 はそれ以外の例外（traceback が stderr に出る）。
- 5 は「genice3 のバグではない」ので、バグ修正ループからは除外したい場合に別カテゴリにすると扱いやすい。

---

## 4（バグ）だけを抽出する手順

### 考え方

- **成功のみ記録する discover** の逆で、「失敗した実行」を全部走らせ、**stderr（と exit code）で分類**する。
- 分類結果のうち「4」だけを一覧化し、修正 → 再実行で減っていくことを確認する。

### 手順の流れ

1. **失敗も記録する discover の変形（例: `discover_failures.py`）**
   - `discover.py` と同様に (ice, option_set) を列挙するが、
   - 各実行で **成功/失敗どちらでも** 次の情報を保存する:
     - `target`, `genice_options`, `formatter`, `exit_code`
     - `stderr` 全文（と必要なら `stdout` の先頭 N 行）
     - 実行時間（timeout かどうかの判定用）
   - 出力: 例として `failures.json`（失敗したケースだけでも、全ケースでも可。分類は次のステップで行う）

2. **失敗理由の自動分類**
   - 各失敗について `stderr` の内容から種別を付与:
     - **1**: `パースエラー` / `validate` 周りのメッセージ、未定義オプション・プラグイン名
     - **2**: `ConfigurationError`、または既知の文言（`Impossible to dope`, `Cage type .* is not defined`, `bondlen and graph`, `rep=n is required` など）
     - **3**: `Timeout` または「Timeout」が stderr に含まれる
     - **4**: **Python の traceback が含まれる**（`Traceback (most recent call last):`, `AttributeError`, `KeyError`, `TypeError` など）
     - **5**: `ModuleNotFoundError`, `MemoryError`, その他環境系メッセージ
   - 複数に当てはまる場合は「一番後ろの処理で起きたもの」を優先（例: traceback があれば 4）などルールを固定する。

3. **4 のみの一覧を作る**
   - 分類結果から `failure_type == 4` のレコードだけを抽出した一覧（JSON や Markdown）を生成。
   - これを「バグ修正用 TODO」として扱い、1 件ずつ修正 → 同じ (ice, options) で再実行して成功 or 別の分類に変わることを確認する。

4. **回帰防止**
   - 既に **成功している組み合わせ**（`discoveries.json`）だけをテストする CI を用意する。
   - ここで失敗した場合は「以前は成功していたのに今は失敗」なので、ほぼ **4（バグ）か環境変化** とみなせる。
   - 逆に、失敗一覧を取るジョブでは「4 の件数」をレポートし、バグ修正で件数が減ることを確認する。

### 分類ルールの疑似コード（stderr ベース）

```text
if "Timeout" in stderr or timeout_occurred:
    → 3
elif "Traceback (most recent call last):" in stderr or "Error:" の後に traceback らしい行:
    → 4  (バグ)
elif "ConfigurationError" in stderr or 既知の ConfigurationError/ValueError メッセージ:
    → 2
elif "パースエラー" in stderr or "バリデーション" 系 or "Nonexistent.*module" 等:
    → 1
elif "ModuleNotFoundError" in stderr or "MemoryError" in stderr:
    → 5
else:
    → 4  (未分類はバグ扱いでリストに載せる)
```

### 運用イメージ

- **週次や PR 時**: 失敗収集スクリプトを実行 → 分類 → `failures_type4.json` を更新。件数が増えていたら要調査。
- **バグ潰し**: `failures_type4.json` のケースを 1 件ずつ再現・修正し、修正後に同じコマンドで成功することを確認。成功したら 4 のリストから削除（または「解消済み」マーク）。
- **CI**: `discoveries.json` ベースの `make test` のみ実行。ここで落ちたら「新規バグ or 環境変化」として検知。

---

## 既存コードとの対応

- **discover.py**: 成功時のみ `discoveries.json` に追加。失敗時は `stderr` を捨てているので、上記手順では「失敗も記録する」拡張か、別スクリプト `discover_failures.py` が必要。
- **run_genice**: 既に `(success, stdout, stderr)` を返しているので、失敗時に `stderr` をファイルや JSON に書き出せば分類の入力になる。
- **genice3 側の例外**: `ConfigurationError` は `genice3/__init__.py` で定義。`ValueError` は各所で使用。これらを「2」用の既知メッセージとして正規表現リスト化すると、分類の一貫性が取りやすい。

このドキュメントと合わせて、`discover_failures.py`（失敗記録）と `classify_failures.py`（分類＋4 のみ抽出）のスケルトンを `tests/auto/` に追加すると、そのまま「4 だけを抽出して修正を繰り返す」手順として使えます。
