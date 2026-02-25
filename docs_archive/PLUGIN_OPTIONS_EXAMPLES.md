# プラグインオプション指定の実例比較

## 使用例

以下の階層的なプラグイン構成を、各手法でどのように表現するか比較します。

### 例 1: 単純なゲスト指定

- genice3
  - 主引数: A15 (結晶構造)
  - オプション: shift 0.1 0.1 0.1
  - オプション: anion 1=Cl
  - オプション: rep 3 3 3
  - オプション: cation 6=Na
  - オプション: exporter gromacs
    - gromacs のオプション: guest A12=me
      - me のオプション: monatomic
    - gromacs のオプション: guest A14=et
      - et のオプション: molecular
    - gromacs のオプション: spot_guest 0=propane

### 例 2: 混合ゲスト分子と占有率の指定

- genice3
  - 主引数: A15 (結晶構造)
  - オプション: shift 0.1 0.1 0.1
  - オプション: anion 1=Cl
  - オプション: rep 3 3 3
  - オプション: cation 6=Na
  - オプション: exporter gromacs
    - gromacs のオプション: guest A12=me*0.3+et*0.6
      - me のオプション: monatomic
      - et のオプション: molecular
    - gromacs のオプション: spot_guest 0=propane

**注意**:

- `me*0.3+et*0.6` は、A12 ケージに me を 30%、et を 60%の占有率で配置することを意味します。
- この例では、`guest` と `spot_guest` は gromacs exporter プラグインのオプションとして指定されています。現在の実装では、これらは genice3 のメインオプション（`--guest`、`--spot_guest`）として指定されますが、exporter プラグイン内で指定する方法を検討しています。

---

## 方法 1: 角括弧形式（現在の実装、推奨）

### 基本形

```bash
genice3 A15 \
  --shift 0.1 0.1 0.1 \
  --anion 1=Cl \
  --rep 3 3 3 \
  --cation 6=Na \
  --exporter "gromacs[guest:A12=me[monatomic]:guest:A14=et[molecular]:spot_guest:0=propane]"
```

### 階層構造の表現

ネストした角括弧で階層を表現：

- `me[monatomic]` - me プラグインに`monatomic`オプション
- `et[molecular]` - et プラグインに`molecular`オプション

**問題点**:

- ネストした括弧が読みにくい
- どの括弧がどのプラグインに対応するか分かりにくい

---

## 方法 2: 丸括弧形式

```bash
genice3 A15 \
  --shift 0.1 0.1 0.1 \
  --anion 1=Cl \
  --rep 3 3 3 \
  --cation 6=Na \
  --exporter "gromacs(guest:A12=me(monatomic):guest:A14=et(molecular):spot_guest:0=propane)"
```

**問題点**:

- 角括弧と同じく、ネストした括弧が読みにくい
- bash でも引用符が必要

---

## 方法 3: 複数オプション引数方式

```bash
genice3 A15 \
  --shift 0.1 0.1 0.1 \
  --anion 1=Cl \
  --rep 3 3 3 \
  --cation 6=Na \
  --exporter gromacs \
  --exporter-option "guest A12=me" \
  --exporter-option "guest.options monatomic" \
  --exporter-option "guest A14=et" \
  --exporter-option "guest.options molecular" \
  --exporter-option "spot_guest 0=propane"
```

**問題点**:

- 非常に冗長
- 階層関係が分かりにくい
- どのオプションがどの guest に対応するか不明確

---

## 方法 4: 階層的キー名（推奨）

プラグインの階層構造をキー名に反映：

```bash
genice3 A15 \
  --shift 0.1 0.1 0.1 \
  --anion 1=Cl \
  --rep 3 3 3 \
  --cation 6=Na \
  --exporter "gromacs[guest.A12.molecule=me:guest.A12.monatomic:guest.A14.molecule=et:guest.A14.molecular:spot_guest.0=propane]"
```

または、より構造化して：

```bash
genice3 A15 \
  --shift 0.1 0.1 0.1 \
  --anion 1=Cl \
  --rep 3 3 3 \
  --cation 6=Na \
  --exporter "gromacs[guest.A12=me:guest.A12.monatomic:guest.A14=et:guest.A14.molecular:spot_guest.0=propane]"
```

**メリット**:

- 階層構造がキー名から明確
- 簡潔

**デメリット**:

- キー名が長くなる

---

## 方法 5: 複数オプション方式（階層的キー名）

```bash
genice3 A15 \
  --shift 0.1 0.1 0.1 \
  --anion 1=Cl \
  --rep 3 3 3 \
  --cation 6=Na \
  --exporter gromacs \
  --exporter-option "guest.A12.molecule=me" \
  --exporter-option "guest.A12.monatomic" \
  --exporter-option "guest.A14.molecule=et" \
  --exporter-option "guest.A14.molecular" \
  --exporter-option "spot_guest.0=propane"
```

**メリット**:

- 階層構造が明確
- スペースが使える

**デメリット**:

- 冗長

---

## 方法 6: ネストした括弧（改良版）

括弧の種類を変えて階層を明確化：

```bash
genice3 A15 \
  --shift 0.1 0.1 0.1 \
  --anion 1=Cl \
  --rep 3 3 3 \
  --cation 6=Na \
  --exporter "gromacs[guest:A12=me{monatomic}:guest:A14=et{molecular}:spot_guest:0=propane]"
```

- `[]` で gromacs のオプション全体
- `{}` で molecule プラグインのオプション

**メリット**:

- 括弧の種類で階層が分かる

**デメリット**:

- まだ複雑

---

## 方法 7: コンパクトな階層記法（推奨候補）

コロンとドットで階層を表現：

```bash
genice3 A15 \
  --shift 0.1 0.1 0.1 \
  --anion 1=Cl \
  --rep 3 3 3 \
  --cation 6=Na \
  --exporter "gromacs[guest.A12=me:me.monatomic:guest.A14=et:et.molecular:spot_guest.0=propane]"
```

または、より構造化：

```bash
genice3 A15 \
  --shift 0.1 0.1 0.1 \
  --anion 1=Cl \
  --rep 3 3 3 \
  --cation 6=Na \
  --exporter "gromacs[guest.A12.molecule=me:guest.A12.molecule.options=monatomic:guest.A14.molecule=et:guest.A14.molecule.options=molecular:spot_guest.0=propane]"
```

---

## 方法 8: グループ化記法

関連するオプションをグループ化：

```bash
genice3 A15 \
  --shift 0.1 0.1 0.1 \
  --anion 1=Cl \
  --rep 3 3 3 \
  --cation 6=Na \
  --exporter "gromacs[guest(A12=me[monatomic]),guest(A14=et[molecular]),spot_guest(0=propane)]"
```

---

## 推奨案の比較

| 方法             | 簡潔性 | 可読性 | 階層の明確性 | 実装の複雑さ |
| ---------------- | ------ | ------ | ------------ | ------------ |
| 角括弧（ネスト） | 高     | 低     | 低           | 中           |
| 丸括弧（ネスト） | 高     | 低     | 低           | 中           |
| 複数オプション   | 低     | 中     | 中           | 低           |
| 階層的キー名     | 中     | 高     | 高           | 中           |
| コンパクト階層   | 高     | 中     | 中           | 中           |
| グループ化       | 高     | 中     | 高           | 高           |

---

## 最終推奨案

### 案 1: 階層的キー名方式（実装が比較的簡単）

```bash
genice3 A15 \
  --shift 0.1 0.1 0.1 \
  --anion 1=Cl \
  --rep 3 3 3 \
  --cation 6=Na \
  --exporter "gromacs[guest.A12=me:guest.A12.options=monatomic:guest.A14=et:guest.A14.options=molecular:spot_guest.0=propane]"
```

- ドットで階層を表現
- `guest.A12=me` で A12 ケージに me 分子を配置
- `guest.A12.options=monatomic` で me 分子のオプションを指定

### 案 2: シンプルな 2 階層（実用的）

```bash
genice3 A15 \
  --shift 0.1 0.1 0.1 \
  --anion 1=Cl \
  --rep 3 3 3 \
  --cation 6=Na \
  --exporter "gromacs[guest.A12=me[monatomic]:guest.A14=et[molecular]:spot_guest.0=propane]"
```

- ネストした括弧を許容
- よりコンパクト

### 案 3: 複数オプション方式（柔軟性重視）

```bash
genice3 A15 \
  --shift 0.1 0.1 0.1 \
  --anion 1=Cl \
  --rep 3 3 3 \
  --cation 6=Na \
  --exporter gromacs \
  --exporter-option "guest.A12.molecule=me" \
  --exporter-option "guest.A12.molecule.options=monatomic" \
  --exporter-option "guest.A14.molecule=et" \
  --exporter-option "guest.A14.molecule.options=molecular" \
  --exporter-option "spot_guest.0=propane"
```

- 最も冗長だが、最も柔軟

---

## 実装の考慮点

1. **階層の深さ**: exporter → guest → molecule という 3 階層がある
2. **同じキーの繰り返し**: `guest.A12` と `guest.A14` のように、同じキーが複数回
3. **オプションの継承**: molecule プラグインのオプションをどう指定するか
4. **混合ゲスト分子と占有率**: `A12=me*0.3+et*0.6` のように、1 つのケージに複数の分子を異なる占有率で配置する場合
5. **現在の実装との整合性**: 現在は `--guest` や `--spot_guest` がメインオプションだが、exporter プラグイン内で指定する場合の設計

実装が簡単で、かつ階層が明確な方法を選ぶ必要があります。

---

## 実用的な提案

### 現実的なアプローチ: 階層的キー名 + 角括弧形式

現在の実装を踏まえると、以下のような階層的キー名方式が実用的です：

```bash
genice3 A15 \
  --shift 0.1 0.1 0.1 \
  --anion 1=Cl \
  --rep 3 3 3 \
  --cation 6=Na \
  --exporter "gromacs[guest.A12=me:guest.A12.monatomic:guest.A14=et:guest.A14.molecular:spot_guest.0=propane]"
```

**利点**:

- 簡潔で 1 行で書ける
- 階層構造がドットで明確
- 実装が比較的簡単（キーのパースのみ）

**実装方法**:

- `guest.A12=me` → `guest`キーに`A12=me`という値を持つリストまたは辞書
- `guest.A12.monatomic` → `guest.A12`に関連する molecule プラグインのオプション`monatomic=True`
- パーサーが階層的キーを解析して、適切なデータ構造に変換

### 代替案: メインオプションと exporter オプションの分離

現在の実装を維持しつつ、exporter プラグインにオプションを渡す：

#### 例 1: 単純なゲスト指定

```bash
# メインオプションでguestを指定（現在の実装）
genice3 A15 \
  --shift 0.1 0.1 0.1 \
  --anion 1=Cl \
  --rep 3 3 3 \
  --cation 6=Na \
  --guest A12=me \
  --guest A14=et \
  --spot_guest 0=propane \
  --exporter "gromacs[me.monatomic:et.molecular]"
```

#### 例 2: 混合ゲスト分子と占有率

```bash
# 混合ゲスト分子も自然に表現できる
genice3 A15 \
  --shift 0.1 0.1 0.1 \
  --anion 1=Cl \
  --rep 3 3 3 \
  --cation 6=Na \
  --guest A12=me*0.3+et*0.6 \
  --spot_guest 0=propane \
  --exporter "gromacs[me.monatomic:et.molecular]"
```

**利点**:

- 既存の実装を大きく変更しない
- guest の指定と molecule プラグインのオプションが分離されて明確
- 混合ゲスト分子も自然に表現できる（`me*0.3+et*0.6`）

**欠点**:

- molecule プラグインのオプションがどの guest に適用されるかがやや不明確（プラグイン名で推測）

---

## 混合ゲスト分子と占有率を考慮した比較

混合ゲスト分子（`A12=me*0.3+et*0.6`）と各 molecule プラグインのオプションを指定する場合の各手法での表現：

### 方法 1: 階層的キー名方式

```bash
--exporter "gromacs[guest.A12=me*0.3+et*0.6:guest.A12.me.monatomic:guest.A12.et.molecular:spot_guest.0=propane]"
```

- 階層が深くなる（`guest.A12.me.monatomic`）

### 方法 2: ネスト括弧方式（推奨）

```bash
--exporter "gromacs[guest.A12=me*0.3[monatomic]+et*0.6[molecular]:spot_guest.0=propane]"
```

- 最も読みやすい（`me*0.3[monatomic]+et*0.6[molecular]`）
- 混合ゲスト分子と各分子のオプションが明確

### 方法 3: 複数オプション方式

```bash
--exporter gromacs \
  --exporter-option "guest.A12=me*0.3+et*0.6" \
  --exporter-option "guest.A12.me.monatomic" \
  --exporter-option "guest.A12.et.molecular" \
  --exporter-option "spot_guest.0=propane"
```

- 冗長だが明確

### 方法 4: メイン分離方式（実用的）

```bash
--guest A12=me*0.3+et*0.6 \
--spot_guest 0=propane \
--exporter "gromacs[me.monatomic:et.molecular]"
```

- 既存実装を活かし、最も自然

**結論**: 混合ゲスト分子がある場合、ネスト括弧方式（`me*0.3[monatomic]+et*0.6[molecular]`）が最も読みやすく実用的です。
