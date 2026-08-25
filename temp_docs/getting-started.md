# Getting started

## Quick start

To generate a hydrogen-disordered ice structure, install the package and pass a unit cell name (e.g. `1h` for Ice Ih, `4` for Ice IV) as the first argument:

```shell
pip install genice3
genice3 1h > ice.gro
```

This is the current GenIce. Manual: [genice-dev.github.io/GenIce3](https://genice-dev.github.io/GenIce3). For AI assistants: [for-ai-assistants](https://genice-dev.github.io/GenIce3/for-ai-assistants/) · [llms.txt](https://genice-dev.github.io/GenIce3/llms.txt).

## New in GenIce3

{% include 'templates/new-in-genice3.md' %}

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
