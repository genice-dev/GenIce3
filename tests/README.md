# tests

## Make ターゲット（`make -C tests` またはプロジェクトルートで `make test`）

- **all** … test_unittest, test_cli_ux, test_genice3 を順に実行
- **test_unittest** … `unittest/` 以下の pytest
- **test_cli_ux** … `test_cli_ux.py` の pytest
- **test_genice3** … genice3 テストスイート（検証・コア・統合・オプション解析など）

## genice3 テストスイート

以下は `tests/` 直下に配置されています（旧 `tests/genice3/` から移動済み）。

- `test_validation.py` … 検証関数の定義
- `test_core.py` … GenIce3 コアの単体テスト
- `test_integration.py` … 代表的な unitcell / molecule / exporter の組み合わせテスト
- `test_optionparser_integration.py` … PoolBasedParser の統合テスト
- `test_gromacs_parse_options.py` … gromacs exporter の parse_options テスト

実行例（プロジェクトルートで）:

```bash
make test
# または genice3 のみ
make -C tests test_genice3
```

pytest は `python -m pytest` で実行します（Makefile 内で `PYTEST` として定義）。
