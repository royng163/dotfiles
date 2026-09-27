# dotfiles

Dotfiles for macOS, WSL (Ubuntu) and Windows, managed with [chezmoi](https://www.chezmoi.io/).

## What syncs where

| Target | macOS | WSL | Windows |
| --- | :-: | :-: | :-: |
| `~/.zshrc` (login shell on macOS and WSL) | ✓ | ✓ | |
| `~/.config/starship.toml` | ✓ | ✓ | ✓ |
| `~/.config/bat/config` | ✓ | ✓ | |
| `~/.config/ghostty/config` | ✓ | | |
| Zed settings | ✓ | | ✓ |
| `~/.config/cmux/cmux.json` | ✓ | | |
| `~/.claude/` (settings, CLAUDE.md, hooks, skills, MCP server) | ✓ | ✓ | |
| Windows Terminal settings: default profile, font, color scheme | | | ✓ |
| Windows Terminal color scheme (One Dark Pro Darker) | | | ✓ |
| PowerShell 7 profile (conda, Starship; the Coreutils block is left alone) | | | ✓ |

## What gets installed

Scripts in `home/.chezmoiscripts/`. Each skips what is already installed.

| Script | OS | Does |
| --- | --- | --- |
| `unix/install-nvm` | macOS, WSL | nvm (unless Homebrew's is present), plus Node LTS as default if there is none |
| `unix/install-miniforge` | macOS, WSL | Miniforge at `~/miniforge3` |
| `unix/install-cli-tools` | macOS, WSL | apt or brew: zsh plugins, fzf, ripgrep, fd, bat, eza, btop, zoxide, direnv (plus zsh on Linux) |
| `linux/chsh` | WSL | makes zsh the login shell |
| `windows/install-packages` | Windows | winget: Windows Terminal, PowerShell 7, Git, Starship, chezmoi, Coreutils, Zed, nvm for Windows, Miniforge |
| `windows/install-node` | Windows | Node LTS via nvm, if no version is active (nvm asks for UAC) |
| `windows/install-font` | Windows | Cascadia Mono NF (pinned release, hash-checked), unless already installed |
| `windows/configure-windows` | Windows | Registry, with one UAC prompt: Explorer (extensions, hidden files, full path, opens to This PC, no frequent/recent/cloud files), taskbar End Task, no web search/highlights/Start recommendations/Widgets, Do Not Disturb, no Bluetooth tray icon, dark mode, Sudo, Developer Mode, long paths, Remote Desktop off, Edge blank new tab and no first-run |

Some Explorer settings take effect after signing out. Installers never edit shell rc files; `.zshrc` and the PowerShell profile load nvm and conda. `.zshrc` expects `starship`, and uses the CLI tools and zsh plugins when present.

## New machine

```sh
brew install chezmoi                   # macOS
sudo snap install chezmoi --classic    # WSL
winget install --id twpayne.chezmoi -e # Windows

chezmoi init royng163    # clone only, no --apply yet
chezmoi data             # check the machine data
chezmoi diff             # review
chezmoi apply -v
```

## Per-machine data

Secrets and work-specific values live in `~/.config/chezmoi/chezmoi.toml` under `[data]`, never in this repo. Templates skip the related sections when a key is missing.

| Key | Used by |
| --- | --- |
| `proxy` | Claude Code `HTTP(S)_PROXY` |
| `claudeAutoModeEnvironment` | Claude Code `autoMode.environment` (list) |
| `wakatimeApiKey` | Zed (required on macOS and Windows) |
| `sonarqubeUrl`, `sonarqubeConnectionId`, `sonarqubeToken` | Zed SonarLint |
| `zedProxy` | Zed agent terminal |

## Command guide

Adapted from [chezmoi and git: dotfiles without pretending every machine is the same](https://blog.hofstede.it/chezmoi-and-git-dotfiles-without-pretending-every-machine-is-the-same/).

| Task | Command |
| --- | --- |
| Start managing a file | `chezmoi add ~/.config/foo` |
| Edit, then apply | `chezmoi edit --apply ~/.config/foo` |
| What would change | `chezmoi status`, `chezmoi diff [file]` |
| Dry run | `chezmoi apply --dry-run -v` |
| Apply | `chezmoi apply -v [file]` |
| Edited the real file by mistake | `chezmoi re-add [file]` (plain files), `chezmoi merge file` (templates) |
| Make a file a template | `chezmoi chattr +template ~/.config/foo` |
| Restrict permissions | `chezmoi chattr +private ~/.ssh/config` |
| Preview a rendered file | `chezmoi cat ~/.config/foo` |
| Show template data | `chezmoi data` |
| Health check | `chezmoi doctor` |
| Find the source file | `chezmoi source-path ~/.config/foo` |
| Pull and apply | `chezmoi update -v` |
| Commit and push | `chezmoi cd`, then `git add -A && git commit && git push`, then `exit` |

## Layout

`.chezmoiroot` points chezmoi at `home/`, so repo files (this README, `CLAUDE.md`) are never deployed.

```
home/
  .chezmoiignore              per-OS ignore rules (template)
  .chezmoiscripts/unix/       run_onchange_* scripts, macOS and WSL
  .chezmoiscripts/linux/      run_onchange_* scripts, Linux only
  .chezmoiscripts/windows/    run_onchange_* scripts, Windows only
  .chezmoitemplates/          shared templates (Zed settings for macOS and Windows)
  AppData/, Documents/        Windows targets
  dot_claude/, dot_config/, dot_zshrc.tmpl
```

Name prefixes: `dot_` → `.`, `private_` → mode 600, `executable_` → +x, `modify_` → edits the existing file, `run_onchange_` → reruns when its content changes, `.tmpl` → template.
