import { Plugin } from "@opencode/plugin"
import { execFileSync } from "node:child_process"
import { homedir } from "node:os"
import { isAbsolute, resolve } from "node:path"

// The gate rules live in the shared script; this plugin only reports what the session wrote.
const GATE = `${homedir()}/.agents/hooks/work-note-gate.py`

const writes = new Map<string, Set<string>>()
const pending = new Map<string, string[]>()
const idleAt = new Map<string, number>()
const running = new Set<string>()

function propsOf(event: any): any {
  return event?.properties ?? event?.data ?? {}
}

function toolPaths(input: any, directory: string): string[] {
  if (!input) return []
  const raw: string[] = []
  if (typeof input.patchText === "string") {
    for (const line of input.patchText.split("\n")) {
      const match = /^\*\*\* (?:Add File|Update File|Move to): (.+)$/.exec(line.trim())
      if (match) raw.push(match[1].trim())
    }
  } else if (
    typeof input.path === "string" &&
    ("oldString" in input || "newString" in input || "content" in input)
  ) {
    raw.push(input.path)
  } else if (typeof input.filePath === "string" && "content" in input) {
    raw.push(input.filePath)
  }
  return raw.map((path) => (isAbsolute(path) ? path : resolve(directory, path)))
}

function runGate(payload: unknown): string | null {
  try {
    execFileSync("python3", [GATE], { input: JSON.stringify(payload), encoding: "utf8", timeout: 20000 })
    return null
  } catch (error: any) {
    if (error?.status !== 2) {
      console.error("[work-note-gate] gate failed", error?.stderr ?? error)
      return null
    }
    try {
      return JSON.parse(String(error.stdout ?? "")).reason ?? null
    } catch {
      return String(error.stdout ?? "").trim() || null
    }
  }
}

async function check(ctx: any, sessionID: string, sourceID: string = sessionID): Promise<void> {
  const written = writes.get(sourceID)
  if (!written || written.size === 0) return

  const session = await ctx.session.get({ sessionID }).catch(() => undefined)
  if (!session) return
  const cwd = session.location?.directory ?? session.directory

  const reason = runGate({ tool: "opencode", session_id: sessionID, cwd, written: [...written] })
  if (!reason) return

  writes.delete(sourceID)
  try {
    await ctx.session.prompt({ sessionID, text: reason, delivery: "steer" })
  } catch (error) {
    console.error("[work-note-gate] prompt failed", error)
  }
}

function mergeIntoParent(ctx: any, sessionID: string, parentID: string): void {
  const child = writes.get(sessionID)
  if (!child) return
  let parent = writes.get(parentID)
  if (!parent) {
    parent = new Set()
    writes.set(parentID, parent)
  }
  for (const path of child) parent.add(path)
  writes.delete(sessionID)
  if (!running.has(parentID)) setTimeout(() => void check(ctx, parentID), 1000)
}

async function handleIdle(ctx: any, sessionID: string): Promise<void> {
  const now = Date.now()
  if (now - (idleAt.get(sessionID) ?? 0) < 1500) return
  idleAt.set(sessionID, now)
  for (const key of pending.keys()) {
    if (key.startsWith(`${sessionID}:`)) pending.delete(key)
  }

  const session = await ctx.session.get({ sessionID }).catch(() => undefined)
  if (!session) return
  const directory = session.location?.directory ?? session.directory
  if (directory !== ctx.location.directory) return

  if (session.parentID) {
    const parent = await ctx.session.get({ sessionID: session.parentID }).catch(() => undefined)
    const parentDirectory = parent?.location?.directory ?? parent?.directory
    if (parent && parentDirectory === directory) {
      mergeIntoParent(ctx, sessionID, session.parentID)
    } else if (parent) {
      await check(ctx, session.parentID, sessionID)
    }
    return
  }

  await check(ctx, sessionID)
}

export default Plugin.define({
  id: "work-note-gate",
  async setup(ctx) {
    const controller = new AbortController()

    void (async () => {
      for await (const event of ctx.event.subscribe({ signal: controller.signal })) {
        const type = (event as any).type
        const props = propsOf(event)
        const sessionID = props.sessionID
        if (!sessionID) continue

        if (type === "session.execution.started") {
          running.add(sessionID)
          continue
        }

        if (type === "session.execution.failed" || type === "session.execution.interrupted") {
          running.delete(sessionID)
          continue
        }

        if (type === "session.execution.succeeded" || type === "session.idle") {
          running.delete(sessionID)
          await handleIdle(ctx, sessionID)
          continue
        }

        if (type === "session.tool.called") {
          const directory = (event as any).location?.directory
          if (!directory || directory !== ctx.location.directory || !props.input) continue
          const paths = toolPaths(props.input, directory)
          if (!paths.length || !props.id) continue
          pending.set(`${sessionID}:${props.id}`, paths)
          continue
        }

        if (type === "session.tool.success") {
          const key = `${sessionID}:${props.id}`
          const call = pending.get(key)
          if (!call) continue
          pending.delete(key)
          let set = writes.get(sessionID)
          if (!set) {
            set = new Set()
            writes.set(sessionID, set)
          }
          for (const path of call) set.add(path)
          continue
        }

        if (type === "session.tool.failed") {
          if (props.id) pending.delete(`${sessionID}:${props.id}`)
          continue
        }
      }
    })().catch((error) => console.error("[work-note-gate] event stream failed", error))

    return () => controller.abort()
  },
})
