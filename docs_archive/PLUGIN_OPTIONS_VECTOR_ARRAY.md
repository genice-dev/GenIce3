# プラグインオプションでのベクトル・配列指定方法

## 問題設定

プラグインオプションにベクトル（例: `(1.0, 2.0, 3.0)`）や配列（例: `[1, 2, 3]`）などの列挙型を指定する方法を検討します。

現在の推奨構文：

```
gromacs[guest.A12=me*0.3[monatomic], spot_guest.0=propane]
```

---

## 検討すべき要素

### 既存の構文との整合性

- `[]` は既にプラグインオプション全体とネストしたプラグインのオプションに使用
- `,` は複数オプションの区切りに使用
- 本体のオプションでは `--shift 0.1 0.1 0.1` のようにスペース区切りを使用

### シェルでの扱いやすさ

- スペースを含む場合は引用符が必要
- 特殊文字のエスケープが必要になる可能性

### プラグイン側でのパース

- プラグインが自分でオプションを処理するため、柔軟に対応可能
- ただし、標準的な形式があると便利

---

## 提案方式の比較

### 方式 1: カンマ区切り（シンプル）

```bash
--exporter "gromacs[shift=0.1,0.1,0.1, rep=3,3,3]"
```

**構文**:

- `key=value1,value2,value3` 形式

**メリット**:

- ✅ シンプルで分かりやすい
- ✅ 引用符で囲めば問題なし
- ✅ プラグイン側でのパースが簡単

**デメリット**:

- ⚠️ `,` が既に複数オプションの区切りに使われている（衝突の可能性）
- ⚠️ 値にカンマが含まれる場合は問題

**評価**: ⭐⭐⭐（既存構文との衝突に注意）

---

### 方式 2: スペース区切り（本体オプションと一貫性）

```bash
--exporter "gromacs[shift='0.1 0.1 0.1', rep='3 3 3']"
```

または、引用符の二重エスケープを避けて：

```bash
--exporter "gromacs[shift:0.1 0.1 0.1, rep:3 3 3]"
```

**構文**:

- `key='value1 value2 value3'` 形式（引用符で囲む）
- または `key:value1 value2 value3` 形式（キーと値の区切りを `:` に変更）

**メリット**:

- ✅ 本体オプション（`--shift 0.1 0.1 0.1`）と一貫性がある
- ✅ スペース区切りは直感的

**デメリット**:

- ⚠️ 引用符のネストが必要（`"gromacs[shift='0.1 0.1 0.1']"`）
- ⚠️ シェルでの扱いが複雑

**評価**: ⭐⭐⭐⭐（一貫性が高いが、引用符の扱いが複雑）

---

### 方式 3: 角括弧で配列を表現

```bash
--exporter "gromacs[shift=[0.1,0.1,0.1], rep=[3,3,3]]"
```

**構文**:

- `key=[value1,value2,value3]` 形式

**メリット**:

- ✅ 配列であることが明確
- ✅ JSON ライクな形式で直感的

**デメリット**:

- ❌ `[]` が既にプラグインオプション全体に使われている（衝突）
- ❌ ネストしたプラグインのオプションでも `[]` を使用しているため、さらに複雑に

**評価**: ⭐⭐（既存構文との衝突が大きい）

---

### 方式 4: 丸括弧で配列を表現（推奨）

```bash
--exporter "gromacs[shift=(0.1,0.1,0.1), rep=(3,3,3)]"
```

**構文**:

- `key=(value1,value2,value3)` 形式

**メリット**:

- ✅ 配列であることが明確
- ✅ `()` は現在の構文で未使用（衝突なし）
- ✅ タプル/リストのイメージで直感的
- ✅ プラグイン側でのパースが簡単

**デメリット**:

- ⚠️ シェルでは `()` が特殊文字として扱われる場合がある（引用符で囲めば問題なし）

**評価**: ⭐⭐⭐⭐⭐（最も明確で実用的）

---

### 方式 5: セミコロン区切り（オプション内の配列用）

```bash
--exporter "gromacs[shift=0.1;0.1;0.1, rep=3;3;3]"
```

**構文**:

- `key=value1;value2;value3` 形式

**メリット**:

- ✅ 既存の構文要素と衝突しない
- ✅ 明確に区別できる

**デメリット**:

- ⚠️ Pythonic ではない
- ⚠️ シェルではエスケープが必要な場合がある

**評価**: ⭐⭐⭐（実用的だが、あまり美しくない）

---

### 方式 6: 複数オプション引数方式で個別指定

```bash
--exporter gromacs \
  --exporter-option "shift 0.1 0.1 0.1" \
  --exporter-option "rep 3 3 3"
```

**構文**:

- `--exporter-option "key value1 value2 value3"` 形式（スペース区切り）

**メリット**:

- ✅ 本体オプション（`--shift 0.1 0.1 0.1`）と完全に一貫性がある
- ✅ 引用符で囲むだけで問題なし
- ✅ プラグイン側でのパースが簡単

**デメリット**:

- ⚠️ 冗長（複数のオプションを指定する場合）

**評価**: ⭐⭐⭐⭐（一貫性が高く実用的）

---

## 比較表

| 方式               | 構文例                | 既存構文との衝突 | 一貫性     | 可読性     | 実装の簡単さ | 総合評価       |
| ------------------ | --------------------- | ---------------- | ---------- | ---------- | ------------ | -------------- |
| カンマ区切り       | `shift=0.1,0.1,0.1`   | ⚠️ `,` と衝突    | ⭐⭐       | ⭐⭐⭐     | ⭐⭐⭐⭐     | ⭐⭐⭐         |
| スペース区切り     | `shift='0.1 0.1 0.1'` | なし             | ⭐⭐⭐⭐   | ⭐⭐⭐⭐   | ⭐⭐⭐       | ⭐⭐⭐⭐       |
| 角括弧配列         | `shift=[0.1,0.1,0.1]` | ❌ `[]` と衝突   | ⭐⭐       | ⭐⭐⭐     | ⭐⭐⭐       | ⭐⭐           |
| **丸括弧配列**     | `shift=(0.1,0.1,0.1)` | **なし**         | ⭐⭐⭐     | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐   | **⭐⭐⭐⭐⭐** |
| セミコロン区切り   | `shift=0.1;0.1;0.1`   | なし             | ⭐⭐       | ⭐⭐⭐     | ⭐⭐⭐⭐     | ⭐⭐⭐         |
| 複数オプション引数 | `"shift 0.1 0.1 0.1"` | なし             | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐   | ⭐⭐⭐⭐⭐   | ⭐⭐⭐⭐       |

---

## 推奨案

### 案 1: 丸括弧配列形式（括弧形式内で使用）

```bash
--exporter "gromacs[shift=(0.1,0.1,0.1), rep=(3,3,3), guest.A12=me*0.3[monatomic]]"
```

**構文規則**:

- `key=(value1,value2,value3)` - 配列/ベクトルの指定
- `,` は配列内の要素の区切りと、オプション間の区切りの両方に使用
  - コンテキストで判断可能（`=` の後か、オプション間か）

**パース方法**:

```python
def parse_value(value_str: str):
    """値をパース（配列か単一値か）"""
    # 丸括弧で囲まれている場合は配列
    if value_str.startswith("(") and value_str.endswith(")"):
        content = value_str[1:-1]  # 括弧を除去
        # カンマで分割して数値に変換
        return [float(x.strip()) for x in content.split(",")]
    else:
        # 単一値
        return value_str
```

---

### 案 2: 複数オプション引数方式（推奨・本体オプションと一貫性）

```bash
--exporter gromacs \
  --exporter-option "shift 0.1 0.1 0.1" \
  --exporter-option "rep 3 3 3" \
  --exporter-option "guest.A12=me*0.3[monatomic]"
```

**構文規則**:

- `"key value1 value2 value3"` - スペース区切りで配列/ベクトルを指定
- 本体オプション（`--shift 0.1 0.1 0.1`）と完全に一貫性がある

**パース方法**:

```python
def parse_option(opt_str: str):
    """オプション文字列をパース"""
    parts = opt_str.split()
    if len(parts) == 1:
        # フラグまたは key=value 形式
        if "=" in parts[0]:
            key, value = parts[0].split("=", 1)
            return key, value
        else:
            return parts[0], True
    else:
        # 配列/ベクトル形式: "key value1 value2 value3"
        key = parts[0]
        values = parts[1:]
        # 数値に変換できる場合は変換
        try:
            values = [float(v) if "." in v else int(v) for v in values]
        except ValueError:
            pass  # 変換できない場合は文字列のまま
        return key, values if len(values) > 1 else values[0]
```

---

## 実装例（プラグイン側）

### 丸括弧形式を使用する場合

```python
# genice3/exporters/gromacs.py

def parse_vector_option(value_str: str) -> List[float]:
    """ベクトルオプションをパース"""
    if value_str.startswith("(") and value_str.endswith(")"):
        content = value_str[1:-1]
        return [float(x.strip()) for x in content.split(",")]
    else:
        return [float(value_str)]

def dump(genice: GenIce3, file: TextIOWrapper, **options):
    # shift オプションをパース
    shift_str = options.get("shift", "(0.0,0.0,0.0)")
    shift = parse_vector_option(shift_str)

    # rep オプションをパース
    rep_str = options.get("rep", "(1,1,1)")
    rep = parse_vector_option(rep_str)

    # ...
```

### 複数オプション引数方式を使用する場合

```python
# genice3/exporters/gromacs.py

def dump(genice: GenIce3, file: TextIOWrapper, **options):
    # options は既にパース済みの辞書（CLI側で処理）
    # {"shift": [0.1, 0.1, 0.1], "rep": [3, 3, 3], ...}

    shift = options.get("shift", [0.0, 0.0, 0.0])
    rep = options.get("rep", [1, 1, 1])

    # ...
```

---

## 結論

### 最終決定: 丸括弧配列形式

**丸括弧配列形式を採用**

```bash
--exporter "gromacs[shift=(0.1,0.1,0.1), rep=(3,3,3)]"
```

### 採用理由

1. ✅ **角括弧は既に別の意味がある**: プラグインオプション全体とネストしたプラグインのオプションに使用
2. ✅ **明確性**: `()` で配列/ベクトルであることが明確
3. ✅ **実装が簡単**: プラグイン側でのパースが容易
4. ✅ **一貫性**: 既存の構文と整合性がある

### 実装方針

- **CLI 側**: 最小限の処理のみ（プラグイン名とオプション文字列を分離）
- **プラグイン側**: 文字列のまま受け取り、完全にパースする責任を持つ
- **decorator 方式ではない**: シンプルに文字列を渡す方式
