# GenIce2 と GenIce3 の並立方針（リポジトリ・ドキュメント）

- **GenIce2**: 現行公開版。vitroid.github.io/GenIce は GenIce2 の説明。
- **GenIce3**: 開発中。CLI・構造が GenIce2 と異なる。公開後も GenIce2 はユーザー需要のためしばらく並立させる想定。

---

## リポジトリを分けるか・同じにするか

### 結論：**分けたほうが無難**

| 観点 | 同一リポジトリ | リポジトリを分ける |
|------|----------------|-------------------|
| **ユーザーの混乱** | README が「どちら」かで迷いやすい。main を GenIce3 にすると GenIce2 ユーザーが古い情報を探しに来る | GenIce2 用・GenIce3 用で URL がはっきり分かれる |
| **ドキュメント** | 1 サイトで両方の manual をパスで分ける必要あり（/GenIce/ vs /GenIce/genice3 等） | 各リポジトリ＝各マニュアル。GenIce2 は現行 URL 維持、GenIce3 は新 URL でよい |
| **Issue・Release** | ラベルやタグで版を分ける必要。リリース一覧が混ざる | 版ごとに Issue/Release が分離され、運用が単純 |
| **PyPI** | すでに `genice2` と `genice3` は別パッケージなので、リポジトリも分けておくと対応が分かりやすい | パッケージとリポジトリが 1:1 で一致する |
| **「GenIce2 は閉鎖したい」** | 同じ repo だと「main を GenIce3 にしたら GenIce2 はどこ？」となりがち | GenIce2 リポジトリはそのまま「安定版・保守のみ」にできる |
| **デメリット** | 2 リポジトリのメンテ、相互リンク・移行ガイドの管理 | リポジトリが 2 つになる手間（CI などはコピー or テンプレで対応） |

GenIce2 と GenIce3 は「全く異なる」前提なので、**別リポジトリで運用する**のがおすすめです。

---

## リポジトリを分ける場合のイメージ

- **GenIce2（現行）**  
  - リポジトリ: 既存の `vitroid/GenIce` のまま、または `vitroid/GenIce2` に移行してそちらを公式にしても可。  
  - ドキュメント: 現行の https://vitroid.github.io/GenIce を GenIce2 専用のまま維持。  
  - 役割: 安定版。新機能は原則入れず、バグ修正・セキュリティのみ。

- **GenIce3（新版）**  
  - リポジトリ: 新規 `vitroid/GenIce3`（または `vitroid/GenIce-next` など）。  
  - ドキュメント: GenIce3 用に **新規でマニュアルを用意**（例: https://vitroid.github.io/GenIce3 や Read the Docs）。  
  - 役割: メイン開発。README・manual はすべて GenIce3 用に書き直す。

現在の開発が「GenIce2 の repo の中で genice3 を育てている」状態なら、**GenIce3 が安定したタイミングでこのコードベースを GenIce3 専用リポジトリとして push し、GenIce2 は既存リポジトリ（または GenIce2 専用 repo）に固定する**形にするとよいです。

---

## ドキュメントの準備（GenIce3 用に全部やり直す場合）

1. **GenIce3 専用マニュアルを 1 から用意する**  
   - vitroid.github.io/GenIce は GenIce2 用のまま触らない。  
   - GenIce3 用は別 URL（例: vitroid.github.io/GenIce3）で新規サイトを用意。  
   - 内容: インストール、クイックスタート、YAML 設定、unitcell / exporter 一覧、オプション説明など、GenIce2 の説明を流用せず GenIce3 に合わせて書き直す。

2. **GenIce3 リポジトリの README**  
   - 「GenIce3 は氷の水素無秩序構造を生成するツール。GenIce2 の後継で、YAML 設定・CLI が異なります」と明記。  
   - インストール・最小例・「詳細は https://vitroid.github.io/GenIce3 へ」を記載。  
   - 「GenIce2 ユーザーは https://github.com/vitroid/GenIce と https://vitroid.github.io/GenIce を参照」と 1 行リンクを書いておく。

3. **相互リンク**  
   - GenIce2 の README または manual に「次世代版 GenIce3 は ○○ リポジトリ / ○○ マニュアル」を 1 行追加。  
   - GenIce3 の README に「従来版 GenIce2 は ○○」を 1 行追加。  
   - 必要なら「GenIce2 から GenIce3 への移行」を GenIce3 の docs に 1 ページだけ用意すると親切。

4. **AI 向け・検索向け**  
   - `docs/AI_DISCOVERABILITY.md` やクイックスタートのひな形は、**GenIce3 のコマンド・YAML 例**に合わせて書き、GenIce3 のマニュアル／README に反映する。  
   - GenIce2 用の「氷の作り方」は現行マニュアル側に残しておけば、両方が検索でヒットする。

---

## 同一リポジトリにしたい場合（分けない場合）

- **ブランチ or ディレクトリで分ける**  
  - 例: `main` = GenIce3、`genice2` ブランチ = GenIce2。  
  - または `genice2/` と `genice3/` をトップ階層に置く（パッケージは別なので、どちらか一方をデフォルトにする必要あり）。
- **README**  
  - トップ README は「GenIce ファミリー」として、冒頭で「GenIce2（安定版）」「GenIce3（開発版・推奨）」を並べてリンクし、それぞれの README（または docs/）へ誘導する。
- **ドキュメント**  
  - 例: https://vitroid.github.io/GenIce を GenIce2 のままにして、https://vitroid.github.io/GenIce/genice3 で GenIce3 を別パスにまとめる。  
  - または GenIce3 だけ別ドメイン/サブドメイン（例: genice3.vitroid.github.io）にする。

同一リポジトリの場合は「どちらがメインか」を README とナビで明確にしないと、ユーザーが迷いやすいです。

---

## まとめ

- **リポジトリ**: GenIce2 と GenIce3 は **分けたほうがよい**。パッケージ・ドキュメント・Issue の境界がはっきりし、GenIce2 を「保守のみ」にしやすい。
- **ドキュメント**: GenIce3 用は **新規に全部用意**する。現行の vitroid.github.io/GenIce は GenIce2 用のままにし、GenIce3 用は別 URL で新規マニュアルを用意する。
- **並立**: 両方の README とマニュアルに「もう一方」への 1 行リンクを入れ、必要なら GenIce3 側に「GenIce2 からの移行」を 1 ページ用意する。

この方針で進めると、公開後も「GenIce2 はここ」「GenIce3 はここ」が明確に伝わります。
