# Getting started

## Quick start

To generate a hydrogen-disordered ice structure, use the unit cell name (e.g. `1h` for Ice Ih, `4` for Ice IV) as the first argument:

```shell
genice3 1h > ice.gro
```

Full documentation is available at the [manual](https://genice-dev.github.io/GenIce3).

## New in GenIce3

- **Command line**
  - Option syntax is unified; hierarchical options and YAML config files (`-Y` / `--config`) replace many GenIce2-style flags.
  - Polarization control uses `pol_loop_1` and `pol_loop_2` (replacing `depol_loop`).
  - Package and entry points are `genice3` (PyPI: `genice3`); plugin groups use the `genice3.*` namespaces.
- **API**
  - Python API redesigned around `GenIce3` and `DependencyEngine`: specify what you need and dependent quantities recompute automatically.
  - Embed protonic defects (H₃O⁺, OH⁻) and Bjerrum topological defects from Python (see the [API examples](https://genice-dev.github.io/GenIce3/api-examples/) in the manual).
  - Setter-style configuration and expanded notebooks/examples (`API.ipynb`, `examples/api/`).
- **Algorithm and core**
  - Ice-rule and depolarization logic delegated to **genice-core** (≥1.6.0); GenIce3 focuses on unit cells, guests, ions, and exporters.
  - Reactive pipeline: `@reactive` properties and explicit dependency tracking replace ad-hoc recalculation.
- **Unit cells and structures**
  - Lattice plugins moved to `genice3.unitcell`; many GenIce2 structures ported with identity comparison tests.
  - CIF-derived unit cells branch on whether hydrogen positions are supplied; `partial_order` removed.
  - New or updated structures include auxiliary ices, `YKD`, `ice21` (and aliases), and cylindrical **prism** ice (API).
- **Clathrates, ions, and defects**
  - Cage assessment: GenIce2's `--assess_cages` removed — use exporter `cage_survey` (JSON). Default max cage ring count is 16 (override via exporter options).
  - Spot ions use `-A` / `-C` (spot anion/cation; **not** the old cage-assessment flag). Group guests and spot-cation cage reporting extended; unit-cell ion suboptions (e.g. `--group`) in YAML.
- **Exporters and visualization**
  - Built-in and plugin exporters (GROMACS, CIF, LAMMPS, yaplot, plotly, py3Dmol, etc.); format functions and option parsing refined.
  - Optional **Web API** (`genice3-web`) with client examples and tests.
- **Documentation and tooling**
  - Manual on GitHub Pages; plugin tables and citations generated from the repo (`make docs`, `make README.md`).
  - For a narrative of the GenIce3 development period and compatibility notes, see [RELEASE_NOTE.md](https://github.com/genice-dev/GenIce3/blob/main/RELEASE_NOTE.md) in the repository.

**Example — cage survey (formerly `--assess_cages`):**

```shell
genice3 CS2 -e cage_survey > cages.json
```

## Demo

GenIce3 works well in interactive environments.  
[Try it](https://colab.research.google.com/github/genice-dev/GenIce3/blob/main/API.ipynb) on Google Colaboratory.

## Requirements

- networkx >=2.0.dev20160901144005
- numpy >=2.0
- pairlist >=1.0.0
- cycless >=0.7
- graphstat >=0.3.3
- yaplotlib >=0.1.2
- openpyscad >=0.5.0
- pyyaml >=6.0
- jinja2 >=3.1.4
- cif2ice (>=0.4.1,<0.5.0)
- genice-core (>=1.6.0,<2.0.0)
- fastapi (>=0.135.3,<0.136.0)
- uvicorn (>=0.44.0,<0.45.0)


## Installation

GenIce3 is on [PyPI](https://pypi.org/project/genice3/). Install with pip:

```shell
pip install genice3
```

## Uninstallation

```shell
pip uninstall genice3
```