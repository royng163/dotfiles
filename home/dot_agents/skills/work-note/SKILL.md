---
name: work-note
description: >
  Create or extend the shared work note for a feature: one file per feature at
  the monorepo root when the repo is a monorepo, otherwise at the parent of the
  repo so sibling repos share it. Holds the contract between surfaces (backend,
  frontend, admin) and what each one actually changed — terse, carrying only what
  the user or the next surface acts on. Also scaffolds the shared notes folder.
  Trigger: starting or finishing work on a surface, picking up a feature another
  surface began, "work note", "write the work note", /work-note.
---

One file per feature, shared across every surface: at the monorepo root, or at the
parent of a single-surface repo. It is how a surface tells the next one what it can
rely on.

## Output location

Resolve the **notes root** from the current git repository:

- **Monorepo:** `<git-root>/.notes/work/`.
- **Single-surface repo:** `<git-root>/../.notes/work/`, so sibling repos share the
  note.

A repo is a monorepo when any of these is true:

- the root has a workspace manifest: `pnpm-workspace.yaml`, `lerna.json`, `nx.json`,
  `turbo.json`, `rush.json`, `go.work`, a `Cargo.toml` with `[workspace]`, a
  `package.json` with `workspaces`, or a `pyproject.toml` with `[tool.uv.workspace]`;
- the root has `apps/`, `packages/`, or `services/`;
- the root has two or more surface directories, such as `backend/` with `client/`,
  `frontend/`, `web/`, `mobile/`, or `admin/`;
- the project's `CLAUDE.md` or `AGENTS.md` declares more than one surface.

Examples:

- `FinC` has `backend/` and `client/`, so notes go in `FinC/.notes/work/`.
- A standalone `api` repo with sibling `web-client` and `web-admin` repos puts notes
  in the parent: `../.notes/work/`.

Never create `.notes/` inside a surface directory. Do not keep a parent `.notes/`
alongside a monorepo `.notes/`; the monorepo root is canonical. If an existing note
lives at the old parent location in a monorepo, move it to the monorepo root.

When the hook is installed, `python3 ~/.agents/hooks/work-note-gate.py --where`
prints the resolved folder.

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
   question there rather than guessing. Make each changed behaviour an acceptance
   case: concrete setup or input, expected result and a named check or browser flow.
3. Only then implement, and append the surface's own section.

**Picking up a surface:** start with frontmatter, `## Status`, and `## Contract`.
Read the assigned entry points and follow relevant callers, tests and evidence links
as needed. Ask for the specific missing contract decision rather than loading unrelated
surface histories.

**Finishing a surface:** append or extend its section, update its `## Status` line
with state plus branch and commit, and update `pending` in frontmatter.

**In an agent team:** only the lead edits the note. Each teammate returns its
`## Status` line and surface section as its final message, and the lead writes both in.

**Sending work back:** edit `## Contract` to the new truth, append the reasoning to
the section of the surface that has to change, and set that surface's `## Status`
line back to `todo`. Do not keep a superseded contract next to the new one.

## Acceptance evidence

Reuse `WHEN` / `THEN` / `AND` cases in `## Contract`. Add a `Check:` line naming the
existing test, repository command or reproducible manual/browser flow that proves each
case. Include relevant refusal and regression cases when the behaviour needs them.
Run the check and record its actual outcome under the owning surface's `Testing Done`.
Name checks that could not run and what blocks them.

For a bug fix, reproduce the wrong result before the fix when practical. Record the
failing test ID or reproduction and compare the same check afterward. Keep unrelated
baseline failures separate from regressions. A manual check is appropriate when a useful
automated regression would cost more than the change warrants; record its inputs and result.

## Resume checkpoints

Before planned compaction, a restart or a switch to unrelated work, update `## Status`
and keep a short `### Resume` block there. For each active surface, record:

- Checkout, branch and observed HEAD, owned dirty files and any changes owned by others.
- Next concrete action, blocker or dependency and who can resolve it.
- Verification commands or browser flows already run, outcomes and evidence paths;
  link `Testing Done` when it already holds the details.
- For Orca work, Run/Task/Dispatch IDs and terminal handle, with the observed worker state.

The lead collects worker checkpoints and is the only writer of a shared note. Read the
checkpoint on resume, then verify Git/filesystem state and live Orca state before editing
or dispatching. Saved handles and liveness are observations, not current authority.
Keep checkpoints in the project note; they do not authorize a stash, commit or background
session observer. Replace the resume block as work advances so it describes one next state.

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
- **Check:** submit a guest checkout in the client; verify the response and reject token reuse.

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
- **`## Contract` is written first and edited in place.** Keep its current truth;
  preserve decisions in the owning surface section. Use `WHEN` / `THEN` / `AND` bullets
  under an H3 naming the behaviour, plus the endpoints, payload fields and error codes
  the next surface consumes. Error codes are the contract; user-facing copy is not,
  unless the server sends it.
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

When the resolved notes root has no `.notes/`, create at that root:

```
.notes/
  INDEX.md              entry point, one line per note, grouped by section
  work/README.md        local conventions only: folder scheme, surfaces
  changelog/            per-release notes (see the changelog skill)
```

Then add to the root `CLAUDE.md` or `AGENTS.md` (or the parent one for a
single-surface repo), filled in for that project:

```markdown
## Feature Work

Every feature gets a work note — see the `work-note` skill for the format and
procedure. Notes live at the resolved notes root: `<monorepo>/.notes/work/` for a
monorepo, or `<parent>/.notes/work/` for a single-surface repo.
Surfaces, in dependency order: `Backend` (<repo>), `Frontend` (<repo>).
Work loops back; the frontend surfacing a backend problem is normal.
Mandatory before the task is done.
```

Keep the format in this skill only. A project's `work/README.md` states what is
local to that project and points here for everything else.
