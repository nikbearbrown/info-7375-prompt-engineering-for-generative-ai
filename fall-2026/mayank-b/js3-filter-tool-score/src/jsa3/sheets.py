"""Seeded draws and the hand-judgment sheets (held-out labels, reject audit) and reading them back.

The sheets are Markdown, one block per posting, with blank lines for MY verdicts. Claude Code
never fills a verdict line. read_verdicts() parses only lines of the exact form
"**My verdict:** keep|reject|cannot tell".
"""
from __future__ import annotations

import random
import re

from . import filter as F

VERDICT_RE = re.compile(r"^### (?P<tag>[HDRCK]\d+) · (?P<board>\S+) · (?P<id>\S+)\s*$|^\*\*My verdict:\*\*[ \t]*(?P<v>[^\n]*)$", re.M)
YEARS_RE = re.compile(r"[^.\n]{0,120}\b\d+\s*\+?\s*(?:-|–|to)?\s*\d*\+?\s*years?\b[^.\n]{0,120}", re.I)
FLAG_WORDS = ("pipeline", "training")   # FILTER.md section 5: false-friend candidates to flag


def draw(records: list[dict], cfg: dict, seeds: dict, sizes: dict) -> dict:
    """Held-out H first (10 kept / 10 close calls / 10 random rejects), then the audit D from what is left:
    30 random rejects, the close calls (all, or a seeded 15), 10 kept. H and D never overlap."""
    keep = [r for r in records if r["verdict"] == "keep"]
    close = [r for r in records if F.is_close_call(r, cfg)]
    rej = [r for r in records if r["verdict"] == "reject"]
    key = lambda r: (r["board"], r["id"])

    def sample(pool, n, rng, taken):
        pool = sorted((r for r in pool if key(r) not in taken), key=key)
        return pool if len(pool) <= n else rng.sample(pool, n)

    taken: set = set()
    rh = random.Random(seeds["heldout"])
    H = []
    for stratum, pool in (("kept", keep), ("close", close), ("reject", rej)):
        got = sample(pool, sizes["heldout_per_stratum"], rh, taken)
        taken |= {key(r) for r in got}
        H += [dict(r, stratum=stratum) for r in got]
    rh.shuffle(H)
    ra = random.Random(seeds["audit"])
    D = {}
    for part, pool, n in (("random-rejects", rej, sizes["audit_rejects"]), ("close-calls", close, sizes["audit_close_max"]),
                          ("kept", keep, sizes["audit_kept"])):
        got = sample(pool, n, ra, taken)
        taken |= {key(r) for r in got}
        D[part] = got
    return {"H": H, "D": D, "pools": {"kept": len(keep), "close": len(close), "rejects": len(rej),
                                      "cannot_tell": sum(r["verdict"] == "cannot_tell" for r in records), "all": len(records)}}


def excerpt(text: str, n: int = 900) -> str:
    """The part of the posting that describes the job: from 'About the role' / 'The role' if present."""
    t = text or ""
    m = re.search(r"\b(About the role|About The Role|The role|What you'll do|What You'll Do|Responsibilities)\b", t)
    start = m.start() if m and m.start() < len(t) - 200 else 0
    s = t[start:start + n].strip()
    return s + ("…" if start + n < len(t) else "")


def years_lines(text: str) -> list[str]:
    return [m.group(0).strip() for m in YEARS_RE.finditer(text or "")][:4]


def flag_hits(text: str) -> list[str]:
    out = []
    for w in FLAG_WORDS:
        for at in F.find_term(text or "", w)[:2]:
            out.append(f"`{w}`: " + F.snippet(text, at, 200))
    return out


def block(tag: str, r: dict, posting: dict, blind: bool) -> str:
    text = posting.get("text") or ""
    lines = [f"### {tag} · {r['board']} · {r['id']}", "",
             f"**{r['title']}** · {r['location'] or '(no location)'} · [original posting]({r['url']})", ""]
    if not blind:
        hits = ", ".join(f"`{h['word']}`" + (f" (×{h['count']})" if h["count"] > 1 else "") for h in r["topic_hits"]) or "none"
        lines += [f"Filter v{r['filter_version']}: **{r['verdict']}**. {r['reason']}. Score {r['score']}. Role word: {r['role_match'] or '-'}. "
                  f"Exclude word: {r['exclude_match'] or '-'}. Location: {r['location_status']}{' (' + r['location_piece'] + ')' if r['location_piece'] else ''}.",
                  f"Topic words: {hits}", ""]
        for h in r["topic_hits"][:3]:
            lines.append(f"> `{h['word']}` → {h['snippet']}")
        flags = flag_hits(text)
        if flags:
            lines += ["", "False-friend check:"] + [f"> {f}" for f in flags]
        lines.append("")
    yl = years_lines(text)
    if yl:
        lines += ["Experience lines in the text: " + " · ".join(f"“{y}”" for y in yl), ""]
    lines += ["<details><summary>Posting text (excerpt)</summary>", "", excerpt(text) if text else "(no posting text)", "", "</details>", "",
              "**My verdict:** ", "**Why (one line):** ", ""]
    if not blind:
        lines.insert(-1, "**False friend? (word, or -):** ")
    return "\n".join(lines)


def read_verdicts(md: str) -> dict:
    """-> {(board, id): {"tag", "verdict"}}; verdict is None when the line is still blank."""
    out, cur = {}, None
    for m in VERDICT_RE.finditer(md):
        if m.group("tag"):
            cur = (m.group("board"), m.group("id"))
            out[cur] = {"tag": m.group("tag"), "verdict": None}
        elif cur is not None:
            v = m.group("v").strip().lower().rstrip(".")
            v = {"cannot_tell": "cannot tell"}.get(v, v)
            out[cur]["verdict"] = v if v in ("keep", "reject", "cannot tell") else (None if not v else f"INVALID:{v}")
    return out
