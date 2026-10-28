#!/bin/sh
set -eu
python="$HOME/miniforge3/bin/python3"
[ -x "$python" ] || python=python3
"$python" -c 'import mcp, patchright' 2>/dev/null || "$python" -m pip install mcp patchright
"$python" -m patchright install chromium
