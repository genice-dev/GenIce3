"""
genice3 CLI runner の統合テスト（option_parser ベース）
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from genice3.cli.runner import parse_argv, validate_result


def test_basic_parsing():
    """基本的なパースのテスト"""
    result = parse_argv(["A15", "--exporter", "gromacs", "--rep", "2", "2", "2"])

    assert result["unitcell"]["name"] == "A15"
    assert result["exporter"]["name"] == "gromacs"
    assert result["base_options"]["replication_factors"] == (2, 2, 2)
    print("✓ 基本パーステスト成功")


def test_complex_parsing():
    """複雑なパースのテスト"""
    result = parse_argv(
        [
            "A15",
            "--exporter",
            "gromacs",
            "--rep",
            "2",
            "2",
            "2",
            "--seed",
            "42",
            "--spot_anion",
            "1=Cl",
            "--spot_cation",
            "5=Na",
        ]
    )

    assert result["unitcell"]["name"] == "A15"
    assert result["exporter"]["name"] == "gromacs"
    assert result["base_options"]["seed"] == 42
    assert result["base_options"]["spot_anion"] == {"1": "Cl"}
    assert result["base_options"]["spot_cation"] == {"5": "Na"}
    print("✓ 複雑なパーステスト成功")


def test_validation():
    """バリデーションのテスト"""
    result = parse_argv(["A15", "--exporter", "gromacs"])
    is_valid, errors = validate_result(result)
    assert is_valid, f"バリデーションエラー: {errors}"
    print("✓ バリデーションテスト成功")


def test_rep_followed_by_short_option():
    """--rep 8 8 8 の直後に -e cif があるとき、-e が rep の引数に食われないこと"""
    result = parse_argv(["1h", "--rep", "8", "8", "8", "-e", "cif"])
    assert result["base_options"]["replication_factors"] == (8, 8, 8), (
        "replication_factors should be (8,8,8), got %s" % result["base_options"].get("replication_factors")
    )
    assert result["exporter"]["name"] == "cif", (
        "exporter should be cif, got %s" % result["exporter"].get("name")
    )
    print("✓ --rep の直後の -e がオプションとして認識されるテスト成功")


def test_missing_unitcell():
    """unitcellが指定されていない場合のテスト"""
    result = parse_argv(["--exporter", "gromacs"])
    is_valid, errors = validate_result(result)
    assert not is_valid, "unitcellが指定されていない場合はエラーになるべき"
    assert any("unitcell" in error.lower() for error in errors)
    print("✓ unitcell未指定のテスト成功")


def test_exporter_without_plugin_name_raises():
    """-e / --exporter のあとプラグイン名が無いとエラー（既定 gromacs に落とさない）"""
    cases = (
        ["1h", "-e"],
        ["1h", "--exporter"],
        ["1h", "-e", "--rep", "2", "2", "2"],
        ["1h", "--exporter", "--rep", "2", "2", "2"],
    )
    for argv in cases:
        try:
            parse_argv(argv)
        except (RuntimeError, ValueError) as e:
            msg = str(e)
            assert "exporter" in msg.lower(), (
                f"{argv}: unexpected message: {msg}"
            )
            continue
        raise AssertionError(f"{argv} はエラーになるべき")
    # 未指定は従来どおり gromacs
    result = parse_argv(["1h"])
    assert result["exporter"]["name"] == "gromacs"
    print("✓ exporter名未指定のテスト成功")


def test_required_option_without_argument_raises():
    """引数が1個以上必要な既知オプションは、引数なしだとエラー"""
    cases = (
        (["1h", "-s"], "seed"),
        (["1h", "--seed"], "seed"),
        (["1h", "-g"], "guest"),
        (["1h", "-G"], "spot_guest"),
        (["1h", "-a"], "anion"),
        (["1h", "-r"], "rep"),
        (["1h", "--rep"], "rep"),
        (["1h", "--pol_loop_1"], "pol_loop_1"),
        (["1h", "--density"], "density"),
        (["1h", "-Y"], "config"),
        (["1h", "--config"], "config"),
        (["1h", "-s", "--rep", "2", "2", "2"], "seed"),
    )
    for argv, hint in cases:
        try:
            parse_argv(argv)
        except (RuntimeError, ValueError) as e:
            msg = str(e).lower()
            assert hint.lower() in msg or "argument" in msg, (
                f"{argv}: expected {hint!r} in message, got: {e}"
            )
            continue
        raise AssertionError(f"{argv} はエラーになるべき")
    print("✓ 必須引数なしオプションのテスト成功")


def test_unknown_option_parsed_and_in_unitcell_options():
    """未定義オプション（--pass 等）は unitcell_options に入り、実行時に警告される"""
    result = parse_argv(["CS2", "-c", "0=Na", "-a", "1=Cl", "--pass"])
    assert result["unitcell"]["name"] == "CS2"
    uopts = result["unitcell"]["options"]
    assert "pass" in uopts, "未定義の --pass は unitcell_options に入る（警告は logger で出力される）"
    assert uopts.get("cation") is not None
    assert uopts.get("anion") is not None
    print("✓ 未定義オプション --pass のパーステスト成功")


if __name__ == "__main__":
    print("=" * 60)
    print("genice3 CLI runner 統合テスト")
    print("=" * 60)
    print()

    try:
        test_basic_parsing()
        test_complex_parsing()
        test_rep_followed_by_short_option()
        test_validation()
        test_missing_unitcell()
        test_exporter_without_plugin_name_raises()
        test_required_option_without_argument_raises()
        test_unknown_option_parsed_and_in_unitcell_options()
        print()
        print("=" * 60)
        print("✓ すべてのテストが成功しました")
        print("=" * 60)
    except Exception as e:
        print(f"✗ テスト失敗: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
