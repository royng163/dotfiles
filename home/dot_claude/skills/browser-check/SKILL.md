---
name: browser-check
description: Verify frontend changes in a real browser through the patchright MCP server (stealth Chromium). Use after editing any web UI (Vue/React/Svelte/plain HTML components, pages, or styling) to confirm the page renders, catch failed and 4xx/5xx requests, drive a flow, and capture screenshots — whenever the user asks to "check the page", "see if it works", "verify the UI", "screenshot the app", or after implementing a frontend change that should be visually confirmed. Works in any project with a running dev server.
---

# browser-check

Drive a running dev server with the `patchright` MCP tools (`mcp__patchright__browser_*`) and
report what a real browser sees. Use this to confirm a frontend change works instead of guessing.

## How

1. Find the dev server URL for this project (README, `package.json` scripts, vite/next config):
   base path, and whether it is a hash router (`http://localhost:5173/admin/#/route`). Use a
   server that is already running; start one only if the project's docs allow it.
2. `browser_set_viewport` first when the size matters (it reloads the page).
3. `browser_navigate` to the route, then `browser_wait_for` a selector the change renders, so
   the page has loaded its data before you judge it.
4. Drive the flow with `browser_click`, `browser_type` and `browser_evaluate`. Prefer a stable
   selector over text.
5. `browser_errors` after each page or step: it returns failed requests and 4xx/5xx responses
   since the last call. Patchright disables the console API, so console errors and uncaught
   exceptions do not show; read them with `browser_evaluate` if the app logs them somewhere.
6. `browser_screenshot` to confirm visually. Pass `path` to keep the file, e.g. for MR shots.

Report what you checked, every error found, and the screenshots. If something is wrong, fix it
and run the steps again.

## Notes

- API-driven pages need their backend up; check the project's proxy config for the target.
- If a route redirects to login, ask the user how to supply a session rather than guessing
  credentials.
- `browser_close` when done, so the next check starts from a clean context.
