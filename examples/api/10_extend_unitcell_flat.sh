#!/bin/bash
# 拡大胞を新たに単位胞とする unitcell プラグインを出力する例（フラットオプション）
# 対応する Python API: examples/api/10_extend_unitcell.py
# 対応する YAML: examples/api/10_extend_unitcell.yaml
#
# 生成された A15e.py は、rep=1 1 1 で同じ構造を再現する unitcell プラグインです。

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

python3 -m genice3.cli.genice A15 \
  --replication_matrix 1 1 0 -1 1 0 0 0 1 \
  --exporter python
