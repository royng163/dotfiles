---
name: commit-msg
description: >
  Generate a conventional commit message for staged (or unstaged) changes without committing.
  Follows the Conventional Commits v1.0.0 spec (https://www.conventionalcommits.org/en/v1.0.0/).
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

<optional BREAKING CHANGE footer>
```

## Types

The only types `config-conventional` allows (`type-enum`); use no others:

- `feat` — a new feature
- `fix` — a bug fix
- `build` — build system or external dependencies (e.g. deps, project version)
- `chore` — housekeeping; no src or test behaviour change
- `ci` — CI configuration files and scripts (e.g. `.gitlab-ci.yml`, pipelines)
- `docs` — documentation only
- `perf` — a code change that improves performance
- `refactor` — a code change that neither fixes a bug nor adds a feature
- `revert` — reverts a previous commit
- `style` — formatting/whitespace; no change to code meaning
- `test` — adds or corrects tests

Behavior gate: before choosing `style`, `chore`, `docs`, `ci`, or `build`, confirm runtime behavior is
unchanged. If any user-observable behavior changes (e.g. new options, altered defaults, different output),
it must be `feat` / `fix` / `refactor` / `perf` instead. Test the change against the type's stated
criterion — do not pick a type from the edit's surface appearance.

## Rules

Enforced by `config-conventional` — a message that breaks any of these fails lint:

- Type: required and lower-case, exactly one from the list above (`type-empty`, `type-case`, `type-enum`).
- Scope: optional; when present, lower-case (`scope-case`). Noun (e.g. `payment`, `auth`). Never use issue IDs.
- Description: required (`subject-empty`); must NOT be Sentence-case, Start-Case, PascalCase, or UPPER-CASE (`subject-case`) — start lower-case. No trailing period (`subject-full-stop`).
- Header line `type(scope): description`: max 100 chars, trimmed (`header-max-length`, `header-trim`).
- Body: preceded by a blank line; each line max 100 chars (`body-leading-blank`, `body-max-line-length`).
- Footer: preceded by a blank line; each line max 100 chars (`footer-leading-blank`, `footer-max-line-length`).
- Breaking change: append `!` before `:` (e.g. `feat(api)!: remove endpoint`) and/or add a `BREAKING CHANGE:` footer. `BREAKING CHANGE` must be upper-case (per the v1.0.0 spec the parser recognises).

House style (not enforced by the config, kept for quality):

- Description: imperative present tense ("add" not "added"). The subject alone should convey the change.
- **Default to subject only.** Most commits need no body. Add one only when a reviewer would
  otherwise lose the WHY, or when the commit bundles genuinely separate changes.
- Body: at most 3 bullets, imperative, one line each (no wrapped continuation). No prose
  paragraphs, no tables, no measurements, no restating the diff, no bullet per file. A commit
  spanning several areas may group them instead — see Grouped body.
- Explain WHY only when it is not obvious from the change and would otherwise be lost. One short clause.
- Whole message under ~60 words. If a bullet only rephrases the subject, delete it.
- No ticket references anywhere: no Jira keys (`HV-602`) or issue numbers in the subject, scope,
  body or footer, and no `Refs:` / `Closes:` / `Fixes:` section, even when the branch or diff names one.
- Footer: only for breaking-change detail, as a `BREAKING CHANGE:` trailer. Omit it otherwise.

## Grouped body

When one commit genuinely spans several parts — a rule and the emails it triggers, a schema
change and the endpoints reading it — a flat bullet list buries which change belongs where.
Group the body under plain label lines instead:

```
feat(booking): require contact details out of hours and notify every party

Requirements:
- Refuse the hold unless a second user and both contact numbers are supplied
- Judge the slot against the location's hours alone, never the equipment's

Notifications:
- Send the booker, equipment team and FMO a notice once the booking confirms
- Replace the ordinary confirmation out of hours rather than sending both
```

Escalate to this form only when it earns its length:

- **Ask first whether these should be separate commits.** Groups that share no reason to land
  together are two commits wearing one hat. Group only what must ship atomically.
- **2-4 groups**, 1-3 bullets each, **10 bullets total** across all groups. One group means a
  flat list; five means the commit is too big.
- Labels are domain areas, capitalised, ending in a colon on their own line — not layer or
  file names. "Notifications:", not "services/:" or "Backend:".
- A blank line between groups. Every bullet still one line, imperative, under 100 chars.
- Whole message under ~120 words at this size, and the subject alone must still convey the
  change — the groups add detail, they never carry the headline.

## Output

Print only the raw commit message text inside a code block. No explanation, no git command wrapping.
