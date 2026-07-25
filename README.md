![Logo](https://raw.githubusercontent.com/vitroid/GenIce/develop/logo/genice-v0.png)

# GenIce3

A Swiss army knife to generate hydrogen-disordered ice structures.

**Quick start:** Use the unit cell name as the first argument (e.g. `1h` for Ice Ih, `4` for Ice IV): `genice3 1h > ice.gro`

Version 3.0b5

For **usage**, **ice structures**, **output formats**, **water models**, **guest molecules**, and the full manual, see the [documentation](https://genice-dev.github.io/GenIce3).

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

[Try GenIce3 on Google Colaboratory](https://colab.research.google.com/github/genice-dev/GenIce3/blob/main/API.ipynb).

## Requirements

- networkx >=2.0.dev20160901144005
- numpy >=2.0
- pairlist >=0.6.4
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

## References

See the [manual → References](https://genice-dev.github.io/GenIce3/references.html) for the full reference list (generated from `citations.yaml`).

## Citation

If you use GenIce in your work, please cite as in [CITATION.cff](CITATION.cff) or:

> M. Matsumoto, T. Yagasaki, and H. Tanaka, "GenIce: Hydrogen-Disordered Ice Generator", _J. Comput. Chem._ **39**, 61-64 (2017). [DOI: 10.1002/jcc.25077](http://doi.org/10.1002/jcc.25077)

> M. Matsumoto, T. Yagasaki, and H. Tanaka, "GenIce-core: Efficient algorithm for generation of hydrogen-disordered ice structures.", _J. Chem. Phys._ **160**, 094101 (2024). [DOI:10.1063/5.0198056](https://doi.org/10.1063/5.0198056)

## How to contribute

GenIce is developed on GitHub (https://github.com/genice-dev/GenIce3). Feedback, bug fixes, and contributions are welcome.

## License

MIT License. See [LICENSE](LICENSE) for details.
