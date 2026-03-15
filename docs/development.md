# 開発環境セットアップ

## Poetry と Git 依存（genice-core）について

`genice-core` は GitHub のブランチ `nx_again` を参照する **Git 依存**です。  
Poetry の既知の不具合（dulwich 由来の `b'HEAD'` 表示／KeyError）の影響で、`poetry install` だけでは **genice-core が正しく入らない**ことがあります。

### 1. 入っているか確認する

```bash
poetry run python -c "import genice_core; print(genice_core.__file__)"
```

- **成功**: パスが表示される → インストール済み
- **失敗**: `ModuleNotFoundError: No module named 'genice_core'` → 未インストール

### 2. 未インストールの場合の対処（推奨）

Poetry の仮想環境に、**pip で直接** genice-core を入れます。  
（`poetry.lock` の `resolved_reference` に合わせると再現性が高いです。）

```bash
# ブランチ指定
poetry run pip install "git+https://github.com/genice-dev/genice-core.git@nx_again"

# または lock のコミット固定（poetry.lock の resolved_reference を参照）
# poetry run pip install "git+https://github.com/genice-dev/genice-core.git@5034b7ce9fe519b2e176d1519e4192354d0c7be3"
```

その後、再度「1. 入っているか確認する」を実行して確認してください。

### 3. 毎回やる場合（例: CI やクリーンインストール）

```bash
poetry install
poetry run pip install "git+https://github.com/genice-dev/genice-core.git@nx_again"
```

### 4. その他

- **`b'HEAD'` が赤字で出る**: Poetry が Git 参照を解決する際の表示バグ。無視してよいです。
- **lock / update / install が一瞬で終わる**: Git 依存の取得に失敗している可能性があります。上記の pip インストールで補ってください。

## リポジトリ内の配置

- **本番テスト**: `tests/`（`tests/test_option_parser/`, `tests/identity/` など）。`make test` で実行。
- **レガシー単位胞テスト**（GenIce2 比較など）: `tests/unitcell_legacy/`。`make unitcell-test` は `tests.unitcell_legacy.lattice_vs_unitcell` を利用。
- **開発用スクリプト**: `scripts/`（例: `test_py3dmol_plugin.py`, `fix_engel_references.py`, `convert_symlinks.py`）。必要に応じて手動実行。
- **設計メモ・試作コードのアーカイブ**: `docs_archive/`。参照用で、ビルドや本番コードには未使用。
