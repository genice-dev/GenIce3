import numpy as np

ex, ey, ez = 1 / 3, 2 / 3, 2 / 3
r = (ex**2 + ey**2) ** 0.5
Ry = np.array([[ez, 0, -r], [0, 1, 0], [r, 0, ez]])
Rz = np.array([[ex / r, ey / r, 0], [-ey / r, ex / r, 0], [0, 0, 1]])
v1 = np.array([0, 0, 1]) @ Ry
print(v1, np.linalg.norm(v1))
v2 = v1 @ Rz
print(v2, np.linalg.norm(v2))
print(np.linalg.det(Ry @ Rz))
