# プラグインオプション指定方法の比較

## 指定したい内容

### 例 1: 単純なゲスト指定

```
genice3 A15
  --shift 0.1 0.1 0.1
  --anion 1=Cl
  --rep 3 3 3
  --cation 6=Na
  --exporter gromacs
    - guest A12=me (meのオプション: monatomic)
    - guest A14=et (etのオプション: molecular)
    - spot_guest 0=propane
```

### 例 2: 混合ゲスト分子と占有率の指定

```
genice3 A15
  --shift 0.1 0.1 0.1
  --anion 1=Cl
  --rep 3 3 3
  --cation 6=Na
  --exporter gromacs
    - guest A12=me*0.3+et*0.6
      - meのオプション: monatomic
      - etのオプション: molecular
    - spot_guest 0=propane
```

**注意**: `me*0.3+et*0.6` は、A12 ケージに me を 30%、et を 60%の占有率で配置することを意味します。

---

## 各手法での表現

### 方法 1: 角括弧形式（簡潔・推奨）

#### 例 1: 単純なゲスト指定

```bash
genice3 A15 \
  --shift 0.1 0.1 0.1 \
  --anion 1=Cl \
  --rep 3 3 3 \
  --cation 6=Na \
  --exporter "gromacs[guest.A12=me:guest.A12.monatomic:guest.A14=et:guest.A14.molecular:spot_guest.0=propane]"
```

#### 例 2: 混合ゲスト分子と占有率

```bash
genice3 A15 \
  --shift 0.1 0.1 0.1 \
  --anion 1=Cl \
  --rep 3 3 3 \
  --cation 6=Na \
  --exporter "gromacs[guest.A12=me*0.3+et*0.6:guest.A12.me.monatomic:guest.A12.et.molecular:spot_guest.0=propane]"
```

**特徴**:

- ✅ 1 行で簡潔
- ✅ 階層がドットで明確（`guest.A12.me.monatomic`）
- ⚠️ 引用符が必要
- ⚠️ キー名が長くなる
- ⚠️ 混合ゲストの場合、階層がさらに深くなる（`guest.A12.me.monatomic`）

---

### 方法 2: ネストした角括弧形式

#### 例 1: 単純なゲスト指定

```bash
genice3 A15 \
  --shift 0.1 0.1 0.1 \
  --anion 1=Cl \
  --rep 3 3 3 \
  --cation 6=Na \
  --exporter "gromacs[guest.A12=me[monatomic]:guest.A14=et[molecular]:spot_guest.0=propane]"
```

#### 例 2: 混合ゲスト分子と占有率

```bash
genice3 A15 \
  --shift 0.1 0.1 0.1 \
  --anion 1=Cl \
  --rep 3 3 3 \
  --cation 6=Na \
  --exporter "gromacs[guest.A12=me*0.3[monatomic]+et*0.6[molecular]:spot_guest.0=propane]"
```

**特徴**:

- ✅ よりコンパクト
- ✅ 混合ゲストでも比較的読みやすい（`me*0.3[monatomic]+et*0.6[molecular]`）
- ⚠️ ネストした括弧で読みにくい場合がある
- ⚠️ 実装が複雑（括弧のマッチングが必要）

---

### 方法 3: 複数オプション引数方式

#### 例 1: 単純なゲスト指定

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

#### 例 2: 混合ゲスト分子と占有率

```bash
genice3 A15 \
  --shift 0.1 0.1 0.1 \
  --anion 1=Cl \
  --rep 3 3 3 \
  --cation 6=Na \
  --exporter gromacs \
  --exporter-option "guest.A12=me*0.3+et*0.6" \
  --exporter-option "guest.A12.me.monatomic" \
  --exporter-option "guest.A12.et.molecular" \
  --exporter-option "spot_guest.0=propane"
```

**特徴**:

- ✅ 引用符不要（値にスペースがない場合）
- ✅ スペースが使える
- ✅ 混合ゲストの指定も比較的明確
- ❌ **非常に冗長**（ユーザー指摘）
- ❌ オプションが多いと 1 行が長くなる

---

### 方法 4: 混合方式（基本 + 追加オプション）

```bash
genice3 A15 \
  --shift 0.1 0.1 0.1 \
  --anion 1=Cl \
  --rep 3 3 3 \
  --cation 6=Na \
  --exporter "gromacs[guest.A12=me:guest.A14=et:spot_guest.0=propane]" \
  --exporter-option "guest.A12.monatomic" \
  --exporter-option "guest.A14.molecular"
```

**特徴**:

- ✅ 基本は括弧形式で簡潔
- ✅ 追加オプションは個別指定で柔軟
- ⚠️ 2 つの方式を混在させる必要がある

---

### 方法 5: 現在の実装を活かす（推奨候補）

メインオプションと exporter オプションを分離：

#### 例 1: 単純なゲスト指定

```bash
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
genice3 A15 \
  --shift 0.1 0.1 0.1 \
  --anion 1=Cl \
  --rep 3 3 3 \
  --cation 6=Na \
  --guest A12=me*0.3+et*0.6 \
  --spot_guest 0=propane \
  --exporter "gromacs[me.monatomic:et.molecular]"
```

**特徴**:

- ✅ 既存の実装を大きく変更しない
- ✅ guest の指定と molecule オプションが分離されて明確
- ✅ 比較的簡潔
- ✅ 混合ゲストでも自然（`--guest A12=me*0.3+et*0.6`）
- ⚠️ molecule プラグインのオプションがどの guest に適用されるかがやや不明確（プラグイン名で推測）

---

## 比較表

| 方法                 | 行数  | 簡潔性 | 可読性 | 階層の明確性 | 実装の複雑さ | 総合評価 |
| -------------------- | ----- | ------ | ------ | ------------ | ------------ | -------- |
| 角括弧（階層的キー） | 6 行  | ⭐⭐⭐ | ⭐⭐   | ⭐⭐⭐       | ⭐⭐         | ⭐⭐⭐   |
| ネスト括弧           | 6 行  | ⭐⭐⭐ | ⭐     | ⭐⭐         | ⭐           | ⭐⭐     |
| 複数オプション       | 11 行 | ⭐     | ⭐⭐   | ⭐⭐⭐       | ⭐⭐⭐       | ⭐       |
| 混合方式             | 8 行  | ⭐⭐   | ⭐⭐   | ⭐⭐⭐       | ⭐⭐         | ⭐⭐     |
| メイン分離方式       | 9 行  | ⭐⭐   | ⭐⭐⭐ | ⭐⭐         | ⭐⭐⭐       | ⭐⭐⭐   |

---

## 最終推奨

### 1 位: 角括弧形式（階層的キー名） - 新規実装向け

```bash
--exporter "gromacs[guest.A12=me:guest.A12.monatomic:guest.A14=et:guest.A14.molecular:spot_guest.0=propane]"
```

**理由**:

- 簡潔で 1 行で書ける
- 階層構造が明確
- 実装が比較的簡単

### 2 位: 現在の実装を活かす方式 - 既存コードとの整合性重視

```bash
--guest A12=me \
--guest A14=et \
--spot_guest 0=propane \
--exporter "gromacs[me.monatomic:et.molecular]"
```

**理由**:

- 既存の実装を大きく変更しない
- 明確な分離

### 3 位: 複数オプション方式 - 特殊な場合のみ

```bash
--exporter gromacs \
--exporter-option "guest.A12.molecule=me" \
--exporter-option "guest.A12.monatomic"
```

**理由**:

- 冗長だが、スペースを含む値など特殊な場合に有用

---

---

## 混合ゲスト分子と占有率を考慮した比較

混合ゲスト分子（`me*0.3+et*0.6`）と各 molecule プラグインのオプションを指定する場合：

| 方法           | 表現                                                                            | 可読性 | 簡潔性 | 実装の複雑さ |
| -------------- | ------------------------------------------------------------------------------- | ------ | ------ | ------------ |
| 階層的キー名   | `guest.A12=me*0.3+et*0.6:guest.A12.me.monatomic:guest.A12.et.molecular`         | ⭐⭐   | ⭐⭐   | ⭐⭐         |
| ネスト括弧     | `guest.A12=me*0.3[monatomic]+et*0.6[molecular]`                                 | ⭐⭐⭐ | ⭐⭐⭐ | ⭐           |
| 複数オプション | `guest.A12=me*0.3+et*0.6` + `guest.A12.me.monatomic` + `guest.A12.et.molecular` | ⭐⭐   | ⭐     | ⭐⭐⭐       |
| メイン分離方式 | `--guest A12=me*0.3+et*0.6` + `--exporter "gromacs[me.monatomic:et.molecular]"` | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐       |

**混合ゲストの場合の推奨**:

- **ネスト括弧方式**: `me*0.3[monatomic]+et*0.6[molecular]` が最も読みやすく、簡潔
- **メイン分離方式**: 既存の実装を活かし、自然な表現

---

## 結論

**ユーザーの指摘通り、複数オプション方式は冗長すぎるため、括弧形式を基本とすべきです。**

階層的なプラグインオプション指定には、以下の方式が推奨されます：

1. **混合ゲストがある場合**: ネスト括弧方式が読みやすい

   - `guest.A12=me*0.3[monatomic]+et*0.6[molecular]`

2. **単純なゲスト指定の場合**: 階層的キー名方式が明確

   - `guest.A12=me:guest.A12.monatomic`

3. **既存実装を活かす場合**: メインオプションと exporter オプションの分離
   - `--guest A12=me*0.3+et*0.6` + `--exporter "gromacs[me.monatomic:et.molecular]"`
