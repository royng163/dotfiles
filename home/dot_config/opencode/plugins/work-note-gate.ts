import { Plugin } from "@opencode/plugin"
import { execFileSync } from "node:child_process"
import {
  existsSync,
  mkdirSync,
  readdirSync,
  readFileSync,
  statSync,
  unlinkSync,
  writeFileSync,
} from "node:fs"
import { homedir } from "node:os"
import { basename, dirname, extname, isAbsolute, join, resolve } from "node:path"

const SOURCE_SUFFIXES = new Set([
  ".py", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx", ".vue", ".go", ".rs",
  ".java", ".kt", ".rb", ".php", ".c", ".h", ".cpp", ".hpp", ".cs", ".swift",
  ".sql",
])
const STATE_DIR = join(homedir(), ".local", "share", "opencode", "work-note-gate")
const EXCLUDED_DIRS = [
  join(homedir(), ".claude"),
  join(homedir(), ".config", "opencode"),
  join(homedir(), ".local", "share", "opencode"),
]
const MAX_BLOCKS = 2
const PRUNE_MS = 7 * 24 * 60 * 60 * 1000

const writes = new Map<string, Set<string>>()
const pending = new Map<string, { sessionID: string; paths: string[] }>()
const branchCache = new Map<string, string | null>()
const checking = new Set<string>()
const running = new Set<string>()
const idleAt = new Map<string, number>()
const promptedAt = new Map<string, number>()

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

function isSource(path: string): boolean {
  if (!SOURCE_SUFFIXES.has(extname(path).toLowerCase())) return false
  const normalized = resolve(path)
  return !EXCLUDED_DIRS.some(
    (dir) => normalized === dir || normalized.startsWith(dir + "/"),
  )
}

function workDir(start: string): string | null {
  let dir = resolve(start)
  for (;;) {
    const candidate = join(dir, ".notes", "work")
    try {
      if (statSync(candidate).isDirectory()) return candidate
    } catch {}
    const parent = dirname(dir)
    if (parent === dir) return null
    dir = parent
  }
}

function loadNotes(folder: string): Array<{ text: string; mtime: number }> {
  const notes: Array<{ text: string; mtime: number }> = []
  const walk = (dir: string) => {
    let entries
    try {
      entries = readdirSync(dir, { withFileTypes: true })
    } catch {
      return
    }
    for (const entry of entries) {
      if (entry.name.startsWith(".")) continue
      const path = join(dir, entry.name)
      if (entry.isDirectory()) {
        walk(path)
      } else if (entry.isFile() && entry.name.endsWith(".md")) {
        try {
          notes.push({ text: readFileSync(path, "utf8"), mtime: statSync(path).mtimeMs })
        } catch {}
      }
    }
  }
  walk(folder)
  return notes
}

function branchOf(directory: string): string | null {
  if (branchCache.has(directory)) return branchCache.get(directory) ?? null
  let branch: string | null = null
  try {
    branch =
      execFileSync("git", ["-C", directory, "symbolic-ref", "--short", "HEAD"], {
        encoding: "utf8",
        timeout: 5000,
        stdio: ["ignore", "pipe", "ignore"],
      }).trim() || null
  } catch {}
  branchCache.set(directory, branch)
  return branch
}

function noteStamp(
  branch: string | null,
  notes: Array<{ text: string; mtime: number }>,
): number | null {
  const naming = branch ? notes.filter((note) => note.text.includes(branch)) : []
  const stamps = (naming.length ? naming : notes).map((note) => note.mtime)
  return stamps.length ? Math.max(...stamps) : null
}

function stateFile(sessionID: string, extension: string): string {
  return join(STATE_DIR, `${sessionID}.${extension}`)
}

function blockCount(sessionID: string): number {
  try {
    return Number.parseInt(readFileSync(stateFile(sessionID, "blocks"), "utf8").trim(), 10) || 0
  } catch {
    return 0
  }
}

function prune(): void {
  const cutoff = Date.now() - PRUNE_MS
  let entries
  try {
    entries = readdirSync(STATE_DIR)
  } catch {
    return
  }
  for (const name of entries) {
    const path = join(STATE_DIR, name)
    try {
      if (statSync(path).mtimeMs < cutoff) unlinkSync(path)
    } catch {}
  }
}

async function check(
  ctx: any,
  promptSessionID: string,
  sourceSessionID: string = promptSessionID,
): Promise<void> {
  if (checking.has(promptSessionID)) return
  checking.add(promptSessionID)
  try {
    const written = writes.get(sourceSessionID)
    if (!written || written.size === 0) return

    prune()
    const session = await ctx.session.get({ sessionID: promptSessionID }).catch(() => undefined)
    if (!session) return

    const folder =
      workDir(session.location?.directory ?? session.directory) ??
      workDir(dirname([...written][0]))
    if (!folder) return

    const notes = loadNotes(folder)
    const stale: string[] = []
    for (const path of written) {
      let stat
      try {
        stat = statSync(path)
      } catch {
        continue
      }
      if (!stat.isFile() || !isSource(path)) continue
      const stamp = noteStamp(branchOf(dirname(path)), notes)
      if (stamp === null || stat.mtimeMs > stamp) stale.push(path)
    }
    stale.sort()

    if (stale.length === 0) {
      try {
        unlinkSync(stateFile(promptSessionID, "blocks"))
      } catch {}
      writes.delete(sourceSessionID)
      return
    }

    const skip = stateFile(promptSessionID, "skip")
    if (existsSync(skip)) {
      writes.delete(sourceSessionID)
      return
    }

    const blocks = blockCount(promptSessionID)
    if (blocks >= MAX_BLOCKS) return

    if (Date.now() - (promptedAt.get(promptSessionID) ?? 0) < 3000) return
    promptedAt.set(promptSessionID, Date.now())

    mkdirSync(STATE_DIR, { recursive: true })
    writeFileSync(stateFile(promptSessionID, "blocks"), String(blocks + 1))

    const shown =
      stale.slice(0, 5).map((path) => basename(path)).join(", ") +
      (stale.length > 5 ? `, +${stale.length - 5} more` : "")
    const text = [
      `Work-note gate: this session or its subagents wrote ${stale.length} source file(s) after the work note for their branch was last updated (${shown}).`,
      `The note records what the code ended up doing, so update it under ${folder} now, after the code rather than before.`,
      `Write the section of any teammate that has returned, or update the Status line of one still working.`,
      `See the work-note skill for the format. If this change genuinely needs no note, run \`touch ${skip}\` and stop.`,
    ].join(" ")

    try {
      await ctx.session.prompt({ sessionID: promptSessionID, text, delivery: "steer" })
    } catch (error) {
      console.error("[work-note-gate] prompt failed", error)
    }
  } catch (error) {
    console.error("[work-note-gate] check failed", error)
  } finally {
    checking.delete(promptSessionID)
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
    mkdirSync(STATE_DIR, { recursive: true })
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

        if (
          type === "session.execution.failed" ||
          type === "session.execution.interrupted"
        ) {
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
          const paths = toolPaths(props.input, directory).filter(isSource)
          if (!paths.length || !props.id) continue
          pending.set(`${sessionID}:${props.id}`, { sessionID, paths })
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
          for (const path of call.paths) set.add(path)
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
