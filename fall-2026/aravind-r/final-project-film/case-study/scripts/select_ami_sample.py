"""Select whole AMI scenario meetings and export transcripts + abstractive summaries.

Selection rule:
  1. Scenario meetings only (ES/IS/TS series), from corpusResources/meetings.xml.
  2. Duration under MAX_SECONDS (35 min), from the meeting's `duration` attribute.
  3. The abstractive summary has a non-empty DECISIONS section.
  4. At most one meeting per team (series, e.g. ES2002): keep the one with the
     most DECISIONS sentences (tie -> shorter meeting -> lower ID).
  5. Rank teams by that DECISIONS count (desc), tie -> lower ID; take the top N.

Usage:
  python3 -I select_ami_sample.py <extracted_ami_dir> <sample_out_dir> [N]
"""
import csv
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

NITE = "{http://nite.sourceforge.net/}"
MAX_SECONDS = 35 * 60
SECTIONS = [("abstract", "ABSTRACT"), ("decisions", "DECISIONS"),
            ("problems", "PROBLEMS/ISSUES"), ("actions", "ACTIONS")]
RANGE = re.compile(r"#id\(([^)]+)\)(?:\.\.id\(([^)]+)\))?")


def meetings(root):
    tree = ET.parse(root / "corpusResources" / "meetings.xml")
    for m in tree.iter("meeting"):
        if m.get("type") != "scenario":
            continue
        roles = {s.get("nxt_agent"): s.get("role") for s in m.iter("speaker")}
        yield m.get("observation"), float(m.get("duration") or 0), roles


def summary(root, mid):
    path = root / "abstractive" / f"{mid}.abssumm.xml"
    if not path.exists():
        return None
    tree = ET.parse(path).getroot()
    out = {}
    for tag, _ in SECTIONS:
        out[tag] = [" ".join(s.text.split()) for el in tree.iter(tag)
                    for s in el.iter("sentence") if s.text and s.text.strip()]
    return out


def words_for(root, mid, agent):
    path = root / "words" / f"{mid}.{agent}.words.xml"
    toks = []
    for el in ET.parse(path).getroot():
        if el.tag != "w":
            continue
        st = el.get("starttime")
        toks.append((el.get(f"{NITE}id"), el.text or "", el.get("punc") == "true",
                     float(st) if st not in (None, "") else None))
    return toks


def utterances(root, mid, agent):
    toks = words_for(root, mid, agent)
    pos = {t[0]: i for i, t in enumerate(toks)}
    path = root / "dialogueActs" / f"{mid}.{agent}.dialog-act.xml"
    for da in ET.parse(path).getroot().iter("dact"):
        child = da.find(f"{NITE}child")
        m = RANGE.search(child.get("href")) if child is not None else None
        if not m or m.group(1) not in pos:
            continue
        a = pos[m.group(1)]
        b = pos.get(m.group(2) or m.group(1), a)
        span = toks[a:b + 1]
        text = ""
        for _, w, punc, _ in span:
            text += w if (punc or not text) else " " + w
        times = [t for *_, t in span if t is not None]
        if text.strip() and times:
            yield min(times), text.strip()


def transcript(root, mid, roles):
    lines = []
    for agent in sorted(roles):
        if not (root / "dialogueActs" / f"{mid}.{agent}.dialog-act.xml").exists():
            continue
        for start, text in utterances(root, mid, agent):
            lines.append((start, agent, text))
    lines.sort()
    out = []
    for start, agent, text in lines:
        s = int(start)
        out.append(f"[{s // 3600:02d}:{s % 3600 // 60:02d}:{s % 60:02d}] "
                   f"{agent} ({roles[agent]}): {text}")
    return "\n".join(out) + "\n"


def main():
    root, out = Path(sys.argv[1]), Path(sys.argv[2])
    n = int(sys.argv[3]) if len(sys.argv) > 3 else 10
    rows = []
    for mid, dur, roles in meetings(root):
        summ = summary(root, mid)
        if summ is None:
            continue
        rows.append(dict(meeting=mid, team=mid[:-1], duration_s=dur,
                         decisions=len(summ["decisions"]), actions=len(summ["actions"]),
                         eligible=dur < MAX_SECONDS and len(summ["decisions"]) > 0,
                         roles=roles, summ=summ))
    best = {}
    for r in rows:
        if not r["eligible"]:
            continue
        key = (-r["decisions"], r["duration_s"], r["meeting"])
        if r["team"] not in best or key < best[r["team"]][0]:
            best[r["team"]] = (key, r)
    chosen = sorted((r for _, r in best.values()),
                    key=lambda r: (-r["decisions"], r["meeting"]))[:n]
    chosen_ids = {r["meeting"] for r in chosen}

    out.mkdir(parents=True, exist_ok=True)
    with open(out / "selection.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["meeting", "duration_s", "decisions", "actions", "eligible", "selected"])
        for r in sorted(rows, key=lambda r: r["meeting"]):
            w.writerow([r["meeting"], r["duration_s"], r["decisions"], r["actions"],
                        r["eligible"], r["meeting"] in chosen_ids])

    for r in chosen:
        d = out / r["meeting"]
        d.mkdir(exist_ok=True)
        (d / "transcript.txt").write_text(transcript(root, r["meeting"], r["roles"]))
        body = [f"{label}\n" + "\n".join(f"- {s}" for s in r["summ"][tag])
                for tag, label in SECTIONS]
        (d / "summary.txt").write_text(
            f"AMI abstractive summary (human-written), meeting {r['meeting']}\n\n"
            + "\n\n".join(body) + "\n")
        print(f"{r['meeting']}\t{r['duration_s']:.0f}s\t{r['duration_s'] / 60:.1f} min"
              f"\tdecisions={r['decisions']}\tactions={r['actions']}")
    print(f"eligible={sum(r['eligible'] for r in rows)} teams={len(best)} selected={len(chosen)}")


if __name__ == "__main__":
    main()
