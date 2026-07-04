---
name: commit-msg
description: >
  Generate a conventional commit message for staged (or unstaged) changes without committing.
  Follows https://gist.github.com/qoomon/5dfcdf8eec66a051ecd85625518cfd13.
  Trigger: "commit message", "write commit", /commit-msg.
---

Generate a conventional commit message. Do NOT commit.

## Steps

1. Run `git diff --staged` — if empty, run `git diff HEAD` instead.
2. Run `git status --short`.
3. Analyse the diff to determine type, optional scope, and description.

## Format

```
<type>(<optional scope>): <description>

<optional body>

<optional footer>
```

## Types

- `feat` — adds, adjusts, or removes a feature visible to the API or UI
- `fix` — fixes a bug in a preceding feat
- `refactor` — restructures code without changing API/UI behaviour
- `perf` — refactor that specifically improves performance
- `style` — whitespace, formatting, missing semicolons; no behaviour change
- `test` — adds or corrects tests only
- `docs` — documentation only
- `build` — build tools, dependencies, project version
- `ops` — CI/CD, infra, deployment, monitoring
- `chore` — gitignore, init commit, housekeeping

## Rules

- Scope: optional, lowercase, noun (e.g. `payment`, `booking`, `auth`). Never use issue IDs.
- Breaking change: append `!` before `:` in subject line (e.g. `feat(api)!: remove endpoint`). Add `BREAKING CHANGE:` in footer.
- Description: imperative present tense ("add" not "added"). Lowercase first letter. No trailing period. Max ~72 chars.
- Body: optional. Imperative tense. Explain WHY, not what.
- Footer: optional. Issue refs (`Closes #123`) or breaking change detail.

## Output

Print only the raw commit message text inside a code block. No explanation, no git command wrapping.
