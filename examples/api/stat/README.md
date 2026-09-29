**Structural statistics** of the hydrogen-bond network.

- `18_hbdensity.py`  
  - Hydrogen-bond density: the average number of hydrogen bonds crossing a unit cross-sectional area (bonds / nm²) of ice, computed for ices 1h, 1c, 3, 5, and 6.
  - Compares the number of bonds actually crossing the cell faces, the density averaged over the position of the cut, `sigma(n) = (1/V) * sum |b_ij . n|`, and the cell-independent orientational average `sigma_avg = N <L> / V`.
  - Tilting the cell (e.g. monoclinic ice V) does not bias the density; the count at the cell faces depends on where the boundary cuts the crystal.

Additional implementations for the same topics (e.g., CLI- or config-file–driven variants) may be added here in the future.
