# プロンプトによる指示例

## プロンプト例

### CLI（sIハイドレート・GROMACS・TIP4P）

- https://genice-dev.github.io/GenIce3 のマニュアルを参照して、GenIce3で以下を実現するCLIコマンドを書いて：sI型ハイドレートを2x2x2で、全ケージにUnited atomメタン、GROMACS形式、水はTIP4P。

### API（ビルトイン構造）

- このリポジトリの `docs/` を参照して、GenIce3 APIで以下を実現するPythonコードを書いて：Zeolite ITT構造の氷を2x2x2で、GROMACS形式、水はTIP4P。

（注: Zeolite **ITT** は GenIce3 にビルトインで含まれていません。ITT を使う場合は IZA 等から CIF を取得し、単位胞に `CIF[file=path/to/ITT.cif]` を指定する必要があります。ビルトインのゼオライト氷は FAU, RHO, LTA, SOD, DDR など。）

### API（aeroice・GROMACS・TIP5P）

- このリポジトリの `docs/` を参照して、GenIce3 APIで以下を実現するPythonコードを書いて: 結合部の長さが3のaeroice構造の氷をGROMACS形式、水はTIP5P。

（ヒント: 単位胞は [Unit cells](docs/unitcells.md) の「サブオプション付き」に aeroice / xFAU がある。「結合部の長さ」＝オプション `length`。API では `UnitCell("aeroice", length=3)`、水モデルは `Exporter("gromacs").dump(genice, water_model="tip5p")` または `water_model="5site"`。）
