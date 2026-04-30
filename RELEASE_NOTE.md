# RELEASE NOTE

Scope: GenIce3-related changes after `a7e63b652a2cc324e84a55dced9892eba907ce84`

## Overview

After branching from the GenIce2 line, GenIce3 has been extensively redesigned around its API, option model, dependency engine, and plugin architecture.  
This period includes not only feature additions but also broad migration and stabilization work across CLI behavior, configuration style, documentation, and tests.

## Major Updates

- **Core foundation of GenIce3**
  - Introduced `genice3.py` and reorganized internals around a dependency-driven reactive recalculation model.
  - Improved reevaluation stability when settings change through refinements to `DependencyCacheMixin`, `@reactive`, and dependency processing.

- **CLI and option-system redesign**
  - Reworked option syntax in multiple iterations, resulting in a more structured interface and stronger YAML-based workflows.
  - Refined polarization-related parameters such as `pol_loop_1` and `pol_loop_2`, including forced and target-polarization handling.
  - Improved CLI usability by supporting negative values and shorthand option forms.

- **unitcell and structure-model expansion**
  - Migrated and added many unitcell plugins, with continuous behavior-comparison tests.
  - Added new structures including `YKD`, `ice21`, and its alias entries.
  - Improved CIF-derived unitcell generation by branching logic based on whether hydrogen positions are explicitly provided.

- **Doping, defects, and cage analysis**
  - Added or expanded support for ion placement, `spot_cation`-related handling, group options, Hydronium/Hydroxide, and Bjerrum defects.
  - Enhanced `cage_survey`-related behavior, including max-ring handling and evaluation logic.

- **Exporter and visualization improvements**
  - Improved GROMACS output, added a LAMMPS exporter, and expanded visualization paths including plotly and py3Dmol.
  - Continued refinement of exporter format functions and option parsing.

- **Web/API and documentation updates**
  - Expanded API notebooks, examples, and WebAPI docs/tests.
  - Updated README, references, and citations to improve usability and traceability.

- **Testing and development environment**
  - Strengthened comparison tests (including identity-related suites) and discovery workflows.
  - Continued refactoring around project layout and tooling (`scripts/`, `dev/`, and Makefile/build flows).

## Compatibility Notes

- Migration from GenIce2-style usage to the GenIce3 API/option system includes behavior and syntax changes.
- Polarization settings, cage evaluation, doping options, and exporter options should be checked when porting older scripts.
- In CIF processing, the `partial_order` option has been removed, and behavior now depends on hydrogen-position input availability.

## Version Progression (observed in this period)

- `3.0a3` -> `3.0a4` -> `3.0b0` -> `3.0b1` -> `3.0b2` -> `3.0b3` -> `3.0b4`

## Recent Topics (2026-04)

- Added WebAPI-related documentation and tests.
- Added `prism`.
- Improved exporter-format handling and API docs.
- Adopted `ice21` and added alias entries.
- Improved CIF-based unitcell generation logic for hydrogen-position handling.
