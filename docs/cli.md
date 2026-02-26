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
  -r, --rep, --replication_factors INT INT INT
                           Repeat the unit cell along a, b, and c axes.
                           For example, --rep 2 2 2 creates a 2x2x2
                           supercell. This is a convenient shortcut for
                           diagonal replication matrices.
  -s, --seed INTEGER       Random seed for guest molecule placement and
                           other stochastic processes. Using the same
                           seed will produce reproducible results.
  -e, --exporter TEXT      Exporter plugin name (e.g. 'gromacs').
                           Exporter-specific options are given as :key
                           value after UNITCELL (e.g. gromacs
                           :water_model 4site).
  -g, --guest TEXT         Specify guest molecules for each cage type.
                           Format: CAGE_LABEL=GUEST_SPEC. Examples:
                           A12=me (single), 12=co2*0.6+me*0.4
                           (probabilistic mix; use quotes in shell: -g
                           "12=co2*0.6+me*0.4"). Both molecule*occupancy
                           (co2*0.6) and occupancy*molecule (0.6*co2)
                           are accepted. Multiple cage types with
                           multiple -g options.
  -G, --spot_guest TEXT    Specify guest molecule at a specific cage
                           index. Format: CAGE_INDEX=MOLECULE_NAME, e.g.
                           0=me, 5=4site. Multiple spot guests can be
                           specified with multiple -G options.
  -a, --anion TEXT         Anion at lattice site (unitcell-defined).
                           Passed to unitcell plugin. Format:
                           INDEX=ION_NAME (e.g. -a 3=Cl). Same as
                           unitcell suboption --anion.
  -c, --cation TEXT        Cation at lattice site (unitcell-defined).
                           Passed to unitcell plugin. Format:
                           INDEX=ION_NAME (e.g. -c 3=Na). Same as
                           unitcell suboption --cation.
  -A, --spot_anion TEXT    Specify anion replacing the specified water
                           molecule (spot doping). Format:
                           WATER_INDEX=ION_NAME. Examples: -A 13=Cl
                           (place Cl- in cage 13), -A 32=Br (place Br-
                           in cage 32). Multiple spot anions can be
                           specified with multiple -A options.
  -C, --spot_cation TEXT   Specify cation replacing the specified water
                           molecule (spot doping). Format:
                           WATER_INDEX=ION_NAME. Examples: -C 13=Na
                           (place Na+ in cage 13), -C 32=K (place K+ in
                           cage 32). Multiple spot cations can be
                           specified with multiple -C options.
  -Y, --config PATH        Path to a YAML configuration file. Settings
                           from the config file will be overridden by
                           command-line arguments. See documentation for
                           the config file format.

Arguments:
  UNITCELL                 Unitcell plugin name (required)

Unitcell options (depend on UNITCELL; some unitcell may have additional options. Pass after UNITCELL):
  --density FLOAT          Target density (e.g. g/cm³). Supported by
                           many unit cells.
  --shift X Y Z            Shift fractional coordinates. Supported by
                           many unit cells.
  --cation INDEX=ION       Cation at lattice site (unitcell-defined).
                           May support :group suboption.
  --anion INDEX=ION        Anion at lattice site (unitcell-defined).
```

Give the unit cell name as the first argument (see [Unit cells](unitcells.md) for symbols such as `1h`, `4`, `CS2`), then options. Optional settings can be read from a YAML file with `-Y path/to/config.yaml`. Use `./genice3.x` instead of `genice3` when running from the source tree.

In the CLI, the first argument is the unitcell name; all options that follow (e.g. `--rep`, `--file`, `--shift`) are passed to that unitcell. So for unitcells that take extra options (such as CIF), those options are written at the same level as the common unitcell options (e.g. `--density`, `--shift`). This is intentional and does not conflict with base-level options (e.g. `--config` is `-Y`).

## Unitcell plugins with their own options

Most unitcell plugins only use the [common unitcell options](#usage) (`--density`, `--shift`, `--anion`, `--cation`). The following plugins accept additional options; pass them after the unitcell name like any other unitcell option.

### CIF

The **CIF** unitcell builds a unit cell from a CIF file (e.g. from [cif2ice](https://github.com/vitroid/cif2ice) or structure databases). It supports the common unitcell options and:

| Option | Description |
|--------|-------------|
| `--file` | Path to the CIF file (required). |
| `--osite` | Regex or label for oxygen sites in the CIF (default: `O`). |
| `--hsite` | Regex or label for hydrogen sites. If omitted, hydrogen positions are generated by GenIce3. |

Example:

```shell
genice3 CIF --file path/to/structure.cif --osite T --rep 2 2 2 -e gromacs > out.gro
```

In a config file, use the same keys under the unitcell section, e.g. `unitcell.name: CIF`, `unitcell.file: path/to/structure.cif`, `unitcell.osite: T`.

### Zeolite

The **zeolite** unitcell fetches a zeolite framework CIF from the [IZA Structure Commission database](https://www.iza-structure.org/databases/) by 3-letter framework code, then interprets it via the same logic as the CIF unitcell. It supports the common unitcell options and:

| Option | Description |
|--------|-------------|
| `--code` | IZA 3-letter framework code (required), e.g. `LTA`, `FAU`, `MFI`. |
| `--osite` | Regex or label for tetrahedral/oxygen sites in the CIF (default: `T`; IZA uses T for degree-4 nodes). |
| `--hsite` | Regex or label for hydrogen sites. If omitted, hydrogen positions are generated by GenIce3. |

Example:

```shell
genice3 zeolite --code LTA --rep 2 2 2 -e gromacs > lta.gro
```

The plugin downloads the framework CIF from IZA (`download_cif.php`) to a temporary file and passes it to the CIF unitcell. If the IZA server layout changes, downloads may fail; in that case use a local CIF with the **CIF** unitcell and `--file` instead.

## Config file

The `-Y` / `--config` option loads a YAML file. Keys correspond to command-line options; values are overridden by any options given on the command line. Top-level keys include:

- **unitcell**: unit cell name (string) or `name` plus options (e.g. `shift`).
- **genice3**: options such as `seed`, `depol_loop`, `replication_factors` (or `replication_matrix`), `debug`.
- **exporter**: exporter name (string) or `name` plus options (e.g. `guest`, `water_model` for water model).
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

Water model is specified as the exporter suboption `:water_model` (e.g. `-e "gromacs :water_model tip4p"`). In a config file, set `exporter.water_model`.

- To generate a 3×3×3 supercell of hydrogen-disordered ice IV with TIP4P water in GROMACS .gro format:

    ```shell
    genice3 4 --rep 3 3 3 -e "gromacs :water_model tip4p" > ice4.gro
    ```

- To generate a 2×2×4 supercell of CS2 clathrate hydrate with TIP4P water and THF in the large cages (united-atom model) in GROMACS .gro format:

    ```shell
    genice3 CS2 -g 16=uathf6 --rep 2 2 4 -e "gromacs :water_model tip4p" > cs2-224.gro
    ```