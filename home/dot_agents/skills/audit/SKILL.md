---
name: audit
description: >
  The single verification pass over finished work: run the project's own checks,
  then five passes over one scope — correctness (does it do what it claims, and do
  the edge and error paths hold), laziness (delete / stdlib / native / yagni /
  shrink / docs), performance (N+1 and query slope, payload fields nothing reads,
  request waterfalls, serial loads), backend styleguide including HTTP status and
  error-code correctness, and frontend design-system compliance. Reads the repo's
  own rule docs instead of restating them, measures rather than guessing, and runs
  each pass to a stated bound rather than stopping at the first findings. Reports
  first, applies on approval.
  Use when the user says "audit", "audit this", "verify this", "check my work",
  "review before I commit", "perf audit", "check the conventions", "is this
  following the styleguide", "any N+1 here", "any bugs here", "check the design
  system", "check the error codes", "are the status codes right", or invokes /audit.
argument-hint: "[path | --diff <repo> | --repo]"
---

# Audit

The verification pass over work that is finished but not yet trusted: does it work,
what should be deleted, what does it cost, and where does it drift from the house
rules. Report first, apply on approval.

The rules are not in this file. They live in the repo's own docs, and this skill
reads them — a copy here would be one more thing to drift. The exceptions are HTTP
status semantics in pass 4, which no repo owns, and the defect classes in pass 1,
which are questions rather than rules.

## Scope

| Invocation | Scope |
|---|---|
| `/audit` | the working diff: `git diff`, `git diff --cached`, and untracked files |
| `/audit --diff <repo>` | that repo's working diff, run as `git -C <repo> ...`; for a workspace root that is not a git repo |
| `/audit <path>` | that file or directory, whole contents |
| `/audit --repo` | whole repo. Say up front that this is the slow path |

Decide backend vs frontend **per file**, by extension and by which repo it sits in,
so a change spanning a server repo and a client repo gets both rule sets in one run.

## Rule sources

Find them, do not assume paths. In the repo and, if it sits in a multi-repo
workspace, at the workspace root too:

- **Agent and contributor docs** — `CLAUDE.md`, `AGENTS.md`, `CONTRIBUTING.md`, and
  any local override such as `CLAUDE.local.md`. These usually also declare the
  project's verification procedure and its known defect classes.
- **A styleguide section** in `README.md` or `docs/` — handler thinness, service
  naming and signatures, raise-don't-return, module boundaries, money handling,
  import placement, whatever the project actually declares.
- **A convention or architecture-review doc**, wherever the project keeps one. Read
  it for three things, under whatever names it uses: a per-file index (a file in
  scope that is already listed has its finding written), the conventions governing
  new code, and any list of findings already rejected on verification — read that
  last one so they are not re-reported.
- **A design-system doc** — `DESIGN.md` or equivalent. Tokens and rules.
- **The error module** — whichever module the failure-response helper imports its
  code vocabulary and code→status map from, plus any exception classes that carry a
  status. Locate it from the response helper. Read the envelope rules next to it.
- **Domain flow docs** — state machines, payment or booking lifecycles, whatever the
  project documents. Pass 1 checks transitions against these.

If a doc tiers its conventions — apply-to-new-code versus only-when-already-editing
versus do-not-start — honour that tiering; it maps onto the severity buckets below.

Read only what the files in scope need. **Skip a pass whose rule source does not
exist rather than inventing rules.** Cite the source on every finding —
`[README styleguide]`, `[conventions A10]`, `[DESIGN.md Colors]` — so it can be
argued with or overruled.

## Ground truth

Run the project's own checks before reporting anything. They outrank every reading
of the code: a pass that contradicts a failing test is wrong.

Find the procedure rather than inventing one — the agent docs usually list it (test
command, lint, contract check, browser check, log check). Run what the scope
touches: the backend suite for server files, unit tests and lint for client files.

**Diff failing test IDs, never counts.** A suite with pre-existing failures makes
counts meaningless — two failures swapping places reads as "no change" by count and
as two regressions by ID. Capture the failing set before the change (stash, or the
merge-base) and compare sets.

Report what ran, what failed, and whether each failure is new. **Never report green
without having run it**, and never describe a skipped check as passed. If a check
cannot run here — a browser flow, a manual contract call — say so and name it as
outstanding rather than dropping it silently.

### Framework checks

Run the stack's own static checks over backend code in scope, even when the repo's docs do not
list them. For Django: `manage.py check` and `manage.py makemigrations --check --dry-run`, under
the project's test environment. A warning the change introduces is **Must fix**. A pre-existing
warning on a model or field in a file the change touches is **Opportunistic**; any other is one
**Out of scope** line. After a fix, `makemigrations --check --dry-run` must show no change, or
the migration follows the repo's migration rules and is propose-and-stop.

### SonarQube

When the repo has a `sonar-project.properties`, fetch the open issues for each changed file from
its last analysis: `sonar list issues --file <path> --statuses OPEN,CONFIRMED --format json`, run
from the repo root. They predate the change, so each one is an **Opportunistic** finding in the
file it sits in: offer it with its rule key, `[sonar python:S3776]`, and say whether the fix is
local and safe or falls under propose-and-stop. Skip files outside the scope. If `sonar` is
missing, unauthenticated or fails, say so in the ground truth and carry on without it.

## Pass 1 — correctness

Does the change do what it claims, and do the paths around it hold? Questions, not
rules; the repo's docs supply the specifics for the ones that are project-shaped.

- **The claim.** Read what the change says it does — commit message, work note,
  ticket, the handler's own docstring — then check the code actually does that.
- **Edge and boundary.** Empty, single and full collections; first and last element;
  zero, negative and maximum values; the exact inclusive-or-exclusive bound on any
  comparison against a limit or a date.
- **Error paths.** Every raise and every early return: reachable, and does the caller
  handle it. A broad `except` that swallows a specific failure into a generic one. A
  guard placed inside a block whose handler will eat it.
- **Null and absence.** A field that can be absent, a relation that can be unset, a
  lookup that can miss. Distinguish absent from empty from zero where the domain does.
- **State transitions.** Check every status change against the project's documented
  state machine: is the source state guaranteed, is the transition legal, is a
  reverse path needed.
- **Money and time.** Decimal end to end, never float. Timezone: whatever the
  project's documented gotcha is, check the change against it — a naive date
  extracted from an aware datetime is the usual one.
- **Concurrency and idempotency.** A read-then-write without a lock or a unique
  constraint. A webhook, retry or sync write that must survive being delivered twice.
- **Soft delete and scoping.** Reads that must filter deleted rows but rely on a
  manager that does not. Queries that must be scoped to a company, tenant or
  permission set and are not.
- **Test coverage of the new behaviour.** Not coverage percentage: is there a test
  that fails if this specific change is reverted.

A finding here names the input and the wrong outcome — "with `valid_to` equal to
today, the guard refuses" — not a feeling that the code looks risky. If a defect is
real but proving it needs a signal you do not have, say which loop would prove it.

## Pass 2 — laziness

Tags: `delete:` dead code or unused flexibility · `stdlib:` hand-rolled thing the
standard library ships · `native:` code or a dependency doing what the platform
does · `yagni:` abstraction with one implementation, config nobody sets, layer
with one caller · `shrink:` same logic, fewer lines · `docs:` a comment that
should not exist, or should be shorter.

`docs:` catches a comment narrating the change instead of the behaviour · a
contrast to a previous version or to the task · a ticket reference in source · a
comment on self-evident code · a comment past the project's cap where naming
should carry it · a wrapped comment with a stub second line under a short first
one. Comment and prose conventions often live in the **operator's** agent doc
rather than the repo's — read both before reporting.

`delete:` also covers commented-out code in any function the change touches: report the block, which
history keeps. A `TODO` / `FIXME` / `XXX` / "not supported in current phase" note in that function is
either done by this change (drop the note), still open (move it to the tracker and keep or drop the
note, as the project prefers), or stale (drop it). Report each one with which of the three it is. A
`ponytail:` prefix is a `docs:` finding: keep the comment as plain prose if it names a real ceiling,
otherwise drop it.

## Pass 3 — performance

Static read, then measure what the change touches. The checks below are spelled in
ORM and SPA terms because that is where they bite most often; they are
stack-independent questions, so translate the mechanics for another stack rather
than skipping them.

**Backend:** a serializer or template walking a relation the query does not eager
load · a response schema declared as "all fields" on a client-facing endpoint, and
any many-to-many inside one · a count where an existence check fits, or a count
inside a loop · a list endpoint with no page-size cap · float arithmetic on money.

**Frontend:** independent awaits run serially in a loader → run them concurrently ·
a query inside a loop · a deep or recursive fetch where only plain attributes are
read · a store field written by one endpoint and not another, so an entity's shape
depends on the entry route · a statically imported route component · a full refetch
to update one flag.

## Measurement

Skip it when the change touches no endpoint, loader or serializer. Otherwise:

**Decode the object, never its summary.** A reported aggregate answers a different
question than the one being asked, and diverges hardest under exactly the load that
prompted the look. A process's resident size is not what it is charged; a declared
limit is not the count in use; an executable's name is not the product it belongs
to; a duration in a log is not the timestamp of the event. Read the structure —
the config file, the full command line, the row, the plist — and quote the field.
When a claim rests on an aggregate, say which one, so a wrong reading is arguable.

**Query slope.** Count at 1 / 10 / 30 rows and report **queries per row**, not the
total — "58 per item" makes a block obviously deletable where "578 queries" does
not. Use the ORM's query log in a scratch test under the project's test
environment. In Django that is:

```python
from django.db import connection
from django.test.utils import CaptureQueriesContext

with CaptureQueriesContext(connection) as ctx:
    self.client.get('/some/list/endpoint/')
```

**Payload fields.** Grep the **bare field name** across the consuming client, never
`entity.<field>`. Entities get read through short aliases that a dotted pattern
misses, and a wrong call here is a silent runtime undefined. A field with hits only
in the client's model or type declaration is a candidate to drop.

**Frontend.** Count awaits in the touched loader and requests per route load — the
browser network panel via `browser-check` when a dev server is already up,
otherwise read the loader.

## Pass 4 — backend styleguide

Thin handler (decorator → validation → one service call → response) · service
functions with explicit, typed, keyword-style arguments and the project's naming
convention · the project's error envelope, never a new key beside it · validate
before any write · a logger, never a bare print · new models and helpers in a
domain module, not a mega file · the stdlib or framework one-liner over a
hand-rolled date or time expression · explicit soft-delete filtering on models
whose default manager does not apply it.

### HTTP status and error codes

Two questions, two authorities. **Which status a code ships with** is the repo's
call, declared in its error module — read it, never assume. **What a status means**
is the standard's call: [RFC 9110 §15](https://www.rfc-editor.org/rfc/rfc9110#section-15)
and the [IANA registry](https://www.iana.org/assignments/http-status-codes/http-status-codes.xhtml)
are the tiebreaker. Cheat sheets are fine for a quick lookup but carry no normative
weight, so do not cite one against the repo.

A status is part of the **wire contract**. Every finding here is propose-and-stop:
clients branch on status, so changing one needs a coordinated client change.

| Check | Failure it catches |
|---|---|
| Code reachable in a response but absent from the code→status map | Falls through to the default status silently. Compare the code's semantic against RFC 9110 before accepting the default |
| `2xx` on a body that reports failure | The status contradicts the envelope. A refusal is never `200` |
| Missing, malformed or expired credentials → not `401` | `401` is "authenticate"; `403` is "authenticated, still refused". Auth and token-validation codes belong at `401` |
| Authenticated-but-not-permitted → not `403` | The inverse of the above |
| `404` where the caller may not learn the record exists, or `403` where it may | Existence leakage in one direction, a confusing refusal in the other |
| Already exists / already processed / duplicate → `400` | RFC 9110 §15.5.10: a request conflicting with the target's current state is `409`. Check whether the repo declares a conflict exception and leaves it unused |
| An expected refusal answered `5xx` | A business rule saying no is a client error. `5xx` claims the server broke |
| Create not `201`, delete-with-no-body not `204` | Success statuses drift more quietly than failures |
| Hand-rolled `405`, `406`, `415` | The framework owns method, negotiation and media-type refusals |
| A status literal in a handler that the map or an exception class could carry | Puts the status somewhere the next reader will not look for it |
| An exception class raised with a status override contradicting the class | The class exists to keep the status with the rule that decided it |
| Two codes for the same condition with different statuses | Whichever the client hits first becomes the de facto contract |
| Code and status disagreeing at a call site — a permission code shipped non-`403` | One of the two is wrong; say which |

A status code declared in the vocabulary but raised nowhere is a `yagni:` finding
for pass 2, not a status finding — confirm it is genuinely unused first.

## Pass 5 — frontend design system

A hardcoded colour literal instead of a theme token · a bare heading element for
in-app text where the global type scale is oversized (utility class plus weight
instead) · spacing off the project's scale · per-component overrides of properties
the theme already sets, or a text transform on an icon-only control · an accent
colour on the wrong surface for the active theme · an off-palette colour that is
not one of the documented functional exceptions · a user-facing string not going
through the translation function · a catalogue entry in a locale the app cannot
select.

**Per-component CSS where the framework has a utility.** When the project uses a
component framework that ships utility classes (Vuetify, Tailwind, Bootstrap), a
scoped or module style block is the last resort, not the default: check spacing,
typography, layout and colour against the framework's utilities and the
component's own props first. Where a block is genuinely unavoidable, it must use
theme variables rather than literals, and cover only the need that justified it.
The project's conventions doc says which framework and which escape hatches are
sanctioned — read it rather than assuming this rule applies.

## Completion

A pass ends on its bound, not on having found something. Two or three findings is
not a finished pass; an unexamined file in scope is an unfinished one. State the
bound met at the end of each pass, or name what was skipped and why.

| Pass | Done when |
|---|---|
| Ground truth | The project's declared checks either run and reported, or named as unrunnable here |
| 1 correctness | Every changed function's claim, edge cases, error paths and state transitions checked; every new behaviour either covered by a test or reported as uncovered |
| 2 laziness | Every file in scope read end to end, and every added function, class, abstraction, dependency and comment either kept for a stated reason or tagged, and every commented-out block and TODO-style note in a touched function reported |
| 3 performance | Every endpoint, serializer, query and loader the change touches either measured or explicitly skipped with the reason |
| 4 styleguide | Every rule source that exists was read, and every handler, service, response and error code in scope checked against it — including each code's status |
| 5 design system | Every colour, spacing value, heading, control override and user-facing string in the changed markup checked against the tokens, and every new style block justified against the framework's utilities |

The bound is the whole scope, not the interesting part of it. `/audit --repo` is the
one case where a pass may be bounded by budget instead: say so, and name the
directories covered.

## Output

Ground truth first, then one line per finding, grouped by pass, most severe first,
each citing its rule source. End with `net:` covering lines **and** queries.

```
tests: 1798 run, 123 failed — failing IDs identical to baseline, no regressions
lint:  clean
browser check: not run (no dev server) — golden path still outstanding

cart.py:L118       bug: hold created before the capacity check, so an over-capacity
                   request leaves a HELD row behind. Two concurrent holds on a
                   capacity-1 session reproduce it.
orders.py:L92      money: cart total summed as float. Decimal + .quantize. [conventions P1.2]
invoices.py:L73    n+1: serializer walks invoices + approval_steps per row.
                   eager-load both — measured 158 -> 14 at 50 rows. [conventions P2.1]
errors.py:L161     status: 5 already-exists codes absent from the map, so they
                   answer 400 by default. Each is a state conflict -> 409.
                   [RFC 9110 §15.5.10] contract — propose only
ProductCard.vue:L44  design: hardcoded #035CE1. use the primary theme token. [DESIGN.md Colors]
Checkout.vue:L88     perf: two independent awaits serial. run concurrently. [conventions A1]

net: -31 lines, -144 queries at 50 rows. 1 bug, 1 contract change proposed.
```

A status finding names the code, the status it ships today, the status it should
ship, and why. A correctness finding names the input and the wrong outcome. "Wrong
status code" or "looks fragile" with no specifics is not a finding.

Nothing to cut and nothing to fix → `Verified. Ship.` and stop. Never manufacture a
finding to fill the report, and never bank an early find as a finished pass — a
report is only as good as the bound behind it.

## Severity buckets

What keeps this from becoming the repo-wide sweep the project's own convention docs
forbid:

- **Bug** — a correctness defect in the change. Reported first, always, whichever
  file it sits in. Fixed only on approval, with a test that fails without the fix.
- **Must fix** — new code in the change violating a convention that applies to all
  new code. Auto-applicable.
- **Opportunistic** — a pre-existing problem in a file the change already touches.
  Offered, applied only on approval.
- **Out of scope** — a pre-existing problem in a file the change does not touch, or
  anything the docs list as a big lift or "do not start". One line, reported, never
  fixed. Security items owned by a security team go here: flag and stop.

## Apply

Report, then apply the approved subset.

Safe: add eager loading · count → existence check · colour literal → theme token ·
bare heading → utility class · float money → decimal with explicit rounding · print
→ logger · concurrent execution over provably independent awaits · delete code with
no reader.

Propose and stop — never auto-apply:

- **any correctness fix.** A bug fix changes behaviour, needs a test that fails
  without it, and may not be the fix the author wants. Name the fix, do not make it
- narrowing a response payload, turning a prose message into a code, or changing the
  HTTP status a code ships with: all three are wire-contract changes needing a
  coordinated client change. For a status, say which clients branch on it — grep
  them for the code and for the status before proposing
- deleting an endpoint or a route
- moving code between modules — that is its own commit, with no logic change
- anything in the security bucket
- a data or schema migration

A deliberate shortcut with a known ceiling gets a plain comment naming the ceiling and the upgrade
path (`# global lock; per-account locks if throughput matters`), never a `ponytail:` prefix. Most fixes
need none: eager loading or a token swap has no ceiling to name.

Verify what was applied: re-run ground truth and the touched test module for a
backend fix, the unit tests and lint for a frontend fix. Report before/after
numbers, and say plainly when a check fails.

A standalone run writes no note of its own. When the audit rides a feature, its
findings belong in that feature's work note — see the `work-note` skill if the
project keeps them.

## Boundaries

**Do not invoke another skill.** A run stays one audit; starting a second review or
a separate diagnosis is the user's call. Name what you would reach for, and stop.
The exception is a read-only helper this skill already calls for measurement, such
as a browser check against a dev server that is already up.

It reads rules, it does not restate them, and it does not touch files outside the
scope. When a bug needs a signal that does not exist yet — a failing test, a replay
harness, a log line — describe the loop that would prove it rather than guessing at
the cause from a summary.
