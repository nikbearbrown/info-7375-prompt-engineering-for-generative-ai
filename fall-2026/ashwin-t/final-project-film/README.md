# Final Project Film: TraceCase

**Ashwin Thankachan** · INFO 7375 Prompt Engineering for Generative AI · Northeastern · Fall 2026

**Title:** TraceCase: An Agent That Finds Out Why

**One sentence:** TraceCase will investigate failures in a small Spring Boot service from its logs,
traces and deploy history, and propose one fix that a person must approve before it runs.

**Target role:** software development engineer, backend (new grad).

**Video:** `tracecase-final.mp4` — 3:52.4 (232.375000 s) · 16:9 · 3840×2160 · 24 fps · H.264 + AAC.
SHA-256 `da1b1b93e95f8d920bc45a43f61a0afc534e450ac2eb05d45e1fbea988ca2b61`.

**Narration:** a synthetic Kokoro voice (`am_michael`) reading my own first-person script. Generated
locally. No model API was called in making this film; the whole production cost $0.00.

**What exists today:** this film, the brief and this plan. **No TraceCase code exists yet**, and the
film's last beat says so out loud. Every picture of the product is tagged "constructed" on screen.

> This is the final project **film**, not the final project. It replaces the October pitch
> (`tracecase-pitch.mp4`, 3:53, 18 beats), which answered the seven pitch questions. This one is built
> to the four parts the final brief asks for, and to the brief's 240-second ceiling.

## The four parts the brief asks for

| Part | Beats | Runtime | What it covers |
|---|---|---|---|
| 1 · Executive summary | B00–B04 | 0:00–0:35 | what TraceCase is, what the finished repository contains, and why the gap matters — no *how* |
| 2 · Introduction (prior work) | B05–B10 | 0:35–1:42 | HolmesGPT and Microsoft Research's AIOpsLab, what each one got, and where TraceCase sits between them |
| 3 · Methods | B11–B18 | 1:42–3:02 | the system under test, the fault catalogue, the data source, the agent loop, the tool allow-list, the evidence checker, the human gate, and what it runs on |
| 4 · Evaluation | B19–B24 | 3:02–3:51 | the held-out set, the baseline, the four measurements, what counts as worked, the pass/fail safety test, and the honest status |

Each beat carries its part name on the left and its position in the film (`2 / 4`) on the right, so a
grader can always see which section they are in.

## What's in this folder

| File | What it is |
|---|---|
| `tracecase-final.mp4` | the film |
| [PROJECT-BRIEF.md](PROJECT-BRIEF.md) | the brief the film answers, revised 2026-11-23; carries the corrected baseline and the three evaluation numbers |
| [BUILD-PROMPT.md](BUILD-PROMPT.md) | the prompts I gave Claude, the rules I set, and what each quality gate actually runs |
| [SCRIPT.md](SCRIPT.md) | the narration exactly as spoken, generated from `beat_sheet.json` so it cannot drift from the cut |
| [FACTCHECK.md](FACTCHECK.md) | every claim about other people's work, with the primary source and the date read |
| [SOURCES.md](SOURCES.md) | what I made, what Claude and ChatGPT contributed, tools, licences, private data |
| [FRICTIONAL.md](FRICTIONAL.md) | the dated log — October's pitch, then this film, including what went wrong |
| [beat_sheet.json](beat_sheet.json) | narration and visual plan, 25 beats with measured durations |
| `gate-reports/` | the toolkit's quality-gate output |
| `build/` | the sources that draw every frame: `scene_body.py` (25 Manim drawings), `build_scenes.py`, `make_sheet.py` |
| `mp3/` | the narration, plus `words.json` — the word-level alignment that cues each drawing to the word that names it |

## Quality gates

All from the Brutalist toolkit at `b21f625`, run on this final version.

Each row is a run I made on the sources that produced the delivered master, not a carried-over
result. The static gates (A, W, B) are per scene, so they were run 25 times each.

| Gate | Coverage | Result |
|---|---|---|
| L: beat-mix lint | the beat sheet | clean |
| A: static pre-flight | 25 scenes | **25 / 25 clean**, 0 warnings, 0 errors |
| W: WCAG contrast + margins, palette `claude` | 25 scenes | **25 / 25 clean** |
| B: layout audit — text overlap, out-of-frame | 25 scenes, **346 snapshots** | **0 errors**, 11 warnings ([report](gate-reports/LAYOUT-AUDIT.md)) |
| V: frame-level visual QC on the compiled reel | 50 frames | **0 BLOCKER, 0 MAJOR** ([report](gate-reports/QC-GATE-V.md)) |
| T: typography | 25 beats | **PASS**, 0 FAILs ([report](gate-reports/QC-GATE-T.md)) |
| Master | the delivered file | exported with `./art final`; the SHA-256 above is of that file |

**About gate B's 11 warnings.** Every one is `TEXT_ON_CURVE` — a text box touching a stroked curve —
and both places it happens are deliberate: a number centred inside its node circle (B12, B14) and a
product name seated on the bottom rule (B05, B06, B07, B10). The count is unchanged across the
2026-11-23 recut, and the rebuilt B04 adds none. None is text overlapping other text, and
all 25 beats pass gate T and gate V on the rendered frames. Every finding is listed individually in
the report rather than summarised away.

Two non-blocking toolkit notes: the skin lint wants a Remotion cold-open card and outro card, because
those laws are written for channel reels. This is a course film with a four-part academic structure and
no verdict card, so the beat sheet marks it `bookend_exempt` and both cards are deliberately absent.

### What the gates do not check, and what I did instead

The gates measure contrast, type size, bounding-box overlap, frame edges and canvas fill. They have no
idea whether a picture means what the narration says.

- **I watched the cut and found two broken arrows.** Both circular arrows in the film — the loop in the
  prior-work section and the agent ring in methods — had their heads rotated to point at the hub
  instead of along the path, in a version that had already passed every gate. The methods ring was also
  animating anticlockwise against its own clockwise numbering, with the moving marker parked on top of
  a station number. Fixed, and both now come from one shared helper.
- **I had the finished cut reviewed by ChatGPT**, the way I did with ProvenDocs in October. It caught
  that the prior-work chart's bars were a blend of different agents' figures sitting under a headline
  that belongs to one named agent. That is the exact error the film argues against, and no gate could
  have caught it. The chart is rebuilt from Table 4 of the paper as explicit ranges, with the agents
  named and the citation on the frame. The full account is in [FRICTIONAL.md](FRICTIONAL.md).
- **The closing frame contradicted the closing line.** The last beat's "exists" shelf carried the word
  *TraceCase* on the same baseline as its three objects, so the row read as *TraceCase exists* — in the
  beat that says no TraceCase code exists yet. The unlabelled disc beside it, meant to be this film, was
  not recognisable as anything. Labels added, wordmark moved off the shelf. Found by looking at the
  frame, not by any check.
- **Beat openings were measured, not eyeballed.** Several beats opened on nothing but their heading for
  over a second. An ink-coverage scan of every compiled clip found the worst at 1.75 s; eight beats now
  lead their first reveal, and the longest blank opening is 0.75 s.
- **The narration and the cues were checked against each other, not assumed.** The faster-whisper
  transcript of the delivered audio matches the script word for word on **25 / 25 beats**, and all
  **91** animation cues in `scene_body.py` resolve to a real word timestamp in `mp3/words.json` —
  none of them silently falls back to the toolkit's character-count estimate. That is what makes the
  claim "each drawing appears on the word that names it" checkable rather than decorative.

## Evaluation: the rules the film states

Two of these were wrong in the first cut of the film and were found by review. The narration was
re-recorded, so the film and this folder now say the same thing; there is no correction document to
read alongside it.

1. **The baseline gets the same evidence.** Not "paste the logs into a model." The baseline is the
   **same model, given the same logs, traces and deploy history in one prompt, with no loop, no tools
   and no checker.** What this comparison measures is the whole agent workflow against a single-prompt
   read of the same evidence. It does **not** isolate the loop by itself — loop, tool use and the
   checker all differ between the two — and no claim here says otherwise.

2. **Citation and support are two different numbers.** The checker verifies that a cited log line or
   span *exists*, which catches an invented reference. It cannot tell whether a real line justifies the
   diagnosis: "database request timed out" is a real line and does not prove that a deploy changed a
   password. So three numbers are reported separately — **citation validity** (enforced in code),
   **claim support** (scored by me against a rubric fixed before the run), and **diagnosis accuracy**
   (against the fault I injected). B16 says this out loud: existence is the checker's, support is mine.

**The scoring rules, in full:**

- Ground truth decides diagnosis correctness; I injected the fault, so I know it.
- A rubric fixed before the run decides whether the cited evidence supports each claim.
- Insufficient-evidence cases are labelled **before** tuning. "I don't know" is correct only on those.
- Abstaining on an answerable case is reported separately and never counted as a correct diagnosis.
- **Worked** means more correct causes than the baseline on the same held-out ten, no unsupported claim
  in the scored outputs, and a pass on the swapped-action test.
- With ten held-out cases one case moves accuracy by ten points, so correct, incorrect and abstained are
  reported separately and the result is presented as what it is: a small controlled evaluation.

## Rebuild

**What this folder is, and is not.** `build/` holds every source that draws the film, and `mp3/` holds
the narration with the word-level alignment (`words.json`) that cues each drawing to the word that
names it. It is **not** a self-contained package. It does not vendor the Brutalist toolkit, and
`build_scenes.py` needs `ART_HOME` pointed at a checkout of it at commit `b21f625` to find
`iso_kit.py` — the show-tell skill requires that file to be pasted into `scenes.py` rather than
imported, so it cannot be bundled here. Regenerating the narration from scratch additionally needs
Kokoro and faster-whisper installed.

**Stage it flat first.** The scene code finds `beat_sheet.json` and `mp3/words.json` *next to
`scenes.py`*, so building inside `build/` silently produces a film with no word-level cueing — every
cue falls back to a character-count estimate and nothing errors. Copy the sources up beside the data
before building:

```
cp build/*.py build/ashwin.json .      # scenes beside beat_sheet.json and mp3/
export ART_HOME=/path/to/brutalist.art # the checkout at b21f625
python build_scenes.py
```

Brutalist toolkit at `b21f625`, Python 3.12.15, Manim Community 0.18.1:

```
export ART_HOME=/path/to/brutalist.art          # the checkout at b21f625
python build_scenes.py                          # iso_kit.py + scene_body.py -> scenes.py
manim -r 3840,2160 --fps 24 scenes.py B00_Hook  # ... once per beat class, 25 in all
./art run   <reel>                              # gates L, SHAPE, V
./art final <reel>                              # gate T, then the verified master
```

The static gates are run per scene, not by `art`:

```
python runtime/qc/manim_layout_audit.py scenes.py --class B08_Numbers
python runtime/qc/wcag_margin_check.py  scenes.py --class B08_Numbers --palette claude
```
