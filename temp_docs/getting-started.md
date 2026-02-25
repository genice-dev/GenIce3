# Getting started

## Quick start

To generate a hydrogen-disordered ice structure, use the unit cell name (e.g. `1h` for Ice Ih, `4` for Ice IV) as the first argument:

```shell
genice3 1h > ice.gro
```

Full documentation is available at the [manual](https://genice-dev.github.io/GenIce3).

## New in GenIce3

-   **Command line**
    -   Option syntax is now unified.
    -   Options can also be read from config files.
-   **API**
    -   The API has been significantly improved.
    -   Python users can embed protonic (H₃O⁺, OH⁻) and Bjerrum topological defects directly into ice lattices.
-   **Algorithm**
    -   A reactive programming style is used; the `DependencyEngine` was developed for this purpose.
    -   Once you specify the required data, the data generation pipeline is prepared and run automatically.

## Demo

GenIce3 works well in interactive environments.  
[Try it](https://colab.research.google.com/github/genice-dev/GenIce3/blob/main/API.ipynb) on Google Colaboratory.

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
