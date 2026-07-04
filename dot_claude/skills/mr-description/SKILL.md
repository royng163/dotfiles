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
<UI: add screenshot/GIF. Backend: paste example output/log if available.>
```

Omit any section that would be empty — never print a heading followed by "none" or
"N/A". Summary and Changes are always present; Testing appears only when there is
something to say. Reference the Jira ticket in the Summary with the link embedded
inline — there is no separate Related section.

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


## Workflow


2. Enumerate scope with the commands above; exclude merged-in work (`git log --merges` to spot it).
3. Classify the dominant change type to set emphasis.
4. Draft the title, then Summary / Changes / Testing.
5. Print raw markdown in one fenced code block.
