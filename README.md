![Logo](https://raw.githubusercontent.com/vitroid/GenIce/develop/logo/genice-v0.png)

# GenIce3

A Swiss army knife to generate hydrogen-disordered ice structures.

Version 3.0a2

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
[Try it](https://colab.research.google.com/github/genicetroid/GenIce/blob/main/jupyter.ipynb) on Google Colaboratory.

## Requirements

- networkx >=2.0.dev20160901144005
- python >=3.11,<3.14
- numpy ^2.0
- pairlist >=0.6
- cycless >=0.4.2
- graphstat >=0.3.3
- yaplotlib >=0.1.2
- openpyscad >=0.5.0
- genice-core >=1.1
- pyyaml ^6.0


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

```text
Usage: genice3 [OPTIONS] UNITCELL

Options:
  -h, --help                Show this message and exit.
  --version, -V             Show the version and exit.
  -D, --debug               Enable debug mode
  --depol_loop INTEGER      Number of iterations for the depolarization optimization loop. Larger values may improve the quality of the hydrogen bond network. Default is 1000.
  --target_polarization FLOAT FLOAT FLOAT
                           Target polarization vector (three floats: Px Py Pz). The dipole optimization will aim to make the net polarization close to this value. Example: --target_polarization 0 0 0 (default).
  --replication_matrix INT INT INT INT INT INT INT INT INT
                           Replication matrix as 9 integers (3x3 matrix). This matrix defines how the unit cell is replicated to create the supercell. The first row (p, q, r) specifies that the new a' axis direction is represented as pa+qb+rc using the original unit cell's basis vectors (a, b, c). Similarly, the second row (s, t, u) specifies that the b' axis direction is sa+tb+uc, and the third row defines the c' axis. For example, --replication_matrix 0 1 0  1 0 0  0 0 1 swaps the a and b axes of the unit cell. Another example, --replication_matrix 1 1 0  1 -1 0  0 0 1 transforms the unit cell such that a'=a+b and b'=a-b. If not specified, replication_factors is used instead.
  --rep, --replication_factors INT INT INT
                           Repeat the unit cell along a, b, and c axes. For example, --rep 2 2 2 creates a 2x2x2 supercell. This is a convenient shortcut for diagonal replication matrices.
  -s, --seed INTEGER        Random seed for guest molecule placement and other stochastic processes. Using the same seed will produce reproducible results.
  -e, --exporter TEXT       Exporter plugin name (e.g., 'gromacs' or 'gromacs[options]')
  -A, --assess_cages        Assess and report cage positions and types in the ice structure. This is useful for understanding the clathrate structure and determining where guest molecules can be placed.
  -a, --spot_anion TEXT     Specify anion replacing the specified water molecule. Format: WATER_INDEX=ION_NAME, where WATER_INDEX is the index of the water molecule and ION_NAME is the anion name. Examples: -a 13=Cl (place Cl- in cage 13), -a 32=Br (place Br- in cage 32). Multiple spot anions can be specified with multiple -a options.
  -c, --spot_cation TEXT    Specify cation replacing the specified water molecule. Format: WATER_INDEX=ION_NAME, where WATER_INDEX is the index of the water molecule and ION_NAME is the cation name. Examples: -c 13=Na (place Na+ in cage 13), -c 32=K (place K+ in cage 32). Multiple spot cations can be specified with multiple -c options.
  -C, --config PATH         Path to a YAML configuration file. Settings from the config file will be overridden by command-line arguments. See documentation for the config file format.

Arguments:
  UNITCELL                  Unitcell plugin name (required)
```

Use `./genice3.x` instead of `genice3` when running from the source tree.

## Examples

- To generate a 3×3×3 supercell of hydrogen-disordered ice IV (4) with TIP4P water in GROMACS
  .gro format:

  ```shell
  genice3 --water tip4p --rep 3 3 3  4 > ice4.gro
  ```

- To generate a 2×2×4 supercell of CS2 clathrate hydrate with TIP4P water and THF in the large cages (united-atom model with a dummy site) in GROMACS .gro format:

  ```shell
  genice3 -g 16=uathf6 --water tip4p --rep 2 2 4  CS2 > cs2-224.gro
  ```

## Basics

The program generates various hydrogen-disordered ice structures without defects. The total dipole moment is set to zero unless you specify the `--depol` option. The minimal structure (with `--rep 1 1 1`) is not always a single unit cell, because handling the hydrogen-bond network topology of very small lattices under periodic boundary conditions is difficult. Note that the generated structure is not optimized for potential energy.

- To generate a large supercell of ice Ih in XYZ format,

  ```shell
  genice3 --rep 8 8 8 1h -e xyz > 1hx888.xyz
  ```

- To generate an ice V lattice with a different hydrogen order in CIF format, use the `-s` option to set the random seed.

  ```shell
  genice3 5 -s 1024 -e cif > 5-1024.cif
  ```

- To generate an ice VI lattice at a different density with the TIP4P water model in GROMACS format, use the `--dens` option to set the density in g·cm<sup>−3</sup>.

  ```shell
  genice3 6 --dens 1.00 --format g --water tip4p > 6d1.00.gro
  ```

GenIce3 is modular: it loads unit cells from plugins in the `unitcell` folder, places water and guest molecules using plugins in the `molecules` folder, and writes output via plugins in the `exporter` folder. You can add your own plugins to extend GenIce3; many plugins accept options.

## Clathrate hydrates

For clathrate hydrates, you can build lattices with cages partially occupied by guest molecules.

- To generate a CS1 clathrate hydrate with TIP4P water and CO₂ in GROMACS .gro format (60% of small cages filled with CO₂, 40% with methane):

  ```shell
  genice3 -g 12=co2*0.6+me*0.4 -g 14=co2 --water tip4p CS1 > cs1.gro
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

Small ions can replace water molecules. Use the `--anion` and `--cation` options (or `-a` and `-c`) to assign anions and cations to specific water sites.

The following places Na⁺ at water 0 and Cl⁻ at water 1 in the replicated lattice; hydrogen bonds around the ions are adjusted accordingly.

```shell
genice3 CS2 -c 0=Na -a 1=Cl > CS2.gro
```

_Note 1:_ The number of cations and anions must be equal, or the ice rule cannot be satisfied and the program may not terminate.

_Note 2:_ Protonic defects (H<sub>3</sub>O<sup>+</sup> and OH<sup>−</sup>) are not yet implemented.

## Semiclathrate hydrates

_Under construction, sorry._

### Placement of a tetrabutylammonium ion (testing)

Assume the water molecule to be replaced by the TBA nitrogen has index 0. Place the nitrogen as a cation and replace water molecule 2 with the counter-ion Br.

```shell
genice3 HS1 -c 0=N -a 2=Br --depol=optimal > HS1.gro
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

The nitrogen is in cages 0, 9, 2, and 7 (their types appear in the output). Place the Bu⁻ group (the minus sign denotes the group, not a charge) in those cages adjacent to dopant 0.

```shell
genice3 HS1 -c 0=N -a 2=Br -H 0=Bu-:0 -H 9=Bu-:0 -H 2=Bu-:0 -H 7=Bu-:0 --depol=optimal > HS1.gro
```

The `-H` option has the form `-H (cage_id)=(group_name):(root)`, where the root is the nitrogen site given by `-c` (cation).

### Placement of TBAB in the lattice module

_Under preparation_

It is often easier if the semiclathrate lattice is defined with molecular ions already in place. The procedure for building such a custom module is described elsewhere.

## Output formats

| Name | Application | extension | water | solute | HB | remarks |
| --- | --- | --- | --- | --- | --- | --- |
| `_KG` | Kirkwood G(r) |  |  |  |  | Statistical test suite 2: Calculate G(r) for checking long-range disorder in molecular orientations. |
| `_pol` | Polarization |  |  |  | none | Calculate the polarization of the ice. |
| `cif`, `cif2` | CIF | .cif | Atomic positions | Atomic positions | none | Experimental |
| `g`, `gromacs` | [Gromacs](http://www.gromacs.org) | .gro | Atomic positions | Atomic positions | none | Default format. |
| `lammps`, `lmp` | [LAMMPS](https://www.lammps.org/) | .lammps | Atomic positions | Atomic positions | none | Yet to be verified. |
| `plotly` | [Plotly](https://plotly.com/python/) | .html | Atomic positions | Atomic positions | o | Interactive 3D visualization. |
| `y`, `yaplot` | [Yaplot](https://github.com/vitroid/Yaplot) | .yap | Atomic positions | Atomic positions | o | It renders molecular configurations and the HB network. |

Installing the [`genice2-mdanalysis`](https://github.com/vitroid/genice-mdanalysis) package adds support for many formats used by molecular dynamics software. For example:

```shell
% pip install genice2-mdanalysis
% genice3 1c -f 'mdanalysis[1c.pdb]'
% genice3 1h -f 'mdanalysis[1h.xtc]'
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

| Symbol | Description |
| ------ | ----------- |
| 0, ice0 | Metastable ice "0". [Russo 2014] |
| 11, XI, ice11 | A candidate for an antiferroelectric Ice XI #19. [Jackson 1997, Fan 2010] |
| 115_2_114, 12_1_11, 144_2_7301, 151_2_4949650, 153_2_155471, 176_2_5256, 207_1_4435, 2_2_623457, ACO, CS4, DDR, IWV, LTA, MAR, NON, PCOD8007225, PCOD8036144, PCOD8204698, PCOD8301974, PCOD8321499, PCOD8324623, SGT, SOD, engel01, engel03, engel04, engel17, engel20, engel23, engel24, engel26, engel29, engel30, engel31, engel34, sVII | Hypothetical zeolitic ice [Jeffrey 1984, Kosyakov 1999, Engel 2018, IZA Database] |
| 11alt | A layered ferroelectric Ice XI. |
| 12, XII, ice12 | Metastable high-pressure ice XII. [Lobban 1998, Koza 2000] |
| 13, XIII, ice13 | Ice XIII, a hydrogen-ordered counterpart of ice V. [Salzmann 2006] |
| 14, ice14 | Ice XIV, a partially hydrogen-ordered counterpart of ice XII. Note that it does not reproduce the occupancies (probability of occupation) of the possible hydrogen sites. [Salzmann 2006] |
| 16, CS2, MTN, XVI, ice16, sII | Ultralow-density Ice XVI. [Jeffrey 1984, Kosyakov 1999, Sikiric 2010, Falenty 2014, IZA Database] |
| 17, XVII, ice17 | Ultralow-density Ice XVII. [Smirnov 2013, Rosso 2016, Strobel 2016] |
| 1c, Ic, ice1c | Cubic type of ice I. [Vos 1993] |
| 1h, Ih, ice1h | Most popular Ice I (hexagonal). NOTE: Due to a historical reason, the crystal axes of hexagonal ice are exchanged. If you want the basal plane to be Z axis, please use 'one[hh]' instead. |
| 2, II, ice2 | Hydrogen-ordered ice II. [Kamb 1964, Londono 1988, Kamb 2003] |
| 2D3 | Trilayer honeycomb ice. |
| 2d, ice2d, ice2rect | A hydrogen-disordered counterpart of ice II. [Nakamura 2015] |
| 3, III, ice3 | Ice III. [Petrenko 1999] |
| 4, IV, ice4 | Ice IV. [Avogadro] |
| 5, V, ice5 | Monoclinic ice V (testing). |
| 5R | Ice V with orthogonal unit cell. (testing) |
| 6, VI, ice6 | Conventional high-pressure ice VI. [Petrenko 1999] |
| 6h | Half lattice of ice VI. |
| 7, VII, ice7 | Conventional high-pressure ice VII. |
| 8, VIII, ice8 | Ice VIII, a hydrogen-ordered counterpart of ice VII. [Kuhs 1998] |
| 9, IX, ice9 | Ice IX, a hydrogen-ordered counterpart of ice III. [Londono 1993] |
| A, iceA | Hypothetical ice A. [Baez 1998] |
| A15, Struct33 | Cubic Structure I of clathrate hydrate. [Sikiric 2010] |
| B, iceB | Hypothetical ice B. [Baez 1998] |
| BSV, engel05 | Hypothetical zeolitic ice of the gyroid structure. [Engel 2018, IZA Database] |
| C14, C15, C36, FK6layers, FK9layers, HS2, Hcomp, Struct01, Struct03, Struct04, Struct05, Struct06, Struct07, Struct08, Struct09, Struct10, Struct11, Struct12, Struct13, Struct14, Struct15, Struct16, Struct17, Struct18, Struct19, Struct20, Struct21, Struct22, Struct23, Struct24, Struct25, Struct26, Struct27, Struct28, Struct29, Struct30, Struct31, Struct32, Struct34, Struct35, Struct36, Struct37, Struct38, Struct39, Struct40, Struct41, Struct42, Struct43, Struct44, Struct45, Struct46, Struct47, Struct48, Struct49, Struct50, Struct51, Struct52, Struct53, Struct54, Struct55, Struct56, Struct57, Struct58, Struct59, Struct60, Struct61, Struct62, Struct63, Struct64, Struct65, Struct66, Struct67, Struct68, Struct69, Struct70, Struct71, Struct72, Struct73, Struct74, Struct75, Struct76, Struct77, Struct78, Struct79, Struct80, Struct81, Struct82, Struct83, Struct84, Z, delta, mu, psigma, sV, sigma, zra-d | A space fullerene. [Sikiric 2010] |
| CRN1, CRN2, CRN3 | A continuous random network of Sillium. [Mousseau 2001] |
| CS1, MEP, sI | Clathrate hydrates sI. [Frank 1959, Jeffrey 1984, Kosyakov 1999, IZA Database] |
| DOH, HS3, sH | Clathrate type H. |
| EMT | Hypothetical ice with a large cavity. [Liu 2019, IZA Database] |
| FAU | Hypothetical ice at negative pressure ice 'sIV'. [Huang 2017, IZA Database] |
| HS1, sIV | Hydrogen-disordered ice Ih. [Kosyakov and Polyanskaya 1999] |
| M, iceM | A hypothetical hydrogen-ordered high-density ice. [Mochizuki 2024] |
| RHO | Hypothetical ice at negative pressure ice 'sIII'. [Huang 2016, IZA Database] |
| Struct02 | A space fullerene. (I phase?) [Sikiric 2010] |
| T | Hypothetical clathrate type T. [Sikiric 2010, Karttunen 2011] |
| XIc-a | A candidate for the proton-ordered counterpart of ice Ic. The structure 'a' in Figure 1. [Geiger 2014] |
| YKD | Ice in a d-surface (testing). [Kawano 2024] |
| c0te | Filled ice C0 by Teeratchanan (Hydrogen-disordered.) (Positions of guests are supplied.) [Teeratchanan 2015] |
| c1te | Hydrogen-ordered hydrogen hydrate C1 by Teeratchanan. (Positions of guests are supplied.) [Teeratchanan 2015] |
| eleven | Ice XI w/ stacking faults. |
| i | Hypothetical ice "i". [Fennell 2005] |
| iceL | The hypothetical Ice L [Lei 2025] |
| iceMd | A hydrogen-disordered counterpart of ice M. [Mochizuki 2024] |
| iceT | Hypothetical ice T. [Hirata 2017] |
| iceT2 | Hypothetical ice T2. [Yagasaki 2018] |
| one | Ice I w/ stacking disorder. |
| oprism | Hydrogen-ordered ice nanotubes. [Koga 2001] |
| sTprime | Filled ice sT'. [Smirnov 2013] |
| xFAU | Aeroice xFAU. [Matsui 2017] |
| xdtc | A porous ice with cylindrical channels. [Matsumoto 2021] |
| 1h_unit, CIF, TS1, dtc, ice1h_unit, sIII | (Undocumented) |


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

| symbol | type |
| ------ | ---- |
| 3site, spce, tip3p | A typical 3-site model. |
| 4site | A typical 4-site model. [Jorgensen 1983, Jorgensen 1985] |
| 5site, tip4p, tip5p | A typical 5-site model. |
| 6site, NvdE | A 6-site water model. [Nada 2003] |
| 7site | A seven-site water model. [Zhao 2019] |
| physical_water | Physical model of water; Oxygen atom is on the lattice point. [Jorgensen, Chandrasekhar, Madura, Impey, Klein, J Chem Phys, 79, 926 (1983).] |
| ice | (Undocumented) |


## Guest molecules

| symbol | type |
| ------ | ---- |
| H2 | Hydrogen molecule. [https://www.britannica.com/science/hydrogen] |
| ch4, co2 | An all-atom methane model. |
| et, me | A united-atom methane model. |
| mol | Loader for MOL files (generated by MolView.org), e.g. mol[THF.mol]. |
| thf | An all-atom tetrahydrofuran (THF) model. |
| uathf | A united-atom five-site tetrahydrofuran (THF) model. |
| empty, g12, g14, g15, g16, one, uathf6 | (Undocumented) |


You can add custom guest molecules by placing plugins in a `molecules` directory in the current working directory.

# Extra plugins

Additional plugins are available on the Python Package Index (PyPI). For example, to install the RDF plugin and compute radial distribution functions:

```shell
pip install genice2-rdf
```
```shell
genice3 TS1 -f _RDF > TS1.rdf.txt
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

- [Avogadro] Avogadro https://github.com/cryos/avogadro/blob/master/crystals/ice/H2O-Ice-IV.cif
- [Baez 1998] 
BÁEZ, Luis A. and CLANCY, Paulette, 1995, Phase equilibria in extended simple point charge ice‐water systems. The Journal of Chemical Physics [online]. 8 December 1995. Vol. 103, no. 22, p. 9744–9755. DOI 10.1063/1.469938. Available from: http://dx.doi.org/10.1063/1.469938

- [Cockayne 1995] 
COCKAYNE, Eric, 1995. Dense quasiperiodic decagonal disc packing. Physical Review B [online]. 1 June 1995. Vol. 51, no. 21, p. 14958–14961. DOI 10.1103/physrevb.51.14958. Available from: http://dx.doi.org/10.1103/PhysRevB.51.14958

- [Engel 2018] 
ENGEL, Edgar A., ANELLI, Andrea, CERIOTTI, Michele, PICKARD, Chris J. and NEEDS, Richard J., 2018, Mapping uncharted territory in ice from zeolite networks to ice structures. Nature Communications [online]. 5 June 2018. Vol. 9, no. 1. DOI 10.1038/s41467-018-04618-6. Available from: http://dx.doi.org/10.1038/s41467-018-04618-6

- [Frank 1959] 
FRANK, F. C. and KASPER, J. S., 1959, Complex alloy structures regarded as sphere packings. II. Analysis and classification of representative structures. Acta Crystallographica [online]. 10 July 1959. Vol. 12, no. 7, p. 483–499. DOI 10.1107/s0365110x59001499. Available from: http://dx.doi.org/10.1107/S0365110X59001499

- [Falenty 2014] 
FALENTY, Andrzej, HANSEN, Thomas C. and KUHS, Werner F., 2014, Formation and properties of ice XVI obtained by emptying a type sII clathrate hydrate. Nature [online]. December 2014. Vol. 516, no. 7530, p. 231–233. DOI 10.1038/nature14014. Available from: http://dx.doi.org/10.1038/nature14014

- [Fan 2010] Xiaofeng Fan, Dan Bing, Jingyun Zhang, Zexiang Shen, Jer-Lai Kuo,  Computational Materials Science 49 (2010) S170–S175.
- [Fennell 2005] 
FENNELL, Christopher J. and GEZELTER, J. Daniel, 2005, Computational Free Energy Studies of a New Ice Polymorph Which Exhibits Greater Stability than Ice Ih. Journal of Chemical Theory and Computation [online]. 30 April 2005. Vol. 1, no. 4, p. 662–667. DOI 10.1021/ct050005s. Available from: http://dx.doi.org/10.1021/ct050005s

- [Geiger 2014] 
GEIGER, Philipp, DELLAGO, Christoph, MACHER, Markus, FRANCHINI, Cesare, KRESSE, Georg, BERNARD, Jürgen, STERN, Josef N. and LOERTING, Thomas, 2014. Proton Ordering of Cubic Ice Ic: Spectroscopy and Computer Simulations. The Journal of Physical Chemistry C. Online. 13 May 2014. Vol. 118, no. 20, p. 10989–10997. DOI 10.1021/jp500324x. 

- [Hirata 2017] 
HIRATA, Masanori, YAGASAKI, Takuma, MATSUMOTO, Masakazu and TANAKA, Hideki, 2017, Phase Diagram of TIP4P/2005 Water at High Pressure. Langmuir [online]. 24 August 2017. Vol. 33, no. 42, p. 11561–11569. DOI 10.1021/acs.langmuir.7b01764. Available from: http://dx.doi.org/10.1021/acs.langmuir.7b01764

- [Hirsch 2004] Hirsch, T. K. & Ojamäe, L. Quantum-Chemical and Force-Field Investigations of Ice Ih: Computation of Proton-Ordered Structures and Prediction of Their Lattice Energies. J. Phys. Chem. B 108, 15856-15864 (2004)
- [Huang 2016] 
HUANG, Yingying, ZHU, Chongqin, WANG, Lu, CAO, Xiaoxiao, SU, Yan, JIANG, Xue, MENG, Sheng, ZHAO, Jijun and ZENG, Xiao Cheng, 2016, A new phase diagram of water under negative pressure: The rise of the lowest-density clathrate s-III. Science Advances [online]. February 2016. Vol. 2, no. 2, p. e1501010. DOI 10.1126/sciadv.1501010. Available from: http://dx.doi.org/10.1126/sciadv.1501010

- [Huang 2017] 
HUANG, Yingying, ZHU, Chongqin, WANG, Lu, ZHAO, Jijun and ZENG, Xiao Cheng, 2017, Prediction of a new ice clathrate with record low density: A potential candidate as ice XIX in guest-free form. Chemical Physics Letters [online]. March 2017. Vol. 671, p. 186–191. DOI 10.1016/j.cplett.2017.01.035. Available from: http://dx.doi.org/10.1016/j.cplett.2017.01.035

- [IZA Database] http://www.iza-structure.org/databases/
- [Jackson 1997] Jackson, S. M., V. M. Nield, R. W. Whitworth, M. Oguro, and C. C. Wilson, 1997, ‘‘Single-crystal neutron diffraction studies of the structure of ice XI,’’ J. Phys. Chem. B 101, 6142.
- [Jeffrey 1984] G. A. Jeffrey, In Inclusion Compounds; J. L. Atwood, J. E. D. Davies, D. D. MacNicol, Eds.; Academic Press: London, 1984, Vol. 1, Chap. 5.
- [Jorgensen 1983] W. L. Jorgensen, J. Chandrasekhar, J. D. Madura, R. W. Impey, and M. L. Klein, Comparison of simple potential functions for simulating liquid water, J. Chem. Phys. 79 (1983) 926-935.
- [Jorgensen 1985] W. L. Jorgensen and J. D. Madura, Temperature and size dependence for monte carlo simulations of TIP4P water, Mol. Phys. 56 (1985) 1381-1392.
- [Kamb 1964] Kamb, B.IUCr. Ice. II. A proton-ordered form of ice. Acta Cryst 17, 1437–1449 (1964).
- [Kamb 2003] Kamb, B., Hamilton, W. C., LaPlaca, S. J. & Prakash, A. Ordered Proton Configuration in Ice II, from Single‐Crystal Neutron Diffraction. J. Chem. Phys. 55, 1934–1945 (2003).
- [Karttunen 2011] 
KARTTUNEN, Antti J., FÄSSLER, Thomas F., LINNOLAHTI, Mikko and PAKKANEN, Tapani A., 2011, Structural Principles of Semiconducting Group 14 Clathrate Frameworks. Inorganic Chemistry [online]. 7 March 2011. Vol. 50, no. 5, p. 1733–1742. DOI 10.1021/ic102178d. Available from: http://dx.doi.org/10.1021/ic102178d

- [Koga 1997] 
KOGA, Kenichiro, ZENG, X. C. and TANAKA, Hideki, 1997. Freezing of Confined Water: A Bilayer Ice Phase in Hydrophobic Nanopores. Physical Review Letters [online]. 29 December 1997. Vol. 79, no. 26, p. 5262–5265. DOI 10.1103/physrevlett.79.5262. Available from: http://dx.doi.org/10.1103/PhysRevLett.79.5262

- [Koga 2001] 
KOGA, Kenichiro, GAO, G. T., TANAKA, Hideki and ZENG, X. C., 2001, Formation of ordered ice nanotubes inside carbon nanotubes. Nature [online]. August 2001. Vol. 412, no. 6849, p. 802–805. DOI 10.1038/35090532. Available from: http://dx.doi.org/10.1038/35090532

- [Kosyakov 1999] 
KOSYAKOV, V. I. and POLYANSKAYA, T. M., 1999, Using structural data for estimating the stability of water networks in clathrate and semiclathrate hydrates. Journal of Structural Chemistry [online]. March 1999. Vol. 40, no. 2, p. 239–245. DOI 10.1007/bf02903652. Available from: http://dx.doi.org/10.1007/BF02903652

- [Koza 2000] 
KOZA, M. M., SCHOBER, H., HANSEN, T., TÖLLE, A. and FUJARA, F., 2000, Ice XII in Its Second Regime of Metastability. Physical Review Letters [online]. 1 May 2000. Vol. 84, no. 18, p. 4112–4115. DOI 10.1103/physrevlett.84.4112. Available from: http://dx.doi.org/10.1103/PhysRevLett.84.4112

- [Kuhs 1998] 
KUHS, W. F., FINNEY, J. L., VETTIER, C. and BLISS, D. V., 1984, Structure and hydrogen ordering in ices VI, VII, and VIII by neutron powder diffraction. The Journal of Chemical Physics [online]. 15 October 1984. Vol. 81, no. 8, p. 3612–3623. DOI 10.1063/1.448109. Available from: http://dx.doi.org/10.1063/1.448109

- [Liu 2019] 
LIU, Yuan, HUANG, Yingying, ZHU, Chongqin, LI, Hui, ZHAO, Jijun, WANG, Lu, OJAMÄE, Lars, FRANCISCO, Joseph S. and ZENG, Xiao Cheng, 2019, An ultralow-density porous ice with the largest internal cavity identified in the water phase diagram. Proceedings of the National Academy of Sciences [online]. 10 June 2019. Vol. 116, no. 26, p. 12684–12691. DOI 10.1073/pnas.1900739116. Available from: http://dx.doi.org/10.1073/pnas.1900739116

- [Lei 2025] 
- [Lobban 1998] 
LOBBAN, C., FINNEY, J. L. and KUHS, W. F., 1998, The structure of a new phase of ice. Nature [online]. January 1998. Vol. 391, no. 6664, p. 268–270. DOI 10.1038/34622. Available from: http://dx.doi.org/10.1038/34622

- [Londono 1988] 
LONDONO, D., KUHS, W. F. and FINNEY, J. L., 1988, Enclathration of helium in ice II: the first helium hydrate. Nature [online]. March 1988. Vol. 332, no. 6160, p. 141–142. DOI 10.1038/332141a0. Available from: http://dx.doi.org/10.1038/332141a0

- [Londono 1993] 
LONDONO, J. D., KUHS, W. F. and FINNEY, J. L., 1993, Neutron diffraction studies of ices III and IX on under‐pressure and recovered samples. The Journal of Chemical Physics [online]. 15 March 1993. Vol. 98, no. 6, p. 4878–4888. DOI 10.1063/1.464942. Available from: http://dx.doi.org/10.1063/1.464942

- [Matsui 2017] 
MATSUI, Takahiro, HIRATA, Masanori, YAGASAKI, Takuma, MATSUMOTO, Masakazu and TANAKA, Hideki, 2017, Communication: Hypothetical ultralow-density ice polymorphs. The Journal of Chemical Physics [online]. 7 September 2017. Vol. 147, no. 9, p. 091101. DOI 10.1063/1.4994757. Available from: http://dx.doi.org/10.1063/1.4994757

- [Matsui 2019] 
MATSUI, Takahiro, YAGASAKI, Takuma, MATSUMOTO, Masakazu and TANAKA, Hideki, 2019, Phase diagram of ice polymorphs under negative pressure considering the limits of mechanical stability. The Journal of Chemical Physics [online]. 28 January 2019. Vol. 150, no. 4, p. 041102. DOI 10.1063/1.5083021. Available from: http://dx.doi.org/10.1063/1.5083021

- [Matsumoto 2019] 
MATSUMOTO, Masakazu, YAGASAKI, Takuma and TANAKA, Hideki, 2019, A Bayesian approach for identification of ice Ih, ice Ic, high density, and low density liquid water with a torsional order parameter. The Journal of Chemical Physics [online]. 7 June 2019. Vol. 150, no. 21, p. 214504. DOI 10.1063/1.5096556. Available from: http://dx.doi.org/10.1063/1.5096556

- [Matsumoto 2021] 
MATSUMOTO, Masakazu, YAGASAKI, Takuma and TANAKA, Hideki, 2021, Novel Algorithm to Generate Hydrogen-Disordered Ice Structures. Journal of Chemical Information and Modeling [online]. 24 May 2021. DOI 10.1021/acs.jcim.1c00440. Available from: http://dx.doi.org/10.1021/acs.jcim.1c00440

- [Maynard-Casely 2010] 
MAYNARD-CASELY, H. E., BULL, C. L., GUTHRIE, M., LOA, I., MCMAHON, M. I., GREGORYANZ, E., NELMES, R. J. and LOVEDAY, J. S., 2010, The distorted close-packed crystal structure of methane A. The Journal of Chemical Physics [online]. 14 August 2010. Vol. 133, no. 6, p. 064504. DOI 10.1063/1.3455889. Available from: http://dx.doi.org/10.1063/1.3455889

- [Mochizuki 2014] 
MOCHIZUKI, Kenji, HIMOTO, Kazuhiro and MATSUMOTO, Masakazu, 2014, Diversity of transition pathways in the course of crystallization into ice VII. Phys. Chem. Chem. Phys. [online]. 2014. Vol. 16, no. 31, p. 16419–16425. DOI 10.1039/c4cp01616e. Available from: http://dx.doi.org/10.1039/c4cp01616e

- [Mochizuki 2024] 
MOCHIZUKI, Kenji, 2024. Hydrogen Ordering in Ice Ih Facilitates the Transition from HDA to Ice XII. The Journal of Physical Chemistry C. Online. 16 October 2024. DOI 10.1021/acs.jpcc.4c05371. 

- [Mousseau 2001] 
MOUSSEAU, Normand and BARKEMA, G.T., 2001, Fast bond-transposition algorithms for generating covalent amorphous structures. Current Opinion in Solid State and Materials Science [online]. December 2001. Vol. 5, no. 6, p. 497–502. DOI 10.1016/s1359-0286(02)00005-0. Available from: http://dx.doi.org/10.1016/S1359-0286(02)00005-0

- [Nada 2003] Nada, Hiroki, and Jan P. J. M. van der Eerden. 2003. “An Intermolecular Potential Model for the Simulation of Ice and Water near the Melting Point: A Six-Site Model of H2O.” The Journal of Chemical Physics 118 (16): 7401–13.
- [Nakamura 2015] 
NAKAMURA, Tatsuya, MATSUMOTO, Masakazu, YAGASAKI, Takuma and TANAKA, Hideki, 2015, Thermodynamic Stability of Ice II and Its Hydrogen-Disordered Counterpart: Role of Zero-Point Energy. The Journal of Physical Chemistry B [online]. 3 December 2015. Vol. 120, no. 8, p. 1843–1848. DOI 10.1021/acs.jpcb.5b09544. Available from: http://dx.doi.org/10.1021/acs.jpcb.5b09544

- [Petrenko 1999] Petrenko and Whitworth, Physics of Ice, Table 11.2.
- [Rosso 2016] 
DEL ROSSO, Leonardo, CELLI, Milva and ULIVI, Lorenzo, 2016, New porous water ice metastable at atmospheric pressure obtained by emptying a hydrogen-filled ice. Nature Communications [online]. 7 November 2016. Vol. 7, no. 1. DOI 10.1038/ncomms13394. Available from: http://dx.doi.org/10.1038/ncomms13394

- [Russo 2014] 
RUSSO, John, ROMANO, Flavio and TANAKA, Hajime, 2014, New metastable form of ice and its role in the homogeneous crystallization of water. Nature Materials [online]. 18 May 2014. Vol. 13, no. 7, p. 733–739. DOI 10.1038/nmat3977. Available from: http://dx.doi.org/10.1038/NMAT3977

- [Salzmann 2006] 
SALZMANN, C. G., 2006, The Preparation and Structures of Hydrogen Ordered Phases of Ice. Science [online]. 24 March 2006. Vol. 311, no. 5768, p. 1758–1761. DOI 10.1126/science.1123896. Available from: http://dx.doi.org/10.1126/science.1123896

- [Sikiric 2010] 
DUTOUR SIKIRIĆ, Mathieu, DELGADO-FRIEDRICHS, Olaf and DEZA, Michel, 2010, Space fullerenes: a computer search for new Frank–Kasper structures. Acta Crystallographica Section A Foundations of Crystallography [online]. 5 August 2010. Vol. 66, no. 5, p. 602–615. DOI 10.1107/s0108767310022932. Available from: http://dx.doi.org/10.1107/S0108767310022932

- [Smirnov 2013] 
SMIRNOV, Grigory S. and STEGAILOV, Vladimir V., 2013, Toward Determination of the New Hydrogen Hydrate Clathrate Structures. The Journal of Physical Chemistry Letters [online]. 9 October 2013. Vol. 4, no. 21, p. 3560–3564. DOI 10.1021/jz401669d. Available from: http://dx.doi.org/10.1021/jz401669d

- [Stampfli 1986] Stampfli, P. A dodecagonal quasi-periodic lattice in 2 dimensions. Helv. Phys. Acta 59, 1260–1263 (1986).
- [Strobel 2016] Strobel, Timothy A et al. “Hydrogen-Stuffed, Quartz-Like Water Ice.” Journal of the American Chemical Society 138.42 (2016): 13786–13789.
- [Svishchev 1996] 
SVISHCHEV, Igor M. and KUSALIK, Peter G., 1996. Quartzlike polymorph of ice. Physical Review B. Online. 1 April 1996. Vol. 53, no. 14, p. R8815–R8817. DOI 10.1103/physrevb.53.r8815. 

- [Teeratchanan 2015] 
TEERATCHANAN, Pattanasak and HERMANN, Andreas, 2015, Computational phase diagrams of noble gas hydrates under pressure. The Journal of Chemical Physics [online]. 21 October 2015. Vol. 143, no. 15, p. 154507. DOI 10.1063/1.4933371. Available from: http://dx.doi.org/10.1063/1.4933371

- [Vos 1993] 
VOS, Willem L., FINGER, Larry W., HEMLEY, Russell J. and MAO, Ho-kwang, 1993, NovelH2-H2O clathrates at high pressures. Physical Review Letters [online]. 8 November 1993. Vol. 71, no. 19, p. 3150–3153. DOI 10.1103/physrevlett.71.3150. Available from: http://dx.doi.org/10.1103/PhysRevLett.71.3150

- [Weaire 1994] 
WEAIRE, D. and FHELAN, R., 1994. The structure of monodisperse foam. Philosophical Magazine Letters [online]. November 1994. Vol. 70, no. 5, p. 345–350. DOI 10.1080/09500839408240997. Available from: http://dx.doi.org/10.1080/09500839408240997

- [Yagasaki 2018] 
YAGASAKI, Takuma, MATSUMOTO, Masakazu and TANAKA, Hideki, 2018, Phase Diagrams of TIP4P/2005, SPC/E, and TIP5P Water at High Pressure. The Journal of Physical Chemistry B [online]. 17 July 2018. Vol. 122, no. 31, p. 7718–7725. DOI 10.1021/acs.jpcb.8b04441. Available from: http://dx.doi.org/10.1021/acs.jpcb.8b04441

- [Zhao 2019] Zhao, C.-L. et al. Seven-Site Effective Pair Potential for Simulating Liquid Water. J. Phys. Chem. B 123, 4594-4603 (2019).


## Algorithms and citation

The algorithms for generating depolarized, hydrogen-disordered ice are described in the following papers:

M. Matsumoto, T. Yagasaki, and H. Tanaka,"GenIce: Hydrogen-Disordered
Ice Generator", J. Comput. Chem. 39, 61-64 (2017). [DOI: 10.1002/jcc.25077](http://doi.org/10.1002/jcc.25077)

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

M. Matsumoto, T. Yagasaki, and H. Tanaka, “GenIce-core: Efficient algorithm for generation of hydrogen-disordered ice structures.”, J. Chem. Phys. 160, 094101 (2024). [DOI:10.1063/5.0198056](https://doi.org/10.1063/5.0198056)

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

GenIce has been available as open source software on GitHub (https://github.com/vitroid/GenIce) since 2015.
Feedback, suggestions for improvements and enhancements, bug fixes, etc. are sincerely welcome.
Developers and test users are also welcome. If you have any ice that is publicly available but not included in GenIce, please let us know.
