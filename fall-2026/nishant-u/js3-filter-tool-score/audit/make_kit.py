"""Build the blind audit kit for the FILTER.md v1 reject audit. Offline; deterministic for a seed.

    python -m audit.make_kit --seed 20261124

Sampling, in this order, with one random.Random(seed):
1. reject: 30 drawn uniformly (random.sample) from ALL rejected postings, so the sample can
   speak for the reject pile as a whole.
2. close: 5 from the rejected postings NOT drawn in step 1 that fail exactly one of F1-F4
   when every rule is checked independently (not just the first failing one). Tiers, filled
   in order, random within a tier: (a) only F4 fails (0 shipped skills, F1-F3 pass);
   (b) only F2 fails (a role word plus an exclusion word); (c) only F1 fails and the title has
   a borderline word (BORDERLINE below); (d) only F3 fails.
3. accept: 10 drawn from the accepted postings (all of them if there are 10 or fewer).
The 45 are shuffled together. The kit never writes the filter's reason, rule or tier.
"""
import argparse
import csv
import html
import random
import re
from pathlib import Path

from agent.resume import load_resume
from agent3 import filter as flt
from agent3 import run as runner

ROOT = Path(__file__).resolve().parents[1]
BORDERLINE = ("AI", "science", "sciences", "scientists", "analysts", "modeling", "insights", "research",
              "statistics", "statistical", "quantitative", "intelligence", "BI")
N_REJECT, N_CLOSE, N_ACCEPT = 30, 5, 10


def failing_rules(posting, skills):
    """Which of F1-F4 fail when each is checked on its own (a missing field fails its rule)."""
    title, location, text = posting["title"], posting["location"], posting["text"]
    fails = []
    if not title or not any(flt.find_term(title, w) for w in flt.ROLE_WORDS):
        fails.append("F1")
    if not title or any(flt.find_term(title, w) for w in flt.EXCLUDE_WORDS):
        fails.append("F2")
    if not location or not flt.us_part(location):
        fails.append("F3")
    if not text or len(flt.skills_in(text, skills)) < flt.MIN_SKILLS:
        fails.append("F4")
    return fails


def close_tier(posting, fails):
    if len(fails) != 1:
        return None
    rule = fails[0]
    if rule == "F4":
        return "a"
    if rule == "F2":
        return "b"
    if rule == "F1" and any(flt.find_term(posting["title"], w) for w in BORDERLINE):
        return "c"
    if rule == "F3":
        return "d"
    return None


def readable(raw_html):
    """Display-only text for a human reader: HTML removed, paragraph and list breaks kept."""
    text = html.unescape(raw_html or "")
    text = re.sub(r"(?i)<\s*li[^>]*>", "\n- ", text)
    text = re.sub(r"(?i)<\s*(br|/p|/div|/li|/h[1-6]|/ul|/ol)[^>]*>", "\n", text)
    text = html.unescape(re.sub(r"<[^>]+>", " ", text))
    lines = [re.sub(r"[ \t ]+", " ", line).strip() for line in text.splitlines()]
    out, blank = [], False
    for line in lines:
        if line:
            out.append(line)
            blank = False
        elif not blank:
            out.append("")
            blank = True
    return "\n".join(out).strip()


def raw_text(posting, raw_root):
    import json
    data = json.loads((Path(raw_root) / posting["source"]).read_text(encoding="utf-8"))
    job_id = posting["posting_id"].split(":", 2)[2]
    job = next(j for j in data["jobs"] if str(j.get("id")) == job_id)
    if posting["system"] == "greenhouse":
        return readable(job.get("content"))
    return readable(job.get("descriptionHtml")) or (job.get("descriptionPlain") or "").strip()


def build(seed, raw_root, out_dir, resume_path):
    skills = flt.shipped_skills(load_resume(resume_path))
    postings, _, _ = runner.collect(raw_root)
    verdicts = {p["posting_id"]: flt.evaluate(p, skills)["verdict"] for p in postings}
    rejects = [p for p in postings if verdicts[p["posting_id"]] == "reject"]
    accepts = [p for p in postings if verdicts[p["posting_id"]] == "accept"]
    rng = random.Random(seed)

    reject_sample = rng.sample(rejects, N_REJECT)
    drawn = {p["posting_id"] for p in reject_sample}
    tiers = {t: [] for t in "abcd"}
    for p in rejects:
        if p["posting_id"] in drawn:
            continue
        tier = close_tier(p, failing_rules(p, skills))
        if tier:
            tiers[tier].append(p)
    close = []
    for t in "abcd":
        pool = tiers[t][:]
        rng.shuffle(pool)
        close.extend(pool[:N_CLOSE - len(close)])
    accept_sample = accepts[:] if len(accepts) <= N_ACCEPT else rng.sample(accepts, N_ACCEPT)

    rows = ([("reject", p) for p in reject_sample] + [("close", p) for p in close]
            + [("accept", p) for p in accept_sample])
    rng.shuffle(rows)

    out_dir = Path(out_dir)
    (out_dir / "postings").mkdir(parents=True, exist_ok=True)
    with open(out_dir / "audit.csv", "w", newline="", encoding="utf-8-sig") as fh:
        writer = csv.writer(fh)
        writer.writerow(["posting_id", "group", "board", "title", "location", "my_relevant", "my_note"])
        for group, p in rows:
            writer.writerow([p["posting_id"], group, f"{p['system']}:{p['board']}", p["title"],
                             p["location"], "", ""])
            name = p["posting_id"].replace(":", "_") + ".txt"
            (out_dir / "postings" / name).write_text(
                f"posting_id: {p['posting_id']}\nTitle: {p['title']}\nLocation: {p['location']}\n"
                f"URL: {p['url']}\n\n{raw_text(p, raw_root)}\n", encoding="utf-8")
    sizes = {"reject": len(reject_sample), "close": len(close), "accept": len(accept_sample)}
    pools = {"rejects": len(rejects), "accepts": len(accepts),
             "close_candidates_by_tier": {t: len(v) for t, v in tiers.items()}}
    return sizes, pools


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--raw-root", default=str(ROOT / "out"))
    parser.add_argument("--out", default=str(ROOT / "audit"))
    parser.add_argument("--resume", default=str(ROOT / "data" / "resume.example.json"))
    args = parser.parse_args(argv)
    sizes, pools = build(args.seed, args.raw_root, args.out, args.resume)
    print(f"seed {args.seed}: {sizes} from pools {pools}")


if __name__ == "__main__":
    main()
