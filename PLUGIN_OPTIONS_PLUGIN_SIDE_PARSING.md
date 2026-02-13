# プラグイン側でのオプション処理設計

## 設計原則

**プラグインのオプションは、プラグイン自身が処理する**

この設計により、各プラグインが独自のオプション形式を自由に選択でき、柔軟性が大幅に向上します。

---

## 基本的な設計

### 1. オプション文字列の渡し方

コマンドラインからプラグインにオプションを渡す方法は、以下のいずれか（または両方）をサポート：

#### 方法 A: 括弧形式（簡潔）

```bash
--exporter "gromacs[guest.A12=me:water_model=tip4p]"
```

#### 方法 B: 複数オプション引数（柔軟）

```bash
--exporter gromacs \
  --exporter-option "guest.A12=me" \
  --exporter-option "water_model=tip4p"
```

### 2. プラグイン側での処理

プラグインは、**生のオプション文字列のリスト**を受け取り、自分でパースします。

```python
# genice3/exporters/gromacs.py

def dump(genice: GenIce3, file: TextIOWrapper, **options):
    """
    Gromacs形式で出力

    Args:
        genice: GenIce3インスタンス
        file: 出力先ファイル
        **options: プラグインオプション（文字列形式）
            - 例: {"guest.A12": "me", "water_model": "tip4p"}
            または
            - 例: {"guest.A12": "me*0.3+et*0.6", "guest.A12.me": "monatomic"}
    """
    # プラグインが自分でオプションをパース
    guest_specs = parse_guest_options(options)
    water_model = parse_water_model(options)

    structure = genice.get_atomic_structure(
        water_model=water_model,
        guests=guest_specs,
    )

    output = to_gro(...)
    file.write(output)
```

---

## 実装の詳細

### コマンドライン引数の処理

#### CLI 側の実装

```python
# genice3/cli/genice.py

@click.option("--exporter", "-e", default="gromacs")
@click.option("--exporter-option", multiple=True)
def main(..., exporter, exporter_option):
    # プラグイン名とオプションを分離
    plugin_name, option_strings = parse_exporter_spec(exporter, exporter_option)

    # プラグインをロード
    exporter_module = safe_import("exporter", plugin_name)

    # プラグインに渡す前に、オプション文字列を辞書に変換（基本的なパースのみ）
    # ただし、プラグインが独自にパースできるように、文字列のまま渡すことも可能
    options = basic_parse_options(option_strings)  # または option_strings をそのまま渡す

    # プラグインを呼び出す
    exporter_module.dump(genice, sys.stdout, **options)
```

#### 基本的なオプションパース（共通処理）

```python
# genice3/plugin.py

def basic_parse_options(option_strings: List[str]) -> Dict[str, str]:
    """
    基本的なオプション文字列のパース（共通処理）

    プラグインが独自のパースを必要とする場合でも、
    この基本パースで辞書形式にしてから渡すことが可能。

    しかし、プラグインが完全に独自の形式を望む場合は、
    生の文字列リストを渡すことも選択肢。
    """
    options = {}

    for opt_str in option_strings:
        if "=" in opt_str:
            key, value = opt_str.split("=", 1)
            options[key] = value
        else:
            options[opt_str] = True

    return options
```

### プラグイン側での処理例

#### 例 1: 単純なオプション

```python
# genice3/exporters/gromacs.py

def dump(genice: GenIce3, file: TextIOWrapper, **options):
    # オプションから水分子モデルを取得
    water_model_name = options.get("water_model", "foursite")
    water_model = get_molecule(water_model_name)

    structure = genice.get_atomic_structure(water_model=water_model)
    # ...
```

#### 例 2: 階層的なオプション（プラグインが独自にパース）

```python
# genice3/exporters/gromacs.py

def dump(genice: GenIce3, file: TextIOWrapper, **options):
    # プラグインが自分で階層的なオプションをパース
    guest_specs = {}

    # guest.A12=me のような形式を処理
    for key, value in options.items():
        if key.startswith("guest."):
            cage_type = key.replace("guest.", "")
            guest_specs[cage_type] = parse_guest_value(value)

        # guest.A12.me.monatomic のような molecule オプションも処理
        if key.startswith("guest.") and "." in key.replace("guest.", "", 1):
            # 階層構造をパース
            parts = key.split(".")
            if len(parts) >= 3:
                cage_type = parts[1]
                molecule_name = parts[2]
                option_key = ".".join(parts[3:]) if len(parts) > 3 else None

                # molecule オプションを保存
                if option_key:
                    # molecule オプションを処理
                    pass

    structure = genice.get_atomic_structure(guests=guest_specs)
    # ...
```

#### 例 3: 複雑な形式を独自にパース

```python
# genice3/exporters/gromacs.py

def parse_gromacs_options(options: Dict[str, str]) -> Dict:
    """
    gromacs exporter のオプションを独自にパース

    サポートする形式:
    - guest.A12=me*0.3+et*0.6
    - guest.A12.me.monatomic
    - guest.A12.et.molecular
    """
    result = {
        "guests": {},
        "water_model": options.get("water_model", "foursite"),
    }

    # guest オプションをパース
    for key, value in options.items():
        if key.startswith("guest."):
            # guest.A12=me*0.3+et*0.6 をパース
            parts = key.split(".")
            if len(parts) == 2 and "=" not in key:
                # key が "guest.A12" で value が "me*0.3+et*0.6" の場合
                cage_type = parts[1]
                result["guests"][cage_type] = parse_guest_spec(value)
            elif len(parts) > 2:
                # guest.A12.me.monatomic のような molecule オプション
                cage_type = parts[1]
                molecule_name = parts[2]
                option_name = ".".join(parts[3:])

                if cage_type not in result["guests"]:
                    result["guests"][cage_type] = {}
                if molecule_name not in result["guests"][cage_type]:
                    result["guests"][cage_type][molecule_name] = {}

                result["guests"][cage_type][molecule_name][option_name] = value

    return result

def parse_guest_spec(spec: str) -> List[Tuple[str, float, Dict]]:
    """
    guest 指定をパース
    例: "me*0.3+et*0.6" -> [("me", 0.3, {}), ("et", 0.6, {})]
    """
    result = []
    for part in spec.split("+"):
        if "*" in part:
            molecule, occupancy = part.split("*")
            occupancy = float(occupancy)
        else:
            molecule = part
            occupancy = 1.0
        result.append((molecule, occupancy, {}))
    return result

def dump(genice: GenIce3, file: TextIOWrapper, **options):
    parsed_options = parse_gromacs_options(options)

    # パースしたオプションを使用
    water_model = get_molecule(parsed_options["water_model"])
    guests = convert_guest_specs(parsed_options["guests"])

    structure = genice.get_atomic_structure(
        water_model=water_model,
        guests=guests,
    )
    # ...
```

---

## メリット

### 1. 柔軟性

各プラグインが独自のオプション形式を選択できる：

- 単純な `key=value` 形式
- 階層的な `key.subkey=value` 形式
- 複雑な `key=value1*0.3+value2*0.6` 形式
- JSON 形式
- その他の任意の形式

### 2. プラグインの独立性

- プラグインが独自にオプション形式を変更できる
- 他のプラグインに影響を与えない
- プラグイン固有の複雑な要件に対応可能

### 3. 実装の簡素化

- 共通パーサーの複雑な制約がない
- プラグインが必要な部分だけを実装できる

---

## オプション文字列の形式

プラグインに渡されるオプションは、基本的に文字列の辞書形式です。

### 括弧形式から変換

```bash
--exporter "gromacs[guest.A12=me:water_model=tip4p]"
```

↓ 変換

```python
{
    "guest.A12": "me",
    "water_model": "tip4p",
}
```

### 複数オプション引数から変換

```bash
--exporter gromacs \
  --exporter-option "guest.A12=me" \
  --exporter-option "water_model=tip4p"
```

↓ 変換

```python
{
    "guest.A12": "me",
    "water_model": "tip4p",
}
```

### 混合ゲスト分子の例

```bash
--exporter "gromacs[guest.A12=me*0.3+et*0.6:guest.A12.me.monatomic:guest.A12.et.molecular]"
```

↓ 変換

```python
{
    "guest.A12": "me*0.3+et*0.6",
    "guest.A12.me.monatomic": True,  # または値
    "guest.A12.et.molecular": True,  # または値
}
```

プラグインは、これらの文字列を受け取り、自分で解釈します。

---

## プラグイン開発者向けガイドライン

### 推奨事項

1. **オプションパースの実装**: プラグインは、自分が受け取るオプション形式を明確にドキュメント化する

2. **エラーハンドリング**: 無効なオプションが渡された場合、明確なエラーメッセージを表示する

3. **デフォルト値**: オプションが指定されない場合のデフォルト動作を明確にする

4. **ヘルプ機能**: `?` オプションで使用法を表示する機能を実装することを推奨

### 実装例（ヘルパー関数）

```python
# genice3/exporters/gromacs.py

def parse_gromacs_options(options: Dict[str, str]) -> Dict:
    """gromacs exporter のオプションをパース"""
    # 実装
    pass

def show_usage():
    """使用法を表示"""
    print("""
Gromacs Exporter Options:
  water_model: Water model name (default: foursite)
  guest.CAGE_TYPE: Guest molecule specification
    Example: guest.A12=me*0.3+et*0.6
  guest.CAGE_TYPE.MOLECULE.OPTION: Molecule-specific option
    Example: guest.A12.me.monatomic
    """)

def dump(genice: GenIce3, file: TextIOWrapper, **options):
    if "?" in options:
        show_usage()
        return

    parsed = parse_gromacs_options(options)
    # ...
```

---

## CLI 側の実装（現在の実装との比較）

### 現在の実装

```python
# genice3/cli/genice.py (現在)
exporter = genice3.plugin.safe_import("exporter", exporter)
print(exporter.dump(genice, sys.stdout))
```

### 新しい実装（プラグイン側でオプション処理）

```python
# genice3/cli/genice.py (新設計)

def parse_exporter_spec(exporter_spec: str, exporter_options: Tuple[str, ...]) -> Tuple[str, Dict[str, str]]:
    """
    exporter指定をパースして、プラグイン名とオプション辞書を返す

    Args:
        exporter_spec: プラグイン名、または "plugin[key=value]" 形式
        exporter_options: --exporter-option で指定された追加オプション

    Returns:
        (plugin_name, options_dict)
    """
    # 括弧形式からオプションを抽出
    if "[" in exporter_spec and "]" in exporter_spec:
        left = exporter_spec.find("[")
        right = exporter_spec.find("]")
        plugin_name = exporter_spec[:left]
        option_string = exporter_spec[left + 1 : right]

        # オプション文字列をパース
        options = {}
        for elem in option_string.split(":"):
            if "=" in elem:
                k, v = elem.split("=", 1)
                options[k] = v
            else:
                options[elem] = True
    else:
        plugin_name = exporter_spec
        options = {}

    # --exporter-option で指定されたオプションを追加
    for opt in exporter_options:
        if "=" in opt:
            k, v = opt.split("=", 1)
            options[k] = v
        else:
            options[opt] = True

    return plugin_name, options

@click.option("--exporter", "-e", default="gromacs")
@click.option("--exporter-option", multiple=True)
def main(..., exporter, exporter_option):
    # ...

    # プラグイン名とオプションを取得
    plugin_name, exporter_options = parse_exporter_spec(exporter, exporter_option)

    # プラグインをロード
    exporter_module = genice3.plugin.safe_import("exporter", plugin_name)

    # プラグインにオプションを渡す（プラグインが自分でパース）
    exporter_module.dump(genice, sys.stdout, **exporter_options)
```

---

## まとめ

### 設計原則

- **プラグインのオプションは、プラグイン自身が処理する**
- CLI 側は、基本的な文字列 → 辞書変換のみを行う
- 各プラグインが独自のオプション形式を選択できる

### メリット

1. **柔軟性**: 各プラグインが最適な形式を選択できる
2. **独立性**: プラグイン間で影響しない
3. **拡張性**: 新しい形式を簡単に追加できる
4. **簡素化**: 共通パーサーの複雑な制約がない

### 実装の流れ

1. CLI 側: コマンドライン引数を基本的な辞書形式に変換
2. プラグイン側: 受け取ったオプション辞書を自分で解釈・処理
3. プラグイン側: 必要に応じて、GenIce3 からデータを取得
