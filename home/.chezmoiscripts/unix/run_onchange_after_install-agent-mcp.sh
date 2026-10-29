#!/bin/sh
set -eu
python="$HOME/miniforge3/bin/python3"
[ -x "$python" ] || python=python3
"$python" -c '
from importlib.metadata import version
from patchright.async_api import Locator
assert version("mcp").split(".")[0] == "1" and hasattr(Locator, "aria_snapshot")
' 2>/dev/null || "$python" -m pip install 'mcp>=1.28,<2' patchright
"$python" -m patchright install chromium
