"""
One-off script: convert .py symlinks under genice3 to alias files (from .X import *).
Run from repo root: python scripts/convert_symlinks.py
"""
import os
import pathlib


def convert_symlinks(root_dir):
    for root, dirs, files in os.walk(root_dir):
        for name in files:
            path = pathlib.Path(root) / name
            if path.is_symlink():
                target = os.readlink(path)
                if name.endswith(".py") and target.endswith(".py"):
                    # Get the stem of the target (e.g., 'tip5p' from 'tip5p.py')
                    target_path = pathlib.Path(target)
                    target_stem = target_path.stem

                    print(
                        f"Converting symlink: {path} -> {target} (alias to {target_stem})"
                    )

                    # Remove the symlink
                    path.unlink()

                    # Create the alias file
                    with open(path, "w") as f:
                        f.write(f"from .{target_stem} import *\n")


if __name__ == "__main__":
    root = pathlib.Path(__file__).resolve().parent.parent
    convert_symlinks(root / "genice3")
