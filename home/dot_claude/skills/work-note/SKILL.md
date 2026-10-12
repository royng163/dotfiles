---
name: work-note
description: >
  Create or extend the shared work note for a feature in a multi-repo workspace:
  a single file per feature, at the workspace root, holding the contract between
  surfaces (backend, frontend, admin) and what each one actually changed — terse,
  carrying only what the user or the next surface acts on. Also
  scaffolds the shared notes folder in a new workspace.
  Trigger: starting or finishing work on a surface, picking up a feature another
  surface began, "work note", "write the work note", /work-note.
---

One file per feature, shared across every repo in the workspace. It is how a
surface tells the next one what it can rely on.

## Output location

Notes live in the **workspace-root** shared folder `.notes/work/`, the parent
directory holding all the repos — never inside a repo, and never in a repo's own
`.notes/`. From a repo worktree that is `../.notes/work/`.

Name: `<ticket>-<slug>.md`, ticket lowercase and dashed (`abc-123-guest-checkout`).
No ticket, use the slug alone. A project may group notes into subfolders by
release; its `CLAUDE.md` says so if it does.

## Surfaces, and why this is a loop

A **surface** is one deployable side of the feature: `Backend`, `Frontend`,
`Frontend (client)`, `Frontend (admin)`. The project's `CLAUDE.md` declares which
surfaces exist and in what dependency order; use those strings verbatim, because
inconsistent spellings make the sections unfindable.

Work is **not** a pipeline. The usual path is backend, then frontend, then the
frontend finds a problem and work returns to the backend, repeating until both
sides agree. So:

- A surface section is append-only, but never closed. Returning to it is normal.
- There is no integration or sign-off section. A cross-surface finding is written
  in the section of the surface that changed.
- `## Contract` is the negotiation record. Its edit is what marks a loop-back.

## Steps

**Starting a feature** (before writing code, from the approved plan):

1. Create the note with frontmatter, `## Status`, and `## Contract`.
2. `## Contract` states the behaviour being built and the wire shape the next
   surface will consume. If a requirement is not yet decided, write the open
   question there rather than guessing.
3. Only then implement, and append the surface's own section.

**Picking up a surface:** read frontmatter, `## Status`, and `## Contract`. Nothing
else. The surface sections are long by design and hold reasoning the next surface
does not need.

**Finishing a surface:** append or extend its section, update its `## Status` line
with state plus branch and commit, and update `pending` in frontmatter.

**In an agent team:** only the lead edits the note. Each teammate returns its
`## Status` line and surface section as its final message, and the lead writes both in.

**Sending work back:** edit `## Contract` to the new truth, append the reasoning to
the section of the surface that has to change, and set that surface's `## Status`
line back to `todo`. Do not keep a superseded contract next to the new one.

## Format

```markdown
---
ticket: ABC-123
status: doing                # open | doing | done
repos: [api, web-client, web-admin]
pending: [frontend-admin]
---

# ABC-123 Guest checkout

## Status
- Backend — done, `feat/guest-checkout` @ 3f9a12c, uncommitted
- Frontend (client) — done, committed 88ee54e
- Frontend (admin) — todo, refund panel needs the new order shape

## Contract
### A guest order carries no account
- **WHEN** checkout completes with no session
- **THEN** `POST /orders/` returns 201 with `account: null` and a `claim_token`
- **AND** the token is single-use and expires in 7 days

### Claiming attaches the order to a new account
- **WHEN** `POST /orders/claim/` is called with a valid token
- **THEN** the order's `account` is set and the token is consumed
- **AND** an already-consumed token returns 409 `{msg: order_already_claimed}`

## Backend

### Files Changed
### API / Contract Changes
### Workarounds
### Testing Done
### Next Surface

## Frontend (client)

## Frontend (admin)
```

## Rules

- **Frontmatter is the queryable half.** Flat keys only — nested objects do not
  render as properties. Add a `release:` (quoted string) when the project groups by
  release.
- **`## Status` is the readable half**: one line per surface, `state, branch @ sha`.
  Prose lines, **not checkboxes** — a checkbox implies monotonic progress, and
  surfaces reopen. Omit surfaces the feature does not touch.
- **`## Contract` is written first and edited in place.** It is the only section
  that is ever rewritten. Behaviour as `WHEN` / `THEN` / `AND` bullets under an H3
  naming the behaviour, plus the endpoints, payload fields and error codes the next
  surface consumes. Error codes are the contract; user-facing copy is not, unless
  the server sends it.
- **Surface sections use the declared headings verbatim.** Their subsections are
  H3: Files Changed, API / Contract Changes, Workarounds, Testing Done, Next
  Surface. Nothing else goes at H2.
- **Name the convention doc the work touched** (the repo's `CLAUDE.md`,
  `DESIGN.md`, …). A convention the work *changed* is updated in that doc in the
  same change, and the surface section says so.
- **Record decisions that stop future work**, not just what changed: a feature
  deliberately not built, a defect found and left alone, a rule that turned out
  wrong. This is the part that exists nowhere else.
- **No code diffs, no copied source.** File paths and line references only.

## What earns a line

Write for exactly two readers: the user deciding what to do next, and the surface
that picks the work up. A line earns its place by changing what one of them does;
everything else lived in the session transcript and can die there.

Include:

- files changed, one line each — rationale only where the next reader would
  otherwise undo the choice
- deviations from the contract or the plan, and who decided them
- decisions that stop future work: the thing deliberately not built, the defect
  found and left, the rule that turned out wrong
- verification, one line per check: what ran and the outcome
- open items, each naming who or what unblocks it

Cut:

- reasoning that ended where it started — a debate resolved as "left as-is" is one
  line, not the debate
- process narration: what was tried, in what order, what was reverted
- measurements, unless the number itself justifies a decision someone may revisit
- anything restating the contract, the code, or a rule doc that can be linked

A surface section normally fits in 20–40 lines. Far past that, transcript material
is leaking in and burying the lines that matter — cut, don't reorganise.

## New workspace scaffold

When a workspace has no `.notes/`, create at its root:

```
.notes/
  INDEX.md              entry point, one line per note, grouped by section
  work/README.md        local conventions only: folder scheme, surfaces
  changelog/            per-release notes (see the changelog skill)
```

Then add to the workspace `CLAUDE.md`, filled in for that project:

```markdown
## Feature Work

Every feature gets a work note — see the `work-note` skill for the format and
procedure. Notes live in `<workspace>/.notes/work/`, never inside a repo.
Surfaces, in dependency order: `Backend` (<repo>), `Frontend` (<repo>).
Work loops back; the frontend surfacing a backend problem is normal.
Mandatory before the task is done.
```

Keep the format in this skill only. A project's `work/README.md` states what is
local to that project and points here for everything else.
