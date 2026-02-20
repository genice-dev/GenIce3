#!/bin/bash
# Generated from 10_extend_unitcell.yaml

python3 -m genice3.cli.genice A15 \
  --replication_matrix 1 1 0 -1 1 0 0 0 1 \
  --exporter python
