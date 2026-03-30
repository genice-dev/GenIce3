# Example: GRO to PDB and analysis via MDAnalysis

This category is included in **`API.ipynb`** through the `CATEGORIES` list in `scripts/build_api_notebook.py` (run `make api-notebook`). In the notebook, install **`MDAnalysis`** and **`matplotlib`** using the **Optional: MDAnalysis** cell after **Installation**, then run **Setup** and the cells below.

**`MDAnalysis`** and **`matplotlib`** (for plotting) are **not** core dependencies of GenIce3. Install them only when you use the scripts here, for example:

- From the repository root (recommended): `pip install ".[mdanalysis]"`
- If you installed `genice3` from PyPI: `pip install "genice3[mdanalysis]"`
- Standalone: `pip install MDAnalysis matplotlib`
- One-line list for `examples/api`: `pip install -r ../requirements-mdanalysis.txt` (from `examples/api`)

To use MDAnalysis as a GenIce3 **exporter** (e.g. `Exporter("pdb")`), install **[genice3-mdanalysis](https://github.com/genice-dev/genice3-mdanalysis)** separately. The examples in this repository use MDAnalysis’ standard `Universe.write` only.

## Running standalone (under `examples/api`)

After installing dependencies from the repository root, either:

```bash
# Repo root as cwd (e.g. 1h_unit.pdb written to cwd)
python examples/api/mdanalysis/15_mdanalysis.py
```

```bash
cd examples/api
make mdanalysis
```

`make mdanalysis` uses the Poetry environment’s Python from the repo root; install `MDAnalysis` into that venv first (e.g. `pip install '.[mdanalysis]'` via Poetry’s pip, or `poetry run pip install MDAnalysis`).

To enable the extra with Poetry: from the repo root, `poetry install --extras mdanalysis` (if your Poetry version reads `[project.optional-dependencies]`).
