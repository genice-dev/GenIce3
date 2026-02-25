This directory contains examples for **extending or transforming the unit cell**.

- `10_extend_unitcell.py`  
  - Use `replication_matrix` to extend the unit cell and build a larger supercell.

---

## Sample code

### 10_extend_unitcell

[`10_extend_unitcell.py`](https://github.com/genice-dev/GenIce3/blob/main/examples/api/unitcell_transform/10_extend_unitcell.py) | [`10_extend_unitcell.sh`](https://github.com/genice-dev/GenIce3/blob/main/examples/api/unitcell_transform/10_extend_unitcell.sh) | [`10_extend_unitcell.yaml`](https://github.com/genice-dev/GenIce3/blob/main/examples/api/unitcell_transform/10_extend_unitcell.yaml)

=== "10_extend_unitcell.py"

    ```python
    #!/usr/bin/env python3
    """
    拡大胞を新たに単位胞とする unitcell プラグインを出力する例。
    
    対応する CLI: examples/api/10_extend_unitcell.sh
    対応する YAML: examples/api/10_extend_unitcell.yaml
    
    生成された A15e.py は、rep=1 1 1 で同じ構造を再現する unitcell プラグインです。
    """
    
    from pathlib import Path
    
    from genice3.genice import GenIce3
    from genice3.plugin import safe_import
    
    # A15 単位胞、複製行列で拡大
    unitcell = safe_import("unitcell", "A15").UnitCell()
    genice = GenIce3(unitcell=unitcell)
    genice.replication_matrix = [[1, 1, 0], [-1, 1, 0], [0, 0, 1]]
    
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
