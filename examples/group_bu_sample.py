#!/usr/bin/env python3
"""
Bu group プラグインを呼び出して座標を取得するサンプル

Usage:
  poetry run python examples/group_bu_sample.py
"""

import numpy as np
from genice3.group.methyl import Methyl

# Group プラグインをロード
methyl = Methyl()
print(methyl)
