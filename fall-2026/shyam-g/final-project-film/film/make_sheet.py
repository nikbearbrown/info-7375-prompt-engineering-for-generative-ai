"""Writes the StopLine pitch beat sheet in the Brutalist show-tell format.

Output: film/reel/beat_sheet.json (what the toolkit renders) and a copy at
../beat_sheet.json (the submission copy). Pattern follows the toolkit's
skills/make/show-tell/reference/example-make_sheet.py at commit 4115560, with
these deliberate changes so the film is narrated as myself:
  - BIDEA greeting is mine, not the toolkit's default persona line.
  - BDEFS (terms card) and BHTF (Your Turn) are dropped to stay under 4 minutes;
    bookend_check.py allows exempting "bhtf", "cold-open" and "bvdt".
  - BOUT outro carries my title and my handle (metadata.channel_title).

Run: python film/make_sheet.py            (writes the sheet)
     python film/make_sheet.py --final    (also fails if any [FILL] remains)
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REEL = HERE / "reel"
ROOT_COPY = HERE.parent / "beat_sheet.json"

SLUG = "stopline-pitch"
TITLE = "StopLine: Checking the Evidence Behind a Quality Decision"
NAME = "Shyam Sundar Jayaraman Gopalakrishnan"
HANDLE = "@contactshyam14-code"
VOICE = "am_onyx"
WPS = 2.5  # rough speaking rate, used only for the estimate before audio exists

SPARSE_REASON = ("show-tell style: one drawn object or scene on a cream stage per beat, minimal labels, "
                 "the voice carries the explanation. Only underfill and clustered are waived.")


def beat(bid, act, narration, cls, image, show):
    return {"beat_id": bid, "act": act, "lane": "manim", "proof_gate": "SHOW",
            "narration_text": narration, "estimated_duration_s": round(len(narration.split()) / WPS, 1),
            "voice": VOICE, "engine": "kokoro",
            "new_visual_element": image.split(".")[0],
            "shot": {"type": "GRAPHIC", "source": "own", "visual_intent": image, "show": show,
                     "manim": {"class": cls}, "motion_claim": image},
            "qc": {"sparse_by_design": True, "sparse_reason": SPARSE_REASON}}


BODY = [
    beat("B00", "what",
         "My final project is called StopLine. It's a small Python tool that checks a proposed decision on a "
         "factory quality incident against the evidence that decision cites.",
         "B00_Crate", "A kraft crate (the lot) drops in. A proposed-action sheet appears beside it, and an ink "
         "arrow draws from the sheet to two evidence records.",
         [{"at": 0.05, "event": "crate drops"}, {"at": 0.25, "event": "sheet + records"}, {"at": 0.65, "event": "arrow draws"}]),
    beat("B01", "what",
         "When it's finished, it will be a public repository with a command-line tool, a synthetic test set, "
         "tests, and an evaluation report that lists where it fails.",
         "B01_Parts", "Three objects land in a row: a dark terminal block, a stack of test pages, and a report page.",
         [{"at": 0.05, "event": "terminal"}, {"at": 0.25, "event": "pages"}, {"at": 0.65, "event": "report"}]),
    beat("B02", "what",
         "It gives one of three answers: human review required, needs more evidence, or accept for review. The "
         "most cautious one wins. It never approves anything. Accept only means a person may now look at it.",
         "B02_Lanes", "Three stacked lanes. A marker drops from the bottom lane up to the top lane, which takes a terracotta dot.",
         [{"at": 0.05, "event": "lanes"}, {"at": 0.65, "event": "marker settles on the top lane"}]),
    beat("B03", "exists",
         "A first version exists today. Claude Code wrote most of the code with me on October fourteenth, and "
         "I've since reviewed every check myself. Here is the real output: seventeen synthetic incidents, one "
         "outcome each, and twelve tests passing. Every incident and number in it is made up for testing.",
         "B03_Run", "A terminal panel redraws three real lines from reports/cli_output.txt and reports/test_run.txt "
         "(run 2026-10-14). Caption: real run, synthetic data.",
         [{"at": 0.05, "event": "panel"}, {"at": 0.25, "event": "real lines"}, {"at": 0.65, "event": "check"}]),
    beat("B04", "why",
         "The real alternative is SAP's quality module, where a usage decision accepts or rejects a lot. From my "
         "experience in SAP, it already checks that results are recorded, that they belong to the right lot, and "
         "that they come before the decision, and it can refuse or warn. It checks structured results, not the "
         "written justification. So, honestly, StopLine doesn't beat SAP yet. The question I'll test is whether "
         "checking written claims catches something SAP's checks don't, and right now my own tool misses that case too.",
         "B04_SAP", "Constructed sketch: two columns, SAP QM and StopLine, ticks on the same three rows in both; "
         "a fourth row stays empty in both.",
         [{"at": 0.05, "event": "columns"}, {"at": 0.25, "event": "three ticks each"}, {"at": 0.65, "event": "empty fourth row"}]),
    beat("B05", "who",
         "It's aimed at supply chain manager roles. When a lot goes on hold, supply waits on the decision to "
         "release, rework, or scrap it. A hiring manager runs one command, sees an outcome for each incident, "
         "and opens the report, in under a minute.",
         "B05_Hold", "The crate sits behind a hold bar. A terminal prompt appears, then a report page slides in beside it.",
         [{"at": 0.05, "event": "crate on hold"}, {"at": 0.25, "event": "prompt"}, {"at": 0.65, "event": "report"}]),
    beat("B06", "proves",
         "It shows verification: every claim checked against a record. Evaluation: a labelled test set and a "
         "report. And escalation: what it can't check goes to a person. It does not show an agent loop or "
         "prompt contracts. There's no language model in it.",
         "B06_Badges", "Three badges light up (verify, evaluate, escalate); two more stay ghost grey with a slash.",
         [{"at": 0.05, "event": "badges"}, {"at": 0.25, "event": "three light"}, {"at": 0.65, "event": "two slashed"}]),
    beat("B07", "scope",
         "Out of scope, on purpose: real factory data, and any model making the decision. The first piece, the "
         "command-line run, already works, and the saved output shows it ran.",
         "B07_Fence", "A fence line: a crate and a dark model block outside it; inside, a terminal whose light comes on.",
         [{"at": 0.05, "event": "fence"}, {"at": 0.25, "event": "outside objects"}, {"at": 0.65, "event": "terminal lights"}]),
    beat("B08", "risk",
         "The risk is already visible. Two of seventeen cases get it wrong. One claim says all suspect units are "
         "contained, citing four hundred units from a lot of twelve hundred. The number is right, the sentence "
         "misleads, and every rule passes. A check is only as strict as the information it's given. I'll add "
         "harder cases and keep escalation as the default.",
         "B08_Gate", "A row of twelve small crates; only four sit inside a rope. A ticket passes through the gate, which stays open.",
         [{"at": 0.05, "event": "twelve crates, rope round four"}, {"at": 0.25, "event": "gate + ticket"}, {"at": 0.65, "event": "ticket passes"}]),
    beat("B09", "why-me",
         "Why this project? I had an idea of how to bring it to life, so I took it on. It's a mix. What I already "
         "bring is supply chain work: supplier scorecards and root-cause reviews in SAP as an analyst, and a Six "
         "Sigma Green Belt. What's new is writing and testing a verification engine like this myself, with a "
         "labelled test set and an honest failure report, and blending supply chain with AI in a way I can check.",
         "B09_Columns", "Two columns of pages, already-have and new-to-me; each column fills with scribbled pages.",
         [{"at": 0.05, "event": "two columns"}, {"at": 0.25, "event": "already-have fills"}, {"at": 0.65, "event": "new-to-me fills"}]),
    beat("B10", "close",
         "What exists today: the engine, the data, the tests, and an honest report. What will exist: harder test "
         "cases, fixes for the misses, and a real test against SAP's checks. That's StopLine.",
         "B10_Split", "Left, four solid crates labelled exists; right, three ghost crates labelled will exist.",
         [{"at": 0.05, "event": "solid crates"}, {"at": 0.65, "event": "ghost crates"}]),
]


def remotion(bid, act, narration, pattern, props, show, **extra):
    b = {"beat_id": bid, "act": act, "lane": "bookend", "proof_gate": "SHOW",
         "narration_text": narration, "estimated_duration_s": round(len(narration.split()) / WPS, 1),
         "voice": VOICE, "engine": "kokoro",
         "shot": {"type": "REMOTION", "source": "own", "show": show, "remotion": {"pattern": pattern, "props": props}}}
    b.update(extra)
    return b


OPEN = remotion(
    "BIDEA", "the question",
    "Hi, I'm Shyam Sundar. When a lot is released, the question isn't only whether someone approved it. "
    "It's whether the evidence behind it holds up.",
    "BrutalistHesitantWriter",
    {"text": "Was this lot release\napproved", "triggerWords": "approved", "replacementWords": "backed by evidence",
     "fontSize": 70, "charMs": 22, "hesitateBetween": 6, "hesitateWithin": 1, "mistakeRate": 2, "jitter": 20,
     "seed": SLUG, "banner": ""},
    [{"at": 0.0, "event": "types 'Was this lot release approved'"},
     {"at": 0.6, "event": "corrects 'approved' to 'backed by evidence' on the spoken correction"}],
    lead_silence_s=0.8,
    motion_claim="The writer types the naive question and corrects it to the real one: is the release backed by evidence.",
    qc={"sparse_by_design": True, "sparse_reason": "Hesitant-writer bookend: the correction is the motion."})

OUTRO = {"beat_id": "BOUT", "act": "outro", "lane": "bookend", "proof_gate": "SHOW",
         "narration_text": f"{TITLE}. By {NAME}.", "estimated_duration_s": 5.0, "voice": VOICE, "engine": "kokoro",
         "shot": {"type": "REMOTION", "source": "own", "show": [{"at": 0.0, "event": "title restates; handle"}],
                  "remotion": {"pattern": "ClaudeTitleOutro",
                               "props": {"title": TITLE, "slug": SLUG, "handle": HANDLE, "subline": ""}}},
         "kind": "outro_voice", "tail_silence_s": 1.0}


def build():
    beats = [OPEN] + BODY + [OUTRO]
    return {
        "metadata": {
            "slug": SLUG, "title": TITLE, "topic": "INFO 7375 · FINAL PROJECT PITCH",
            "skill": "show-tell", "style_preset": "show-tell",
            "channel": "student-pitch", "channel_title": HANDLE, "persona": NAME,
            "voice": VOICE, "voice_kokoro": VOICE, "engine": "kokoro",
            "clock": "narration", "palette": "claude", "fps": 24, "aspect_ratio": "16:9",
            "width": 3840, "height": 2160, "caption_policy": "none",
            "bookend_exempt": ["cold-open", "bvdt", "bhtf"],
            "bookend_exempt_reason": ("Student pitch for INFO 7375, 2-4 minute limit: opens on the hesitant writer, "
                                      "no terms card, no verdict card, no Your Turn composer; the spoken outro stays."),
            "audience": "hiring managers for supply chain manager roles; INFO 7375 reviewers",
            "source_doc": "PROJECT-BRIEF.md and reports/ in this repository (run 2026-10-14)",
            "purpose": "Final project pitch: what StopLine is, what exists, what will exist, and the risk.",
            "playlist": "INFO 7375 Final Project", "chapter_number": 0,
            "tags": ["StopLine", "quality incidents", "verification", "evaluation", "supply chain", "INFO 7375"],
            "estimated_total_s": round(sum(b["estimated_duration_s"] for b in beats), 1),
        },
        "beats": beats,
    }


def unfilled(sheet):
    return sorted(set(re.findall(r"\[FILL[^\]]*\]", json.dumps(sheet))))


if __name__ == "__main__":
    sheet = build()
    missing = unfilled(sheet)
    if "--final" in sys.argv and missing:
        print(f"refusing: {len(missing)} [FILL] markers remain:", *missing, sep="\n  ")
        sys.exit(1)
    REEL.mkdir(exist_ok=True)
    text = json.dumps(sheet, indent=2, ensure_ascii=False) + "\n"
    for out in (REEL / "beat_sheet.json", ROOT_COPY):
        with open(out, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
    print(f"wrote film/reel/beat_sheet.json and beat_sheet.json: {len(sheet['beats'])} beats, "
          f"~{sheet['metadata']['estimated_total_s']}s; {len(missing)} [FILL] markers remain")
