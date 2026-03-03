**Extending or transforming the unit cell**

- `10_extend_unitcell.py`  
  - Use `replication_matrix` to extend the unit cell and build a larger supercell, then
    export it as a standalone unitcell plugin (Python file) via the `python` exporter.

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
    
    # A15 単位胞、複製行列で拡大
    unitcell = safe_import("unitcell", "A15").UnitCell()
    genice = GenIce3(unitcell=unitcell)
    genice.set_replication_matrix([[1, 1, 0], [-1, 1, 0], [0, 0, 1]])
    
    # python exporter で unitcell プラグインのソースを取得
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

# ice1c 単位胞、複製行列で拡大
unitcell = ice1c.UnitCell()
genice = GenIce3(unitcell=unitcell)
genice.set_replication_matrix([[2, 2, 0], [-2, 2, 0], [0, 0, 2]])

reshaped = py_exporter.supercell_as_unitcell(genice, name="ice1c_reshaped")

genice2 = GenIce3(unitcell=reshaped)
print(cage_survey.dumps(genice2))
```
