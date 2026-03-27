# -*- coding: utf-8 -*-
from logging import getLogger, DEBUG, INFO, StreamHandler, Formatter
import sys


class ConfigurationError(Exception):
    """設定に関するエラーを表す例外"""

    pass


def _setup_logging(debug: bool) -> None:
    """ルートロガーの設定を統一する。

    debug=False: ユーザー向け。シンプルな `LEVEL: message` 表示（ロガー名は出さない）。
    debug=True: 開発者向け。`LEVEL logger:lineno: message` 形式で詳細情報を含める。
    """
    root = getLogger()

    # 既存のハンドラをすべて外す（basicConfig 等の影響を消す）
    for handler in root.handlers[:]:
        root.removeHandler(handler)

    handler = StreamHandler(sys.stderr)
    if debug:
        root.setLevel(DEBUG)
        handler.setLevel(DEBUG)
        fmt = "%(levelname)s %(name)s:%(lineno)d: %(message)s"
    else:
        root.setLevel(INFO)
        handler.setLevel(INFO)
        fmt = "%(levelname)s: %(message)s"
    handler.setFormatter(Formatter(fmt))
    root.addHandler(handler)


# API利用時にも明示的な呼び出しなしでINFOログが出るよう、
# ハンドラ未設定の場合だけデフォルト設定を適用する。
# （ユーザーが事前に basicConfig 等を呼んでいる場合はそちらを尊重する）
if not getLogger().handlers:
    _setup_logging(debug=False)
