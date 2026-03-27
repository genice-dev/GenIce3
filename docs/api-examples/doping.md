**Ionic substitution and group (cation group) doping**.

CLI: Ions in the unit cell are specified by **-a / --anion** and **-c / --cation**. Spot substitutions use **-A / --spot_anion** and **-C / --spot_cation**.

- `3_doped.py`  
  - Basic usage of anion/cation substitutional doping (unitcell + spot).

- `9_ion_group.py`  
  - Attach *groups* to cations inside a unit cell.

- `11_ion_group_unitcell.py`  
  - Use `cation_groups` defined in the unit cell and expand them to the replicated supercell.

---

## Sample code

### 11_ion_group_unitcell

[`11_ion_group_unitcell.py`](https://github.com/genice-dev/GenIce3/blob/main/examples/api/doping/11_ion_group_unitcell.py) | [`11_ion_group_unitcell.sh`](https://github.com/genice-dev/GenIce3/blob/main/examples/api/doping/11_ion_group_unitcell.sh) | [`11_ion_group_unitcell.yaml`](https://github.com/genice-dev/GenIce3/blob/main/examples/api/doping/11_ion_group_unitcell.yaml)

=== "11_ion_group_unitcell.py"

    ```python
    from logging import basicConfig, INFO
    import numpy as np
    from genice3.genice import GenIce3
    from genice3.plugin import Exporter
    
    # Corresponding CLI command:
    # genice3 A15 --cation 0=N :group 1=methyl 6=methyl 3=methyl 4=methyl \
    #   --anion 2=Cl --rep 2 2 2 --exporter gromacs :water_model 4site
    
    basicConfig(level=INFO)
    
    genice = GenIce3(
        replication_matrix=np.array([[2, 0, 0], [0, 2, 0], [0, 0, 2]]),
        seed=43,
    )
    
    # Set anion/cation and cation_groups in the unit cell (group assignment for cation arms).
    genice.set_unitcell(
        "A15",
        anion={2: "Cl"},
        cation={0: "N"},
        cation_groups={0: {1: "methyl", 6: "methyl", 3: "methyl", 4: "methyl"}},
    )
    
    Exporter("gromacs").dump(
        genice,
        water_model="4site",
    )
    ```

=== "11_ion_group_unitcell.sh"

    ```bash
    #!/bin/bash
    # Generated from 11_ion_group_unitcell.yaml
    
    python3 -m genice3.cli.genice A15 --seed 43 \
      --cation 0=N :group 1=methyl 6=methyl 3=methyl 4=methyl \
      --anion 2=Cl \
      --rep 2 2 2 \
      --exporter gromacs :water_model 4site
    ```

=== "11_ion_group_unitcell.yaml"

    ```yaml
    # Run with GenIce3: genice3 --config 11_ion_group_unitcell.yaml
    # Generated from 11_ion_group_unitcell.sh
    
    unitcell: A15
    seed: 43
    cation:
      0=N:
        group:
        - 1=methyl
        - 6=methyl
        - 3=methyl
        - 4=methyl
    anion: 2=Cl
    rep:
    - 2
    - 2
    - 2
    exporter:
      gromacs:
        water_model: 4site
    ```


### 3_doped

[`3_doped.py`](https://github.com/genice-dev/GenIce3/blob/main/examples/api/doping/3_doped.py) | [`3_doped.sh`](https://github.com/genice-dev/GenIce3/blob/main/examples/api/doping/3_doped.sh) | [`3_doped.yaml`](https://github.com/genice-dev/GenIce3/blob/main/examples/api/doping/3_doped.yaml)

=== "3_doped.py"

    ```python
    from logging import basicConfig, DEBUG, INFO
    import numpy as np
    from genice3.genice import GenIce3
    from genice3.plugin import Exporter, Molecule
    
    # Corresponding CLI command:
    # genice3 "A15[shift=(0.1,0.1,0.1), anion.0=Cl, cation.6=Na, density=0.8]" \
    #   --rep 2 2 2 \
    #   --spot_anion 1=Cl --spot_anion 35=Br \
    #   --spot_cation 1=Na --spot_cation 35=K \
    #   --exporter gromacs :water_model 4site \
    #   --seed 42 --pol_loop_1 2000 -D
    
    basicConfig(level=INFO)
    
    # Create a GenIce3 instance.
    # seed: random seed.
    # pol_loop_1: number of depolarization loop iterations.
    # replication_matrix: replication matrix (here a 2x2x2 diagonal matrix).
    # spot_anions: replace specific water molecules with anions (water index -> ion name). CLI: -A / --spot_anion
    # spot_cations: replace specific water molecules with cations (water index -> ion name). CLI: -C / --spot_cation
    # Note: the GenIce3 constructor does not take a debug flag (logging level is set via basicConfig).
    genice = GenIce3(
        seed=42,
        pol_loop_1=2000,
        replication_matrix=np.array([[2, 0, 0], [0, 2, 0], [0, 0, 2]]),
        spot_anions={
            1: "Cl",
        },
        spot_cations={
            51: "Na",
        },
    )
    
    # Set the unit cell.
    # shift: shift in fractional coordinates.
    # anion: replace lattice sites in the unit cell with anions (site index -> ion name). CLI: -a / --anion
    # cation: replace lattice sites in the unit cell with cations (site index -> ion name). CLI: -c / --cation
    # density: density in g/cm³.
    # If cage information is needed, you can use Exporter("cage_survey").dump(genice, file) to output JSON.
    genice.set_unitcell(
        "A15",
        shift=(0.1, 0.1, 0.1),
        anion={15: "Cl"},
        cation={21: "Na"},
        density=0.8,
    )
    
    
    # Output using the exporter.
    Exporter("gromacs").dump(
        genice,
        water_model="4site",
    )
    ```

=== "3_doped.sh"

    ```bash
    #!/bin/bash
    # Generated from 3_doped.yaml
    
    python3 -m genice3.cli.genice A15 \
      --shift 0.1 0.1 0.1 \
      --anion 15=Cl \
      --cation 21=Na \
      --density 0.8 \
      --rep 2 2 2 \
      --exporter gromacs :water_model 4site \
      --seed 42 \
      --pol_loop_1 2000 \
      --spot_anion 1=Cl \
      --spot_cation 51=Na
    ```

=== "3_doped.yaml"

    ```yaml
    # Run with GenIce3: genice3 --config 3_doped.yaml
    # Generated from 3_doped.sh
    
    unitcell: A15
    shift:
    - 0.1
    - 0.1
    - 0.1
    anion: 15=Cl
    cation: 21=Na
    density: 0.8
    rep:
    - 2
    - 2
    - 2
    exporter:
      gromacs:
        water_model: 4site
    seed: 42
    pol_loop_1: 2000
    spot_anion: 1=Cl
    spot_cation: 51=Na
    ```


### 9_ion_group

[`9_ion_group.py`](https://github.com/genice-dev/GenIce3/blob/main/examples/api/doping/9_ion_group.py) | [`9_ion_group.sh`](https://github.com/genice-dev/GenIce3/blob/main/examples/api/doping/9_ion_group.sh) | [`9_ion_group.yaml`](https://github.com/genice-dev/GenIce3/blob/main/examples/api/doping/9_ion_group.yaml)

=== "9_ion_group.py"

    ```python
    from logging import basicConfig, DEBUG, INFO
    import numpy as np
    from genice3.genice import GenIce3
    from genice3.plugin import Exporter, Molecule
    
    # Corresponding CLI command:
    # genice3 "A15[shift=(0.1,0.1,0.1), anion.0=Cl, cation.6=Na, density=0.8]" \
    #   --rep 2 2 2 \
    #   --spot_anion 1=Cl --spot_anion 35=Br \
    #   --spot_cation 1=Na --spot_cation 35=K \
    #   --exporter gromacs :water_model 4site \
    #   --seed 42 --pol_loop_1 2000 -D
    
    basicConfig(level=INFO)
    
    # Create a GenIce3 instance.
    # seed: random seed.
    # pol_loop_1: maximum number of iterations for the first polarization convergence stage.
    # replication_matrix: replication matrix (here a 2x2x2 diagonal matrix).
    # spot_anions / spot_cations: water-molecule index -> ion name. CLI: -A / --spot_anion, -C / --spot_cation
    # spot_cation_groups: group suboption (site -> {cage ID -> group name}).
    # The nested \"ion\" key used in YAML/CLI is not needed in the Python API (it is passed as a separate argument).
    genice = GenIce3(
        seed=42,
        pol_loop_1=2000,
        replication_matrix=np.array([[2, 0, 0], [0, 2, 0], [0, 0, 2]]),
        spot_anions={1: "Cl"},
        spot_cations={51: "N"},
        spot_cation_groups={
            51: {12: "methyl", 48: "methyl", 49: "methyl", 50: "methyl"},
        },
    )
    
    # Set the unit cell.
    # anion / cation: replace lattice sites in the unit cell with ions (site index -> ion name). CLI: -a / --anion, -c / --cation
    # density: density in g/cm³.
    # If cage information is needed, you can use Exporter("cage_survey").dump(genice, file) to output JSON.
    genice.set_unitcell("A15", shift=(0.1, 0.1, 0.1), density=0.8)
    
    
    # Output using the exporter.
    Exporter("yaplot").dump(
        genice,
    )
    ```

=== "9_ion_group.sh"

    ```bash
    #!/bin/bash
    # Generated from 9_ion_group.yaml
    
    python3 -m genice3.cli.genice A15 \
      --shift 0.1 0.1 0.1 \
      --density 0.8 \
      --rep 2 2 2 \
      --spot_anion 1=Cl \
      --spot_cation 51=N :group 12=methyl 48=methyl 49=methyl 50=methyl \
      --exporter yaplot \
      --seed 42 \
      --pol_loop_1 2000
    ```

=== "9_ion_group.yaml"

    ```yaml
    # Run with GenIce3: genice3 --config 9_ion_group.yaml
    # Generated from 9_ion_group.sh
    
    unitcell: A15
    shift:
    - 0.1
    - 0.1
    - 0.1
    density: 0.8
    rep:
    - 2
    - 2
    - 2
    spot_anion: 1=Cl
    spot_cation:
      51=N:
        group:
        - 12=methyl
        - 48=methyl
        - 49=methyl
        - 50=methyl
    exporter: yaplot
    seed: 42
    pol_loop_1: 2000
    ```
