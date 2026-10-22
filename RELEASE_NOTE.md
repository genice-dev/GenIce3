# RELEASE NOTE

Scope: GenIce3-related changes after `a7e63b652a2cc324e84a55dced9892eba907ce84`

## Overview

## 3.1.1

Documentation and visualization examples patch: restore plotly in the formats table, unify py3Dmol / Plotly / Yaplot under `examples/api/visualize`, fix Yaplot notebook helper install, and document `set_replication_matrix` with the reshape figure.

## 3.1

Yaplot visualization polish: CPK-style colors, layer names, startup centering (Yaplot 5.6+), and a one-click Colab demo for CS2 methane hydrate (`demo_CS2.ipynb`). Depends on `yaplotlib` ≥ 1.0.


After branching from the GenIce2 line, GenIce3 was redesigned around its API, option model, dependency engine, and plugin architecture. Version **3.0** is the first stable release of this line: ice-rule and polarization logic live in **genice-core**, while GenIce3 focuses on unit cells, guests, ions, exporters, and the CLI/Python API.

## Major Updates

- **Core foundation of GenIce3**
  - Introduced `genice3.py` and reorganized internals around a dependency-driven reactive recalculation model.
  - Improved reevaluation stability when settings change through refinements to `DependencyCacheMixin`, `@reactive`, and dependency processing.
  - Reactive inputs (`unitcell`, `seed`, …) are declared with `Input` on `GenIce3`; `@reactive(public=True)` drives the public property list.

- **CLI and option-system redesign**
  - Reworked option syntax in multiple iterations, resulting in a more structured interface and stronger YAML-based workflows (`-Y` / `--config`).
  - Refined polarization-related parameters such as `pol_loop_1` and `pol_loop_2`, including forced and target-polarization handling.
  - Improved CLI usability by supporting negative values and shorthand option forms.

- **unitcell and structure-model expansion**
  - Migrated and added many unitcell plugins, with continuous behavior-comparison tests.
  - Added new structures including `YKD`, `ice21`, and its alias entries, plus cylindrical **prism** ice (API).
  - Improved CIF-derived unitcell generation by branching logic based on whether hydrogen positions are explicitly provided.

- **Doping, defects, and cage analysis**
  - Added or expanded support for ion placement, `spot_cation`-related handling, group options, Hydronium/Hydroxide, and Bjerrum defects.
  - Enhanced `cage_survey`-related behavior, including max-ring handling (default 16) and evaluation logic.

- **Exporter and visualization improvements**
  - Improved GROMACS output, added a LAMMPS exporter, and expanded visualization paths including plotly and py3Dmol.
  - Continued refinement of exporter format functions and option parsing; several exporters sort sites/edges for deterministic output.

- **Optional service layer (Web API and MCP)**
  - Shared `genice3.service` for YAML/TOML/JSON config, meta queries, and generate.
  - Optional **Web API** (`genice3[web]` / `genice3-web`) and **stdio MCP** (`genice3[mcp]` / `genice3-mcp`). See [docs/mcp.md](docs/mcp.md).

- **Documentation and tooling**
  - Manual on GitHub Pages; plugin tables and citations generated from the repo.
  - Agent skill distributed from this repository (`npx skills add genice-dev/GenIce3`).
  - Expanded API notebooks and examples (`API.ipynb`, `examples/api/`).

- **Testing and development environment**
  - Strengthened comparison tests and discovery workflows (identity suite under renovation for a later release).
  - Continued refactoring around project layout and tooling (`scripts/`, `dev/`, and Makefile/build flows).

## Compatibility Notes

- Migration from GenIce2-style usage to the GenIce3 API/option system includes behavior and syntax changes. See [changes from GenIce2](https://genice-dev.github.io/GenIce3/changes-from-genice2/).
- Polarization settings (`pol_loop_1` / `pol_loop_2`, replacing `depol_loop`), cage evaluation (`cage_survey` instead of `--assess_cages`), doping options (`-A` / `-C`), and exporter options should be checked when porting older scripts.
- In CIF processing, the `partial_order` option has been removed, and behavior now depends on hydrogen-position input availability.
- Package name and entry points are `genice3` (PyPI: `genice3`); plugin groups use the `genice3.*` namespaces.

## Version Progression (observed in this period)

- `3.0a3` -> `3.0a4` -> `3.0b0` -> `3.0b1` -> `3.0b2` -> `3.0b3` -> `3.0b4` -> `3.0b5` -> `3.0b6` -> `3.0b7` -> `3.0b8` -> **`3.0`**

## Recent Topics (through 2026-10)

- Shared `genice3.service` layer; optional stdio MCP and Web API (`genice3[mcp]`, `genice3[web]`).
- Structured JSON logging (NDJSON opt-in).
- Agent skill packaging and try-it links on README / docs.
- Reactive `Input` declarations and public `@reactive` property list (`3.0b7`).
- Deterministic exporter ordering (site index / molecule name / graph edges).
- Earlier beta work: `prism`, `ice21` aliases, CIF hydrogen-position branching, exporter and API doc improvements.
