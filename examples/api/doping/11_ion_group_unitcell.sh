#!/bin/bash
# Generated from 11_ion_group_unitcell.yaml

python3 -m genice3.cli.genice A15 \
  --cation 0=N :group 1=methyl 6=methyl 3=methyl 4=methyl \
  --anion 2=Cl \
  --rep 2 2 2 \
  --exporter gromacs :water_model 4site
