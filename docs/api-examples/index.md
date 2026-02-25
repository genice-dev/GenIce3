This directory contains **API-level examples** for GenIce3.  
Each subdirectory groups examples by topic, showing how to call GenIce3 from Python.

## Example categories

| Directory | Description |
|-----------|-------------|
| [basic](basic.md) | Basic usage (reactive properties, simple structure generation) |
| [cif_io](cif_io.md) | Reading from and writing to CIF files |
| [doping](doping.md) | Ionic substitution and group (cation group) doping |
| [guest_occupancy](guest_occupancy.md) | Guest placement and cage survey for clathrate hydrates |
| [polarization](polarization.md) | Polarization and dipole optimization (`target_pol`, `depol_loop`) |
| [unitcell_transform](unitcell_transform.md) | Extending the unit cell (`replication_matrix`) |
| [topological_defects](topological_defects.md) | Topological defects (Bjerrum, H3O⁺, OH⁻) |
| [tools](tools.md) | Helper scripts for YAML ↔ shell conversions used by the examples |

Each subdirectory has its own `README.md` describing the example scripts it contains.

## How to run

In an environment where `genice3` can be imported, you can run each `.py` file directly from the project root:

```bash
python examples/api/basic/2_simple.py
```

For examples that use YAML configuration, you can generate the corresponding `.sh` scripts with `tools/gen_sh_from_yaml.py` and then run those shell scripts.
