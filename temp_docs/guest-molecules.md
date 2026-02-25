# Guest molecules

{{ guests }}

For THF, `uathf` is a 5-site united-atom model; `uathf6` adds a dummy site (e.g. for some force fields). Both can be used with `-g` (e.g. `-g 16=uathf` or `-g 16=uathf6`).

You can add custom guest molecules by placing plugins in a `molecules` directory in the current working directory.
