# SOURCES — SponsorScout, Final Project Film (v2)

Akshit Verma · 2026-11-23

## 1. What the film's claims rest on

Claim by claim: `FACTCHECK.md`.

| Source | Used for | When |
|---|---|---|
| Assignment 1 repository `the-reallocation-engine` @ `a1d321f` (run-2, engine-baseline) | 123 sponsors, 16 boards, the four verdicts, the scorer's zero → skip | run 2026-10-03 |
| `../board-resolver/` (code, tests, `runs/live-2026-11-23/`) | 629 requests, 39 candidates, 16 → 50 / 123, the five refused boards, Weight Watchers, 5 empty, 67 not found, the fingerprint on screen, 28 tests, the console bug | 2026-11-23 |
| myvisajobs.com | P2A. **Akshit looked at it on 2026-10-07.** No content, logo or screenshot used | 2026-10-07 |
| h1bgrader.com (employer pages) | P2A: "grades employers on past approvals and denials". **Found by Claude's web search, 2026-11-23; Akshit has not looked at it** | 2026-11-23 |
| Interstride, as described by university career centres (e.g. career.cornell.edu, 2025-02-06) | P2A: "shows sponsorship history and filters jobs by visa". **Found by Claude's web search, 2026-11-23** | 2026-11-23 |

Data behind the runs: all public (80 Days to Stay CSV; SEC Form D samples; public Greenhouse, Lever and
Ashby job-board APIs). The job seeker is fictional. No private data, résumé, contacts or transcript is in the film.

## 2. Tools

Same toolchain as the pitch film (its SOURCES.md §2): brutalist.art `6a8380a` + my changes, Kokoro-82M
voice **`am_michael`** (the narration is a **synthetic voice**, not my recorded voice), Manim 0.18.1,
Remotion 4.0.486, ffmpeg, faster-whisper, EB Garamond and Lato (SIL OFL). Cost: $0.00.

**Toolkit changes for v2** (in brutalist.art; the originals are in `_superseded/`):
- `runtime/remotion/src/illustrations/pitch.tsx`: an optional `byline` prop (default `"a pitch by"`,
  so the pitch film renders unchanged). This film passes `"a film by"`.
- `runtime/scripts/run.sh` and `runtime/scripts/type_check.py`: **both back to the originals**
  (byte-identical; checked with `cmp`). A 1080p scene-render change to `run.sh`, and a fix to Gate T's
  kerning test, were tried and reverted: the kerning fix failed its own negative test (FRICTIONAL Entry 4).
  As in the pitch film, scenes render at 4K and the film is compiled at **1920×1080**.

## 3. Who did what

Claude Code (Claude Opus 5.5) did most of the building in this session, under my direction.

| Part | Me (Akshit) | Claude Code |
|---|---|---|
| Scope | build the resolver first, offline first; work in a new folder; then the film | proposed the order |
| Board resolver | approved the live run; the 44 G1 decisions (I ran 13 myself; Claude ran 31 at my instruction, each noted in `decisions.json`); refused the five wrong boards | contract, tests, code, live run, the evidence for each proposal, flagged the five wrong boards |
| Script | asked for the four-part film | wrote the narration from the run records; checked every claim (FACTCHECK) |
| Prior work | MyVisaJobs (my look, 2026-10-07) | web search for H1BGrader and Interstride |
| Evaluation plan | approved the 9-in-10 threshold, 2026-11-23 | drafted it |
| Visuals, gates, captions | — | all drawings (`scenes.py`, built on the pitch film's kit), every gate, captions |
| Sign-off | signed off FACTCHECK.md, 2026-11-23, after watching the film | recorded it at Akshit's instruction |

**No Claude response is shown in the film.** Every picture is a constructed drawing, tagged on screen.
