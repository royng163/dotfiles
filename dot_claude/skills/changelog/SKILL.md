---
name: changelog
description: >
  Curate a per-release changelog file following the Common Changelog
  convention (https://common-changelog.org/). Reads git history since the last
  release, groups changes by impact, and writes one file per release to the
  workspace-root .notes/changelog/ folder (shared across repos). Does NOT
  commit or tag.
  Trigger: "changelog", "update changelog", "release notes", /changelog.
---

Curate a Common Changelog release entry. Do NOT commit or tag.

## Output location

Changelog files live in the **workspace-root** shared folder `../.notes/changelog/`
— the parent directory holding all the repos, alongside the other shared notes.
NOT a `CHANGELOG.md` inside the repo, and NOT the repo's own `.notes/`. If the
project has no workspace-root notes folder, ask before creating one.

- **One file per release**, named `v<VERSION>-<repo>.md` (e.g. `v2.3.0-web.md`).
  The repo suffix disambiguates releases from the different repos that share the
  folder.
- Each file holds a single release block. Do not prepend to or aggregate an
  existing file — write the new version's own file.

## Steps

1. Determine the range:
   - Last tag: `git describe --tags --abbrev=0` (if none, use full history).
   - Commits since: `git log <tag>..HEAD --no-merges --format="%h %s"`.
   - Repo name: basename of `git rev-parse --show-toplevel`. Repo URL: `git remote get-url origin` (strip `.git`).
2. Read commit subjects and, where impact is unclear, the diff. Commits follow
   Conventional Commits — use the type to classify, not to copy verbatim.
3. Curate into Common Changelog form (rules below). Drop noise.
4. Write `../.notes/changelog/v<VERSION>-<repo>.md` with the release block.

## Format

```
# Changelog — <repo>

## [VERSION] - YYYY-MM-DD

_Optional one-sentence notice._

### Changed
- **Breaking:** <change> ([`abc1234`])
- <change> ([`abc1234`])

### Added
- <change> ([`abc1234`])

[VERSION]: <repo-url>/-/releases/v<VERSION>

[`abc1234`]: <repo-url>/-/commit/abc1234
```

## Categories

Only these four, in this exact order; omit any that are empty:

- **Changed** — modifications to existing functionality
- **Added** — new functionality
- **Removed** — deleted functionality
- **Fixed** — bug fixes

Map from Conventional Commit types as a starting heuristic, then curate:
`feat` → Added (or Changed if it modifies existing behaviour); `fix` → Fixed;
`perf`/`refactor` → Changed only if user-visible; feature removals → Removed.
Skip `docs`/`test`/`style`/`chore`/`build`/`ops` unless they have user impact.

## Rules

- Heading: `## [VERSION] - YYYY-MM-DD`. VERSION is semver-valid, no `v` prefix,
  matching the git tag. DATE is ISO 8601 (today, or the tag date). Latest-first.
- No "Unreleased" section. No "Deprecated" / "Security" categories.
- Entry: imperative mood, present-tense verb (`Add`, `Fix`, `Bump`, `Remove`),
  self-describing without its heading ("Support CentOS", not "Support of CentOS").
- Breaking: prefix `**Breaking:**` (or `**<subsystem> (breaking):**`) and list
  breaking entries first within their category.
- References: reference-style commit links in parentheses at the end of the same
  line, sorted so the line reads most-important-first. Commit: `` ([`abc1234`]) ``;
  PR/issue: `(#194)`; external ticket: `(JIRA-837)`. Combine same-type refs in one
  paren, comma-separated: `` ([`abc1234`], [`def5678`]) ``. When several refs
  exist, keep only the best starting point.
- Authors (optional): after refs, comma-separated — `(#194) (Alice, Bob)`, or split
  with a semicolon `(#194; Alice, Bob)`. Omit for single-contributor projects.
- Notice (optional, max one per release): a single italic sentence right after the
  heading — `_First release._`, `_See [UPGRADING.md](UPGRADING.md)._`.
- Links: reference-style, all definitions collected at the bottom of the file — the
  version linked to its release page (`<repo-url>/-/releases/v<VERSION>`), each
  commit hash to its commit page (`<repo-url>/-/commit/<hash>`).
- Curate for humans: communicate impact, sort by importance, exclude noise, link
  each change to further information.

## Output

Write `../.notes/changelog/v<VERSION>-<repo>.md` and print the new release block.
No commit, no tag.
