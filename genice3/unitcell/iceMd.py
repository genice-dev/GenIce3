#!/usr/bin/python
# coding: utf-8

from genice3.unitcell.iceM import UnitCell as UnitCellM
import networkx as nx

desc = {
    "ref": {"Md": "Mochizuki 2024"},
    "brief": "A hydrogen-disordered counterpart of ice M.",
    "test": ({"options": "--depol=none"},),
}


class UnitCell(UnitCellM):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fixed = nx.DiGraph()
