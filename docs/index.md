# GenIce3 Manual

![Logo](https://raw.githubusercontent.com/vitroid/GenIce/develop/logo/genice-v0.png)

**GenIce3** generates hydrogen-disordered ice and clathrate hydrate structures for molecular simulation. It is the **current GenIce**. You give a unit cell name, optional replication, guests, ions, and an exporter; GenIce3 writes coordinates that obey the ice rules (GROMACS, CIF, LAMMPS, and others). It does not minimize the energy.

```shell
pip install genice3
genice3 1h > ice.gro
```

**Quick start:** `genice3 1h > ice.gro` (`1h` is Ice Ih; `4` is Ice IV).

---

## Documentation

| Section | Description |
|--------|-------------|
| [Getting started](getting-started.md) | Installation, requirements, demo, what's new in GenIce3 |
| [CLI reference](cli.md) | Command-line usage and options |
| [Basics](basics.md) | Generating ice, supercells, seed, density |
| [Clathrate hydrates](clathrate-hydrates.md) | Guest molecules, cage types, occupancy |
| [Doping and defects](doping-and-defects.md) | Ions (CLI), H₃O⁺/OH⁻ and Bjerrum defects (API) |
| [Output formats](output-formats.md) | Exporters (GROMACS, CIF, LAMMPS, etc.) and generation stages |
| [Unit cells](unitcells.md) | Table of unit cell symbols (1h, 4, CS2, CIF, …) |
| [Water models](water-models.md) | Built-in water models (exporter `water_model` suboption) |
| [Guest molecules](guest-molecules.md) | Built-in guest molecules for clathrates |
| [Plugins](plugins.md) | Extra PyPI plugins and custom unit cell / exporter / molecule plugins |
| [Changes from GenIce2](changes-from-genice2.md) | Cage survey and other changes |
| [Citation](citation.md) | How to cite GenIce |
| [Contribute](contribute.md) | How to contribute |
| [License](license.md) | MIT License |

## API examples

The [API examples](api-examples/index.md) show how to use GenIce3 from Python with embedded sample code (basic usage, CIF I/O, doping, guest occupancy, polarization, unit cell extension, topological defects).

## For AI assistants

A concise, structured overview of GenIce3 for AI/LLM systems that need to explain the project or to drive it themselves: [For AI assistants](for-ai-assistants.md). A machine-readable index of this site, in the [llms.txt](https://llmstxt.org) convention, is at [/llms.txt](llms.txt).

---

## Links

- [Repository](https://github.com/genice-dev/GenIce3)
- [Bug tracker](https://github.com/genice-dev/GenIce3/issues)
- [Try on Colaboratory](https://colab.research.google.com/github/genice-dev/GenIce3/blob/main/API.ipynb)
