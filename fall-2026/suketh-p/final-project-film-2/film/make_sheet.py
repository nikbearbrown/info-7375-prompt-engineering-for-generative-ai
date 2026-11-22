#!/usr/bin/env python3
"""make_sheet.py: beat_sheet.json for fine-print-film, Suketh Reddy Produtoor's INFO 7375 Final Project Film.

Drafted by Claude Code on 2026-11-21 from the records listed in ../FACTCHECK.md. DRAFT until the student approves
the script (../SCRIPT.md is generated from this file for that review).

Skill: brutalist.art `show-tell` at 519fcbb (one drawn picture per beat, minimal labels, the narration carries the
idea), adapted as in October's pitch film: first person as the student (Kokoro am_eric, the student's choice), no
instructor name, persona, handle or credit line. Every beat carries a part tag (top right) and an honesty stamp
(top left): "real · ..." for what ran or was checked, "constructed · not built" for the plan.

The four parts follow the instructor's brief (../ASSIGNMENT-BRIEF.md): what and why; what exists; how; did it work.
Run: python3 make_sheet.py   (then build_audio.sh; see ../PLAN.md)
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SLUG = "fine-print-film"
TITLE = "Fine Print"
VOICE = "am_eric"

P1, P2, P3, P4 = "1 · What and why", "2 · What exists", "3 · How", "4 · Did it work?"
CONSTRUCTED = "constructed · not built"


def beat(bid, part, narration, cls, image, show, status=None, terminal=None):
    b = {"beat_id": bid, "act": part, "lane": "manim", "proof_gate": "SHOW",
         "narration_text": narration, "estimated_duration_s": round(len(narration.split()) / 2.8, 1),
         "voice": VOICE, "engine": "kokoro", "on_screen_part": part,
         "shot": {"type": "GRAPHIC", "source": "own", "visual_intent": image, "show": show,
                  "manim": {"class": cls}, "motion_claim": image}}
    if status:
        b["on_screen_status"] = status
    if terminal:
        b["terminal_replay"] = terminal          # evidence/terminal/<name>.json files whose exact lines are shown
    return b


OPEN = [{
    "beat_id": "BIDEA", "act": P1, "lane": "bookend", "proof_gate": "SHOW", "on_screen_part": P1,
    "narration_text": ("Hi, I'm Suketh Produtoor. I'm an international student on F-1, looking for new-grad "
                       "machine learning roles. Before I tailor an application, I need to know one thing: "
                       "does this posting rule me out?"),
    "estimated_duration_s": 12.0, "voice": VOICE, "engine": "kokoro",
    "shot": {"type": "REMOTION", "source": "own",
             "show": [{"at": 0.0, "event": "types 'Will this company sponsor me'"},
                      {"at": 0.6, "event": "backspaces 'company sponsor me' -> 'posting rule me out'"}],
             "remotion": {"pattern": "BrutalistHesitantWriter",
                          "props": {"text": "Will this company sponsor me", "triggerWords": "company sponsor me",
                                    "replacementWords": "posting rule me out", "fontSize": 72, "charMs": 22,
                                    "hesitateBetween": 6, "hesitateWithin": 1, "mistakeRate": 2, "jitter": 20,
                                    "seed": SLUG, "banner": ""}}},
    "lead_silence_s": 0.8,
    "motion_claim": "The writer types October's company-level question and corrects it to the posting-level one.",
    "qc": {"sparse_by_design": True, "sparse_reason": "Hesitant-writer bookend: the correction is the motion."}}]

B = [
 # ── Part 1 · What and why (ends by 60 s) ─────────────────────────────────────────────────────────────────
 beat("B01", P1,
      "Titles can't tell me. Earlier this term, a recipe Claude Code and I built screened eight real postings for "
      "a fictional new grad, by title and sponsor record. When an AI reviewer read them in full, six asked for two "
      "to twelve-plus years of experience, or excluded new graduates.",
      "B01_EightPostings",
      "Eight posting pages in a row, each with a title line and grey text rules (no sponsor ticks: only four of the eight had a sponsor tier); a reading lens passes over them; six get an ink cross over a darkened line, two stay. Labels: '8 real postings', '6 of 8', '2–12+ yrs or no new grads'.",
      [{"at": 0.0, "event": "8 posting pages"}, {"at": 0.25, "event": "'8 real postings'"}, {"at": 0.4, "event": "title lines drawn"}, {"at": 0.55, "event": "reading lens passes"}, {"at": 0.71, "event": "6 crossed, 2 stay"}, {"at": 0.75, "event": "'6 of 8' · '2–12+ yrs or no new grads'"}],
      "real · from my A3 work · fictional applicant"),
 beat("B02", P1,
      "So I'm building Fine Print. It will read each new posting, show me the exact sentence behind every "
      "requirement that could rule me out, and wait for my approval before anything reaches my shortlist.",
      "B02_FinePrint",
      "The inspection lamp (Fine Print) lowers over a posting; a sentence slip slides out ('exact sentence'); the approval stamp arrives and stays raised ('my approval').",
      [{"at": 0.16, "event": "lamp head lowers"}, {"at": 0.28, "event": "slip · 'exact sentence'"}, {"at": 0.68, "event": "approval stamp · 'my approval'"}, {"at": 0.74, "event": "stamp stays raised"}],
      CONSTRUCTED),
 beat("B03", P1,
      "And postings keep coming. In under two weeks, the three boards I watch showed one hundred seventy-two "
      "postings that weren't in my November eighth snapshot. One piece of Fine Print already runs: the watcher. "
      "The reader is next.",
      "B03_NewPostings",
      "Three open crates (the three boards) fill with pages: two tall stacks and one page, counted 83 · 88 · 1; '172' with 'not seen on Nov 8' lands above; 'watcher: runs' under the crates; the inspection lamp, drawn faint, with 'reader: next'.",
      [{"at": 0.09, "event": "crates fill"}, {"at": 0.2, "event": "83 · 88 · 1"}, {"at": 0.32, "event": "'172 · not seen on Nov 8'"}, {"at": 0.67, "event": "'watcher: runs'"}, {"at": 0.71, "event": "faint lamp · 'reader: next'"}],
      "real · live run, Nov 21"),

 # ── Part 2 · What exists ─────────────────────────────────────────────────────────────────────────────────
 beat("B04", P2,
      "What already exists? My own first try matched on title and sponsor record, and couldn't tell fit. On "
      "LinkedIn, I checked two graduate ML postings, from Qualcomm and TikTok. Both separated minimum from "
      "preferred qualifications. Neither stated sponsorship.",
      "B04_Exists",
      "Left: the A3 binder ('A3 recipe') with a '?' beside it. Right: two LinkedIn posting pages ('Qualcomm · TikTok'), each split into a 'minimum' block and a 'preferred' block, with an empty 'sponsorship' slot.",
      [{"at": 0.29, "event": "'?' beside the A3 binder"}, {"at": 0.37, "event": "two posting pages"}, {"at": 0.58, "event": "'Qualcomm · TikTok'"}, {"at": 0.66, "event": "minimum | preferred blocks"}, {"at": 0.81, "event": "empty sponsorship slots"}],
      "real · my A3 work · my LinkedIn check, Oct 14"),
 beat("B05", P2,
      "Others have built pieces. Government H-1B data counts an employer's past approvals and denials, not what a "
      "posting asks for. Jobscan scores a résumé against a posting and lists missing keywords. One paper flags "
      "whether experience and education are required or preferred. And a 2024 study found language models find "
      "skills but miss their exact wording.",
      "B05_Others",
      "Four cards, two by two, each showing what that tool gives back, labelled in plain text beside it: 'H-1B approvals · denials · per employer' (USCIS data hub; pairs of bars), 'match score · missing keywords' (Jobscan; a meter and keyword chips, one missing), 'experience, education: required or preferred?' (2025 paper; two blocks), 'skill found · exact wording missed' (2024 study; a check and a cross). No logos.",
      [{"at": 0.06, "event": "card: H-1B approvals · denials"}, {"at": 0.34, "event": "card: match score"}, {"at": 0.54, "event": "card: required or preferred?"}, {"at": 0.76, "event": "card: skill found · wording missed"}],
      "real · sources checked Nov 21"),
 beat("B06", P2,
      "Fine Print will put those pieces together for one question: should I apply? Each requirement will carry the "
      "posting's own sentence, checked word for word by code. Required will stay apart from preferred, silence on "
      "sponsorship will mean unknown, and nothing will reach my shortlist until I approve.",
      "B06_Adds",
      "The checkpoint scanner checks a sentence slip (a check lands); two trays 'required' and 'preferred'; a grey 'sponsorship: unknown' tag; the approval stamp ('my approval') stays raised over its sheet.",
      [{"at": 0.24, "event": "sentence slip"}, {"at": 0.37, "event": "scanner pass + check"}, {"at": 0.53, "event": "required | preferred trays"}, {"at": 0.67, "event": "'sponsorship: unknown'"}, {"at": 0.82, "event": "stamp stays raised"}],
      CONSTRUCTED),

 # ── Part 3 · How ────────────────────────────────────────────────────────────────────────────────────────
 beat("B07", P3,
      "Now, how. In October I planned to build the reader first, and now I can build it on top of jobwatch, which "
      "already monitors three job boards. Its data: public job-board feeds, read only from an allow-list, each "
      "response saved with a fingerprint before anything reads it. The applicant is fictional.",
      "B07_Data",
      "The inspection lamp (the reader, October's plan; drawn faint with a grey 'plan' tag, since it is not built) lands on top of three open crates ('jobwatch', three terracotta lights for the three boards); a permission gate ('allow-list') opens for three feed slips and stops a fourth; the release parcel closes with a terracotta seal ('fingerprint'); a persona card ('fictional applicant').",
      [{"at": 0.25, "event": "lamp lands on jobwatch"}, {"at": 0.4, "event": "three board lights"}, {"at": 0.57, "event": "gate opens · 'allow-list'"}, {"at": 0.67, "event": "fourth feed stopped"}, {"at": 0.74, "event": "parcel sealed · 'fingerprint'"}, {"at": 0.81, "event": "'fictional applicant'"}],
      "real · how jobwatch works (JS2)"),
 beat("B08", P3,
      "On November twenty-first, Claude Code ran it from a fresh copy. All one hundred sixty-four tests passed. "
      "Then a live run read three boards, Anthropic, Databricks and Linear, and found one hundred seventy-two "
      "postings it hadn't seen on November eighth.",
      "B08_LiveRun",
      "Two terminal windows replay the saved logs, row by row as they are spoken: the test command, 'Ran 164 tests in 4.180s' and 'OK'; then the run command and the three board lines (jobs=635 new=83, jobs=895 new=88, jobs=32 new=1); '172 not seen on Nov 8' below.",
      [{"at": 0.1, "event": "python3 -m unittest"}, {"at": 0.27, "event": "Ran 164 tests in 4.180s · OK"}, {"at": 0.53, "event": "python3 -m jobwatch run …"}, {"at": 0.61, "event": "anthropic new=83"}, {"at": 0.66, "event": "databricks new=88"}, {"at": 0.73, "event": "linear new=1"}, {"at": 0.77, "event": "'172 not seen on Nov 8'"}],
      "real · ran Nov 21 · replay of the saved terminal log",
      terminal=["tests-2026-11-21", "film-normal-noapproval-2026-11-21"]),
 beat("B09", P3,
      "Its simple word rule, from my first agent, rejected all one hundred seventy-two for the fictional "
      "applicant. Were those rejections right? A word rule can't say. That's the gap the reader will fill.",
      "B09_RuleRejects",
      "A terminal window replays the count command returning 172; below, pages slide into the open 'rejected' crate, the 'kept' tray stays empty, a large '?' hangs over the crate, and the inspection lamp (the reader) arrives, drawn faint with a grey 'plan' tag.",
      [{"at": 0.0, "event": "grep -c not_relevant …"}, {"at": 0.19, "event": "172"}, {"at": 0.23, "event": "pages into 'rejected'"}, {"at": 0.38, "event": "empty 'kept' tray"}, {"at": 0.53, "event": "'?'"}, {"at": 0.76, "event": "the reader arrives"}],
      "real · ran Nov 21 · replay of the saved terminal log",
      terminal=["film-rule-count-2026-11-21"]),
 beat("B10", P3,
      "The run also refused to save its memory, because I hadn't approved that: it ended incomplete, state "
      "unchanged. On November eighth, I typed that approval myself, for one run and one file, and only then did "
      "it save.",
      "B10_Approval",
      "Two terminal windows replay the saved logs. Top, Nov 21: the run command with no approval, 'incomplete — the state was not saved: no approval was given for this run; results are provisional' and 'state advanced: False'. Bottom, Nov 8: the command with '--approve-state 2026-11-08-normal-1:state/state.json', 'finished' and 'state advanced: True'.",
      [{"at": 0.0, "event": "Nov 21 command"}, {"at": 0.04, "event": "incomplete · no approval"}, {"at": 0.32, "event": "state advanced: False"}, {"at": 0.53, "event": "Nov 8: --approve-state …"}, {"at": 0.8, "event": "finished · state advanced: True"}],
      "real · Nov 21 run · Nov 8 run typed by me",
      terminal=["film-normal-noapproval-2026-11-21", "2026-11-08-normal-1-run-by-student"]),
 beat("B11", P3,
      "So far, in both job-search agents, I wrote the rules first, before any code. Claude "
      "Code wrote the code, all but five of the tests, and ran most checks. I ran my own checks, and twice I "
      "withheld my sign-off until the record was right.",
      "B11_RulesFirst",
      "Three stations left to right: a rules page written by the kit quill ('rules first'), the agent workstation ('Claude Code'), and the approval stamp beside two sign-off sheets, one per agent: 'JS1: withheld → signed' and 'JS2: withheld → signed'.",
      [{"at": 0.13, "event": "'rules first' · quill writes"}, {"at": 0.31, "event": "workstation · 'Claude Code'"}, {"at": 0.43, "event": "tool docks"}, {"at": 0.63, "event": "approval stamp"}, {"at": 0.67, "event": "JS1 and JS2: withheld → signed"}],
      "real · my JS1–JS2 record"),
 beat("B12", P3,
      "Next, step by step. By November twenty-fifth, the reader: each claim labelled supported, contradicted or "
      "insufficient by the posting's own text, or 'I cannot tell'. By December first, every quote checked against "
      "the saved posting. By December thirteenth, my approval tied to the exact shortlist. December twentieth: the "
      "full evaluation.",
      "B12_Steps",
      "Four dated stations on a rail ('Nov 25', 'Dec 1', 'Dec 13', 'Dec 20'), each filled at its date by the film's object for it: the inspection lamp (reader), the checkpoint scanner (quote check), the approval stamp, the experiment bench (evaluation); an ink line and a terracotta dot advance along the rail.",
      [{"at": 0.04, "event": "Nov 25: lamp"}, {"at": 0.52, "event": "Dec 1: scanner"}, {"at": 0.67, "event": "Dec 13: stamp"}, {"at": 0.8, "event": "Dec 20: bench"}],
      CONSTRUCTED),
 beat("B13", P3,
      "Do I have what I need? No API credits: model calls will go through my Claude Code login, as my first agent's "
      "judge did for twenty-seven postings in October. Public boards need no accounts; a laptop runs it. The "
      "limits: boards can refuse automated reads, and usage caps mean a daily reading budget.",
      "B13_Resources",
      "Four stations: a grey 'no API credits' tag and a plug going into its socket ('Claude Code login'); a page stack with a check ('27 judged', 'Oct 31'); the agent workstation ('no accounts', 'laptop'); budget slots with a grey 'plan' tag ('daily budget'), a token lifting and stopping at an ink cap line.",
      [{"at": 0.06, "event": "'no API credits'"}, {"at": 0.21, "event": "plug in · 'Claude Code login'"}, {"at": 0.4, "event": "'27 judged · Oct 31'"}, {"at": 0.52, "event": "'no accounts · laptop'"}, {"at": 0.68, "event": "budget slots · 'plan'"}, {"at": 0.72, "event": "token stops at the cap"}],
      "real · JS1 judge run, Oct 31"),

 # ── Part 4 · Did it work? ───────────────────────────────────────────────────────────────────────────────
 beat("B14", P4,
      "How will I know it worked? I'll label real public postings by hand, including a random sample of the ones "
      "my rule rejected, and lock a held-out group away before tuning anything.",
      "B14_TestSet",
      "Three posting pages marked by the kit quill (labelled by hand); two pages pulled from the open 'rejected' crate join them; two go into the 'held out' vault, which locks; the rest go to the 'development' tray.",
      [{"at": 0.15, "event": "pages appear"}, {"at": 0.2, "event": "quill marks each page"}, {"at": 0.41, "event": "sample pulled from 'rejected'"}, {"at": 0.69, "event": "'held out' vault locks"}, {"at": 0.78, "event": "rest to 'development'"}],
      CONSTRUCTED),
 beat("B15", P4,
      "I'll measure four things: whether every quote really appears in the posting; misreads, like 'preferred' "
      "read as 'required'; two errors kept apart, clearing the applicant for a requirement they don't meet, and "
      "ruling out a posting they'd qualify for; and how often it says 'I cannot tell'.",
      "B15_Measures",
      "Four stations on a bench line: the checkpoint scanner with a check ('quote found'); a page with two blocks and a cross ('misreads'); two separate crates ('two errors': 'unsupported clearance', 'false exclusion'); a large '?' ('I cannot tell').",
      [{"at": 0.07, "event": "'quote found'"}, {"at": 0.25, "event": "'misreads'"}, {"at": 0.41, "event": "two crates · 'two errors'"}, {"at": 0.52, "event": "'unsupported clearance'"}, {"at": 0.71, "event": "'false exclusion'"}, {"at": 0.79, "event": "'?' · 'I cannot tell'"}],
      CONSTRUCTED),
 beat("B16", P4,
      "I'll break it on purpose at least five times: a quote with one word changed, an either-or rule, a posting "
      "silent on sponsorship, a board that refuses. And the failure I'm predicting now: a quote copied word for "
      "word, but 'five years preferred' treated as a requirement, caught by a separate check.",
      "B16_Failures",
      "Five slips in a column ('at least 5'), cracked one by one as each case is named; one slip set apart ('predicted', with ''5 years preferred' → read as required'); the student's own hand label catches it: a label card written by the quill, 'my label: preferred', and an ink cross on the predicted slip. The code quote check is not shown catching it: a true quote passes that check.",
      [{"at": 0.0, "event": "five slips · 'at least 5'"}, {"at": 0.14, "event": "cracks, one per case"}, {"at": 0.52, "event": "'predicted' slip"}, {"at": 0.73, "event": "'my label: preferred'"}, {"at": 0.83, "event": "caught by the hand label"}],
      CONSTRUCTED),
 # B17_Bar: the student's own bar, in the student's own words (chat, 2026-11-21, after approving the draft).
 # Only change for speech: the numerals are spelled out (27 -> twenty-seven, 30 -> thirty, 60 -> sixty).
 beat("B17", P4,
      "It worked if at least twenty-seven of thirty held-out decisions match my labels and my checks catch every "
      "deliberate failure. It didn't work if the reader misquotes a posting, clears even one unmet requirement, or "
      "wrongly rules out more than one eligible posting, regardless of the overall score. I'll label about sixty "
      "postings by hand, including thirty randomly picked rejects, and set thirty aside before tuning.",
      "B17_Bar",
      "A measuring bar with two zones. 'worked if': '≥ 27 of 30 held-out match my labels' and 'every deliberate "
      "failure caught'. 'didn't work if': 'any misquote', 'any unmet requirement cleared', 'more than 1 eligible "
      "posting ruled out'. Below: '60 labelled by hand · 30 random rejects · 30 held out'.",
      [{"at": 0.1, "event": "'worked if' zone"}, {"at": 0.45, "event": "'didn't work if' zone"},
       {"at": 0.8, "event": "'60 · 30 rejects · 30 held out'"}],
      "plan · my bar, set Nov 21"),
 beat("B18", P4,
      "One honest limit: a set this small can show me where it fails. It can't prove it works on every posting.",
      "B18_Limits",
      "A small iso stack of pages ('my set') and, as the limit is spoken, a towering stack ('every posting').",
      [{"at": 0.13, "event": "'my set'"}, {"at": 0.56, "event": "towering stack"}, {"at": 0.75, "event": "'every posting'"}],
      CONSTRUCTED),
]

SPARSE_REASON = ("show-tell style: one drawn object or scene on a cream stage per beat, minimal labels, with the "
                 "voice carrying the explanation. The negative space is the style, so only underfill and "
                 "clustered are waived; edge-bleed, empty-frame and contrast still apply.")
for b in B:
    b["qc"] = {"sparse_by_design": True, "sparse_reason": SPARSE_REASON}
    if b["beat_id"] == "B17":                     # on-screen text of the student's bar, from the student's words
        b["bar_lines"] = {"worked_title": "worked if",
                          "worked": ["≥ 27 of 30 held-out decisions match my labels", "every deliberate failure caught"],
                          "failed_title": "didn't work if",
                          "failed": ["any misquote", "any unmet requirement cleared",
                                     "more than 1 eligible posting ruled out"],
                          "footer": "60 labelled by hand · 30 random rejects · 30 held out"}

BEATS = OPEN + B
# BOUT is a drawn Manim beat, not the toolkit's ClaudeTitleOutro, which hard-codes the handle "@NikBearBrown".
BEATS.append({"beat_id": "BOUT", "act": "outro", "lane": "manim", "proof_gate": "SHOW", "on_screen_part": "",
              "narration_text": f"{TITLE}. Suketh Reddy Produtoor.", "estimated_duration_s": 3.0,
              "voice": VOICE, "engine": "kokoro",
              "shot": {"type": "GRAPHIC", "source": "own", "manim": {"class": "BOUT_Outro"},
                       "visual_intent": ("The title and my name beside the inspection lamp; one small line: "
                                         "'Script and pictures by Claude Code from my records, approved by me · "
                                         "synthesized voice (Kokoro am_eric) · detail: the appendix'"),
                       "motion_claim": "The title and my name beside the inspection lamp; a landing shadow.",
                       "show": [{"at": 0.0, "event": "title"}, {"at": 0.1, "event": "my name + rule"}, {"at": 0.23, "event": "disclosure line"}]},
              "kind": "outro_voice", "tail_silence_s": 1.0,
              "qc": {"sparse_by_design": True, "sparse_reason": SPARSE_REASON}})

sheet = {"metadata": {
    "slug": SLUG, "title": TITLE, "topic": "FINAL PROJECT FILM", "skill": "show-tell", "style_preset": "show-tell",
    "channel": "suketh-p", "persona": "Suketh Reddy Produtoor (first person)", "voice": VOICE, "voice_kokoro": VOICE,
    "engine": "kokoro", "clock": "narration", "palette": "claude", "register": "Plain", "fps": 24,
    "aspect_ratio": "16:9", "width": 3840, "height": 2160, "caption_policy": "none",
    "bookend_exempt": ["cold-open", "bvdt", "bdefs", "bhtf"],
    "bookend_exempt_reason": ("Course project film, not a channel episode (INFO 7375 Final Project Film, four parts "
                              "in the instructor's order, at most five minutes): it opens on the hesitant writer, has "
                              "no verdict card or Your Turn composer, and no terms card (GATE T failed the fixed-size "
                              "terms card in October, so terms are defined in the narration). The spoken outro is our "
                              "own drawn beat with the student's name: the toolkit's ClaudeTitleOutro hard-codes the "
                              "handle @NikBearBrown, and the course says to narrate as yourself, without the "
                              "instructor's name, persona or credit line."),
    "audience": "INFO 7375 classmates, TAs and instructor; later, a hiring manager reviewing the project",
    "source_doc": "../DESIGN.md; ../FACTCHECK.md; ../evidence/",
    "playlist": "INFO 7375 final project", "chapter_number": 0, "draft": True,
    "tags": ["INFO 7375", "final project", "agents", "job postings", "F-1", "quote check", "human gate"]},
    "beats": BEATS}

old = HERE / "beat_sheet.json"
if old.exists():                                    # keep measured audio for any beat whose words did not change
    prev = {b["beat_id"]: b for b in json.loads(old.read_text())["beats"]}
    for b in BEATS:
        o = prev.get(b["beat_id"])
        if o and o.get("narration_text") == b["narration_text"] and o.get("audio_file"):
            b["audio_file"], b["actual_duration_s"] = o["audio_file"], o.get("actual_duration_s")
(HERE / "beat_sheet.json").write_text(json.dumps(sheet, indent=2, ensure_ascii=False) + "\n")
words = sum(len(b["narration_text"].split()) for b in BEATS)
print(len(BEATS), "beats;", words, "words; est", round(sum(b["estimated_duration_s"] for b in BEATS)), "s")
