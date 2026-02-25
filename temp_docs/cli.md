# Command-line interface

## Usage

{{ usage }}

Give the unit cell name as the first argument (see [Ice structures](ice-structures.md) for symbols such as `1h`, `4`, `CS2`), then options. Optional settings can be read from a YAML file with `-Y path/to/config.yaml`. Use `./genice3.x` instead of `genice3` when running from the source tree.

## Config file

The `-Y` / `--config` option loads a YAML file. Keys correspond to command-line options; values are overridden by any options given on the command line. Top-level keys include:

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
