#!/usr/bin/env python3
"""Build beat_sheet.json for tracecase-final from the narration script."""
import json, datetime

WPM = 150.0  # narration pace used by the pitch reel (~2.5 words/s)

SPARSE = {
    "sparse_by_design": True,
    "sparse_reason": "show-tell style: one drawn object or scene on a cream stage per beat, "
                     "minimal labels, the voice carries the explanation. Only underfill and "
                     "clustered are waived; edge-bleed, empty-frame and contrast still apply.",
}

# (beat_id, manim_class, narration, visual_intent, [(at, event), ...])
BEATS = [
 ('B00','B00_Hook',
  "A dashboard tells you a service broke. It doesn't tell you why.",
  'A dark dashboard panel stands on a cream stage with one terracotta light burning; a large question mark rises behind it and the panel stays silent.',
  [(0.25, 'dashboard + red light'), (0.65, 'question mark rises'), (0.9, 'panel stays silent')]),

 ('B01','B01_WhatItIs',
  "TraceCase is an agent that reads a broken service's logs, traces and deploy history, works out why it broke, and proposes one fix a person must approve.",
  'A server stack sits left under a warning light; a log page, trace bars and a deploy timeline fan out beside it; a magnifier sweeps across them; one proposal card slides right and halts at a closed gate arm.',
  [(0.15, 'service'), (0.4, 'three sources'), (0.68, 'magnifier sweep'), (0.88, 'card stops at gate')]),

 ('B02','B02_Artifact',
  "Finished, it's one public repository: a demo service to break on purpose, the agent, an approval screen, and an evaluation report.",
  'A single open box on the stage; four flat pages rise out of it in sequence and arrange into a row, each labelled beside it.',
  [(0.2, 'the repo box opens'), (0.45, 'service + agent'), (0.7, 'approval screen'), (0.9, 'evaluation report')]),

 ('B03','B03_WhyCare',
  "A team project of mine answered one question: is the service healthy? When the answer is no, an engineer reads logs by hand. That's where time goes.",
  'A green tick sits on a plinth left; it flips to a terracotta cross; a wall of log pages stacks up on the right and a small cursor crawls down them while a clock hand sweeps.',
  [(0.15, 'healthy tick'), (0.38, 'flips to a cross'), (0.65, 'wall of logs'), (0.88, 'clock sweeps')]),

 ('B04','B04_CheckNotTrust',
  "It's built so you can check it instead of trusting it. It does the digging, and you decide whether any fix runs.",
  "A claim card floats centre; a drawn arrow leaves it and lands on one highlighted line inside a log page; a second card's arrow finds nothing and the card is struck out.",
  [(0.25, 'claim card'), (0.5, 'arrow lands on a real line'), (0.75, 'second arrow finds nothing'), (0.92, 'card struck out')]),

 ('B05','B05_Holmes',
  "This isn't new. HolmesGPT is an open-source SRE agent, a CNCF sandbox project, about four thousand stars. It runs an agentic loop over live data, read-only by design.",
  'Two plinths rise on a cream stage; on the left one a magnifier orbits a ring of four small source blocks, a star count beside it, a small lock badge marking it read-only.',
  [(0.12, 'two plinths'), (0.35, 'HolmesGPT on the left'), (0.65, 'loop over sources'), (0.88, 'read-only lock')]),

 ('B06','B06_HolmesGap',
  "It's the mature option. What I couldn't find was an independent evaluation. The evidence I can read is the project describing itself.",
  'A badge reading mature settles on the left plinth; a second empty frame labelled independent evaluation stays blank; a loop arrow curls from the project back to itself.',
  [(0.2, 'mature badge'), (0.5, 'empty evidence frame'), (0.82, 'self-referential loop')]),

 ('B07','B07_AIOpsLab',
  "Microsoft Research's AIOpsLab is the opposite: a benchmark, not a product. Forty-eight problems across two applications, faults injected on purpose.",
  'On the right plinth a grid of forty-eight small tiles assembles; two application clusters sit beneath it; a small fault bolt drops into the grid.',
  [(0.25, '48 tiles'), (0.58, 'two apps'), (0.85, 'injected fault')]),

 ('B08','B08_Numbers',
  'And it published numbers. Their best agent scored about fifty-nine percent overall. By task: detection, sixty-nine to one hundred percent; root cause, thirty-six to forty-five; mitigation, twenty-seven to fifty-five. In their words, none consistently achieve high accuracy.',
  'Four dim bars rise on the stage labelled beside them: detection tall, localisation mid, root cause low, mitigation low; a single terracotta rule crosses at the halfway mark.',
  [(0.15, '59 percent overall'), (0.4, 'detection bar tall'), (0.68, 'root cause and mitigation fall short'), (0.9, 'halfway rule')]),

 ('B09','B09_Cluster',
  'It also needs Kubernetes: its SocialNetwork application alone runs twenty-eight microservices. Not something a reviewer opens on a laptop in sixty seconds.',
  'A dense cluster of small service blocks piles up on the right; a closed laptop sits small beside it and does not open; a stopwatch beside the laptop stays at zero.',
  [(0.25, 'cluster piles up'), (0.6, 'laptop stays shut'), (0.87, 'stopwatch at zero')]),

 ('B10','B10_Gap',
  'So: a mature tool with thin public evidence, a benchmark that needs a cluster. TraceCase goes between them, laptop-sized, shipping the broken service.',
  'The two plinths slide apart and a third, smaller plinth rises between them carrying an open laptop with a tiny service and a magnifier on its lid.',
  [(0.2, 'two plinths apart'), (0.52, 'third plinth rises'), (0.78, 'laptop + service'), (0.93, 'magnifier')]),

 ('B11','B11_SystemUnderTest',
  'Step one is the thing that breaks: a Spring Boot API and worker, Postgres, and Redis, in Docker Compose. Open Telemetry writes traces and logs.',
  'Four blocks assemble into a small isometric stack: API, worker, database cylinder, cache cylinder; thin trace lines run out of the stack into two flat files on the stage floor.',
  [(0.18, 'API + worker'), (0.45, 'Postgres + Redis'), (0.7, 'compose box closes round them'), (0.9, 'traces land in files')]),

 ('B12','B12_FaultCatalogue',
  'Step two: a fixed catalogue of failures, each triggered with one command. Stale cache, slow query, bad deploy, queue backup. True causes written down first.',
  'Five labelled cards deal out in a row; a single switch flips and one card lights terracotta; a sealed envelope marked ground truth sits closed beneath the row.',
  [(0.2, 'five fault cards'), (0.55, 'one switch, one fault lights'), (0.85, 'sealed ground-truth envelope')]),

 ('B13','B13_DataSource',
  "That's my data: the system generates it. No customer logs, nothing scraped. I break my own service. The ground truth is mine because I caused it.",
  'A closed loop is drawn: the service emits pages that fall into a labelled tray, and the tray feeds back to the service; three outside doors stand shut around the loop.',
  [(0.2, 'service emits, tray fills'), (0.5, 'loop closes'), (0.75, 'outside doors shut'), (0.92, 'ground truth seal')]),

 ('B14','B14_AgentLoop',
  "Step three is the agent. Observe, pick a tool, update the hypothesis. It stops when every claim cites a line that exists, or on a step budget, never on the model's say-so.",
  'A four-station ring draws itself with a travelling dot; a step counter ticks beside it; the dot halts on a seal, and a second dashed exit marked budget also halts it.',
  [(0.18, 'ring of four stations'), (0.48, 'dot travels, counter ticks'), (0.75, 'halts on evidence'), (0.92, 'halts on budget')]),

 ('B15','B15_AllowList',
  "Its tools are an allow-list in code: read logs, query traces, read deploys. Not a shell — the Microsoft study gave its agents one. I'm deliberately not.",
  'Three tool pills sit inside a drawn boundary; a fourth pill marked shell is outside it and a gate arm bars its way in.',
  [(0.25, 'three allowed tools'), (0.6, 'boundary drawn'), (0.87, 'shell barred outside')]),

 ('B16','B16_Checker',
  "Every claim must cite a log line or span. A checker reopens the file; if it isn't there, the claim is rejected. Whether that line supports the diagnosis is my call.",
  "A claim card hands a citation to a small checker block; the checker opens a log page, finds the line and stamps the card; a second card's line is absent and the card is pushed into a reject tray.",
  [(0.2, 'claim cites a line'), (0.45, 'checker opens the file'), (0.7, 'stamped'), (0.9, 'second card rejected')]),

 ('B17','B17_HumanGate',
  'The fix comes from a short menu, never free text. Approval binds three things: the action, its target, and its evidence. Change one and it refuses.',
  'A short menu of three fix pills; one is chosen and a seal binds it to a target block and an evidence page; the target swaps and the seal cracks, and the gate arm drops.',
  [(0.22, 'menu of fixes'), (0.52, 'seal binds three things'), (0.8, 'one is swapped'), (0.93, 'seal cracks, gate drops')]),

 ('B18','B18_Resources',
  'Everything else is a laptop and Docker. No cluster, no GPU. Model access is the open question: my seat covers the assistant, not calls from code. So the agent targets a model interface, and a local model can stand in.',
  'An open laptop centre with a small compose box beside it; a cluster and a GPU card sit dim and crossed out at the edge; a model-shaped socket on the laptop stays empty with two labelled plugs waiting beside it.',
  [(0.15, 'laptop + docker'), (0.35, 'cluster and GPU crossed out'), (0.65, 'empty model socket'), (0.9, 'two plugs waiting')]),

 ('B19','B19_EvalSet',
  "About thirty scenarios from that catalogue. Ten locked away before I tune anything, so I can't quietly fit to them.",
  'Thirty small tiles assemble in a block; ten slide into a dark vault and a lock closes on it; twenty remain on the stage.',
  [(0.25, 'thirty tiles'), (0.6, 'ten move to the vault'), (0.88, 'lock closes')]),

 ('B20','B20_Baseline',
  'The baseline gets the same model and the same logs, traces and deploy history, in one prompt. No loop, no tools, no checker.',
  'A log page is dropped whole into a model pill and one answer card falls out; beside it the three machinery pieces from earlier sit dim and unused.',
  [(0.25, 'logs pasted in'), (0.55, 'one answer out'), (0.85, 'loop, tools, checker dim')]),

 ('B21','B21_FourNumbers',
  "Four measurements. Did it name the right cause. Did it say I don't know when evidence was missing. How many unsupported claims survived — I score those by hand. And how many steps it burned.",
  'Four counters appear in a row with labels beside them; the second counter is ticked with a check rather than a cross; the third shows a bold zero target.',
  [(0.15, 'right cause'), (0.42, "honest I don't know, ticked"), (0.72, 'unsupported claims, zero'), (0.92, 'steps used')]),

 ('B22','B22_WhatCountsAsWorked',
  'It worked if it names more correct causes than the baseline on the held-out ten, and no unsupported claim survives. It failed if it only wins by guessing more often.',
  'Two bars face each other over the held-out vault: TraceCase and baseline; a terracotta line marks the pass mark; a guess-more arrow is drawn and then crossed out.',
  [(0.25, 'two bars over the vault'), (0.58, 'pass mark'), (0.85, 'guessing route crossed out')]),

 ('B23','B23_SafetyTest',
  "And one test that's simply pass or fail. Approve fix A, swap in fix B, and the system must refuse.",
  'A sealed approval card marked A sits at a gate; a hand swaps in a card marked B; the seal cracks and the gate arm stays down with a terracotta refusal mark.',
  [(0.25, 'A approved at the gate'), (0.55, 'B swapped in'), (0.87, 'refused, gate stays down')]),

 ('B24','B24_Status',
  "Where it stands tonight: a brief, this plan, and this film. No TraceCase code exists yet. Everything you just heard is what I'm going to build.",
  'Two shelves on the cream stage: the lower shelf labelled exists holds a brief page and a film reel; the upper shelf labelled will exist holds ghosted outlines of the service, agent, gate and report.',
  [(0.25, 'exists shelf fills'), (0.6, 'no code yet'), (0.88, 'will-exist shelf stays ghosted')]),

]

def est(text):
    return round(len(text.split()) / WPM * 60.0, 1)


# Measured audio, if it has already been generated. Without this, re-running make_sheet.py after the
# audio exists drops actual_duration_s and audio_file for every beat, and the compile step then
# refuses with "missing required audio". Beats whose narration changed since the audio was made are
# left without a measured duration on purpose, so the next generate_audio run fills them in.
try:
    _MEASURED = json.load(open("mp3/timings.json"))
except OSError:
    _MEASURED = {}

beats = []
for bid, cls, narr, intent, show in BEATS:
    beats.append({
        "beat_id": bid,
        "act": "show-tell",
        "lane": "manim",
        "proof_gate": "SHOW",
        "narration_text": narr,
        "estimated_duration_s": est(narr),
        "voice": "am_michael",
        "engine": "kokoro",
        "shot": {
            "type": "GRAPHIC",
            "source": "own",
            "visual_intent": intent,
            "show": [{"at": a, "event": e} for a, e in show],
            "manim": {"class": cls},
            "motion_claim": intent,
        },
        "qc": dict(SPARSE),
        **({"actual_duration_s": round(_MEASURED[bid], 2),
            "audio_file": f"mp3/beat-{bid}.mp3"} if bid in _MEASURED else {}),
    })

sheet = {
  "metadata": {
    "slug": "tracecase-final",
    "title": "TraceCase: An Agent That Finds Out Why",
    "topic": "FINAL PROJECT FILM",
    "skill": "show-tell",
    "style_preset": "show-tell",
    "channel": "ashwin-t",
    "channel_title": "Ashwin Thankachan",
    "persona": "Ashwin Thankachan (first person)",
    "voice": "am_michael",
    "voice_kokoro": "am_michael",
    "engine": "kokoro",
    "clock": "narration",
    "palette": "claude",
    "register": "Plain",
    "fps": 24,
    "aspect_ratio": "16:9",
    "width": 3840,
    "height": 2160,
    "caption_policy": "none",
    "greeting_language": "English (Hi)",
    "bookend_exempt": ["cold-open", "bvdt", "bhtf"],
    "bookend_exempt_reason": "Course final-project film, not a channel reel: four-part academic structure, no verdict card.",
    "audience": "INFO 7375 instructor and TAs; backend engineering hiring managers",
    "source_doc": "SCRIPT.md (2026-11-21); HolmesGPT public pages and arXiv:2501.06706v1 (read 2026-11-21)",
    "playlist": "INFO 7375 Final Project",
    "chapter_number": 1,
    "tags": ["TraceCase","final project","agent","evaluation","OpenTelemetry","Spring Boot","INFO 7375"],
    "structure": ["executive summary","introduction / prior work","methods","evaluation"],
  },
  "beats": beats,
}

with open("beat_sheet.json","w") as f:
    json.dump(sheet, f, indent=2)

total = sum(b["estimated_duration_s"] for b in beats)
print(f"beats: {len(beats)}")
print(f"estimated runtime: {int(total//60)}:{int(total%60):02d}  ({total:.1f}s)")
for b in beats:
    print(f"  {b['beat_id']}  {b['estimated_duration_s']:5.1f}s  {b['shot']['manim']['class']}")
