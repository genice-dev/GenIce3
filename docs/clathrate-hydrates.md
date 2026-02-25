# Clathrate hydrates

For clathrate hydrates, you can build lattices with cages partially occupied by guest molecules.

- To generate a CS1 clathrate hydrate with TIP4P water and CO₂ in GROMACS .gro format (60% of small cages filled with CO₂, 40% with methane):

    ```shell
    genice3 CS1 -g A12=co2*0.6+me*0.4 -g A14=co2 --water tip4p > cs1.gro
    ```

    You can look up cage names in advance with `cage_survey`:

    ```shell
    genice3 CS1 -e cage_survey > survey.log
    ```

- To generate a CS2 clathrate hydrate with TIP5P water, THF in the large cages, and methane in one small cage: first run `genice3` without guest options:

    ```shell
    genice3 CS2 -e cage_survey > survey.log
    ```

    The cage list will be printed, for example:

    ```text
    INFO:root:Cage types: ['A12', 'A16']
    INFO:root:Cage type A12: {1, 2, 4, ...}
    INFO:root:Cage type A16: {0, 3, 5, ...}
    ```

    This shows two cage types, `A12` and `A16`. To fill type `A16` with THF and put methane in cage `0` of type `A12`:

    ```shell
    genice3 CS2 -g A16=uathf -G 0=me > CS2.gro
    ```

Only a few guest molecules are included by default; you can add more by writing a plugin. Here is an example for ethylene oxide:

```python
import numpy as np
import genice3.molecule

class Molecule(genice3.molecule.Molecule):
    def __init__(self):
        # United-atom EO model with a dummy site
        LOC = 0.1436  # nm
        LCC = 0.1472  # nm
        Y = (LOC**2 - (LCC/2)**2)**0.5
        sites = np.array([[0., 0., 0.], [-LCC/2, Y, 0.], [+LCC/2, Y, 0.]])
        mass = np.array([16, 14, 14])
        CoM = mass @ sites / np.sum(mass)
        sites -= CoM
        atoms = ["O", "C", "C"]
        labels = ["Oe", "Ce", "Ce"]
        name = "EO"
        super().__init__(sites=sites, labels=labels, name=name, is_water=False)
```

Save this as `eo.py` in a `molecule` folder in your current directory.

!!! warning "Multiple occupancy not supported"
Multiple occupancy is not supported. To model it, prepare a `molecule` plugin that represents multiple molecules.
