#!/usr/bin/env python3
"""Drive a running dev server with patchright (stealth Chromium) and report what
a real browser sees: screenshot + console errors + failed requests.

Usage:
    BASE_URL=http://localhost:5173/ python check.py <route> [route2 ...]
    python check.py "/login" "/dashboard"
    python check.py "http://localhost:3000/full/url"   # absolute route wins

The final URL is BASE_URL + route, unless route is absolute (starts http).
For hash-router apps set BASE_URL to end in '#' (e.g. http://localhost:5173/admin/#).
Env: BASE_URL (default http://localhost:5173/), SCRATCHPAD (screenshot dir,
default ./), HEADLESS=0 to watch live.
Exit code is non-zero if any page emitted a console/page/request error.
"""
import os
import re
import sys

from patchright.sync_api import sync_playwright

BASE_URL = os.environ.get("BASE_URL", "http://localhost:5173/")
OUT_DIR = os.environ.get("SCRATCHPAD") or "."
HEADLESS = os.environ.get("HEADLESS", "1") != "0"


def check(page, route):
    errors = []
    page.on("console", lambda m: errors.append(f"console.{m.type}: {m.text}")
            if m.type in ("error", "warning") else None)
    page.on("pageerror", lambda e: errors.append(f"pageerror: {e}"))
    page.on("requestfailed", lambda r: errors.append(
        f"requestfailed: {r.method} {r.url} -> {r.failure}"))

    url = route if route.startswith("http") else BASE_URL + route.lstrip("/")
    page.goto(url, wait_until="networkidle", timeout=30000)
    page.wait_for_timeout(800)  # ponytail: fixed settle; bump if SPA renders slow

    slug = re.sub(r"[^a-zA-Z0-9]+", "_", route).strip("_") or "root"
    shot = os.path.join(OUT_DIR, f"check_{slug}.png")
    page.screenshot(path=shot, full_page=True)
    return shot, [e for e in errors if e]


def main(routes):
    failed = False
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS)
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        for route in routes:
            shot, errors = check(page, route)
            print(f"\n=== {route} ===")
            print(f"screenshot: {shot}")
            if errors:
                failed = True
                print(f"{len(errors)} issue(s):")
                for e in errors:
                    print(f"  - {e}")
            else:
                print("no console/page/request errors")
        browser.close()
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main(sys.argv[1:] or ["/"])
