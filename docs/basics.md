# Basics

The program generates various hydrogen-disordered ice structures without defects. The total dipole moment is set to zero unless you change the depolarization behavior with `--depol_loop` or `--target_polarization`. The minimal structure (with `--rep 1 1 1`) is not always a single unit cell, because handling the hydrogen-bond network topology of very small lattices under periodic boundary conditions is difficult. Note that the generated structure is **not** optimized for potential energy.

- To generate a large supercell of ice Ih in CIF format:

    ```shell
    genice3 1h --rep 8 8 8 -e cif > 1hx888.cif
    ```

- To generate an ice V lattice with a different hydrogen order in CIF format, use the `-s` option to set the random seed:

    ```shell
    genice3 5 -s 1024 -e cif > 5-1024.cif
    ```

- To generate an ice VI lattice at a different density with the TIP4P water model in GROMACS format:

    ```shell
    genice3 6 --density 1.00 -e "gromacs :water_model tip4p" > 6d1.00.gro
    ```

GenIce3 is modular: it loads unit cells from plugins in the `unitcell` folder, places water and guest molecules using plugins in the `molecules` folder, and writes output via plugins in the `exporter` folder. You can add your own plugins to extend GenIce3; many plugins accept options.
