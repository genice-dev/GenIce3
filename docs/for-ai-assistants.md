# GenIce3: Overview for AI Assistants

This page is intended for AI/LLM systems that need to understand and explain GenIce3 to users. It provides a compact, structured summary of the project.

## What GenIce3 is

- **GenIce3** is a Python program and library that **generates hydrogen-disordered ice structures** (and related systems such as **clathrate hydrates**). It is the **current GenIce**; for new work use this package (`pip install genice3`), not GenIce 1 or GenIce2.
- It takes a **unit cell** (lattice type), optionally **replicates** it, applies the **ice rule** and **depolarization**, orients water molecules, and **exports** atomic coordinates in various formats (GROMACS, CIF, LAMMPS, etc.).
- It does **not** perform energy minimization; structures are topologically correct but not energy-optimized. Relax with the intended force field before a production run.
- Choose GenIce3 when the user wants **ice-rule-compliant coordinates** of ice or clathrate hydrates for molecular simulation. Do not guess lattice names; list them with `genice3 --list unitcell`.

## Key concepts

| Concept | Meaning |
|--------|--------|
| **Unit cell** | A small repeating unit of the ice/clathrate lattice (e.g. `1h` = Ice Ih, `CS2` = clathrate sII). Specified by name as first argument. |
| **Replication** | The unit cell is repeated to form a supercell (`--rep 2 2 2` or `--replication_matrix`). |
| **Ice rule** | Each oxygen has exactly two covalently bound hydrogens; hydrogen bonds are assigned to satisfy this. |
| **Depolarization** | Dipole optimization so that net polarization is near a target (default zero). |
| **Cages** | In clathrates, cavities (e.g. 12-hedra, 16-hedra) that can hold **guest molecules** (methane, THF, etc.). |
| **Doping** | **Unit-cell ions**: `-a`/`--anion`, `-c`/`--cation` (lattice sites). **Spot ions**: `-A`/`--spot_anion`, `-C`/`--spot_cation` (specific water in supercell). See [Doping and defects](doping-and-defects.md). |
| **Protonic / Bjerrum defects** | H₃O⁺, OH⁻, or L/D Bjerrum defects; currently **API-only** (see [API examples](api-examples/index.md)). |

## Install and verify

```shell
pip install genice3          # Python 3.11 or later
genice3 --version            # prints "genice3 3.x.y"
genice3 1h --rep 1 1 1       # smoke test: writes a .gro file to stdout
```

## Discovering valid names

Do not guess plugin names; the program will list them.

```shell
genice3 --list unitcell      # every ice / clathrate / zeolite framework, with descriptions
genice3 --list exporter      # every output format
genice3 --list molecule      # every water model and guest molecule
genice3 CS2 -e cage_survey   # the cage labels (A12, A16, ...) that -g expects, as JSON
genice3 <name>?              # the suboptions of one unit cell, in CLI, API, and YAML form
```

If a name is wrong, the error names the closest matches, so the message itself is
enough to correct the command (the following line reports how many plugins are
installed and points at `--list`):

```text
$ genice3 iceXVII
ERROR: Unknown unitcell "iceXVII". Did you mean: iceXXI, XVII, XVI, XII, VII?
```

## Entry points

1. **Command line**: `genice3 [OPTIONS] UNITCELL`  
   - Unit cell name is required. Options include `--rep`, `-e` (exporter), `-g`/`-G` (guests), `-a`/`-c` (unitcell ions), `-A`/`-C` (spot ions), `-Y` (config file).  
   - Full list: run `genice3 --help` or see [CLI reference](cli.md).

2. **Python API**: `from genice3.genice import GenIce3; from genice3.plugin import Exporter`  
   - Create `GenIce3()`, then `genice.set_unitcell("A15")` (or another name). Plugins that need options take keyword arguments on the same call: `set_unitcell("CIF", file="path.cif")`, `set_unitcell("zeolite", code="LTA")`. Assigning `genice.unitcell = UnitCell("A15")` is equivalent. Optionally set `replication_matrix`, `spot_anions`, `spot_cations`, `spot_hydroniums`, `spot_hydroxides`, then access reactive properties (`graph`, `lattice_sites`, `digraph`, `orientations`) or call `Exporter("gromacs").dump(genice, ...)`.  
   - **Reactive pipeline**: Properties like `fixed_edges`, `digraph`, `orientations` are computed on demand from `unitcell`, `spot_*`, etc.  
   - Examples: [API examples](api-examples/index.md) (with embedded code).

## Plugin architecture

- **Unit cells**: Plugins in `unitcell` (built-in and user-added); name passed as first CLI argument or `set_unitcell("Name", ...)`. Some unit cells require options: pass them as keyword arguments, e.g. `set_unitcell("CIF", file="path/to.cif")`, `set_unitcell("aeroice", length=3)` or `set_unitcell("xFAU", length=3)` (length = hexagonal prism length), `set_unitcell("zeolite", code="LTA")`. See [Unit cells](unitcells.md) for the list and suboption tables.
- **Exporters**: Plugins in `exporter`; selected with `-e` or `Exporter("name").dump(genice, ...)`.
- **Molecules**: Water and guest models in `molecules`; water model via exporter suboption (e.g. `-e "gromacs :water_model tip4p"` or config `exporter.water_model`), or in API `Exporter("gromacs").dump(genice, water_model="tip5p")`. Symbols: tip3p, tip4p, 5site/tip5p, etc. See [Water models](water-models.md). `-g`/`-G` for guests.
- User can add plugins by placing Python modules in `unitcell`, `exporter`, or `molecules` directories (e.g. current working directory).

## Common tasks (quick answers)

- **Generate Ice Ih**: `genice3 1h` or `genice3 1h --rep 2 2 2 -e gromacs > ice.gro`
- **Clathrate with guests**: `genice3 CS2 -g A16=uathf -G 0=me` (guest by cage type and by cage index; the labels are those of `-e cage_survey`, not bare numbers)
- **Ions**: `genice3 CS2 -c 0=Na -a 1=Cl` (equal number of cations and anions required)
- **Water model**: an exporter suboption, not a top-level flag: `genice3 4 -e "gromacs :water_model tip4p"`
- **Polarized sample**: `genice3 1h --rep 4 4 4 --pol_loop_2 10000 --target_polarization 0 0 40`
- **H₃O⁺/OH⁻ or Bjerrum defects**: Use the Python API; see [Topological defects](api-examples/topological_defects.md).
- **Output formats**: GROMACS (default), CIF, LAMMPS, plotly, cage_survey (JSON), etc. See [Output formats](output-formats.md).
- **List of unit cells**: `genice3 --list unitcell`, or see [Unit cells](unitcells.md) (symbols like `1h`, `4`, `CS1`, `CIF` for CIF file input).

## Common errors

| Message | Cause and remedy |
|--------|--------|
| `Unknown unitcell "..."` / `Unknown exporter "..."` | The name is not installed. The message lists near matches; `genice3 --list CATEGORY` gives all of them. Names are case-sensitive (`A15`, not `a15`). |
| `Cage type 16 is not defined. Available cage types ...` | `-g` takes the cage label, e.g. `A16`, not the number of faces. `genice3 STRUCTURE -e cage_survey` reports the labels. |
| `Unrecognized options; stopping: ...` | A flag was not consumed by the base parser, the unit cell, or the exporter. Unit-cell suboptions must follow the unit-cell name; exporter suboptions go inside `-e "name :key value"`. |
| Different structure on every run | Expected: the proton network is random. Pass `--seed N` to reproduce one. |

## Where to find more

- **Machine-readable index of this site**: [llms.txt](llms.txt), in the [llms.txt](https://llmstxt.org) convention.
- **Manual (this site)**: [Home](index.md), [Getting started](getting-started.md), [CLI](cli.md), [API examples](api-examples/index.md).
- **Repository**: [github.com/genice-dev/GenIce3](https://github.com/genice-dev/GenIce3).
- **Citation**: [Citation](citation.md); core algorithm in J. Comput. Chem. (2017) and J. Chem. Phys. (2024).

When explaining GenIce3 to a user, prefer linking to the relevant manual section (e.g. CLI, ice structures, API examples) and summarize in one or two sentences what the user can do (generate ice/clathrate, choose lattice, export to MD formats, add ions or defects via API).
