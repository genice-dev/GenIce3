# Archived docs and design notes

このディレクトリは、**本筋のドキュメント・コードから外した**参照用のアーカイブです。

- **旧ドキュメント**: 以前の Jekyll 用設定や Cursor 生成の設計メモ。現在のマニュアルはリポジトリ直下の `docs/` を MkDocs (Material) でビルドし、GitHub Pages に公開しています（`.github/workflows/mkdocs.yml` 参照）。
- **設計・検討メモ**（ルートから移動したもの）:
  - `option_handling_considerations.md` — オプション／YAML 構造の検討
  - `MEMO_bjerrum_defect.md` — Bjerrum 欠陥導入の設計メモ
- **試作コード**: `prototype_option_parser/` — プールベースオプションパーサーの試作（本番は `genice3/cli/` と `tests/test_option_parser/`）。

参照用に残してあり、削除してもビルド・本番コードには影響しません。
