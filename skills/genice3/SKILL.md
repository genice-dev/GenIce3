---
name: genice3
description: >-
  Generate hydrogen-disordered ice and clathrate hydrate structures that obey
  the ice rules with GenIce3 (the genice3 command or its Python API), and
  export them for GROMACS, LAMMPS, CIF, and other formats. Use when the user
  needs atomic coordinates or an initial configuration of crystalline ice
  (Ih, Ic, II-XXI, ...), clathrate hydrates (sI/CS1, sII/CS2, sH, ...), or
  zeolite-like ice frameworks; wants guest molecules in hydrate cages, ions,
  H3O+/OH-, or Bjerrum defects in ice; or mentions GenIce.
license: MIT
compatibility: Requires Python 3.11 or later and the genice3 package from PyPI; installing it needs network access.
metadata:
  genice3-version: "3.0b7"
---
<!-- Generated from temp_skill/SKILL.md by scripts/build_skill.py (make skill). Do not edit. -->

# GenIce3

GenIce3 builds ice and clathrate hydrate structures whose hydrogen-bond network obeys the ice rules and whose net polarization is driven to a target (zero by default). This skill was written for GenIce3 3.0b7. If `genice3 --version` reports another version, trust the program's own `--help`, `--list`, and `NAME?` output over this file.

## 1. Make sure genice3 runs

Check with `genice3 --version`. If the command is missing, install it. When it is unclear which Python environment the user works in, ask before installing.

- Into the active virtual environment: `pip install genice3`
- Without installing anything: prefix every command with `uvx`, e.g. `uvx genice3 1h`
- As a standalone command: `pipx install genice3`

Python 3.11 or later is required. Do not install into a system or Homebrew Python; pip refuses with `externally-managed-environment`.

## 2. Look names up; never guess them

```shell
genice3 --list unitcell 2>&1    # ice phases, clathrates, zeolite frameworks
genice3 --list exporter 2>&1    # output formats
genice3 --list molecule 2>&1    # water models and guest molecules
genice3 'zeolite?'              # suboptions of one plugin (quote the ?)
genice3 CS2 -e cage_survey      # cage list as JSON; specs.cage_type is the label -g expects
```

`--list` writes to stderr. Names are case-sensitive (`A15`, not `a15`). An unknown name fails with a message listing the closest matches; use it to correct the command.

## 3. Build the command

```shell
genice3 UNITCELL [unit-cell options] [options] -e "EXPORTER :key value" > OUTPUT
```

- Coordinates go to stdout and the log to stderr, so always redirect stdout to a file.
- Always pass `--seed N`; otherwise each run gives a different proton arrangement.
- Supercell: `--rep 2 2 2` (or `--replication_matrix` with 9 integers).
- Unit-cell options follow the unit-cell name: `genice3 zeolite --code LTA`, `genice3 6 --density 1.00`.
- The water model is an exporter suboption, not a top-level flag: `-e "gromacs :water_model tip4p"`.
- Clathrate guests: run `-e cage_survey` first and read the `cage_type` labels. Then fill cages by type with `-g A16=uathf` (mixtures: `-g "A12=co2*0.6+me*0.4"`) or a single cage by index with `-G 0=me`.
- Ions: `-a`/`-c INDEX=ION` put ions on unit-cell sites (repeated in every replica); `-A`/`-C INDEX=ION` replace one water molecule of the supercell. The numbers of cations and anions must be equal, otherwise the program may not terminate.
- Many settings: write a YAML file and run `genice3 -Y config.yaml`; command-line options override it. See [reference/cli.md](reference/cli.md).

Typical commands:

```shell
genice3 1h --rep 4 4 4 --seed 1 -e "gromacs :water_model tip4p" > ice1h.gro
genice3 CS1 --rep 2 2 2 --seed 1 -g A12=me -g A14=me -e "gromacs :water_model tip4p" > cs1.gro
genice3 CS2 --seed 1 -g A16=uathf -G 0=me -e lammps > cs2.lammps
genice3 1h --rep 4 4 4 --seed 1 --pol_loop_2 10000 --target_polarization 0 0 40 > polarized.gro
```

## 4. Use the Python API when the CLI cannot do it

- H3O+ / OH- (`add_spot_hydronium`, `add_spot_hydroxide`) and Bjerrum L/D defects (`add_bjerrum_L`, `add_bjerrum_D`) exist only in the API. See [reference/api/topological_defects.md](reference/api/topological_defects.md).
- Also prefer the API to place things by coordinate, to write one structure in several formats, or to read the hydrogen-bond graph and molecular orientations.

```python
import numpy as np
from genice3.genice import GenIce3
from genice3.plugin import Exporter

genice = GenIce3(replication_matrix=np.diag([2, 2, 2]), seed=42)
genice.set_unitcell("1h")   # unit-cell options as keywords: set_unitcell("zeolite", code="LTA")
with open("ice.gro", "w") as f:
    Exporter("gromacs").dump(genice, file=f, water_model="tip4p")
```

## 5. Check the result and report it

- On a nonzero exit status, read the `ERROR:` line on stderr; it says what to change. With `--log-format json` (or `GENICE_LOG_FORMAT=json`), look for an NDJSON line with `"event":"run.error"` instead.
- Confirm the output file is not empty. In a `.gro` file the second line is the number of atoms.
- Tell the user which seed was used, and that the structure obeys the ice rules but is **not energy-minimized**: it must be relaxed with the intended force field before a production run.
- If the structure will be used in a publication, point the user to [reference/citation.md](reference/citation.md).

## Reference files

Read only the file the task needs.

| File | Read it for |
| --- | --- |
| [reference/overview.md](reference/overview.md) | Concepts, entry points, and common error messages with remedies |
| [reference/cli.md](reference/cli.md) | Every CLI option and the YAML configuration file |
| [reference/basics.md](reference/basics.md) | Replication, density, seeds, and polarization |
| [reference/unitcells.md](reference/unitcells.md) | Catalogue of unit cells and their suboptions |
| [reference/clathrate-hydrates.md](reference/clathrate-hydrates.md) | Cage types, mixed occupancy, `cage_survey` |
| [reference/guest-molecules.md](reference/guest-molecules.md) | Built-in guest molecules |
| [reference/water-models.md](reference/water-models.md) | Built-in water models |
| [reference/output-formats.md](reference/output-formats.md) | Exporters and their suboptions |
| [reference/doping-and-defects.md](reference/doping-and-defects.md) | Unit-cell ions, spot ions, and defects |
| [reference/plugins.md](reference/plugins.md) | Writing a new unit cell, molecule, or exporter plugin |
| [reference/citation.md](reference/citation.md) | How to cite GenIce |
| `reference/api/*.md` | Python API examples: `basic`, `polarization`, `guest_occupancy`, `doping`, `topological_defects`, `cif_io`, `unitcell_transform`, `exotic_ice` |

The full manual is at https://genice-dev.github.io/GenIce3.
