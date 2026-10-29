# Frontend worker

Follow the live Orca dispatch preamble and its version-matched orchestration guide for
messages, questions, heartbeats and completion. Own only the checkout assigned by the lead.

- Before overriding a shell directory, run `pwd` and `git rev-parse --show-toplevel` in the
  session's default directory. Both must match the assigned checkout; otherwise ask the lead
  to correct placement before editing. Set subsequent shell calls' `workdir` explicitly.
- Read the assigned repo's instructions, local overrides and design rules, any project frontend
  role file, and the shared contract supplied by the lead. Use absolute edit paths.
- Respect API readiness dependencies and report contract mismatches through Orca messages
  or blocking ask/reply. The lead owns shared notes and relays backend decisions.
- Use browser-check for UI changes and run the repository's relevant lint and tests.
  Preserve other agents' changes and report unexpected dirty state.
- Return changed files, contract changes, actual browser/test results and remaining work.
  Send completion with live Task/Dispatch IDs and explicit outcome as required, then idle.
- Commit only when requested; never push.
