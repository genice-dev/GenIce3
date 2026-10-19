"""Web / MCP が共有する設定・生成例外（HTTP ステータスに写せる）。"""

from __future__ import annotations


class ServiceError(Exception):
    """サービス層の基底。``http_status`` は Web アダプタ用の目安。"""

    http_status: int = 500

    def __init__(self, message: str, *, detail: object | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.detail = detail if detail is not None else message


class ParseError(ServiceError):
    """設定テキストのパース失敗。"""

    http_status = 400


class ValidationError(ServiceError):
    """必須欠落・未知キー・型不正など。"""

    http_status = 400


class UnknownPluginError(ServiceError):
    """存在しない unitcell / exporter 名。"""

    http_status = 404


class GenerationError(ServiceError):
    """構造生成・export 中の（想定しうる）失敗。"""

    http_status = 422
