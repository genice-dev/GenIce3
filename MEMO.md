## Bjerrum欠陥導入について。

### API

- genice.add_bjerrum_L(edges)

### 内部処理（設計方針）

edge (i,j) について。

- (i,j) を非等価な **有向エッジ** として扱う（(j,i) とは別物）。
- Bjerrum 欠陥は **GenIce3 の公開プロパティ（spot_*）を書き換えず**、
  DependencyEngine のリアクティブ関数の内部でのみ反映する。
- hydronium / hydroxide はあくまで「実イオン欠陥」を表し、
  Bjerrum L/D は「水素結合のトポロジカル欠陥」として扱う。

### 実装メモ

- **API 追加案**
  - `genice.add_bjerrum_L(edge_or_edges)`  
    - `edge_or_edges` は `(i, j)` のタプル、またはそのリスト／配列。
    - 片向きの「有向エッジ」として扱う（`(j, i)` とは別物）。
  - 将来必要になれば `genice.add_bjerrum_D(...)` も同様の形で追加する。
- **内部状態の持ち方（候補）**
  - `GenIce3` に非公開メンバとして  
    - `_bjerrum_L_edges: list[tuple[int, int]]`  
    - `_bjerrum_D_edges: list[tuple[int, int]]`  
    を追加する。
  - DependencyEngine の入力としては
    - `bjerrum_L_edges`
    - `bjerrum_D_edges`
    を `_get_inputs()` で渡す形にする（外からは setter / メソッドのみ公開）。
- **DependencyEngine との接続**
  - Bjerrum の影響は、`digraph` リアクティブ関数の **引数として渡された `bjerrum_L_edges` / `bjerrum_D_edges` を元に、その関数の中だけで完結させる。**
  - 典型的な流れ（案）：
    - 入力: `graph, depol_loop, lattice_sites, fixed_edges, target_pol, bjerrum_L_edges, bjerrum_D_edges`
    - 関数内部で：
      - Bjerrum L/D に対応する一時的な「仮想 hydronium / hydroxide 的な制約」をローカルに構成する。
      - それを反映した形で `genice_core.ice_graph(...)` を呼ぶ。
      - 返ってきた `DiGraph` に対し、Bjerrum の定義に従ってローカルにエッジの追加／削除を行う。
    - 重要: **この過程で `GenIce3.spot_*` プロパティや engine.cache には一切触らない**（純粋関数として扱う）。
  - これにより、Bjerrum 用の「後処理フック」が再度リアクションをトリガーすることはなく、
    DependencyEngine から見ても `digraph` は「入力 → 出力」の純粋な変換として扱える。
- **制約・バリデーション**
  - `(i, j)` は必ず `graph` のエッジとして存在する必要がある。
  - `(i, j)` と `(j, i)` を同時に L / D 指定しない（禁止）。
  - hydronium / hydroxide / anion / cation と同じサイトに Bjerrum を重ねない（同じサイト・同じエッジの多重指定は禁止）。
  - 将来的に複数欠陥を同時に扱う場合も、  
    「**hydronium / hydroxide のルールが満たせない組合せならエラー**」という方針でよい。
  - 上記制約を守れば、**実イオン欠陥（hydronium/hydroxide）と Bjerrum 欠陥を同一系に混在させることができる。**
- **サンプルコードとの対応**
  - `examples/api/13_topological_defect2.py` では、
    - hydronium / hydroxide 用サンプル（`12_topological_defect.py`）と同じスタイルで、
    - `find_nearest_edges_pbc`（仮）で `(i, j)` を決定し、
    - `genice.add_bjerrum_L(edges)` を呼ぶ、
    という流れを想定。

