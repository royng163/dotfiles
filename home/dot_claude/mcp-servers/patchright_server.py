#!/usr/bin/env python3
"""Patchright MCP server — drop-in replacement for @playwright/mcp."""

import asyncio
import base64
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, ImageContent

server = Server("patchright")

_browser = None
_context = None
_page = None
_pw = None
_viewport = {"width": 1280, "height": 720}


async def get_page():
    global _browser, _context, _page, _pw
    if _page is None:
        from patchright.async_api import async_playwright
        _pw = await async_playwright().start()
        _browser = await _pw.chromium.launch(headless=True)
        _context = await _browser.new_context(viewport=_viewport)
        _page = await _context.new_page()
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
                    "full_page": {"type": "boolean", "description": "Capture full scrollable page (default false)"}
                },
            },
        ),
        Tool(
            name="browser_click",
            description="Click an element by CSS selector or text",
            inputSchema={
                "type": "object",
                "properties": {
                    "selector": {"type": "string", "description": "CSS selector or text to click"}
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
            description="Get the accessibility tree snapshot of the current page",
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
            description="Set browser viewport size (recreates page context). Use width=375 for mobile, 1440 for desktop.",
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
            name="browser_close",
            description="Close the browser",
            inputSchema={"type": "object", "properties": {}},
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict):
    global _browser, _context, _page

    if name == "browser_navigate":
        page = await get_page()
        await page.goto(arguments["url"], wait_until="domcontentloaded")
        return [TextContent(type="text", text=f"Navigated to {arguments['url']}")]

    elif name == "browser_screenshot":
        page = await get_page()
        full_page = arguments.get("full_page", False)
        data = await page.screenshot(full_page=full_page)
        b64 = base64.b64encode(data).decode()
        return [ImageContent(type="image", data=b64, mimeType="image/png")]

    elif name == "browser_click":
        page = await get_page()
        sel = arguments["selector"]
        try:
            await page.click(sel)
        except Exception:
            await page.get_by_text(sel).first.click()
        return [TextContent(type="text", text=f"Clicked {sel}")]

    elif name == "browser_type":
        page = await get_page()
        await page.fill(arguments["selector"], arguments["text"])
        return [TextContent(type="text", text=f"Typed into {arguments['selector']}")]

    elif name == "browser_snapshot":
        page = await get_page()
        snapshot = await page.accessibility.snapshot()
        import json
        return [TextContent(type="text", text=json.dumps(snapshot, indent=2))]

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
        global _browser, _context, _page, _viewport
        w, h = arguments["width"], arguments["height"]
        _viewport = {"width": w, "height": h}
        current_url = _page.url if _page else None
        if _context:
            await _context.close()
        _context = await _browser.new_context(viewport=_viewport)
        _page = await _context.new_page()
        if current_url and current_url != "about:blank":
            await _page.goto(current_url, wait_until="domcontentloaded")
        return [TextContent(type="text", text=f"Viewport set to {w}x{h}")]

    elif name == "browser_close":
        if _browser:
            await _browser.close()
            _browser = _context = _page = None
        return [TextContent(type="text", text="Browser closed")]

    return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def main():
    async with stdio_server() as streams:
        await server.run(streams[0], streams[1], server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
