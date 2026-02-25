# README 由来の内容チェック（簡素化後の対応状況）

## 対応済み（docs に同等以上がある）

| 旧 README の内容 | 現在の場所 |
|------------------|------------|
| Usage（オプション一覧） | docs/cli.md（temp_docs から生成） |
| Examples（1h, CS2 等） | docs/cli.md |
| Basics（depolarization, seed, density, モジュール構成） | docs/basics.md |
| Clathrate（CS1/CS2 例、cage 一覧、EO プラグイン例、多重占有の注意） | docs/clathrate-hydrates.md |
| Doping（-a/-c, Na/Cl 例、陽陰イオン同数、プロトン/Bjerrum は API のみ） | docs/doping-and-defects.md |
| Output formats（表、mdanalysis、7 ステージ） | docs/output-formats.md |
| Ice structures（表、命名対応表、cif2ice） | docs/ice-structures.md |
| Water models（表） | docs/water-models.md |
| Guest molecules（表） | docs/guest-molecules.md |
| Extra plugins（genice2-rdf 等） | docs/plugins.md |
| Main changes from GenIce2（cage_survey） | docs/changes-from-genice2.md |
| References / Citation / Contribute / License | README + docs/citation.md, contribute.md, license.md |

---

## 現状とずれている可能性がある点

### 1. pyproject.toml の二重管理（version・dependencies）

- **replacer が参照しているのは `[tool.poetry]`**（version, dependencies）。
- **`[project]`** には別の version（3.0a4）と依存（genice-core>=1.3.1, cycless>=0.7 等）がある。
- README / docs/getting-started の「Version」「Requirements」は **poetry 側** の値になる。
- 運用で `[project]` を正とする場合、README と実ビルドの情報が食い違う可能性あり。
- **提案**: version と dependencies を `[project]` に一本化し、replacer で `[project]` を読むようにするか、少なくとも poetry と project を手動で揃える。

### 2. 設定ファイル（-C / YAML）のフォーマットが未記載

- 旧 README では「-C で YAML を読める。フォーマットは manual 参照」だった。
- 現在の docs には **「config ファイルの YAML フォーマット」の説明ページや節がない**。
- cli.md の usage に "config file format" と出るが、manual 内にその説明がない。
- **提案**: docs の CLI か Getting started に「設定ファイル」の短い節を追加し、例 YAML と主要キー（unitcell, rep, exporter, guest 等）を書く。

### 3. 表記のゆれ（uathf / uathf6）

- **cli.md**: `genice3 CS2 -g 16=uathf6 ...`（旧 README と同じ）。
- **clathrate-hydrates.md**: `genice3 CS2 -g 16=uathf -G 0=me`。
- guest-molecules では `uathf`（5-site）と `uathf6`（Undocumented）が別エントリ。
- 意図的に「別の例」なら問題ないが、どちらを推すかで揃えてもよい。

---

## 不足している情報（あった方がよいもの）

- **-C / YAML 設定ファイルのフォーマット**（上記 2）。
- 上記以外で、旧 README にあった実質的な説明が docs から抜けているものはなし。
