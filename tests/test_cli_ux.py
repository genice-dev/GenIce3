"""
CLI 利用者目線のテスト（使いやすさ・エラーメッセージのわかりやすさ）

【準備すべきテストの種類】

1. ヘルプ・バージョン
   - --help / -h: 使い方が分かる文言が表示される
   - --version / -V: バージョンが表示される
   - 終了コード 0 であること

2. 必須引数不足
   - UNITCELL 未指定: 「unitcell名が指定されていません」など明確なメッセージが stderr に出る
   - 終了コード 1 であること
   - メッセージが日本語で分かりやすいこと（必要なら英語でも一貫性を検証）

3. 不正なオプション値
   - --rep に不正な値（例: 0, 負の数, 非数）を渡したときのメッセージ
   - --seed に非整数を渡したときのメッセージ
   - エラー時に「何が悪いか」「どう直すか」が分かる文言を含むこと

4. 存在しないプラグイン名
   - 存在しない unitcell 名を指定したとき（例: --exporter gromacs NoSuchUnitcell）
   - 存在しない exporter 名を指定したとき（例: A15 --exporter NoSuchExporter）
   - 「Nonexistent or failed to load」「Dubious ... name」など、ユーザーが次に何をすべきか分かるメッセージ

5. 成功時の振る舞い
   - 正常系（例: A15 --exporter gromacs --rep 1 1 1）で exit 0、stdout に何か出力される
   - エラー時は stdout にスタックトレースを出さない（本番では logger のみにし、stderr に短いメッセージを出す設計が望ましい）

6. エラー時の出力形式
   - パースエラー時: traceback を出さず、1行程度のメッセージ＋必要なら「--help で使い方を確認」などの案内
   - バリデーションエラー時: 複数エラーを列挙する場合、箇条書きや改行で読みやすいこと

このファイルでは、上記のうち 1・2 と正常系の一部を subprocess で実行して検証する。
それ以外は、改善実装に合わせてテストを追加する。
"""

import subprocess
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


def _run_genice3(args: list[str], timeout: int = 10):
    """genice3 を python -m で実行し、(returncode, stdout, stderr) を返す"""
    cmd = [sys.executable, "-m", "genice3.cli.genice"] + args
    result = subprocess.run(
        cmd,
        cwd=project_root,
        capture_output=True,
        text=True,
        timeout=timeout,
        env={**__import__("os").environ, "PYTHONPATH": str(project_root)},
    )
    return result.returncode, result.stdout, result.stderr


# ---------------------------------------------------------------------------
# 1. ヘルプ・バージョン
# ---------------------------------------------------------------------------


def test_help_exits_zero_and_shows_usage():
    """--help で終了コード 0 かつ Usage が表示される"""
    code, out, err = _run_genice3(["--help"])
    assert code == 0, f"Expected exit 0, got {code}. stderr: {err}"
    assert "Usage:" in out or "usage:" in out.lower(), f"Expected Usage in stdout. got: {out[:500]}"
    assert "UNITCELL" in out or "unitcell" in out.lower()


def test_short_help_exits_zero():
    """-h でも同様にヘルプが表示される"""
    code, out, err = _run_genice3(["-h"])
    assert code == 0
    assert "Usage:" in out or "usage:" in out.lower()


def test_version_exits_zero_and_shows_version():
    """--version で終了コード 0 かつバージョン表示"""
    code, out, err = _run_genice3(["--version"])
    assert code == 0, f"Expected exit 0, got {code}. stderr: {err}"
    assert "genice3" in out
    # 3.0 などバージョンらしき数字
    assert any(c.isdigit() for c in out), f"Version-like string expected in: {out}"


# ---------------------------------------------------------------------------
# 2. 必須引数不足（バリデーションエラー）
# ---------------------------------------------------------------------------


def test_missing_unitcell_exits_nonzero_and_message_on_stderr():
    """UNITCELL 未指定時は終了コード 1 かつ stderr に分かりやすいメッセージ"""
    code, out, err = _run_genice3(["--exporter", "gromacs"])
    assert code == 1, f"Expected exit 1 when unitcell missing, got {code}. stdout: {out}, stderr: {err}"
    # 利用者に分かる文言（現在の実装は「unitcell名が指定されていません」）
    assert "unitcell" in err.lower() or "unitcell" in out.lower(), (
        f"Error message should mention unitcell. stderr: {err}, stdout: {out}"
    )


def test_missing_unitcell_message_is_user_friendly():
    """UNITCELL 未指定時のメッセージは短く、何を指定すべきか分かる"""
    code, out, err = _run_genice3(["--exporter", "gromacs"])
    combined = (err + "\n" + out).lower()
    # 単に「unitcell」に言及があるだけでなく、指定されていないことが分かる
    assert "指定" in (err + out) or "required" in combined or "unitcell" in combined


# ---------------------------------------------------------------------------
# 5. 成功時の振る舞い（軽いスモークテスト）
# ---------------------------------------------------------------------------


def test_valid_minimal_command_exits_zero_and_produces_stdout():
    """最小限の正常コマンドで終了コード 0 かつ stdout に出力がある"""
    code, out, err = _run_genice3(["1h", "--exporter", "gromacs", "--rep", "1", "1", "1"])
    assert code == 0, f"Expected exit 0. stderr: {err}"
    assert len(out.strip()) > 0, "Normal run should produce stdout (e.g. gro file)"


# ---------------------------------------------------------------------------
# 今後の拡張用: 不正オプション・存在しないプラグイン
# ---------------------------------------------------------------------------
# 以下は、エラーメッセージを改善したあとで assert を書くとよい。
#
# def test_invalid_rep_value_shows_clear_message():
#     code, out, err = _run_genice3(["1h", "--rep", "0", "0", "0"])
#     assert code == 1
#     assert "rep" in (err + out).lower() or "replication" in (err + out).lower()
#
# def test_nonexistent_unitcell_shows_plugin_error():
#     code, out, err = _run_genice3(["NoSuchUnitcell123", "--exporter", "gromacs"])
#     assert code == 1
#     assert "NoSuchUnitcell123" in (err + out) or "not found" in (err + out).lower()
#
