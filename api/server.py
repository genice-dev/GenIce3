"""
GenIce3 結晶構造生成API（たたき台）

JSON で結晶構造リクエストを受け取り、酸素骨格＋水素結合を PDB 形式で返す。
gromacs エクスポーターを使わず、水素配置（depol_loop）を必要としない。
"""
import logging
from typing import Any, Optional

import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# プロジェクトルートを path に追加（api パッケージの import のため）
import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from genice3.genice import GenIce3
from genice3 import ConfigurationError
from genice3.plugin import UnitCell

from api.skeleton import lattice_sites_to_pdb

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="GenIce3 API",
    description="結晶構造（酸素骨格＋水素結合）を生成するAPI",
    version="0.1.0",
)


# --- リクエスト/レスポンススキーマ ---


class GenerateRequest(BaseModel):
    """結晶構造生成リクエスト"""

    unitcell: str = Field(..., description="単位胞名（例: 1h, A15, ice1h）")
    rep: list[int] = Field(default=[2, 2, 2], description="複製 [nx, ny, nz]")
    unitcell_options: Optional[dict[str, Any]] = Field(
        default=None,
        description="単位胞オプション（shift, density, assess_cages など）",
    )
    seed: Optional[int] = Field(default=None, description="乱数シード（骨格では未使用）")


class GenerateResponse(BaseModel):
    """結晶構造生成レスポンス"""

    pdb: str = Field(..., description="PDB形式（酸素＋CONECT）")
    format: str = Field(default="pdb", description="出力形式")
    cell: list[list[float]] = Field(..., description="セル行列 3x3 (nm)")
    water_count: int = Field(..., description="水分子（酸素）数")
    cages: Optional[dict[str, Any]] = Field(
        default=None,
        description="ケージ情報（assess_cages 時のみ）",
    )


class ErrorResponse(BaseModel):
    """エラーレスポンス"""

    detail: str
    error_type: Optional[str] = None


# --- エンドポイント ---


@app.get("/health")
def health():
    """ヘルスチェック"""
    return {"status": "ok"}


@app.post("/generate", response_model=GenerateResponse)
def generate(req: GenerateRequest) -> GenerateResponse:
    """
    結晶骨格（酸素＋水素結合）を生成する。
    depol_loop は使用しないため、イオン配置など不正な設定でも失敗しない。
    """
    try:
        rep = req.rep
        if len(rep) != 3:
            raise HTTPException(status_code=400, detail="rep must have 3 elements [nx, ny, nz]")

        replication_matrix = np.diag(rep)
        uc_opts = req.unitcell_options or {}

        genice = GenIce3(
            depol_loop=0,
            replication_matrix=replication_matrix,
        )
        genice.unitcell = UnitCell(req.unitcell, **uc_opts)

        lattice_sites = genice.lattice_sites
        graph = genice.graph
        cell = genice.cell

        pdb_str = lattice_sites_to_pdb(
            lattice_sites_frac=lattice_sites,
            graph=graph,
            cell=cell,
        )

        cages_data = None
        if genice.cages is not None:
            raw = genice.cages.to_json_capable_data()
            # JSON のキーは文字列必須。int キーを str に変換。
            cages_data = {str(k): v for k, v in raw.items()}

        return GenerateResponse(
            pdb=pdb_str,
            format="pdb",
            cell=cell.tolist(),
            water_count=len(lattice_sites),
            cages=cages_data,
        )

    except ConfigurationError as e:
        logger.warning(f"ConfigurationError: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except ValueError as e:
        logger.warning(f"ValueError: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Unexpected error in /generate")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
