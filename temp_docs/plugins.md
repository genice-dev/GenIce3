# Plugins and extensions

## Prepared exporter plugins

The following exporter plugins are prepared for GenIce3 (install separately; compatibility may vary):

{% for p in extra_plugins %}

- **{{ p.name }}** (`pip install {{ p.package }}`){% if p.get("note") %} — {{ p.note }}{% endif %}

{% endfor %}
(List is maintained in `EXTRA.yaml` in the repository.)

<!-- ## Other extra plugins on PyPI

For example, to install the RDF plugin and compute radial distribution functions:

```shell
pip install genice2-rdf
genice3 TS1 -e _RDF > TS1.rdf.txt
``` -->

## Custom plugins

- **Unit cells**: Place unit-cell plugins in a `unitcell` directory. The [cif2ice](https://github.com/vitroid/cif2ice) tool can help create lattice modules from CIF files (e.g. from the [IZA structure database](http://www.iza-structure.org/databases)).
- **Exporters**: Place exporter plugins in an `exporter` directory under the current working directory to add custom output formats.
- **Molecules**: Place water or guest molecule plugins in a `molecule` directory in the current working directory (see [Clathrate hydrates](clathrate-hydrates.md) for an example guest plugin).

## Plugin source locations

Built-in unit cells and water/guest molecules live in the `genice3` package (`genice3/unitcell/`, `genice3/molecule/`). For developers, the source code for each plugin is in the corresponding module file; the [Ice structures](ice-structures.md) and [Water models](water-models.md) / [Guest molecules](guest-molecules.md) tables list the symbol names that correspond to those modules.
