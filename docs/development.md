# 開発環境セットアップ

## genice-core 1.6.0（MCF デフォルト）

GenIce3 は **genice-core >= 1.6.0**（PyPI）を要求します。`ice_graph` の既定 `connect_engine` は
`connect_matching_paths_mcf` です（GenIce3 側での注入は不要）。

```bash
poetry install   # poetry.lock で 1.6.0 が固定される
```

genice-core をローカルで開発する場合:

```bash
poetry run pip install -e ../genice-core
```

## Poetry と Git 依存（旧手順・参考）

以前は `genice-core` を Git ブランチ `nx_again` から入れていました。現在は PyPI の **1.6.0 以降**を使ってください。  
Poetry のキャッシュが古いと `poetry update genice-core` が失敗することがあります。そのときは `poetry cache clear pypi --all` の後に再実行してください。

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

## 変更履歴ファイルの役割

| ファイル | 役割 | 更新方法 |
|----------|------|----------|
| `CHANGELOG.md` | **バージョン単位の要約**（GenIce 0.x〜1.x、GenIce2 1.0.x、GenIce3 3.0a/b）。利用者向け。 | リリース時に手で追記（過去分は git ログ・タグから要約済み）。 |
| `CHANGES.md` | **フォーク以降の全コミット一覧**（監査・リリース前の差分確認用）。 | `make changes` で自動生成（コミットしない運用も可）。 |
| `RELEASE_NOTE.md` | **現行ベータ期間の叙述**（互換性注意・大きなテーマ）。リリース候補の説明文。 | リリース前に手で更新。 |
| `templates/new-in-genice3.md` | **GenIce2 からの主な変更**（README・マニュアルで共有する本文）。 | 内容を直したら `make README.md` と `make docs`。 |
| `docs/changes-from-genice2.md` | 上記テンプレートの生成結果（MkDocs）。 | `temp_docs/changes-from-genice2.md` 経由で `make docs`。 |
| `README.md` | PyPI / GitHub トップ（`temp_README.md` から生成）。 | `make README.md`。 |

`temp_README.md` の「New in GenIce3」、`docs/getting-started.md`、`docs/changes-from-genice2.md` は同じ `templates/new-in-genice3.md` を include する。

## エージェント skill（`skills/genice3/`）

AI エージェント向けの skill（[Agent Skills](https://agentskills.io) 形式）は `make skill` で生成する。手で編集しない。

| 生成物 | 元 |
|--------|----|
| `skills/genice3/SKILL.md` | `temp_skill/SKILL.md`（Jinja2。`version` は `pyproject.toml`、`manual_url` は `mkdocs.yml` の `site_url`） |
| `skills/genice3/reference/*.md` | `docs/` の一部（対応表は `scripts/build_skill.py` の `REFERENCES`） |

- 生成時に、コピーしたページ同士のリンクは skill 内の相対リンクに、それ以外のリンクはマニュアルの URL に書き換える。名前・description の長さなど Agent Skills 仕様の検証もここで行う。
- `make docs` の後に `make skill` を実行する（`make all` はこの順で両方を実行する）。
- `make skill-check` は、生成物が最新でなければ失敗する。リリース前や CI で使う。
- 配布はこのリポジトリから直接行う。`npx skills add genice-dev/GenIce3` と `gh skill install genice-dev/GenIce3 genice3` は、どちらも `skills/*/SKILL.md` を自動で見つける。`gh skill` は `genice3@3.0b8` のようにタグで版を固定できるので、リリースタグを打つ前に `make skill` の結果をコミットしておく。
- skill に載せるページを増減するときは `REFERENCES` と `temp_skill/SKILL.md` の参照表の両方を直す。
- `temp_skill/SKILL.md` と `docs/for-ai-assistants.md` は似たコマンド例を別々に持つ。`make skill-check` は両者の食い違いを見ないので、片方のオプションを変えたらもう片方も確認する。`tests/test_doc_commands.py`（`make test` に含まれる）が両文書の `genice3` コマンド例を実際に実行し、通らない例があれば失敗する。

## リポジトリ内の配置

- **本番テスト**: `tests/`（`tests/test_option_parser/`, `tests/identity/` など）。`make test` で実行。
- **レガシー単位胞テスト**（GenIce2 比較など）: `tests/unitcell_legacy/`。`make unitcell-test` は `tests.unitcell_legacy.lattice_vs_unitcell` を利用。
- **開発用スクリプト**: `scripts/`（例: `test_py3dmol_plugin.py`, `fix_engel_references.py`, `convert_symlinks.py`）。必要に応じて手動実行。
- **設計メモ・試作コードのアーカイブ**: `docs_archive/`。参照用で、ビルドや本番コードには未使用。
