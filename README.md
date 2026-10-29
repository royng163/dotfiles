# dotfiles

Portable settings for macOS, WSL Ubuntu and Windows, managed with [chezmoi](https://www.chezmoi.io/).

## Setup

Install chezmoi with Homebrew (macOS), Snap (WSL), or winget (Windows), then:

```sh
chezmoi init royng163
# Add machine-local [data] values to ~/.config/chezmoi/chezmoi.toml.
chezmoi diff
chezmoi apply -v
```

Run Windows applies in a real terminal because nvm-windows requires a console.
Install Orca (and Zed on macOS), then sign into Codex. Review plugin trust prompts locally.

## What syncs

| Settings | macOS | WSL | Windows |
| --- | :---: | :---: | :---: |
| zsh, bat | Yes | Yes | |
| Starship | Yes | Yes | Yes |
| Zed, with thread sidebar on the left | Yes | | Yes |
| Codex preferences, instructions and Git rules | Yes | Yes | |
| Shared agent instructions, skills and MCP | Yes | Yes | |
| WakaTime config, when an API key is supplied | Yes | Yes | |
| WakaTime two-minute sync timer | Yes | | |
| Zed `subl` editor bridge | Yes | | |
| Windows Terminal theme/settings, PowerShell profile | | | Yes |

Six custom skills are synced: audit, browser-check, changelog, commit-msg,
mr-description and work-note, including its helper. Archify v3.2.0 is installed
from a pinned, checksum-verified release only when missing; existing builds stay in place.
Orca's bundled orchestration skill is installed when its CLI is available, preserving
customized copies. If Orca is installed later, run:

```sh
orca skills install --skill orchestration --agent universal --json
```

On Linux, use `orca-ide` instead of `orca`. Say **“Orca this”** or **“Use Orca teams”**
to request supervised Codex workers.

Context7 and Patchright share one registry in `home/.chezmoitemplates/mcp-servers.json`.
It renders to `~/.agents/mcp.json` and Codex's native config; other clients need adapters.
Codex preferences in `codex-settings.toml` merge with local plugins, hooks and project trust.
Sessions, authentication, imported memories and Orca UI settings/keybindings remain local.
WakaTime records attributable file activity, so its total can be shorter than session time.

## Installed tools

macOS/WSL scripts provision nvm + Node LTS, Miniforge, shell tools and plugins,
Starship, gitleaks, Codex + WakaTime, MCP dependencies, Chromium and shared skills.
macOS also gets Cascadia Mono NF. Linux sets zsh as the login shell.
Windows scripts install terminal/developer tools and the font, configure Node LTS,
and apply Explorer, taskbar, privacy and development preferences with UAC as needed.
Shell profiles stay chezmoi-managed; installers skip tools already present.

## Machine-local data

Keep secrets and private endpoints in `~/.config/chezmoi/chezmoi.toml` under `[data]`:

| Keys | Purpose |
| --- | --- |
| `wakatimeApiKey` | Required by Zed; enables `~/.wakatime.cfg` |
| `sonarqubeUrl`, `sonarqubeConnectionId`, `sonarqubeToken` | Optional Zed SonarLint connection |
| `zedProxy` | Optional Zed agent terminal proxy |
| `wakatimeExclude` | Optional list of extra WakaTime exclusions |

## Maintenance

Sources live under `home/` (`.chezmoiroot`); OS selection is in `.chezmoiignore`.
Edit shared templates for portable preferences, then review and apply:

```sh
chezmoi diff
chezmoi apply
chezmoi status    # empty when managed files match
chezmoi managed  # targets for this machine
```

The local chezmoi Git automation policy may commit/push during operations; review it
before changing sources. The repository's pre-commit hook runs gitleaks on staged files.

[MIT license](LICENSE)
