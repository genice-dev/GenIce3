#!/bin/bash
# guest/spot_guest は基底オプション。water_model は exporter オプション。
# 対応するPythonコード: examples/api/6_with_guests.py

python3 -m genice3.cli.genice A15 --shift 0.1 0.1 0.1 --density 0.8 \
  --rep 2 2 2 \
  --guest A12=me --guest A14=et --spot_guest 0=4site \
  --exporter gromacs --water_model 4site \
  --seed 42 \
  --depol_loop 2000
