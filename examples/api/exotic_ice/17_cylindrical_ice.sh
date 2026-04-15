#!/bin/bash

python3 -m genice3.cli.genice prism \
  --circum 6 1 \
  --axial -2 10 \
  --x f \
  --y a \
  --exporter gromacs :water_model 4site \
  --seed 42
