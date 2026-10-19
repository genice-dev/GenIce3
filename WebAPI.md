# WebAPIの設計指針

## ターゲット

- 人間
- AI（**OpenAPI `/openapi.json` および各オペレーションの `description` / `summary` / `tags`** に、エージェント向けの手順と外部マニュアルへのリンクを載せる。自前ブラウザ UI はメタ API で動的に組む）

## エンドポイント

URL は **`/v1/` を付ける**（現状どおり。破壊的変更時に `/v2/` を切れるようにする）。

1. generate: 構造を返す。(LAMMPS, Gromacs, GRO/PDB 相当のテキスト、など exporter に準拠)
   - `POST /v1/generate` … リクエストボディに **設定テキスト**（既定は CLI の `-Y` と同じ YAML。下記「入力」）
   - `POST /v1/generate/json` … JSON `{"config_yaml": "<YAML全文>"}`（**JSON ボディしか送れないクライアント**向けの任意経路。中身の意味は同じ設定スキーマ）
2. メタ query（一覧・**動的 UI 用スキーマ**）
   - 一覧: `GET /v1/meta/unitcells` / `GET /v1/meta/exporters`
   - **unitcell 選択後**: `GET /v1/meta/unitcells/{name}/options` … プラグイン `desc["options"]` を正規化した `specific_options`、多くの格子で使える `common_options`（density, shift, anion, cation 等）、CLI/API/YAML の例文 `examples`
   - **exporter 選択後**: `GET /v1/meta/exporters/{name}/options` … `format_desc`（`suboptions` 文字列含む）と `usage`。あわせて **`dumps()` が出せる書式の宣言**（下記「出力」）

パラメータは CLI と共通の設定スキーマで渡せば、WebAPI のために別 DSL を用意する必要がない。

**可視化**: 3Dmol.js 等の viewer は **クライアント側**で、`generate` が返した構造ファイル（例: GRO）を `addModel` すればよい。**visualize 用の API は設けない**（構造テキストの返却で足りる）。

**範囲の限界**: トポロジカル欠陥（H₃O⁺/OH⁻・Bjerrum）など Python API 専用機能は、この HTTP 面には載せない（CLI/YAML と同じ境界）。

---

## 方針（詰めた点）

### 1. 入力

- **共通の設定スキーマ**（CLI の `-Y` と同一。サブセットにしない）。
- シリアライズは **YAML を正**とし、**それに互換な TOML / JSON** も受け付ける（同じキー構造。パース後は同じ内部表現に流す）。
- Content-Type で判別する（例: `application/x-yaml` / `application/toml` / `application/json`）。判別不能なら YAML として試す、などでよい。

### 2. 出力

- レスポンスには **メタ情報を付ける**（使った seed、exporter、水モデル、原子数、警告、`genice3` / `genice-core` 版など）。
  - 載せ方（JSON ラップ vs `X-GenIce-*` ヘッダ vs multipart）は実装時に一つに決める。メタが必須なら JSON ラップが扱いやすい。
- 各 exporter は **`dumps()` がどういう書式を出せるか宣言する**（例: `text/plain` の GRO、`application/json` の cage_survey、HTML の plotly）。メタ API と OpenAPI の双方からその宣言を読めるようにする。
- クライアント（viewer 含む）は宣言された MIME / 種別を見て本文を解釈する。

### 3. エラー

- **区別する**（少なくとも）:
  - **400**: 設定のパース失敗・未知キー・バリデーション失敗
  - **404**: 存在しない unitcell / exporter 名
  - **422** または **500**: 生成・export 中の失敗（計算不能・内部エラー）。公開時に「クライアント起因 / サーバ起因」をどこで切るかは実装で揃える
  - **413**: リクエスト過大（外部公開時の上限とセット。下記）
- **ログの構造化**は Web API 本体とは別枠。裏セッションで準備中 → できたらここに載せる。

### 4. seed

- 省略時のデフォルトは **CLI / `GenIce3` と同じ `1`**。OpenAPI・マニュアル・メタ情報に **明示**する（「省略＝毎回ランダム」ではない）。

### WebUI と 3Dmol.js

- ブラウザは `generate` のレスポンス本文（または JSON ラップ時はその中の構造テキスト）をそのまま viewer に渡す。別エンドポイントは不要。
- **Plotly exporter**（トポロジ用 HTML）を返したい場合は、`generate` の exporter 選択で足りる。

### サブオプション query（実装方針）

- 固有オプションは各 **unitcell / exporter プラグインの `desc` / `format_desc`** が真実の源泉。Web API はそれを JSON に載せ替えるだけにし、**CLI と矛盾しない**。
- `common_options` は CLI が unitcell 未実装時に消費する **共通キー**（`get_common_unitcell_option_names`）と揃え、UI では「よくある追加欄」として出す。
- 未知のプラグイン名は **404**（ImportError）、不正な記号は **400**（ValueError）。

### 運用

- **上限**（最大原子数・最大実行秒・同時リクエスト数など）は、**外部向け HTTP サービスとして公開するときに定める**。手元・開発用途では必須にしない。
- 大きい `--rep` を同期のままにするか、ジョブ ID＋ポーリングにするかも、公開形態とセットで決める。
- **`/v1/` は付ける**（望ましい・採用）。

---

## 「設定を YAML（等）一本にする」とは何か

以前ここに書いてあった「注意」は分かりにくかったので、言い直す。

ここで言う「一本」は **アプリケーションの設定言語を HTTP 用に新しく作らない**、という意味である。CLI の `-Y`・将来の MCP・Web が、同じ設定オブジェクトを共有する。

これと **別物**なのが次の二つで、混同しやすい。

1. **OpenAPI（`/openapi.json`）**  
   「どの URL に、何を POST し、何が返るか」という **HTTP の地図**。FastAPI が生成する。設定ファイルの中身（unitcell 名や `--rep`）の詳細表ではない。  
   → 設定を YAML にしても OpenAPI は消えないし、置き換えにもならない。

2. **設定ボディの検証**  
   受け取った YAML/TOML/JSON を、GenIce3 既存の設定読み（CLI と同じパス）に流せば、**追加の検証ロジックを Web 専用に書かなくてよい**。  
   必要なら、その結果から JSON Schema をメタ API やドキュメント用に出す、という順でよい（「先に JSON Schema を別実装する」は必須ではない）。

ブラウザから別オリジンで POST する場合は **CORS** が要る。CSRF は Cookie 認証を付けない限り、多くの公開 API では問題にならない（トークン認証にするならそのとき考える）。

**まとめ**: 設定は YAML（互換 TOML/JSON）一本。HTTP の説明は OpenAPI が担う。検証は CLI と同じ読み込みに寄せる。
