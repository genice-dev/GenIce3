# Output formats

{{ exporter }}

!!! info "MDAnalysis-based exporters"
    A GenIce3-compatible exporter for [MDAnalysis](https://www.mdanalysis.org/) and the many formats it supports is **not yet implemented**. The GenIce2 package [`genice2-mdanalysis`](https://github.com/genice-dev/genice-mdanalysis) targets GenIce2; see [Plugins](plugins.md) for prepared/planned plugins.

You can add custom output formats by placing exporter plugins in an `exporter` directory under the current working directory.

## Pipeline (Reactive / Dependency)

GenIce3 does **not** use the old GenIce2-style fixed “seven stages”. The pipeline is **reactive**: which steps run is determined automatically from the **Dependency** graph. You request outputs (e.g. coordinates, cage list); the engine runs only the tasks required to produce them. Exporter plugins register hooks that run when their inputs become available.
