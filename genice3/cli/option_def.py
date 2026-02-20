"""OptionDef と型定数（--help と検証用）。options と validator の両方から参照する。"""

from dataclasses import dataclass
from typing import Any, Callable, Optional

OPTION_TYPE_FLAG = "flag"
OPTION_TYPE_STRING = "string"
OPTION_TYPE_TUPLE = "tuple"
OPTION_TYPE_KEYVALUE = "keyvalue"


@dataclass(frozen=True)
class OptionDef:
    """CLI で認識するオプションの定義（ヘルプ・検証用）。"""

    name: str
    short: Optional[str] = None
    is_flag: bool = False
    max_values: Optional[int] = None
    level: str = "base"
    parse_type: Optional[str] = None
    metavar: Optional[str] = None
    help_text: Optional[str] = None
    help_format: Optional[str] = None
    parse_validator: Optional[Callable[[Any], None]] = None
