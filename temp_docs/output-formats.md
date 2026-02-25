# Output formats

{{ exporter }}

A GenIce3-compatible plugin **[genice3-mdanalysis](https://github.com/genice-dev/genice3-mdanalysis)** is available; it provides an exporter for [MDAnalysis](https://www.mdanalysis.org/) and the many formats it supports. See [`genice3-mdanalysis`](https://github.com/genice-dev/genice3-mdanalysis). [Plugins](plugins.md) lists other prepared/planned plugins.

You can add custom output formats by placing exporter plugins in an `exporter` directory under the current working directory.

## Pipeline (Reactive / Dependency)

GenIce3 does **not** use the old GenIce2-style fixed “seven stages”. The pipeline is **reactive**: which steps run is determined automatically from the **Dependency** graph. You request outputs (e.g. coordinates, cage list); the engine runs only the tasks required to produce them. Exporter plugins register hooks that run when their inputs become available.
