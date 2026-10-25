#!/usr/bin/env python3
"""Block the turn from ending while the work note is older than the code.

Every source file the session or its subagents wrote, read from the transcript, must be older
than the work note naming that file's branch. An agent-team teammate never edits the note, so
its writes are handed to the lead's session, and the lead is checked when it next stops.

The notes folder lives at the monorepo root when the repo is a monorepo, otherwise at the
parent of the repo so sibling repos share it. `--where` prints that path.

Runs as a Stop hook for Claude Code and CodeBuddy Code, which pass a transcript, and as a
plugin adapter in OpenCode, which passes the paths the session wrote. Each tool blocks
differently, so the caller is detected from `tool` in the payload or the transcript path.

No-ops unless a resolved or legacy `.notes/work/` folder exists, so it stays silent in
projects that do not keep work notes.
"""
import json
import subprocess
import sys
import time
from functools import lru_cache
from pathlib import Path

SOURCE_SUFFIXES = {
    '.py', '.js', '.mjs', '.cjs', '.ts', '.tsx', '.jsx', '.vue', '.go', '.rs',
    '.java', '.kt', '.rb', '.php', '.c', '.h', '.cpp', '.hpp', '.cs', '.swift',
    '.sql',
}
WRITE_TOOLS = {'Write', 'Edit', 'MultiEdit', 'NotebookEdit'}
CLAUDE_HOME = Path.home() / '.claude'
CODEBUDDY_HOME = Path.home() / '.codebuddy'
AGENTS_HOME = Path.home() / '.agents'
TOOL_HOMES = (CLAUDE_HOME, CODEBUDDY_HOME, AGENTS_HOME)
OPENCODE_STATE = Path.home() / '.local' / 'share' / 'opencode' / 'work-note-gate'
PRUNE_AFTER = 7 * 24 * 60 * 60
# The gate yields after this many blocks in one session. A blocking hook that
# cannot be satisfied would otherwise stall the turn until the harness cap.
MAX_BLOCKS = 2
WORKSPACE_FILES = (
    'pnpm-workspace.yaml', 'lerna.json', 'nx.json', 'turbo.json', 'rush.json', 'go.work',
)
WORKSPACE_DIRS = {'apps', 'packages', 'services'}
BACKEND_DIRS = {'backend', 'server', 'api'}
FRONTEND_DIRS = {'frontend', 'client', 'web', 'mobile', 'admin'}


def resolve_tool(payload):
    """Which agent invoked the gate: an explicit field, else the transcript's home."""
    tool = payload.get('tool')
    if tool in ('claude', 'codebuddy', 'opencode'):
        return tool
    transcript = payload.get('transcript_path')
    if transcript:
        for home in TOOL_HOMES:
            if home in Path(transcript).parents:
                return 'codebuddy' if home == CODEBUDDY_HOME else 'claude'
    return 'claude'


def state_dir(tool):
    """Where block counters, skip markers and handoffs live for one agent."""
    if tool == 'opencode':
        return OPENCODE_STATE
    if tool == 'codebuddy':
        return CODEBUDDY_HOME / 'hooks' / 'state'
    return CLAUDE_HOME / 'hooks' / 'state'


@lru_cache(maxsize=None)
def git_root(start):
    """The repository root containing start, or None."""
    try:
        result = subprocess.run(
            ['git', '-C', str(start), 'rev-parse', '--show-toplevel'],
            capture_output=True, text=True, timeout=5,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0 or not result.stdout.strip():
        return None
    return Path(result.stdout.strip())


def _contains(path, needle):
    try:
        return needle in path.read_text(errors='replace')
    except OSError:
        return False


def _declares_multiple_surfaces(root):
    """A 'Surfaces: Backend, Frontend' line in the project instructions."""
    for name in ('CLAUDE.md', 'AGENTS.md'):
        try:
            text = (root / name).read_text(errors='replace')
        except OSError:
            continue
        for line in text.splitlines():
            if line.strip().lower().startswith('surfaces') and ',' in line:
                return True
    return False


@lru_cache(maxsize=None)
def is_monorepo(root):
    """A repo with a workspace manifest or more than one deployable surface."""
    if any((root / name).is_file() for name in WORKSPACE_FILES):
        return True
    if _declares_multiple_surfaces(root):
        return True
    if _contains(root / 'package.json', '"workspaces"'):
        return True
    if _contains(root / 'Cargo.toml', '[workspace]'):
        return True
    if _contains(root / 'pyproject.toml', '[tool.uv.workspace]'):
        return True
    try:
        dirs = {path.name for path in root.iterdir() if path.is_dir()}
    except OSError:
        return False
    if dirs & WORKSPACE_DIRS:
        return True
    return bool(dirs & BACKEND_DIRS) and bool(dirs & FRONTEND_DIRS)


def resolve_notes_root(start):
    """The canonical .notes/work folder: monorepo root, else the repo's parent."""
    root = git_root(start)
    if root is not None:
        base = root if is_monorepo(root) else root.parent
        return base / '.notes' / 'work'
    for parent in [start, *start.parents]:
        candidate = parent / '.notes' / 'work'
        if candidate.is_dir():
            return candidate
    return start / '.notes' / 'work'


def work_dir(start):
    """The resolved notes folder if it exists, else an existing legacy folder."""
    canonical = resolve_notes_root(start)
    if canonical.is_dir():
        return canonical
    root = git_root(start)
    if root is not None:
        for candidate in (root / '.notes' / 'work', root.parent / '.notes' / 'work'):
            if candidate.is_dir():
                return candidate
    for parent in [start, *start.parents]:
        candidate = parent / '.notes' / 'work'
        if candidate.is_dir():
            return candidate
    return None


def written_paths(line):
    """File paths one transcript line shows as written."""
    if '"trackedFileBackups"' in line:
        # CodeBuddy Code: the file history snapshot lists everything the session wrote.
        try:
            snapshot = (json.loads(line).get('snapshot') or {}).get('trackedFileBackups') or {}
        except ValueError:
            return []
        return list(snapshot)
    if '"file_path"' not in line and '"notebook_path"' not in line:
        return []
    try:
        entry = json.loads(line)
    except ValueError:
        return []
    paths = []
    # Claude Code: tool use blocks inside the assistant message.
    content = (entry.get('message') or {}).get('content')
    for item in content if isinstance(content, list) else []:
        if isinstance(item, dict) and item.get('name') in WRITE_TOOLS:
            tool_input = item.get('input') or {}
            paths.append(tool_input.get('file_path') or tool_input.get('notebook_path'))
    # CodeBuddy Code: a function call carries the tool input as JSON text.
    if entry.get('type') == 'function_call' and entry.get('name') in WRITE_TOOLS:
        arguments = entry.get('arguments')
        if isinstance(arguments, str):
            try:
                arguments = json.loads(arguments)
            except ValueError:
                arguments = {}
        if isinstance(arguments, dict):
            paths.append(arguments.get('file_path') or arguments.get('notebook_path'))
    return [path for path in paths if path]


def read_transcript(transcript, root):
    """(source paths written, team name) from a session transcript and its subagents."""
    files = [transcript, *sorted(transcript.with_suffix('').glob('subagents/*.jsonl'))]
    written, team = [], None
    for index, path in enumerate(files):
        try:
            handle = path.open(errors='replace')
        except OSError:
            continue
        with handle:
            for line in handle:
                if index == 0 and team is None and '"teamName"' in line:
                    try:
                        team = json.loads(line).get('teamName')
                    except ValueError:
                        pass
                written += written_paths(line)
    return [name for name in written if name], team


def is_source(name, root):
    if not name:
        return False
    path = Path(name)
    if path.suffix.lower() not in SOURCE_SUFFIXES:
        return False
    # Agent config and hook scripts are tooling, not the project's source.
    if any(home in path.parents for home in TOOL_HOMES):
        return False
    # Only files in the session's repository belong to its work note.
    return root is None or root in path.parents


def lead_session(teams_dir, team):
    try:
        return json.loads((teams_dir / team / 'config.json').read_text()).get('leadSessionId')
    except (OSError, ValueError):
        return None


def existing(names):
    """(path, mtime) for each distinct path that still exists."""
    found = {}
    for name in names:
        if name in found:
            continue
        try:
            found[name] = Path(name).stat().st_mtime
        except OSError:
            continue
    return found


def branch_of(directory, cache):
    if directory not in cache:
        try:
            result = subprocess.run(['git', '-C', directory, 'symbolic-ref', '--short', 'HEAD'],
                                    capture_output=True, text=True, timeout=5)
            cache[directory] = result.stdout.strip() if result.returncode == 0 else None
        except (OSError, subprocess.TimeoutExpired):
            cache[directory] = None
    return cache[directory]


def note_stamp(branch, notes):
    """Newest mtime among notes naming the branch, else among all notes."""
    naming = [stamp for text, stamp in notes if branch and branch in text]
    stamps = naming or [stamp for _, stamp in notes]
    return max(stamps) if stamps else None


def load_notes(folder):
    notes = []
    for path in folder.rglob('*.md'):
        try:
            notes.append((path.read_text(errors='replace'), path.stat().st_mtime))
        except OSError:
            continue
    return notes


def prune(log_dir):
    cutoff = time.time() - PRUNE_AFTER
    try:
        for path in log_dir.glob('*'):
            if path.is_file() and path.stat().st_mtime < cutoff:
                path.unlink()
    except OSError:
        pass


def block(tool, reason, system_message):
    """Report a block in the shape the calling tool expects."""
    if tool == 'claude':
        print(json.dumps({'decision': 'block', 'reason': reason, 'systemMessage': system_message}))
        return 0
    # CodeBuddy blocks on exit 2; the OpenCode plugin reads `reason` and re-prompts.
    print(json.dumps({'reason': reason, 'systemMessage': system_message}))
    return 2


def main():
    if '--where' in sys.argv[1:]:
        print(resolve_notes_root(Path.cwd()))
        return 0

    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        payload = {}

    session = payload.get('session_id')
    if not session:
        return 0

    tool = resolve_tool(payload)
    log_dir = state_dir(tool)
    teams_dir = CLAUDE_HOME / 'teams'
    prune(log_dir)

    cwd = Path(payload.get('cwd') or Path.cwd())
    root = git_root(cwd)
    # OpenCode has no transcript, so its plugin reports the paths the session wrote.
    explicit = payload.get('written')
    if explicit:
        raw, team = [str(path) for path in explicit], None
    elif payload.get('transcript_path'):
        raw, team = read_transcript(Path(payload['transcript_path']), root)
    else:
        return 0

    handoff = log_dir / f'{session}.handoff'
    try:
        raw += handoff.read_text().split('\n')
    except OSError:
        pass
    written = existing(name for name in (n.strip() for n in raw) if name and is_source(name, root))
    if not written:
        (log_dir / f'{session}.blocks').unlink(missing_ok=True)
        return 0

    folder = work_dir(cwd) or work_dir(Path(next(iter(written))).parent)
    if folder is None:
        return 0

    notes = load_notes(folder)
    branches, stale = {}, []
    for name, stamp in sorted(written.items()):
        note = note_stamp(branch_of(str(Path(name).parent), branches), notes)
        if note is None or stamp > note:
            stale.append(name)

    if team:
        lead = lead_session(teams_dir, team)
        if stale and lead:
            try:
                log_dir.mkdir(parents=True, exist_ok=True)
                with (log_dir / f'{lead}.handoff').open('a') as log:
                    log.write(''.join(f'{name}\n' for name in stale))
            except OSError:
                pass
        return 0

    if not stale:
        (log_dir / f'{session}.blocks').unlink(missing_ok=True)
        handoff.unlink(missing_ok=True)
        return 0

    # An explicit opt-out the gate can verify, rather than a claim it cannot see.
    if (log_dir / f'{session}.skip').exists():
        return 0

    blocks_file = log_dir / f'{session}.blocks'
    try:
        blocks = int(blocks_file.read_text().strip())
    except (OSError, ValueError):
        blocks = 0
    if blocks >= MAX_BLOCKS:
        print(json.dumps({'systemMessage':
            f'Work-note gate: yielding after {blocks} blocks; '
            f'{len(stale)} file(s) still newer than the note.'}))
        return 0
    try:
        log_dir.mkdir(parents=True, exist_ok=True)
        blocks_file.write_text(str(blocks + 1))
    except OSError:
        pass

    shown = ', '.join(Path(name).name for name in stale[:5])
    if len(stale) > 5:
        shown += f', +{len(stale) - 5} more'
    source = 'This session or its teammates wrote' if handoff.exists() else 'This session wrote'

    reason = (
        f'{source} {len(stale)} source file(s) after the work note for their branch was '
        f'last updated ({shown}). The note records what the code ended up doing, so update '
        f'it under {folder} after the code, not before: write in the section of any teammate '
        'that has returned, or update the Status line of one still working. See the '
        'work-note skill for the format. If this change genuinely '
        f'needs no note, run `touch {log_dir}/{session}.skip` and then stop.'
    )
    return block(tool, reason, f'Work-note gate: {len(stale)} file(s) written after the note.')


if __name__ == '__main__':
    sys.exit(main())
