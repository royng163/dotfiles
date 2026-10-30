---
name: mr-description
description: >
  Generate MR title + body as a communication artifact: action-oriented title, then
  Summary / Changes / Testing, plus a deployment checklist when needed. Changes grouped by feature with rationale only
  when non-obvious; Testing gives steps with expected outcomes. Emphasis adapts to change
  type. Diffs against the repo's default branch unless told otherwise. Prints raw
  markdown in a code block so it is copyable.
  Trigger: "write MR", "PR body", "summarize branch", /mr.
---

A PR body lets a reviewer grasp what changed, why it matters, and how to verify it
without reading the diff. Keep it tight: short sentences, one line per bullet, no filler.

Bias hard toward brevity. The whole body should scan in under 30 seconds. When in doubt,
cut. A reviewer opens the diff for detail — the body orients, it does not transcribe.

## Defaults

- Target: the repo's default branch — `git symbolic-ref --short refs/remotes/origin/HEAD`. A project that merges into a long-lived release or variant branch instead will say so in its own docs or a project-level override of this skill; honour that over the default.
- Scope: `git log <target>..HEAD --no-merges` + `git diff <target> --stat`.
- Print the whole body in one fenced code block (``` ``` ```) so it is copyable. No preamble, no file writing.
- No file/line counts — reviewers see those in the UI.

## Structure

```
<title>

## Summary
<1-2 sentences: what this does and why. Lead with the outcome. Embed the issue link inline here, e.g. "... ([ABC-366](<tracker-url>/ABC-366)).">

## Changes
**<Area>**
- <what changed> (`<filename>: <function or method>()`; `<other filename>: <function or method>()`)

## Testing
- <command / step> → <expected outcome>
<UI: one screenshot/GIF placeholder. Backend: at most 2 lines of example output.>

## Deployment checklist
- [ ] After deployment: <required command or manual step> → <expected result>

## Related MRs
- <label>: <MR link>
```

Omit any section that would be empty — never print a heading followed by "none" or
"N/A". Summary and Changes are always present; Testing appears only when there is
something to say. Reference the Jira ticket in the Summary with the link embedded
inline. Add a Related MRs section when the feature spans repos or surfaces — if the
project keeps work notes, check the feature's note for which surfaces it touched.
Emit a placeholder link (e.g. `<backend MR link>`) per companion MR; never ask for or
invent URLs. Omit the section when the work stands alone.

## Length budget

Hard caps, not aspirations. Whole body **under ~150 words**, except when required deployment
instructions need more space. If it does not fit, cut content
— do not compress by removing spaces or merging unrelated points into one bullet.

- Summary: **one sentence.** A second is allowed only for a fix that needs symptom + cause.
- Changes: **3-5 bullets total**, hard cap 6 — across all areas, not per area.
- Every bullet: **one line, ~15 words max**, excluding its reference suffix. No wrapped continuation lines. If a bullet needs
  two clauses joined by a dash, the rationale is probably inferable — drop it.
- Rationale: only for a decision a reviewer would question, and ~8 words max.
- Area headings: only with 2+ genuinely distinct areas **and** more than 4 bullets. Otherwise
  just list bullets with no heading.
- Testing: 1-3 bullets, ~12 words each.
- One bullet per user-facing behaviour or decision, not per field/column/method/file. Name the
  shape ("Members + Equipment sheets"), not the contents.

Never include: restatements of the title, mechanism detail the diff already shows, measurement
dumps or tables, or a bullet a reader could infer from another bullet.

When creating the MR, open it as a draft (`glab mr create --draft`) and assign no reviewers; the
author marks it ready and picks them.

## Emphasis by change type

Keep the structure above; shift the stress:
- **Feature** — Summary = user story; Changes span the stack; Testing = concrete steps; add visual proof for UI.
- **Fix** — Summary = symptom + root cause; Testing = the failing case now passing (regression test).
- **Refactor** — Summary asserts behavior unchanged + names the benefit; Testing = suite still green.
- **Deps** — Summary = version deltas + notable impacts; Testing = app still runs.
- **Docs/chore** — Summary = rationale + who is affected.

## Rules

- Title: specific, action-oriented, imperative, lowercase first letter, no period, ~72 chars. Optional conventional-commit prefix (feat/fix/refactor/deps/docs).
- Group Changes by feature, not file. Rationale only for non-obvious decisions.
- End every Changes bullet with parenthesized references: (`example.py: Class.method()`; `other.py: function()`). Use only filenames, without directory paths, and verify exact function or method names in the diff and source. Wrap each reference separately in backticks and separate them with semicolons. Include the relevant files and functions for that feature change, repeating the filename for each function. Use (`filename`) when the change has no named function, such as configuration, styles or documentation.
- Testing states expected outcomes, not just "ran tests".
- Use backticks for Changes references and deployment commands; keep paths and symbols elsewhere in the body plain.
- Include a Deployment checklist only when this change requires deployment follow-up, such as a migration, seed, management command or manual restart. Use unchecked Markdown checkboxes with the required timing/order, verified command or step, and expected result. Check source, deployment configuration and work notes; include manual actions still needed beyond existing automation. Never invent commands or execute them while generating the description.
- Describe only this branch's commits; drop work merged in from the target.
- Omit empty sections entirely — no "none"/"N/A" placeholder headings.
- Reference the issue only in the Summary, with the link embedded inline. Take the tracker's URL shape from the project's own docs or an existing MR; never invent a host. Do not put the issue in Related MRs.
- Related MRs section: include for split features; one bullet per companion MR, labelled by the surface it covers, each a placeholder link. Never fabricate a URL. Keep it last.

## Workflow

1. Get the branch and resolve the target. Ask if the resolved default looks wrong for this project.
2. Enumerate scope with the commands above; exclude merged-in work (`git log --merges` to spot it). Read the relevant diff and source to verify each Changes reference.
3. Classify the dominant change type to set emphasis.
4. Draft the title, then Summary / Changes / Testing. Check deployment configuration and work notes for required follow-up and add a Deployment checklist when needed.
5. Check the work note for split-feature phases; if any, add a Related MRs section (last) with placeholder links.
6. Print raw markdown in one fenced code block.
