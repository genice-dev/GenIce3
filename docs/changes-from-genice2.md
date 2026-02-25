# Main changes from GenIce2

- **Cage survey output**: The `-A` / `--assess_cages` option has been removed. To obtain cage positions and types, use the exporter plugin `cage_survey` (output is JSON; redirect to a file for reuse):

    ```shell
    genice3 CS2 -e cage_survey > cages.json
    ```
