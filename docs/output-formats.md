# Output formats

| Name | Application | extension | water | solute | HB | remarks |
| --- | --- | --- | --- | --- | --- | --- |
| `_KG` | Kirkwood G(r) |  |  |  |  | Statistical test suite 2: Calculate G(r) for checking long-range disorder in molecular orientations. |
| `_pol` | Polarization |  |  |  | none | Calculate the polarization of the ice. |
| `cage_survey` | JSON | .json | none | none | none | Cage positions and types (fractional coords, labels, faces). Replaces -A/--assess_cages. |
| `cif` | CIF | .cif | Atomic positions | Atomic positions | none | Experimental |
| `g`, `gromacs` | [Gromacs](http://www.gromacs.org) | .gro | Atomic positions | Atomic positions | none | Default format. |
| `lammps`, `lmp` | [LAMMPS](https://www.lammps.org/) | .lammps | Atomic positions | Atomic positions | none | Yet to be verified. |
| `plotly` | [Plotly](https://plotly.com/python/) | .html | Atomic positions | Atomic positions | o | Interactive 3D visualization. |
| `py`, `python` | Python unitcell plugin | .py | none | none | graph | Outputs a unitcell plugin where the supercell becomes the new unit cell. |
| `y`, `yaplot` | [Yaplot](https://github.com/vitroid/Yaplot) | .yap | Atomic positions | Atomic positions | o | It renders molecular configurations and the HB network. |

!!! info "MDAnalysis-based exporters"
    A GenIce3-compatible exporter for [MDAnalysis](https://www.mdanalysis.org/) and the many formats it supports is **not yet implemented**. The GenIce2 package [`genice2-mdanalysis`](https://github.com/genice-dev/genice-mdanalysis) targets GenIce2; see [Plugins](plugins.md) for prepared/planned plugins.

You can add custom output formats by placing exporter plugins in an `exporter` directory under the current working directory.

## Pipeline (Reactive / Dependency)

GenIce3 does **not** use the old GenIce2-style fixed “seven stages”. The pipeline is **reactive**: which steps run is determined automatically from the **Dependency** graph. You request outputs (e.g. coordinates, cage list); the engine runs only the tasks required to produce them. Exporter plugins register hooks that run when their inputs become available.