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
        "Web API には FastAPI が必要です。例: pip install 'genice3[web]'"
    ) from e


_GENERATE_YAML_EXAMPLE = (
    "unitcell: 1h\n"
    "genice3:\n"
    "  rep: [1, 1, 1]\n"
    "exporter: gromacs\n"
)

_OPENAPI_DESCRIPTION = """
GenIce3（水素無秩序氷・クラスレート等の構造生成）の HTTP 薄ラッパーです。**CLI の `genice3` と同じ設定論理**を YAML で渡します。

## 典型フロー（エージェント向け）

1. **`GET /v1/meta/unitcells`** で利用可能な単位胞名を得る。
2. ユーザーが選んだ単位胞について **`GET /v1/meta/unitcells/{name}/options`** で、プラグイン固有オプション（`specific_options`）と多くの格子で共通のオプション（`common_options`）を得る。フォームを組む場合はここを参照。
3. 出力形式は **`GET /v1/meta/exporters`** と **`GET /v1/meta/exporters/{name}/options`** で調べる（`format_desc.suboptions` 等）。
4. **`POST /v1/generate`** に **YAML 全文をリクエストボディそのまま**（UTF-8）で送る。本文は CLI の **`-Y` 設定ファイルと同系統**（トップに `unitcell` / `genice3` / `exporter` 等）。成功時のレスポンスは **`text/plain`** で、内容は選んだ exporter のテキスト（例: GROMACS の .gro 相当のテキスト）。
5. どうしても **JSON ボディだけ**送れる場合は **`POST /v1/generate/json`** に `{"config_yaml": "<上記と同じYAML文字列>"}` を渡す（中身は `/v1/generate` と同一）。

## エラー

- **400**: YAML の解釈・必須欠如・未認識オプション・バリデーション失敗。`detail` は JSON（文字列またはオブジェクト）。
- **404**: メタ API で存在しないプラグイン名を指定したとき。
- **500**: 計算・出力段階の失敗。`detail` にメッセージ。

## 背景ドキュメント（人間・LLM 兼用）

- プロジェクトの要約: **https://genice-dev.github.io/GenIce3/for-ai-assistants/**
- マニュアル全体: **https://genice-dev.github.io/GenIce3**
"""

_OPENAPI_TAGS = [
    {
        "name": "generate",
        "description": "設定 YAML から構造テキストを生成する。メインは `POST /v1/generate`（生ボディ）。",
    },
    {
        "name": "meta",
        "description": "単位胞・exporter の一覧と、動的 UI / エージェント向けのオプションスキーマ。",
    },
    {
        "name": "health",
        "description": "稼働確認。",
    },
]


class GenerateJsonBody(BaseModel):
    """`application/json` で YAML 全文を渡すとき用（中身は `/v1/generate` と同じ）。"""

    config_yaml: str = Field(
        ...,
        description="CLI の `-Y` と同系統の YAML 全文（1 文字列にまとめる）",
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

    @app.get("/health", tags=["health"], summary="稼働確認")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get(
        "/v1/meta/unitcells",
        tags=["meta"],
        summary="単位胞プラグイン一覧",
        description=(
            "`unitcells.system` 等にプラグイン名の配列、`descriptions` に短い説明文。"
            "エージェントはここで得た名前を `GET .../unitcells/{name}/options` に渡す。"
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
        summary="exporter プラグイン一覧（表形式メタ）",
        description="`exporters` は行の配列。各 exporter の別名・拡張子・`suboptions` の説明文字列などが含まれる。",
    )
    def meta_exporters() -> dict[str, Any]:
        rows = get_exporter_format_rows()
        return {"exporters": rows}

    @app.get(
        "/v1/meta/unitcells/{name}/options",
        tags=["meta"],
        summary="指定単位胞のオプションスキーマ",
        description=(
            "`specific_options`: そのプラグインの `desc.options` 由来（`name`, `help`, `required`, `example`）。"
            "`common_options`: 多くの格子で使える共通キー（density, shift, anion, cation 等）の UI ヒント。"
            "`examples`: CLI / Python API / YAML の例文。"
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
        summary="指定 exporter のメタデータ",
        description="`format_desc`（`suboptions` 文字列含む）と `usage` テキスト。",
    )
    def meta_exporter_options(name: str) -> dict[str, Any]:
        try:
            return exporter_options_schema(name)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
        except ImportError as e:
            raise HTTPException(status_code=404, detail=str(e)) from e

    def _run_generate_from_yaml(body: str) -> Response:
        result = parsed_result_from_yaml_text(body)
        ok, errors = validate_result(result)
        if not ok:
            raise HTTPException(status_code=400, detail={"errors": errors})

        uc_u = result.get("unitcell", {}).get("unprocessed") or {}
        ex_u = result.get("exporter", {}).get("unprocessed") or {}
        if uc_u or ex_u:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "認識されなかったオプションがあります",
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
        summary="YAML 全文（生ボディ）で構造生成",
        description=(
            "**リクエストボディ全体**が YAML 文字列（UTF-8）。`Content-Type` は問わず解釈するが、"
            "OpenAPI 上は `text/plain` または `application/x-yaml` を推奨。"
            "成功時は **200** かつ **`text/plain`** 本文（exporter の出力）。"
            "事前に `GET /v1/meta/...` で単位胞名・オプション・exporter を確認すると安全。"
        ),
        openapi_extra={
            "requestBody": {
                "required": True,
                "description": "CLI の `-Y` と同系統の YAML 全文（UTF-8）。",
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
        summary="YAML 全文を JSON で包んで構造生成",
        description=(
            "`POST /v1/generate` と同じ処理。HTTP クライアントが **JSON しか送れない**とき用の別入口。"
            "フィールド `config_yaml` に、`/v1/generate` のボディに置くのと同じ YAML 文字列を入れる。"
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
