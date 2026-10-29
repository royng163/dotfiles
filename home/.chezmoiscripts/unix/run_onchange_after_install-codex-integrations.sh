#!/bin/sh
set -eu
export NVM_DIR="$HOME/.nvm"
nvm_sh="$NVM_DIR/nvm.sh"
[ -s "$nvm_sh" ] || [ ! -s /opt/homebrew/opt/nvm/nvm.sh ] || nvm_sh=/opt/homebrew/opt/nvm/nvm.sh
[ ! -s "$nvm_sh" ] || . "$nvm_sh"
command -v codex >/dev/null 2>&1 || npm install -g @openai/codex
if ! codex plugin marketplace list | awk '{print $1}' | grep -qx wakatime; then
  codex plugin marketplace add wakatime/codex-cli-wakatime
fi
if [ ! -d "$HOME/.codex/plugins/cache/wakatime/codex-cli-wakatime" ]; then
  codex plugin add codex-cli-wakatime@wakatime
fi
if [ "$(uname -s)" = Darwin ] && [ -f "$HOME/Library/LaunchAgents/com.royng.aitime.plist" ]; then
  launchctl bootout "gui/$(id -u)/com.royng.aitime" 2>/dev/null || :
  launchctl bootstrap "gui/$(id -u)" "$HOME/Library/LaunchAgents/com.royng.aitime.plist"
fi
