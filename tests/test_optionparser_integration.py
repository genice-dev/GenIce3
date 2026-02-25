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
