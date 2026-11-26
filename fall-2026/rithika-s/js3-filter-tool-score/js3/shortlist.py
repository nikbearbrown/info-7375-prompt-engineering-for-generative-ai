"""Shortlist the top kept postings and (optionally) ask Claude to justify them.

    python3 -m js3.shortlist --decisions out/filter/v1.1/decisions.jsonl \
        --top 5 [--run-claude]

1. Takes the postings the filter kept, sorted by score (highest first),
   ties broken by board then id (both ascending, as strings), and keeps the
   first --top.
2. Renders prompts/justify-v1.md for each one with that posting's text from
   the frozen corpus and writes out/shortlist/prompts/<board>__<id>.md,
   plus out/shortlist/shortlist.json listing the shortlist. Re-running with
   the same inputs rewrites identical files; a file that would change is
   refused (delete it yourself if that is intended).
3. Only with --run-claude: calls `claude -p` once per posting (prompt on
   stdin) through an injectable runner, and saves
   {date_utc, command, prompt_sha256, raw_stdout, raw_stderr, returncode}
   to out/shortlist/claude_raw/<board>__<id>.json. An existing raw file is
   never overwritten and that posting is not re-asked. Output is saved as
   received, whether or not it parses; js3.evidence reports parse errors.

Without --run-claude nothing is sent anywhere.
"""

import argparse
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from js3 import corpus as js3_corpus

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = Path("prompts") / "justify-v1.md"
TARGET = Path("data") / "target.example.json"
OUT = Path("out") / "shortlist"
CLAUDE_COMMAND = ["claude", "-p", "--output-format", "text", "--tools", ""]
CLAUDE_TIMEOUT_SECONDS = 300
RAW_KEYS = ("date_utc", "command", "prompt_sha256", "raw_stdout",
            "raw_stderr", "returncode")


class ShortlistError(Exception):
    """The shortlist cannot be written as asked."""


def sha256_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def stem(board, pid):
    """File stem for a posting. Board and id are checked so a stem can never
    leave its folder."""
    name = f"{board}__{pid}"
    if not re.fullmatch(r"[A-Za-z0-9._-]+__[A-Za-z0-9._-]+", name) \
            or ".." in name:
        raise ShortlistError(f"unsafe board/id for a file name: {name!r}")
    return name


def read_decisions(path):
    rows = []
    with open(path, encoding="utf-8") as fh:
        for number, line in enumerate(fh, 1):
            if line.strip():
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError as exc:
                    raise ShortlistError(
                        f"{path} line {number}: {exc.msg}") from None
    return rows


def top_kept(rows, top):
    kept = [r for r in rows if r.get("decision") == "kept"]
    kept.sort(key=lambda r: (-r["score"], str(r["board"]), str(r["id"])))
    return kept[:top]


def render_prompt(template, posting, target):
    values = {
        "target_title_keywords": ", ".join(target["target_title_keywords"]),
        "excluded_terms": ", ".join(target.get("excluded_terms", [])),
        "board": posting["board"],
        "id": str(posting["id"]),
        "title": posting.get("title") or "",
        "location": posting.get("location") or "",
        "body": posting.get("body_text") or "",
    }

    def fill(match):
        key = match.group(1)
        if key not in values:
            raise ShortlistError(f"unknown placeholder {{{{{key}}}}}")
        return values[key]

    # one pass, so text inside the posting is never treated as a placeholder
    return re.sub(r"\{\{([a-z_]+)\}\}", fill, template)


def write_stable(path, text):
    """Write text, or leave an identical file alone; refuse to change one."""
    path = Path(path)
    if path.exists():
        if path.read_text("utf-8") == text:
            return "unchanged"
        raise ShortlistError(f"{path} exists with different content; not "
                             "overwritten")
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "x", encoding="utf-8") as fh:
        fh.write(text)
    return "written"


def run_claude(prompt, run=subprocess.run):
    """Call `claude -p` once. `run` is injectable (tests pass a fake)."""
    try:
        done = run(CLAUDE_COMMAND, input=prompt, capture_output=True,
                   text=True, timeout=CLAUDE_TIMEOUT_SECONDS, check=False)
    except FileNotFoundError as exc:
        return "", f"cannot start claude: {exc}", None
    except subprocess.TimeoutExpired as exc:
        out = exc.stdout if isinstance(exc.stdout, str) else ""
        return out, f"timed out after {CLAUDE_TIMEOUT_SECONDS}s", None
    return done.stdout, done.stderr, done.returncode


def save_raw(path, prompt, stdout, stderr, returncode, now=None):
    record = {
        "date_utc": (now or datetime.now(timezone.utc)).isoformat(
            timespec="seconds"),
        "command": CLAUDE_COMMAND,
        "prompt_sha256": sha256_text(prompt),
        "raw_stdout": stdout,
        "raw_stderr": stderr,
        "returncode": returncode,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "x", encoding="utf-8") as fh:  # never overwrite
        json.dump(record, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    return record


def build(root, decisions_path, top, out_dir, run_claude_flag=False,
          runner=run_claude, log=print):
    root = Path(root)
    rows = read_decisions(decisions_path)
    chosen = top_kept(rows, top)
    if not chosen:
        raise ShortlistError(f"no kept postings in {decisions_path}")
    versions = sorted({str(r.get("config_version")) for r in rows})
    postings = {(p["board"], str(p["id"])): p
                for p in js3_corpus.load(root)["postings"]}
    template = (root / TEMPLATE).read_text("utf-8")
    target = json.loads((root / TARGET).read_text("utf-8"))

    entries = []
    for rank, row in enumerate(chosen, 1):
        key = (row["board"], str(row["id"]))
        if key not in postings:
            raise ShortlistError(f"{key} is in the decisions but not in the "
                                 "frozen corpus")
        name = stem(*key)
        prompt = render_prompt(template, postings[key], target)
        prompt_path = out_dir / "prompts" / f"{name}.md"
        state = write_stable(prompt_path, prompt)
        log(f"{rank}. {key[0]}/{key[1]} score {row['score']} "
            f"{row.get('title', '')!r}: prompt {state}")
        entries.append({"rank": rank, "board": key[0], "id": key[1],
                        "title": row.get("title"), "score": row["score"],
                        "prompt": f"prompts/{name}.md",
                        "prompt_sha256": sha256_text(prompt),
                        "claude_raw": f"claude_raw/{name}.json"})
        if run_claude_flag:
            raw_path = out_dir / "claude_raw" / f"{name}.json"
            if raw_path.exists():
                log(f"   claude_raw/{name}.json exists: not re-asked")
                continue
            stdout, stderr, code = runner(prompt)
            save_raw(raw_path, prompt, stdout, stderr, code)
            log(f"   claude returncode {code}: saved claude_raw/{name}.json")

    manifest = {
        "decisions": str(decisions_path),
        "config_versions": versions,
        "top": top,
        "order": "score desc, then board asc, then id asc",
        "template": str(TEMPLATE),
        "template_sha256": sha256_text(template),
        "postings": entries,
    }
    write_stable(out_dir / "shortlist.json",
                 json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    return manifest


def main(argv=None, runner=run_claude):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--decisions", required=True)
    parser.add_argument("--top", type=int, default=5)
    parser.add_argument("--run-claude", action="store_true",
                        help="call `claude -p` once per shortlisted posting")
    parser.add_argument("--root", default=str(ROOT))
    parser.add_argument("--out", default=None,
                        help="output folder (default <root>/out/shortlist)")
    args = parser.parse_args(argv)
    if args.top < 1:
        parser.error("--top must be at least 1")
    root = Path(args.root)
    out_dir = Path(args.out) if args.out else root / OUT
    try:
        build(root, Path(args.decisions), args.top, out_dir,
              args.run_claude, runner)
    except (ShortlistError, js3_corpus.CorpusError, OSError) as exc:
        print(f"shortlist: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
