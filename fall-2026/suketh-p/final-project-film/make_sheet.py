#!/usr/bin/env python3
"""make_sheet.py: beat_sheet.json for fine-print-pitch, Suketh Reddy Produtoor's
INFO 7375 final-project pitch film.

Skill: brutalist.art `show-tell` (one drawn isometric picture per beat, minimal labels,
the narration carries the idea), adapted to the assignment's rules: narrated in the
first person as the student (Kokoro am_eric, the student's choice), no instructor name, persona,
handle or credit line, and every picture of something not yet built stamped
"constructed · not built" on screen.

Sources for every claim: PROJECT-BRIEF.md and FACTCHECK.md (each row points at a file).
Run: python3 make_sheet.py   (then generate audio; see BUILD-PROMPT.md)
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SLUG = "fine-print-pitch"
TITLE = "Fine Print"
VOICE = "am_eric"
HANDLE = "@sukethrp"


def beat(bid, narration, cls, image, show, status=None):
    b = {"beat_id": bid, "act": "show-tell", "lane": "manim", "proof_gate": "SHOW",
         "narration_text": narration, "estimated_duration_s": round(len(narration.split()) / 2.9, 1),
         "voice": VOICE, "engine": "kokoro",
         "shot": {"type": "GRAPHIC", "source": "own", "visual_intent": image, "show": show,
                  "manim": {"class": cls}, "motion_claim": image}}
    if status:
        b["on_screen_status"] = status
    return b


def remotion(bid, act, narration, pattern, props, show, gate="SHOW", **extra):
    b = {"beat_id": bid, "act": act, "lane": "bookend", "proof_gate": gate,
         "narration_text": narration, "estimated_duration_s": round(len(narration.split()) / 2.9, 1),
         "voice": VOICE, "engine": "kokoro",
         "shot": {"type": "REMOTION", "source": "own", "show": show,
                  "remotion": {"pattern": pattern, "props": props}}}
    b.update(extra)
    return b


REAL = "real · from my A3 work"
SKETCH = "constructed · not built"

B = [
 beat("B00",
      "Earlier this term, Claude Code and I built a recipe for the course's job-search engine, the "
      "Reallocation Engine. "
      "It checks a company's sponsor record, its past work-visa filings, at the role level. Claude wrote the "
      "code; I chose the rules "
      "and ran the checks. Its thirty-six tests still pass.",
      "B00_Recipe",
      "An evidence binder (the A3 recipe) opens; check marks land beside it as the tests are named.",
      [{"at": 0.1, "event": "binder + 'A3 recipe'"}, {"at": 0.55, "event": "cover opens"},
       {"at": 0.85, "event": "'36 tests' + checks"}], REAL),
 beat("B01",
      "Then it screened eight real postings by title and company record, for Arjun Rao, a fictional applicant "
      "with no work history on file. Read in full, six asked for two "
      "to twelve-plus years of experience, or excluded new graduates. An AI reviewer read them, Claude "
      "re-checked, and I held all eight.",
      "B01_EightPostings",
      "Eight posting pages in two rows; a scan passes over them and six get a dark marker; '6 of 8' lands; "
      "a hold bar lies across all eight.",
      [{"at": 0.1, "event": "eight pages"}, {"at": 0.4, "event": "six markers"},
       {"at": 0.85, "event": "hold across all eight"}], "real · Sep 29 review · fictional applicant"),
 beat("B02",
      "A relevant title and a sponsor record are useful signals. But the posting itself can change the "
      "decision. So I will build Fine Print: an agent that will read each posting, quote the sentence "
      "behind every requirement, and stop for my approval before anything reaches my shortlist.",
      "B02_FinePrint",
      "The inspection lamp swings over a posting page; fine-print lines lift off the page as quote slips.",
      [{"at": 0.15, "event": "page + lamp"}, {"at": 0.45, "event": "lamp focuses"},
       {"at": 0.75, "event": "quote slips lift out"}], SKETCH),
 beat("B03",
      "Every requirement it finds will need its sentence, word for word. Code will check that the "
      "sentence really is in the posting. If it isn't, the requirement gets thrown out.",
      "B03_QuoteCheck",
      "A quote slip rides through the checkpoint scanner and gets a check; a second slip fails and drops off.",
      [{"at": 0.2, "event": "scanner"}, {"at": 0.4, "event": "slip passes, check"},
       {"at": 0.8, "event": "second slip fails, drops"}], SKETCH),
 beat("B04",
      "What could sink it: a real quote, read the wrong way. Say a posting says five years preferred, and "
      "the agent records required. The quote check would still pass. So preferred, required, and "
      "either-or rules will stay apart, and anything unclear will stop at me.",
      "B04_Misread",
      "Constructed example: a slip reading '5 yrs preferred' passes the scanner with a check, but the reading "
      "'required' is ringed and the slip is turned aside to the review desk.",
      [{"at": 0.15, "event": "slip '5 yrs preferred'"}, {"at": 0.35, "event": "'required' + scanner check"},
       {"at": 0.8, "event": "turned aside to the desk"}], "constructed example"),
 beat("B05",
      "A requirement also needs the applicant's documented background beside it. I have about two and a half "
      "years at Amazon and six months at Vertex, so two years required needs a comparison, not a guess. "
      "The repo will use a fictional profile; mine stays private.",
      "B05_Background",
      "Comparison trays: the requirement in one tray, a profile card in the other; a balance line draws between them.",
      [{"at": 0.15, "event": "two trays"}, {"at": 0.5, "event": "profile slides in"},
       {"at": 0.8, "event": "'fictional profile'"}], SKETCH),
 beat("B06",
      "It will run as a loop: fetch a public posting from an allowed job board, read it, check the sponsor "
      "record, log what it found. It will stop when the list is done or the budget runs out. It will read, "
      "and never apply, email, or log in.",
      "B06_Loop",
      "A permission gate lifts for a posting (read), budget slots empty one token at a time; a crossed 'apply' stays shut.",
      [{"at": 0.2, "event": "gate lifts: read"}, {"at": 0.55, "event": "budget token spent"},
       {"at": 0.85, "event": "'never apply'"}], SKETCH),
 beat("B07",
      "That's the human gate: nothing will reach my shortlist until I approve it, and the record will keep "
      "exactly what I saw. A value the model proposed will still say source: model, and my approval will be "
      "recorded beside it, as its own field. My earlier prototype labelled those as mine.",
      "B07_Gate",
      "The approval stamp presses onto the reviewed page; a tag reads 'source: model', and a second tag 'review: approved' is added beside it; neither replaces the other.",
      [{"at": 0.2, "event": "desk + stamp"}, {"at": 0.45, "event": "'source: model' tag"},
       {"at": 0.75, "event": "'review: approved' tag added"}], SKETCH),
 beat("B08",
      "I checked graduate ML descriptions from Qualcomm and TikTok on LinkedIn. Both separate minimum and "
      "preferred qualifications; neither accessible description states sponsorship. Fine Print will preserve "
      "those distinctions, attach checked source quotes, and keep missing sponsorship evidence marked unknown.",
      "B08_Alternatives",
      "Left: the two LinkedIn postings, each split into minimum and preferred blocks, with an empty sponsorship slot (real, my check). Right: Fine Print's report with quote slips and one slip flagged unknown (sketch).",
      [{"at": 0.15, "event": "two postings"}, {"at": 0.35, "event": "minimum / preferred blocks"},
       {"at": 0.55, "event": "empty sponsorship slot"}, {"at": 0.75, "event": "Fine Print report + unknown"}], None),
 beat("B09",
      "Who opens it? A hiring manager or an ML engineer. In the first minute, they'll run one command with "
      "no API key, which replays recorded model outputs, and read the report: each posting, each requirement "
      "beside its sentence, and my decision.",
      "B09_FirstMinute",
      "A release parcel (the repository) opens and a report page slides out with three quote rows.",
      [{"at": 0.2, "event": "parcel"}, {"at": 0.5, "event": "lid opens"}, {"at": 0.75, "event": "report rows"}], SKETCH),
 beat("B10",
      "It should prove I can build an agent whose claims can be checked. I'll label real postings by hand, "
      "set a held-out group aside before tuning, and count two mistakes separately: clearing a posting I "
      "don't qualify for, and excluding one I do.",
      "B10_Evaluation",
      "The experiment bench: a sample goes into the held-out slot and stays; two tally marks start under two error names.",
      [{"at": 0.2, "event": "bench"}, {"at": 0.45, "event": "held-out sample sealed"},
       {"at": 0.8, "event": "two error counts"}], SKETCH),
 beat("B11",
      "It will never apply for me. The first piece will be one loop over one public posting, with the "
      "quote check, and a test that fails if a quote changes by a single word.",
      "B11_FirstSlice",
      "The task queue hands over one task (one posting); a test light goes from check to cross when one word changes.",
      [{"at": 0.25, "event": "one task taken"}, {"at": 0.75, "event": "one-word change fails"}], SKETCH),
 beat("B12",
      "Why this project? It's a mix. I already have production ML from Amazon, data checks with human "
      "sign-off from Vertex, and AgentOS, my open-source project with budget limits and a kill switch. New "
      "to me: reading a requirement without changing what it means, and testing extraction and interpretation "
      "separately.",
      "B12_Skills",
      "A stack of skill pages ('have'); one new blank page arrives beside it ('new').",
      [{"at": 0.2, "event": "'have' stack"}, {"at": 0.7, "event": "'new' page arrives"}], None),
 beat("B13",
      "Today there's the recipe, its passing tests, the eight-posting finding, and an open pull request. "
      "Not yet: the agent, the quote check, the evaluation. Those I will build.",
      "B13_ExistsWill",
      "Two places: the binder (exists) fills with pages; the closed crate (not yet) stays taped.",
      [{"at": 0.2, "event": "'exists' binder fills"}, {"at": 0.65, "event": "'not yet' crate"}], None),
]

OPEN = [
 remotion("BIDEA", "the question",
    "Hi, I'm Suketh Produtoor. I'm an international student on F-1, looking for new-grad machine learning "
    "roles. The question isn't only whether a company sponsors. It's whether the posting even fits me.",
    "BrutalistHesitantWriter",
    {"text": "Will this company sponsor me", "triggerWords": "company sponsor me",
     "replacementWords": "posting even fit me", "fontSize": 72, "charMs": 22, "hesitateBetween": 6,
     "hesitateWithin": 1, "mistakeRate": 2, "jitter": 20, "seed": SLUG, "banner": ""},
    [{"at": 0.0, "event": "types 'Will this company sponsor me'"},
     {"at": 0.6, "event": "backspaces 'company sponsor me' -> 'posting even fit me'"}],
    lead_silence_s=0.8,
    motion_claim="The writer types the company-level question and corrects it to the posting-level one.",
    qc={"sparse_by_design": True, "sparse_reason": "Hesitant-writer bookend: the correction is the motion."}),
]

SPARSE_REASON = ("show-tell style: one drawn object or scene on a cream stage per beat, minimal labels, with the "
                 "voice carrying the explanation. The negative space is the style, so only underfill and "
                 "clustered are waived; edge-bleed, empty-frame and contrast still apply.")
for b in B:
    b["qc"] = {"sparse_by_design": True, "sparse_reason": SPARSE_REASON}

BEATS = OPEN + B
# BOUT is a drawn Manim beat, not the toolkit's ClaudeTitleOutro: that component hard-codes the handle
# "@NikBearBrown" (no prop overrides it), and the assignment forbids the instructor's credit line.
BEATS.append({"beat_id": "BOUT", "act": "outro", "lane": "manim", "proof_gate": "SHOW",
              "narration_text": f"{TITLE}. Suketh Reddy Produtoor.", "estimated_duration_s": 3.0,
              "voice": VOICE, "engine": "kokoro",
              "shot": {"type": "GRAPHIC", "source": "own", "manim": {"class": "BOUT_Outro"},
                       "visual_intent": "The title and my name beside the inspection lamp; a landing shadow.",
                       "motion_claim": "The title and my name beside the inspection lamp; a landing shadow.",
                       "show": [{"at": 0.0, "event": "title"}, {"at": 0.2, "event": "my name"}]},
              "kind": "outro_voice", "tail_silence_s": 1.0,
              "qc": {"sparse_by_design": True, "sparse_reason": SPARSE_REASON}})

sheet = {"metadata": {
    "slug": SLUG, "title": TITLE, "topic": "FINAL PROJECT PITCH", "skill": "show-tell", "style_preset": "show-tell",
    "channel": "suketh-p", "persona": "Suketh Reddy Produtoor (first person)", "voice": VOICE, "voice_kokoro": VOICE,
    "engine": "kokoro", "clock": "narration", "palette": "claude", "register": "Plain", "fps": 24,
    "aspect_ratio": "16:9", "width": 3840, "height": 2160, "caption_policy": "none",
    "bookend_exempt": ["cold-open", "bvdt", "bdefs", "bhtf"],
    "bookend_exempt_reason": ("Course pitch film, not a channel episode (INFO 7375 Final Project Pitch Film, "
                              "2-4 min): it opens on the hesitant writer, has no verdict card, "
                              "and drops the Your Turn composer to keep the runtime under four minutes. The terms card is "
                              "dropped too: GATE T measured its fixed-size definition text at 40 px, under the 41 px "
                              "floor, so each term is defined in the narration where it is first used (show-tell law 3). The spoken "
                              "outro stays but is our own drawn beat with the student's name: the toolkit's ClaudeTitleOutro "
                              "hard-codes the handle @NikBearBrown, and the assignment says to narrate as yourself and "
                              "not to use the instructor's name, persona or credit line."),
    "audience": "a hiring manager or ML engineer reviewing a new-grad ML/AI engineer's portfolio; the course TAs",
    "source_doc": "PROJECT-BRIEF.md; Assignment 3 record (sukethrp/the-reallocation-engine @ 95d4982); evidence/",
    "playlist": "INFO 7375 final project", "chapter_number": 0,
    "tags": ["INFO 7375", "final project pitch", "agents", "job postings", "F-1", "quote check", "human gate"]},
    "beats": BEATS}

old = HERE / "beat_sheet.json"
if old.exists():                                    # keep measured audio for any beat whose words did not change
    prev = {b["beat_id"]: b for b in json.loads(old.read_text())["beats"]}
    for b in BEATS:
        o = prev.get(b["beat_id"])
        if o and o.get("narration_text") == b["narration_text"] and o.get("audio_file"):
            b["audio_file"], b["actual_duration_s"] = o["audio_file"], o.get("actual_duration_s")
            if "remotion" in b["shot"] and "durationSeconds" in o["shot"].get("remotion", {}).get("props", {}):
                b["shot"]["remotion"]["props"]["durationSeconds"] = o["shot"]["remotion"]["props"]["durationSeconds"]
(HERE / "beat_sheet.json").write_text(json.dumps(sheet, indent=2, ensure_ascii=False) + "\n")
words = sum(len(b["narration_text"].split()) for b in BEATS)
print(len(BEATS), "beats;", words, "words; est", round(sum(b["estimated_duration_s"] for b in BEATS)), "s")
