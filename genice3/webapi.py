"""
GenIce3 の薄い HTTP 層（FastAPI）。共有ロジックは ``genice3.service``。

依存: ``pip install "genice3[web]"`` 後に ``genice3-web`` または
``uvicorn genice3.webapi:app`` で起動。

入力は CLI の ``-Y`` と同系統の設定（YAML 正、互換 TOML / JSON）。
成功時の応答は常に JSON ラップ:
``{"meta": {...}, "content": "...", "media_type": "..."}``。
"""

from __future__ import annotations

import os
import time
import uuid
from logging import ERROR, INFO, getLogger
from typing import Any, Optional, Union

from pydantic import BaseModel, Field, model_validator

from genice3.logging_config import (
    bind_context,
    log_event,
    reset_context,
    resolve_log_format,
    setup_logging,
)
from genice3.service import (
    ServiceError,
    generate,
    get_exporter_options,
    get_unitcell_options,
    list_exporters,
    list_unitcells,
)

try:
    from fastapi import FastAPI, HTTPException, Request
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse
except ModuleNotFoundError as e:  # pragma: no cover
    raise ModuleNotFoundError(
        "The web API needs FastAPI. Install it with: pip install 'genice3[web]'"
    ) from e

logger = getLogger(__name__)


_GENERATE_YAML_EXAMPLE = (
    "unitcell: 1h\n"
    "genice3:\n"
    "  rep: [1, 1, 1]\n"
    "  seed: 1\n"
    "exporter: gromacs\n"
)

_OPENAPI_DESCRIPTION = """
A thin HTTP wrapper around GenIce3, which builds hydrogen-disordered ice and
clathrate hydrate structures. The configuration is the **same schema as the
`genice3` CLI `-Y` file** (YAML by default; TOML and JSON with the same keys
are also accepted).

## Typical flow (for agents)

1. **`GET /v1/meta/unitcells`** for available unit cells.
2. **`GET /v1/meta/unitcells/{name}/options`** for plugin and common options.
3. **`GET /v1/meta/exporters`** and **`GET /v1/meta/exporters/{name}/options`**
   (includes `media_type` for the exporter's `dumps()` output).
4. **`POST /v1/generate`** with the configuration as the request body.
   On success the body is **JSON**:
   `{"meta": {...}, "content": "<structure text>", "media_type": "..."}`.
   `meta.seed` defaults to **1** when omitted (same as the CLI / `GenIce3`).
5. **`POST /v1/generate/json`** accepts a JSON object: either the config
   mapping directly, `{"config": {...}}`, or legacy `{"config_yaml": "<yaml>"}`.

## Errors

- **400**: parse / validation failure.
- **404**: unknown unitcell or exporter name (meta or generate).
- **422**: generation / export failure.
- **500**: unexpected server error.

## Limits

Topological defects (H₃O⁺/OH⁻, Bjerrum) are **API-only** and not exposed here
(same boundary as the CLI / YAML).

## Background documents

- Project summary: **https://genice-dev.github.io/GenIce3/for-ai-assistants/**
- Full manual: **https://genice-dev.github.io/GenIce3**
"""

_OPENAPI_TAGS = [
    {
        "name": "generate",
        "description": "Build a structure from a configuration. Success responses are JSON-wrapped.",
    },
    {
        "name": "meta",
        "description": "Catalogue of unit cells and exporters, and their option schemas.",
    },
    {
        "name": "health",
        "description": "Liveness check.",
    },
]


class GenerateJsonBody(BaseModel):
    """JSON 経路: 設定オブジェクト、またはレガシー ``config_yaml`` 文字列。"""

    config: Optional[dict[str, Any]] = Field(
        default=None,
        description="Configuration mapping (same keys as the YAML `-Y` file).",
    )
    config_yaml: Optional[str] = Field(
        default=None,
        description="Legacy: whole YAML configuration as one string.",
    )

    @model_validator(mode="before")
    @classmethod
    def _accept_bare_config(cls, data: Any) -> Any:
        # トップレベルがそのまま設定（unitcell 等）の場合
        if isinstance(data, dict) and "config" not in data and "config_yaml" not in data:
            if "unitcell" in data or "genice3" in data or "exporter" in data:
                return {"config": data}
        return data

    @model_validator(mode="after")
    def _one_of(self) -> GenerateJsonBody:
        if self.config is None and self.config_yaml is None:
            raise ValueError("Provide `config` (object) or `config_yaml` (string)")
        return self


def _http_for_service_error(exc: ServiceError) -> HTTPException:
    detail: Any = exc.detail
    return HTTPException(status_code=exc.http_status, detail=detail)


def create_app() -> FastAPI:
    # Web は既定で JSON ログ（GENICE_LOG_FORMAT=text で人間向けに戻せる）
    setup_logging(debug=False, fmt=resolve_log_format(default="json"))

    app = FastAPI(
        title="GenIce3 Web API",
        version="0.1.0",
        description=_OPENAPI_DESCRIPTION.strip(),
        openapi_tags=_OPENAPI_TAGS,
    )

    origins = os.environ.get("GENICE3_CORS_ORIGINS", "*").strip()
    if origins:
        allow = ["*"] if origins == "*" else [o.strip() for o in origins.split(",") if o.strip()]
        app.add_middleware(
            CORSMiddleware,
            allow_origins=allow,
            allow_credentials=False,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    @app.middleware("http")
    async def bind_request_log_context(request: Request, call_next):
        token = bind_context(run_id=uuid.uuid4().hex[:8])
        try:
            return await call_next(request)
        finally:
            reset_context(token)

    @app.get("/health", tags=["health"], summary="Liveness check")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get(
        "/v1/meta/unitcells",
        tags=["meta"],
        summary="The catalogue of unit cell plugins",
    )
    def meta_unitcells() -> dict[str, Any]:
        return list_unitcells()

    @app.get(
        "/v1/meta/exporters",
        tags=["meta"],
        summary="The catalogue of exporter plugins, as table rows",
    )
    def meta_exporters() -> dict[str, Any]:
        return list_exporters()

    @app.get(
        "/v1/meta/unitcells/{name}/options",
        tags=["meta"],
        summary="The option schema of one unit cell",
    )
    def meta_unitcell_options(name: str) -> dict[str, Any]:
        try:
            return get_unitcell_options(name)
        except ServiceError as e:
            raise _http_for_service_error(e) from e

    @app.get(
        "/v1/meta/exporters/{name}/options",
        tags=["meta"],
        summary="The metadata of one exporter (includes media_type)",
    )
    def meta_exporter_options(name: str) -> dict[str, Any]:
        try:
            return get_exporter_options(name)
        except ServiceError as e:
            raise _http_for_service_error(e) from e

    def _run_generate(
        source: Union[str, dict[str, Any]],
        *,
        content_type: Optional[str],
        command_line: str,
    ) -> JSONResponse:
        t0 = time.time()
        try:
            result = generate(
                source,
                content_type=content_type,
                command_line=command_line,
            )
        except ServiceError as e:
            log_event(
                logger,
                ERROR,
                "run.error",
                e.message,
                error_type=type(e).__name__,
                error=str(e.detail),
            )
            raise _http_for_service_error(e) from e
        except Exception as e:
            log_event(
                logger,
                ERROR,
                "run.error",
                str(e),
                error_type=type(e).__name__,
                error=str(e),
            )
            raise HTTPException(status_code=500, detail=str(e)) from e

        meta = result["meta"]
        bind_context(
            unitcell=meta.get("unitcell"),
            exporter=meta.get("exporter"),
            seed=meta.get("seed"),
        )
        log_event(
            logger,
            INFO,
            "run.end",
            "Generation finished",
            duration_ms=round((time.time() - t0) * 1000.0, 3),
            ok=True,
            unitcell=meta.get("unitcell"),
            exporter=meta.get("exporter"),
            seed=meta.get("seed"),
        )
        return JSONResponse(content=result)

    @app.post(
        "/v1/generate",
        tags=["generate"],
        summary="Build a structure from a raw config body (YAML / TOML / JSON)",
        description=(
            "The **whole request body** is the configuration in UTF-8. "
            "`Content-Type` selects YAML / TOML / JSON (default: YAML). "
            "On success the status is **200** and the body is **JSON** with "
            "`meta`, `content`, and `media_type`. "
            "Omitted `seed` defaults to **1**."
        ),
        openapi_extra={
            "requestBody": {
                "required": True,
                "description": "Configuration text (CLI `-Y` schema).",
                "content": {
                    "text/plain": {
                        "schema": {"type": "string"},
                        "example": _GENERATE_YAML_EXAMPLE,
                    },
                    "application/x-yaml": {
                        "schema": {"type": "string"},
                        "example": _GENERATE_YAML_EXAMPLE,
                    },
                    "application/toml": {
                        "schema": {"type": "string"},
                    },
                    "application/json": {
                        "schema": {"type": "object"},
                    },
                },
            },
        },
    )
    async def generate_endpoint(request: Request) -> JSONResponse:
        try:
            raw = (await request.body()).decode("utf-8")
        except UnicodeDecodeError as e:
            raise HTTPException(status_code=400, detail="body must be UTF-8") from e
        return _run_generate(
            raw,
            content_type=request.headers.get("content-type"),
            command_line="POST /v1/generate",
        )

    @app.post(
        "/v1/generate/json",
        tags=["generate"],
        summary="Build a structure from a JSON config object (or legacy config_yaml)",
    )
    async def generate_json(payload: GenerateJsonBody) -> JSONResponse:
        if payload.config is not None:
            source: Union[str, dict[str, Any]] = payload.config
            ctype = "application/json"
        else:
            source = payload.config_yaml or ""
            ctype = "application/x-yaml"
        return _run_generate(
            source,
            content_type=ctype,
            command_line="POST /v1/generate/json",
        )

    return app


app = create_app()


def main() -> None:
    """``genice3-web`` コンソールスクリプトのエントリ。"""
    import uvicorn

    host = os.environ.get("GENICE3_HOST", "127.0.0.1")
    port = int(os.environ.get("GENICE3_PORT", "8000"))
    reload = os.environ.get("GENICE3_RELOAD", "").strip() in ("1", "true", "yes")
    uvicorn.run(
        "genice3.webapi:app",
        host=host,
        port=port,
        reload=reload,
    )


if __name__ == "__main__":
    main()
