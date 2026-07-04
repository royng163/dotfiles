---
name: browser-check
description: Verify frontend changes in a real browser using patchright (stealth Chromium). Use after editing any web UI (Vue/React/Svelte/plain HTML components, pages, or styling) to confirm the page renders, catch console/page/network errors, and capture a screenshot — whenever the user asks to "check the page", "see if it works", "verify the UI", "screenshot the app", or after implementing a frontend change that should be visually confirmed. Works in any project with a running dev server.
---

# browser-check

Drive a running dev server with patchright and report what a real browser
sees: a screenshot plus any console errors, page errors, and failed requests.
Use this to confirm a frontend change actually works instead of guessing.
Project-agnostic — point it at whatever dev URL the current project serves.

## When to use

Auto-trigger after frontend edits (UI components, styling, routing) and
whenever the user wants the UI confirmed visually. Skip for backend-only or
non-UI changes.

## How

1. Find the dev server URL and port for THIS project (check its README /
   package.json scripts / vite/next/webpack config). Common defaults: Vite
   `5173`, Next/CRA `3000`. Note the base path and whether it's a hash router.

2. Ensure the dev server is running; if not, start it in the background with
   the project's command (e.g. `yarn dev`, `npm run dev`) and wait for it to
   print its local URL.

3. Run the driver. The URL is `BASE_URL + route` (absolute routes starting
   with `http` are used as-is):
   ```bash
   BASE_URL="http://localhost:5173/" \
   SCRATCHPAD="$CLAUDE_SCRATCHPAD" \
   python ~/.claude/skills/browser-check/scripts/check.py "/login" "/dashboard"
   ```
   - Hash-router app? End `BASE_URL` with `#`, e.g.
     `http://localhost:5173/admin/#`.
   - `SCRATCHPAD` = where screenshots go (use the session scratchpad).
   - `HEADLESS=0` to watch it run live.

4. Read the output:
   - **screenshot** path — Read it to visually confirm the change.
   - **issues list** — console errors/warnings, uncaught exceptions, failed
     requests. Exit code is non-zero if any fired.

5. If the screenshot or errors show a problem, fix and re-run. Report the
   result to the user with the screenshot.

## Notes

- patchright is preinstalled (Python `patchright.sync_api`) with Chromium
  binaries; no setup needed.
- API-driven pages need their backend running too — check the project's proxy
  config for the target.
- Auth: if a route redirects to login, note it and ask the user how to supply
  a token/session rather than guessing credentials.
