---
name: audit
description: >
  Review finished changes against original requirements with a fresh independent reviewer,
  OCR delegation, project checks, and correctness, simplicity, performance,
  backend-contract and frontend-design checks. Report coverage and reproducible findings;
  apply only user-approved findings. Use for audit, verify this, check my work,
  review before commit, performance or convention review, and /audit.
---

# Audit

Establish what the exact change does, what it preserves and what remains unverified.
OCR delegation supplies the changed-file inventory and grouped rules. The fresh Codex reviewer
uses them to review code, check requirements and verify behavior.

## 1. Launch first

Follow [fresh-reviewer.md](references/fresh-reviewer.md). Start one fresh read-only reviewer
across the affected repos before OCR preparation, Sonar history, code analysis or audit checks.
Reuse declared refs/manifests and links to original requirements, decisions and existing evidence.
Only missing identity metadata gets one batched lookup; do not rebuild manifests or prepare another
review packet before launch. The reviewer verifies the declared snapshot first and prepares missing
manifests after launch. Use a concise brief, roughly 150–250 words plus paths.

Require a confirmed started/ready receipt and session/Task/Dispatch identity. An uncertain or blocked
launch blocks audit analysis; do not substitute self-review or duplicate the launch. A dispatched
implementer asks its lead for this peer. An explicitly dispatched `audit independent reviewer`
skips this launch gate, reviews its assigned scope and never spawns a reviewer.

## 2. Pin the scope

| Invocation | Reviewed input |
|---|---|
| `/audit` | Staged, unstaged and untracked changes |
| `/audit --diff <repo>` | That repo's working changes, including untracked files |
| `/audit --mr <url>` | Provider's exact diff base/head, target and stacked dependencies |
| `/audit --range <base>...<head>` | Pinned merge-base-to-head changes |
| `/audit <path>` | Whole file or directory |
| `/audit --repo` | Whole repo; announce the slow path and any budget bound |

Record checkout, base/head or dirty-snapshot identity and affected paths. Use immutable blobs for
committed reviews; current clean diffs and later local edits are not evidence about an MR. An
unresolved base blocks scope. Recheck identity before reporting; drift invalidates affected evidence.

The reviewer follows [ocr.md](references/ocr.md) once per repo and uses OCR only in
delegation mode. Account for every in-scope changed `(path, status)`. Inspect relevant excluded
tests, schemas, migrations and changed code, plus unchanged collaborators where behavior requires
it. Record each remaining gap or exclusion. Report coverage against all changed files.

## 3. Prove behavior against authority

Read original tickets/specs, latest explicit user decisions and approved contracts before treating
code or tests as an oracle. Author summaries and tests are claims to verify. Resolve conflicting
policy with the user/lead; a review suggestion cannot define money, access or lifecycle rules.

Use the existing work-note Contract or report for a compact map:
`requirement | setup/input | expected result | original source/decision | evidence or gap`.
Name preserved and intentionally changed rules. Choose a case that distinguishes the approved
behavior from a plausible wrong implementation, plus a preservation control; do not exhaustively
cross every dimension. Reuse relevant evidence and existing test modules. Before fix approval,
new executable probes belong outside the repo; repo test edits are remediation.

Trace the affected writer → persisted representation → reader/consumer and actual Save/Submit path.
Choose relevant boundaries below and attach concrete evidence or an explicit coverage gap:

| Boundary | Discriminating case |
|---|---|
| Representation | Maximum accepted value through API/model, snapshot, PDF and export field limits |
| Hidden state | Edit an invalid hidden view, switch tab or reload, then Save/Submit; backend acceptance too |
| Provenance | Save/Copy after catalogue changes; frozen/current values, typed fallback and legacy/null data |
| Time and lifecycle | Payment/delay/expiry/verification/cancellation; local midnight and UTC-date differences |
| Aggregation | Multiple lines with different GL/BU/tax/discount attributes; allocation and exact rounding |
| Access and retries | Role/tenant/soft-delete boundaries; duplicate requests and concurrent transitions |

Missing authority is an open decision, not permission to infer policy from implementation. Existing
and later decisions may supersede old review suggestions; judge defects at the cited revision/rule.

## 4. Divide work and verify

The fresh reviewer uses the delegated inventory and rules to review correctness, simplicity,
performance candidates and conventions, then verifies requirements, downstream behavior and gaps.
The lead and owners supply project-specific measurements and checks, then reconcile one report.
Reuse this evidence across the team. All five areas still need coverage:

| Area | Evidence required |
|---|---|
| Correctness | Requirement map, relevant boundary cases, test-oracle and downstream/legacy tracing |
| Simplicity | Each added abstraction/dependency/comment and touched dead/TODO block justified or flagged |
| Performance | Affected endpoints/serializers/loaders measured, or a specific reason measurement is skipped |
| Backend contract/style | Repo conventions, validation/write order, error vocabulary/status and wire consumers |
| Frontend design | Repo tokens/utilities, controls, translations, active/hidden state and browser acceptance |

Read relevant sections of [checks.md](references/checks.md), plus repo/parent instructions and local
overrides, conventions/rejected findings, design docs, error modules and domain flows. OCR's bundled
rules supplement those sources; they do not override them. Do not invent missing house rules.

Run or reuse required tests/lint/browser/log checks for the same source, dependencies, configuration
and environment. Run focused checks while iterating and full required verification once per batch.
Compare failing test IDs/kinds with a matching baseline, never counts alone. Do not stash or disturb
another worker for a baseline. A mocked or extracted-function probe proves only its tested boundary.
For Django scope, include `manage.py check` and `manage.py makemigrations --check --dry-run` in the
project's test environment; new warnings need findings and schema changes remain approval-gated.
When Sonar is configured, follow [sonarqube.md](references/sonarqube.md) after reviewer launch.
Missing, stale or partial analysis is unverified; listing server issues does not scan dirty edits.

## 5. Report, then stop

Ground truth first: revision, checks run/reused with provenance, baseline/new failures and unverified
paths. State reviewed/all-changed coverage and every exclusion/skip, including tests. Then one table:

`ID | Where | Kind | Finding | My call`

Keep stable b1/b2 backend, c1/c2 client and a1/a2 admin IDs. Each finding names setup/input, actual
wrong result, file/function/line, requirement or rule source, expected result and evidence. Separate
verified defects from open policy or coverage gaps. Use Bug, Must fix (new violation), Opportunistic
(touched pre-existing issue) and Out of scope; security-owned items are flag-and-stop. Deduplicate
reviewer/Sonar overlaps. Mark proposed savings separately; never invent line/query measurements.

End with a bounded verdict: exact revision, covered requirements, fresh reviewer evidence and limits.
No findings means only no findings within that scope/coverage; missing checks are not a green result.
Present the complete report and end the turn before assigning or applying fixes to new findings.
Severity, My call, accepted worker completion and a general review-and-fix request are not approval
of the reported IDs. No category, including cosmetic fixes, bypasses the user's decision.

After explicit approval, relay the approved IDs/scope and approval reference to owners. Preserve
prior authorization for an identified current batch; it does not authorize new findings, policy
changes, commits or pushes. Keep contract/API/status, endpoint, module, security and migration
changes propose-and-stop. Apply only the approved scope, rerun affected checks on the final snapshot
and revalidate independent coverage. Record escaped findings in the existing feature note: original
rule, why the requirement/oracle/scope/transition check missed it, approved remedy and regression proof.
A standalone audit creates no permanent feature note merely to satisfy a template.
