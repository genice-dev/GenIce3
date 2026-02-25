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
