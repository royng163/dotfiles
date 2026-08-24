## Approach
- Read existing files before writing. Don't re-read unless changed.
- Thorough in reasoning, concise in output.
- Skip files over 100KB unless required.
- No sycophantic openers or closing fluff.
- No emojis or em-dashes.
- Do not guess APIs, versions, flags, commit SHAs, or package names. Verify by reading code or docs before asserting.

## Code comments
- Comments describe what the code does for a future reader who has no idea a change was ever made. Never narrate the edit or its history.
- Banned: comparisons to prior/other versions or to the task ("all statuses, not just the dashboard ones", "now also handles X", "changed to", "previously", "as requested", "per ticket"). Strip the contrast and state the present behavior plainly, or omit the comment.
- Only add a comment when the code is non-obvious; do not annotate self-evident code.
- Keep comments short: at most 1-2 lines. Prefer fewer comments overall; don't explain how the code works step by step. If a comment needs a paragraph, the code or naming should carry it instead.
- Fill the line before wrapping: write one line up to the project's print width (prettier `printWidth`, ruff/black `line-length`, else 100). A second line is only for text that genuinely doesn't fit, and then both lines run near-full — never a long first line with a few dangling words under it. Rewrite the sentence shorter rather than spilling into a stub line.
