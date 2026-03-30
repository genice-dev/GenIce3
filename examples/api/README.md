**API-level examples** for GenIce3.  
Each subdirectory groups examples by topic, showing how to call GenIce3 from Python.

## Example categories

| Directory | Description |
|-----------|-------------|
| [basic](basic.md) | Basic usage (reactive properties, simple structure generation) |
| [cif_io](cif_io.md) | Reading from and writing to CIF files |
| [doping](doping.md) | Ionic substitution and group (cation group) doping |
| [guest_occupancy](guest_occupancy.md) | Guest placement and cage survey for clathrate hydrates |
| [polarization](polarization.md) | Polarization and dipole optimization (`target_pol`, `pol_loop_1`) |
| [unitcell_transform](unitcell_transform.md) | Extending the unit cell (`replication_matrix`) |
| [topological_defects](topological_defects.md) | Topological defects (Bjerrum, H3O⁺, OH⁻) |
| [mdanalysis](mdanalysis/README.md) | GRO → PDB via MDAnalysis (optional dependency) |
| [tools](tools.md) | Helper scripts for YAML ↔ shell conversions used by the examples |

Each subdirectory has its own `README.md` describing the example scripts it contains.

### Generated docs and notebook

- **MkDocs pages** (`docs/api-examples/<category>.md`, e.g. `polarization.md`, `mdanalysis.md`): built by `scripts/build_api_docs.py`, which concatenates each `examples/api/<category>/README.md` with a **Sample code** section (embedded `*.py` / `*.sh` / `*.yaml` in that folder). Run as part of `make docs`. No per-category switch: every subdirectory that has a `README.md` gets a page.
- **API.ipynb**: built by `scripts/build_api_notebook.py` (`make api-notebook`); categories are listed explicitly in `CATEGORIES` inside that script (includes `mdanalysis`).

## How to run

In an environment where `genice3` can be imported, you can run each `.py` file directly from the project root:

```bash
python examples/api/basic/2_simple.py
```

**Run all examples at once** (from project root):

```bash
make run-api-examples
# or
python scripts/run_api_examples.py
```

By default only `.py` files are run. To include `.sh` and/or `.yaml`:

```bash
python scripts/run_api_examples.py --sh        # .py + .sh (bash)
python scripts/run_api_examples.py --yaml      # .py + .yaml (genice3 --config)
python scripts/run_api_examples.py --all       # .py + .sh + .yaml
```

List entries without running: `python scripts/run_api_examples.py --dry-run`.  
On failure, stdout/stderr are written to `run_api_examples.log`.  
Note: `doping/11_ion_group_unitcell.py` may occasionally fail due to random depolarization; re-run if needed.

Examples that need **optional pip packages** (e.g. `MDAnalysis` under `mdanalysis/`) are **not** run by default. After installing the extra (`pip install '.[mdanalysis]'` from repo root, or `pip install -r examples/api/requirements-mdanalysis.txt`), run:

```bash
python scripts/run_api_examples.py --with-optional
```

Or run one script directly (from repo root, with `genice3` on `PYTHONPATH` or installed):

```bash
pip install '.[mdanalysis]'          # once per environment
python examples/api/mdanalysis/15_mdanalysis.py
```

From `examples/api` only:

```bash
pip install -r requirements-mdanalysis.txt
make mdanalysis
```

(`make mdanalysis` uses the Poetry venv’s Python from the repo root; install the extra into that venv first.)

To generate `.sh` from YAML (or vice versa), use `tools/gen_sh_from_yaml.py` and `tools/gen_yaml_from_sh.py`.

**API.ipynb** is generated from these examples (`make api-notebook`). It includes all categories except `tools` (those scripts rely on `__file__` and are meant to be run from the command line). After **Installation**, run the **Optional: MDAnalysis** cell if you use the **Using MDAnalysis** section (`pip install MDAnalysis matplotlib` is not part of the minimal Colab install). Then run **Setup** so paths like `cif/MEP.cif` resolve correctly.
