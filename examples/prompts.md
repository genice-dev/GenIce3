# Example prompts for GenIce3

Example prompts used to check whether an AI with no prior context can configure GenIce3 correctly by reading only the `docs/` directory (and [For AI assistants](docs/for-ai-assistants.md)).

## Example prompts

### CLI (sI hydrate, GROMACS, TIP4P)

- Using the manual at https://genice-dev.github.io/GenIce3, write a GenIce3 CLI command that: generates an sI clathrate hydrate 2×2×2 with United-atom methane in all cages, GROMACS format, and TIP4P water.

### API (zeolite, GROMACS, TIP4P)

- Using this repository’s `docs/`, write Python code that uses the GenIce3 API to: generate a zeolite LTA ice structure 2×2×2, GROMACS format, TIP4P water.

(Zeolite is specified with the `zeolite` unit cell and a 3-letter IZA code (e.g. LTA, FAU). See [Unit cells](docs/unitcells.md).)

### Config file / YAML (aeroice, GROMACS, TIP5P)

- Using this repository’s `docs/`, write a GenIce3 config file (YAML) that: generates an aeroice structure with prism length 3, GROMACS format, TIP5P water.
