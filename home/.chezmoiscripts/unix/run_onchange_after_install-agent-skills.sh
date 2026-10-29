#!/bin/sh
set -eu

python="$HOME/miniforge3/bin/python3"
[ -x "$python" ] || python=python3
"$python" - <<'PY'
import hashlib
from pathlib import Path
import tempfile
import urllib.request
import zipfile

skills = Path.home() / ".agents/skills"
target = skills / "archify"
if not target.exists() and not target.is_symlink():
    skills.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".archify-", dir=skills) as temporary:
        staging = Path(temporary)
        archive = staging / "archify.zip"
        urllib.request.urlretrieve(
            "https://github.com/tt-a1i/archify/releases/download/v3.2.0/archify.zip",
            archive,
        )
        expected = "70e210265c59f24dcbdf2a502ff671104b5454e7ee7d3554aecd86bad32384f5"
        if hashlib.sha256(archive.read_bytes()).hexdigest() != expected:
            raise SystemExit("Archify checksum mismatch; installation cancelled")
        with zipfile.ZipFile(archive) as bundle:
            for entry in bundle.infolist():
                path = Path(entry.filename)
                if path.is_absolute() or ".." in path.parts or path.parts[0] != "archify":
                    raise SystemExit("Unsafe Archify archive path")
            bundle.extractall(staging)
        if not (staging / "archify/SKILL.md").is_file():
            raise SystemExit("Archify archive has no SKILL.md")
        (staging / "archify").rename(target)
PY

orca_cli=${ORCA_CLI_COMMAND:-}
if [ -z "$orca_cli" ]; then
  case "$(uname -s)" in
    Darwin)
      orca_cli=$(command -v orca || :)
      if [ -z "$orca_cli" ] && [ -x /Applications/Orca.app/Contents/Resources/bin/orca ]; then
        orca_cli=/Applications/Orca.app/Contents/Resources/bin/orca
      fi
      ;;
    Linux) orca_cli=$(command -v orca-ide || :) ;;
  esac
fi
if [ -n "$orca_cli" ]; then
  "$orca_cli" skills install --skill orchestration --agent universal --json
else
  printf '%s\n' 'Orca CLI not found; install its orchestration skill after installing Orca.'
fi
