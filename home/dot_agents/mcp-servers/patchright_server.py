#!/usr/bin/env python3
"""Patchright MCP server — drop-in replacement for @playwright/mcp."""

import asyncio
import base64
import os
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, ImageContent

server = Server("patchright")

_browser = None
_context = None
_page = None
_pw = None
_viewport = {"width": 1280, "height": 720}
_issues = []


async def _new_page():
    global _context, _page
    _context = await _browser.new_context(viewport=_viewport)
    _page = await _context.new_page()
    # patchright disables the console API for stealth, so console and page errors never fire
    _page.on("requestfailed", lambda r: _issues.append(f"requestfailed: {r.method} {r.url} -> {r.failure}"))
    _page.on("response", lambda r: _issues.append(f"http {r.status}: {r.request.method} {r.url}")
             if r.status >= 400 else None)


async def get_page():
    global _browser, _pw
    if _page is None:
        from patchright.async_api import async_playwright
        _pw = await async_playwright().start()
        _browser = await _pw.chromium.launch(headless=True)
        await _new_page()
    return _page


@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="browser_navigate",
            description="Navigate to a URL",
            inputSchema={
                "type": "object",
                "properties": {"url": {"type": "string", "description": "URL to navigate to"}},
                "required": ["url"],
            },
        ),
        Tool(
            name="browser_screenshot",
            description="Take a screenshot of the current page",
            inputSchema={
                "type": "object",
                "properties": {
                    "full_page": {"type": "boolean", "description": "Capture full scrollable page (default false)"},
                    "path": {"type": "string", "description": "Also save the PNG to this absolute path"},
                },
            },
        ),
        Tool(
            name="browser_click",
            description='Click a CSS or Playwright selector. For visible text use text="Save".',
            inputSchema={
                "type": "object",
                "properties": {
                    "selector": {"type": "string", "description": 'CSS or Playwright selector, e.g. #save or text="Save"'}
                },
                "required": ["selector"],
            },
        ),
        Tool(
            name="browser_type",
            description="Type text into a focused element",
            inputSchema={
                "type": "object",
                "properties": {
                    "selector": {"type": "string", "description": "CSS selector of input"},
                    "text": {"type": "string", "description": "Text to type"},
                },
                "required": ["selector", "text"],
            },
        ),
        Tool(
            name="browser_snapshot",
            description="Get the ARIA snapshot of the current page",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="browser_evaluate",
            description="Execute JavaScript in the page context",
            inputSchema={
                "type": "object",
                "properties": {"expression": {"type": "string", "description": "JS expression to evaluate"}},
                "required": ["expression"],
            },
        ),
        Tool(
            name="browser_wait_for",
            description="Wait for a selector to appear",
            inputSchema={
                "type": "object",
                "properties": {
                    "selector": {"type": "string", "description": "CSS selector to wait for"},
                    "timeout": {"type": "number", "description": "Timeout in ms (default 30000)"},
                },
                "required": ["selector"],
            },
        ),
        Tool(
            name="browser_get_text",
            description="Get the text content of an element",
            inputSchema={
                "type": "object",
                "properties": {"selector": {"type": "string", "description": "CSS selector"}},
                "required": ["selector"],
            },
        ),
        Tool(
            name="browser_get_url",
            description="Get the current page URL",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="browser_set_viewport",
            description="Resize the current page while preserving login and form state. Use width=375 for mobile, 1440 for desktop.",
            inputSchema={
                "type": "object",
                "properties": {
                    "width": {"type": "integer", "description": "Viewport width in px"},
                    "height": {"type": "integer", "description": "Viewport height in px"},
                },
                "required": ["width", "height"],
            },
        ),
        Tool(
            name="browser_errors",
            description="Failed requests and 4xx/5xx responses since the last call, then clear them",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="browser_close",
            description="Close the browser",
            inputSchema={"type": "object", "properties": {}},
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict):
    global _browser, _context, _page, _pw, _viewport

    if name == "browser_navigate":
        page = await get_page()
        await page.goto(arguments["url"], wait_until="domcontentloaded")
        return [TextContent(type="text", text=f"Navigated to {arguments['url']}")]

    elif name == "browser_screenshot":
        page = await get_page()
        full_page = arguments.get("full_page", False)
        path = arguments.get("path")
        if path:
            os.makedirs(os.path.dirname(path), exist_ok=True)
        data = await page.screenshot(full_page=full_page, path=path)
        b64 = base64.b64encode(data).decode()
        return [ImageContent(type="image", data=b64, mimeType="image/png")]

    elif name == "browser_click":
        page = await get_page()
        sel = arguments["selector"]
        await page.click(sel)
        return [TextContent(type="text", text=f"Clicked {sel}")]

    elif name == "browser_type":
        page = await get_page()
        await page.fill(arguments["selector"], arguments["text"])
        return [TextContent(type="text", text=f"Typed into {arguments['selector']}")]

    elif name == "browser_snapshot":
        page = await get_page()
        snapshot = await page.locator("body").aria_snapshot()
        return [TextContent(type="text", text=snapshot)]

    elif name == "browser_evaluate":
        page = await get_page()
        result = await page.evaluate(arguments["expression"])
        return [TextContent(type="text", text=str(result))]

    elif name == "browser_wait_for":
        page = await get_page()
        timeout = arguments.get("timeout", 30000)
        await page.wait_for_selector(arguments["selector"], timeout=timeout)
        return [TextContent(type="text", text=f"Selector {arguments['selector']} found")]

    elif name == "browser_get_text":
        page = await get_page()
        text = await page.text_content(arguments["selector"])
        return [TextContent(type="text", text=text or "")]

    elif name == "browser_get_url":
        page = await get_page()
        return [TextContent(type="text", text=page.url)]

    elif name == "browser_set_viewport":
        w, h = arguments["width"], arguments["height"]
        _viewport = {"width": w, "height": h}
        page = await get_page()
        await page.set_viewport_size(_viewport)
        return [TextContent(type="text", text=f"Viewport set to {w}x{h}")]

    elif name == "browser_errors":
        found = _issues[:]
        _issues.clear()
        return [TextContent(type="text", text="\n".join(found) or "no failed requests")]

    elif name == "browser_close":
        if _browser:
            await _browser.close()
            _browser = _context = _page = None
        if _pw:
            await _pw.stop()
            _pw = None
        return [TextContent(type="text", text="Browser closed")]

    return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def main():
    async with stdio_server() as streams:
        await server.run(streams[0], streams[1], server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
