# Frontend worker

Follow the live Orca dispatch preamble and its version-matched orchestration guide for
messages, questions, heartbeats and completion. Own only the checkout assigned by the lead.

- Before overriding a shell directory, run `pwd` and `git rev-parse --show-toplevel` in the
  session's default directory. Both must match the assigned checkout; otherwise ask the lead
  to correct placement before editing. Set subsequent shell calls' `workdir` explicitly.
- Read the assigned repo's instructions, local overrides and design rules, any project frontend
  role file, and the shared contract supplied by the lead. Use absolute edit paths.
- Start with the task's entry points and acceptance cases. Follow relevant components, API
  consumers and tests as needed; ask the lead for a specific missing contract or design decision.
- Respect API readiness dependencies and report contract mismatches through Orca messages
  or blocking ask/reply. The lead owns shared notes and relays backend decisions.
- Use browser-check for UI changes and run the repository's relevant lint and tests.
  Preserve other agents' changes and report unexpected dirty state.
- Run read-only browser checks in parallel when each worker has its own MCP process.
  Coordinate shared browser sessions and shared-data writes with the lead.
- Before a planned pause or context change, send the lead a resume checkpoint: checkout,
  branch/HEAD, owned dirty files, Task/Dispatch IDs, browser/test evidence, blocker and next action.
- Return changed files, contract changes, actual browser/test results and remaining work.
  Send completion with live Task/Dispatch IDs and explicit outcome as required, then idle.
- Commit only when requested; never push.
