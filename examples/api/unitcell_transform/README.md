**Extending or transforming the unit cell**

- `10_extend_unitcell.py`  
  - Use `replication_matrix` to extend the unit cell and build a larger supercell, then
    export it as a standalone unitcell plugin (Python file) via the `python` exporter.

- `14_use_reshaped_unitcell.py`  
  - Use `genice3.exporter.python.supercell_as_unitcell` to turn the current supercell
    into an in‑memory `UnitCell` object (no file output), then run `cage_survey` on the
    reshaped unit cell to analyse cage positions and types.

