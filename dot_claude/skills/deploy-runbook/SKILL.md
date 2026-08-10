---
name: deploy-runbook
description: >
  Draft a deployment runbook for a release to a named environment (UAT, production),
  written to the workspace-root .notes/ folder. Inspects the release delta first to
  find irreversible migrations, new configuration, and startup blockers, then writes
  a minimal-structure runbook with a backup gate and an honest rollback section.
  Calibrates detail to the audience (internal ops vs external security review).
  Trigger: "deployment runbook", "deploy runbook", "release runbook", "deployment
  instructions", /deploy-runbook.
---

Draft a deployment runbook for a release. Analyse the release delta BEFORE writing.
Do NOT deploy anything, and do NOT commit.

## Output location


matching the existing files there (`Local Development Setup.md`):
`../.notes/<Environment> Deployment Runbook.md`

One file per environment. Re-running for a later release updates the same file.

## Step 1 — Establish the facts (never skip, never infer)

Ask the user first if unknown: target environment, version, audience, and how the
rollout is actually performed (console, CLI, or handed to another team). These
change the document materially and are not in the repos.

Then read, do not assume:

1. **Version range.** Last tag (`git tag --sort=-v:refname | head`), target version,
   and whether repos tag in lockstep.
2. **Destructive or irreversible migrations — the highest-value check.**
   ```
   git diff --name-only --diff-filter=A <lasttag>..<ref> -- '*/migrations/*.py'
   ```
   For each new migration, inspect for `RunPython`, `reverse_code`, `noop`,
   `delete()`, `hard_delete`, and raw SQL. Classify every one as reversible or not.
   A data migration whose reverse is `noop`/`RunPython.noop`, or that deletes rows,
   makes the backup step a **mandatory gate** and constrains the whole rollback
   section.
3. **When migrations run.** Check the entrypoint (`start.sh`, Dockerfile `CMD`,
   workload command overrides). If migrations run on container start, there is no
   window to inspect the database after the image change — say so explicitly.
4. **Which workloads migrate.** Workloads sharing the app image but overriding the
   command (Celery workers, schedulers) do NOT migrate. Only the one running the
   entrypoint does. This determines rollout order.
5. **New configuration.** `git diff --stat <lasttag>..<ref> -- <settings> <deps>`.
   If unchanged, state "no new environment variables, secrets, or dependencies" —
   it stops the reader hunting.
6. **Startup blockers.** Grep entrypoints and inject scripts for checks that exit
   non-zero on missing config (e.g. a required SDK URL). These cause crash-loops
   that look like deploy failures.
7. **Image and registry facts.** Read the CI config for the real registry
   hostnames, namespaces, repo names, and which tag pattern publishes where. Never
   recall these from memory.
8. **Submodule deltas**, if the repo uses them, and whether the referenced commits
   are pushed.
9. **Verification assets that already exist.** Look for a `docs/verify_*.sql` or
   similar written for these migrations, and reuse it rather than inventing checks.

## Step 2 — Structure

Minimal structure only. Metadata header plus five sections:

```
# <Environment> Deployment Runbook — Release vX.Y.Z

| Release | Environment | Approved by | Date | Change reference |   (table)

## 1. Scope          start state, end state, what is out of scope, workload table,
                     and the critical-notice callout if a migration is irreversible
## 2. Prerequisites  access table (least privilege), sign-off checklist,
                     database-changes table with a Reversible column
## 3. Procedure       numbered sub-steps, each with an Expected result
## 4. Verification    table: check / method / expected
## 5. Rollback        split by scenario; honest about what cannot be undone
```

Optional extras, only if the user wants an audit artifact: escalation contacts,
revision history, controls appendix. Default to leaving them out.

Standard-format background: no formal standard exists for runbook layout.
Practitioner templates (Google SRE, PagerDuty) are incident-oriented — trigger,
severity, decision trees — which do not fit a planned change. For planned changes
the relevant reference is ISO 27001:2022 Annex A 8.32 (Change Management), which
dictates content, not layout: each change proposed, impact-assessed, authorised,
tested, executed, documented, communicated. The metadata header plus the sign-off
checklist is what carries that evidence.

## Step 3 — Procedure ordering

Order is not arbitrary. Derive it from Step 1:

1. Verify the artifact exists in the target registry, and record current image tags
   and replica counts as rollback targets — before touching anything.
2. **Backup gate**, if any migration is irreversible. Must appear before any step
   that can trigger a migration, with the reason stated plainly. State that the
   backup is the only rollback mechanism when that is true.
3. Scale down workloads that share the image but do not migrate, so previous-version
   code cannot run against a migrated schema.
4. Deploy the migrating workload. Follow with an explicit **checkpoint** confirming
   migrations applied, with instructions to stop and roll back on failure.
5. Bring the remaining workloads up on the new version, then the web/static tier.

## Rules

- **Verify every command, path, and URL.** Read the files; fetch official docs for
  console navigation. Never invent a help URL, a console menu path, or a CLI flag.
  Prefer the user's own correction to a console label over the doc's wording.
- **Never state a security property without verifying it.** Check the actual
  Dockerfile/settings before writing "runs as non-root", "cookies are Secure", or
  similar. A false assurance in a review document is worse than an omission.
- **Rollback must be honest.** Reverting an image tag does not undo a data
  migration. If the platform's restore does not work in place (ApsaraDB RDS full
  restore provisions a NEW instance), say so and give the real routes plus the time
  implication, so it informs the go/no-go decision rather than surprising an
  incident.
- **Record rollback targets before changing anything**, not after.
- Give each procedure step an expected result. That, not prose, is what makes a
  runbook followable under pressure.
- Placeholders over guesses. If the namespace or workload name is not in the repos,
  leave `<placeholder>` and say so, rather than inventing a plausible name.
- Do not deploy, do not commit, do not tag.

## Audience calibration

| Audience | Include | Exclude |
|---|---|---|
| Internal ops | CI pipeline mechanics, tag/build commands, CLI, internal registry and tooling names | — |
| External security review | Console steps with official doc links, change-control framing, least-privilege access table | Self-hosted CI details, internal repo paths, full env-var dumps, raw SQL |

If the rollout is console-only, drop every CLI command rather than offering both.

## Alibaba Cloud console references



| Operation | Doc |
|---|---|
| RDS manual full backup | https://www.alibabacloud.com/help/en/rds/apsaradb-rds-for-mysql/full-backup |
| RDS full restore (creates a new instance) | https://www.alibabacloud.com/help/en/rds/apsaradb-rds-for-mysql/restore-full-data-of-an-apsaradb-rds-for-mysql-instance |
| RDS restore individual databases/tables (into the original instance) | https://www.alibabacloud.com/help/en/apsaradb-for-rds/latest/restore-the-individual-databases-and-tables-of-an-apsaradb-rds-for-mysql-instance |
| ACK manage deployments | https://www.alibabacloud.com/help/en/ack/ack-managed-and-ack-dedicated/user-guide/create-a-stateless-application-by-using-a-deployment |
| ACK view pod logs | https://www.alibabacloud.com/help/en/ack/ack-managed-and-ack-dedicated/user-guide/manage-pods |
| ACR view image versions | https://www.alibabacloud.com/help/en/acr/getting-started/use-a-container-registry-enterprise-edition-instance-to-push-and-pull-images |
| DMS SQL Console | https://www.alibabacloud.com/help/en/dms/manage-a-database-on-the-sqlconsole-tab |

## Output

Write `../.notes/<Environment> Deployment Runbook.md`. Then report, outside the
document: any irreversible migration found, any unverifiable claim left out, and
every placeholder the user must fill.
