# Fresh independent reviewer

## Coordinator

The first substantive action of every audit effort is starting one fresh read-only reviewer.
Before launch, do only dispatch preparation: locate repo/scope and requirement/evidence links,
pin snapshot metadata, load orchestration guidance and check ownership. Sonar history/issues,
code/requirement analysis, test execution and old audit-report review wait until the start
receipt confirms a fresh reviewer session is started/ready. Do not wait for its final report
before beginning normal checks; those can run concurrently after confirmed launch.

In a cross-repo audit, use one reviewer across the declared surfaces; authors do not each
create another reviewer. A dispatched implementer asks the lead to launch that peer before
its own audit checks. If launch is blocked or uncertain, report it and stop audit analysis;
do not bypass nesting limits, substitute self-review or duplicate an uncertain launch.
Existing implementation evidence can be linked without repeating checks. The final audit
still requires accepted independent completion and coordinator reconciliation.

Follow the user's orchestration preference. In this setup use the Orca orchestration skill
and the selected CLI's current guide: reuse the feature Run or create one for a standalone
audit, then start a fresh Codex reviewer session. Native subagents are used only when the
user explicitly selects that separate workflow. If unavailable or refused, report the exact
blocker and leave independent review pending; never silently waive it or spawn duplicates.

The Task brief contains:
- Role: `audit independent reviewer`, a read-only leaf of this audit; do not spawn reviewers.
- Absolute checkout/source paths, instructions, original requirements/decisions, contract
  and skill path, exact MR/range/dirty snapshot and audit scope, and existing raw check logs.
- The objective: assess requirements, preserved/changed business rules, independently
  justified expected results and affected end-to-end/legacy/transition behavior.
- Constraints: no source/note/index/ref edits, fixes, shared-data writes, remote scans,
  issue-status changes, commits or pushes. Do not rerun full suites already proven for the
  same inputs. Run bounded read-only/isolated probes only for a specific evidence gap.
- Completion: coverage by requirement, reproducible findings with rule authority, unresolved
  decisions and limitations, plus the active Task/Dispatch's accepted worker_done evidence.

Do not include the author's verdict, rationale or suspected findings in the initial brief.
Link raw requirements and artifacts; the reviewer must question the contract/test assertions
against original authority. Supply explicit user decisions and approved prior findings when
needed to avoid reopening settled scope. The reviewer may inspect code/tests/relevant history.

Use a new session, not the implementation conversation or an author with the same history.
Read-only reviewers may share a checkout only while its audited snapshot stays stable;
they are not additional editors. Pin immutable blobs or isolate if concurrent edits would
invalidate the read. Record reviewer repo/terminal and title it `audit-reviewer`.

After confirmed reviewer launch, continue available author checks and follow Orca's wake
procedure when waiting; do not poll. Report pending work honestly while waiting. Require accepted completion
and reconcile the result with the source/authority, not a summary alone. Preserve stable
surface finding IDs, deduplicate overlapping findings and route approved fixes to owners.
After revisions, revalidate affected checks and independent-review coverage; do not reuse an
old verdict for a changed snapshot. Clean up the reviewer using the current lifecycle guide.

## Independent reviewer

When explicitly dispatched in that role, perform the requirements/behavior part of this
same audit and return evidence to its coordinator. Do not invoke a full nested audit or
start another reviewer. Check the actual target snapshot, requirement authorities, test
oracles and downstream preserved rules; a green test or author contract is not proof of
policy correctness. Reuse matching check results and name missing evidence.

The coordinator continues the normal five passes and owns the combined final verdict.
Review completion does not authorize fixes, MR publication or a blanket shipping guarantee.
