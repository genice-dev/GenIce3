**Polarization and dipole optimization**.

- `7_polarized.py`
  - Generate a structure with a specified polarization using `target_pol`, `pol_loop_1`, and `pol_loop_2`.

---

## Sample code

### 7_polarized

[`7_polarized.py`](https://github.com/genice-dev/GenIce3/blob/main/examples/api/polarization/7_polarized.py) | [`7_polarized.sh`](https://github.com/genice-dev/GenIce3/blob/main/examples/api/polarization/7_polarized.sh) | [`7_polarized.yaml`](https://github.com/genice-dev/GenIce3/blob/main/examples/api/polarization/7_polarized.yaml)

=== "7_polarized.py"

    ```python
    # How to build a polarized ice sample (1): specify target_pol in the constructor.
    # Corresponding command: 7_polarized_1.sh or 7_polarized_1_flat.sh
    
    import numpy as np
    from genice3.genice import GenIce3
    from genice3.plugin import Exporter
    
    genice = GenIce3(
        seed=114,
        pol_loop_1=1000,
        pol_loop_2=10000,
        replication_matrix=np.diag([6, 6, 6]),
        target_pol=np.array([0.0, 0.0, 72.0]),
    )
    genice.set_unitcell("one", layers="hh")
    
    Exporter("_pol").dump(genice)
    ```

=== "7_polarized.sh"

    ```bash
    #!/bin/bash
    # Generated from 7_polarized.yaml
    
    python3 -m genice3.cli.genice one \
      --layers hh \
      --rep 6 6 6 \
      --exporter _pol \
      --seed 114 \
      --pol_loop_1 1000 \
      --pol_loop_2 10000 \
      --target_polarization 0 0 72
    ```

=== "7_polarized.yaml"

    ```yaml
    # Run with GenIce3: genice3 --config 7_polarized.yaml
    # Generated from 7_polarized.sh
    
    unitcell: one
    layers: hh
    rep:
    - 6
    - 6
    - 6
    exporter: _pol
    seed: 114
    pol_loop_1: 1000
    pol_loop_2: 10000
    target_polarization:
    - 0
    - 0
    - 72
    ```
