# Doping ions and topological defects

## Two ways to place ions

### Spot ions: `-a` / `-c` (specific sites in the supercell)

**Spot** anions and cations replace **specific** water molecules by their site index in the **replicated** (supercell) lattice. Use `-a` (spot_anion) and `-c` (spot_cation):

- `-a WATER_INDEX=ION_NAME` — put an anion at that water site
- `-c WATER_INDEX=ION_NAME` — put a cation at that water site

Example: Na⁺ at water 0 and Cl⁻ at water 1 in the supercell; hydrogen bonds around the ions are adjusted:

```shell
genice3 CS2 -c 0=Na -a 1=Cl > CS2.gro
```

!!! failure "Charge balance"
    The total number of cations and anions must be equal, or the ice rule cannot be satisfied and the program may not terminate.

### Unit-cell–defined ions (periodic, replicated with the cell)

Some **unit-cell plugins** define anion/cation sites **inside the unit cell**. Those ions are then **replicated** with the cell (e.g. with `--rep 2 2 2` you get the same pattern in each replica). There is **no CLI option** for this: you choose a lattice that already has those sites (e.g. a custom unit cell that sets `anions` and `cations` in its plugin). The spot options `-a` / `-c` add or override **specific** sites on top of any unit-cell–defined ions.

## Protonic and Bjerrum defects (API only)

With the GenIce3 **Python API** you can embed **protonic defects** (H₃O⁺ and OH⁻) and **Bjerrum topological defects** at specified positions in the lattice. These are not exposed as command-line options yet.

- **H₃O⁺ / OH⁻**: Use `spot_hydroniums` and `spot_hydroxides` (lists of site indices). See [API examples → Topological defects](api-examples/topological_defects.md).
- **Bjerrum L/D defects**: Place defects on specific edges (hydrogen bonds) by fixing adjacent bond orientations; use helpers such as `edges_closeto()` to find the edge nearest to a coordinate. Example scripts: `examples/api/12_topological_defect.py` and `examples/api/13_topological_defect2.py`.
