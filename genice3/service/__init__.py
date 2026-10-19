"""HTTP / MCP 非依存の共有サービス層（設定パース・メタ・生成）。"""

from genice3.service.config import (
    config_dict_from_input,
    parsed_result_from_config,
)
from genice3.service.exceptions import (
    GenerationError,
    ParseError,
    ServiceError,
    UnknownPluginError,
    ValidationError,
)
from genice3.service.generate import GenerateResult, generate
from genice3.service.meta import (
    get_exporter_options,
    get_unitcell_options,
    list_exporters,
    list_unitcells,
)

__all__ = [
    "ServiceError",
    "ParseError",
    "ValidationError",
    "UnknownPluginError",
    "GenerationError",
    "config_dict_from_input",
    "parsed_result_from_config",
    "list_unitcells",
    "list_exporters",
    "get_unitcell_options",
    "get_exporter_options",
    "generate",
    "GenerateResult",
]
