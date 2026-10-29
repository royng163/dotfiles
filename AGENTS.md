# Dotfiles repo guide

chezmoi source repo, shared by macOS (work dev), WSL Ubuntu (home dev) and Windows (daily machine: terminal, Zed to open WSL, Node and Python, OS settings). See README.md for what syncs where.

## Layout

- `.chezmoiroot` = `home`: every managed file lives under `home/`. Root files (README.md, this file) are never deployed.
- `home/.chezmoiignore` decides per-OS targets. WSL reports `.chezmoi.os` = `linux`; it is detected from `.chezmoi.kernel.osrelease` containing `microsoft`.
- OS-only scripts go in `home/.chezmoiscripts/unix/` (macOS, WSL), `linux/` or `windows/`, ignored elsewhere. zsh is the only managed shell on macOS and WSL. Windows runs `.ps1` under Windows PowerShell 5.1, so no pwsh-only syntax (`??`, `?.`, ternary).
- `home/.chezmoitemplates/agents.md` is the user's global instructions for every agent, rendered into `~/.agents/AGENTS.md` and the Codex adapter `~/.codex/AGENTS.md`. It is not a guide to this repo.
- Shared MCP definitions live in `home/.chezmoitemplates/mcp-servers.json`, deployed to `~/.agents/mcp.json` and adapted into Codex TOML. Portable Codex preferences live in `.chezmoitemplates/codex-settings.toml`; runtime state stays local.
- Skills live in `home/dot_agents/skills/` and Codex discovers them directly.
- The repo is public and chezmoi auto-commits and auto-pushes: `.githooks/pre-commit` runs gitleaks on staged changes.

## Rules

- Never commit machine values. Secrets, proxies and work hostnames go in `~/.config/chezmoi/chezmoi.toml` `[data]`; guard optional ones with `hasKey`. README lists the keys.
- Files that another program rewrites use `modify_` + `chezmoi:modify-template` and own only their keys: Windows Terminal `settings.json`, Windows Zed `settings.json` (renders `.chezmoitemplates/zed-settings.json`, keeps `wsl_connections`), Codex `config.toml` (merges owned keys and preserves runtime hooks, project trust and plugin configuration), and the PowerShell profile (the Coreutils installer owns its marked block).
- On Windows, chezmoi strips a script extension from `modify_` names, so the profile source is `modify_Microsoft.PowerShell_profile.ps1.ps1`.
- `run_onchange_` scripts must be idempotent and skip work that is already done.
- nvm-windows refuses to run without a console (it shows a "Terminal Only" dialog and prints nothing when piped): run Windows applies from a real terminal, and check its state on disk.
- Don't `git add`/`commit`/`push`; leave changes unstaged for the user.

## Verify

- `chezmoi diff` and `chezmoi status` print nothing after `chezmoi apply`; `chezmoi managed` lists what this OS gets.
- Render a template without private data: `chezmoi --config <file with only [data]> execute-template < home/path.tmpl`.
- Test a modify template: `chezmoi execute-template --with-stdin "$(cat home/.../modify_x)" < current-file`.
- Windows from WSL: `chezmoi --source '\\wsl.localhost\Ubuntu\home\user\.local\share\chezmoi' diff` run through `pwsh.exe`.
