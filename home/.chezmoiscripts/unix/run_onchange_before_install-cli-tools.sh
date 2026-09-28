#!/bin/sh
set -e

if command -v apt-get >/dev/null; then
  missing=""
  for p in zsh zsh-autosuggestions zsh-syntax-highlighting fzf ripgrep fd-find bat eza btop zoxide direnv; do
    dpkg -s "$p" >/dev/null 2>&1 || missing="$missing $p"
  done
  [ -z "$missing" ] && exit 0
  sudo apt-get update
  # shellcheck disable=SC2086
  sudo apt-get install -y $missing
elif command -v brew >/dev/null; then
  for p in fzf ripgrep fd bat eza btop zoxide direnv zsh-autosuggestions zsh-syntax-highlighting; do
    brew list "$p" >/dev/null 2>&1 || brew install "$p"
  done
  # Same Nerd Font as windows/install-font. Not needed on WSL, which renders in Windows Terminal.
  brew list --cask font-cascadia-mono-nf >/dev/null 2>&1 || brew install --cask font-cascadia-mono-nf
fi
