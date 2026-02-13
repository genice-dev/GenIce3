![Logo]({{tool.genice.urls.logo}})

# GenIce3

{{tool.poetry.description}}

**Quick start:** To generate a hydrogen-disordered ice structure, use the unitcell name (e.g. `1h` for Ice Ih, `4` for Ice IV) as the first argument. Example: `genice3 1h -e gromacs > ice.gro`

Version {{version}}

## New in GenIce3

- **Command line**
  - Option syntax is now unified.
  - Options can also be read from config files.
- **API**
  - The API has been significantly improved.
- **Algorithm**
  - A reactive programming style is used; the `DependencyEngine` was developed for this purpose.
  - Once you specify the required data, the data generation pipeline is prepared and run automatically.

## Demo

GenIce3 works well in interactive environments.
[Try it](https://colab.research.google.com/github/genice-dev/GenIce3/blob/main/API.ipynb) on Google Colaboratory.

Full documentation is available at the [manual](https://genice-dev.github.io/GenIce3).

## Requirements

{% for item in tool.poetry.dependencies %}- {{item}} {{tool.poetry.dependencies[item]}}
{% endfor %}

## Installation

GenIce3 is registered on [PyPI (Python Package Index)](https://pypi.org/project/genice3/).
Install with pip:

```shell
pip3 install genice3
```

## Uninstallation

```shell
pip3 uninstall genice3
```

## Usage

{{usage}}

Give the unitcell name as the first argument (see the [Ice structures](#ice-structures) table for symbols such as `1h`, `4`, `CS2`), then options. Optional settings can be read from a YAML file with `-C path/to/config.yaml` (see the [manual](https://genice-dev.github.io/GenIce3) for the format). Use `./genice3.x` instead of `genice3` when running from the source tree.

## Examples

- To generate a 3×3×3 supercell of hydrogen-disordered ice IV (4) with TIP4P water in GROMACS
  .gro format:

  ```shell
  genice3 4 --water tip4p --rep 3 3 3 > ice4.gro
  ```

- To generate a 2×2×4 supercell of CS2 clathrate hydrate with TIP4P water and THF in the large cages (united-atom model with a dummy site) in GROMACS .gro format:

  ```shell
  genice3 CS2 -g 16=uathf6 --water tip4p --rep 2 2 4 > cs2-224.gro
  ```

## Basics

The program generates various hydrogen-disordered ice structures without defects. The total dipole moment is set to zero unless you change the depolarization behavior with `--depol_loop` or `--target_polarization`. The minimal structure (with `--rep 1 1 1`) is not always a single unit cell, because handling the hydrogen-bond network topology of very small lattices under periodic boundary conditions is difficult. Note that the generated structure is not optimized for potential energy.

- To generate a large supercell of ice Ih in CIF format,

  ```shell
  genice3 1h --rep 8 8 8 -e cif > 1hx888.cif
  ```

- To generate an ice V lattice with a different hydrogen order in CIF format, use the `-s` option to set the random seed.

  ```shell
  genice3 5 -s 1024 -e cif > 5-1024.cif
  ```

- To generate an ice VI lattice at a different density with the TIP4P water model in GROMACS format, use the `--density` option to set the density in g·cm<sup>−3</sup>, and `-e` to choose the exporter (e.g. `gromacs` or `g`).

  ```shell
  genice3 6 --density 1.00 -e gromacs --water tip4p > 6d1.00.gro
  ```

GenIce3 is modular: it loads unit cells from plugins in the `unitcell` folder, places water and guest molecules using plugins in the `molecules` folder, and writes output via plugins in the `exporter` folder. You can add your own plugins to extend GenIce3; many plugins accept options.

## Clathrate hydrates

For clathrate hydrates, you can build lattices with cages partially occupied by guest molecules.

- To generate a CS1 clathrate hydrate with TIP4P water and CO₂ in GROMACS .gro format (60% of small cages filled with CO₂, 40% with methane):

  ```shell
  genice3 CS1 -g 12=co2*0.6+me*0.4 -g 14=co2 --water tip4p > cs1.gro
  ```

- To generate a CS2 clathrate hydrate with TIP5P water, THF in the large cages, and methane in one small cage: first run `genice3` without guest options:

  ```shell
  genice3 CS2 > CS2.gro
  ```

  The cage list will be printed, for example:

  ```text
  INFO   Cage types: ['12', '16']
  INFO   Cage type 12: {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179, 180, 181, 182, 183}
  INFO   Cage type 16: {136, 137, 138, 139, 140, 141, 142, 143, 16, 17, 18, 19, 20, 21, 22, 23, 160, 161, 162, 163, 164, 165, 166, 167, 40, 41, 42, 43, 44, 45, 46, 47, 184, 185, 186, 187, 188, 189, 190, 191, 64, 65, 66, 67, 68, 69, 70, 71, 88, 89, 90, 91, 92, 93, 94, 95, 112, 113, 114, 115, 116, 117, 118, 119}
  ```

  This shows two cage types, `12` and `16`. To fill type `16` with THF and put methane in cage `0` of type `12`:

  ```shell
  genice3 CS2 -g 16=uathf -G 0=me > CS2.gro
  ```

Only a few guest molecules are included by default; you can add more by writing a plugin. Here is an example for ethylene oxide.

```python
import numpy as np
import genice3.molecule

class Molecule(genice3.molecule.Molecule):
    def __init__(self):
        # United-atom EO model with a dummy site
        LOC = 0.1436 # nm
        LCC = 0.1472 # nm

        Y = (LOC**2 - (LCC/2)**2)**0.5

        sites = np.array([[ 0.,    0., 0. ],
                          [-LCC/2, Y,  0. ],
                          [+LCC/2, Y,  0. ],])

        mass = np.array([16,14,14])
        # center of mass
        CoM = mass @ self.sites / np.sum(mass)
        sites -= CoM

        atoms  = ["O","C","C"]
        labels = ["Oe","Ce","Ce"]
        name   = "EO"
        super().__init__(sites=sites, labels=labels, name=name, is_water=is_water)
```

Save this as `eo.py` in a `molecules` folder in your current directory.

_Note:_ Multiple occupancy is not supported. To model it, use a virtual molecule that represents several molecules.

## Doping ions

Small ions can replace water molecules. Use the `-a` (spot_anion) and `-c` (spot_cation) options to assign anions and cations to specific water sites.

The following places Na⁺ at water 0 and Cl⁻ at water 1 in the replicated lattice; hydrogen bonds around the ions are adjusted accordingly.

```shell
genice3 CS2 -c 0=Na -a 1=Cl > CS2.gro
```

_Note 1:_ The number of cations and anions must be equal, or the ice rule cannot be satisfied and the program may not terminate.

_Note 2:_ Protonic defects (H<sub>3</sub>O<sup>+</sup> and OH<sup>−</sup>) are not yet implemented.

<!-- ## Semiclathrate hydrates

_Under construction, sorry._

### Placement of a tetrabutylammonium ion (testing)

Assume the water molecule to be replaced by the TBA nitrogen has index 0. Place the nitrogen as a cation and replace water molecule 2 with the counter-ion Br.

```shell
genice3 HS1 -c 0=N -a 2=Br > HS1.gro
```

Example output:

```
INFO   Hints:
INFO     Cage types: ['12', '14', '15']
INFO     Cage type 12: {0, 1, 2, 3, 4, 5}
INFO     Cage type 14: {8, 9, 6, 7}
INFO     Cage type 15: {10, 11, 12, 13}
...
INFO Stage7: Arrange guest atoms.
INFO     Cages adjacent to dopant 2: {0, 9, 2, 13}
INFO     Cages adjacent to dopant 0: {0, 9, 2, 7}
```

The nitrogen is in cages 0, 9, 2, and 7 (their types appear in the output). Place the Bu⁻ group (the minus sign denotes the group, not a charge) in those cages adjacent to dopant 0. (The `-H` option and exact syntax may depend on the build; see the source or plugin docs if available.)

```shell
genice3 HS1 -c 0=N -a 2=Br > HS1.gro
```

### Placement of TBAB in the lattice module

_Under preparation_

It is often easier if the semiclathrate lattice is defined with molecular ions already in place. The procedure for building such a custom module is described elsewhere. -->

## Output formats

{{exporter}}

Installing the [`genice2-mdanalysis`](https://github.com/genice-dev/genice-mdanalysis) package adds support for many formats used by molecular dynamics software. Use the `-e` (exporter) option. For example:

```shell
% pip install genice2-mdanalysis
% genice3 1c -e 'mdanalysis[1c.pdb]'
% genice3 1h -e 'mdanalysis[1h.xtc]'
```

All the supported file types are listed in the [MDAnalysis web page](https://docs.mdanalysis.org/stable/documentation_pages/coordinates/init.html#supported-coordinate-formats).

You can add custom output formats by placing exporter plugins in an `exporter` directory under the current working directory.

Ice generation runs in seven stages:

1. Cell repetition
2. Random graph generation and replication
3. Apply the ice rule
4. Depolarize
5. Orient water molecules
6. Place atoms in water molecules
7. Place atoms in guest molecules

Exporter plugins define hooks that run after each stage.

## Ice structures

{{ices}}

Names in quotation marks have not been experimentally verified.

You can add custom ice structures by placing unit-cell plugins in a `unitcell` directory. [cif2ice](https://github.com/vitroid/cif2ice) can fetch CIF files from the [IZA structure database](http://www.iza-structure.org/databases) and help you create a lattice module.

Note: Different naming conventions are used in the literature.

| CH/FI | CH  | ice | FK    | Zeo | Foam          |
| ----- | --- | --- | ----- | --- | ------------- |
| sI    | CS1 | -   | A15   | MEP | Weaire-Phelan |
| sII   | CS2 | 16  | C15   | MTN |               |
| sIII  | TS1 | -   | sigma | -   |               |
| sIV   | HS1 | -   | Z     | -   |               |
| sV    | HS2 | -   | \*    | -   |               |
| sVII  | CS4 | -   | \*    | SOD | Kelvin        |
| sH    | HS3 | -   | \*    | DOH |               |
| C0    | -   | 17  | \*    | -   |               |
| C1    | -   | 2   | \*    | -   |               |
| C2    | -   | 1c  | \*    | -   |               |

FI: Filled ices; CH: Clathrate hydrates; FK:Frank-Kasper duals; Zeo: Zeolites; Foam: foam crystals (Weaire 1994).

-: No correspondence; \*: Non-FK types.

To request new ice structures, contact [vitroid@gmail.com](mailto:vitroid@gmail.com).

## Water models

Select a water model with the `--water` option.

{{waters}}

## Guest molecules

{{guests}}

You can add custom guest molecules by placing plugins in a `molecules` directory in the current working directory.

## Extra plugins

Additional plugins are available on the Python Package Index (PyPI). For example, to install the RDF plugin and compute radial distribution functions:

```shell
pip install genice2-rdf
```

```shell
genice3 TS1 -e _RDF > TS1.rdf.txt
```

<!-- ## Output and analysis plugins

Analysis plugin is a kind of output plugin (specified with -f option).

| pip name                                                             | GenIce3 option         | Description                                                                                                         | output format                               | requirements              |
| -------------------------------------------------------------------- | ---------------------- | ------------------------------------------------------------------------------------------------------------------- | ------------------------------------------- | ------------------------- |
| [`genice2-cage`](https://github.com/vitroid/genice-cage)             | `-f _cage`             | Detect cages and quasi-polyhedra (vitrites).                                                                        | text, json, gromacs                         | `cycless`                 |
| [`genice2-rdf`](https://github.com/vitroid/genice-rdf)               | `-f _RDF`              | Radial distribution functions.                                                                                      | text                                        |                           |
| [`genice2-svg`](https://github.com/vitroid/genice-svg)               | `-f svg`<br />`-f png` | 2D graphics in SVG format.<br /> ... in PNG format.                                                                 | SVG<br />PNG                                | `svgwrite`                |
| [`genice2-twist`](https://github.com/vitroid/genice-twist)           | `-f twist`             | Calculate the twist order parameter (and visualize) [Matsumoto 2019]                                                | text (@BTWC)<br />SVG<br />PNG <br />yaplot | `twist-op`, `genice2-svg` |
| [`genice2-mdanalysis`](https://github.com/vitroid/genice-mdanalysis) | `-f mdanalysis`        | Output the atoms in various file formats that are served by [MDAnalysis](https://github.com/MDAnalysis/mdanalysis). | text, binary                                | `mdanalysis`              | -->

<!-- ## Input plugins

Input plugins (unitcell plugins) construct a crystal structure on demand.

| pip name                                               | GenIce3 usage                                       | Description                                                                       | requirements |
| ------------------------------------------------------ | --------------------------------------------------- | --------------------------------------------------------------------------------- | ------------ |
| [`genice2-cif`](https://github.com/vitroid/genice-cif) | `genice3 cif[ITT.cif]`<br /> `genice3 zeolite[ITT]` | Read a local CIF file as an ice structure.<br />Read a structure from Zeolite DB. | `cif2ice`    | -->

## References

See [references.md](references.md) for the full reference list.

## Algorithms and citation

If you use GenIce in your work, please cite as described in [CITATION.cff](CITATION.cff) or the papers below.

The algorithms for generating depolarized, hydrogen-disordered ice are described in the following papers:

> M. Matsumoto, T. Yagasaki, and H. Tanaka,"GenIce: Hydrogen-Disordered
> Ice Generator", _J. Comput. Chem._ **39**, 61-64 (2017). [DOI: 10.1002/jcc.25077](http://doi.org/10.1002/jcc.25077)

```bibtex
@article{Matsumoto:2017bk,
    author = {Matsumoto, Masakazu and Yagasaki, Takuma and Tanaka, Hideki},
    title = {GenIce: Hydrogen-Disordered Ice Generator},
    journal = {Journal of Computational Chemistry},
    volume = {39},
    pages = {61-64},
    year = {2017}
}
```

> M. Matsumoto, T. Yagasaki, and H. Tanaka, “GenIce-core: Efficient algorithm for generation of hydrogen-disordered ice structures.”, _J. Chem. Phys._ **160**, 094101 (2024). [DOI:10.1063/5.0198056](https://doi.org/10.1063/5.0198056)

```bibtex
@article{Matsumoto:2024,
    author = {Matsumoto, Masakazu and Yagasaki, Takuma and Tanaka, Hideki},
    title = {GenIce-core: Efficient algorithm for generation of hydrogen-disordered ice structures},
    journal = {Journal of Chemical Physics},
    volume = {160},
    pages = {094101},
    year = {2024}
}
```

## How to contribute

GenIce has been available as open source software on GitHub ({{tool.genice.urls.repository}}) since 2015.
Feedback, suggestions for improvements and enhancements, bug fixes, etc. are sincerely welcome.
Developers and test users are also welcome. If you have any ice that is publicly available but not included in GenIce, please let us know.

## License

MIT License. See [LICENSE](LICENSE) for details.
