"""
CLI / Web 等が共有する GenIce3 実行コア（パース済み result → exporter 出力）。
"""

from __future__ import annotations

from typing import Any, Dict, TextIO

from genice3.cage import apply_max_cage_rings
from genice3.genice import GenIce3
from genice3.plugin import safe_import
from genice3.cli.options import extract_genice_args


def run_parsed_result(
    result: Dict[str, Any],
    file: TextIO,
    *,
    command_line: str | None = None,
) -> None:
    """パース・検証済みの ``result`` で GenIce3 を実行し、exporter 出力を ``file`` に書く。

    Args:
        result: :func:`genice3.cli.runner.parse_argv` または
            :func:`genice3.cli.runner.parsed_result_from_merged` が返す辞書。
        file: 出力先（例: ``sys.stdout``、``io.StringIO()``）。
        command_line: exporter に渡すメタ用。省略時は ``""``。

    Raises:
        プラグインや exporter の例外はそのまま伝播する（呼び出し側で捕捉してよい）。
    """
    base_options = result["base_options"]
    genice_kwargs = extract_genice_args(base_options)

    unitcell_name = result["unitcell"]["name"]
    unitcell_processed = result["unitcell"]["processed"]
    exporter_name = result["exporter"]["name"] or "gromacs"
    exporter_processed = dict(result["exporter"]["processed"])

    genice = GenIce3(**genice_kwargs)
    genice.unitcell = safe_import("unitcell", unitcell_name).UnitCell(**unitcell_processed)

    if exporter_name == "cage_survey":
        apply_max_cage_rings(genice, exporter_processed.get("max_cage_rings"))

    exporter_processed["command_line"] = command_line if command_line is not None else ""

    safe_import("exporter", exporter_name).dump(genice, file, **exporter_processed)
