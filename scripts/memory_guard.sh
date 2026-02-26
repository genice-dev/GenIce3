#!/usr/bin/env bash
# memory_guard.sh - メモリ逼迫時に最大消費プロセスに SIGSTOP を送る「先制攻撃」スクリプト
#
# 使い方:
#   手動: ./scripts/memory_guard.sh
#   様子見: MEMORY_GUARD_DRY_RUN=1 ./scripts/memory_guard.sh
#   launchd: com.genice.memoryguard.plist.example を ~/Library/LaunchAgents/ にコピーし、
#            ABSOLUTE_PATH_TO_GenIce3 を実パスに書き換えて launchctl load する。
# 復帰: kill -CONT <pid> でプロセスを再開できる。

set -e

# 設定（環境変数で上書き可）
FREE_MB_THRESHOLD="${MEMORY_GUARD_THRESHOLD_MB:-500}"   # この MB を下回ったら発動
SKIP_NAMES="${MEMORY_GUARD_SKIP:-kernel_task|WindowServer|loginwindow|launchd|sysmond|UserEventAgent}"
LOG="${MEMORY_GUARD_LOG:-$HOME/.memory_guard.log}"
DRY_RUN="${MEMORY_GUARD_DRY_RUN:-0}"

log() {
  local msg="[$(date '+%Y-%m-%d %H:%M:%S')] $*"
  echo "$msg"
  ( echo "$msg" >> "$LOG" ) 2>/dev/null || true
}

# macOS: vm_stat で空きメモリ（bytes）を取得
get_free_memory_bytes() {
  local page_size pages_free
  page_size=$(vm_stat | awk '/page size/ { gsub(/[^0-9]/,""); print $0 }')
  pages_free=$(vm_stat | awk '/Pages free/ { gsub(/[^0-9]/,""); print $0 }')
  echo $((page_size * pages_free))
}

# メモリ使用量トップのプロセス PID を取得（自分自身と除外リストを除く）
get_top_memory_pid() {
  local self_pid=${1:-$$}
  ps -eo pid,rss,comm -c 2>/dev/null | awk -v skip="$SKIP_NAMES" -v self="$self_pid" '
    NR>1 && $1 != self && $3 !~ skip && $2+0 > 0 { print $2, $1, $3 }
  ' | sort -k1 -rn | head -1 | awk '{ print $2 }'
}

free_bytes=$(get_free_memory_bytes)
free_mb=$((free_bytes / 1024 / 1024))

if [ "$free_mb" -ge "$FREE_MB_THRESHOLD" ]; then
  [ "$DRY_RUN" = "1" ] && log "OK: free=${free_mb}MB (threshold=${FREE_MB_THRESHOLD}MB) - no action"
  exit 0
fi

pid=$(get_top_memory_pid "$$")
if [ -z "$pid" ] || [ "$pid" = "" ]; then
  log "WARN: free=${free_mb}MB but no candidate process found"
  exit 1
fi

name=$(ps -o comm= -p "$pid" 2>/dev/null || echo "?")
rss_kb=$(ps -o rss= -p "$pid" 2>/dev/null || echo "0")
rss_mb=$((rss_kb / 1024))

if [ "$DRY_RUN" = "1" ]; then
  log "DRY RUN: would SIGSTOP pid=$pid ($name) rss=${rss_mb}MB (free=${free_mb}MB)"
  exit 0
fi

log "LOW MEMORY: free=${free_mb}MB -> SIGSTOP pid=$pid ($name) rss=${rss_mb}MB"
if kill -STOP "$pid" 2>/dev/null; then
  log "STOPPED pid=$pid. Resume with: kill -CONT $pid"
else
  log "FAILED to STOP pid=$pid (no permission or gone)"
  exit 1
fi
