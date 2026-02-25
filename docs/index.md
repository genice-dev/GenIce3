# GenIce3 Manual

![Logo](https://raw.githubusercontent.com/vitroid/GenIce/develop/logo/genice-v0.png)

**GenIce3** is a Swiss army knife to generate hydrogen-disordered ice structures (and related systems such as clathrate hydrates). You provide a unit cell name, optional replication and options (guests, ions, exporters), and GenIce3 produces atomic coordinates in formats suitable for molecular dynamics or visualization.

**Quick start:** `genice3 1h > ice.gro`

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
| [Ice structures](ice-structures.md) | Table of unit cell symbols (1h, 4, CS2, CIF, …) |
| [Water models](water-models.md) | Built-in water models (`--water`) |
| [Guest molecules](guest-molecules.md) | Built-in guest molecules for clathrates |
| [Plugins](plugins.md) | Extra PyPI plugins and custom unit cell / exporter / molecule plugins |
| [Changes from GenIce2](changes-from-genice2.md) | Cage survey and other changes |
| [Citation](citation.md) | How to cite GenIce |
| [Contribute](contribute.md) | How to contribute |
| [License](license.md) | MIT License |

## API examples

The [API examples](api-examples/index.md) show how to use GenIce3 from Python with embedded sample code (basic usage, CIF I/O, doping, guest occupancy, polarization, unit cell extension, topological defects).

## For AI assistants

A concise, structured overview of GenIce3 for AI/LLM systems that need to explain the project to users: [For AI assistants](for-ai-assistants.md).

---

## Links

- [Repository](https://github.com/genice-dev/GenIce3)
- [Bug tracker](https://github.com/genice-dev/GenIce3/issues)
- [Try on Colaboratory](https://colab.research.google.com/github/genice-dev/GenIce3/blob/main/API.ipynb)
