# Doping ions and topological defects

## Two ways to place ions

GenIce3 supports two kinds of ion placement, each with its own CLI options:

| Purpose | Short | Long | Meaning |
|--------|-------|------|--------|
| **Unit-cell ions** (lattice sites, replicated with the cell) | `-a` | `--anion` | Anion at a **unit-cell** site index |
| | `-c` | `--cation` | Cation at a **unit-cell** site index |
| **Spot ions** (specific water in the supercell) | `-A` | `--spot_anion` | Anion replacing one **water molecule** by supercell index |
| | `-C` | `--spot_cation` | Cation replacing one **water molecule** by supercell index |

You can combine both: e.g. unit-cell ions for a periodic pattern and spot ions for extra doping at chosen cages.

---

### Unit-cell ions: `-a` / `-c` (lattice sites, replicated with the cell)

**Unit-cell** anions and cations are defined by a **site index in the unit cell**. Those sites are **replicated** with the lattice (e.g. `--rep 2 2 2` gives the same ion pattern in every 2×2×2 replica). Use `-a` (anion) and `-c` (cation):

- `-a SITE_INDEX=ION_NAME` — put an anion at that lattice site in the unit cell
- `-c SITE_INDEX=ION_NAME` — put a cation at that lattice site in the unit cell

**Example:** CS2 clathrate with Na⁺ at unit-cell site 0 and Cl⁻ at unit-cell site 1; the pattern is repeated with replication:

```shell
genice3 CS2 -c 0=Na -a 1=Cl --rep 2 2 2 -e gromacs > CS2.gro
```

YAML config equivalent:

```yaml
unitcell: CS2
cation: 0=Na
anion: 1=Cl
rep: [2, 2, 2]
exporter: gromacs
```

Many unit cells (e.g. A15, CS2) support optional `:group` suboptions for cations (e.g. `--cation 0=N :group 1=methyl 6=methyl`). See [API examples → doping](api-examples/doping.md).

---

### Spot ions: `-A` / `-C` (specific water molecules in the supercell)

**Spot** anions and cations replace **specific** water molecules by their **water index in the replicated supercell**. Use `-A` (spot_anion) and `-C` (spot_cation):

- `-A WATER_INDEX=ION_NAME` — put an anion at that water molecule (by supercell index)
- `-C WATER_INDEX=ION_NAME` — put a cation at that water molecule (by supercell index)

**Example:** A15 clathrate, 2×2×2 supercell; put Cl⁻ at water index 1 and Na⁺ at water index 51 in the supercell:

```shell
genice3 A15 --rep 2 2 2 -A 1=Cl -C 51=Na -e gromacs > A15_doped.gro
```

YAML config equivalent:

```yaml
unitcell: A15
replication_factors: [2, 2, 2]
spot_anion: 1=Cl
spot_cation: 51=Na
exporter: gromacs
```

Multiple spot ions: use several options, e.g. `-A 1=Cl -A 35=Br -C 1=Na -C 35=K`.

!!! failure "Charge balance"
    The total number of cations and anions must be equal, or the ice rule cannot be satisfied and the program may not terminate.

## Protonic and Bjerrum defects (API only)

With the GenIce3 **Python API** you can embed **protonic defects** (H₃O⁺ and OH⁻) and **Bjerrum topological defects** at specified positions in the lattice. These are not exposed as command-line options yet.

- **H₃O⁺ / OH⁻**: Use `spot_hydroniums` and `spot_hydroxides` (lists of site indices). See [API examples → Topological defects](api-examples/topological_defects.md).
- **Bjerrum L/D defects**: Place defects on specific edges (hydrogen bonds) by fixing adjacent bond orientations; use helpers such as `edges_closeto()` to find the edge nearest to a coordinate. Example scripts: `examples/api/12_topological_defect.py` and `examples/api/13_topological_defect2.py`.
