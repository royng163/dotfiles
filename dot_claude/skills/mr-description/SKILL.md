---
name: mr-description
description: >
  Generate MR title + body as a communication artifact: action-oriented title, then
  Summary / Changes / Testing. Changes grouped by feature with rationale only
  when non-obvious; Testing gives steps with expected outcomes. Emphasis adapts to change

  copyable. Trigger: "write MR", "PR body", "summarize branch", /mr.
---

A PR body lets a reviewer grasp what changed, why it matters, and how to verify it
without reading the diff. Keep it tight: short sentences, one line per bullet, no filler.

Bias hard toward brevity. The whole body should scan in under 30 seconds. When in doubt,
cut. A reviewer opens the diff for detail — the body orients, it does not transcribe.

## Defaults


- Print the whole body in one fenced code block (``` ``` ```) so it is copyable. No preamble, no file writing.
- No file/line counts — reviewers see those in the UI.

## Structure

```
<title>

## Summary


## Changes
**<Area>**
- <what changed> — <rationale only if non-obvious>

## Testing
- <command / step> → <expected outcome>
<UI: one screenshot/GIF placeholder. Backend: at most 2 lines of example output.>

## Related MRs
- <label>: <MR link>
```

Omit any section that would be empty — never print a heading followed by "none" or
"N/A". Summary and Changes are always present; Testing appears only when there is
something to say. Reference the Jira ticket in the Summary with the link embedded
inline. Add a Related MRs section when the feature spans repos or phases — check the

Emit a placeholder link (e.g. `<backend MR link>`) per companion MR; never ask for or
invent URLs. Omit the section when the work stands alone.

## Length budget

Hard caps, not aspirations. Whole body **under ~150 words**. If it does not fit, cut content
— do not compress by removing spaces or merging unrelated points into one bullet.

- Summary: **one sentence.** A second is allowed only for a fix that needs symptom + cause.
- Changes: **3-5 bullets total**, hard cap 6 — across all areas, not per area.
- Every bullet: **one line, ~15 words max.** No wrapped continuation lines. If a bullet needs
  two clauses joined by a dash, the rationale is probably inferable — drop it.
- Rationale: only for a decision a reviewer would question, and ~8 words max.
- Area headings: only with 2+ genuinely distinct areas **and** more than 4 bullets. Otherwise
  just list bullets with no heading.
- Testing: 1-3 bullets, ~12 words each.
- One bullet per user-facing behaviour or decision, not per field/column/method/file. Name the
  shape ("Members + Equipment sheets"), not the contents.

Never include: restatements of the title, mechanism detail the diff already shows, measurement
dumps or tables, or a bullet a reader could infer from another bullet.

## Emphasis by change type

Same four headings; shift the stress:
- **Feature** — Summary = user story; Changes span the stack; Testing = concrete steps; add visual proof for UI.
- **Fix** — Summary = symptom + root cause; Testing = the failing case now passing (regression test).
- **Refactor** — Summary asserts behavior unchanged + names the benefit; Testing = suite still green.
- **Deps** — Summary = version deltas + notable impacts; Testing = app still runs.
- **Docs/chore** — Summary = rationale + who is affected; note any post-merge action.

## Rules

- Title: specific, action-oriented, imperative, lowercase first letter, no period, ~72 chars. Optional conventional-commit prefix (feat/fix/refactor/deps/docs).
- Group Changes by feature, not file. Rationale only for non-obvious decisions.
- Testing states expected outcomes, not just "ran tests".
- No backticks on paths/symbols in the body.
- Describe only this branch's commits; drop work merged in from the target.
- Omit empty sections entirely — no "none"/"N/A" placeholder headings.

- Related MRs section: include for split features (see the work note); one bullet per companion MR, labelled by role (Backend, Frontend, Integration), each a placeholder link. Never fabricate a URL. Keep it last.

## Workflow


2. Enumerate scope with the commands above; exclude merged-in work (`git log --merges` to spot it).
3. Classify the dominant change type to set emphasis.
4. Draft the title, then Summary / Changes / Testing.
5. Check the work note for split-feature phases; if any, add a Related MRs section (last) with placeholder links.
6. Print raw markdown in one fenced code block.
