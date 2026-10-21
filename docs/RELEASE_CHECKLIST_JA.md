# リリース前チェックリスト（GenIce3）

このチェックリストは、リリース候補を確定して公開するまでの最終確認用です。

## 1. スコープと版管理

- [x] リリース対象コミット（またはタグ候補）を確定した
  - ベース: `3.0b8` + GA 前ブロッカー修正（exporter 決定性、YAML flatten、テスト更新）
  - **含めない:** `tests/identity` の WIP（次バージョン向け）
- [x] 以降に取り込む変更の条件（バグ修正のみ等）を決めた
- [x] バージョン表記を統一した（`pyproject.toml` / `README.md` / `RELEASE_NOTE.md` / skill）→ **3.0**
- [x] 既存タグとの整合を確認した（重複・命名ミスなし）— タグは `3.0`

## 2. ドキュメント

- [x] `RELEASE_NOTE.md` が最新変更を反映している
- [x] `make changes` で `CHANGES.md` を更新し、`RELEASE_NOTE.md` / `CHANGELOG.md` と矛盾がない
- [x] 破壊的変更（互換性注意点）が明記されている
- [x] 新機能・主要修正の使用例が最低1つある
- [x] **ドキュメント本文が英語のみで記述されている（原則）**
- [x] 英語以外の記述が必要な場合は、例外理由を明記した（開発用 `docs/development.md` 等は日本語可）
- [x] `make docs` → `make skill` を実行し、`make skill-check` が通る
- [x] プッシュ後、`npx skills add genice-dev/GenIce3 --list` で `genice3` skill が見つかる

## 3. 機能互換性（要注意）

- [x] 旧スクリプトからの移行で問題になりやすいオプション変更点を確認した
- [x] `pol_loop_1` / `pol_loop_2` など分極関連の移行説明を確認した
- [x] CIF 入力時の挙動（H 位置あり/なし）を期待どおりに確認した（API 例 `cif_io`）
- [x] `partial_order` 廃止の影響を確認した（Compatibility Notes）
- [x] `ice21` と alias（`XXI`）の解決が期待どおりに動作する

## 4. テストと動作確認

- [x] テストスイートを実行し、失敗がない（`make test`）
- [x] `make run-api-examples` で `examples/api` 全サンプルが通る
- [x] ~~`tests/identity`~~ **今回スキップ**（改良中・次バージョン以降）
- [x] 代表的な CLI 実行例をクリーン環境で再現できた
- [x] 代表的な YAML 設定例を実行し、出力を確認した（`examples/config_example.yaml`）
- [x] WebAPI / MCP 関連の最小動作を確認した

## 5. 配布物品質

- [x] sdist / wheel をビルドし、必要ファイルが含まれている（`genice3-3.0`）
- [x] エントリポイント（`genice3` / `genice3-web` / `genice3-mcp`）が有効
- [x] 依存関係の上限・下限で致命的不整合がない
- [x] 既知の制限事項を文書化した
- [x] classifier が `Development Status :: 5 - Production/Stable` である

## 6. 公開準備

- [x] 公開手順（タグ作成、配布、告知）を手順化した
  - タグ `3.0` → GitHub Release → `poetry publish` → Pages / skill 確認
- [x] ロールバック/ホットフィックス方針を決めた（次は `3.0.1`）
- [x] 公開後に確認する監視項目を定義した（`pip install genice3==3.0`、マニュアル、skill、Colab）
- [x] 最終レビュー担当者と承認フローを確定した（メンテナ自身）
