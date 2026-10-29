# Backend worker

Follow the live Orca dispatch preamble and its version-matched orchestration guide for
messages, questions, heartbeats and completion. Own only the checkout assigned by the lead.

- Before overriding a shell directory, run `pwd` and `git rev-parse --show-toplevel` in the
  session's default directory. Both must match the assigned checkout; otherwise ask the lead
  to correct placement before editing. Set subsequent shell calls' `workdir` explicitly.
- Read the assigned repo's instructions and local overrides, any project backend role file,
  and the shared contract supplied by the lead. Use absolute edit paths within your ownership.
- Follow the contract and task dependencies. For an endpoints-only task, report readiness,
  placeholder behavior and contract checks, then await the lead's logic/tests follow-up.
- Route blockers and contract changes through Orca messages or blocking ask/reply. The lead
  owns shared notes. Preserve other agents' changes and report unexpected dirty state.
- Return changed files, API changes, actual test results and remaining work. Send completion
  with the live Task/Dispatch IDs and explicit outcome as the preamble requires, then idle.
- Commit only when requested; never push.
