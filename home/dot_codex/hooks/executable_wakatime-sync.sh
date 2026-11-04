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
python3 - "$cli" <<'PYTHON'
import json
import os
from pathlib import Path
import subprocess
import sys
from uuid import UUID

home = Path.home()
view = home / ".wakatime" / "codex-view"
sessions = view / "sessions"
sessions.mkdir(parents=True, exist_ok=True, mode=0o700)
latest = {}
for folder in [home / ".codex" / "sessions", home / ".codex" / "archived_sessions"]:
    for transcript in folder.rglob("*.jsonl"):
        try:
            with transcript.open() as stream:
                session = str(UUID(json.loads(next(stream))["payload"]["id"]))
            modified = transcript.stat().st_mtime_ns
        except (OSError, StopIteration, ValueError, KeyError, TypeError):
            continue
        if session not in latest or modified > latest[session][0]:
            latest[session] = (modified, transcript)

# One hard link per session keeps resumed transcripts discoverable with real sizes and mtimes.
expected = set()
for session, (_, transcript) in latest.items():
    target = sessions / ("rollout-" + session + ".jsonl")
    expected.add(target)
    if target.exists() and os.path.samefile(target, transcript):
        continue
    target.unlink(missing_ok=True)
    os.link(transcript, target)
for target in sessions.glob("*.jsonl"):
    if target not in expected:
        target.unlink()

env = dict(os.environ, CODEX_HOME=str(view))
raise SystemExit(subprocess.call([
    sys.argv[1], "--sync-ai-activity", "--plugin", "codex-cli codex-wakatime-timer/1.0"
], env=env))
PYTHON
