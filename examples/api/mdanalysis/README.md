# Example: GRO to PDB and analysis via MDAnalysis

This category is included in **`API.ipynb`** through the `CATEGORIES` list in `scripts/build_api_notebook.py` (run `make api-notebook`). In the notebook, install **`MDAnalysis`** and **`matplotlib`** using the **Optional: MDAnalysis** cell after **Installation**, then run **Setup** and the cells below.

**`MDAnalysis`** and **`matplotlib`** (for plotting) are **not** core dependencies of GenIce3. Install them explicitly when you use the scripts here, for example:

```bash
pip install MDAnalysis matplotlib
```

Or use the one-line list under `examples/api`:

```bash
pip install -r ../requirements-mdanalysis.txt
```

(from `examples/api`)

To use MDAnalysis as a GenIce3 **exporter** (e.g. `Exporter("pdb")`), install **[genice3-mdanalysis](https://github.com/genice-dev/genice3-mdanalysis)** separately. The examples in this repository use MDAnalysis’ standard `Universe.write` only.

## Running standalone (under `examples/api`)

After installing `MDAnalysis` and `matplotlib` in your environment, either:

```bash
# Repo root as cwd (outputs such as rdf.png / PDB go to cwd)
python examples/api/mdanalysis/15_mdanalysis.py
```

```bash
cd examples/api
make mdanalysis
```

`make mdanalysis` uses the Poetry environment’s Python from the repo root; install the packages into that venv first (e.g. `poetry run pip install MDAnalysis matplotlib`).
