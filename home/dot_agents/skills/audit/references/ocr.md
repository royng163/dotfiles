# OCR preparation inside audit

Use after the fresh reviewer has confirmed start and verified the declared snapshot. The reviewer
owns this preparation once per repo and shares artifacts with the lead; no second OCR review.
This integrates deterministic inventory/rule resolution, not OCR's model-managed review pipeline.

## Dependency and execution

Supported baseline: Open Code Review CLI 1.13.10, executable `ocr`. Check installed `ocr version`
and delegate help if its behavior differs. The chezmoi agent-tool installer provisions the CLI.
If unavailable or a command fails, report OCR unavailable and build the same inventory/checklists
with Git and repository rules; do not report clean or stop all review solely for this helper.
Do not install a second review skill, invoke `ocr review`/`scan`, configure a provider, or use OCR's
optional auto-fix workflow. Delegate commands use no model endpoint; Codex performs the review.

## Exact scope

For a committed range/MR, replace the variables with the already resolved absolute checkout
and immutable provider/Git base/head; preserve the same selectors for both commands:

```sh
ocr delegate preview --repo "$checkout" --from "$base" --to "$head" --format json
ocr delegate rule --repo "$checkout" --from "$base" --to "$head" --format json "$path"
```

Pass selected paths together or in bounded batches; shared rules are grouped by content.
Do not resolve each file in a separate process unless necessary. Save preview, grouped rules,
version and command results alongside existing audit artifacts, outside the checkout.

- Range mode uses merge-base-to-head and excludes dirty/untracked changes. Verify its returned
  merge_base/to match the declared audit scope; a mismatch is a blocker, not permission to widen it.
- Workspace mode omits from/to from both commands and includes staged/unstaged/untracked changes.
  Preserve the declared dirty snapshot; record `(path, status)` identities, including a staged
  deletion followed by an untracked recreation of the same path.
- Whole-file/path/whole-repo review uses the requested file inventory, not the diff preview as a
  substitute. Use delegate rule for applicable language rules and read the requested contents.
- For committed context read `git show "$head:$path"`; do not let today's checkout supply different
  code. Resolve relevant unchanged producers/consumers at the same pinned revision.

## Coverage and rule precedence

Reconcile preview's selected AND excluded paths with the actual in-scope Git changes. Maintain one
small ledger: repo/path/status, selected or exclusion reason, reviewed/skipped, and evidence/gap.
Review relevant changed tests, schema, migrations and config even when OCR's default filters exclude
them. Resolve rules for those paths where supported, otherwise apply repo/test-oracle checks directly.
Binary/secret and explicit user-scope exclusions stay excluded with reasons; do not force-read secrets.
Never call 18/18 selected files full coverage if 17 other changed tests remain unexamined.

Preserve project/global OCR rules and explicit exclusions. Do not write a global include-all override
or duplicate the repo's styleguide into OCR JSON. Bundled language rules are supporting checklists;
read repo/parent/local instructions and authoritative business rules independently. If custom OCR
rules replace language rules or exclude relevant paths, state the resulting gap and cover it under
repository authority rather than silently trusting the filter.

For each scope identity, finish the required reading or record a concrete skip reason. Validate
findings against original authority and a discriminating case; metadata and rules are not a code
review, and an OCR exclusion is not evidence that a file is safe.

Official sources: [delegation workflow](https://github.com/alibaba/open-code-review/blob/v1.13.10/skills/open-code-review-delegate/SKILL.md),
[rule/filter precedence](https://github.com/alibaba/open-code-review/blob/v1.13.10/pages/src/content/docs/en/review-rules.md).
