#!/bin/bash
# Generated from 7_polarized.yaml

python3 -m genice3.cli.genice 1h \
  --rep 2 2 2 \
  --exporter _pol \
  --seed 114 \
  --pol_loop_1 1000 \
  --target_polarization 4 0 0
