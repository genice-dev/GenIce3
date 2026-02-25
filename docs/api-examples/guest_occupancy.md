This directory contains examples for **guest occupancy and cage-related operations** in clathrate hydrates.

- `6_with_guests.py`  
  - Place guest molecules with specified occupancy for each cage type.

- `8_cage_survey.py`  
  - Survey cage positions and types in the structure.

---

## Sample code

### 6_with_guests

[`6_with_guests.py`](https://github.com/genice-dev/GenIce3/blob/main/examples/api/guest_occupancy/6_with_guests.py) | [`6_with_guests.sh`](https://github.com/genice-dev/GenIce3/blob/main/examples/api/guest_occupancy/6_with_guests.sh) | [`6_with_guests.yaml`](https://github.com/genice-dev/GenIce3/blob/main/examples/api/guest_occupancy/6_with_guests.yaml)

=== "6_with_guests.py"

    ```python
    from logging import basicConfig, DEBUG, INFO
    import numpy as np
    from genice3.genice import GenIce3
    from genice3.plugin import UnitCell, Exporter, Molecule
    from genice3.cli.options import parse_guest_option, parse_spot_guest_option
    
    # corresponding command (guest/spot_guest は基底オプション、exporterの外で指定):
    # genice3 "A15[shift=(0.1,0.1,0.1), anion.0=Cl, cation.6=Na, density=0.8]" \
    #   --rep 2 2 2 \
    #   --guest A12=me --guest A14=et --spot_guest 0=4site \
    #   --exporter gromacs :water_model 4site \
    #   --seed 42 --depol_loop 2000 -D
    
    basicConfig(level=INFO)
    
    # GenIce3インスタンスを作成
    # guests: ケージタイプごとのゲスト分子指定（parse_guest_optionで raw dict を変換）
    # spot_guests: 特定ケージへのゲスト分子指定（parse_spot_guest_optionで raw dict を変換）
    genice = GenIce3(
        seed=42,
        depol_loop=2000,
        replication_matrix=np.array([[2, 0, 0], [0, 2, 0], [0, 0, 2]]),
        guests=parse_guest_option({"A12": "me", "A14": "et"}),
        spot_guests=parse_spot_guest_option({0: "4site"}),
    )
    
    # 単位セルを設定
    # shift: シフト（分数座標）
    # anion / cation: 単位胞内の格子サイトをイオンで置換（サイトインデックス: イオン名）。CLI は -a / --anion, -c / --cation
    # density: 密度（g/cm³）
    # ケージ情報が必要な場合は Exporter("cage_survey").dump(genice, file) でJSON出力可能
    genice.unitcell = UnitCell(
        "A15",
        shift=(0.1, 0.1, 0.1),
        density=0.8,
    )
    
    
    # エクスポーターで出力（guest/spot_guest は GenIce3 に設定済み）
    Exporter("gromacs").dump(
        genice,
        water_model="4site",
    )
    ```

=== "6_with_guests.sh"

    ```bash
    #!/bin/bash
    # Generated from 6_with_guests.yaml
    
    python3 -m genice3.cli.genice A15 \
      --shift 0.1 0.1 0.1 \
      --density 0.8 \
      --rep 2 2 2 \
      --guest A12=me A14=et \
      --spot_guest 0=4site \
      --exporter gromacs :water_model 4site \
      --seed 42 \
      --depol_loop 2000
    ```

=== "6_with_guests.yaml"

    ```yaml
    # Run with GenIce3: genice3 --config 6_with_guests.yaml
    # Generated from 6_with_guests.sh
    
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
    guest:
    - A12=me
    - A14=et
    spot_guest: 0=4site
    exporter:
      gromacs:
        water_model: 4site
    seed: 42
    depol_loop: 2000
    ```


### 8_cage_survey

[`8_cage_survey.py`](https://github.com/genice-dev/GenIce3/blob/main/examples/api/guest_occupancy/8_cage_survey.py) | [`8_cage_survey.sh`](https://github.com/genice-dev/GenIce3/blob/main/examples/api/guest_occupancy/8_cage_survey.sh) | [`8_cage_survey.yaml`](https://github.com/genice-dev/GenIce3/blob/main/examples/api/guest_occupancy/8_cage_survey.yaml)

=== "8_cage_survey.py"

    ```python
    """DOH 構造で cage_survey を使う例（Python API）"""
    from genice3.genice import GenIce3
    from genice3.plugin import UnitCell, Exporter
    from logging import basicConfig, INFO
    
    # 対応するコマンド:
    #   genice3 DOH -e cage_survey
    basicConfig(level=INFO)
    genice = GenIce3()
    genice.unitcell = UnitCell("DOH")
    Exporter("cage_survey").dump(genice)
    ```

=== "8_cage_survey.sh"

    ```bash
    #!/bin/bash
    # Generated from 8_cage_survey.yaml
    
    python3 -m genice3.cli.genice DOH \
      --exporter cage_survey
    ```

=== "8_cage_survey.yaml"

    ```yaml
    # Run with GenIce3: genice3 --config 8_cage_survey.yaml
    # Generated from 8_cage_survey.sh
    
    unitcell: DOH
    exporter: cage_survey
    ```
