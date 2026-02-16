from logging import getLogger, basicConfig, DEBUG, INFO
import sys
from importlib.metadata import version, PackageNotFoundError

from genice3.plugin import safe_import
from genice3.genice import GenIce3
from genice3.cli.pool_parser import PoolBasedParser
from genice3.cli.options import (
    GENICE3_OPTION_DEFS,
    BASE_HELP_ORDER,
    get_option_def,
    format_option_for_help,
    extract_genice_args,
)

def get_version():
    """パッケージのバージョンを取得する。見つからない場合はデフォルト値を返す。"""
    try:
        return version("genice3")
    except PackageNotFoundError:
        return "3.*.*.*"


# ヘルプ整形: 先頭2スペース＋オプション書式が24文字超なら改行。説明は28〜72桁で折り返し。
_HELP_OPTION_MAX = 24  # 2スペース＋オプションがこの桁数までなら1行に
_HELP_DESC_START = 28  # 説明開始桁（1-based）
_HELP_DESC_END = 72
_HELP_DESC_WIDTH = _HELP_DESC_END - _HELP_DESC_START + 1  # 45


def _wrap_desc(text: str, width: int) -> list[str]:
    """説明文を width 文字で折り返した行リストを返す"""
    words = text.split()
    lines: list[str] = []
    current: list[str] = []
    current_len = 0
    for w in words:
        need = len(w) + (1 if current else 0)
        if current_len + need <= width:
            current.append(w)
            current_len += need
        else:
            if current:
                lines.append(" ".join(current))
            current = [w]
            current_len = len(w)
    if current:
        lines.append(" ".join(current))
    return lines


def _opt_line(option: str, description: str) -> list[str]:
    """オプション1件を指定ルールで整形。2スペース＋オプションが24文字超なら改行。説明は28〜72桁で折り畳み。"""
    head_len = 2 + len(option)  # 先頭2スペース＋オプション
    desc_lines = _wrap_desc(description, _HELP_DESC_WIDTH)
    indent = " " * (_HELP_DESC_START - 1)  # 説明行の左インデント（27スペース）

    if head_len > _HELP_OPTION_MAX:
        # オプションだけ1行、説明は次の行から28桁目から
        out = ["  " + option]
        for line in desc_lines:
            out.append(indent + line)
        return out
    # オプション＋説明を同じ行から（オプション後に空白を入れて28桁目に合わせる）
    pad = _HELP_DESC_START - 1 - head_len  # 2 + len(option) + pad == 27
    out = ["  " + option + " " * pad + desc_lines[0]]
    for line in desc_lines[1:]:
        out.append(indent + line)
    return out


def print_help():
    """ヘルプメッセージを表示（options のオプション定義から組み立て）"""
    print("Usage: genice3 [OPTIONS] UNITCELL")
    print()
    print("Options:")
    seen = set()  # rep / replication_factors は同じ行なので1回だけ表示
    for name in BASE_HELP_ORDER:
        if name in seen:
            continue
        def_ = get_option_def(name)
        if def_ is None or def_.help_text is None:
            continue
        if def_.name == "replication_factors":
            seen.add("rep")
        seen.add(def_.name)
        opt_str = format_option_for_help(def_)
        for line in _opt_line(opt_str, def_.help_text):
            print(line)
    print()
    print("Arguments:")
    for line in _opt_line("UNITCELL", "Unitcell plugin name (required)"):
        print(line)


def main() -> None:
    """メイン関数"""
    # --helpと--versionを先に処理
    if "--help" in sys.argv or "-h" in sys.argv:
        print_help()
        sys.exit(0)
    if "--version" in sys.argv or "-V" in sys.argv:
        print(f"genice3 {get_version()}")
        sys.exit(0)

    # ロギングを初期化（デフォルトはINFOレベル）
    basicConfig(level=INFO)
    logger = getLogger()

    parser = PoolBasedParser(GENICE3_OPTION_DEFS)
    try:
        parser.parse_args(sys.argv[1:])
    except Exception as e:
        logger.error(f"パースエラー: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)

    result = parser.get_result()

    # バリデーション
    is_valid, errors = parser.validate()
    if not is_valid:
        for error in errors:
            logger.error(error)
        sys.exit(1)

    base_options = result["base_options"]
    if base_options.get("debug"):
        logger.setLevel(DEBUG)
        for handler in logger.handlers:
            handler.setLevel(DEBUG)

    genice_kwargs = extract_genice_args(base_options)
    logger.debug(f"Settings: {genice_kwargs}")

    unitcell_name = result["unitcell"]["name"]
    unitcell_processed = result["unitcell"]["processed"]
    exporter_name = result["exporter"]["name"] or "gromacs"
    exporter_processed = result["exporter"]["processed"]

    genice = GenIce3(**genice_kwargs)

    # unitcellプラグインを設定
    genice.unitcell = safe_import("unitcell", unitcell_name).UnitCell(
        **unitcell_processed
    )

    # コマンドライン全体を取得
    command_line = " ".join(sys.argv)
    exporter_processed["command_line"] = command_line

    # exporterプラグインを実行
    safe_import("exporter", exporter_name).dump(
        genice, sys.stdout, **exporter_processed
    )


if __name__ == "__main__":
    main()
