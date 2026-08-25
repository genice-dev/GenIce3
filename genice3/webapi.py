"""
GenIce3 の薄い HTTP 層（FastAPI）。

依存: ``pip install "genice3[web]"`` 後に ``genice3-web`` または
``uvicorn genice3.webapi:app`` で起動。

入力は CLI の ``-Y`` と同系統の YAML 全文（unitcell / genice3 / exporter を含む）。
出力は exporter 由来のプレーンテキスト（既定 ``text/plain; charset=utf-8``）。
"""

from __future__ import annotations

import os
from io import StringIO
from typing import Any

from pydantic import BaseModel, Field

from genice3.cli.engine import run_parsed_result
from genice3.cli.meta_schema import exporter_options_schema, unitcell_options_schema
from genice3.cli.options import validate_parsed_options
from genice3.cli.runner import parsed_result_from_yaml_text, validate_result
from genice3.plugin import get_exporter_format_rows, scan

try:
    from fastapi import FastAPI, HTTPException, Request, Response
    from fastapi.middleware.cors import CORSMiddleware
except ModuleNotFoundError as e:  # pragma: no cover
    raise ModuleNotFoundError(
        "The web API needs FastAPI. Install it with: pip install 'genice3[web]'"
    ) from e


_GENERATE_YAML_EXAMPLE = (
    "unitcell: 1h\n"
    "genice3:\n"
    "  rep: [1, 1, 1]\n"
    "exporter: gromacs\n"
)

_OPENAPI_DESCRIPTION = """
A thin HTTP wrapper around GenIce3, which builds hydrogen-disordered ice and
clathrate hydrate structures. The configuration is the **same YAML that the
`genice3` command line reads with `-Y`**.

## Typical flow (for agents)

1. **`GET /v1/meta/unitcells`** for the names of the available unit cells.
2. **`GET /v1/meta/unitcells/{name}/options`** for the options of the chosen one:
   `specific_options` are the options of that plugin, `common_options` are the keys
   that most lattices accept. Build a form from these.
3. **`GET /v1/meta/exporters`** and **`GET /v1/meta/exporters/{name}/options`** for the
   output formats and their suboptions (`format_desc.suboptions`).
4. **`POST /v1/generate`** with the **whole YAML as the request body** (UTF-8). The body
   has the same shape as the `-Y` configuration file, with `unitcell`, `genice3`, and
   `exporter` at the top level. A successful response is **`text/plain`**: the output of
   the chosen exporter, for example the text of a GROMACS `.gro` file.
5. If your client can send **only JSON**, post
   `{"config_yaml": "<the same YAML string>"}` to **`POST /v1/generate/json`** instead;
   it does the same thing.

## Errors

- **400**: the YAML could not be read, a required key is missing, an option was not
  recognized, or validation failed. `detail` is JSON, either a string or an object.
- **404**: a meta endpoint was given a plugin name that does not exist.
- **500**: the construction or the export failed. `detail` carries the message.

## Background documents (for humans and for LLMs alike)

- Project summary: **https://genice-dev.github.io/GenIce3/for-ai-assistants/**
- Full manual: **https://genice-dev.github.io/GenIce3**
"""

_OPENAPI_TAGS = [
    {
        "name": "generate",
        "description": "Build a structure from a configuration in YAML. The main entry is `POST /v1/generate`, which takes the raw body.",
    },
    {
        "name": "meta",
        "description": "The catalogue of unit cells and exporters, and their option schemas, for dynamic user interfaces and for agents.",
    },
    {
        "name": "health",
        "description": "Liveness check.",
    },
]


class GenerateJsonBody(BaseModel):
    """Carries the whole YAML as `application/json`; the content is that of `/v1/generate`."""

    config_yaml: str = Field(
        ...,
        description="The whole YAML configuration, as one string, in the form the CLI reads with `-Y`.",
        examples=[
            "unitcell: 1h\ngenice3:\n  rep: [1, 1, 1]\nexporter: gromacs\n"
        ],
    )


def create_app() -> FastAPI:
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

    @app.get("/health", tags=["health"], summary="Liveness check")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get(
        "/v1/meta/unitcells",
        tags=["meta"],
        summary="The catalogue of unit cell plugins",
        description=(
            "`unitcells.system`, `.extra`, and `.local` are arrays of plugin names; "
            "`descriptions` maps a name to its one-line description. "
            "Pass a name from here to `GET .../unitcells/{name}/options`."
        ),
    )
    def meta_unitcells() -> dict[str, Any]:
        data = scan("unitcell")
        return {
            "unitcells": {
                "system": data.get("system", []),
                "extra": data.get("extra", []),
                "local": data.get("local", []),
            },
            "descriptions": data.get("desc", {}),
        }

    @app.get(
        "/v1/meta/exporters",
        tags=["meta"],
        summary="The catalogue of exporter plugins, as table rows",
        description=(
            "`exporters` is an array of rows. `name` is the plain plugin name to use in "
            "this API, `aliases` lists its other names, and `extension` and `suboptions` "
            "describe the file it writes."
        ),
    )
    def meta_exporters() -> dict[str, Any]:
        rows = get_exporter_format_rows(markdown_name=False)
        return {"exporters": rows}

    @app.get(
        "/v1/meta/unitcells/{name}/options",
        tags=["meta"],
        summary="The option schema of one unit cell",
        description=(
            "`specific_options` comes from the plugin's own `desc.options`, each with "
            "`name`, `help`, `required`, and `example`. "
            "`common_options` are the keys that most lattices accept (density, shift, "
            "anion, cation, and so on), with hints for a user interface. "
            "`examples` gives the same request written for the CLI, the Python API, and YAML."
        ),
    )
    def meta_unitcell_options(name: str) -> dict[str, Any]:
        try:
            return unitcell_options_schema(name)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
        except ImportError as e:
            raise HTTPException(status_code=404, detail=str(e)) from e

    @app.get(
        "/v1/meta/exporters/{name}/options",
        tags=["meta"],
        summary="The metadata of one exporter",
        description="Its `format_desc`, including the `suboptions` string, and its `usage` text.",
    )
    def meta_exporter_options(name: str) -> dict[str, Any]:
        try:
            return exporter_options_schema(name)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
        except ImportError as e:
            raise HTTPException(status_code=404, detail=str(e)) from e

    def _run_generate_from_yaml(body: str) -> Response:
        try:
            result = parsed_result_from_yaml_text(body)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
        ok, errors = validate_result(result)
        if not ok:
            raise HTTPException(status_code=400, detail={"errors": errors})

        uc_u = result.get("unitcell", {}).get("unprocessed") or {}
        ex_u = result.get("exporter", {}).get("unprocessed") or {}
        if uc_u or ex_u:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "Some options were not recognized",
                    "unitcell_unprocessed": list(uc_u.keys()),
                    "exporter_unprocessed": list(ex_u.keys()),
                },
            )

        base = result["base_options"]
        try:
            validate_parsed_options(base)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e

        buf = StringIO()
        try:
            run_parsed_result(result, buf, command_line="POST /v1/generate")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e)) from e

        return Response(
            content=buf.getvalue(),
            media_type="text/plain; charset=utf-8",
        )

    @app.post(
        "/v1/generate",
        tags=["generate"],
        summary="Build a structure from a raw YAML body",
        description=(
            "The **whole request body** is the YAML configuration, in UTF-8. Any "
            "`Content-Type` is accepted, but `text/plain` or `application/x-yaml` is "
            "what the OpenAPI schema declares. "
            "On success the status is **200** and the body is **`text/plain`**: the output "
            "of the exporter. "
            "Confirming the unit cell name, its options, and the exporter through "
            "`GET /v1/meta/...` beforehand avoids most 400s."
        ),
        openapi_extra={
            "requestBody": {
                "required": True,
                "description": "The whole YAML configuration in UTF-8, in the form the CLI reads with `-Y`.",
                "content": {
                    "text/plain": {
                        "schema": {"type": "string"},
                        "example": _GENERATE_YAML_EXAMPLE,
                    },
                    "application/x-yaml": {
                        "schema": {"type": "string"},
                        "example": _GENERATE_YAML_EXAMPLE,
                    },
                },
            },
        },
    )
    async def generate(request: Request) -> Response:
        try:
            raw = (await request.body()).decode("utf-8")
        except UnicodeDecodeError as e:
            raise HTTPException(status_code=400, detail="body must be UTF-8") from e
        return _run_generate_from_yaml(raw)

    @app.post(
        "/v1/generate/json",
        tags=["generate"],
        summary="Build a structure from a YAML string wrapped in JSON",
        description=(
            "The same work as `POST /v1/generate`, for clients that can send **only JSON**. "
            "Put in the field `config_yaml` the same YAML string that would be the body of "
            "`/v1/generate`."
        ),
    )
    async def generate_json(payload: GenerateJsonBody) -> Response:
        return _run_generate_from_yaml(payload.config_yaml)

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
