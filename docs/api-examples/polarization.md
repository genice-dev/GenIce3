This directory contains examples for **polarization and dipole optimization**.

- `7_polarized.py`  
  - Generate a structure with a specified polarization using `target_pol` and `depol_loop`.

---

## Sample code

### 7_polarized

[`7_polarized.py`](https://github.com/genice-dev/GenIce3/blob/main/examples/api/polarization/7_polarized.py) | [`7_polarized.sh`](https://github.com/genice-dev/GenIce3/blob/main/examples/api/polarization/7_polarized.sh) | [`7_polarized.yaml`](https://github.com/genice-dev/GenIce3/blob/main/examples/api/polarization/7_polarized.yaml)

=== "7_polarized.py"

    ```python
    # 分極した氷の作り方 (1) コンストラクタで target_pol を指定
    # corresponding command: 7_polarized_1.sh または 7_polarized_1_flat.sh
    
    from logging import basicConfig, INFO
    import numpy as np
    from genice3.genice import GenIce3
    from genice3.plugin import UnitCell, Exporter
    
    basicConfig(level=INFO)
    
    genice = GenIce3(
        seed=114,
        depol_loop=1000,
        replication_matrix=np.diag([2, 2, 2]),
        target_pol=np.array([4.0, 0.0, 0.0]),
    )
    genice.unitcell = UnitCell("1h")
    
    Exporter("_pol").dump(genice)
    ```

=== "7_polarized.sh"

    ```bash
    #!/bin/bash
    # Generated from 7_polarized.yaml
    
    python3 -m genice3.cli.genice 1h \
      --rep 2 2 2 \
      --exporter _pol \
      --seed 114 \
      --depol_loop 1000 \
      --target_polarization 4 0 0
    ```

=== "7_polarized.yaml"

    ```yaml
    # Generated from 7_polarized.sh
    
    unitcell: 1h
    rep:
    - 2
    - 2
    - 2
    exporter: _pol
    seed: 114
    depol_loop: 1000
    target_polarization:
    - 4
    - 0
    - 0
    ```
