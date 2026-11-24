#!/usr/bin/env python3
"""make_sheet.py — beat_sheet.json for coop-sponsor-check-final.

INFO 7375 Final Project Film (four parts: summary, what others did, methods, evaluation) by Arundhati Kandelkar. Built with the brutalist.art
`show-tell` skill: one drawn picture per beat, minimal labels, the voice explains.

Assignment overrides of the skill's house defaults (the assignment governs):
  - narrated in my name, not "Liam, in for Bear"; voice Kokoro bf_emma (my choice, 2026-10-12)
  - no instructor name, persona, handle or portrait anywhere; outro shows my name
Tense rule: past tense = exists and is in evidence/; everything else = "will".
Every body beat carries an on-screen tag: EXISTS (with its evidence) or PLANNED / CONSTRUCTED.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SLUG = "coop-sponsor-check-final"
TITLE = "Co-op Sponsor Check"
VOICE = "bf_emma"
NAME = "Arundhati Kandelkar"


def est(n):
    return round(len(n.split()) / 2.5, 1)


def beat(bid, narration, cls, image, show):
    return {"beat_id": bid, "act": "show-tell", "lane": "manim", "proof_gate": "SHOW",
            "narration_text": narration, "estimated_duration_s": est(narration),
            "voice": VOICE, "engine": "kokoro",
            "shot": {"type": "GRAPHIC", "source": "own", "visual_intent": image, "show": show,
                     "manim": {"class": cls}, "motion_claim": image}}


def remotion(bid, act, narration, pattern, props, show, gate="SHOW", **extra):
    b = {"beat_id": bid, "act": act, "lane": "bookend", "proof_gate": gate,
         "narration_text": narration, "estimated_duration_s": est(narration),
         "voice": VOICE, "engine": "kokoro",
         "shot": {"type": "REMOTION", "source": "own", "show": show,
                  "remotion": {"pattern": pattern, "props": props}}}
    b.update(extra)
    return b


OPEN = [
 remotion("BNAME", "who",
    f"Hello. I'm {NAME}, a master's student at Northeastern.",
    "BrutalistHesitantWriter",
    {"text": "Arundhati Kandelkar\nMSIS, Northeastern University", "triggerWords": "", "replacementWords": "",
     "fontSize": 72, "charMs": 22, "hesitateBetween": 2, "hesitateWithin": 0, "mistakeRate": 0, "jitter": 10,
     "seed": SLUG + "-name", "banner": ""},
    [{"at": 0.0, "event": "my name types"}],
    lead_silence_s=0.5, motion_claim="My name and programme type in while I say them.",
    qc={"sparse_by_design": True, "sparse_reason": "Name card: the name is the whole picture."}),
 remotion("BBUILD", "what",
    "I'm building Co-op Sponsor Check: a tool that tells international students whether a company has ever sponsored someone for a software job.",
    "BrutalistHesitantWriter",
    {"text": "I'm building Co-op Sponsor Check", "triggerWords": "", "replacementWords": "",
     "fontSize": 72, "charMs": 18, "hesitateBetween": 0, "hesitateWithin": 0, "mistakeRate": 0, "jitter": 8,
     "seed": SLUG + "-build", "banner": ""},
    [{"at": 0.0, "event": "types 'I'm building Co-op Sponsor Check' as it is spoken"}],
    motion_claim="The one-sentence summary types in as it is spoken.",
    qc={"sparse_by_design": True, "sparse_reason": "One-sentence summary card."}),
 remotion("BIDEA", "the question",
    "When international students like me pick an internship, we need to know one thing: has this company ever sponsored someone for a software job? "
    "Today we guess, and a missing record looks like a no. My tool says I don't know, instead of guessing no.",
    "BrutalistHesitantWriter",
    {"text": "Does this company sponsor visas", "triggerWords": "sponsor visas",
     "replacementWords": "have a record of sponsoring software jobs",
     "fontSize": 64, "charMs": 22, "hesitateBetween": 6, "hesitateWithin": 1, "mistakeRate": 2, "jitter": 20,
     "seed": SLUG, "banner": ""},
    [{"at": 0.0, "event": "types the naive question"}, {"at": 0.5, "event": "corrects 'sponsor visas' to the narrower question"}],
    motion_claim="The naive question is corrected to the one a tool can answer.",
    qc={"sparse_by_design": True, "sparse_reason": "Hesitant-writer bookend: the correction is the motion."}),
]

def card(bid, act, narration, text):
    return remotion(bid, act, narration, "BrutalistHesitantWriter",
        {"text": text, "triggerWords": "", "replacementWords": "", "fontSize": 96, "charMs": 6,
         "hesitateBetween": 0, "hesitateWithin": 0, "mistakeRate": 0, "jitter": 8, "seed": SLUG + "-" + bid.lower(), "banner": ""},
        [{"at": 0.0, "event": "part title types"}], motion_claim="Part title types in as it is spoken.",
        lead_silence_s=0.3, tail_silence_s=0.8,
        qc={"sparse_by_design": True, "sparse_reason": "Part title card: the structure the assignment asks for."})


def part(n, b):
    b["part"] = n
    return b


B = [
 # ── PART 1 · Executive summary (no "how") ──
 beat("BWHAT", "When it's done, it will be a public GitHub repository: the tool, a twenty-five company evaluation set, and a log of where it fails.",
      "BWHAT_Repo", "A repository folder tray holding three things: the company box (the tool), a small grid (the evaluation set), a page (the failure log); tag 'PLANNED · finished form'.",
      [{"at": 0.15, "event": "repo tray"}, {"at": 0.3, "event": "three parts drop in"}, {"at": 0.62, "event": "folder tab"}]),
 # ── PART 2 · What others have done ──
 card("P2", "part 2", "Part two. What already exists?", "2 · What already exists"),
 beat("B05", "The official source is the U S C I S, H-1B Employer Data Hub. When I searched it for Capital One, it listed two employers, Capital One National Association, and Capital One Services. My dataset has neither. "
      "But the hub is searched one employer at a time, and it has no job-title filter.",
      "B05_Hub", "A search window with the query 'Capital One' and the two employer names the hub listed; beside it a 'job title' filter pill gets crossed out; tag 'MY SEARCH · uscis.gov · 2026-10-25'.",
      [{"at": 0.15, "event": "search window + two rows"}, {"at": 0.62, "event": "job-title pill crossed out"}]),
 beat("BOS", "I also searched Open Sanctions, a database for sanctions and risk screening, for Robinhood, Chime, and So Fi. "
      "Chime returned eleven results, mostly unrelated people, and Chime Financial was not among the ones I reviewed. It shows how a brand-name search returns related or irrelevant matches.",
      "BOS_OpenSanctions", "A search window with the query 'Chime' and a column of eleven result rows, mostly greyed person rows; a crossed-out 'Chime Financial Inc' label beside it; tag 'MY SEARCH · opensanctions.org'.",
      [{"at": 0.15, "event": "query + eleven rows"}, {"at": 0.62, "event": "'Chime Financial Inc' crossed: not in the results"}]),
 beat("BGL", "Then G L E I F, the global register of legal entity identifiers. It connected brand names to legal names: Robinhood to Robinhood Markets, "
      "and So Fi to Social Finance, L L C, which was once Social Finance, Inc.",
      "BGL_Gleif", "Two brand tags on the left, arrows to the legal names GLEIF listed on the right: ROBINHOOD MARKETS, INC. and SOCIAL FINANCE, LLC with 'previously SOCIAL FINANCE, INC.'; tag 'MY SEARCH · gleif.org'.",
      [{"at": 0.15, "event": "Robinhood → ROBINHOOD MARKETS, INC."}, {"at": 0.3, "event": "SoFi → SOCIAL FINANCE, LLC"}, {"at": 0.62, "event": "previous legal name"}]),
 beat("BCARE", "But neither tool is built to find employers that sponsor H-1B visas. Finding them takes time, especially when a company's brand name is different from its legal name in the data. "
      "My tool brings that information together, finds possible name variations, and lets you verify the result, instead of blindly trusting an automatic match.",
      "BCARE_Why", "One brand tag 'Chime' with lines to two legal-name tags; a 'you verify' check box lands between them.",
      [{"at": 0.2, "event": "brand tag and two legal names"}, {"at": 0.62, "event": "you-verify box and check"}]),
 # ── PART 3 · Methods ──
 card("P3", "part 3", "Part three. How I'm building it.", "3 · How I'm building it"),
 beat("B00", "Here is what exists today. On October third I pushed a recipe to my fork of the Reallocation Engine. "
      "It takes a company and the job I want, software or full-stack development.",
      "B00_Arrives", "A kraft company box drops onto the stage beside a flat data page; tag 'EXISTS · 03784b0'.",
      [{"at": 0.1, "event": "box drops in"}, {"at": 0.6, "event": "tag"}]),
 beat("B01", "For each company it checks three things. Is there a record of sponsoring software titles? "
      "Does the co-op start before graduation? And is the job posting still live?",
      "B01_Three", "The box opens; a record page, a calendar block and a check rise out of it, one per question.",
      [{"at": 0.15, "event": "record page"}, {"at": 0.35, "event": "calendar"}, {"at": 0.62, "event": "live check"}]),
 beat("B02", "When a company is missing from the data, it does not treat that as zero. "
      "It says unknown, and tells you to ask a person.",
      "B02_Unknown", "A box rides up to a gate; the gate shows a question mark, never a zero.",
      [{"at": 0.2, "event": "box rides to gate"}, {"at": 0.62, "event": "question mark"}]),
 beat("B03", "The data comes from a public dataset built from a list of funded startups taken from S E C filings. That is its biggest limit: the big banks are not in it at all.",
      "B03_Gap", "A data page with a gap; three bank boxes drop toward it and pass through the gap.",
      [{"at": 0.2, "event": "page with gap"}, {"at": 0.35, "event": "three boxes fall through"}]),
 beat("BFIX", "Today I fixed brand names. If what you type is the first word of a company's name, like Chime, the tool now lists Chime Financial and Chime Inc. "
      "If the legal name shares no word, like So Fi, a short alias list I wrote points to Social Finance. Either way a person picks. Twenty-six tests pass.",
      "BFIX_Brand", "Typed 'Chime' fans out to two rows; typed 'SoFi' goes through an alias arrow to 'SOCIAL FINANCE INC'; a 'human check' box lands; tag 'BUILT · 2026-11-23 · 26 tests'.",
      [{"at": 0.15, "event": "Chime → two rows"}, {"at": 0.35, "event": "SoFi → alias → SOCIAL FINANCE INC"}, {"at": 0.62, "event": "human check"}]),
 beat("B06", "Next, the official hub becomes a second data source, so a missing bank becomes a real answer or an honest unknown. "
      "Then a written failure analysis, and a README with a one-command demo.",
      "B06_Second", "A second page slides under the gapped page and fills the hole; tag 'PLANNED'.",
      [{"at": 0.2, "event": "second page slides in"}, {"at": 0.62, "event": "gap filled"}]),
 beat("BRES", "What do I need? My laptop, Python, GitHub, and the public data, including the U S C I S employer data. "
      "I may use Claude Code to help me build it, but the lookup itself is plain Python, with no AI model at run time, so it stays predictable.",
      "BRES_Need", "Four small objects in a row — laptop, Python page, GitHub folder tray, data page — and a 'no AI model at run time' pill; tag 'WHAT I NEED'.",
      [{"at": 0.15, "event": "four objects"}, {"at": 0.62, "event": "no-model pill"}]),
 beat("B09", "One thing it will deliberately not do: give immigration advice, or predict whether anyone gets a visa. It reports history.",
      "B09_Out", "A stop sign beside the box; three small label tags clip onto the box.",
      [{"at": 0.2, "event": "stop sign"}, {"at": 0.62, "event": "three label tags"}]),
 # ── PART 4 · Evaluation ──
 card("P4", "part 4", "Part four. How will I know it worked?", "4 · How I'll know it worked"),
 beat("B07", "I test it on twenty-five companies. Every company I looked up in the official hub was there. In October my tool found a record for only two. "
      "It never guessed no. But that number told me something was wrong.",
      "B07_Eval", "A grid of twenty-five company squares; all fill grey and rows land in the results table; two get terracotta dots; tag '25 RAN · 2026-10-12 / 10-25'.",
      [{"at": 0.15, "event": "grid"}, {"at": 0.3, "event": "rows land"}, {"at": 0.62, "event": "two found"}]),
 beat("B07A", "Two real problems. First, my matcher turned Goldman Sachs and Co, L L C, into Goldman Sachs and. "
      "It is fixed now, with a test that failed before the fix and passes after.",
      "B07A_Bug", "The hub's name 'GOLDMAN SACHS AND CO LLC', an arrow, and the matcher's output 'GOLDMAN SACHS' with a tick; tag 'FIXED · 2026-10-24'.",
      [{"at": 0.15, "event": "hub name"}, {"at": 0.3, "event": "arrow and fixed output"}, {"at": 0.62, "event": "tick"}]),
 beat("BAFTER", "Second, brand names: Robinhood, Chime and So Fi were missed. Before fixing it, I predicted the first-word rule would catch two, and So Fi would need the alias. That is what happened. "
      "Now none of the three is missed, six of the twenty-five go to a person, and there are no wrong automatic answers.",
      "BAFTER_Result", "A before/after table with three rows: missed strong sponsors 3 → 0, wrong automatic answers 1 → 0, sent to a person 0 → 6; tag 'MEASURED · 2026-11-23 · predictions first'.",
      [{"at": 0.15, "event": "table and before column"}, {"at": 0.62, "event": "after column lands"}]),
 beat("BBAR", "After I add the hub, it passes if it finds known sponsors from both sources, even when brand and legal names differ, shows which source supports each result, and leaves the choice to a person. "
      "It fails if it misses employers that are in the data, confirms a wrong company, picks one on its own, or if the second source does not improve coverage.",
      "BBAR_PassFail", "Two columns, PASS and FAIL, each with a short list; ticks land down PASS, crosses down FAIL; tag 'MY PASS / FAIL BAR · next test'.",
      [{"at": 0.15, "event": "PASS column"}, {"at": 0.62, "event": "FAIL column"}]),
]
PARTS = {"BWHAT": 1, "P2": 2, "B05": 2, "BOS": 2, "BGL": 2, "BCARE": 2, "P3": 3, "B00": 3, "B01": 3, "B02": 3, "B03": 3,
         "BFIX": 3, "B06": 3, "BRES": 3, "B09": 3, "P4": 4, "B07": 4, "B07A": 4, "BAFTER": 4, "BBAR": 4}

YT_PROMPT = ("List every legal name [company] might file U.S. work-visa paperwork under. Mark the ones you are not sure of.")
YOURTURN = remotion("BHTF", "your turn",
    "Your turn. Paste this into Claude: " + YT_PROMPT.replace("[company]", "a company you choose").replace("U.S. work-visa", "United States work visa") +
    " Then look each name up in the U S C I S hub, and count the ones that were wrong.",
    "ClaudeComposerAsk",
    {"greeting": "Your turn.", "topic": "CLAUDE · YOUR TURN", "segment": "Check One Company", "command": YT_PROMPT,
     "runningText": "paste this into Claude…",
     "output": ["Check: look each name up in the USCIS H-1B Employer Data Hub.",
                "Check: count the names that were wrong or made up."],
     "folderLabel": NAME, "modelLabel": "Opus 5.5", "effortLabel": "High"},
    [{"at": 0.0, "event": "Composer opens — 'Your turn.'"}, {"at": 0.1, "event": "the prompt types in full"},
     {"at": 0.8, "event": "two check lines land"}])

SPARSE_REASON = ("show-tell style: one drawn object or scene on a cream stage per beat, minimal labels, the voice "
                 "carrying the explanation. Only underfill and clustered are waived; edge-bleed, empty-frame and contrast still apply.")
for b in B:
    if b["lane"] == "manim":
        b["qc"] = {"sparse_by_design": True, "sparse_reason": SPARSE_REASON}

BEATS = OPEN + B
for b in OPEN:
    b["part"] = 1
for b in B:
    b["part"] = PARTS[b["beat_id"]]
BEATS.append({"beat_id": "BOUT", "act": "outro", "lane": "bookend", "proof_gate": "SHOW",
              "narration_text": f"{TITLE}. Made by {NAME}.", "estimated_duration_s": 4.0,
              "voice": VOICE, "engine": "kokoro",
              "shot": {"type": "REMOTION", "source": "own", "show": [{"at": 0.0, "event": "title; my name"}],
                       "remotion": {"pattern": "ClaudeTitleOutro",
                                    "props": {"title": TITLE, "slug": SLUG, "handle": NAME, "subline": ""}}},
              "kind": "outro_voice", "tail_silence_s": 1.0})

# carry measured audio forward across regenerations (SKILL.md card trap 4)
old = {}
if (HERE / "beat_sheet.json").exists():
    for b in json.loads((HERE / "beat_sheet.json").read_text()).get("beats", []):
        old[b["beat_id"]] = b
for b in BEATS:
    o = old.get(b["beat_id"])
    if o and o.get("narration_text") == b["narration_text"]:
        for k in ("actual_duration_s", "audio_file"):
            if k in o:
                b[k] = o[k]
        if b["shot"].get("remotion") and "actual_duration_s" in b:
            b["shot"]["remotion"]["props"]["durationSeconds"] = round(b["actual_duration_s"], 2)

sheet = {"metadata": {
    "slug": SLUG, "title": TITLE, "topic": "INFO 7375 · FINAL PROJECT FILM", "skill": "show-tell", "style_preset": "show-tell",
    "channel": "info7375-student", "channel_title": NAME, "persona": NAME, "voice": VOICE, "voice_kokoro": VOICE,
    "engine": "kokoro", "clock": "narration", "palette": "claude", "register": "Teardown", "fps": 24,
    "aspect_ratio": "16:9", "width": 3840, "height": 2160, "caption_policy": "none",
    "bookend_exempt": ["cold-open", "bvdt", "bhtf"],
    "bookend_exempt_reason": "No Your Turn: the assignment fixes four parts in order. Opens on the hesitant writer; spoken outro shows the student's name.",
    "audience": "INFO 7375 instructor and TAs; later, hiring managers for software developer roles",
    "source_doc": "fall-2026/arundhati-k/final-film (PREDICTIONS.md, MY-SEARCHES.md, evidence/eval-after-fix-2026-11-23.md); fork branch final/arundhatik26-and-fix",
    "playlist": "INFO 7375 Final Project", "chapter_number": 0,
    "tags": ["INFO 7375", "final project", "H-1B", "co-op", "evaluation"]},
    "beats": BEATS}
(HERE / "beat_sheet.json").write_text(json.dumps(sheet, indent=2, ensure_ascii=False) + "\n")
print(len(BEATS), "beats; est", round(sum(b["estimated_duration_s"] for b in BEATS)), "s")
