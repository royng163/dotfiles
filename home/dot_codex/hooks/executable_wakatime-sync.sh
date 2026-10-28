#!/bin/sh
set -eu
cli="$HOME/.wakatime/wakatime-cli"
[ -x "$cli" ] || exit 0
recent=$(find "$HOME/.codex/sessions" -name '*.jsonl' -mmin -15 -print -quit 2>/dev/null || :)
[ -n "$recent" ] || exit 0
lock="$HOME/.wakatime/codex-sync.lock"
if [ -d "$lock" ] && [ -n "$(find "$lock" -maxdepth 0 -mmin +10 2>/dev/null)" ]; then
  rmdir "$lock" 2>/dev/null || :
fi
mkdir "$lock" 2>/dev/null || exit 0
trap 'rmdir "$lock" 2>/dev/null || :' EXIT
if "$cli" --help 2>&1 | grep -q -- --sync-ai-heartbeats; then
  "$cli" --sync-ai-heartbeats --plugin 'codex-cli codex-wakatime-timer/1.0'
else
  "$cli" --sync-ai-activity --plugin 'codex-cli codex-wakatime-timer/1.0'
fi
