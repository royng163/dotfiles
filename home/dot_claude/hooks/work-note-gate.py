#!/usr/bin/env python3
"""Block the turn from ending while the work note is older than the code.

Every source file the session or its subagents wrote, read from the transcript, must be older
than the work note naming that file's branch. An agent-team teammate never edits the note, so
its writes are handed to the lead's session, and the lead is checked when it next stops.

No-ops unless the workspace has a `.notes/work/` folder, so it stays silent in
projects that do not keep work notes.
"""
import json
import subprocess
import sys
import time
from pathlib import Path

SOURCE_SUFFIXES = {
    '.py', '.js', '.mjs', '.cjs', '.ts', '.tsx', '.jsx', '.vue', '.go', '.rs',
    '.java', '.kt', '.rb', '.php', '.c', '.h', '.cpp', '.hpp', '.cs', '.swift',
    '.sql',
}
WRITE_TOOLS = {'Write', 'Edit', 'MultiEdit', 'NotebookEdit'}
CLAUDE_HOME = Path.home() / '.claude'
TEAMS_DIR = CLAUDE_HOME / 'teams'
LOG_DIR = CLAUDE_HOME / 'hooks' / 'state'
PRUNE_AFTER = 7 * 24 * 60 * 60
# The gate yields after this many blocks in one session. A blocking hook that
# cannot be satisfied would otherwise stall the turn until the harness cap.
MAX_BLOCKS = 2


def work_dir(start):
    """The workspace-root .notes/work directory, or None."""
    for parent in [start, *start.parents]:
        candidate = parent / '.notes' / 'work'
        if candidate.is_dir():
            return candidate
    return None


def read_transcript(transcript):
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
                if '"file_path"' not in line and '"notebook_path"' not in line:
                    continue
                try:
                    content = (json.loads(line).get('message') or {}).get('content')
                except ValueError:
                    continue
                for item in content if isinstance(content, list) else []:
                    if isinstance(item, dict) and item.get('name') in WRITE_TOOLS:
                        tool_input = item.get('input') or {}
                        written.append(tool_input.get('file_path') or tool_input.get('notebook_path'))
    return [name for name in written if is_source(name)], team


def is_source(name):
    if not name:
        return False
    path = Path(name)
    # Agent config and hook scripts are tooling, not the project's source.
    return path.suffix.lower() in SOURCE_SUFFIXES and CLAUDE_HOME not in path.parents


def lead_session(team):
    try:
        return json.loads((TEAMS_DIR / team / 'config.json').read_text()).get('leadSessionId')
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


def prune():
    cutoff = time.time() - PRUNE_AFTER
    try:
        for path in LOG_DIR.glob('*'):
            if path.is_file() and path.stat().st_mtime < cutoff:
                path.unlink()
    except OSError:
        pass


def main():
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        payload = {}

    prune()

    session = payload.get('session_id')
    transcript = payload.get('transcript_path')
    if not session or not transcript:
        return 0

    written, team = read_transcript(Path(transcript))
    handoff = LOG_DIR / f'{session}.handoff'
    try:
        written += handoff.read_text().split('\n')
    except OSError:
        pass
    written = existing(name.strip() for name in written if name.strip())
    if not written:
        return 0

    cwd = Path(payload.get('cwd') or Path.cwd())
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
        lead = lead_session(team)
        if stale and lead:
            try:
                LOG_DIR.mkdir(parents=True, exist_ok=True)
                with (LOG_DIR / f'{lead}.handoff').open('a') as log:
                    log.write(''.join(f'{name}\n' for name in stale))
            except OSError:
                pass
        return 0

    if not stale:
        (LOG_DIR / f'{session}.blocks').unlink(missing_ok=True)
        handoff.unlink(missing_ok=True)
        return 0

    # An explicit opt-out the gate can verify, rather than a claim it cannot see.
    if (LOG_DIR / f'{session}.skip').exists():
        return 0

    blocks_file = LOG_DIR / f'{session}.blocks'
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
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        blocks_file.write_text(str(blocks + 1))
    except OSError:
        pass

    shown = ', '.join(Path(name).name for name in stale[:5])
    if len(stale) > 5:
        shown += f', +{len(stale) - 5} more'
    source = 'This session or its teammates wrote' if handoff.exists() else 'This session wrote'

    print(json.dumps({
        'decision': 'block',
        'reason': (
            f'{source} {len(stale)} source file(s) after the work note for their branch was '
            f'last updated ({shown}). The note records what the code ended up doing, so update '
            f'it under {folder} after the code, not before: write in the section of any teammate '
            'that has returned, or update the Status line of one still working. See the '
            'work-note skill for the format. If this change genuinely '
            f'needs no note, run `touch {LOG_DIR}/{session}.skip` and then stop.'
        ),
        'systemMessage': f'Work-note gate: {len(stale)} file(s) written after the note.',
    }))
    return 0


if __name__ == '__main__':
    sys.exit(main())
