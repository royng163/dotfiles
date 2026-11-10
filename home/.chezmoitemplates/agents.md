## Approach
- Read existing files before writing. Don't re-read unless changed.
- Thorough in reasoning, concise in output.
- Skip files over 100KB unless required.
- No sycophantic openers or closing fluff.
- No emojis or em-dashes.
- Do not guess APIs, versions, flags, commit SHAs, or package names. Verify by reading code or docs before asserting.

## Simplest Solution
Read the task and trace the code it touches first, then stop at the first rung that holds:
1. Does it need to exist? A speculative need is skipped, with one line saying so.
2. Already in this codebase? Reuse the helper, util, type or pattern a few files over.
3. Does the standard library or the platform cover it (CSS over JS, a DB constraint over app code)?
4. Does an installed dependency solve it? Never add a dependency for a few lines of code.
5. Only then write the minimum code that works, in the fewest files, the shortest correct diff.
- No unrequested abstractions: no interface with one implementation, no config for a fixed value.
- A bug fix goes where every caller routes through, not only in the path the ticket names.
- Never simplify away input validation, error handling that prevents data loss, or security.

## Planning
- Before planning a non-trivial change, do a blind-spot pass: list what the request leaves unsaid,
  then interview the user one question at a time about anything that would change the data model,
  API contract or user flow.

## Git
- Run `git add` and `git commit` (including `--amend`) only when the user asks for that commit.
  Otherwise leave changes unstaged, report the state, and stop. Never run `git push`.
- Branch and worktree creation is fine.

## Acceptance and continuity
- Before changing behavior, define concrete inputs or setup and the expected result. For features, keep these acceptance cases in the existing work-note contract and name how each will be checked.
- For a bug fix, reproduce the failure and capture a failing regression check before the fix when practical. Reuse repository checks; record baseline failures and distinguish them from regressions.
- Before compaction, restarting or switching to unrelated work, save a concise resume checkpoint in the existing work note or task record. Follow the work-note skill's checkpoint format for features; verify filesystem and live worker state on resume. Checkpointing does not authorize a stash or commit.
- Use `capture-lessons` when explicitly asked to save reusable learning. Keep project lessons in project instructions and portable preferences in the chezmoi-managed shared source.

## Code comments
- Comments describe what the code does for a future reader who has no idea a change was ever made. Never narrate the edit or its history.
- Banned: comparisons to prior/other versions or to the task ("all statuses, not just the dashboard ones", "now also handles X", "changed to", "previously", "as requested", "per ticket"). Strip the contrast and state the present behavior plainly, or omit the comment.
- Only add a comment when the code is non-obvious; do not annotate self-evident code.
- Keep comments short: at most 1-2 lines. Prefer fewer comments overall; don't explain how the code works step by step. If a comment needs a paragraph, the code or naming should carry it instead.
- Fill the line before wrapping: write one line up to the project's print width (prettier `printWidth`, ruff/black `line-length`, else 100). A second line is only for text that genuinely doesn't fit, and then both lines run near-full — never a long first line with a few dangling words under it. Rewrite the sentence shorter rather than spilling into a stub line.

## Current documentation
Do not answer from training data alone when the question is about a library,
framework, SDK, API, CLI tool, or cloud service — including well-known ones like
React, Next.js, Prisma, Express, Tailwind, Django or Spring Boot. Versions move,
flags get renamed, config keys change shape. Treat "I already know this" as the
signal to check, not to skip.

Applies to: API syntax, configuration keys, version migration, library-specific
debugging, setup instructions, CLI usage and flags.

Fetch the library's own current documentation with web tools or Context7, or web search when the
canonical URL is unknown. Prefer the official docs over blog posts and over
aggregators. Quote or cite what the docs actually say, and name the version when
behaviour is version-dependent.

Does not apply to: refactoring, writing scripts from scratch, debugging business
logic, code review, or general programming concepts.


## Computer use
- Prefer CLI, filesystem and service APIs for tasks they can complete. For GUI-only tasks, use Orca's computer-use skill first. If Orca is unavailable, lacks permission or cannot complete the action, use OpenAI's native Computer Use plugin with its app approvals; keep the ChatGPT app running for that fallback. Inspect the current app state before retrying an action whose outcome is uncertain. Keep browser-check and Patchright for frontend verification.

## Orca Codex workers
- "Use a team", "Team this", "Use Orca teams" and "Orca this" mean supervised Orca Codex workers. Otherwise keep small single-repo work in an ordinary repo session. Native subagents require an explicit request.
- Load the installed `orchestration` skill's version-matched guide once; it owns launch, messaging, wake, reuse and cleanup procedures. Read conditional references only at their action gate. Start independent work together, then end the turn for Orca to wake the lead; never add polling/watch scripts or terminal-input steering.
- Use one Run per effort and one editing worker per affected checkout; a fresh read-only audit reviewer may inspect stable snapshots across those checkouts. Before launch, check unique live handles and saved tabs across Runs, preserve other leads' ownership and resolve the exact existing repo workspace. Prefer primary checkouts; isolate only when requested or concurrency requires it. A timeout is not proof of exit.
- Give each Task one coherent repo change, including known follow-ups, with absolute checkout, portable prompt (`~/.agents/orca/backend-dev.md` or `frontend-dev.md`), project role and shared-note paths, branch/base, exclusive ownership, entry points and acceptance checks. Link authoritative context; do not paste whole histories. Depend only on real prerequisites; split endpoint readiness only when it unblocks another surface.
- Workers verify default `pwd` and Git root before editing, read their repo instructions/local overrides, then use explicit shell workdirs and absolute edit paths. Batch independent reads/checks and bound tool output; preserve full failure logs on disk. Avoid repeated scans, redundant preservation probes and extra reports without a concrete risk.
- Workers may exchange factual API readiness, existing contract details, test results and blockers directly through Orca messages, copying the lead on actionable results. Contract/scope decisions still go through the lead's ask/reply; only the lead edits shared notes. Independent UI/tests may proceed against the agreed contract while backend logic runs; live acceptance waits for actual readiness. Coordinate shared-data writes and shared browser contexts.
- Run focused checks while iterating and full repository verification once per completed change batch. Reuse evidence only for the same relevant source, dependencies, configuration and environment; record its provenance and baseline failures. Revisions rerun affected checks, and the final changed snapshot receives required verification. The lead checks gaps and cross-repo contracts rather than duplicating accepted worker suites. Tests prove their assertions, not the business rule; check expected behavior against original authority. Full audits remain request-driven; before high-risk MRs are ready, require the audit's fresh requirement/behavior review without duplicating the five passes.
- Keep workers as terminal tabs in their assigned repo projects; report repo/handle and set a verified role-based custom tab title after launch/reuse. Reuse the same worker for queued follow-ups through the current guide's supported route. Do not enable Keep open just for visibility; retain only for explicit queued dependencies or a direct retention request, clear it when that queue empties, and verify saved-tab cleanup as well as live state. Follow recovery receipts; never replace an unproven worker.
- Contracts map changed behavior to original ticket/spec/user decisions and checks, with preserved/changed rules and unresolved policy explicit. Audit scopes pin actual MR base/head or dirty snapshots. Each audit effort first launches one fresh read-only reviewer through the lead/current orchestration guide using existing snapshot/manifest and requirement links plus a concise brief, before Sonar history, code analysis or audit checks. Do not rebuild/compare manifests or prepare another review packet before launch; the reviewer verifies the declared snapshot first after launch. Require a confirmed start; a blocked/uncertain launch blocks audit analysis. Keep it separate from author history; independent reviewers never spawn reviewers. Validate later review findings against approved rules and record regression evidence in existing feature notes/tests.
- Accept only the active Task/Dispatch's `worker_done` and actual evidence. Report test ground truth, then team audit findings in one table: `ID | Where | Kind | Finding | My call`. Keep independent stable IDs `b1` backend, `c1` client, `a1` admin. Present new findings to the user and end the turn before fix dispatch or source edits; My call, severity and accepted worker completion are not approval. Relay user-approved IDs/scope and their approval reference to owners. Preserve existing explicit authorization for current batches; new findings need their own approval.
- Diagnose slowness by phase (startup, first edit, implementation, tests/browser, coordination waits) using existing timestamps and logs. Check CPU/memory, MCP startup and network/proxy errors before changing resources or launch settings; collect more evidence only for an unresolved delay. Keep Sol High, Standard speed by default, Extra High planning and the configured context window unless the user changes them. Enable Fast only when requested.
