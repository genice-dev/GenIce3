**Ionic substitution and group (cation group) doping**.

CLI: unitcell のイオンは **-a / --anion**, **-c / --cation**。スポット置換は **-A / --spot_anion**, **-C / --spot_cation**。

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
    from genice3.plugin import UnitCell, Exporter
    
    # corresponding command:
    # genice3 A15 --cation 0=N :group 1=methyl 6=methyl 3=methyl 4=methyl \
    #   --anion 2=Cl --rep 2 2 2 --exporter gromacs :water_model 4site
    
    basicConfig(level=INFO)
    
    genice = GenIce3(
        replication_matrix=np.array([[2, 0, 0], [0, 2, 0], [0, 0, 2]]),
        seed=43,
    )
    
    # 単位胞内の anion/cation と cation_groups（カチオンの腕の group 指定）
    genice.unitcell = UnitCell(
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
    from genice3.plugin import UnitCell, Exporter, Molecule
    
    # corresponding command:
    # genice3 "A15[shift=(0.1,0.1,0.1), anion.0=Cl, cation.6=Na, density=0.8]" \
    #   --rep 2 2 2 \
    #   --spot_anion 1=Cl --spot_anion 35=Br \
    #   --spot_cation 1=Na --spot_cation 35=K \
    #   --exporter gromacs :water_model 4site \
    #   --seed 42 --depol_loop 2000 -D
    
    basicConfig(level=INFO)
    
    # GenIce3インスタンスを作成
    # seed: 乱数シード
    # depol_loop: 分極ループの反復回数
    # replication_matrix: 複製行列（2x2x2の対角行列）
    # spot_anions: 特定の水分子をアニオンで置換（水分子インデックス: イオン名）。CLI は -A / --spot_anion
    # spot_cations: 特定の水分子をカチオンで置換（水分子インデックス: イオン名）。CLI は -C / --spot_cation
    # 注意: debugはGenIce3のコンストラクタでは受け付けられない（ログレベルの設定はbasicConfigで行う）
    genice = GenIce3(
        seed=42,
        depol_loop=2000,
        replication_matrix=np.array([[2, 0, 0], [0, 2, 0], [0, 0, 2]]),
        spot_anions={
            1: "Cl",
        },
        spot_cations={
            51: "Na",
        },
    )
    
    # 単位セルを設定
    # shift: シフト（分数座標）
    # anion: 単位胞内の格子サイトをアニオンで置換（サイトインデックス: イオン名）。CLI は -a / --anion
    # cation: 単位胞内の格子サイトをカチオンで置換（サイトインデックス: イオン名）。CLI は -c / --cation
    # density: 密度（g/cm³）
    # ケージ情報が必要な場合は Exporter("cage_survey").dump(genice, file) でJSON出力可能
    genice.unitcell = UnitCell(
        "A15",
        shift=(0.1, 0.1, 0.1),
        anion={15: "Cl"},
        cation={21: "Na"},
        density=0.8,
    )
    
    
    # エクスポーターで出力
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
      --depol_loop 2000 \
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
    depol_loop: 2000
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
    from genice3.plugin import UnitCell, Exporter, Molecule
    
    # corresponding command:
    # genice3 "A15[shift=(0.1,0.1,0.1), anion.0=Cl, cation.6=Na, density=0.8]" \
    #   --rep 2 2 2 \
    #   --spot_anion 1=Cl --spot_anion 35=Br \
    #   --spot_cation 1=Na --spot_cation 35=K \
    #   --exporter gromacs :water_model 4site \
    #   --seed 42 --depol_loop 2000 -D
    
    basicConfig(level=INFO)
    
    # GenIce3インスタンスを作成
    # seed: 乱数シード
    # depol_loop: 分極ループの反復回数
    # replication_matrix: 複製行列（2x2x2の対角行列）
    # spot_anions / spot_cations: 水分子インデックス -> イオン名。CLI は -A / --spot_anion, -C / --spot_cation
    # spot_cation_groups: group サブオプション（サイト -> {ケージID -> group名}）。
    # YAML/CLI のネスト形式で使う "ion" キーは Python API では不要（別引数で渡す）。
    genice = GenIce3(
        seed=42,
        depol_loop=2000,
        replication_matrix=np.array([[2, 0, 0], [0, 2, 0], [0, 0, 2]]),
        spot_anions={1: "Cl"},
        spot_cations={51: "N"},
        spot_cation_groups={
            51: {12: "methyl", 48: "methyl", 49: "methyl", 50: "methyl"},
        },
    )
    
    # 単位セルを設定
    # anion / cation: 単位胞内の格子サイトをイオンで置換（サイトインデックス: イオン名）。CLI は -a / --anion, -c / --cation
    # density: 密度（g/cm³）
    # ケージ情報が必要な場合は Exporter("cage_survey").dump(genice, file) でJSON出力可能
    genice.unitcell = UnitCell(
        "A15",
        shift=(0.1, 0.1, 0.1),
        density=0.8,
    )
    
    
    # エクスポーターで出力
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
      --depol_loop 2000
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
    depol_loop: 2000
    ```
