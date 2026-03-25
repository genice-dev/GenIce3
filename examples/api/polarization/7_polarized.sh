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
