"""
genice3 CLI パッケージ。

- option_parser: option_handling.md に基づくオプション文字列パーサー
- runner: argv のパースとプラグイン dispatch（parse_argv, validate_result）
"""

from genice3.cli.option_parser import (
    parse_options,
    structure_for_display,
    scalarize_single_item_lists,
    structure_to_option_string,
)

__all__ = [
    "parse_options",
    "structure_for_display",
    "scalarize_single_item_lists",
    "structure_to_option_string",
]
