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


def args_to_cli(args):
    """unitcell 用 args 辞書を CLI オプション文字列に（--key val または --key v1 v2 v3）"""
    if not args or type(args) != dict:
        return ""
    parts = []
    for k, v in args.items():
        parts.append(f"--{k}")
        if isinstance(v, (list, tuple)):
            parts.extend(str(x) for x in v)
        else:
            parts.append(str(v))
    return " " + " ".join(parts)


def normalize_legacy_options(opts_str: str) -> str:
    """unitcell desc['test'] 由来の旧形式オプションを新形式に置換"""
    if not opts_str:
        return opts_str
    s = opts_str.replace(" -r ", " --rep ")
    return s


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
            logger.debug(f"{ice} {test}")
            # 単位胞オプション（旧 args）を --key val 形式で先頭に
            if "args" in test:
                genice_options = args_to_cli(test["args"])
            if "options" in test:
                genice_options = (
                    genice_options + " " + normalize_legacy_options(test["options"])
                ).strip()

            # 決定的なオプション（random を使わない）
            opts = additional_options_base.copy()
            if supports_ion_doping(ice):
                if ice in ("6", "ice6"):
                    opts.extend(additional_options_doping_6)
                elif ice in ("HS1",):
                    pass
                else:
                    opts.extend(additional_options_doping)
            genice_options = (genice_options + " " + " ".join(opts)).strip()
            # 新形式: --exporter name、gromacs のときは :water_model 4site
            genice_options += f" --exporter {formatter_prefix}"
            if formatter_prefix == "gromacs":
                genice_options += " :water_model 4site"
            target = ice
            logger.debug(f"Target: {target} {genice_options}")

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
# --water は exporter サブオプション（gromacs 時は --exporter gromacs :water_model 4site で付与）
additional_options_base = [
    "--seed 1",
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
