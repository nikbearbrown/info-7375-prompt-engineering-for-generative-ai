# SOURCES.md — TraceCase final project film

Ashwin Thankachan · INFO 7375 Prompt Engineering for Generative AI · Northeastern · Fall 2026

## What I made

- The project itself, and every decision in [FRICTIONAL.md](FRICTIONAL.md).
- The four-part structure of the film, and the call to keep every part when the film had to be cut to
  fit the 240-second ceiling: narration speed went up rather than a prior-work or evaluation beat
  coming out.
- The narration (in `beat_sheet.json`, reproduced in [SCRIPT.md](SCRIPT.md)), reviewed line by line
  and approved by me.
- The defect reports that drove the last three rounds of fixes: I watched the cut and sent back what
  was wrong.

## What AI contributed

**Claude Code (Opus 5), 2026-11-21 to 2026-11-23**

- Rewrote the pitch into the four-part structure the final brief asks for: 18 beats became 25.
- Wrote `scene_body.py` — all 25 Manim drawings — and ran the toolkit's render and quality gates.
- Checked the primary sources behind every claim about other people's work, and wrote
  [FACTCHECK.md](FACTCHECK.md).
- Drafted this file, [README.md](README.md), and [FRICTIONAL.md](FRICTIONAL.md) from my chats and the
  command output. I corrected both and supplied my own reasons.

What it got wrong, and I caught by watching:

- Both circular arrows in the film pointed the wrong way — rotated to aim at the hub instead of along
  the path — in a cut it had already reported as verified against every gate.
- The methods ring animated anticlockwise against its own clockwise numbering, and parked a marker on
  top of a station number.

**ChatGPT, 2026-11-23**

- Gave a brutal read of the finished cut, the way Codex did for ProvenDocs in October. It found that
  the prior-work chart's bars were a blend of different agents' figures under a headline belonging to
  one named agent, and that the resources frame crossed out "billing" as not needed while the
  narration calls model access the open question. Both were real; both are fixed.
- I first recorded two of its findings as rejected — that the evaluation rewards abstention, and that
  the chart's ranges flatter me. Re-reading its actual words, I had misquoted both and had already
  complied with both. The correction is in [FRICTIONAL.md](FRICTIONAL.md); I left the mistake in the
  record rather than editing it out.
- A second round found that my own README reported gate results I had never run. True, and worse than
  it said: two of the three static gates had never been run at all in November.
- A third round found that B04 was explaining the citation mechanism inside the executive summary,
  which the brief reserves for what and why; that my corrected baseline lived only in the documents
  while the film still spoke the loose version; and that "detection nearly solved" and "the local
  option runs 28 microservices" were both broader than their sources. All true. All four beats, and
  three more, were re-recorded on 2026-11-23.

**What neither model caught, and no gate could**

The film ran **4:48** against the assignment's **240-second ceiling** until eleven hours before the
deadline. The toolkit's gates check the film against itself and have no idea what the assignment says;
ChatGPT said plainly it was working from a brief with no stated requirements, and I never gave it the
runtime rule. It surfaced only when I asked what the limit was and Claude went and measured all 22
classmates' films in the course repo — none over 240 s — and found the rule quoted in three of their
build logs. See [FRICTIONAL.md](FRICTIONAL.md), "the film was 48 seconds over the limit".

I chose this project, I reviewed every beat of this cut, and I am responsible for everything in this
folder.

## What I used

Everything ran locally. No model API was called at any point in making this film, and it cost $0.00.

| Thing | Use | Licence / terms |
|---|---|---|
| Brutalist toolkit, github.com/nikbearbrown/brutalist.art at `b21f625` | the show-tell skill, the `iso_kit.py` drawing kit (pasted into `scenes.py` by `build_scenes.py`), the render pipeline and the quality gates | Course-provided toolkit; the repository has no licence file |
| Manim Community 0.18.1 (Python 3.12.15) | every drawing in all 25 beats — native vectors, no raster art | MIT |
| Kokoro-82M via kokoro-onnx 0.6.1, voice `am_michael` | all narration, generated locally from my own first-person script | Kokoro-82M: Apache-2.0; kokoro-onnx: MIT |
| faster-whisper 1.2.1 | word-level alignment, so each drawing is cued to the word that names it, and a transcript check of every beat | MIT |
| ffmpeg 9.0.2 (Homebrew) | audio assembly, padding, and the final mux | LGPL/GPL |
| EB Garamond (bundled with the toolkit) | every on-screen label | SIL Open Font License |

No Remotion bookend cards in this cut. The toolkit's cold-open and outro laws are written for channel
reels; this is a course film with a four-part academic structure and no verdict card, so the beat sheet
marks it `bookend_exempt` and the skin lint's two notes about it are expected, not failures.

## What I read for facts

Dates read are recorded per row in [FACTCHECK.md](FACTCHECK.md). All public, all primary.

- **arXiv:2501.06706v1**, "AIOpsLab: A Holistic Framework to Evaluate AI Agents for Enabling Autonomous
  Clouds" (Microsoft Research). Table 3 for the 59.32% headline, Table 4 for every number in the chart.
  A later MLSys 2025 version exists and I did not read it; the film cites v1 on screen.
- **github.com/microsoft/AIOpsLab** — the framework, its Kubernetes/`kind` requirement, MIT licence.
- **github.com/HolmesGPT/holmesgpt** and **holmesgpt.dev** — what HolmesGPT is, CNCF sandbox status,
  star count, the agentic loop, and read-only-by-design. Also the Kubernetes Remediation MCP page, which
  is why the film does not claim human approval as my difference.
- **opentelemetry-java-instrumentation** supported-libraries doc — Spring Web MVC, Lettuce, Jedis.
- **jaegertracing.io** getting-started — Jaeger all-in-one runs as one Docker container.

## Third-party assets

None. No stock images, music, sound effects, footage, or generated media. Every picture is a Manim
vector drawing written for this film.

## Private data

None in this folder or in the film. No resume, contacts, application tracker, job postings, or
conversation transcripts. The job-market percentages quoted in FRICTIONAL.md are aggregate keyword
counts over postings that are not included here. My CloudPulse work is described in one sentence and no
private code is shown.
