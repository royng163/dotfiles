## Approach
- Read existing files before writing. Don't re-read unless changed.
- Thorough in reasoning, concise in output.
- Skip files over 100KB unless required.
- No sycophantic openers or closing fluff.
- No emojis or em-dashes.
- Do not guess APIs, versions, flags, commit SHAs, or package names. Verify by reading code or docs before asserting.
- For any question about Claude Code, or a library/framework/SDK/CLI/API (behavior, config, flags, env vars, setup), query context7 first — even when confident. Do not answer such questions from memory alone; training data may be stale. Treat "I already know this" as the signal to check, not to skip.

## Code comments
- Comments describe what the code does for a future reader who has no idea a change was ever made. Never narrate the edit or its history.
- Banned: comparisons to prior/other versions or to the task ("all statuses, not just the dashboard ones", "now also handles X", "changed to", "previously", "as requested", "per ticket"). Strip the contrast and state the present behavior plainly, or omit the comment.
- Only add a comment when the code is non-obvious; do not annotate self-evident code.
- Never write `ponytail:`-style or persona/assumption-narrating comments (comments that justify a simplification, shortcut, or default, or that flag an assumption to revisit) even when a skill or persona suggests them. State present behavior plainly or omit.
- Keep comments short: at most 1-2 lines. Prefer fewer comments overall; don't explain how the code works step by step. If a comment needs a paragraph, the code or naming should carry it instead.

<!-- launchd sync probe -->
