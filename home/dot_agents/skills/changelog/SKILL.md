---
name: changelog
description: Write one concise, user-facing changelog per release. Compare released versions, combine backend and frontend changes, and save the entry in the workspace's shared .notes/changelog folder. Use for changelogs, release notes, or a summary of what changed between release tags.
---

# Changelog

Write one release entry to `<workspace-root>/.notes/changelog/v<VERSION>-release-notes.md`. Use the shared notes beside the repositories. If the workspace has no shared notes folder, ask before creating one. Do not commit or tag.

## Find the shipped changes

1. Use the requested release range. When only the target release is given, find the preceding reachable release tag. Prefer the published tag if the local tag points elsewhere.
2. Read the commits and relevant diffs for the released repositories. If a release pins components through submodules, compare their recorded commits at the two release points.
3. Make an internal checklist of user-visible outcomes before drafting. Check the shipped diffs and relevant tickets or work notes. Include changes to PDFs, emails, and exports alongside screen and workflow changes.
4. Group related backend and frontend changes into concise bullets. After shortening, check that each meaningful outcome is named in the final draft or deliberately omitted with a reason. Keep the checklist and omission reasons out of the release entry.

Omit internal implementation, maintenance, CI, and test changes unless they visibly affect users.

## Format

Use the version without a `v` prefix and the release date in ISO format. Start with one top-level heading and use second-level category headings.

```markdown
# 1.1.17 - 2026-11-24

## Changed

- Choose eligible payment methods from a single Pay button.

## Added

- Submit and track offline payments with proof.

## Fixed

- Preserve quotation versions and rejection history.
```

Use these categories in order: Changed, Added, Removed, Fixed. Omit empty categories. Start each bullet with a present-tense verb, state the user or administrator outcome, and keep the full entry to a short list of the most important changes. Flag breaking changes first in their category. Leave commit details, issue references, and author credits out of the release entry.

Save the file and show the release entry in the reply.
