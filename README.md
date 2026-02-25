![Logo](https://raw.githubusercontent.com/vitroid/GenIce/develop/logo/genice-v0.png)

# GenIce3

A Swiss army knife to generate hydrogen-disordered ice structures.

**Quick start:** Use the unit cell name as the first argument (e.g. `1h` for Ice Ih, `4` for Ice IV): `genice3 1h > ice.gro`

Version 3.0b0

For **usage**, **ice structures**, **output formats**, **water models**, **guest molecules**, and the full manual, see the [documentation](https://genice-dev.github.io/GenIce3).

## New in GenIce3

-   **Command line**: Option syntax unified; options can be read from config files.
-   **API**: Improved API; embed protonic (H<sub>3</sub>O<sup>+</sup>, OH<sup>−</sup>) and Bjerrum topological defects via Python.
-   **Algorithm**: Reactive pipeline with `DependencyEngine`; data generation runs automatically from your specifications.

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
- genice-core >=1.3.1
- pyyaml >=6.0
- jinja2 >=3.1.4
- cif2ice (>=0.4.1,<0.5.0)


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

See the [manual → References](https://genice-dev.github.io/GenIce3/references/) for the full reference list (generated from `citations.yaml`).

## Citation

If you use GenIce in your work, please cite as in [CITATION.cff](CITATION.cff) or:

> M. Matsumoto, T. Yagasaki, and H. Tanaka, "GenIce: Hydrogen-Disordered Ice Generator", _J. Comput. Chem._ **39**, 61-64 (2017). [DOI: 10.1002/jcc.25077](http://doi.org/10.1002/jcc.25077)

> M. Matsumoto, T. Yagasaki, and H. Tanaka, "GenIce-core: Efficient algorithm for generation of hydrogen-disordered ice structures.", _J. Chem. Phys._ **160**, 094101 (2024). [DOI:10.1063/5.0198056](https://doi.org/10.1063/5.0198056)

## How to contribute

GenIce is developed on GitHub (https://github.com/genice-dev/GenIce3). Feedback, bug fixes, and contributions are welcome.

## License

MIT License. See [LICENSE](LICENSE) for details.
