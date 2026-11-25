"""Numbers quoted in FILTER.md v1 (JS3 Step 1), recomputed from the saved raw files.

Why it exists: FILTER.md cites measurements (wrong version W1, v2 candidate L1). The brief's
honesty rule wants every number traceable, so this script is the one place that produces them.
It reads only `evidence/raw/<RUN>/` and the persona; it changes no profile and fetches nothing.

Run: .venv/bin/python reports/filter_v1_measure.py   -> reports/filter_v1_measure/result.md
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from job_agent.judges.checks import CHECKS, Criteria, PostingText  # noqa: E402
from job_agent.judges.words import has_all_words, strip_html, words  # noqa: E402
from job_agent.watch.boards import ashby, greenhouse  # noqa: E402

# The latest run that saved all three working boards (JS2, 2026-11-08); striqe fails on purpose.
RUN = "2026-11-08T234257Z"
BOARDS = [("stripe", greenhouse), ("cloudflare", greenhouse), ("openai", ashby)]
# v2 candidate L1: US city names and the abbreviations boards actually write (e.g. "Toronto, NY, SEA, SF").
L1_EXTRA = ["ny", "sea", "sf", "nyc", "seattle", "san francisco", "new york"]


def load_postings():
    raw = ROOT / "evidence" / "raw" / RUN
    for name, mod in BOARDS:
        for p in mod.parse((raw / f"{name}_content.json").read_bytes()):
            yield name, p


def criteria(profile: dict) -> Criteria:
    # Rules 1a/1b/2 read only the profile; the résumé side is not needed for them.
    return Criteria(resume_keywords=[], profile=profile, aliases={}, phrases=[])


def w1_substring(postings, keywords) -> list[str]:
    """W1: rule 3 with `kw.lower() in jd.lower()` instead of word matching."""
    flips, only_sub = 0, {}
    for _, p in postings:
        jd = strip_html(p.content)
        jd_words = set(words(jd))
        sub = [k for k in keywords if k.lower() in jd.lower() and not has_all_words(k, jd_words)]
        for k in sub:
            only_sub[k] = only_sub.get(k, 0) + 1
        # Cut by v1 (no keyword as a word) but passed by the substring version.
        if sub and not any(has_all_words(k, jd_words) for k in keywords):
            flips += 1
    rows = [f"| {k} | {n} |" for k, n in sorted(only_sub.items(), key=lambda x: -x[1])]
    return ["## W1 — substring match for rule 3", "",
            f"Postings cut at rule 3 by v1 that substring matching would pass: **{flips}** of {len(postings)}.", "",
            "| résumé keyword | JDs where it appears only inside another word |", "|---|---|", *rows, ""]


def l1_locations(postings, profile) -> list[str]:
    c1 = criteria(profile)
    c2 = criteria(dict(profile, locations=profile["locations"] + L1_EXTRA))
    cut_after_titles, flips = 0, []
    for name, p in postings:
        t = PostingText.of(p)
        titles_pass = CHECKS[0].run(t, c1).passed and CHECKS[1].run(t, c1).passed
        before, after = CHECKS[2].run(t, c1).passed, CHECKS[2].run(t, c2).passed
        if titles_pass and not before:
            cut_after_titles += 1
        if before != after:
            flips.append(f"| {name} | {titles_pass} | {p.title} | {p.location} |")
    return ["## L1 — city names and abbreviations in `profile.locations`", "",
            f"Pass rules 1a + 1b but cut at rule 2 under v1: **{cut_after_titles}**.", "",
            f"Rule 2 cut → pass when adding {L1_EXTRA}: **{len(flips)}**.", "",
            "| board | passes title rules | title | location |", "|---|---|---|---|", *flips, ""]


def main() -> None:
    postings = list(load_postings())
    profile = json.loads((ROOT / "personas" / "aarav-patel.profile.json").read_text())
    resume = json.loads((ROOT / "personas" / "aarav-patel.resume.json").read_text())
    keywords = [k for s in resume["skills"] for k in s["keywords"]]
    lines = [f"# FILTER v1 measurements — `evidence/raw/{RUN}/`, {len(postings)} postings", "",
             *w1_substring(postings, keywords), *l1_locations(postings, profile)]
    out = ROOT / "reports" / "filter_v1_measure" / "result.md"
    out.parent.mkdir(exist_ok=True)
    out.write_text("\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
