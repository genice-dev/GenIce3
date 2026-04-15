**Exotic / nonstandard ice structures**.

- `17_cylindrical_ice.py`  
  - Generate a cylindrical (nanotube-like) hydrogen-ordered ice using the `prism` unitcell with chiral/axial vectors and export it in GROMACS format.

---

## Sample code

### 17_cylindrical_ice

[`17_cylindrical_ice.py`](https://github.com/genice-dev/GenIce3/blob/main/examples/api/exotic_ice/17_cylindrical_ice.py) | [`17_cylindrical_ice.sh`](https://github.com/genice-dev/GenIce3/blob/main/examples/api/exotic_ice/17_cylindrical_ice.sh) | [`17_cylindrical_ice.yaml`](https://github.com/genice-dev/GenIce3/blob/main/examples/api/exotic_ice/17_cylindrical_ice.yaml)

=== "17_cylindrical_ice.py"

    ```python
    from genice3.genice import GenIce3
    from genice3.plugin import Exporter
    
    # Corresponding command:
    # python3 -m genice3.cli.genice prism \
    #   --circum 6 1 \
    #   --axial -2 10 \
    #   --x f \
    #   --y a \
    #   --exporter gromacs :water_model 4site \
    #   --seed 42
    genice = GenIce3(seed=42)
    genice.set_unitcell(
        "prism",
        circum=(6, 1),
        axial=(-2, 10),
        x="f",
        y="a",
    )
    
    Exporter("gromacs").dump(genice, water_model="4site")
    ```

=== "17_cylindrical_ice.sh"

    ```bash
    #!/bin/bash
    
    python3 -m genice3.cli.genice prism \
      --circum 6 1 \
      --axial -2 10 \
      --x f \
      --y a \
      --exporter gromacs :water_model 4site \
      --seed 42
    ```

=== "17_cylindrical_ice.yaml"

    ```yaml
    # Run with GenIce3: genice3 --config 17_cylindrical_ice.yaml
    # Generated from 17_cylindrical_ice.sh
    
    unitcell: prism
    circum:
      - 6
      - 1
    axial:
      - -2
      - 10
    x: f
    y: a
    exporter:
      gromacs:
        water_model: 4site
    seed: 42
    ```
