---
name: capture-lessons
description: Save verified lessons in existing instructions when explicitly asked to capture lessons or remember a reusable correction.
---

# Capture lessons

Use the requested scope and available session evidence to save lessons that change a
future decision. An explicit user preference is enough evidence; inferred conventions
need support from the code, documentation or a verified result. Keep uncertainty explicit.

Search the relevant existing instructions before writing. Update a matching rule instead
of adding a duplicate. Preserve its scope and replace a contradicted rule when the user's
correction establishes the new behaviour.

Choose the narrowest existing home:

| Lesson | Destination |
|---|---|
| Project behaviour, conventions or environment constraints | The project's existing instruction or convention file; use local overrides for machine-specific details |
| Portable user preference or development rule | The shared agent instruction source managed by chezmoi |
| Reusable procedure already covered by a skill | The matching skill's canonical source |
| Feature decision, current blocker, worker IDs or next action | The existing work note or task record |

Write a concise trigger and action, with a reason or evidence reference only when it helps
the next reader act correctly. Avoid narrating the session or treating one task's workaround
as a universal rule. If a lesson is already covered, report that without changing files.

For chezmoi-managed instructions or skills, edit the source and apply only the affected
targets. Respect the repository's Git policy and preserve unrelated local changes.
Keep private project names, paths, tickets, credentials and activity out of public dotfiles;
only portable, sanitized rules belong there. Keep raw transcripts and runtime observations local.

Only the lead writes a shared work note. A worker returns its lesson and proposed destination
to the lead. Creating a separate learning database, background observer, hook or new skill
requires its own concrete need and authorization.

Report the lesson and changed file briefly, including any item left uncertain or already covered.
