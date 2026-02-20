"""
genice3 CLI のオプション検証

パース直後に実行する parse_validator を定義。
runtime_validator（構造体などコンテキストが必要）は必要になったら追加。
"""

from typing import Any, Dict, Sequence

from genice3.cli.option_def import OptionDef


# =============================================================================
# parse_validator 関数（パース直後に実行、コンテキスト不要）
# =============================================================================


def validate_seed(value: Any) -> None:
    """seed は非負整数であること"""
    if value is None:
        return
    try:
        v = int(value)
        if v < 0:
            raise ValueError(f"--seed must be non-negative, got: {v}")
    except (TypeError, ValueError) as e:
        if isinstance(e, ValueError) and "non-negative" in str(e):
            raise
        raise ValueError(f"--seed must be an integer, got: {value}") from e


def validate_replication_factors(value: Any) -> None:
    """replication_factors は 1〜3 個の正の整数であること"""
    if value is None:
        return
    t = value if isinstance(value, (tuple, list)) else (value,)
    if len(t) < 1 or len(t) > 3:
        raise ValueError(
            f"--rep / --replication_factors must have 1–3 values, got {len(t)}"
        )
    for v in t:
        try:
            n = int(v)
            if n < 1:
                raise ValueError(
                    f"--rep / --replication_factors values must be positive, got: {v}"
                )
        except (TypeError, ValueError) as e:
            if isinstance(e, ValueError) and "positive" in str(e):
                raise
            raise ValueError(
                f"--rep / --replication_factors must be integers, got: {v}"
            ) from e


def validate_depol_loop(value: Any) -> None:
    """depol_loop は正の整数であること"""
    if value is None:
        return
    try:
        n = int(value)
        if n < 1:
            raise ValueError(f"--depol_loop must be positive, got: {n}")
    except (TypeError, ValueError) as e:
        if isinstance(e, ValueError) and "positive" in str(e):
            raise
        raise ValueError(f"--depol_loop must be an integer, got: {value}") from e


def validate_target_polarization(value: Any) -> None:
    """target_polarization は3個の数値であること"""
    if value is None:
        return
    if hasattr(value, "shape") and value.shape == (3,):
        return
    t = value if isinstance(value, (tuple, list)) else (value,)
    if len(t) != 3:
        raise ValueError(
            f"--target_polarization must have exactly 3 values, got: {len(t)}"
        )
    for v in t:
        try:
            float(v)
        except (TypeError, ValueError):
            raise ValueError(
                f"--target_polarization must be numbers, got: {value}"
            ) from None


def validate_replication_matrix(value: Any) -> None:
    """replication_matrix は9個の整数であること"""
    if value is None:
        return
    t = value if isinstance(value, (tuple, list)) else (value,)
    if hasattr(value, "size"):
        t = list(value.flatten())
    if len(t) != 9:
        raise ValueError(
            f"--replication_matrix must have exactly 9 integers, got: {len(t)}"
        )
    for v in t:
        try:
            int(v)
        except (TypeError, ValueError):
            raise ValueError(
                f"--replication_matrix must be integers, got: {value}"
            ) from None


def validate_spot_ion_dict(value: Any, option_name: str) -> None:
    """spot_cation / spot_anion の辞書: キーは非負整数、または '51=N' 形式（= の前がサイト番号）"""
    if value is None or (isinstance(value, dict) and not value):
        return
    if not isinstance(value, dict):
        raise ValueError(
            f"--{option_name} must be key=value format or bracketed, got: {type(value).__name__}"
        )
    for k in value.keys():
        key_str = str(k).strip()
        # '51=N' 形式なら = の前をサイト番号として検証
        if "=" in key_str:
            key_str = key_str.split("=", 1)[0].strip()
        try:
            idx = int(key_str)
            if idx < 0:
                raise ValueError(
                    f"--{option_name} site index must be non-negative, got: {k}"
                )
        except (TypeError, ValueError) as e:
            if isinstance(e, ValueError) and "non-negative" in str(e):
                raise
            raise ValueError(
                f"--{option_name} site index must be an integer (or LABEL=ION), got: {k}"
            ) from e


# =============================================================================
# 一括検証
# =============================================================================


def validate_parsed_options(
    base_options: Dict[str, Any],
    option_defs: Sequence[OptionDef],
) -> None:
    """
    パース済み base_options に対して parse_validator を実行する。
    エラーがあれば ValueError を raise する。
    """
    for def_ in option_defs:
        if def_.parse_validator is None:
            continue
        # rep は build_options_dict で replication_factors に正規化される
        key = "replication_factors" if def_.name == "rep" else def_.name
        if key not in base_options:
            continue
        def_.parse_validator(base_options[key])
