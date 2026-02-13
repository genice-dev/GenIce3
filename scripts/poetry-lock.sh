#!/usr/bin/env sh
# poetry が内部で "python" を呼ぶ環境用。bin/python → python3 のラッパーを PATH に足してから lock する。
cd "$(dirname "$0")/.."
export PATH="${PWD}/bin:${PATH}"
exec poetry lock "$@"
