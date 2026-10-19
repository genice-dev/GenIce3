from logging import ERROR, INFO, getLogger
import sys
import time
import uuid
from importlib.metadata import version, PackageNotFoundError

from genice3 import ConfigurationError, _setup_logging
from genice3.logging_config import bind_context, log_event, reset_context
from genice3.cli.runner import parse_argv, validate_result
from genice3.plugin import PluginNotFoundError
from genice3.cli.engine import run_parsed_result
from genice3.cli.options import (
    BASE_HELP_ORDER,
    get_option_def,
    format_option_for_help,
    extract_genice_args,
    validate_parsed_options,
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
    print()
    print(
        "Unitcell options (depend on UNITCELL; some unitcell may have additional options. Pass after UNITCELL):"
    )
    for line in _opt_line(
        "--density FLOAT",
        "Target density (e.g. g/cm3). Supported by many unit cells.",
    ):
        print(line)
    for line in _opt_line(
        "--shift X Y Z",
        "Shift fractional coordinates. Supported by many unit cells.",
    ):
        print(line)
    for line in _opt_line(
        "--cation INDEX=ION",
        "Cation at lattice site (unitcell-defined). May support :group suboption.",
    ):
        print(line)
    for line in _opt_line(
        "--anion INDEX=ION",
        "Anion at lattice site (unitcell-defined).",
    ):
        print(line)


def print_plugin_list(argv: list[str]) -> int:
    """Handle ``genice3 --list [CATEGORY]``."""
    from genice3.plugin import CATEGORIES, available_plugin_names, descriptions

    index = argv.index("--list")
    category = argv[index + 1] if index + 1 < len(argv) else ""
    if category in CATEGORIES:
        print(descriptions(category))
        return 0
    if category:
        print(f'Unknown plugin category "{category}".', file=sys.stderr)
    print("Usage: genice3 --list {" + "|".join(CATEGORIES) + "}")
    print()
    for name in CATEGORIES:
        print(f"  {name:<10} {len(available_plugin_names(name))} plugins")
    return 1 if category else 0


def run(argv: list[str]) -> int:
    """CLI と同じ処理を ``sys.argv[1:]`` 相当の ``argv`` で実行する。

    戻り値はプロセスの終了コード（0 が成功）。ヘルプ・バージョン表示時も 0。
    標準出力・標準エラーは呼び出し側の ``sys.stdout`` / ``sys.stderr`` に書く。
    """
    if len(argv) == 0 or "--help" in argv or "-h" in argv:
        print_help()
        return 0
    if "--version" in argv or "-V" in argv:
        print(f"genice3 {get_version()}")
        return 0
    if "--list" in argv:
        return print_plugin_list(argv)

    run_id = uuid.uuid4().hex[:8]
    ctx_token = bind_context(run_id=run_id)
    _setup_logging(debug=False)
    logger = getLogger()
    t0 = time.time()

    try:
        try:
            result = parse_argv(argv)
        except (PluginNotFoundError, ConfigurationError) as e:
            # These name the valid alternatives; a traceback would only bury them.
            log_event(
                logger,
                ERROR,
                "run.error",
                str(e),
                error_type=type(e).__name__,
                error=str(e),
            )
            return 1
        except Exception as e:
            logger.error(f"Failed to parse the command line: {e}")
            import traceback

            traceback.print_exc()
            return 1

        is_valid, errors = validate_result(result)
        if not is_valid:
            for error in errors:
                log_event(
                    logger,
                    ERROR,
                    "run.error",
                    error,
                    error_type="ValidationError",
                    error=error,
                )
            return 1

        uc_unprocessed = result.get("unitcell", {}).get("unprocessed") or {}
        ex_unprocessed = result.get("exporter", {}).get("unprocessed") or {}
        if uc_unprocessed or ex_unprocessed:
            parts = []
            if uc_unprocessed:
                parts.append(f"unitcell: {list(uc_unprocessed.keys())}")
            if ex_unprocessed:
                parts.append(f"exporter: {list(ex_unprocessed.keys())}")
            msg = "Unrecognized options; stopping: %s" % ", ".join(parts)
            log_event(
                logger,
                ERROR,
                "run.error",
                msg,
                error_type="UnrecognizedOptions",
                error=msg,
            )
            return 1

        base_options = result["base_options"]
        debug = bool(base_options.get("debug"))
        log_format = base_options.get("log_format")
        _setup_logging(debug=debug, fmt=log_format)
        logger = getLogger()

        try:
            validate_parsed_options(base_options)
        except ValueError as e:
            log_event(
                logger,
                ERROR,
                "run.error",
                str(e),
                error_type=type(e).__name__,
                error=str(e),
            )
            return 1

        genice_kwargs = extract_genice_args(base_options)
        logger.debug(f"Settings: {genice_kwargs}")

        unitcell_name = result["unitcell"]["name"]
        unitcell_processed = result["unitcell"]["processed"]
        exporter_name = result["exporter"]["name"] or "gromacs"
        exporter_processed = result["exporter"]["processed"]
        seed = genice_kwargs.get("seed")

        bind_context(
            unitcell=unitcell_name,
            exporter=exporter_name,
            seed=seed,
        )

        log_event(
            logger,
            INFO,
            "run.start",
            "Starting generation",
            unitcell=unitcell_name,
            exporter=exporter_name,
            seed=seed,
        )

        if unitcell_processed:
            logger.info("unitcell %s options: %s", unitcell_name, unitcell_processed)
        molecule_related = {
            k: genice_kwargs.get(k)
            for k in ("guests", "spot_guests", "spot_anions", "spot_cations")
            if genice_kwargs.get(k)
        }
        if molecule_related:
            logger.info("molecule-related options: %s", molecule_related)
        if exporter_processed:
            logger.info("exporter %s options: %s", exporter_name, exporter_processed)

        cmd = " ".join(["genice3", *argv])
        try:
            run_parsed_result(result, sys.stdout, command_line=cmd)
        except (PluginNotFoundError, ConfigurationError) as e:
            log_event(
                logger,
                ERROR,
                "run.error",
                str(e),
                error_type=type(e).__name__,
                error=str(e),
            )
            return 1
        except Exception as e:
            logger.exception(
                "exporter.dump failed",
                extra={
                    "event": "run.error",
                    "error_type": type(e).__name__,
                    "error": str(e),
                },
            )
            return 1

        duration_ms = round((time.time() - t0) * 1000.0, 3)
        log_event(
            logger,
            INFO,
            "run.end",
            "Generation finished",
            duration_ms=duration_ms,
            ok=True,
        )
        return 0
    finally:
        reset_context(ctx_token)


def main() -> None:
    """メイン関数"""
    raise SystemExit(run(sys.argv[1:]))


if __name__ == "__main__":
    main()
