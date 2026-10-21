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
| Unit cells（表、命名対応表、cif2ice、サブオプション付きプラグイン） | docs/unitcells.md（自動生成） |
| Water models（表） | docs/water-models.md |
| Guest molecules（表） | docs/guest-molecules.md |
| Extra plugins（genice2-rdf 等） | docs/plugins.md |
| Main changes from GenIce2（README と同一本文） | `templates/new-in-genice3.md` → README / `docs/changes-from-genice2.md` / getting-started |
| References / Citation / Contribute / License | README + docs/citation.md, contribute.md, license.md |

---

## 現状とずれている可能性がある点

### 1. pyproject.toml の二重管理（version・dependencies）— 解消済み

- 正は **`[project]`**。`scripts/replacer.py` も `[project]` を読む。
- README / docs の Version・Requirements は `make README.md` / `make docs` で `[project]` から生成される。

### 2. 設定ファイル（`-Y` / YAML）のフォーマット

- **対応済み:** `docs/cli.md` の「Config file」節（主要キーと最小例）。長い例は `examples/config_example.yaml`。
- 生成元は `temp_docs/cli.md`。編集後は `make docs`。

### 3. 表記のゆれ（uathf / uathf6）

- **cli.md**: `genice3 CS2 -g 16=uathf6 ...`（旧 README と同じ）。
- **clathrate-hydrates.md**: `genice3 CS2 -g 16=uathf -G 0=me`。
- guest-molecules では `uathf`（5-site）と `uathf6`（Undocumented）が別エントリ。
- 意図的に「別の例」なら問題ないが、どちらを推すかで揃えてもよい。

---

## 不足している情報（あった方がよいもの）

- 上記以外で、旧 README にあった実質的な説明が docs から抜けているものはなし。
