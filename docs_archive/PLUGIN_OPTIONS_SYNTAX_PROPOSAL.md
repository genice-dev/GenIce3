# プラグインオプション構文の提案と評価

## ユーザー提案構文

```
--exporter "gromacs[guest(A12:0.3*me[monatomic]+0.6*et[molecular]); spot_guest(0:propane)]"
```

### 構文の構造

- `[]` - プラグインオプション全体を囲む
- `()` - 各オプションの引数を囲む
- `:` - キーと値の区切り
- `;` - 複数オプションの区切り
- `[]` - molecule プラグインのオプション（ネスト）

---

## 評価

### メリット

1. **階層構造が明確**: `()` で各オプションの引数が明確
2. **キーと値の区切りが明確**: `:` が直感的
3. **ネストが表現できる**: molecule プラグインのオプションも `[]` で表現

### 問題点

1. **`[]` の二重使用**:

   - プラグインオプション全体: `gromacs[...]`
   - molecule プラグインのオプション: `me[...]`
   - 同じ記号で 2 つの意味を持つため混乱の可能性

2. **セミコロンの問題**:

   - Pythonic ではない（Python では通常`,`や改行）
   - 一部のシェルでは特殊文字として扱われる可能性

3. **複雑なネスト**:

   - `me[monatomic]` が `guest(...)` の中にあり、さらに `gromacs[...]` の中にある
   - 括弧の対応が追いにくい

4. **可読性**:
   - 長い文字列が読みにくい

---

## 代替案の比較

### 案 1: ユーザー提案（セミコロン版）

```
gromacs[guest(A12:0.3*me[monatomic]+0.6*et[molecular]); spot_guest(0:propane)]
```

**評価**: ⭐⭐（やや複雑）

### 案 2: カンマ区切り（Pythonic）

```
gromacs[guest(A12:0.3*me[monatomic]+0.6*et[molecular]), spot_guest(0:propane)]
```

**評価**: ⭐⭐⭐（より Pythonic）

### 案 3: 異なる括弧でネストを明確化

```
gromacs[guest(A12:0.3*me{monatomic}+0.6*et{molecular}), spot_guest(0:propane)]
```

- `[]` - プラグインオプション全体
- `()` - 各オプションの引数
- `{}` - molecule プラグインのオプション

**評価**: ⭐⭐⭐⭐（ネストが明確）

### 案 4: 階層的キー名（既存提案）

```
gromacs[guest.A12=0.3*me+0.6*et, guest.A12.me.monatomic, guest.A12.et.molecular, spot_guest.0=propane]
```

**評価**: ⭐⭐⭐（実装が簡単）

### 案 5: 混合記法（推奨）

```
gromacs[guest(A12:me*0.3{monatomic}+et*0.6{molecular}), spot_guest(0:propane)]
```

- `()` でオプション名と引数を明確化
- `{}` で molecule プラグインのオプション（`[]`との衝突を回避）
- `,` で複数オプションを区切り（Pythonic）

**評価**: ⭐⭐⭐⭐⭐（最も明確で読みやすい）

---

## 詳細な構文比較

### 例: 単純なゲスト指定

| 方式                       | 構文                                                                            | 可読性   | 明確性     |
| -------------------------- | ------------------------------------------------------------------------------- | -------- | ---------- |
| ユーザー提案（セミコロン） | `gromacs[guest(A12:me[monatomic]); guest(A14:et[molecular])]`                   | ⭐⭐     | ⭐⭐⭐     |
| ユーザー提案（カンマ）     | `gromacs[guest(A12:me[monatomic]), guest(A14:et[molecular])]`                   | ⭐⭐⭐   | ⭐⭐⭐     |
| 異なる括弧                 | `gromacs[guest(A12:me{monatomic}), guest(A14:et{molecular})]`                   | ⭐⭐⭐⭐ | ⭐⭐⭐⭐   |
| 階層的キー名               | `gromacs[guest.A12=me, guest.A12.monatomic, guest.A14=et, guest.A14.molecular]` | ⭐⭐⭐   | ⭐⭐⭐     |
| 混合記法                   | `gromacs[guest(A12:me{monatomic}), guest(A14:et{molecular})]`                   | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

### 例: 混合ゲスト分子

| 方式         | 構文                                                                               | 可読性   | 明確性   |
| ------------ | ---------------------------------------------------------------------------------- | -------- | -------- |
| ユーザー提案 | `gromacs[guest(A12:0.3*me[monatomic]+0.6*et[molecular])]`                          | ⭐⭐     | ⭐⭐     |
| 異なる括弧   | `gromacs[guest(A12:me*0.3{monatomic}+et*0.6{molecular})]`                          | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 階層的キー名 | `gromacs[guest.A12=me*0.3+et*0.6, guest.A12.me.monatomic, guest.A12.et.molecular]` | ⭐⭐⭐   | ⭐⭐⭐   |

---

## 推奨案

### 案 A: ユーザー提案の改良版（カンマ + 異なる括弧）

```
gromacs[guest(A12:me*0.3{monatomic}+et*0.6{molecular}), spot_guest(0:propane)]
```

**構文規則**:

- `[]` - プラグインオプション全体
- `()` - 各オプション名とその引数
- `:` - キーと値の区切り（オプション内）
- `{}` - ネストしたプラグイン（molecule など）のオプション
- `,` - 複数オプションの区切り（Pythonic）

**メリット**:

- ✅ 階層が明確（括弧の種類で区別できる）
- ✅ セミコロンではなくカンマ（Pythonic）
- ✅ `[]` の二重使用を回避
- ✅ 読みやすい

### 案 B: シンプル版（括弧を減らす）

```
gromacs[guest.A12=me*0.3{monatomic}+et*0.6{molecular}, spot_guest.0=propane]
```

**構文規則**:

- `[]` - プラグインオプション全体
- `.` - 階層的キー名
- `=` - 値の代入
- `{}` - ネストしたプラグインのオプション
- `,` - 複数オプションの区切り

**メリット**:

- ✅ より簡潔
- ✅ 括弧が少なく読みやすい
- ✅ 実装が簡単

---

## 実装の考慮

### プラグイン側でのパース

プラグインが自分でオプションをパースする場合、以下のような構造を期待：

```python
# プラグインが受け取るオプション辞書
{
    "guest": {
        "A12": {
            "spec": "me*0.3+et*0.6",
            "molecules": {
                "me": {"monatomic": True},
                "et": {"molecular": True}
            }
        }
    },
    "spot_guest": {
        "0": "propane"
    }
}
```

または、よりフラットな形式：

```python
{
    "guest.A12": "me*0.3+et*0.6",
    "guest.A12.me.monatomic": True,
    "guest.A12.et.molecular": True,
    "spot_guest.0": "propane"
}
```

プラグインが自分でパースするため、どの形式でも対応可能です。

---

## ユーザー新提案: 括弧を減らしたシンプル版

```
gromacs[guest.A12=0.3*me[monatomic]+0.6*et[molecular], spot_guest.0=propane]
```

### 構文の構造

- `[]` - プラグインオプション全体
- `.` - 階層的キー名（`guest.A12`, `spot_guest.0`）
- `=` - 値の代入
- `[]` - molecule プラグインのオプション（ネスト）
- `,` - 複数オプションの区切り

### 評価

**メリット**:

1. ✅ **括弧が少ない**: `()` を削除してシンプル
2. ✅ **階層的キー名が明確**: `guest.A12` で構造が分かる
3. ✅ **カンマ区切り**: Pythonic でシェルでの扱いも容易
4. ✅ **シンプルで読みやすい**: 括弧の対応が追いやすい
5. ✅ **`[]` の二重使用は自然**: プラグインがネストしているため、括弧が二重になるのは違和感がない
6. ✅ **実装が簡単**: 階層的キー名をドットで分割するだけ

**考慮点**:

- `[]` が 2 つの意味で使われるが、ネストの文脈で自然（プラグインがネストしているので括弧が二重になるのは違和感がない）

**評価**: ⭐⭐⭐⭐⭐（最もシンプルで実用的）

### 実装例（プラグイン側でのパース）

```python
def parse_gromacs_options(options: Dict[str, str]) -> Dict:
    """プラグイン側でオプションをパース"""
    result = {}

    for key, value in options.items():
        # guest.A12=0.3*me[monatomic]+0.6*et[molecular] を処理
        if key.startswith("guest."):
            # key からケージタイプを取得
            cage_type = key.split("=")[0].replace("guest.", "")
            # value をパース（0.3*me[monatomic]+0.6*et[molecular]）
            result["guests"] = result.get("guests", {})
            result["guests"][cage_type] = parse_guest_spec(value)
        elif key.startswith("spot_guest."):
            cage_index = key.split("=")[0].replace("spot_guest.", "")
            result["spot_guests"] = result.get("spot_guests", {})
            result["spot_guests"][int(cage_index)] = value

    return result

def parse_guest_spec(spec: str) -> List[Tuple[str, float, Dict]]:
    """
    guest 指定をパース
    例: "0.3*me[monatomic]+0.6*et[molecular]"
    -> [("me", 0.3, {"monatomic": True}), ("et", 0.6, {"molecular": True})]
    """
    result = []
    for part in spec.split("+"):
        # molecule オプションを抽出（[...]）
        import re
        molecule_options = {}
        if "[" in part and "]" in part:
            left = part.find("[")
            right = part.find("]")
            option_str = part[left + 1 : right]
            part = part[:left]
            # オプションをパース（例: "monatomic" または "key=value"）
            if "=" in option_str:
                opt_key, opt_val = option_str.split("=", 1)
                molecule_options[opt_key] = opt_val
            else:
                molecule_options[option_str] = True

        # 占有率と分子名を抽出
        if "*" in part:
            occupancy, molecule = part.split("*")
            occupancy = float(occupancy)
        else:
            molecule = part
            occupancy = 1.0

        result.append((molecule, occupancy, molecule_options))

    return result
```

---

## 構文の比較表

### 単純なゲスト指定

| 方式                 | 構文                                                          | 括弧の数 | 可読性   | 実装の簡単さ |
| -------------------- | ------------------------------------------------------------- | -------- | -------- | ------------ |
| ユーザー初提案       | `gromacs[guest(A12:me[monatomic]); guest(A14:et[molecular])]` | 多い     | ⭐⭐     | ⭐⭐         |
| 階層的キー名         | `gromacs[guest.A12=me[monatomic], guest.A14=et[molecular]]`   | 少ない   | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐   |
| 混合記法（`{}`使用） | `gromacs[guest(A12:me{monatomic}), guest(A14:et{molecular})]` | 中       | ⭐⭐⭐⭐ | ⭐⭐⭐⭐     |

### 混合ゲスト分子

| 方式                       | 構文                                                      | 括弧の数 | 可読性     | 実装の簡単さ |
| -------------------------- | --------------------------------------------------------- | -------- | ---------- | ------------ |
| ユーザー初提案             | `gromacs[guest(A12:0.3*me[monatomic]+0.6*et[molecular])]` | 多い     | ⭐⭐       | ⭐⭐         |
| **ユーザー新提案（推奨）** | `gromacs[guest.A12=0.3*me[monatomic]+0.6*et[molecular]]`  | 少ない   | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐   |
| 混合記法（`{}`使用）       | `gromacs[guest(A12:me*0.3{monatomic}+et*0.6{molecular})]` | 中       | ⭐⭐⭐⭐   | ⭐⭐⭐⭐     |

---

## 結論

### 最終推奨構文（ユーザー新提案）

```
gromacs[guest.A12=0.3*me[monatomic]+0.6*et[molecular], spot_guest.0=propane]
```

または、占有率の順序を変更して（より読みやすいかも）：

```
gromacs[guest.A12=me*0.3[monatomic]+et*0.6[molecular], spot_guest.0=propane]
```

### 構文規則

1. **`[]`** - プラグインオプション全体を囲む
2. **`.`** - 階層的キー名の区切り（`guest.A12`, `spot_guest.0`）
3. **`=`** - 値の代入
4. **`[]`** - ネストしたプラグイン（molecule など）のオプション（プラグインがネストしているので自然）
5. **`,`** - 複数オプションの区切り（Pythonic）

### 特徴

- ✅ **シンプル**: 括弧を最小限に（`()` を使わない）
- ✅ **明確**: 階層的キー名で構造が分かる
- ✅ **自然**: プラグインのネストに対応する `[]` の二重使用は違和感がない
- ✅ **実装容易**: プラグイン側でのパースが簡単（階層的キー名をドットで分割）
- ✅ **Pythonic**: カンマ区切りで複数オプションを指定

この構文なら、プラグイン側で柔軟にパースでき、かつ可読性も高く、実装も簡単です。
