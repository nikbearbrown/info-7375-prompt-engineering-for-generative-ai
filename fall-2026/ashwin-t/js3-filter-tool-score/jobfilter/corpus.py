"""The JS3 corpus: every posting the JS2 live run collected on 2026-11-09.

Built once from JS2's saved raw responses (byte-for-byte, sha256 in JS2's trace.jsonl),
parsed with JS2's unchanged parsers, and frozen into corpus/postings.json so this folder
is self-contained. `python3 -m jobfilter.corpus --build` rebuilds it and checks every hash.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

from .providers import PROVIDERS, ParseError

HERE = Path(__file__).resolve().parent.parent
CORPUS = HERE / "corpus" / "postings.json"
JS2_RUN = HERE.parent / "js2-loop-tools-diff" / "runs" / "2026-11-09T20-21-52Z-live"


def _trace_hashes(run: Path) -> dict:
    """raw file name -> sha256, as JS2 recorded it at fetch time."""
    out = {}
    for line in (run / "trace.jsonl").read_text().splitlines():
        ev = json.loads(line)
        if ev.get("sha256") and ev.get("raw_file"):
            out[Path(ev["raw_file"]).name] = ev["sha256"]
    return out


def build(run: Path = JS2_RUN) -> dict:
    hashes = _trace_hashes(run)
    sources, postings = [], []
    for raw in sorted((run / "raw").glob("*.json")):
        body = raw.read_bytes()
        digest = hashlib.sha256(body).hexdigest()
        recorded = hashes.get(raw.name)
        if recorded is not None and recorded != digest:
            raise SystemExit(f"{raw.name}: sha256 {digest} != JS2 trace {recorded}")
        provider, board = raw.name.replace("__attempt-1.json", "").split("__")
        entry = {"file": raw.name, "provider": provider, "board": board, "sha256": digest,
                 "sha256_matches_js2_trace": recorded == digest if recorded else None}
        try:
            parsed = PROVIDERS[provider].parse(body, board)
        except ParseError as exc:
            entry.update(status="failed", reason=f"{exc.kind}: {exc}", postings=None)
            sources.append(entry)
            continue
        entry.update(status="parsed", postings=len(parsed))
        sources.append(entry)
        postings.extend(parsed)
    return {
        "collected_utc": "2026-11-09T20:21:52Z",
        "collected_by": "JS2 live run (fall-2026/ashwin-t/js2-loop-tools-diff, code e270605)",
        "sources": sources,
        "postings": postings,
    }


def load(path: Path = CORPUS) -> dict:
    return json.loads(Path(path).read_text())


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if argv != ["--build"]:
        print("usage: python3 -m jobfilter.corpus --build", file=sys.stderr)
        return 2
    data = build()
    CORPUS.parent.mkdir(exist_ok=True)
    CORPUS.write_text(json.dumps(data, indent=1, ensure_ascii=False, sort_keys=True) + "\n")
    for s in data["sources"]:
        print(f'{s["provider"]}/{s["board"]}: {s["status"]} {s["postings"]} '
              f'(sha256 matches JS2 trace: {s["sha256_matches_js2_trace"]})')
    print(f'{len(data["postings"])} postings -> {CORPUS.relative_to(HERE)}')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
