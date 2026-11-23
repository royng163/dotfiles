# OCR delegation inside audit

After verifying the declared snapshot, the fresh Codex reviewer runs OCR delegation once per repo.
OCR provides local file selection and grouped language rules. The Codex reviewer reviews the code.
Delegation requires only the local `ocr` executable. Use `ocr delegate preview` and
`ocr delegate rule` as the OCR entry points for an audit.

## Scope and rules

For MR or committed range scope, pass the verified merge-base and head to both commands:

```sh
ocr delegate preview --repo "$checkout" --from "$base" --to "$head" --format json
ocr delegate rule --repo "$checkout" --from "$base" --to "$head" --format json "${paths[@]}"
```

- Confirm the preview's merge base and head match the declared scope. Read committed source and
  context from pinned Git blobs. For a whole working diff, omit both range flags and recheck
  staged, unstaged and untracked identities afterward.
- Pass paths together or in bounded batches to reuse grouped rules. For a file, directory or
  other restricted scope, inventory the requested paths directly and resolve rules for those paths.
- Use the applicable Simplest Solution rule and repo instructions as the authority. OCR's
  bundled rules provide additional language checks. Preserve configured safe exclusions.

## Coverage and fallback

- Reconcile selected and excluded paths with all in-scope Git changes. Keep one ledger of paths
  reviewed or skipped, with reasons. Check relevant excluded tests, schemas, migrations and config.
  Treat binary files, secret paths and explicit scope exclusions as recorded exclusions.
- Review changed code and the collaborators needed to verify each affected behavior. Confirm
  findings against source and use targeted probes for behavior or performance claims. Share the
  review and ledger so the lead can focus on separate project checks.
- If the local CLI is unavailable or a delegate command fails, record the gap and use Git plus
  repository rules to review the affected scope. Preserve the independent reviewer and approval gate.

[OCR delegation documentation](https://github.com/alibaba/open-code-review/blob/v1.14.2/pages/src/content/docs/en/integrations/delegate.md)
