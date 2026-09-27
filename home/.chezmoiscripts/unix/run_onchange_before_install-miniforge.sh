#!/bin/sh
set -e

[ -x "$HOME/miniforge3/bin/conda" ] && exit 0

# The installer refuses to run unless its file name ends in .sh.
dir=$(mktemp -d)
trap 'rm -rf "$dir"' EXIT
# Release downloads can stall midway; abort under 100 KB/s for 30s and retry.
curl -fsSL --speed-limit 102400 --speed-time 30 --retry 5 --retry-all-errors -o "$dir/miniforge.sh" \
  "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh"
# -b: batch install, leaves shell rc files alone.
bash "$dir/miniforge.sh" -b -p "$HOME/miniforge3"
