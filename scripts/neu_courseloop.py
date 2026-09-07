#!/usr/bin/env python3
"""Resumable course film supervisor. Standard library; macOS/Linux flock locks."""
import argparse
import collections
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import time


def save(path, data):
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(data, indent=2) + '\n')
    tmp.replace(path)


def headings(text):
    """Markdown headings outside fenced code (including Python # comments)."""
    result, fence = [], None
    for i, line in enumerate(text.splitlines()):
        mark = re.match(r'^\s*(`{3,}|~{3,})', line)
        if mark:
            token = mark[1]
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence):
                fence = None
            continue
        m = re.match(r'^(#{1,6})\s+(.+)', line)
        if fence is None and m:
            result.append((i, len(m[1]), m[2].strip()))
    return result


def inventory(root):
    course = json.loads((root / 'course.json').read_text())
    config = json.loads((root / 'neu-courseloop.json').read_text())
    prompt = (root / 'NEU-COURSELOOP-PROMPT.md').read_text()
    jobs = []

    def add(kind, path, focus='', excerpt=''):
        p = root / path
        if not p.resolve().is_relative_to(root.resolve()) or not p.is_file():
            raise ValueError(f'Invalid local source: {path}')
        identity = kind + ':' + path + ':' + focus
        slug = re.sub(r'[^a-z0-9]+', '-', (Path(path).stem + '-' + focus).lower()).strip('-')[:75]
        key = kind + '-' + slug + '-' + hashlib.sha256(identity.encode()).hexdigest()[:8]
        digest = hashlib.sha256((p.read_text() + prompt + json.dumps(course, sort_keys=True)
                                 + identity + excerpt).encode()).hexdigest()
        jobs.append(dict(id=key, kind=kind, source=path, focus=focus, excerpt=excerpt,
                         source_hash=digest, skill={'chapter':'deep-explainer',
                         'assignment':'ai-explainer', 'exercise':'cli-explainer'}[kind],
                         output=f'youtube/claude-liam-neu-{key}-v-{digest[:12]}'))

    if config.get('book_file'):
        path = config['book_file']
        content = (root / path).read_text()
        lines = content.splitlines()
        hs = [h for h in headings(content) if h[1] == 1]
        for n, (start, _, title) in enumerate(hs):
            end = hs[n+1][0] if n+1 < len(hs) else len(lines)
            add('chapter', path, title, '\n'.join(lines[start:end]))
    else:
        for p in sorted((root / 'chapters').glob('[0-9]*.md')):
            if p.name not in config.get('exclude_chapters', []):
                add('chapter', str(p.relative_to(root)))
    assignments = sorted((root / config['assignments_dir']).glob('assignment-*.md'))
    if len(assignments) != 10:
        raise ValueError(f'Expected 10 current Assignment briefs, got {len(assignments)}')
    for p in assignments:
        add('assignment', str(p.relative_to(root)))
    lessons = course.get('lessons', course.get('weeks', []))
    for lesson in lessons:
        p = root / lesson['path']
        if p.is_dir():
            p = p / 'docs/en.md'
        content = p.read_text()
        lines, hs = content.splitlines(), headings(content)
        sections = [h for h in hs if h[2].startswith('Assessments')]
        if len(sections) != 1:
            raise ValueError(f'Expected one Assessment section: {p}')
        start, level, _ = sections[0]
        end = next((h[0] for h in hs if h[0] > start and h[1] <= level), len(lines))
        section = '\n'.join(lines[start+1:end])
        items = re.findall(r'^\d+\.\s+(.+)$', section, re.M)
        if not items:
            raise ValueError(f'No numbered Assessments: {p}')
        for n, item in enumerate(items, 1):
            add('exercise', str(p.relative_to(root)), f'lesson-{lesson.get("lesson", lesson.get("week"))}-assessment-{n}', item)
    # Round-robin formats: don't make all exercises wait for the entire book.
    groups = {k: [j for j in jobs if j['kind'] == k] for k in ('chapter','assignment','exercise')}
    result = []
    while any(groups.values()):
        for group in groups.values():
            if group:
                result.append(group.pop(0))
    return result


def verify(root, job):
    out = root / job['output']
    receipt = json.loads((out / 'RESULT.json').read_text())
    if any(receipt.get(k) != v for k, v in {'status':'review-ready',
             'source_hash':job['source_hash'], 'voice':'am_onyx', 'cut':'review.mp4'}.items()):
        raise ValueError('Invalid or stale receipt')
    for name in ('beat_sheet.json', 'FACTCHECK.md', 'BUILD-PROMPT.md', 'BUILD-LOG.md',
                 'SOURCES.md', 'CHECKS-REPORT.md', 'TYPECHECK.md', '_qc/REPORT.md'):
        if not (out / name).is_file() or not (out / name).stat().st_size:
            raise ValueError(f'Missing {name}')
    if job['kind'] == 'chapter' and not (out / 'SHOPPING.md').is_file():
        raise ValueError('Missing SHOPPING.md')
    if not re.search(r'Overall:\s*PASS', (out / 'TYPECHECK.md').read_text()):
        raise ValueError('GATE T does not report Overall: PASS')
    sheet = json.loads((out / 'beat_sheet.json').read_text())
    if not sheet.get('beats'):
        raise ValueError('Empty beat sheet')
    meta = sheet.get('metadata', {})
    for block in [meta, sheet] + sheet['beats']:
        if block.get('voice', 'am_onyx') != 'am_onyx' or block.get('engine', 'kokoro') != 'kokoro':
            raise ValueError('Beat-sheet voice is not local Liam/Kokoro')
    cut = out / 'review.mp4'
    if cut.stat().st_mtime < (out / 'beat_sheet.json').stat().st_mtime:
        raise ValueError('Stale MP4')
    probe = json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams',
            '-show_format','-of','json',str(cut)], timeout=60))
    kinds = {s['codec_type'] for s in probe['streams']}
    if not {'audio','video'} <= kinds or float(probe['format']['duration']) < 10:
        raise ValueError('Missing audio/video or implausibly short cut')
    sound = subprocess.run(['ffmpeg','-nostdin','-i',str(cut),'-af','volumedetect',
            '-f','null','-'], capture_output=True, text=True, timeout=600)
    volume = re.findall(r'mean_volume: ([-\d.]+) dB', sound.stderr)
    if sound.returncode or not volume or float(volume[-1]) <= -40:
        raise ValueError('Silent/inaudible review cut')
    return str(cut)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--dry', action='store_true', help='read-only full inventory')
    mode.add_argument('--status', action='store_true')
    mode.add_argument('--once', action='store_true')
    parser.add_argument('--retry-failed', action='store_true')
    args = parser.parse_args()
    root = args.root.resolve()
    state = root / '.neu-courseloop'
    if args.dry:
        jobs = inventory(root)
        print(json.dumps({'counts':dict(collections.Counter(j['kind'] for j in jobs)), 'jobs':jobs}, indent=2))
        return
    if args.status:
        print((state / 'status.json').read_text() if (state / 'status.json').exists() else 'Not started')
        return
    for command in ('claude','ffprobe','ffmpeg'):
        if not shutil.which(command):
            raise SystemExit(f'Missing dependency: {command}')
    toolkit = Path(os.environ.get('BRUTALIST_ART', str(root.parent / 'brutalist-art'))).resolve()
    if not (toolkit / 'art').is_file():
        raise SystemExit('Missing Brutalist toolkit; set BRUTALIST_ART')
    state.mkdir(exist_ok=True)
    lock = (state / 'worker.lock').open('a')
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        raise SystemExit('This course already has a worker')
    # Common to all six courses; advisory locks release on exit, never delete locks.
    shared_dir = Path(os.environ.get('NEU_SHARED_STATE', str(root.parent / '.neu-courseloop')))
    shared_dir.mkdir(exist_ok=True)
    shared = (shared_dir / 'render.lock').open('a')
    cooldown_path = shared_dir / 'cooldown.json'
    records_path = state / 'records.json'
    records = json.loads(records_path.read_text()) if records_path.exists() else {}
    if args.retry_failed:
        records = {k:v for k,v in records.items() if v.get('status') == 'review-ready'}
    child = None

    def stop(signum, frame):
        if child is not None and child.poll() is None:
            os.killpg(child.pid, signal.SIGTERM)
        raise SystemExit(0)

    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)

    def status(message, jobs, active=None):
        counts = collections.Counter(records.get(j['source_hash'], {}).get('status','pending') for j in jobs)
        data = {'pid':os.getpid(), 'updated':time.strftime('%Y-%m-%d %H:%M:%S'),
                'message':message, 'counts':dict(counts), 'active':active}
        save(state / 'status.json', data)
        print(json.dumps(data), flush=True)

    while True:
        jobs = inventory(root)
        now = time.time()
        eligible = [j for j in jobs if records.get(j['source_hash'],{}).get('status') != 'review-ready'
                    and records.get(j['source_hash'],{}).get('attempts',0) < 2
                    and records.get(j['source_hash'],{}).get('retry_at',0) <= now]
        if not eligible:
            status('Queue drained or waiting; rescanning in 30 minutes', jobs)
            if args.once: return
            time.sleep(1800)
            continue
        if cooldown_path.exists() and json.loads(cooldown_path.read_text()).get('until',0) > now:
            status('Shared account/system cooldown; no job launched', jobs)
            if args.once: return
            time.sleep(60)
            continue
        if shutil.disk_usage(root).free < int(os.environ.get('NEU_MIN_FREE_GB','20')) * 1024**3:
            status('Paused: less than minimum free disk space', jobs)
            if args.once: return
            time.sleep(600)
            continue
        try:
            fcntl.flock(shared, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            status('Waiting for shared render slot', jobs)
            time.sleep(30)
            continue
        job = eligible[0]
        out = root / job['output']
        out.mkdir(parents=True, exist_ok=True)
        record = records.setdefault(job['source_hash'], {'attempts':0})
        record.update(status='building', id=job['id'], output=job['output'])
        save(records_path, records)
        status('Building local review video', jobs, job['id'])
        prompt = (root / 'NEU-COURSELOOP-PROMPT.md').read_text()
        prompt += '\nBRUTALIST_ART: ' + str(toolkit) + '\nOUTPUT: ' + str(out) + '\nJOB:\n' + json.dumps(job)
        env = dict(os.environ)
        # Subscription-only: do not silently switch unattended production to API billing.
        for key in list(env):
            if key.startswith(('ANTHROPIC_', 'CLAUDE_CODE_USE_', 'ELEVENLABS_', 'HIGGSFIELD_')):
                env.pop(key)
        cmd = ['claude','-p',prompt,'--permission-mode','acceptEdits',
               '--allowedTools','Read,Glob,Grep,Edit,Write,Bash',
               '--strict-mcp-config','--mcp-config','{"mcpServers":{}}',
               '--tools','Read,Glob,Grep,Edit,Write,Bash', '--output-format','json']
        try:
            log = state / (job['id'] + '.log')
            with log.open('a') as stream:
                child = subprocess.Popen(cmd, cwd=root, env=env, stdin=subprocess.DEVNULL,
                                         stdout=stream, stderr=subprocess.STDOUT, start_new_session=True)
                try:
                    rc = child.wait(timeout=int(os.environ.get('NEU_JOB_TIMEOUT','5400')))
                except subprocess.TimeoutExpired:
                    os.killpg(child.pid, signal.SIGTERM)
                    try: child.wait(timeout=30)
                    except subprocess.TimeoutExpired:
                        os.killpg(child.pid, signal.SIGKILL)
                        child.wait()
                    raise ValueError('Job exceeded wall-clock timeout')
            tail = log.read_text(errors='replace')[-6000:]
            if re.search(r'hit your.*limit|rate.limit|not logged in|authentication.*fail', tail, re.I):
                record.update(status='paused', retry_at=time.time()+1800, note='Account limit/authentication; see job log')
                save(cooldown_path, {'until':time.time()+1800, 'reason':'Account limit/authentication'})
            elif rc:
                raise ValueError(f'Claude exited {rc}; see {log}')
            else:
                record.update(status='review-ready', cut=verify(root,job), retry_at=0)
        except (ValueError, OSError, KeyError, subprocess.SubprocessError) as exc:
            record.update(status='failed', attempts=record['attempts']+1,
                          retry_at=time.time()+1800, note=str(exc))
            save(cooldown_path, {'until':time.time()+1800, 'reason':'Build failure; review logs before retry'})
        finally:
            child = None
            save(records_path, records)
            fcntl.flock(shared, fcntl.LOCK_UN)
        status('Job finished; see records and log for result', jobs)
        if args.once: return
        time.sleep(30)


if __name__ == '__main__':
    main()
