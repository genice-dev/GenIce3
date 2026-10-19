"""Structured logging helpers for GenIce3 (text default, JSON opt-in).

Logs always go to stderr so stdout can carry structure files.
"""

from __future__ import annotations

import json
import os
import sys
from contextvars import ContextVar, Token
from datetime import datetime, timezone
from logging import (
    DEBUG,
    INFO,
    Formatter,
    LogRecord,
    StreamHandler,
    getLogger,
)
from typing import Any, Literal, MutableMapping, Optional

LogFormat = Literal["text", "json"]

_LOG_CONTEXT: ContextVar[dict[str, Any]] = ContextVar(
    "genice3_log_context", default={}
)

# LogRecord の組み込み属性（JSON のカスタムフィールドから除外する）
_RESERVED_ATTRS = frozenset(LogRecord("", 0, "", 0, "", (), None).__dict__) | {
    "message",
    "asctime",
    "msg",
    "args",
    "exc_info",
    "exc_text",
    "stack_info",
    "created",
    "msecs",
    "relativeCreated",
    "levelname",
    "levelno",
    "name",
    "pathname",
    "filename",
    "module",
    "lineno",
    "funcName",
    "process",
    "processName",
    "thread",
    "threadName",
    "taskName",
}


def get_context() -> dict[str, Any]:
    """Return a shallow copy of the current log context."""
    return dict(_LOG_CONTEXT.get())


def bind_context(**kwargs: Any) -> Token:
    """Merge kwargs into the log context; return a token for :func:`reset_context`."""
    current = dict(_LOG_CONTEXT.get())
    for key, value in kwargs.items():
        if value is not None:
            current[key] = value
    return _LOG_CONTEXT.set(current)


def reset_context(token: Token) -> None:
    """Restore the context to the state before :func:`bind_context`."""
    _LOG_CONTEXT.reset(token)


def clear_context() -> None:
    """Clear all bound context fields."""
    _LOG_CONTEXT.set({})


def resolve_log_format(
    cli_value: Optional[str] = None,
    *,
    default: LogFormat = "text",
) -> LogFormat:
    """Resolve ``text`` / ``json`` from CLI value, then ``GENICE_LOG_FORMAT``, then default."""
    if cli_value is not None:
        normalized = str(cli_value).strip().lower()
        if normalized in ("text", "json"):
            return normalized  # type: ignore[return-value]
    env = os.environ.get("GENICE_LOG_FORMAT", "").strip().lower()
    if env in ("text", "json"):
        return env  # type: ignore[return-value]
    return default


class JsonFormatter(Formatter):
    """One NDJSON object per log record on stderr."""

    def format(self, record: LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts": datetime.fromtimestamp(record.created, tz=timezone.utc)
            .isoformat(timespec="milliseconds")
            .replace("+00:00", "Z"),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        for key, value in get_context().items():
            if key not in payload:
                payload[key] = value
        event = getattr(record, "event", None)
        if event is not None:
            payload["event"] = event
        for key, value in record.__dict__.items():
            if key in _RESERVED_ATTRS or key.startswith("_"):
                continue
            if key == "event":
                continue
            if value is None:
                continue
            payload[key] = value
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False, default=str)


def setup_logging(
    debug: bool = False,
    fmt: Optional[str] = None,
    *,
    default_format: LogFormat = "text",
) -> LogFormat:
    """Configure the root logger to write to stderr.

    Args:
        debug: If True, set level to DEBUG and (in text mode) include logger:lineno.
        fmt: ``text`` or ``json``. ``None`` uses :func:`resolve_log_format`.
        default_format: Fallback when neither CLI nor env sets a format.

    Returns:
        The format actually applied.
    """
    resolved = resolve_log_format(fmt, default=default_format)
    root = getLogger()
    for handler in root.handlers[:]:
        root.removeHandler(handler)

    handler = StreamHandler(sys.stderr)
    level = DEBUG if debug else INFO
    root.setLevel(level)
    handler.setLevel(level)

    if resolved == "json":
        handler.setFormatter(JsonFormatter())
    elif debug:
        handler.setFormatter(
            Formatter("%(levelname)s %(name)s:%(lineno)d: %(message)s")
        )
    else:
        handler.setFormatter(Formatter("%(levelname)s: %(message)s"))

    root.addHandler(handler)
    return resolved


def log_event(
    logger: Any,
    level: int,
    event: str,
    msg: str,
    *args: Any,
    **fields: Any,
) -> None:
    """Log ``msg`` with a stable ``event`` name and optional structured fields."""
    extra: MutableMapping[str, Any] = {"event": event}
    for key, value in fields.items():
        if value is not None:
            extra[key] = value
    logger.log(level, msg, *args, extra=extra)
