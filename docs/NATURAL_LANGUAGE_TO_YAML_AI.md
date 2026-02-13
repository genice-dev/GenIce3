# 平文要望 → genice3 YAML を生成するAIの作り方

利用者の平文（例：「Ice Ih を 2x2x2 で GROMACS 形式で出力して」）を読み、それに沿った genice3 用 YAML 設定ファイルを生成するAIの設計・実装案です。

---

## 1. genice3 YAML の構造（前提知識）

設定は次の3セクションに分かれます。

| セクション | 役割 | 主なキー例 |
|-----------|------|------------|
| `genice3` | 本体オプション | `seed`, `depol_loop`, `replication_factors`, `replication_matrix`, `target_polarization`, `assess_cages`, `debug`, `spot_anion`, `spot_cation` |
| `unitcell` | 単位セル | `name`（必須）, `shift`, `density`, `file`（CIF用）, `anion`, `cation` など |
| `exporter` | 出力形式 | `name`（必須）, `guest`, `spot_guest`, `water_model`, `shift` など |

- コマンドラインで指定した値が YAML を上書きする。
- プラグインごとに追加オプションがある（例: gromacs の `guest`, unitcell の `shift`）。

---

## 2. 実装アプローチの候補

### A. LLM + プロンプト（推奨・手軽）

**概要**: OpenAI / Claude / ローカルLLM などに「genice3 の YAML スキーマと例」をプロンプトで渡し、平文から YAML 文字列を生成させる。

**メリット**  
- 既存コード変更がほぼ不要。  
- スキーマや例を変えるだけで挙動を調整しやすい。  

**やること**  
1. **システムプロンプト**に以下を入れる:  
   - YAML の3セクション説明、主要オプション一覧、型（数値・リスト・真偽値など）。  
   - 利用可能な unitcell / exporter 名のリスト（または「不明な場合は省略」と指示）。  
2. **ユーザープロンプト**: 利用者の平文そのまま。  
3. **出力**: YAML のみ返すよう指示（「```yaml ... ```」で囲む等）。  
4. 必要なら **Few-shot**: 平文→YAML の例を2〜3個入れる。

**運用**:  
- Cursor / ChatGPT 等で「このプロンプトで聞く」用のスニペットやルールとして保存。  
- または `genice3-yaml-from-text` のような CLI スクリプトで API を叩き、ファイルに書き出す。

### B. ルールベース + LLM のハイブリッド

**概要**:  
- キーワードで「単位セル名」「rep」「exporter名」などを正規表現や簡易NLUで抽出。  
- それでも決まらない部分（曖昧な表現など）だけ LLM に聞く。

**メリット**: 確実に決まる部分は安定、曖昧な部分だけ LLM で補う。  
**デメリット**: キーワード辞書とルールのメンテが必要。

### C. ファインチューニング / 専用モデル

**概要**: 平文→YAML のペアを多数用意し、小さい言語モデルをファインチューニングする。

**メリット**: プロンプトが短くて済む、応答が速い。  
**デメリット**: データ作成・学習パイプラインが必要。まずは A で検証してから検討するのが現実的。

---

## 3. プロンプトに含める「オプション仕様」の要約

プロンプト用に、仕様を短くまとめたテキストを用意するとよいです（以下は要約例）。

```
## genice3 YAML スキーマ

- genice3:
  - seed: 整数（乱数シード）
  - depol_loop: 整数（分極ループ反復回数）
  - replication_factors: [a, b, c] または rep（単位セルの a,b,c 方向の繰り返し）
  - replication_matrix: 9整数のリスト（3x3 複製行列）
  - target_polarization: [Px, Py, Pz]
  - assess_cages: true/false
  - debug: true/false
  - spot_anion: {"水分子インデックス": "イオン名"} 例 {"1": "Cl"}
  - spot_cation: {"水分子インデックス": "イオン名"} 例 {"5": "Na"}

- unitcell:
  - name: 必須。例 1h, Ih, 1c, 2, A15, CIF, ...
  - shift: [x, y, z] 分数座標
  - density: 数値 (g/cm³)
  - file: CIF のときのファイルパス
  - anion / cation: 単位セル内の置換

- exporter:
  - name: 必須。例 gromacs, cif, lammps, yaplot, ...
  - guest: ケージタイプごとのゲスト 例 A12: me, A14: "0.5*co2+0.3*et"
  - spot_guest: ケージ番号ごとのゲスト 例 "0": "4site"
  - water_model: 例 "spce", "4site"
```

利用可能な `unitcell` / `exporter` 名は、`genice3` の entry_points から取得するスクリプトで一覧化し、そのリストをプロンプトに含めると精度が上がります。

---

## 4. プロトタイプの流れ（A 案）

1. **スキーマ＋例をまとめたテキスト**を用意（上記 + `examples/api/*.yaml` から数例）。  
2. **CLI またはノートブック**で:  
   - 平文を入力  
   - LLM API を呼び出し（プロンプト = スキーマ + 例 + 平文）  
   - 返答から YAML 部分を抽出  
   - ファイルに保存 or 標準出力  
3. **検証**: 生成した YAML を `genice3 --config generated.yaml` で実行してエラーにならないか確認。

---

## 5. まとめ

- **まずは「LLM + よく整理したプロンプト」で試す**のが作りやすく、genice3 の仕様変更にも追従しやすい。  
- プロンプトには「genice3 YAML の3セクション」「主要オプションと型」「利用可能なプラグイン名」「1〜2個の平文→YAML 例」を含める。  
- 必要ならルールベースでキーワード抽出を足し、曖昧な部分だけ LLM に任せるハイブリッドに発展させる。  
- データが溜まったら、のちにファインチューニングで専用モデルを検討する。
