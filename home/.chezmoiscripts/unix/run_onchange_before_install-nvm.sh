#!/bin/bash
set -e

export NVM_DIR="$HOME/.nvm"
nvm_sh="$NVM_DIR/nvm.sh"
[ -s "$nvm_sh" ] || [ ! -s /opt/homebrew/opt/nvm/nvm.sh ] || nvm_sh=/opt/homebrew/opt/nvm/nvm.sh

if [ ! -s "$nvm_sh" ]; then
  # PROFILE=/dev/null: shell rc files are chezmoi-managed, so the installer must not edit them.
  curl -fsSL https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.8/install.sh | PROFILE=/dev/null bash
fi

. "$nvm_sh"
if [ "$(nvm version default)" = "N/A" ]; then
  nvm install --lts
  nvm alias default 'lts/*'
fi
