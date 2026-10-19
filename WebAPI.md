# WebAPIの設計指針

## 実装ステータス（2026-10-19）

共有層 [`genice3/service/`](genice3/service/) の上に薄い HTTP アダプタ [`genice3/webapi.py`](genice3/webapi.py)。stdio MCP は [`genice3/mcp.py`](genice3/mcp.py)（同じ service）。

| 項目 | 状態 |
|------|------|
| YAML / TOML / JSON 入力 | 実装済 |
| 成功応答 JSON ラップ `{meta, content, media_type}` | 実装済 |
| seed 省略時 `1` | 実装済（`meta.seed` に明示） |
| exporter `format_desc.media_type` | 主要 exporter + 推定ヘルパ |
| エラー 400 / 404 / 422 / 500 | 実装済 |
| パッケージ | `genice3[web]` / `genice3[mcp]`（本依存から FastAPI 分離） |
| 公式マニュアルでの大宣伝 | しない（現状維持） |

起動例:

```shell
pip install "genice3[web]"
genice3-web                    # または uvicorn genice3.webapi:app

pip install "genice3[mcp]"
genice3-mcp                    # stdio; Cursor 等が子プロセス起動
```

---

## ターゲット

- 人間
- AI（**OpenAPI `/openapi.json` および各オペレーションの `description` / `summary` / `tags`** に、エージェント向けの手順と外部マニュアルへのリンクを載せる。自前ブラウザ UI はメタ API で動的に組む）

## エンドポイント

URL は **`/v1/` を付ける**（破壊的変更時に `/v2/` を切れるようにする）。

1. generate: 構造を返す。(LAMMPS, Gromacs, GRO/PDB 相当のテキスト、など exporter に準拠)
   - `POST /v1/generate` … リクエストボディに **設定テキスト**（既定は CLI の `-Y` と同じ YAML。TOML / JSON 可）
   - `POST /v1/generate/json` … `{"config": {...}}` またはレガシー `{"config_yaml": "<YAML全文>"}`
   - **成功時は常に** `application/json`: `{"meta": {...}, "content": "<構造>", "media_type": "..."}`
2. メタ query（一覧・**動的 UI 用スキーマ**）
   - 一覧: `GET /v1/meta/unitcells` / `GET /v1/meta/exporters`
   - **unitcell 選択後**: `GET /v1/meta/unitcells/{name}/options`
   - **exporter 選択後**: `GET /v1/meta/exporters/{name}/options` … `format_desc` と **`media_type`**

パラメータは CLI と共通の設定スキーマで渡せば、WebAPI のために別 DSL を用意する必要がない。

**可視化**: 3Dmol.js 等の viewer は **クライアント側**で、JSON の `content`（例: GRO）を `addModel` すればよい。**visualize 用の API は設けない**。

**範囲の限界**: トポロジカル欠陥（H₃O⁺/OH⁻・Bjerrum）など Python API 専用機能は、この HTTP / MCP 面には載せない（CLI/YAML と同じ境界）。

**MCP**: `genice3-mcp` は service の薄いラップ（stdio）。tools: `list_unitcells` / `list_exporters` / `get_unitcell_options` / `get_exporter_options` / `generate`。HTTP MCP は後回し。

---

## 方針（確定）

### 1. 入力

- **共通の設定スキーマ**（CLI の `-Y` と同一。サブセットにしない）。
- シリアライズは **YAML を正**とし、**それに互換な TOML / JSON** も受け付ける。
- Content-Type で判別（`application/x-yaml` / `application/toml` / `application/json`）。判別不能なら YAML（先頭 `{` なら JSON）。

### 2. 出力

- **JSON ラップ**（確定）: `meta`（seed, unitcell, exporter, media_type, genice3_version, genice_core_version, warnings）+ `content` + `media_type`。
- 各 exporter は `format_desc.media_type` を宣言。未設定時は `extension` から推定（`genice3.service.media_type`）。

### 3. エラー

- **400**: パース失敗・未知キー・バリデーション失敗
- **404**: 存在しない unitcell / exporter 名
- **422**: 生成・export 中の失敗（`GenerationError`）
- **500**: 予期しない例外
- **413**: 外部公開時の上限とセット（今回は未実装）
- 構造化ログ: Web は JSON 既定（`GENICE_LOG_FORMAT`）。詳細は MEMO のオブザーバビリティ項。

### 4. seed

- 省略時のデフォルトは **CLI / `GenIce3` と同じ `1`**。`meta.seed` と OpenAPI 説明に明示。

### WebUI と 3Dmol.js

- ブラウザは `generate` の JSON の `content` を viewer に渡す（[`examples/web_client/ice3_gromacs_3dmol.html`](examples/web_client/ice3_gromacs_3dmol.html)）。

### サブオプション query

- 固有オプションは各プラグインの `desc` / `format_desc` が真実の源泉。
- 未知のプラグイン名は **404**、不正な記号は **400**。

### 運用

- **上限**は外部向け HTTP サービスとして公開するときに定める。
- **`/v1/` は付ける**（採用）。

---

## 「設定を YAML（等）一本にする」とは何か

「設定 DSL を HTTP 用に新しく作らない」という意味。CLI の `-Y`・MCP・Web が同じ設定オブジェクトを共有する。

これと **別物**:

1. **OpenAPI** … HTTP の地図（設定の中身表ではない）
2. **設定ボディの検証** … CLI と同じ読み込み（`genice3.service` → `cli.runner`）に流す

**まとめ**: 設定は YAML（互換 TOML/JSON）一本。HTTP の説明は OpenAPI。検証と生成は service 層。
