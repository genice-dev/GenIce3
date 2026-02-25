# Command-line interface

## Usage

```text
Usage: genice3 [OPTIONS] UNITCELL

Options:
  -h, --help               Show this message and exit.
  -V, --version            Show the version and exit.
  -D, --debug              Enable debug mode.
  --depol_loop INTEGER     Number of iterations for the depolarization
                           optimization loop. Larger values may improve
                           the quality of the hydrogen bond network.
                           Default is 1000.
  --target_polarization FLOAT FLOAT FLOAT
                           Target polarization vector (three floats: Px
                           Py Pz). The dipole optimization will aim to
                           make the net polarization close to this
                           value. Example: --target_polarization 0 0 0
                           (default).
  --replication_matrix INT INT INT INT INT INT INT INT INT
                           Replication matrix as 9 integers (3x3
                           matrix). This matrix defines how the unit
                           cell is replicated to create the supercell.
                           The first row (p, q, r) specifies that the
                           new a' axis direction is represented as
                           pa+qb+rc using the original unit cell's basis
                           vectors (a, b, c). Similarly, the second row
                           (s, t, u) specifies that the b' axis
                           direction is sa+tb+uc, and the third row
                           defines the c' axis. For example,
                           --replication_matrix 0 1 0 1 0 0 0 0 1 swaps
                           the a and b axes of the unit cell. Another
                           example, --replication_matrix 1 1 0 1 -1 0 0
                           0 1 transforms the unit cell such that a'=a+b
                           and b'=a-b. If not specified,
                           replication_factors is used instead.
  --rep, --replication_factors INT INT INT
                           Repeat the unit cell along a, b, and c axes.
                           For example, --rep 2 2 2 creates a 2x2x2
                           supercell. This is a convenient shortcut for
                           diagonal replication matrices.
  -s, --seed INTEGER       Random seed for guest molecule placement and
                           other stochastic processes. Using the same
                           seed will produce reproducible results.
  -e, --exporter TEXT      Exporter plugin name (e.g., 'gromacs' or
                           'gromacs[options]').
  -g, --guest TEXT         Specify guest molecules for each cage type.
                           Format: CAGE_LABEL=GUEST_SPEC, e.g. A12=me,
                           A12=me+et*0.5. Multiple cage types can be
                           specified with multiple -g options.
  -G, --spot_guest TEXT    Specify guest molecule at a specific cage
                           index. Format: CAGE_INDEX=MOLECULE_NAME, e.g.
                           0=me, 5=4site. Multiple spot guests can be
                           specified with multiple -G options.
  -a, --spot_anion TEXT    Specify anion replacing the specified water
                           molecule. Format: WATER_INDEX=ION_NAME, where
                           WATER_INDEX is the index of the water
                           molecule and ION_NAME is the anion name.
                           Examples: -a 13=Cl (place Cl- in cage 13), -a
                           32=Br (place Br- in cage 32). Multiple spot
                           anions can be specified with multiple -a
                           options.
  -c, --spot_cation TEXT   Specify cation replacing the specified water
                           molecule. Format: WATER_INDEX=ION_NAME, where
                           WATER_INDEX is the index of the water
                           molecule and ION_NAME is the cation name.
                           Examples: -c 13=Na (place Na+ in cage 13), -c
                           32=K (place K+ in cage 32). Multiple spot
                           cations can be specified with multiple -c
                           options.
  -C, --config PATH        Path to a YAML configuration file. Settings
                           from the config file will be overridden by
                           command-line arguments. See documentation for
                           the config file format.

Arguments:
  UNITCELL                 Unitcell plugin name (required)
```

Give the unit cell name as the first argument (see [Ice structures](ice-structures.md) for symbols such as `1h`, `4`, `CS2`), then options. Optional settings can be read from a YAML file with `-C path/to/config.yaml`. Use `./genice3.x` instead of `genice3` when running from the source tree.

## Config file

The `-C` / `--config` option loads a YAML file. Keys correspond to command-line options; values are overridden by any options given on the command line. Top-level keys include:

- **unitcell**: unit cell name (string) or `name` plus options (e.g. `shift`).
- **genice3**: options such as `seed`, `depol_loop`, `replication_factors` (or `replication_matrix`), `debug`.
- **exporter**: exporter name (string) or `name` plus options (e.g. `guest`).
- **spot_anion** / **spot_cation**: water index → ion name (see [Doping and defects](doping-and-defects.md)).

Example (minimal):

```yaml
unitcell: 1h
exporter: gromacs
genice3:
  seed: 42
  replication_factors: [2, 2, 2]
```

A longer example is in the repository: [examples/config_example.yaml](https://github.com/genice-dev/GenIce3/blob/main/examples/config_example.yaml).

## Examples

- To generate a 3×3×3 supercell of hydrogen-disordered ice IV with TIP4P water in GROMACS .gro format:

  ```shell
  genice3 4 --water tip4p --rep 3 3 3 > ice4.gro
  ```

- To generate a 2×2×4 supercell of CS2 clathrate hydrate with TIP4P water and THF in the large cages (united-atom model) in GROMACS .gro format:

  ```shell
  genice3 CS2 -g 16=uathf6 --water tip4p --rep 2 2 4 > cs2-224.gro
  ```