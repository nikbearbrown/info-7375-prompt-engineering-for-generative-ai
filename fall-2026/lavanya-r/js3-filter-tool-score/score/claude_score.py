"""Ask Claude whether a posting is worth Priya's time, for the Chapter 9
experiments. Every call's full raw reply is saved; nothing is invented.

python3 -B score/claude_score.py E0a E0b E1 E2 E3   # runs each on group H
python3 -B score/claude_score.py --report          # agreement with my labels

Calls `claude -p` from a scratch folder OUTSIDE this repo, so the repo's
CLAUDE.md / AGENTS.md are not loaded as context (they would be a hidden
context change). Tools are disabled (--tools "").
"""
import concurrent.futures as cf
import datetime
import json
import pathlib
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
from agent import corpus  # noqa: E402

SCORE = HERE / "score"
EXP = json.loads((SCORE / "experiments.json").read_text())
OUT = SCORE / "runs"
MAX_TEXT = 6000


def build_prompt(p, cfg):
    prompt = (SCORE / "prompts" / cfg["prompt"]).read_text()
    context = (SCORE / "context" / cfg["context"]).resolve().read_text()
    loc = "; ".join(p["locations"])
    return (f"{prompt}\n\n## CANDIDATE\n{context}\n\n## POSTING\n"
            f"Title: {p['title'].strip()}\nLocation: {loc}\n\n"
            f"{p['text'][:MAX_TEXT]}\n")


def call(prompt, model, cwd):
    t0 = datetime.datetime.now(datetime.timezone.utc)
    r = subprocess.run(["claude", "-p", "--model", model, "--tools", "",
                        "--no-session-persistence", "--output-format", "json"],
                       input=prompt, capture_output=True, text=True, cwd=cwd,
                       timeout=300)
    return {"started": t0.isoformat(timespec="seconds"), "exit": r.returncode,
            "stdout": r.stdout, "stderr": r.stderr[-2000:]}


def parse(raw):
    try:
        res = json.loads(raw["stdout"])
        text = res.get("result", "")
        s = text[text.index("{"): text.rindex("}") + 1]
        v = json.loads(s)
        return v.get("verdict"), res.get("modelUsage") and list(res["modelUsage"])
    except Exception:
        return None, None


def run(name):
    cfg = EXP[name]
    draw = json.loads((HERE / "audit/draw.json").read_text())
    hand = {json.loads(l)["key"]: json.loads(l)["verdict"]
            for l in open(HERE / "audit/hand_verdicts.jsonl")}
    keys = [k for k in draw["groups"]["H"] if k in hand]
    posts = {p["key"]: p for p in corpus.load(HERE / "runs/2026-11-24T220432Z-live")}
    out = OUT / name
    out.mkdir(parents=True, exist_ok=True)
    cwd = tempfile.mkdtemp(prefix="js3-score-")
    def one(k):
        f = out / (k.replace("/", "__") + ".json")
        if f.exists():
            return
        raw = call(build_prompt(posts[k], cfg), cfg["model"], cwd)
        raw.update(key=k, experiment=name, config=cfg)
        f.write_text(json.dumps(raw, ensure_ascii=False, indent=1))
    with cf.ThreadPoolExecutor(6) as ex:
        list(ex.map(one, keys))
    print(name, "done", len(list(out.glob("*.json"))), "replies")


def report():
    draw = json.loads((HERE / "audit/draw.json").read_text())
    hand = {json.loads(l)["key"]: json.loads(l)["verdict"]
            for l in open(HERE / "audit/hand_verdicts.jsonl")}
    keys = [k for k in draw["groups"]["H"] if hand.get(k) in ("y", "n")]
    base = {}
    rows = []
    for name in EXP:
        if name.startswith("_") or not (OUT / name).exists():
            continue
        agree = dis = abst = bad = 0
        verdicts, models = {}, set()
        for k in keys:
            f = OUT / name / (k.replace("/", "__") + ".json")
            v, m = parse(json.loads(f.read_text())) if f.exists() else (None, None)
            models.update(m or [])
            verdicts[k] = v
            if v is None:
                bad += 1
            elif v == "cannot_tell":
                abst += 1
            elif (v == "yes") == (hand[k] == "y"):
                agree += 1
            else:
                dis += 1
        if name == "E0a":
            base = verdicts
        flips = sum(1 for k in keys if base and verdicts.get(k) != base.get(k))
        rows.append((name, EXP[name]["what"], agree, dis, abst, bad, flips,
                     ",".join(sorted(models))))
    print(f"held-out labels (group H, y/n): {len(keys)}")
    print("| Exp | One change | Agree | Disagree | cannot_tell | Unparsed | Verdicts changed vs E0a | Model reported |")
    print("|---|---|---|---|---|---|---|---|")
    for r in rows:
        print("| " + " | ".join(str(x) for x in r) + " |")


if __name__ == "__main__":
    if sys.argv[1:] == ["--report"]:
        report()
    else:
        for n in sys.argv[1:]:
            run(n)
