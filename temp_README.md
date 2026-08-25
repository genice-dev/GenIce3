![Logo]({{ tool.genice.urls.logo }})

# GenIce3

{{ project.description }}

Successor of [GenIce 1](https://github.com/vitroid/GenIce) and [GenIce2](https://github.com/vitroid/GenIce2). Use this package for new work.

```shell
pip install genice3
genice3 1h > ice.gro
```

Python 3.11 or later. Output obeys the ice rules and a chosen net polarization (default zero); it is not energy-minimized. Relax with the intended force field before a production run.

**Manual:** [genice-dev.github.io/GenIce3](https://genice-dev.github.io/GenIce3)  
**For AI assistants:** [for-ai-assistants](https://genice-dev.github.io/GenIce3/for-ai-assistants/) · [llms.txt](https://genice-dev.github.io/GenIce3/llms.txt)

Version {{ version }}

## New in GenIce3

{% include 'templates/new-in-genice3.md' %}

## Demo

[Try GenIce3 on Google Colaboratory](https://colab.research.google.com/github/genice-dev/GenIce3/blob/main/API.ipynb).

## Requirements

{% for item in tool.poetry.dependencies %}- {{ item }} {{ tool.poetry.dependencies[item] }}
{% endfor %}

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

GenIce is developed on GitHub ({{ tool.genice.urls.repository }}). Feedback, bug fixes, and contributions are welcome.

## License

MIT License. See [LICENSE](LICENSE) for details.
