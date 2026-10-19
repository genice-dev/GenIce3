# -*- coding: utf-8 -*-
from logging import getLogger

from genice3.logging_config import setup_logging as _setup_logging_impl


class ConfigurationError(Exception):
    """設定に関するエラーを表す例外"""

    pass


def _setup_logging(debug: bool = False, fmt: str | None = None) -> str:
    """ルートロガーの設定を統一する（:func:`genice3.logging_config.setup_logging` への薄いラップ）。"""
    return _setup_logging_impl(debug=debug, fmt=fmt)


# API利用時にも明示的な呼び出しなしでINFOログが出るよう、
# ハンドラ未設定の場合だけデフォルト設定を適用する。
# （ユーザーが事前に basicConfig 等を呼んでいる場合はそちらを尊重する）
if not getLogger().handlers:
    _setup_logging(debug=False)
