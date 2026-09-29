"""
Hydrogen-bond density: the average number of hydrogen bonds crossing a unit
cross-sectional area (1 nm^2) of ice.

For planes with unit normal n, the density averaged over the plane position
is a cell-independent quantity

    sigma(n) = (1/V) * sum_bonds |b_ij . n|,

where b_ij is the bond vector and V is the cell volume.

For the cell face spanned by b and c (normal n_a, area A_a = |b x c|),
b_ij . n_a = d_a V / A_a with d_a the fractional bond component, so
sigma(n_a) = sum_bonds |d_a| / A_a. The number of bonds C_a actually crossing
the face depends on where the cell boundary cuts the crystal; C_a / A_a
fluctuates around sigma(n_a) and equals it on average over the position of
the cut. Tilting the cell (monoclinic, triclinic) increases A_a, but the
number of crossing bonds increases in proportion, so tilting itself does not
bias the density.

Dividing the total crossings over the six faces by the total surface area,
sum_a C_a / sum_a A_a, is an area-weighted average over the three face
normals and depends both on the choice of the cell and on the cut position.

A cell-independent representative value is the orientational average. Since
<|cos theta|> = 1/2,

    sigma_avg = (1/2V) * sum_bonds |b_ij| = N <L> / V   (2N bonds in ideal ice).
"""

from __future__ import annotations

import numpy as np

from genice3.genice import GenIce3


def hb_density(genice: GenIce3) -> dict:
    """Compute hydrogen-bond densities (bonds / nm^2) of the given ice."""
    cell = genice.cell
    frac = genice.lattice_sites % 1.0
    edges = np.array(list(genice.graph.edges()))
    ri = frac[edges[:, 0]]
    d = frac[edges[:, 1]] - ri
    d -= np.rint(d)

    b = d @ cell
    volume = abs(np.linalg.det(cell))

    # Face a is spanned by the other two cell vectors.
    areas = np.array(
        [np.linalg.norm(np.cross(cell[(a + 1) % 3], cell[(a + 2) % 3])) for a in range(3)]
    )
    crossings = np.abs(np.floor(ri + d) - np.floor(ri)).sum(axis=0)
    mean_crossings = np.abs(d).sum(axis=0)

    wrapped = np.any(np.floor(ri + d) != np.floor(ri), axis=1)
    return {
        "N": len(frac),
        "bonds": len(edges),
        "crossing_bonds": int(wrapped.sum()),  # = 2N - n
        "sigma_cut": crossings / areas,
        "sigma_n": mean_crossings / areas,
        "six_faces_cut": crossings.sum() / areas.sum(),
        "six_faces_n": mean_crossings.sum() / areas.sum(),
        "sigma_avg": np.linalg.norm(b, axis=1).sum() / (2 * volume),
    }


if __name__ == "__main__":
    for ice in ["1h", "1c", "3", "5", "6"]:
        genice = GenIce3()
        genice.set_unitcell(ice)
        r = hb_density(genice)
        print(
            f"ice {ice}: N={r['N']}, bonds={r['bonds']}, "
            f"bonds crossing the cell boundary (2N-n)={r['crossing_bonds']}"
        )
        print("  sigma at the cell faces (a,b,c):  ", np.round(r["sigma_cut"], 3))
        print("  sigma(n_a) averaged over the cut: ", np.round(r["sigma_n"], 3))
        print(f"  six faces, at the cell boundary:   {r['six_faces_cut']:.3f}")
        print(f"  six faces, averaged over the cut:  {r['six_faces_n']:.3f}")
        print(f"  orientational average:             {r['sigma_avg']:.3f} / nm^2")
