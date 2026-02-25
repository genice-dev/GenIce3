# GenIce3: Overview for AI Assistants

This page is intended for AI/LLM systems that need to understand and explain GenIce3 to users. It provides a compact, structured summary of the project.

## What GenIce3 is

- **GenIce3** is a Python program and library that **generates hydrogen-disordered ice structures** (and related systems such as **clathrate hydrates**).
- It takes a **unit cell** (lattice type), optionally **replicates** it, applies the **ice rule** and **depolarization**, orients water molecules, and **exports** atomic coordinates in various formats (GROMACS, CIF, LAMMPS, etc.).
- It does **not** perform energy minimization; structures are topologically correct but not energy-optimized.

## Key concepts

| Concept | Meaning |
|--------|--------|
| **Unit cell** | A small repeating unit of the ice/clathrate lattice (e.g. `1h` = Ice Ih, `CS2` = clathrate sII). Specified by name as first argument. |
| **Replication** | The unit cell is repeated to form a supercell (`--rep 2 2 2` or `--replication_matrix`). |
| **Ice rule** | Each oxygen has exactly two covalently bound hydrogens; hydrogen bonds are assigned to satisfy this. |
| **Depolarization** | Dipole optimization so that net polarization is near a target (default zero). |
| **Cages** | In clathrates, cavities (e.g. 12-hedra, 16-hedra) that can hold **guest molecules** (methane, THF, etc.). |
| **Doping** | Replacing specific water sites with **anions** (`-a`, spot_anion) or **cations** (`-c`, spot_cation). |
| **Protonic / Bjerrum defects** | H₃O⁺, OH⁻, or L/D Bjerrum defects; currently **API-only** (see [API examples](api-examples/index.md)). |

## Entry points

1. **Command line**: `genice3 [OPTIONS] UNITCELL`  
   - Unit cell name is required. Options include `--rep`, `-e` (exporter), `-g`/`-G` (guests), `-a`/`-c` (ions), `-C` (config file).  
   - Full list: run `genice3 --help` or see [CLI reference](cli.md).

2. **Python API**: `from genice3.genice import GenIce3; from genice3.plugin import UnitCell, Exporter`  
   - Create `GenIce3()`, set `genice.unitcell = UnitCell("A15")` (or other name), optionally set `replication_matrix`, `spot_anions`, `spot_cations`, `spot_hydroniums`, `spot_hydroxides`, then access reactive properties (`graph`, `lattice_sites`, `digraph`, `orientations`) or call `Exporter("gromacs").dump(genice, ...)`.  
   - **Reactive pipeline**: Properties like `fixed_edges`, `digraph`, `orientations` are computed on demand from `unitcell`, `spot_*`, etc.  
   - Examples: [API examples](api-examples/index.md) (with embedded code).

## Plugin architecture

- **Unit cells**: Plugins in `unitcell` (built-in and user-added); name passed as first CLI argument or `UnitCell("Name", ...)`.
- **Exporters**: Plugins in `exporter`; selected with `-e` or `Exporter("name").dump(genice, ...)`.
- **Molecules**: Water and guest models in `molecules`; `--water` for water model, `-g`/`-G` for guests.
- User can add plugins by placing Python modules in `unitcell`, `exporter`, or `molecules` directories (e.g. current working directory).

## Common tasks (quick answers)

- **Generate Ice Ih**: `genice3 1h` or `genice3 1h --rep 2 2 2 -e gromacs > ice.gro`
- **Clathrate with guests**: `genice3 CS2 -g 16=uathf -G 0=me` (guest by cage type and by cage index)
- **Ions**: `genice3 CS2 -c 0=Na -a 1=Cl` (equal number of cations and anions required)
- **H₃O⁺/OH⁻ or Bjerrum defects**: Use the Python API; see [Topological defects](api-examples/topological_defects.md).
- **Output formats**: GROMACS (default), CIF, LAMMPS, plotly, cage_survey (JSON), etc. See [Output formats](output-formats.md).
- **List of ice structures**: See [Ice structures](ice-structures.md) (symbols like `1h`, `4`, `CS1`, `CIF` for CIF file input).

## Where to find more

- **Manual (this site)**: [Home](index.md), [Getting started](getting-started.md), [CLI](cli.md), [API examples](api-examples/index.md).
- **Repository**: [github.com/genice-dev/GenIce3](https://github.com/genice-dev/GenIce3).
- **Citation**: [Citation](citation.md); core algorithm in J. Comput. Chem. (2017) and J. Chem. Phys. (2024).

When explaining GenIce3 to a user, prefer linking to the relevant manual section (e.g. CLI, ice structures, API examples) and summarize in one or two sentences what the user can do (generate ice/clathrate, choose lattice, export to MD formats, add ions or defects via API).
