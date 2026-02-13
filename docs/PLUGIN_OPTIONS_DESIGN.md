# プラグインオプション指定の一般的な手法

## 現在の実装の問題点

現在は `plugin[key=value:key2=value2]` という形式を使用していますが、以下の問題があります：

- スペースを入れられない（シェルの引数分割のため）
- 引用符で囲む必要がある
- 角括弧 `[]` は一部のシェルで glob パターンとして解釈され、エスケープが必要になる場合がある
- 可読性が低い

## 角括弧 vs 丸括弧

### 角括弧 `[]` の問題点

```bash
# 一部のシェル（zshなど）ではglobパターンとして解釈される可能性
plugin[key=value]  # エラーになる可能性
plugin\[key=value\]  # エスケープが必要
"plugin[key=value]"  # 引用符が必要
```

### 丸括弧 `()` の利点

```bash
# より自然で、エスケープの問題が少ない
plugin(key=value:key2=value2)  # より自然（関数呼び出しのような記法）
"plugin(key=value:key2=value2)"  # 引用符で囲めば問題なし
```

**メリット**:

- **作用範囲を明確に指定できる**: 角括弧と同様に、オプション全体を括弧で囲める
- **関数呼び出しのような自然な記法**: `plugin(options)` という形で直感的
- **エスケープの問題が少ない**: 角括弧ほど glob パターンとして解釈されにくい
- **可読性が高い**: より自然な記法

**注意点**:

- 引用符で囲む必要がある場合がある（スペースを含む場合など）
- シェルではサブシェルの実行に使われるが、引用符内では問題なし

## 一般的な手法の比較

### 1. **複数のオプション引数方式**（推奨）

```
--exporter gromacs --exporter-option key=value --exporter-option key2=value2
```

**メリット**:

- スペースが使える
- 各オプションが独立して指定できる
- 可読性が高い
- シェルでの展開や補完が簡単

**デメリット**:

- オプション名が少し長くなる
- 複数のオプションを指定する場合、少し冗長

**実装例**:

```python
@click.option("--exporter", "-e", default="gromacs")
@click.option("--exporter-option", multiple=True)
def main(exporter, exporter_option):
    options = {}
    for opt in exporter_option:
        if "=" in opt:
            k, v = opt.split("=", 1)
            options[k] = v
        else:
            options[opt] = True
```

---

### 2. **クエリ文字列形式**（URL スタイル）

```
--exporter "gromacs?key=value&key2=value2"
```

**メリット**:

- コンパクト
- URL のクエリパラメータとして一般的
- 既存の`[]`形式と似ている

**デメリット**:

- スペースを含む値は引用符が必要
- `&`文字が特殊文字として扱われる場合がある

**実装例**:

```python
from urllib.parse import parse_qs, urlparse

def plugin_option_parser(s):
    if "?" in s:
        plugin_name, query_string = s.split("?", 1)
        params = parse_qs(query_string)
        options = {k: v[0] if len(v) == 1 else v for k, v in params.items()}
        return plugin_name, options
    return s, {}
```

---

### 3. **コロン区切り方式**

```
--exporter "gromacs:key=value:key2=value2"
```

**メリット**:

- 現在の形式と似ている（`[]`を`:`に変更）
- シンプル
- 読みやすい

**デメリット**:

- スペースを含む値は引用符が必要
- 値の中に`:`が含まれる場合に問題（エスケープ必要）

**実装例**:

```python
def plugin_option_parser(s):
    if ":" in s:
        parts = s.split(":", 1)
        plugin_name = parts[0]
        options_str = parts[1]
        options = {}
        for opt in options_str.split(":"):
            if "=" in opt:
                k, v = opt.split("=", 1)
                options[k] = v
            else:
                options[opt] = True
        return plugin_name, options
    return s, {}
```

---

### 4. **ドット記法（階層的オプション）**

```
--exporter gromacs --exporter.key=value --exporter.key2=value2
```

**メリット**:

- オプションがプラグインに属していることが明確
- 他のオプションと統一的

**デメリット**:

- 複数のプラグインオプションがある場合、冗長
- `key`にドットが含まれる場合に問題

---

### 5. **JSON 形式**

```
--exporter gromacs --exporter-options '{"key": "value", "key2": "value2"}'
```

**メリット**:

- 複雑なネストしたオプションに対応可能
- 型情報を含められる

**デメリット**:

- コマンドラインでは書きづらい
- エスケープが必要
- 一般ユーザーには難しすぎる

---

## 推奨: 複数のオプション引数方式 + 後方互換性

最も実用的なのは、**複数のオプション引数方式**を採用しつつ、既存の`[]`形式も後方互換性のためにサポートすることです。

### 実装例

```python
def plugin_option_parser(name_or_spec, option_list=None):
    """
    プラグイン名とオプションを解析する。

    Args:
        name_or_spec: プラグイン名、または `plugin[key=value]` 形式の文字列
        option_list: 追加のオプションリスト（`--exporter-option` など）

    Returns:
        (plugin_name, options_dict)
    """
    options = {}

    # 既存の [] 形式をサポート（後方互換性）
    if "[" in name_or_spec and "]" in name_or_spec:
        left = name_or_spec.find("[")
        right = name_or_spec.find("]")
        if 0 < left < len(name_or_spec) and 0 < right < len(name_or_spec) and left < right:
            args = name_or_spec[left + 1 : right]
            plugin_name = name_or_spec[:left]
            for elem in args.split(":"):
                if "=" in elem:
                    k, v = elem.split("=", 1)
                    options[k] = v
                else:
                    options[elem] = True
            # オプションリストもマージ
            if option_list:
                for opt in option_list:
                    if "=" in opt:
                        k, v = opt.split("=", 1)
                        options[k] = v
                    else:
                        options[opt] = True
            return plugin_name, options

    # 新しい形式: オプションリストを使用
    plugin_name = name_or_spec
    if option_list:
        for opt in option_list:
            if "=" in opt:
                k, v = opt.split("=", 1)
                options[k] = v
            else:
                options[opt] = True

    return plugin_name, options
```

### 使用例

```python
@click.option("--exporter", "-e", default="gromacs", help="Output format exporter")
@click.option(
    "--exporter-option",
    multiple=True,
    help="Exporter-specific options in key=value format. Can be specified multiple times."
)
def main(exporter, exporter_option):
    plugin_name, options = plugin_option_parser(exporter, exporter_option)
    # ...
```

### コマンドライン使用例

```bash
# 新しい形式（推奨）: スペースが使える
genice3 --exporter gromacs --exporter-option key=value --exporter-option key2=value2

# 既存形式（後方互換性）: 1つの文字列
genice3 --exporter "gromacs[key=value:key2=value2]"

# 混合（オプションリストが優先）
genice3 --exporter gromacs --exporter-option key3=value3
```

---

## 他のツールでの実例

### Docker

```bash
docker run --env KEY=value --env KEY2=value2 image
```

### Kubernetes

```bash
kubectl run pod --env KEY=value --env KEY2=value2
```

### Terraform

```bash
terraform apply -var "key=value" -var "key2=value2"
```

### Git

```bash
git config --global key value
git config --global key2 value2
```

これらはすべて、**複数のオプション引数を繰り返し指定する方式**を採用しています。

---

## 複数の値を指定する場合の手法

1 つのオプションキーに対して複数の値を指定する場合、以下の手法が考えられます。

### 方法 1: 同じキーを複数回指定（推奨）

```bash
--exporter-option key=value1 --exporter-option key=value2 --exporter-option key=value3
```

**メリット**:

- 最も明確
- 各値が独立して指定できる
- スペースを含む値も扱える
- 既存の`multiple=True`パターンと一貫性がある

**実装例**:

```python
def plugin_option_parser(name_or_spec, option_list=None):
    options = {}

    if option_list:
        for opt in option_list:
            if "=" in opt:
                k, v = opt.split("=", 1)
                # 同じキーが複数回指定された場合はリストにまとめる
                if k in options:
                    if not isinstance(options[k], list):
                        options[k] = [options[k]]
                    options[k].append(v)
                else:
                    options[k] = v
            else:
                options[opt] = True

    return name_or_spec, options
```

**結果**: `{"key": ["value1", "value2", "value3"]}`

---

### 方法 2: カンマ区切りリスト

```bash
--exporter-option key=value1,value2,value3
```

**メリット**:

- コンパクト
- 1 つの文字列で指定できる

**デメリット**:

- 値にカンマが含まれる場合に問題
- スペースを含む値は引用符が必要

**実装例**:

```python
def plugin_option_parser(name_or_spec, option_list=None):
    options = {}

    if option_list:
        for opt in option_list:
            if "=" in opt:
                k, v = opt.split("=", 1)
                # カンマ区切りをリストに変換
                if "," in v:
                    options[k] = [x.strip() for x in v.split(",")]
                else:
                    options[k] = v
            else:
                options[opt] = True

    return name_or_spec, options
```

**結果**: `{"key": ["value1", "value2", "value3"]}`

---

### 方法 3: コロン区切り（既存形式との統合）

```bash
# []形式で
--exporter "gromacs[key=value1:value2:value3]"

# 新しい形式で
--exporter-option key=value1:value2:value3
```

**メリット**:

- 既存の`:`区切りと一貫性がある
- コンパクト

**デメリット**:

- 値にコロンが含まれる場合に問題
- スペースを含む値は引用符が必要

---

### 方法 4: 複合形式（推奨の組み合わせ）

**推奨**: 方法 1（同じキーを複数回指定）を基本とし、カンマ区切りもオプションでサポート。

```python
def plugin_option_parser(name_or_spec, option_list=None):
    """
    プラグイン名とオプションを解析する。
    複数の値の指定方法:
    1. 同じキーを複数回指定（推奨）: key=value1 key=value2
    2. カンマ区切り: key=value1,value2,value3
    """
    options = {}

    if option_list:
        for opt in option_list:
            if "=" in opt:
                k, v = opt.split("=", 1)

                # カンマ区切りの値をリストに変換
                if "," in v:
                    values = [x.strip() for x in v.split(",")]
                else:
                    values = v

                # 同じキーが既に存在する場合
                if k in options:
                    existing = options[k]
                    if not isinstance(existing, list):
                        existing = [existing]

                    if isinstance(values, list):
                        existing.extend(values)
                    else:
                        existing.append(values)
                    options[k] = existing
                else:
                    options[k] = values
            else:
                options[opt] = True

    return name_or_spec, options
```

### 使用例

```bash
# 方法1: 同じキーを複数回指定（推奨）
--exporter-option key=value1 --exporter-option key=value2 --exporter-option key=value3

# 方法2: カンマ区切り
--exporter-option key=value1,value2,value3

# 混合（同じキーを複数回 + カンマ区切り）
--exporter-option key=value1,value2 --exporter-option key=value3
# 結果: {"key": ["value1", "value2", "value3"]}
```

### 他のツールでの実例

#### Docker/Kubernetes（環境変数）

```bash
# 複数の値を個別に指定
docker run --env KEY=value1 --env KEY=value2 image

# または、1つの値にカンマ区切り
docker run --env KEY="value1,value2,value3" image
```

#### Terraform

```bash
# 複数の値を個別に指定
terraform apply -var "list=[value1,value2,value3]"
```

#### Git Config

```bash
# 複数の値を個別に指定
git config --add key value1
git config --add key value2
```

---

## 最終推奨

**複数の値を指定する場合**:

1. **基本**: 同じキーを複数回指定（`key=value1 key=value2`）

   - 最も明確で柔軟
   - スペースを含む値も扱える

2. **簡便性**: カンマ区切りもオプションでサポート（`key=value1,value2`）

   - 短いリストの場合に便利
   - 値にカンマが含まれない場合のみ

3. **両方の組み合わせ**: 同じキーを複数回 + カンマ区切りを組み合わせ可能
   - 最大の柔軟性

**実装の推奨**:

```python
# 同じキーが複数回指定された場合、自動的にリストにまとめる
# カンマ区切りの値もリストに変換
# 単一の値はそのまま（後からリストになる可能性を考慮）
```

---

## 一貫性の問題：スペース区切り vs カンマ区切り

### 問題点

本体のオプションではスペース区切りで複数の値を指定できます：

```bash
--rep 1 1 1
--shift 0.0 0.0 0.0
```

しかし、プラグインオプションで `rep=1,1,1` のようにカンマ区切りで書くのは一貫性がありません。

### 解決策：プラグインオプションもスペース区切りをサポート

#### 方法 1: 引用符で囲んでスペース区切り（推奨）

```bash
--exporter-option "rep 1 1 1"
--exporter-option "shift 0.0 0.0 0.0"
```

**メリット**:

- 本体オプションと一貫性がある
- スペース区切りで自然
- 複数の値を明確に指定できる

**実装例**:

```python
def plugin_option_parser(name_or_spec, option_list=None):
    options = {}

    if option_list:
        for opt in option_list:
            # スペース区切りの場合: "key value1 value2 value3"
            parts = opt.split()
            if len(parts) > 1:
                key = parts[0]
                values = parts[1:]

                # 数値に変換できる場合は変換
                converted_values = []
                for v in values:
                    try:
                        converted_values.append(int(v))
                    except ValueError:
                        try:
                            converted_values.append(float(v))
                        except ValueError:
                            converted_values.append(v)

                # 値が1つだけの場合はスカラー、複数の場合はリスト
                if len(converted_values) == 1:
                    value = converted_values[0]
                else:
                    value = converted_values

                # 同じキーが既に存在する場合
                if key in options:
                    existing = options[key]
                    if not isinstance(existing, list):
                        existing = [existing]
                    if isinstance(value, list):
                        existing.extend(value)
                    else:
                        existing.append(value)
                    options[key] = existing
                else:
                    options[key] = value
            # 従来の key=value 形式もサポート（後方互換性）
            elif "=" in opt:
                k, v = opt.split("=", 1)
                # カンマ区切りもサポート
                if "," in v:
                    values = [x.strip() for x in v.split(",")]
                    # 数値に変換できる場合は変換
                    converted = []
                    for val in values:
                        try:
                            converted.append(int(val))
                        except ValueError:
                            try:
                                converted.append(float(val))
                            except ValueError:
                                converted.append(val)
                    options[k] = converted if len(converted) > 1 else converted[0]
                else:
                    options[k] = v
            else:
                options[opt] = True

    return name_or_spec, options
```

#### 方法 2: コロンで区切ってスペース区切り

```bash
--exporter-option rep:1 1 1
--exporter-option shift:0.0 0.0 0.0
```

**メリット**:

- 引用符が不要
- キーと値の区切りが明確

**デメリット**:

- キーの後に `:` が必要で少し特殊

---

## 最終推奨：一貫性を保つ実装

### 推奨される書き方

```bash
# 単一値
--exporter-option key=value

# 複数値（スペース区切り、引用符で囲む） - 本体オプションと一貫性
--exporter-option "rep 1 1 1"
--exporter-option "shift 0.0 0.0 0.0"

# 複数値（カンマ区切り、後方互換性のためサポート）
--exporter-option rep=1,1,1

# 同じキーを複数回指定
--exporter-option "rep 1 1 1" --exporter-option "shift 0.0 0.0 0.0"
```

### 実装方針

1. **基本**: `key=value` 形式をサポート（既存形式）
2. **スペース区切り**: `"key value1 value2"` 形式をサポート（本体オプションと一貫性）
3. **カンマ区切り**: `key=value1,value2` 形式もサポート（簡便性）
4. **数値変換**: 数値として解釈できる場合は自動的に変換

### 実装例（完全版）

```python
def plugin_option_parser(name_or_spec, option_list=None):
    """
    プラグイン名とオプションを解析する。

    サポートする形式:
    1. key=value (単一値)
    2. key=value1,value2,value3 (カンマ区切り)
    3. "key value1 value2 value3" (スペース区切り、本体オプションと一貫性)
    4. 同じキーを複数回指定（リストにまとめる）
    """
    options = {}

    # 既存の [] 形式をサポート（後方互換性）
    if "[" in name_or_spec and "]" in name_or_spec:
        left = name_or_spec.find("[")
        right = name_or_spec.find("]")
        if 0 < left < len(name_or_spec) and 0 < right < len(name_or_spec) and left < right:
            args = name_or_spec[left + 1 : right]
            plugin_name = name_or_spec[:left]
            for elem in args.split(":"):
                if "=" in elem:
                    k, v = elem.split("=", 1)
                    options[k] = v
                else:
                    options[elem] = True
            # オプションリストもマージ
            if option_list:
                _parse_option_list(option_list, options)
            return plugin_name, options

    # 新しい形式: オプションリストを使用
    plugin_name = name_or_spec
    if option_list:
        _parse_option_list(option_list, options)

    return plugin_name, options


def _parse_option_list(option_list, options):
    """オプションリストを解析してoptions辞書に追加"""
    for opt in option_list:
        opt = opt.strip()

        # スペース区切り形式: "key value1 value2 value3"
        if " " in opt and "=" not in opt:
            parts = opt.split()
            key = parts[0]
            values = parts[1:]

            # 数値に変換できる場合は変換
            converted_values = []
            for v in values:
                converted_values.append(_try_convert_number(v))

            # 値が1つだけの場合はスカラー、複数の場合はリスト
            value = converted_values[0] if len(converted_values) == 1 else converted_values

            _add_option(options, key, value)

        # key=value 形式
        elif "=" in opt:
            k, v = opt.split("=", 1)

            # カンマ区切りの値をリストに変換
            if "," in v:
                values = [x.strip() for x in v.split(",")]
                converted = [_try_convert_number(x) for x in values]
                value = converted if len(converted) > 1 else converted[0]
            else:
                value = _try_convert_number(v)

            _add_option(options, k, value)

        # フラグ形式
        else:
            options[opt] = True


def _try_convert_number(s):
    """文字列を数値に変換できる場合は変換"""
    try:
        return int(s)
    except ValueError:
        try:
            return float(s)
        except ValueError:
            return s


def _add_option(options, key, value):
    """オプションを追加（既存のキーの場合はリストにまとめる）"""
    if key in options:
        existing = options[key]
        if not isinstance(existing, list):
            existing = [existing]
        if isinstance(value, list):
            existing.extend(value)
        else:
            existing.append(value)
        options[key] = existing
    else:
        options[key] = value
```

### 使用例

```bash
# 単一値
--exporter-option output=result.gro

# 複数値（スペース区切り、本体オプションと一貫性）
--exporter-option "rep 1 1 1"
--exporter-option "shift 0.0 0.0 0.0"

# 複数値（カンマ区切り、簡便性）
--exporter-option rep=1,1,1

# 混合
--exporter-option "rep 1 1 1" --exporter-option output=result.gro
```

これにより、本体オプション（`--rep 1 1 1`）とプラグインオプション（`--exporter-option "rep 1 1 1"`）で一貫性が保たれます。

---

## exporter プラグインから molecule プラグインを呼ぶ場合

exporter プラグインの中から molecule プラグインを呼ぶ可能性があります。例えば、gromacs exporter が独自の水分子モデルを指定したい場合などです。

### 設計方針

exporter プラグインは`genice3.plugin.Molecule()`を使って、オプションから molecule プラグインを読み取り、呼び出すことができます。

### 実装例: gromacs exporter

```python
# genice3/exporters/gromacs.py

from genice3.plugin import Molecule as get_molecule
from genice3.genice import GenIce3
from genice3.molecule import FourSiteWater

def dump(genice: GenIce3, file: TextIOWrapper, **options):
    """Gromacs形式で出力"""

    # オプションから水分子モデルを取得（オプション指定がない場合はデフォルト）
    water_model_name = options.get("water_model", "foursite")
    water_model_options = options.get("water_model_options", {})

    # moleculeプラグインを呼び出す
    if water_model_name:
        water_model = get_molecule(water_model_name, **water_model_options)
    else:
        water_model = FourSiteWater()

    # オプションからゲスト情報を取得
    guest_info = options.get("guests", {})
    spot_guest_info = options.get("spot_guests", {})

    # 原子構造を取得
    structure = genice.get_atomic_structure(
        water_model=water_model,
        guests=guest_info,
        spot_guests=spot_guest_info,
    )

    output = to_gro(
        cellmat=structure.cell,
        waters=structure.waters,
        guests=structure.guests,
        ions=structure.ions,
    )
    file.write(output)
```

### コマンドライン使用例

```bash
# 水分子モデルを指定
--exporter gromacs --exporter-option water_model=tip4p

# 水分子モデルとそのオプションを指定
--exporter gromacs \
  --exporter-option water_model=tip4p \
  --exporter-option "water_model_options param1=value1 param2=value2"

# ゲスト分子も指定
--exporter gromacs \
  --exporter-option water_model=tip4p \
  --exporter-option "guests A12=me"
```

### ヘルパー関数の提案

exporter プラグインでよく使うパターンを簡略化するため、ヘルパー関数を提供することも考えられます：

```python
# genice3/plugin.py に追加

def get_molecule_from_options(options: dict, key: str = "molecule", default: Optional[str] = None):
    """
    オプション辞書からmoleculeプラグインを取得するヘルパー関数

    Args:
        options: オプション辞書
        key: オプションキー名（例: "water_model", "guest_molecule"）
        default: デフォルト値（オプション名またはMoleculeインスタンス）

    Returns:
        Moleculeインスタンス
    """
    molecule_spec = options.get(key)
    if molecule_spec is None:
        if default is None:
            return None
        elif isinstance(default, str):
            return Molecule(default)
        else:
            return default

    # molecule_specが文字列の場合、プラグイン名として扱う
    if isinstance(molecule_spec, str):
        molecule_options_key = f"{key}_options"
        molecule_options = options.get(molecule_options_key, {})
        return Molecule(molecule_spec, **molecule_options)

    # 既にMoleculeインスタンスの場合
    return molecule_spec
```

### 使用例（ヘルパー関数使用）

```python
# genice3/exporters/gromacs.py

from genice3.plugin import get_molecule_from_options
from genice3.molecule import FourSiteWater

def dump(genice: GenIce3, file: TextIOWrapper, **options):
    """Gromacs形式で出力"""

    # ヘルパー関数で水分子モデルを取得
    water_model = get_molecule_from_options(
        options,
        key="water_model",
        default=FourSiteWater()
    )

    structure = genice.get_atomic_structure(water_model=water_model)
    # ...
```

### プラグイン間の依存関係の整理

exporter プラグインから molecule プラグインを呼ぶ場合の設計原則：

1. **明示的な指定**: exporter プラグインのオプションで molecule プラグイン名を明示的に指定
2. **デフォルト値の提供**: オプションが指定されない場合のデフォルト動作を明確にする
3. **プラグインシステムの活用**: `genice3.plugin.Molecule()`を使ってプラグインを読み込む
4. **オプションの階層化**: molecule プラグインのオプションを、exporter プラグインのオプションから分離して指定可能にする

### オプション指定の例（階層的）

```bash
# 方法1: シンプルな指定
--exporter-option water_model=tip4p

# 方法2: moleculeプラグインのオプションも指定
--exporter-option water_model=tip4p \
--exporter-option "water_model_options param1=value1 param2=value2"

# 方法3: []形式との互換性
--exporter "gromacs[water_model=tip4p:water_model_options:param1=value1]"
```

この設計により、exporter プラグインは柔軟に molecule プラグインを利用できるようになります。

---

## 角括弧と丸括弧の実用性の検討

### 実際のテスト結果

bash で実際にテストした結果：

```bash
# 丸括弧: 引用符なしでエラー
$ echo plugin(key=value)
bash: 予期しないトークン `(' 周辺に構文エラーがあります

# 丸括弧: 引用符ありでOK
$ echo "plugin(key=value)"
plugin(key=value)

# 角括弧: 引用符ありでOK
$ echo "plugin[key=value]"
plugin[key=value]
```

### 結論

**どちらの括弧も引用符が必要**なため、括弧の種類による実用性の差はほとんどありません。

- 丸括弧 `()`: bash ではサブシェルとして解釈されるため引用符が必要
- 角括弧 `[]`: 引用符で囲めば問題なく使用可能

### 推奨: 複数のオプション引数方式が最優先

括弧形式は引用符が必要なため、**複数のオプション引数方式を主推奨**します：

```bash
# 複数のオプション引数方式（推奨）- 引用符不要、スペースが使える
--exporter gromacs --exporter-option water_model=tip4p --exporter-option output=result.gro

# 括弧形式は簡便性のためにサポート（引用符が必要）
--exporter "gromacs[water_model=tip4p:output=result.gro]"  # または "gromacs(...)"
```

### 実装: 両方の形式をサポート

```python
def plugin_option_parser(s, option_list=None):
    """
    プラグイン名とオプションを解析する。
    角括弧 [] と丸括弧 () の両方をサポート（丸括弧を推奨）
    """
    options = {}

    # 丸括弧形式をチェック（優先）
    left_paren = s.find("(")
    right_paren = s.find(")")
    if 0 < left_paren < len(s) and 0 < right_paren < len(s) and left_paren < right_paren:
        args = s[left_paren + 1 : right_paren]
        plugin_name = s[:left_paren]
        for elem in args.split(":"):
            if "=" in elem:
                k, v = elem.split("=", 1)
                options[k] = v
            else:
                options[elem] = True
        # オプションリストもマージ
        if option_list:
            _parse_option_list(option_list, options)
        return plugin_name, options

    # 角括弧形式をチェック（後方互換性）
    left_bracket = s.find("[")
    right_bracket = s.find("]")
    if 0 < left_bracket < len(s) and 0 < right_bracket < len(s) and left_bracket < right_bracket:
        args = s[left_bracket + 1 : right_bracket]
        plugin_name = s[:left_bracket]
        for elem in args.split(":"):
            if "=" in elem:
                k, v = elem.split("=", 1)
                options[k] = v
            else:
                options[elem] = True
        # オプションリストもマージ
        if option_list:
            _parse_option_list(option_list, options)
        return plugin_name, options

    # 新しい形式: オプションリストを使用
    plugin_name = s
    if option_list:
        _parse_option_list(option_list, options)

    return plugin_name, options
```

### 比較

| 形式           | 例                                                          | 引用符 | 簡潔性 | 冗長性 | 柔軟性 | 推奨度 |
| -------------- | ----------------------------------------------------------- | ------ | ------ | ------ | ------ | ------ |
| 括弧形式       | `"plugin[key=value:key2=value2]"`                           | 必要   | 高い   | 低い   | 中     | ★★     |
| 複数オプション | `--exporter-option key=value --exporter-option key2=value2` | 不要   | 低い   | 高い   | 最高   | ★      |

### 最終推奨：用途に応じて使い分け

**結論**: 用途に応じて使い分けるのが最適です。

1. **括弧形式（簡潔性重視・基本推奨）**: 多くのオプションを 1 行で指定する場合

   ```bash
   --exporter "gromacs[water_model=tip4p:output=result.gro:option1=value1:option2=value2]"
   ```

   - **メリット**: 簡潔、1 行で済む、多数のオプションでも読みやすい
   - **デメリット**: 引用符が必要、スペースが使えない
   - **用途**: 通常の使用ではこちらが便利

2. **複数オプション方式（柔軟性重視・補助的）**: スペースを含む値や、動的に生成する場合

   ```bash
   --exporter gromacs \
     --exporter-option water_model=tip4p \
     --exporter-option output=result.gro
   ```

   - **メリット**: 引用符不要、スペースが使える、柔軟
   - **デメリット**: 冗長、オプションが多いと 1 行が非常に長くなる
   - **用途**: スペースを含む値など、特殊な場合のみ

3. **混合使用**: 基本は括弧形式、追加オプションは個別指定
   ```bash
   --exporter "gromacs[water_model=tip4p]" --exporter-option output=result.gro
   ```

### 括弧の種類について

角括弧 `[]` vs 丸括弧 `()`:

- **実用性**: どちらも引用符が必要で実用性に大きな差はない
- **既存コード**: 角括弧 `[]` が既に使用されている
- **推奨**: 角括弧 `[]` をデフォルトとして維持（変更の必要性は低い）
  - 角括弧は配列やオプションを示す記法として一般的
  - 丸括弧は関数呼び出しのイメージが強く、プラグインオプションにはやや不自然

### 実装方針

1. **括弧形式を基本とする**（簡潔性のため）

   - 角括弧 `[]` をデフォルトとして維持
   - 引用符は仕様として受け入れる（簡潔性の代償）

2. **複数オプション方式もサポート**（柔軟性のため）

   - スペースを含む値など、特殊な場合に使用

3. **両方を組み合わせ可能**
