## Approach
- Read existing files before writing. Don't re-read unless changed.
- Thorough in reasoning, concise in output.
- Skip files over 100KB unless required.
- No sycophantic openers or closing fluff.
- No emojis or em-dashes.
- Do not guess APIs, versions, flags, commit SHAs, or package names. Verify by reading code or docs before asserting.

## Simplest Solution
Read the task and trace the code it touches first, then stop at the first rung that holds:
1. Does it need to exist? A speculative need is skipped, with one line saying so.
2. Already in this codebase? Reuse the helper, util, type or pattern a few files over.
3. Does the standard library or the platform cover it (CSS over JS, a DB constraint over app code)?
4. Does an installed dependency solve it? Never add a dependency for a few lines of code.
5. Only then write the minimum code that works, in the fewest files, the shortest correct diff.
- No unrequested abstractions: no interface with one implementation, no config for a fixed value.
- A bug fix goes where every caller routes through, not only in the path the ticket names.
- Never simplify away input validation, error handling that prevents data loss, or security.

## Planning
- Before planning a non-trivial change, do a blind-spot pass: list what the request leaves unsaid,
  then interview the user one question at a time about anything that would change the data model,
  API contract or user flow.

## Git
- Run `git add` and `git commit` (including `--amend`) only when the user asks for that commit.
  Otherwise leave changes unstaged, report the state, and stop. Never run `git push`.
- Branch and worktree creation is fine.

## Code comments
- Comments describe what the code does for a future reader who has no idea a change was ever made. Never narrate the edit or its history.
- Banned: comparisons to prior/other versions or to the task ("all statuses, not just the dashboard ones", "now also handles X", "changed to", "previously", "as requested", "per ticket"). Strip the contrast and state the present behavior plainly, or omit the comment.
- Only add a comment when the code is non-obvious; do not annotate self-evident code.
- Keep comments short: at most 1-2 lines. Prefer fewer comments overall; don't explain how the code works step by step. If a comment needs a paragraph, the code or naming should carry it instead.
- Fill the line before wrapping: write one line up to the project's print width (prettier `printWidth`, ruff/black `line-length`, else 100). A second line is only for text that genuinely doesn't fit, and then both lines run near-full — never a long first line with a few dangling words under it. Rewrite the sentence shorter rather than spilling into a stub line.

## Current documentation
Do not answer from training data alone when the question is about a library,
framework, SDK, API, CLI tool, or cloud service — including well-known ones like
React, Next.js, Prisma, Express, Tailwind, Django or Spring Boot. Versions move,
flags get renamed, config keys change shape. Treat "I already know this" as the
signal to check, not to skip.

Applies to: API syntax, configuration keys, version migration, library-specific
debugging, setup instructions, CLI usage and flags.

Fetch the library's own current documentation with web tools or Context7, or web search when the
canonical URL is unknown. Prefer the official docs over blog posts and over
aggregators. Quote or cite what the docs actually say, and name the version when
behaviour is version-dependent.

Does not apply to: refactoring, writing scripts from scratch, debugging business
logic, code review, or general programming concepts.


## Orca teams
- "Use Orca teams" and "Orca this" request supervised Orca orchestration.
- Follow the orchestration skill, use Codex workers unless another agent is requested, and collect their results before finishing.
- Use Orca dispatches and messages for coordination; never substitute native subagents for an Orca team.
