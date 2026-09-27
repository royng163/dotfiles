#!/bin/sh
set -e

zsh=$(command -v zsh) || exit 0
[ "$(getent passwd "$USER" | cut -d: -f7)" = "$zsh" ] && exit 0
sudo chsh -s "$zsh" "$USER"
