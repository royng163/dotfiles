# Complementary audit checks

Read only the sections needed by the audited behavior. Use the repo's actual rules and tiering
(new code / touched code / do not start), including relevant parent/operator instructions.
OCR supplies common language-defect checklists; do not copy or re-review them in a second agent.
When OCR is unavailable, cover null/empty/boundary inputs, error paths, state transitions,
concurrency/idempotency, access/soft deletes and decimal/time handling directly.

## Simplicity

Inspect every in-scope file and added function, class, abstraction, dependency and comment.
Tag candidates `delete`, `stdlib`, `native`, `yagni`, `shrink` or `docs` with a concrete reason.
Check commented-out code and TODO/FIXME/XXX or deferred-phase notes in touched functions:
resolved, still open (tracker candidate), or stale. A `ponytail:` prefix is a docs finding.
Do not edit or move anything before the user's finding approval.

Comments describe present behavior for a new reader. Check the actual operator/repo limits:
no change history, task comparisons, ticket references or self-evident narration; no oversized
paragraphs or stub wrapping. Native/framework utilities precede custom dependencies and helpers.

## Performance

Measure only affected endpoints, serializers and loaders. State a specific skip reason otherwise.
Read the underlying rows/fields/payload/config rather than trusting an aggregate or log label.

- ORM: related-object traversal without eager loading; count/existence choices; loop queries;
  unbounded list endpoints; unnecessary public fields and many-to-many payloads.
- Query slope: compare representative 1/10/30-row cases and report queries per row with raw totals.
  For Django use the test environment and `CaptureQueriesContext(connection)` around the affected
  request. Use a scratch probe without persistent shared-data writes; no invented load result.
- Payload removal: search the bare field name across consumers, including aliases/types/templates;
  a dotted search misses callers. An unused-field claim still needs wire-contract approval.
- Frontend: independent serial awaits, requests inside loops, deep fetches, inconsistent store
  shapes, unnecessary refetches and route-loading conventions. Count awaits/requests; inspect
  browser network results when a dev server exists. Do not impose a framework pattern absent
  from the project's rules.

## Backend conventions and framework evidence

Read the declared styleguide, response/error vocabulary and status mapping, domain transitions
and relevant rejected findings. Check thin handlers, service signatures, validation before writes,
transaction/error boundaries, logging, module placement, timezone/decimal handling and explicit
scoping where default managers do not enforce it. These are prompts to check house rules, not
new rules to impose on an unrelated project.

Django static checks use the project's test environment. New warnings are Must fix findings;
pre-existing warnings in touched files are Opportunistic, other warnings one Out of scope line.
Migration detection must be clean or the required migration is proposed under the repo's rules.

### HTTP status and error codes

The repo owns its code-to-status map; RFC 9110 owns status semantics. Read the response helper,
vocabulary, exception classes and client branches on both code and status before proposing changes.
Every status/envelope/code change is a wire-contract proposal, never an automatic cleanup.

| Check | Evidence to inspect |
|---|---|
| Reachable error code missing from map | Actual fallback and whether it matches the condition |
| Success status with failure body | Envelope and HTTP semantics |
| Missing/malformed/expired credentials | Authentication refusal semantics, normally 401 |
| Authenticated but forbidden | Permission refusal semantics, normally 403; existence-disclosure policy |
| Missing/hidden resource | 404/403 choice against the approved disclosure rule |
| Duplicate/already-processed state | Current-state conflict semantics (409), existing exception and retry contract |
| Expected business refusal reported as 5xx | Client refusal versus actual server failure |
| Creation or bodyless deletion | Success status/body against the declared API contract and RFC |
| Hand-rolled 405/406/415 | Framework method/negotiation/media-type handling |
| Status literal or exception override | Whether shared mapping already owns the condition |
| Two codes for one condition | Divergent client behavior and declared contract |
| Vocabulary entry never raised | Confirm unused before a simplicity finding |

Cite the code, current/proposed status, condition and authority. Never treat a cheat sheet as
normative or silently change business policy. Sources:
[RFC 9110 §15](https://www.rfc-editor.org/rfc/rfc9110#section-15) and
[IANA HTTP registry](https://www.iana.org/assignments/http-status-codes/http-status-codes.xhtml).

## Frontend design and behavior

Read DESIGN.md or its equivalent. Check theme tokens versus literals, typography/spacing scale,
component variants/props, icon-only controls, translations/selectable locales and framework
utilities before scoped CSS. A necessary custom style uses theme variables and has a stated need.
Missing design authority means no invented design-system violation.

Verify the actual Save/Submit validation owner, not only a visible field's rules. Include invalid
hidden/internal/external views, tab/reload transitions, typed/native-price error handling and
saved/copied values when those behaviors change. Use original authority for expected behavior;
matching the backend's current mistake is not proof the UI is correct. Use browser-check on an
already running dev server for relevant flows, failed requests and layout geometry. Mocked Vue
or API doubles do not prove mounted validation, persistence or a real browser flow.

## Reporting limits and approved fixes

A correctness finding needs reproducible input and wrong outcome, not a suspicion. Keep old
findings separate from new ones and do not re-report a previously rejected or superseded remedy.
Missing test evidence is a gap; an undecided allocation/expiry policy is a question, not a guessed fix.

After user approval, small local candidates include eager loading, existence checks, token or
utility use, decimal rounding, logger use, provably independent concurrent loads and dead code.
Contract/status/payload changes need coordinated consumers; endpoint deletion, module movement,
security work and migrations retain their propose-and-stop boundary. Verify only approved fixes
with affected test modules plus required completion checks; report failures plainly.
