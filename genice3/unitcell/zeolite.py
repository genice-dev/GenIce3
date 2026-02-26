# Load a zeolite framework from IZA by 3-letter code.
# usage: genice3 zeolite --code LTA
# IZA: https://www.iza-structure.org/databases/

import os
import re
import tempfile
import urllib.request
from logging import getLogger
from typing import Any, Dict, Tuple

import genice3.unitcell
from genice3.unitcell import UnitCell as BaseUnitCell
from genice3.unitcell.CIF import UnitCell as CIFUnitCell

desc = {
    "ref": {"IZA": "https://www.iza-structure.org/databases/"},
    "brief": "Load a zeolite framework from IZA by 3-letter code (CIF via download).",
    "options": [
        {"name": "code", "help": "3-letter IZA framework code (e.g. LTA, FAU).", "required": True, "example": "LTA"},
        {"name": "osite", "help": "O site label or regex.", "required": False, "example": "O"},
        {"name": "hsite", "help": "H site label or regex (omit to let GenIce3 place H).", "required": False, "example": None},
    ],
    "test": ({"options": "--code LTA"},),
}

# IZA-SC download URL (Europe). Use download_cif.php for framework-only CIF.
IZA_BASE = "https://europe.iza-structure.org/IZA-SC"
IZA_FTC_TABLE_URL = IZA_BASE + "/ftc_table.php"
IZA_DOWNLOAD_CIF_URL = IZA_BASE + "/download_cif.php"

# Cache: 3-letter code (uppercase) -> framework ID
_code_to_id: Dict[str, int] = {}


def _scalar(v: Any) -> Any:
    if isinstance(v, (list, tuple)) and len(v) == 1:
        return v[0]
    return v


def _fetch_iza_code_to_id() -> Dict[str, int]:
    """Fetch IZA ftc_table and parse framework type code -> ID."""
    global _code_to_id
    if _code_to_id:
        return _code_to_id
    req = urllib.request.Request(
        IZA_FTC_TABLE_URL,
        headers={"User-Agent": "GenIce3/zeolite"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        html = resp.read().decode("utf-8", errors="replace")
    # e.g. href ="framework.php?ID=138">LTA </a> or ID=93">FAU
    pattern = re.compile(r'framework\.php\?ID=(\d+)[^>]*>\s*[\*\-]*([A-Z]{3})\s*</a>', re.IGNORECASE)
    for m in pattern.finditer(html):
        fid, code = int(m.group(1)), m.group(2).strip().upper()
        if code not in _code_to_id:
            _code_to_id[code] = fid
    return _code_to_id


def _download_iza_cif(framework_id: int) -> str:
    """Download framework CIF from IZA to a temporary file; return path."""
    url = f"{IZA_DOWNLOAD_CIF_URL}?ID={framework_id}"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "GenIce3/zeolite"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = resp.read().decode("utf-8", errors="replace")
    if "data_" not in body and "_cell_length_a" not in body:
        raise ValueError(
            f"IZA returned no CIF for framework ID {framework_id}. "
            "The server layout may have changed; check IZA-SC download_cif.php."
        )
    tmp = tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".cif",
        delete=False,
        encoding="utf-8",
    )
    tmp.write(body)
    tmp.close()
    return tmp.name


def parse_options(options: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    zeolite 固有: code, osite, hsite, water_model。
    残りは基底 UnitCell.parse_options に渡し、共通オプション（shift, density 等）をマージする。
    """
    processed: Dict[str, Any] = {}
    unprocessed = dict(options)
    for key in ("code", "osite", "hsite", "water_model"):
        if key in options:
            processed[key] = _scalar(options[key])
            unprocessed.pop(key, None)
    base_processed, base_unprocessed = BaseUnitCell.parse_options(unprocessed)
    processed.update(base_processed)
    unprocessed = base_unprocessed
    return processed, unprocessed


class UnitCell(genice3.unitcell.UnitCell):
    """
    IZA の 3-letter code でゼオライト骨格を指定し、CIF を取得して CIF プラグインで解釈する。
    """

    def __init__(self, **kwargs):
        logger = getLogger("zeolite")
        code = kwargs.get("code")
        if code is None:
            raise ValueError("zeolite unitcell requires --code (3-letter IZA framework code)")
        code = str(code).strip().upper()
        if len(code) != 3:
            raise ValueError(f"IZA framework code must be 3 letters, got: {code}")

        code_to_id = _fetch_iza_code_to_id()
        if code not in code_to_id:
            raise ValueError(
                f"Unknown IZA framework code: {code}. "
                f"Known codes (examples): {', '.join(sorted(code_to_id.keys())[:20])}..."
            )
        framework_id = code_to_id[code]
        logger.info("Fetching CIF for %s (framework ID %s) from IZA.", code, framework_id)

        try:
            tmp_path = _download_iza_cif(framework_id)
        except Exception as e:
            raise ValueError(f"Failed to download CIF from IZA for {code}: {e}") from e

        kwargs_cif = dict(kwargs)
        kwargs_cif.pop("code", None)
        kwargs_cif["file"] = tmp_path
        if kwargs_cif.get("osite") is None:
            kwargs_cif["osite"] = "T"  # Zeolite DB uses T for tetrahedral (degree-4) sites

        try:
            cif_cell = CIFUnitCell(**kwargs_cif)
        finally:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass

        # Copy attributes from the CIF-built unitcell into self (we inherit UnitCell but delegate build to CIF)
        self.cell = cif_cell.cell
        self.lattice_sites = cif_cell.lattice_sites
        self.graph = cif_cell.graph
        self.fixed = cif_cell.fixed
        self.anions = cif_cell.anions
        self.cations = cif_cell.cations
        self.cation_groups = getattr(cif_cell, "cation_groups", {})
        self._cages = cif_cell._cages
