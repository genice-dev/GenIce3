import os
import pathlib


def fix_engel_references(root_dir):
    # lattices ディレクトリと lattices/preparing ディレクトリを対象にする
    target_dirs = [
        pathlib.Path(root_dir) / "genice2" / "lattices",
        pathlib.Path(root_dir) / "genice2" / "lattices" / "preparing",
    ]

    for target_dir in target_dirs:
        if not target_dir.exists():
            continue

        print(f"Checking directory: {target_dir}")
        # すべてのファイルを取得
        files = list(target_dir.glob("*.py"))

        # engel*.py ファイルを探す
        for engel_file in files:
            if engel_file.name.startswith("engel"):
                with open(engel_file, "r") as f:
                    content = f.read()

                # 内容が "from .<target> import *" 形式か確認
                if content.startswith("from .") and content.endswith(" import *\n"):
                    # ターゲット名を取得 (例: .ice1h -> ice1h)
                    target_stem = content.split(".")[1].split(" ")[0]
                    target_file = target_dir / f"{target_stem}.py"

                    if target_file.exists():
                        print(
                            f"Swapping reference: {engel_file.name} <-> {target_file.name}"
                        )

                        # 1. ターゲットファイル（数字名など）の内容を一時保存
                        # (現在は engel からインポートされているだけの状態のはず)

                        # 2. engelファイル（実体にする方）の内容を、ターゲットファイルの実体に置き換える
                        with open(target_file, "r") as f:
                            target_content = f.read()

                        # もしターゲットファイルが engel をインポートしているわけではなく、
                        # engel がターゲットをインポートしている状態（現在の状態）なら、
                        # ターゲットファイルに元々あったはずのコードを engel に戻す必要がある。

                        # しかし、現在の状態は「engel が ターゲットを import * している」状態。
                        # つまり、ターゲットファイルに「実体」がある。
                        # これを逆転させる：
                        # engel.py -> 実体コード
                        # ターゲット.py -> from .engel import *

                        # 実体コードを読み込む
                        with open(target_file, "r") as f:
                            actual_code = f.read()

                        # engel.py を実体コードにする
                        with open(engel_file, "w") as f:
                            f.write(actual_code)

                        # ターゲット.py（数字名など）をエイリアスにする
                        # 数字名から engel をインポートするのは文法的に OK (from .engel01 import *)
                        with open(target_file, "w") as f:
                            f.write(f"from .{engel_file.stem} import *\n")


if __name__ == "__main__":
    fix_engel_references(".")
