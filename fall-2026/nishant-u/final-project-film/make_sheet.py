#!/usr/bin/env python3
"""make_sheet.py — beat_sheet.json for final-project-pitch-nishant-u.

Show-tell format (brutalist.art skills/make/show-tell/, schema from
reference/example-make_sheet.py) without the persona: Nishant narrates in the
first person, Kokoro am_michael throughout; no Liam/Bear greeting, no channel,
no BHTF Your Turn, no BOUT (ClaudeTitleOutro hard-codes @NikBearBrown). The film
closes on a drawn Manim beat, BEND.

Facts: PROJECT-BRIEF.md only. Past tense only for the "Exists today" list;
"will" for everything else. Nothing of the agent exists yet, so every picture
of its output carries an on-screen "constructed" label.

Narration lives in NARRATION below; edit it there and re-run this script.
Spelled for Kokoro: "H one B", "careery dot pro", "read-me".
"""
import json
from pathlib import Path
HERE = Path(__file__).resolve().parent
SLUG = "final-project-pitch-nishant-u"
TITLE = "A job-search agent that shows its evidence"
VOICE = "am_michael"

NARRATION = {
 "BIDEA": "Hi, I'm Nee-shaant. I lost hours reading job postings that turned out to be a bad fit, or that never mentioned sponsorship. So the real question was which postings are worth my time.",
 "BDEFS": "Three terms. Two verdicts: a rule verdict anyone can recompute, kept beside Claude's judgment. "
          "Evidence labels: a claim will be supported only when the posting says it, and insufficient when "
          "it is silent. Human gate: I will approve the shortlist.",
 "B00":   "I will build a job-search agent. It will watch public job boards at retail and e-commerce "
          "companies, and tell a fictional international data-analytics graduate which new postings are "
          "worth their time.",
 "B01":   "Every verdict will cite the posting text and resume field behind it. It will never apply or "
          "send anything. The repo will hold a Python agent, tests, an evaluation log, a ten-document "
          "evidence packet, and a five-minute demo.",
 "B02":   "I looked at two tools I had used. LinkedIn Job Alerts emailed me postings that matched a saved "
          "search, but never told me why a job fit me, or whether it mentioned sponsorship.",
 "B03":   "Jobright went further: a match score, an H one B filter, and an agent that could submit applications. But a 2026 careery dot pro review said its filter used sponsorship language or past sponsorship history, which doesn't guarantee this job will sponsor.",
 "B04":   "Mine will differ in three ways. It will judge each posting by its own text, and quote the line. "
          "When a posting is silent, it will say insufficient instead of guessing. And it will never apply. "
          "I will approve the shortlist.",
 "B05":   "A hiring manager for data analyst, data scientist, or analytics engineer roles will open the read-me and run one command on saved board data. In sixty seconds they will see the shortlist with citations, skipped postings with reasons, and the scorecard.",
 "B06":   "It will prove prompt contracts with a validator, and a rule verdict beside Claude's judgment. "
          "An agent loop with budgets, exits, and a stop that doesn't rely on the model. Permissions in "
          "code, versioned memory, and a human gate tied to the exact shortlist.",
 "B07":   "The evidence will be tests, a held-out evaluation with at least five deliberate failure cases, "
          "a controlled failure I will predict and then trigger, and a stranger's run of the read-me.",
 "B08":   "It will never apply, email, message, or log in, and it won't scrape LinkedIn. First: one public board and one fictional resume. The first run will be a baseline with zero new postings. The proof: the saved raw board response and the state file.",
 "B09":   "The risk: many postings never state sponsorship or pay, so the agent could look confident with "
          "nothing behind it. The fix will be an insufficient label, an abstention rule, and measuring how "
          "often it abstains.",
 "B10":   "Why this project? Showing off and learning. I bring Python, SQL, and data analysis from almost two years as a Data Analyst at Deloitte, and a co-op at Wayfair. New to me will be agent loops with budgets, permissions in code, an MCP server from scratch, and an evaluation that can say no.",
 "B11":   "What exists today? My Brutalist setup from Week 1, my Week 1 film, pull request ten, and my Reallocation Engine recipe and prototype, pull request seventeen, marked draft. Nothing of the agent exists yet.",
 "BEND":  "I will graduate in December, and I'm looking for a job right now. My real resume will stay private; the agent will run on a fictional persona. I'm Nee-shaant, and this is the agent I will build.",
}

SPARSE_REASON = ("show-tell style: one drawn object or scene on a cream stage per beat, minimal labels, "
                 "with the voice carrying the explanation. Only underfill and clustered are waived; "
                 "edge-bleed, empty-frame and contrast still apply.")

def est(bid):
    return round(len(NARRATION[bid].split()) / 2.5, 1)

def beat(bid, cls, image, labels, show, constructed=False):
    assert 1 <= len(labels) <= 3, f"{bid}: 1-3 labels per beat"
    if constructed:
        assert "constructed" in labels, f"{bid}: constructed picture needs the label"
    return {"beat_id": bid, "act": "show-tell", "lane": "manim", "proof_gate": "SHOW",
            "narration_text": NARRATION[bid], "estimated_duration_s": est(bid),
            "voice": VOICE, "engine": "kokoro",
            "shot": {"type": "GRAPHIC", "source": "own", "visual_intent": image, "show": show,
                     "manim": {"class": cls}, "motion_claim": image,
                     "labels": labels, "constructed": constructed},
            "qc": {"sparse_by_design": True, "sparse_reason": SPARSE_REASON}}

def remotion(bid, act, pattern, props, show, gate="SHOW", **extra):
    b = {"beat_id": bid, "act": act, "lane": "bookend", "proof_gate": gate,
         "narration_text": NARRATION[bid], "estimated_duration_s": est(bid),
         "voice": VOICE, "engine": "kokoro",
         "shot": {"type": "REMOTION", "source": "own", "show": show, "remotion": {"pattern": pattern, "props": props}}}
    b.update(extra)
    return b

OPEN = [
 remotion("BIDEA", "the question", "BrutalistHesitantWriter",
    {"text": "How do I find\nmore job postings", "triggerWords": "more job postings",
     "replacementWords": "postings worth my time",
     "fontSize": 70, "charMs": 22, "hesitateBetween": 6, "hesitateWithin": 1, "mistakeRate": 2, "jitter": 20,
     "seed": SLUG, "banner": ""},
    [{"at": 0.0, "event": "types 'How do I find more job postings'"},
     {"at": 0.65, "event": "backspaces 'more job postings' → 'postings worth my time' on the spoken correction"}],
    lead_silence_s=0.8,
    motion_claim="The writer types the naive question and corrects it to the real one: which postings are worth my time.",
    qc={"sparse_by_design": True, "sparse_reason": "Hesitant-writer bookend: the correction is the motion."}),
 remotion("BDEFS", "terms", "ClaudeDefinitions",
    {"title": "Terms In This Film",
     "terms": [{"term": "Two verdicts", "meaning": "a rule verdict anyone can recompute, beside Claude's judgment"},
               {"term": "Evidence labels", "meaning": "supported only when the posting says it; insufficient when it is silent"},
               {"term": "Human gate", "meaning": "I will approve the shortlist; nothing will be sent"}],
     "folderLabel": ""},
    [{"at": 0.12, "event": "'Two verdicts' lands"}, {"at": 0.45, "event": "'Evidence labels' lands"},
     {"at": 0.8, "event": "'Human gate' lands"}], gate="CARD",
    qc={"sparse_by_design": True, "sparse_reason": "TERMS card: three prerequisites, one line each."}),
]

B = [
 beat("B00", "B00_Agent",
      "Two generic board stacks on the left feed posting pages along a belt into a dark agent block; "
      "a fictional resume page sits beside the block; one page slides out into a small shortlist tray.",
      ["job boards", "agent", "constructed"],
      [{"at": 0.1, "event": "boards land"}, {"at": 0.3, "event": "pages ride the belt"},
       {"at": 0.6, "event": "resume page drops in"}, {"at": 0.8, "event": "one page into the tray"}],
      constructed=True),
 beat("B01", "B01_Repo",
      "The agent block sits inside an open box; parts rise out one by one: a code page, a test sheet "
      "with checks, a log page, a stack of ten thin pages, a small film frame.",
      ["GitHub repo", "evidence packet"],
      [{"at": 0.15, "event": "box opens"}, {"at": 0.45, "event": "agent, tests, log rise"},
       {"at": 0.75, "event": "ten-page packet and demo frame rise"}]),
 beat("B02", "B02_Alerts",
      "A generic envelope shape (no logo) drops postings onto the stage; a blank tag swings beside "
      "each posting where a reason would be.",
      ["LinkedIn Job Alerts", "why?"],
      [{"at": 0.2, "event": "envelope lands"}, {"at": 0.45, "event": "postings slide out"},
       {"at": 0.75, "event": "blank tags appear"}]),
 beat("B03", "B03_Jobright",
      "A generic dial-and-funnel machine (no logo): a needle swings (score), postings pass a funnel "
      "(filter); a history ledger page feeds the funnel from behind.",
      ["Jobright", "careery.pro review, 2026"],
      [{"at": 0.15, "event": "machine lands"}, {"at": 0.4, "event": "needle swings"},
       {"at": 0.7, "event": "history ledger feeds the funnel"}]),
 beat("B04", "B04_ThreeWays",
      "One posting page; a quote bracket draws around one line and a check lands (supported); "
      "a blank stretch gets an open ring (insufficient); a send arrow is stopped at a gate.",
      ["supported", "insufficient", "constructed"],
      [{"at": 0.2, "event": "quote bracket + check"}, {"at": 0.5, "event": "open ring on blank stretch"},
       {"at": 0.8, "event": "send arrow stops at the gate"}],
      constructed=True),
 beat("B05", "B05_SixtySeconds",
      "A laptop on a desk (no person); a command line types, then three trays slide out: shortlist "
      "(pages with ticks), skipped (pages with reason tags), scorecard (bar block).",
      ["shortlist", "skipped", "constructed"],
      [{"at": 0.15, "event": "laptop lands"}, {"at": 0.35, "event": "command types"},
       {"at": 0.75, "event": "three trays slide out"}],
      constructed=True),
 beat("B06", "B06_Proves",
      "The agent block on a loop track; a budget meter drains as it laps; an exit gate opens at a "
      "fixed lap and the block stops; a padlock sits on a tool port.",
      ["loop", "budget", "gate"],
      [{"at": 0.15, "event": "loop track draws"}, {"at": 0.45, "event": "meter drains per lap"},
       {"at": 0.75, "event": "exit gate opens, block stops"}]),
 beat("B07", "B07_Evidence",
      "A test sheet with checks; an evaluation sheet beside it with five marked failure rows; "
      "one ink cross lands on the predicted row.",
      ["tests", "held-out eval", "constructed"],
      [{"at": 0.2, "event": "test checks"}, {"at": 0.5, "event": "five failure rows"},
       {"at": 0.8, "event": "predicted failure marked"}],
      constructed=True),
 beat("B08", "B08_OutFirst",
      "A send arrow, an envelope and a key are struck through and set aside; one board stack and one "
      "resume page stay; a state-file page drops beside them.",
      ["out", "one board", "state file"],
      [{"at": 0.15, "event": "send, mail, key struck through"}, {"at": 0.5, "event": "one board + resume"},
       {"at": 0.8, "event": "state file drops in"}]),
 beat("B09", "B09_Risk",
      "A posting page with blank lines; a tall check grows over it with nothing under it, then is "
      "replaced by an open-ring tag; a small gauge needle rises (abstain rate).",
      ["insufficient", "abstain", "constructed"],
      [{"at": 0.2, "event": "blank posting"}, {"at": 0.45, "event": "hollow check grows"},
       {"at": 0.75, "event": "ring tag + gauge"}],
      constructed=True),
 beat("B10", "B10_Skills",
      "Two shelves: the left holds solid kraft blocks (existing skills); on the right, ghost-outlined "
      "blocks fill in one by one (new skills).",
      ["I bring", "new to me"],
      [{"at": 0.2, "event": "left shelf of solid blocks"}, {"at": 0.6, "event": "right shelf blocks fill in"}]),
 beat("B11", "B11_ExistsWill",
      "Left: three solid boxes with checks (setup, film, recipe). Right: dashed ghost outlines of the "
      "repo box and its parts from B01, unfilled.",
      ["exists today", "will exist"],
      [{"at": 0.2, "event": "three solid boxes, checks"}, {"at": 0.6, "event": "ghost outlines draw"}]),
 beat("BEND", "BEND_Close",
      "The ghost repo box from B11 settles centre stage; the name and working title land beside it.",
      ["Nishant U", "Job-search agent"],
      [{"at": 0.2, "event": "ghost box settles"}, {"at": 0.5, "event": "name and title land"}]),
]

B = OPEN + B
assert [b["beat_id"] for b in B] == list(NARRATION), "NARRATION and beats out of step"

# Carry measured audio forward, or `art run` refuses with "missing required audio" (show-tell
# gate trap 4). Only while the narration is unchanged: an edited line needs a re-voice
# (generate_audio_kokoro.py --only <BID>) before its old duration means anything.
old = {}
if (HERE / "beat_sheet.json").exists():
    old = {b["beat_id"]: b for b in json.loads((HERE / "beat_sheet.json").read_text(encoding="utf-8"))["beats"]}
for b in B:
    o = old.get(b["beat_id"], {})
    if o.get("narration_text") == b["narration_text"] and o.get("actual_duration_s"):
        b["actual_duration_s"], b["audio_file"] = o["actual_duration_s"], o.get("audio_file")
    elif o.get("actual_duration_s"):
        print(f"[sheet] {b['beat_id']}: narration changed — re-voice it before the next run")
    if b["beat_id"] == "BDEFS" and b.get("actual_duration_s"):
        b["shot"]["remotion"]["props"]["durationSeconds"] = b["actual_duration_s"]

sheet = {"metadata": {
    "slug": SLUG, "title": TITLE, "topic": "FINAL PROJECT · PITCH", "skill": "show-tell", "style_preset": "show-tell",
    "voice": VOICE, "voice_kokoro": VOICE, "engine": "kokoro",
    "clock": "narration", "palette": "claude", "fps": 24, "aspect_ratio": "16:9", "width": 3840, "height": 2160,
    "caption_policy": "none",
    "bookend_exempt": ["cold-open", "bvdt", "bhtf"],
    "bookend_exempt_reason": ("I narrate as myself (Nishant), so the persona bookends are dropped: no Liam/Bear "
                              "greeting, no composer cold open, no verdict card, no Your Turn. The ClaudeTitleOutro "
                              "(BOUT) is also dropped because its handle is hard-coded to @NikBearBrown; the film "
                              "closes on a drawn Manim beat, BEND. bookend_check.py's outro check cannot be exempted "
                              "and will fail by design."),
    "audience": "hiring managers for data analyst, data scientist, and analytics engineer roles",
    "source_doc": "PROJECT-BRIEF.md (2026-10-14)",
    "author": "Nishant U",
    "tags": ["job-search agent", "Claude", "agent loop", "evaluation", "source grounding"]},
    "beats": B}
(HERE / "beat_sheet.json").write_text(json.dumps(sheet, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
words = sum(len(t.split()) for t in NARRATION.values())
print(len(B), "beats;", words, "words; est", round(sum(b["estimated_duration_s"] for b in B)), "s")
