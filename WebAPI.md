# WebAPIの設計指針

## ターゲット

- 人間
- AI（**OpenAPI `/openapi.json` および各オペレーションの `description` / `summary` / `tags`** に、エージェント向けの手順と外部マニュアルへのリンクを載せる。自前ブラウザ UI はメタ API で動的に組む）

## エンドポイント

1. generate: 構造を返す。(LAMMPS, Gromacs, GRO/PDB 相当のテキスト、など exporter に準拠)
   - `POST /v1/generate` … リクエストボディに **YAML 生テキスト**（`text/plain` / `application/x-yaml` を OpenAPI に記載。実装は `Request.body()` のため他の Content-Type でも可）
   - `POST /v1/generate/json` … JSON `{"config_yaml": "<YAML全文>"}`（**JSON ボディしか送れないクライアント**向けの任意経路。OpenAPI のトップ説明にフローも記載）
2. メタ query（一覧・**動的 UI 用スキーマ**）
   - 一覧: `GET /v1/meta/unitcells` / `GET /v1/meta/exporters`
   - **unitcell 選択後**: `GET /v1/meta/unitcells/{name}/options` … プラグイン `desc["options"]` を正規化した `specific_options`、多くの格子で使える `common_options`（density, shift, anion, cation 等）、CLI/API/YAML の例文 `examples`
   - **exporter 選択後**: `GET /v1/meta/exporters/{name}/options` … `format_desc`（`suboptions` 文字列含む）と `usage`

パラメータはYAML形式で渡すことにすれば、WebAPIのために新たに何かを準備する必要がない。

**可視化**: 3Dmol.js 等の viewer は **クライアント側**で、`generate` が返した構造ファイル（例: GRO）を `addModel` すればよい。**visualize 用の API は設けない**（構造テキストの返却で足りる）。

---

## もう一段詰めるとよい点

### generate

- **入力**: GenIce3 の設定と同一スキーマの YAML（CLI の `-Y` と揃えるか、サブセットかを決める）。
- **出力**: `Content-Type` を exporter に合わせる（例: GRO は `text/plain` または化学系で慣習のある MIME）に加え、**メタ情報**（使った seed、水モデル、原子数、警告）を **JSON でラップするか**、**`X-GenIce-*` ヘッダ**に載せるかを決める。
- **エラー**: バリデーション失敗（400）、計算失敗（422/500）、**リクエスト過大**（413）の区別。
- **再現性**: `seed` を必須または省略時の既定を文書化。

### WebUI と 3Dmol.js

- ブラウザは `generate` のレスポンス本文（または JSON ラップ時はその中の構造テキスト）をそのまま viewer に渡す。別エンドポイントは不要。
- **Plotly exporter**（トポロジ用 HTML）を返したい場合は、`generate` の exporter 選択で足りる。

### サブオプション query（実装方針）

- 固有オプションは各 **unitcell / exporter プラグインの `desc` / `format_desc`** が真実の源泉。Web API はそれを JSON に載せ替えるだけにし、**CLI と矛盾しない**。
- `common_options` は CLI が unitcell 未実装時に消費する **共通キー**（`get_common_unitcell_option_names`）と揃え、UI では「よくある追加欄」として出す。
- 未知のプラグイン名は **404**（ImportError）、不正な記号は **400**（ValueError）。

### YAML 一本にするときの注意

- **OpenAPI（FastAPI が自動生成）**は別途持つ。YAML 本文のスキーマ検証は **JSON Schema 化**、またはサーバ側で GenIce 既存の設定読みに流すかを決める（無検証だと AI も人間も typo に弱い）。
- ブラウザから **POST で YAML** を送る場合は **CORS** と、必要なら **CSRF** の方針。

### 運用（本番を見据えて）

- **同期のみか**、大きい `--rep` 用に **ジョブID＋ポーリング**にするか（タイムアウト・逆プロキシの上限とセット）。
- **上限**: 最大原子数・最大実行秒・同時リクエスト数（公開時）。
- **バージョン**: URL に `/v1/` などを付けるか。
