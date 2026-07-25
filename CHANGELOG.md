# Change log

Version-oriented summaries. GenIce3 entries cover the line after the GenIce2 fork (`a7e63b65`). For a full per-commit list since that point, run `make changes`. For release-candidate narrative and compatibility notes, see [RELEASE_NOTE.md](RELEASE_NOTE.md).

## GenIce3

### 3.0b6

* Require `pairlist` >= 1.0.0.

### 3.0b5

* Topological-defect examples extended; MCF connect engine integration.
* Exporter logging improvements; documentation updates.
* Removed Poisson-flux exporter and related examples from the tree.

### 3.0b4

* Documentation generation for plugins and citations; API examples refined and translated.
* Polarization: `depol_loop` renamed to `pol_loop_1`; `pol_loop_2` added; forced/target polarization support.
* Utility scripts consolidated under `scripts/` and `dev/`.
* `genice-core` version pinning and random seed passed through to the core library.
* `pyproject.toml` simplified; default max cage rings in `cage_survey` set to 16.

### 3.0b3

* Citations and README references updated (including Matsumoto 2007).
* Logging clarity improvements across modules.

### 3.0b2

* API examples and manual expanded.

### 3.0b1

* Documentation pass across `docs/`; consistency fixes.

### 3.0b0

* Beta track opened (`3.0a4` → `3.0b0`).

### 3.0a3–3.0a4

* GenIce3 package layout stabilized (`genice3` entry points, `DependencyEngine`, `@reactive`).
* CLI option syntax overhauled; YAML workflows for ions and guests.
* `assess_cages` replaced by `cage_survey` exporter; spot cation / group options introduced.
* Hydronium, hydroxide, and Bjerrum defect examples; extensive unit-cell porting and identity tests vs GenIce2.
* Configuration via YAML; CIF export; GROMACS/LAMMPS exporters; WebAPI groundwork.

## GenIce2

### 1.0.11

* Six-site water model adjusted.

### 1.0.10

* CIF-related merges and structure updates.

### 1.0.9

* Structure **sH** updated.

### 1.0.8

* Ice II reimplemented.

### 1.0.6

* Bug fix: center-of-mass calculation for four-site water models.

### 1.0.5

* Load **exyz** format.

### 1.0.3

* Improved atomic positions.

### 1.0.2

* Bug fix.

### 1.0.1

* Expanded descriptions in documentation.

### 1.0.0

* Stable 1.0 release.

## GenIce 1.0 release candidates and earlier

## 1.0RC5

* Visualization of the depolarization paths becomes an option.

## 1.0RC4

* GenIce no longer refers the files in the User global folder (.genice). Make them locally if necessary.
* The way to define cell dimension is changed (lattices/*.py).
* File loaders for analice tool are separated into a folder.
* One can specify the size of the largest ring in rings and _ringstat plugins.

## 1.0RC3

* Several exotic ices are added.

## 1.0RC2

* Load and save multiple files (analice).

## 1.0RC1

* Documents are updated.

## 1.0RC

* Some functions for common use are separated into other packages. (PairList, etc)
* Some plugins that require special libraries are separated into extra packages (vpython, cif, zeolite, svg).
* New plugin hander that enables to implement extensions in separate packages.

## 0.24

* Random noise is no logger added to the molecular positions by default. (Use --add_noise option instead.)

## 0.22 (stable, release)

* Added AnalIce.

## 0.20.2, 0.20.3

* Added --version option.
* The version number is also shown in the usage.

## 0.20.1

* Atomic unit is supported in mdview format.

## 0.19 (develop), 0.20

* Added gromacs module as a lattice module in order to load a .gro
file as an ice structure.
* Added zeolite module as a lattice mofule.
* Added cif module.
* Added `--asis` option to use GenIce for file conversion.
* Changed the default lattice repetition numbers from [2,2,2] to [1,1,1]

## 0.18

* Direct graphical rendering with vpython.
* Added polygonnal expression in yaplot output.
* Added art examples for OpenSCAD format.

## 0.17

* svg_poly module.

## 0.16

* Ring phase statistics.
* Radial Kirkwood G function.
* Some plugins accept options using brackets.
* Cell reshaper.
* Added the current working path as a searchpath for the plugins.
* Aeroice generator.
* Accept the structure that does not obey the ice rules.

## 0.15.1

* Bug fix in case the atomic number exceeds 100 000 in Gromacs format.

## 0.15

* Simulation cell-related functions are separated to a module.

## 0.14

* Adapted to NetworkX 2.

## 0.13

* Regulated the value range of Euler's angles.

## 0.12

* Aeroices are added.

## 0.11

* Added "hooks" for the formats plugin.

## 0.10.6

* Added some new ice structures.

## 0.10.5

## 0.10.4

* Bug fix for ice 5.

## 0.10.3

* Bug fix in format modules.

## 0.10.2

* Bug fix.

## 0.10.1

* Accept semiclathrates, ion doping, etc.

## 0.10.0

* Accept hydrogen-ordered ices.

## 0.1

* First release. (Jun. 25, 2015)
