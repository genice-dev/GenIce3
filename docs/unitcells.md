# Unit cells（単位胞一覧）

第一引数で指定する単位胞名（シンボル）の一覧です。説明が同じ構造は同一行にまとめています。

<div class="unitcell-symbol-table" markdown="1">

| Symbol | Description | References |
| ------ | ----------- | ---------- |
| 0, ice0 | Metastable ice "0". | [[Russo 2014](references.md#russo-2014)] |
| 11, XI, ice11 | A candidate for an antiferroelectric Ice XI #19. | [[Fan 2010](references.md#fan-2010)] [[Jackson 1997](references.md#jackson-1997)] |
| 115_2_114, 12_1_11, 144_2_7301, 151_2_4949650, 153_2_155471, 176_2_5256, 207_1_4435, 2_2_623457, ACO, CS4, DDR, IWV, LTA, MAR, NON, PCOD8007225, PCOD8036144, PCOD8204698, PCOD8301974, PCOD8321499, PCOD8324623, SGT, SOD, engel01, engel03, engel04, engel17, engel20, engel23, engel24, engel26, engel29, engel30, engel31, engel34, sVII | Hypothetical zeolitic ice | [[Engel 2018](references.md#engel-2018)] [[IZA Database](references.md#iza-database)] [[Jeffrey 1984](references.md#jeffrey-1984)] [[Kosyakov 1999](references.md#kosyakov-1999)] |
| 11alt | A layered ferroelectric Ice XI. |  |
| 12, XII, ice12 | Metastable high-pressure ice XII. | [[Koza 2000](references.md#koza-2000)] [[Lobban 1998](references.md#lobban-1998)] |
| 13, XIII, ice13 | Ice XIII, a hydrogen-ordered counterpart of ice V. | [[Salzmann 2006](references.md#salzmann-2006)] |
| 14, ice14 | Ice XIV, a partially hydrogen-ordered counterpart of ice XII. Note that it does not reproduce the occupancies (probability of occupation) of the possible hydrogen sites. | [[Salzmann 2006](references.md#salzmann-2006)] |
| 16, CS2, MTN, XVI, ice16, sII | Ultralow-density Ice XVI. | [[Falenty 2014](references.md#falenty-2014)] [[IZA Database](references.md#iza-database)] [[Jeffrey 1984](references.md#jeffrey-1984)] [[Kosyakov 1999](references.md#kosyakov-1999)] [[Sikiric 2010](references.md#sikiric-2010)] |
| 17, XVII, ice17 | Ultralow-density Ice XVII. | [[Rosso 2016](references.md#rosso-2016)] [[Smirnov 2013](references.md#smirnov-2013)] [[Strobel 2016](references.md#strobel-2016)] |
| 1c, Ic, ice1c | Cubic type of ice I. | [[Vos 1993](references.md#vos-1993)] |
| 1h, Ih, ice1h | Most popular Ice I (hexagonal). NOTE: Due to a historical reason, the crystal axes of hexagonal ice are exchanged. If you want the basal plane to be Z axis, please use ice1h_unit instead. |  |
| 1h_unit, ice1h_unit | Most popular Ice I (hexagonal).  |  |
| 2, II, ice2 | Hydrogen-ordered ice II. | [[Kamb 1964](references.md#kamb-1964)] [[Kamb 2003](references.md#kamb-2003)] [[Londono 1988](references.md#londono-1988)] |
| 2D3 | Trilayer honeycomb ice. |  |
| 2d, ice2d, ice2rect | A hydrogen-disordered counterpart of ice II. | [[Nakamura 2015](references.md#nakamura-2015)] |
| 3, III, ice3 | Ice III. | [[Petrenko 1999](references.md#petrenko-1999)] |
| 4, IV, ice4 | Ice IV. | [[Avogadro](references.md#avogadro)] |
| 5, V, ice5 | Monoclinic ice V (testing). |  |
| 5R | Ice V with orthogonal unit cell. (testing) |  |
| 6, VI, ice6 | Conventional high-pressure ice VI. | [[Petrenko 1999](references.md#petrenko-1999)] |
| 6h | Half lattice of ice VI. |  |
| 7, VII, ice7 | Conventional high-pressure ice VII. |  |
| 8, VIII, ice8 | Ice VIII, a hydrogen-ordered counterpart of ice VII. | [[Kuhs 1998](references.md#kuhs-1998)] |
| 9, IX, ice9 | Ice IX, a hydrogen-ordered counterpart of ice III. | [[Londono 1993](references.md#londono-1993)] |
| A, iceA | Hypothetical ice A. | [[Baez 1998](references.md#baez-1998)] |
| A15, Struct33 | Cubic Structure I of clathrate hydrate. | [[Sikiric 2010](references.md#sikiric-2010)] |
| B, iceB | Hypothetical ice B. | [[Baez 1998](references.md#baez-1998)] |
| BSV, engel05 | Hypothetical zeolitic ice of the gyroid structure. | [[Engel 2018](references.md#engel-2018)] [[IZA Database](references.md#iza-database)] |
| C14, C15, C36, FK6layers, FK9layers, HS2, Hcomp, Struct01, Struct03, Struct04, Struct05, Struct06, Struct07, Struct08, Struct09, Struct10, Struct11, Struct12, Struct13, Struct14, Struct15, Struct16, Struct17, Struct18, Struct19, Struct20, Struct21, Struct22, Struct23, Struct24, Struct25, Struct26, Struct27, Struct28, Struct29, Struct30, Struct31, Struct32, Struct34, Struct35, Struct36, Struct37, Struct38, Struct39, Struct40, Struct41, Struct42, Struct43, Struct44, Struct45, Struct46, Struct47, Struct48, Struct49, Struct50, Struct51, Struct52, Struct53, Struct54, Struct55, Struct56, Struct57, Struct58, Struct59, Struct60, Struct61, Struct62, Struct63, Struct64, Struct65, Struct66, Struct67, Struct68, Struct69, Struct70, Struct71, Struct72, Struct73, Struct74, Struct75, Struct76, Struct77, Struct78, Struct79, Struct80, Struct81, Struct82, Struct83, Struct84, Z, delta, mu, psigma, sV, sigma, zra-d | A space fullerene. | [[Sikiric 2010](references.md#sikiric-2010)] |
| CIF | Load a CIF file and create a unit cell.（オプションあり） |  |
| CRN1, CRN2, CRN3 | A continuous random network of Sillium. | [[Mousseau 2001](references.md#mousseau-2001)] |
| CS1, MEP, sI | Clathrate hydrates sI. | [[Frank 1959](references.md#frank-1959)] [[IZA Database](references.md#iza-database)] [[Jeffrey 1984](references.md#jeffrey-1984)] [[Kosyakov 1999](references.md#kosyakov-1999)] |
| DOH, HS3, sH | Clathrate type H. |  |
| EMT | Hypothetical ice with a large cavity. | [[IZA Database](references.md#iza-database)] [[Liu 2019](references.md#liu-2019)] |
| FAU | Hypothetical ice at negative pressure ice 'sIV'. | [[Huang 2017](references.md#huang-2017)] [[IZA Database](references.md#iza-database)] |
| HS1, sIV | Hydrogen-disordered ice Ih. | [[Frank 1959](references.md#frank-1959)] [[Jeffrey 1984](references.md#jeffrey-1984)] [[Kosyakov 1999](references.md#kosyakov-1999)] |
| M, iceM | A hypothetical hydrogen-ordered high-density ice. | [[Mochizuki 2024](references.md#mochizuki-2024)] |
| RHO | Hypothetical ice at negative pressure ice 'sIII'. | [[Huang 2016](references.md#huang-2016)] [[IZA Database](references.md#iza-database)] |
| Struct02 | A space fullerene. (I phase?) | [[Sikiric 2010](references.md#sikiric-2010)] |
| T | Hypothetical clathrate type T. | [[Karttunen 2011](references.md#karttunen-2011)] [[Sikiric 2010](references.md#sikiric-2010)] |
| XIc-a | A candidate for the proton-ordered counterpart of ice Ic. The structure 'a' in Figure 1. | [[Geiger 2014](references.md#geiger-2014)] |
| aeroice | Aeroice (alias of xFAU).（オプションあり） | [[Matsui 2017](references.md#matsui-2017)] |
| c0te | Filled ice C0 by Teeratchanan (Hydrogen-disordered.) (Positions of guests are supplied.) | [[Teeratchanan 2015](references.md#teeratchanan-2015)] |
| c1te | Hydrogen-ordered hydrogen hydrate C1 by Teeratchanan. (Positions of guests are supplied.) | [[Teeratchanan 2015](references.md#teeratchanan-2015)] |
| eleven | Ice XI w/ stacking faults. |  |
| i | Hypothetical ice "i". | [[Fennell 2005](references.md#fennell-2005)] |
| iceL | The hypothetical Ice L | [[Lei 2025](references.md#lei-2025)] |
| iceMd | A hydrogen-disordered counterpart of ice M. | [[Mochizuki 2024](references.md#mochizuki-2024)] |
| iceT | Hypothetical ice T. | [[Hirata 2017](references.md#hirata-2017)] |
| iceT2 | Hypothetical ice T2. | [[Yagasaki 2018](references.md#yagasaki-2018)] |
| one | Ice I w/ stacking disorder. |  |
| oprism | Hydrogen-ordered ice nanotubes. | [[Koga 2001](references.md#koga-2001)] |
| sTprime | Filled ice sT'. | [[Smirnov 2013](references.md#smirnov-2013)] |
| xFAU | Aeroice xFAU.（オプションあり） | [[Matsui 2017](references.md#matsui-2017)] |
| xdtc | A porous ice with cylindrical channels. | [[Matsumoto 2021](references.md#matsumoto-2021)] |
| zeolite | Load a zeolite framework from IZA by 3-letter code (CIF via download).（オプションあり） |  |
| TS1 | (Undocumented) |  |
| dtc | (Undocumented) |  |
| sIII | (Undocumented) |  |
</div>

## Unit cell プラグイン（サブオプション付き）

以下の単位胞は、追加のオプション（ファイルパス・IZAコードなど）が必須です。

- **CLI:** `--オプション名 値` の形式（例: `genice3 CIF --file MEP.cif`）
- **YAML:** 設定ファイルでは `unitcell:` 配下に `name` とオプションをキーで書く（各プラグインの下に例を示す）
- `genice3 SYMBOL?` でプラグインの usage を表示できます。

### CIF

Load a CIF file and create a unit cell.

**CLI:**

```
genice3 CIF --file path/to/structure.cif (required) --osite O --hsite VALUE
  --file: Path to CIF file.
  --osite: O site label or regex.
  --hsite: H site label or regex (omit to let GenIce3 place H).
```

**API:**

```python
UnitCell("CIF", file='path/to/structure.cif', osite='O', hsite=None)
```

**YAML:**

```yaml
unitcell:
  name: CIF
  file: path/to/structure.cif
  osite: O
  hsite: ...
```

| CLI オプション | 説明 |
| -------------- | ---- |
| `--file` | Path to CIF file. |
| `--osite` | O site label or regex. |
| `--hsite` | H site label or regex (omit to let GenIce3 place H). |

### aeroice

Aeroice (alias of xFAU).

**CLI:**

```
genice3 aeroice --length 3 (required)
  --length: Number of hexagonal prism segments. 0=SOD, 1=FAU, 2+=aeroice.
```

**API:**

```python
UnitCell("aeroice", length=3)
```

**YAML:**

```yaml
unitcell:
  name: aeroice
  length: 3
```

| CLI オプション | 説明 |
| -------------- | ---- |
| `--length` | Number of hexagonal prism segments. 0=SOD, 1=FAU, 2+=aeroice. |

### xFAU

Aeroice xFAU.

**CLI:**

```
genice3 xFAU --length 3 (required)
  --length: Number of hexagonal prism segments. 0=SOD, 1=FAU, 2+=aeroice.
```

**API:**

```python
UnitCell("xFAU", length=3)
```

**YAML:**

```yaml
unitcell:
  name: xFAU
  length: 3
```

| CLI オプション | 説明 |
| -------------- | ---- |
| `--length` | Number of hexagonal prism segments. 0=SOD, 1=FAU, 2+=aeroice. |

### zeolite

Load a zeolite framework from IZA by 3-letter code (CIF via download).

**CLI:**

```
genice3 zeolite --code LTA (required) --osite O --hsite VALUE
  --code: 3-letter IZA framework code (e.g. LTA, FAU).
  --osite: O site label or regex.
  --hsite: H site label or regex (omit to let GenIce3 place H).
```

**API:**

```python
UnitCell("zeolite", code='LTA', osite='O', hsite=None)
```

**YAML:**

```yaml
unitcell:
  name: zeolite
  code: LTA
  osite: O
  hsite: ...
```

| CLI オプション | 説明 |
| -------------- | ---- |
| `--code` | 3-letter IZA framework code (e.g. LTA, FAU). |
| `--osite` | O site label or regex. |
| `--hsite` | H site label or regex (omit to let GenIce3 place H). |

---

Names in quotation marks have not been experimentally verified.

You can add custom unit cells by placing unit-cell plugins in a `unitcell` directory. [cif2ice](https://github.com/vitroid/cif2ice) can fetch CIF files from the [IZA structure database](http://www.iza-structure.org/databases) and help you create a unitcell module.

Note: Different naming conventions are used in the literature.

| CH/FI | CH  | ice | FK    | Zeo | Foam          |
| ----- | --- | --- | ----- | --- | ------------- |
| sI    | CS1 | -   | A15   | MEP | Weaire-Phelan |
| sII   | CS2 | 16  | C15   | MTN |               |
| sIII  | TS1 | -   | sigma | -   |               |
| sIV   | HS1 | -   | Z     | -   |               |
| sV    | HS2 | -   | \*    | -   |               |
| sVII  | CS4 | -   | \*    | SOD | Kelvin        |
| sH    | HS3 | -   | \*    | DOH |               |
| C0    | -   | 17  | \*    | -   |               |
| C1    | -   | 2   | \*    | -   |               |
| C2    | -   | 1c  | \*    | -   |               |

FI: Filled ices; CH: Clathrate hydrates; FK: Frank-Kasper duals; Zeo: Zeolites; Foam: foam crystals [[Weaire 1994](references.md#weaire-1994)].

-: No correspondence; \*: Non-FK types.

To request new unit cells, contact [vitroid@gmail.com](mailto:vitroid@gmail.com).
