# プラグイン単体テスト (GenIce3)

GenIce3 の各プラグインカテゴリ（unitcell, molecule, exporter）について、
プラグインが正しくロード・インスタンス化でき、必須属性・インターフェースを満たすことを検証する。

## テスト内容

- **test_unitcell.py**: 全 unitcell プラグインのうち、引数なしでインスタンス化できるものについて、`cell`, `lattice_sites`, `graph`, `fixed` の存在と型を検証する。
- **test_molecule.py**: 全 molecule プラグインについて、`sites`, `labels`, `name` の存在と型、および整合性を検証する。
- **test_exporter.py**: 全 exporter プラグインについて、モジュールが `dumps` または `dump` を提供することを検証する。

## 実行方法

プロジェクトルートで:

```bash
pytest tests/unittest/ -v
```

または `tests/unittest` で:

```bash
make
```

（Makefile は `pytest` を実行するだけ。事前のデータ生成は不要。）
