**Basic usage examples** of GenIce3.

- `1_reactive_properties.py`  
  - Minimal example to explore how GenIce3's *reactive properties* behave.

- `2_simple.py`  
  - Introductory example that generates a simple ice structure and exports it.

---

## Sample code

### 1_reactive_properties

[`1_reactive_properties.py`](https://github.com/genice-dev/GenIce3/blob/main/examples/api/basic/1_reactive_properties.py)

```python
from genice3.genice import GenIce3
from logging import getLogger, basicConfig, INFO

logger = getLogger("test_genice3api1")
basicConfig(level=INFO)
genice = GenIce3()
logger.info("Reactive properties:")
logger.info(f"     All: {genice.list_all_reactive_properties().keys()}")
logger.info(f"  Public: {genice.list_public_reactive_properties().keys()}")
logger.info("Settabe reactive properties:")
logger.info(f"     All: {genice.list_settable_reactive_properties().keys()}")
logger.info(f"  Public: {genice.list_public_settable_reactive_properties().keys()}")
```

### 2_simple

[`2_simple.py`](https://github.com/genice-dev/GenIce3/blob/main/examples/api/basic/2_simple.py) | [`2_simple.sh`](https://github.com/genice-dev/GenIce3/blob/main/examples/api/basic/2_simple.sh) | [`2_simple.yaml`](https://github.com/genice-dev/GenIce3/blob/main/examples/api/basic/2_simple.yaml)

=== "2_simple.py"

    ```python
    from genice3.genice import GenIce3
    from genice3.plugin import Exporter
    
    # corresponding command:
    # genice3 A15 --exporter gromacs
    genice = GenIce3()
    genice.set_unitcell("A15")
    Exporter("gromacs").dump(genice)
    ```

=== "2_simple.sh"

    ```bash
    #!/bin/bash
    # Generated from 2_simple.yaml
    
    python3 -m genice3.cli.genice A15 \
      --exporter gromacs
    ```

=== "2_simple.yaml"

    ```yaml
    # Run with GenIce3: genice3 --config 2_simple.yaml
    # Generated from 2_simple.sh
    
    unitcell: A15
    exporter: gromacs
    ```
