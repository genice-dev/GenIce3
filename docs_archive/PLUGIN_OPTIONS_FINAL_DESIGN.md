# プラグインオプション最終設計

## 設計原則

1. **プラグインのオプションは、プラグイン自身が処理する**
2. **本体パーサーは最小限の処理のみ**：プラグイン名とオプション文字列を分離し、文字列のままプラグインに渡す
3. **プラグインが責任をもって分割・解釈する**

---

## 構文規則

### 基本構文

```bash
--exporter "gromacs[guest.A12=me*0.3[monatomic]+et*0.6[molecular], spot_guest.0=propane]"
```

または

```bash
--exporter gromacs \
  --exporter-option "guest.A12=me*0.3[monatomic]+et*0.6[molecular]" \
  --exporter-option "spot_guest.0=propane"
```

### 構文要素

1. **`[]`** - プラグインオプション全体を囲む
2. **`.`** - 階層的キー名の区切り（`guest.A12`, `spot_guest.0`）
3. **`=`** - 値の代入
4. **`[]`** - ネストしたプラグイン（molecule など）のオプション
5. **`,`** - 複数オプションの区切り
6. **`()`** - 配列/ベクトルの指定（**丸括弧配列形式**）

### ベクトル・配列の指定（丸括弧形式）

```bash
--exporter "gromacs[shift=(0.1,0.1,0.1), rep=(3,3,3)]"
```

- **丸括弧 `()` を使用**: 角括弧 `[]` は既に別の意味で使用されているため
- 形式: `key=(value1,value2,value3)`

---

## 実装方針

### CLI 側の実装（最小限の処理）

```python
# genice3/cli/genice.py

def parse_exporter_spec(exporter_spec: str) -> Tuple[str, str]:
    """
    exporter指定をパースして、プラグイン名とオプション文字列を返す

    Args:
        exporter_spec: プラグイン名、または "plugin[options]" 形式の文字列

    Returns:
        (plugin_name, option_string)
        - option_string は文字列のまま返す（プラグイン側で解釈）
    """
    # 括弧形式からオプション文字列を抽出
    if "[" in exporter_spec and "]" in exporter_spec:
        left = exporter_spec.find("[")
        right = exporter_spec.rfind("]")  # 最後の ] を取得
        plugin_name = exporter_spec[:left]
        option_string = exporter_spec[left + 1 : right]
        return plugin_name, option_string
    else:
        # プラグイン名のみの場合
        return exporter_spec, ""

@click.option("--exporter", "-e", default="gromacs")
@click.option("--exporter-option", multiple=True)
def main(..., exporter, exporter_option):
    # ...

    # プラグイン名とオプション文字列を取得
    plugin_name, option_string = parse_exporter_spec(exporter)

    # --exporter-option で指定されたオプションを文字列に結合
    if exporter_option:
        if option_string:
            option_string += "," + ",".join(exporter_option)
        else:
            option_string = ",".join(exporter_option)

    # プラグインをロード
    exporter_module = genice3.plugin.safe_import("exporter", plugin_name)

    # プラグインに文字列のまま渡す（プラグインが責任をもって分割・解釈）
    exporter_module.dump(genice, sys.stdout, options=option_string)
```

**重要なポイント**:

- CLI 側では**文字列のまま**プラグインに渡す
- プラグイン側で完全にオプションをパースする責任を持つ
- click のような decorator 方式ではなく、シンプルに文字列を渡す

---

## プラグイン側での実装

### 共通パーサーの使用

基本的なオプションのパースは `genice3.optionparser` の共通関数を使用します。

```python
# genice3/exporters/gromacs.py

from genice3.optionparser import parse_options

def dump(genice: GenIce3, file: TextIOWrapper, options: str = "") -> None:
    """
    Gromacs形式で出力

    Args:
        genice: GenIce3インスタンス
        file: 出力先ファイル
        options: プラグインオプション文字列（例: "guest.A12=me*0.3[monatomic],shift=(0.1,0.1,0.1)"）
    """
    # 共通パーサーで基本的なオプションをパース
    parsed_options = parse_options(options)

    # 基本的なオプションの取得
    shift = parsed_options.get("shift", [0.0, 0.0, 0.0])  # 丸括弧配列形式は自動的にリストに変換
    rep = parsed_options.get("rep", [1, 1, 1])

    # 混合ガスのような複雑な記述は、値として文字列のまま残る
    guest_value = parsed_options.get("guest.A12")  # "me*0.3[monatomic]+et*0.6[molecular]"
    # プラグイン側で解釈
    guest_specs = parse_guest_spec(guest_value)

    # ...
```

### プラグイン側での複雑な記述の解釈例

```python
# genice3/exporters/gromacs.py

def parse_guest_spec(guest_spec: str) -> List[Tuple[str, float, Dict]]:
    """
    ゲスト指定をパース（プラグイン側で解釈）

    例: "me*0.3[monatomic]+et*0.6[molecular]"
    -> [("me", 0.3, {"monatomic": True}), ("et", 0.6, {"molecular": True})]
    """
    result = []

    for part in guest_spec.split("+"):
        # molecule オプションを抽出（[...]）
        import re
        molecule_options = {}
        if "[" in part and "]" in part:
            left = part.find("[")
            right = part.find("]")
            option_str = part[left + 1 : right]
            part = part[:left]
            # オプションをパース
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

## 使用例

### 例 1: 単純なゲスト指定

```bash
genice3 A15 \
  --shift 0.1 0.1 0.1 \
  --anion 1=Cl \
  --rep 3 3 3 \
  --cation 6=Na \
  --exporter "gromacs[guest.A12=me[monatomic], guest.A14=et[molecular], spot_guest.0=propane]"
```

### 例 2: 混合ゲスト分子と占有率

```bash
genice3 A15 \
  --shift 0.1 0.1 0.1 \
  --anion 1=Cl \
  --rep 3 3 3 \
  --cation 6=Na \
  --exporter "gromacs[guest.A12=me*0.3[monatomic]+et*0.6[molecular], spot_guest.0=propane]"
```

### 例 3: ベクトル・配列の指定

```bash
genice3 A15 \
  --shift 0.1 0.1 0.1 \
  --anion 1=Cl \
  --rep 3 3 3 \
  --cation 6=Na \
  --exporter "gromacs[shift=(0.1,0.1,0.1), rep=(3,3,3), guest.A12=me[monatomic]]"
```

### 例 4: 複数オプション引数方式

```bash
genice3 A15 \
  --shift 0.1 0.1 0.1 \
  --anion 1=Cl \
  --rep 3 3 3 \
  --cation 6=Na \
  --exporter gromacs \
  --exporter-option "guest.A12=me*0.3[monatomic]+et*0.6[molecular]" \
  --exporter-option "shift=(0.1,0.1,0.1)" \
  --exporter-option "rep=(3,3,3)"
```

---

## まとめ

### 設計の要点

1. **丸括弧配列形式**: ベクトル・配列には `()` を使用（`[]` は既に別の意味で使用）
2. **文字列のまま渡す**: CLI 側は最小限の処理のみ（プラグイン名とオプション文字列の分離）
3. **プラグイン側で完全パース**: プラグインが責任をもってオプション文字列を分割・解釈
4. **decorator 方式ではない**: シンプルに文字列を渡す方式

### 構文規則のまとめ

- `[]` - プラグインオプション全体を囲む
- `[]` - ネストしたプラグイン（molecule など）のオプション
- `()` - **配列/ベクトルの指定**（丸括弧配列形式）
- `.` - 階層的キー名の区切り
- `=` - 値の代入
- `,` - 複数オプションの区切り（トップレベル）

この設計により、プラグインが柔軟にオプション形式を選択でき、かつ一貫性のある構文が保たれます。
