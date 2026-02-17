import genice3.group
import numpy as np


class Group(genice3.group.Group):
    def __init__(self):
        bondlen = 0.109
        sine = 1 / 3
        cosine = (1 - sine**2) ** 0.5
        z = bondlen * sine
        r = bondlen * cosine
        cosine2 = -1 / 2
        sine2 = (1 - cosine2**2) ** 0.5
        super().__init__(
            sites=np.array(
                [
                    [0.0, 0.0, 0.0],
                    [r, 0.0, z],
                    [r * cosine2, r * sine2, z],
                    [r * cosine2, -r * sine2, z],
                ]
            ),
            labels=["C", "H", "H", "H"],
            bonds=[(0, 1), (0, 2), (0, 3)],
            name="Methyl",
        )
