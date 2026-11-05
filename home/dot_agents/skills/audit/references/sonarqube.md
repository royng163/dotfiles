# SonarQube evidence

This is a read-only audit step. Do not upload a scan, change issue status or edit CI unless
that action is authorized. Use the project's existing analysis procedure when a fresh scan
is requested; `sonar list issues` only retrieves findings already stored on the server.

## Resolve the target

- Work from each actual repo root. Detect `sonar-project.properties`, `.sonar-config.json`,
  `.sonarlint/` or editor connected-mode settings, or CI Sonar configuration. A parent workspace can
  contain several projects; do not inherit one repo's project for another. No binding means
  **not configured**, not clean. Resolve ambiguous bindings with the user/lead.
- Verify `sonar --version` and `sonar auth status --format json`. Missing CLI, invalid auth,
  connection or permission errors mean **unverified**; name the missing prerequisite.
  Reuse an existing approved connection; never print tokens or store them in project files.
- Resolve the explicit project key from the binding and verify it on the connected server.
  Record server/version, project key, Git HEAD, audited scope and relevant dirty state.
- Determine the intended Git branch or MR/PR from the audit request and repository. Confirm
  the matching Sonar branch/PR exists and explicitly select `--branch` or `--pull-request`,
  never both. Missing branch/PR support or analysis means **unverified for this revision**.
  A default/main analysis can be offered as a separately labeled historical baseline, only
  with its actual identity recorded; never silently substitute it for the requested branch.

## Verify freshness

Inspect the server's analysis metadata for the selected target and record its analysis ID,
date and revision when available. Use the server's own `/web_api` documentation or
`sonar api get /api/webservices/list` to verify endpoint parameters for that server version.
Typical discovery endpoints are `/api/project_branches/list`, `/api/project_pull_requests/list`
and `/api/project_analyses/search`; do not assume they expose the same selectors or fields.

Compare the analyzed revision with the audited commit and check local modifications to
in-scope source, dependencies and analysis configuration. An equal branch name or a recent
timestamp alone does not prove matching code. Missing revision evidence, a different analyzed
commit, new/deleted files absent from analysis or uncommitted changes leave that coverage
**unverified/stale**. Server results may still be reported as historical context. A successful
pipeline or scanner process does not prove analysis completion or a passing quality gate;
when reporting the gate, verify the completed analysis and gate for that exact target with
`sonar quality-gate status --project <key> --branch <branch> --format json` (or the PR selector).

## Retrieve the entire scope

For each analyzed file in the audit scope, use an explicit target and repo-relative path:

```sh
sonar list issues --project <key> --branch <branch> --file <path> --statuses OPEN,CONFIRMED --format json --page-size 500 --page 1
```

For PR analysis, replace `--branch <branch>` with `--pull-request <id>`. Verify flags using
installed CLI help. Inspect returned pagination/total metadata and fetch subsequent pages
until all matches are covered; a full page is not proof of completion. Deduplicate by issue
key across overlapping file scopes. Record count/pages and any permission, truncation or API
limit. A partial retrieval is **unverified/partial**, never zero issues. For renamed/deleted
files, resolve analyzed component paths and state coverage gaps rather than silently skipping.
`--new-code` follows Sonar's configured new-code period; it is not the current Git diff.

When the CLI omits pagination or freshness detail, use its read-only `sonar api get` against
endpoints/parameters verified on that server. Keep secrets out of arguments/logs. Security
hotspots are separate from normal issues: retrieve relevant hotspots if claiming Sonar security
coverage, or explicitly state that hotspots were not checked. Keep out-of-scope findings out.

## Classify and report

- Match issue keys against a trustworthy baseline and inspect the current code/diff. A known
  baseline issue that still exists in a touched file is **Opportunistic**, subject to the
  audit's security/contract boundaries. An analyzed issue is not automatically pre-existing.
- A finding demonstrated to be introduced by the audited change uses the normal **Bug** or
  **Must fix** buckets. If attribution cannot be proven, report **attribution unknown**;
  creation date and Sonar's new-code marker alone do not prove introduction by this change.
- Confirm the code still exhibits the issue before offering a historical finding as current.
  Cite issue key, rule key, repo-relative file/line, target and analysis revision. Fixes still
  follow the audit's approval rules. Do not remediate or transition Sonar issues automatically.
- Ground truth states **verified**, **unverified/stale**, **unverified/partial**, **unavailable**
  or **not configured**, with provenance, counts and reasons. "No scoped open issues" applies
  only to complete matching analysis; it does not mean no bugs or no security problems.

Official references: [CLI commands](https://www.sonarsource.com/sonarqube/cli/commands.html),
[authentication](https://docs.sonarsource.com/sonarqube-cli/using-sonarqube-cli/environment-variables).
