# 回帰テスト用 Makefile.rules を生成する。
# A: 参照出力を reference/ に保存して比較
# C: make update-reference で参照を更新
#
# 実行: tests/auto から make test / make update-reference
import sys
import glob
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from genice3 import plugin
from logging import getLogger, basicConfig, INFO

basicConfig(level=INFO)
logger = getLogger()


def supports_ion_doping(ice: str) -> bool:
    """unitcell がイオンドープをサポートするか（水素秩序氷では False）"""
    try:
        mod = plugin.safe_import("unitcell", ice)
        return getattr(mod.UnitCell, "SUPPORTS_ION_DOPING", True)
    except Exception:
        return True


def options_parser(options):
    if type(options) == dict:
        return ":".join([f"{x}={y}" for x, y in options.items()])
    return options


def compose_long_line_from_list(items: list, N=70):
    while True:
        line = ""
        while len(line) < N and items:
            line += " " + items.pop(0)
        yield line + "\\\n"
        if not items:
            yield line + "\\\n"
            break


def make_test(ice: str, tests: dict, formatters: dict):
    for formatter_prefix, formatter_path in formatters.items():
        for i, test in enumerate(tests):
            product = f"{ice}_{i}.{formatter_prefix}"

            genice_options = ""
            module_options = ""

            logger.debug(f"{ice} {test}")
            if "options" in test:
                genice_options = test["options"]
            if "args" in test:
                module_options = options_parser(test["args"])

            # 決定的なオプション（random を使わない）
            opts = additional_options_base.copy()
            if supports_ion_doping(ice):
                if ice in ("6", "ice6"):
                    opts.extend(additional_options_doping_6)
                elif ice in ("HS1",):
                    pass
                else:
                    opts.extend(additional_options_doping)
            genice_options += " " + " ".join(opts)
            genice_options += f" -e {formatter_prefix}"
            if module_options != "":
                module_options = "[" + module_options + "]"
            target = f"{ice}{module_options}"
            logger.debug(f"Target: {target}")

            # test: 現在の出力を reference/ と比較（stderr は $*.log に記録）
            rule = f"{product}.diff: reference/{product}\n"
            rule += f"\t@mkdir -p reference\n"
            rule += f"\t$(GENICE) {target} {genice_options} 2> $*.log | diff - reference/{product}\n"
            rule += f"\t@touch $@\n\n"

            # update-reference: reference/ に出力とログを保存
            rule += f"reference/{product}: ../../genice3/unitcell/{ice}.py  {formatter_path}\n"
            rule += f"\t@mkdir -p reference\n"
            rule += f"\t$(GENICE) {target} {genice_options} > $@ 2> $@.log\n\n"

            yield product, rule


# GenIce3 CLI 互換のオプション（決定的な出力のため --seed 必須）
additional_options_base = [
    "--seed 1",
    "--water 4site",
]
# 水素秩序氷ではドーピング不可なので、イオンドープ可能な unitcell のみに付与
additional_options_doping = [
    "--spot_cation 0=Na --spot_anion 3=Cl",
]
additional_options_doping_6 = [
    "--spot_cation 0=Na --spot_anion 5=Cl",
]


def formatter_list():
    formatter_paths = {}
    for filepath in glob.glob("../../genice3/exporter/*.py"):
        if not os.path.islink(filepath):
            formatter_prefix = os.path.basename(filepath).split(".")[0]
            if formatter_prefix in ("raw", "null", "__init__", "_KG", "plotly"):
                continue
            formatter_paths[formatter_prefix] = filepath
    return formatter_paths


result = plugin.scan("unitcell")
# preinstalled (system) plugins only
ices = result["system"]
tests = result["tests"]
formatters = formatter_list()


# print(tests)
# sys.exit(0)

products_prepare = []
products_test = []
rules = ""


for ice in ices:
    if ice in ("iceR",):
        continue
    if ice not in tests:
        tests[ice] = ("",)

    for product, rule in make_test(ice, tests[ice], formatters):
        products_prepare.append(product)
        products_test.append(product)
        rules += rule

# GenIce3 を python -m で実行（ソースツリーから直接実行可能）
print("GENICE=python -m genice3.cli.genice")
targets = compose_long_line_from_list(products_prepare)
print("TARGETS=", *targets)
print("# 参照出力を更新（意図した変更時のみ実行し、git add してコミット）")
print("update-reference: $(addprefix reference/,$(TARGETS))")
print("# 現在の出力を参照と比較（参照が無ければ自動生成してから比較）")
print("test: $(foreach file,$(TARGETS),$(file).diff)")
print(rules)
