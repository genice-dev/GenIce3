<!-- Generated from docs/api-examples/unitcell_transform.md by scripts/build_skill.py. Do not edit. -->

**Extending or transforming the unit cell**

## `replication_matrix` / `set_replication_matrix`

GenIce2’s `--reshape` (and GenIce3’s `set_replication_matrix`) redefines the
simulation cell by expressing new lattice vectors `(a', b', c')` as integer
linear combinations of the original `(a, b, c)`.

In the API the matrix is given **row-wise**, so each row is the coefficients of
one new vector. For example
`set_replication_matrix([[1,1,1],[1,-1,0],[1,1,-2]])` means:

- `a' = a + b + c`
- `b' = a − b`
- `c' = a + b − 2c`

which is the same as GenIce2 `--reshape 1,1,1,1,-1,0,1,1,-2`:

![Conversion from (a, b, c) to (a′, b′, c′) via replication_matrix](https://genice-dev.github.io/GenIce3/api-examples/replication_matrix.png)

(Figure from the GenIce2 documentation set / wiki materials.)

A plain repetition such as `--rep 3 2 1` is the special case
`[[3,0,0],[0,2,0],[0,0,1]]`.

- `10_extend_unitcell.py`
  - Use `set_replication_matrix` to reshape the unit cell into a supercell, then
    export it as a standalone unitcell plugin (Python file) via the `python` exporter.
  - The sample uses `[[1, 1, 0], [-1, 1, 0], [0, 0, 1]]` (rotate/expand in the
    `ab` plane; `c` unchanged).

- `14_use_reshaped_unitcell.py`
  - Use `genice3.exporter.python.supercell_as_unitcell` to turn the current supercell
    into an in‑memory `UnitCell` object (no file output), then run `cage_survey` on the
    reshaped unit cell to analyse cage positions and types.

---

## Sample code

### 10_extend_unitcell

[`10_extend_unitcell.py`](https://github.com/genice-dev/GenIce3/blob/main/examples/api/unitcell_transform/10_extend_unitcell.py) | [`10_extend_unitcell.sh`](https://github.com/genice-dev/GenIce3/blob/main/examples/api/unitcell_transform/10_extend_unitcell.sh) | [`10_extend_unitcell.yaml`](https://github.com/genice-dev/GenIce3/blob/main/examples/api/unitcell_transform/10_extend_unitcell.yaml)

=== "10_extend_unitcell.py"

    ```python
    #!/usr/bin/env python3
    """
    Example that outputs a unitcell plugin whose unit cell is a reshaped supercell.
    
    Corresponding CLI: examples/api/10_extend_unitcell.sh
    Corresponding YAML: examples/api/10_extend_unitcell.yaml
    
    The generated ``A15e.py`` is a unitcell plugin that reproduces the same structure
    with ``rep=1 1 1``.
    """
    
    from pathlib import Path
    
    from genice3.genice import GenIce3
    from genice3.plugin import safe_import
    
    # Start from the A15 unit cell and enlarge it using a replication matrix.
    unitcell = safe_import("unitcell", "A15").UnitCell()
    genice = GenIce3(unitcell=unitcell)
    genice.set_replication_matrix([[1, 1, 0], [-1, 1, 0], [0, 0, 1]])
    
    # Use the python exporter to obtain the source code of a unitcell plugin.
    exporter = safe_import("exporter", "python")
    exporter.dump(genice)
    ```

=== "10_extend_unitcell.sh"

    ```bash
    #!/bin/bash
    # Generated from 10_extend_unitcell.yaml
    
    python3 -m genice3.cli.genice A15 \
      --replication_matrix 1 1 0 -1 1 0 0 0 1 \
      --exporter python
    ```

=== "10_extend_unitcell.yaml"

    ```yaml
    # Run with GenIce3: genice3 --config 10_extend_unitcell.yaml
    # Generated from 10_extend_unitcell.sh
    
    unitcell: A15
    replication_matrix:
    - 1
    - 1
    - 0
    - -1
    - 1
    - 0
    - 0
    - 0
    - 1
    exporter: python
    ```


### 14_use_reshaped_unitcell

[`14_use_reshaped_unitcell.py`](https://github.com/genice-dev/GenIce3/blob/main/examples/api/unitcell_transform/14_use_reshaped_unitcell.py)

```python
#!/usr/bin/env python3
"""
Example that outputs a unitcell plugin whose unit cell is a reshaped supercell.

Corresponding CLI: examples/api/10_extend_unitcell.sh
Corresponding YAML: examples/api/10_extend_unitcell.yaml

The generated ``A15e.py`` is a unitcell plugin that reproduces the same structure
with ``rep=1 1 1``.
"""

from genice3.genice import GenIce3
from genice3.unitcell import ice1c
from genice3.exporter import python as py_exporter, cage_survey

# Start from the ice1c unit cell and enlarge it using a replication matrix.
unitcell = ice1c.UnitCell()
genice = GenIce3(unitcell=unitcell)
genice.set_replication_matrix([[2, 2, 0], [-2, 2, 0], [0, 0, 2]])

reshaped = py_exporter.supercell_as_unitcell(genice, name="ice1c_reshaped")

genice2 = GenIce3(unitcell=reshaped)
print(cage_survey.dumps(genice2))
```
