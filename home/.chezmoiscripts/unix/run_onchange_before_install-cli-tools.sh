#!/bin/sh
set -e

if command -v apt-get >/dev/null; then
  missing=""
  for p in zsh zsh-autosuggestions zsh-syntax-highlighting fzf ripgrep fd-find bat eza btop zoxide direnv; do
    dpkg -s "$p" >/dev/null 2>&1 || missing="$missing $p"
  done
  if [ -n "$missing" ]; then
    sudo apt-get update
    # shellcheck disable=SC2086
    sudo apt-get install -y $missing
  fi
  # gitleaks for the dotfiles pre-commit hook, from the pinned, hash-checked release.
  if ! command -v gitleaks >/dev/null && [ ! -x "$HOME/.local/bin/gitleaks" ]; then
    v=8.30.1
    dir=$(mktemp -d)
    curl -fsSL -o "$dir/gitleaks.tar.gz" \
      "https://github.com/gitleaks/gitleaks/releases/download/v$v/gitleaks_${v}_linux_x64.tar.gz"
    echo "551f6fc83ea457d62a0d98237cbad105af8d557003051f41f3e7ca7b3f2470eb  $dir/gitleaks.tar.gz" | sha256sum -c -
    tar -xzf "$dir/gitleaks.tar.gz" -C "$dir" gitleaks
    mkdir -p "$HOME/.local/bin"
    mv "$dir/gitleaks" "$HOME/.local/bin/gitleaks"
    rm -rf "$dir"
  fi
elif command -v brew >/dev/null; then
  for p in fzf ripgrep fd bat eza btop zoxide direnv starship zsh-autosuggestions zsh-syntax-highlighting gitleaks; do
    brew list "$p" >/dev/null 2>&1 || brew install "$p"
  done
  # Same Nerd Font as windows/install-font. Not needed on WSL, which renders in Windows Terminal.
  brew list --cask font-cascadia-mono-nf >/dev/null 2>&1 || brew install --cask font-cascadia-mono-nf
fi

if ! command -v starship >/dev/null && [ ! -x "$HOME/.local/bin/starship" ]; then
  dir=$(mktemp -d)
  trap 'rm -rf "$dir"' EXIT
  curl -fsSL -o "$dir/install-starship.sh" https://starship.rs/install.sh
  mkdir -p "$HOME/.local/bin"
  sh "$dir/install-starship.sh" -y -b "$HOME/.local/bin"
fi
