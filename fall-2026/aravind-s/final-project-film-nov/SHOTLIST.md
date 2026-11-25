# SHOTLIST: Klaxon Final Project Film

Real footage first (his rule after the pitch film): Klaxon's own web panel, the screenshots the panel saved during
the week 7 live run, real terminal output, and public GitHub pages. Drawn elements are limited to title and text
cards and one flat diagram. This was the plan for the build. The footage was captured and the film built on
2026-11-20; where the cut differs from the plan is listed under "Review cut (2026-11-20)" below.

**Needs the Docker stack:** nothing required. Every shot reads saved runs or public pages. One OPTIONAL shot
(Grafana during fault 1, no model) needs the stack: see the end. **Needs a live model run:** none.

## Layout rules (his visual bar)

- 1920 x 1080 output; stills captured at device scale 2 (3840 x 2160) unless they are the saved 1440 px screenshots.
- One dark theme for every card, taken from the panel's own CSS (`src/klaxon/panel/static/panel.css`), so cards and
  footage match.
- Text blocks start on the same left margin and sit on one baseline grid; labels in a row share a baseline.
- No logos or screenshots of other companies' sites: prior work is shown as plain text with its source line.
- No two neighbouring beats use the same layout (L1 to L12 below); highlights are one outline box at a time.
- Check every frame at full size before the cut is called done; check no home folder, email or token is on screen.

## Capture setup (for the build phase)

1. Scratch copy of `main`, never the repo folder: `git -C ~/Documents/03-School/klaxon archive fef450b | tar -x -C
   <scratch>/klaxon-fef450b`.
2. A venv inside that copy from its own lock files (the Makefile's `venv` target, run in the copy).
3. The panel, from the copy: `.venv/bin/python -m klaxon.panel --port 8091` (reads `evidence/` only; no Docker, no
   model). Port 8091 so it never meets a week 8 session's panel on 8090.
   - Runs: `http://127.0.0.1:8091/runs`
   - The week 7 live run: `http://127.0.0.1:8091/run/2026-11-17T042300Z_gated-run_duplicate-delivery`
   - Evaluation, week 5, graders shown: `http://127.0.0.1:8091/evaluation?from=week5&graders=shown`
4. Headless Chrome (`--headless=new --remote-debugging-port=9333 --user-data-dir=<scratch profile>`) over the
   DevTools protocol: `Emulation.setDeviceMetricsOverride` 1920 x 1080 at scale 2, `Page.captureScreenshot` per
   scroll offset for pans (or `Page.startScreencast`), highlight boxes drawn with `Runtime.evaluate`.
5. Saved panel screenshots (the only record of the live run while it waited for him), from
   `evidence/week7/2026-11-17T042300Z_gated-run_duplicate-delivery_panel/` at `fef450b`: `1-investigating.png`,
   `2-waiting-for-approval.png`, `3-approved-verifying.png`, `4-verified.png`, `5-postmortem.png` (1440 px wide; 2400 px tall,
   the postmortem 6000).
   Shown at 1:1 inside the 1080p frame (no upscaling), panned vertically.
6. Terminal cards: run the command in the scratch copy, save its stdout exactly, render it as an HTML terminal card
   (Menlo, at most 100 columns), reveal it in 3 or 4 steps.
7. GitHub pages: public, captured signed out.
8. Voice: Kokoro `am_onyx`, speed 1.0, from the `spoken` text in `beats.json`; captions as a soft track from the
   `caption` text (his ffmpeg has no drawtext or libass).

## Beats

| Beat | s | Layout | Footage (exact) | How to capture | Docker |
|---|---|---|---|---|---|
| B01 | 7.7 | L1 TITLE CARD | "Klaxon" / "An AI on-call engineer for a payments system" / "INFO 7375 Final Project Film · Aravind Sundaravadivelu" / footer: "Narration: a synthetic voice (Kokoro, am_onyx). All data is synthetic." | HTML card, fade in | No |
| B02 | 15.6 | L2 browser, full frame | Panel `/runs`: the list of saved runs, the week 7 live run at the top | Headless Chrome on the scratch panel, slow scroll (8 to 10 frames) | No |
| B03 | 18.5 | L3 screenshot crop | `4-verified.png`, the "Signals at the alert" card: five green tiles, the red MoneyCheckFailed tile (`money_off_cents 46100`), then the alert sentence "$461.00 ahead of the provider's balance" | Crop at 1:1; outline box on the red tile, then on the sentence | No (optional Grafana variant: see the end) |
| B04 | 12.3 | L4 split | Left: `4-verified.png` verification bullet "The money is not right ... A rollback repairs nothing". Right: the line "A fix isn't done until the money is checked." | Crop + HTML half card | No |
| B05 | 16.5 | L5 PART CARD + list | Header "2. What others have done", then three rows: "Resolve AI: $125M Series A at a $1B valuation (TechCrunch, Feb 4, 2026)"; "Traversal: $120M Series B (Goodwin, Nov 4, 2026)"; "Datadog Bits AI SRE (Dec 2025), AWS DevOps Agent (GA Mar 31, 2026), Azure SRE Agent (GA Mar 10, 2026)" | HTML card, rows appear on their cue words | No |
| B06 | 14.6 | L6 two-number card | Left "35,000+": "incidents mitigated in Microsoft's own services, by its own count (Mar 10, 2026)". Right "11.4%": "of SRE scenarios resolved by agents on state-of-the-art models (ITBench, ICML 2025)" | HTML card | No |
| B07 | 13.9 | L7 quote card | Header "HolmesGPT · CNCF Sandbox project (accepted Oct 2025)"; mono box with its docs' example query "Compare error rates, latency, restarts, and logs before vs after the rollout and flag any regressions." (the four signals underlined); source line "holmesgpt.dev/latest/operator/deployment-verification, read 2026-11-20" | HTML card | No |
| B08 | 13.6 | L4 split | Left: four chips "error rates · latency · restarts · logs". Right: `4-verified.png` money-check table (at the alert, at the request, at the action, after: failed) | HTML chips + crop | No |
| B09 | 16.2 | L8 PART CARD + flat diagram | Header "3. Methods"; the README's architecture as a flat diagram: simulated customers -> payments API -> fake provider -> signed webhook -> webhook receiver -> Kafka -> ledger consumer and payment confirmer -> PostgreSQL; a side tag "six faults, injected on purpose" | Hand-written SVG in HTML; one floor line, one projection, labels on one baseline | No |
| B10 | 14.3 | L2 browser, zoomed | Panel run page of the week 7 live run (finished): the "Steps" list (1 money_check, 2 recent_deploys, 3 search_logs, 4 diagnose) and "Evidence, each cited by its tool call" (c1, c2, c3) | Headless Chrome on the scratch panel; outline box on the c1 to c3 chips | No |
| B11 | 15.6 | L3 screenshot pan | `2-waiting-for-approval.png`: from the ALERT header down to the APPROVAL REQUEST card ("Waiting for you", "expires in 9:53", rollback_deploy on ledger-consumer, the `make approve` line) | 1:1 vertical pan; caption tag "Saved by the panel during the run" | No |
| B12 | 11.8 | L4 split | Left: `4-verified.png` "The gate's trail" (requested 04:25:01Z, approved typed at a terminal 04:26:11Z, running, done). Right: the money table with posted_exactly_once 7 / 9 / 20 / 20 | Two crops side by side | No |
| B13 | 11.7 | L9 GitHub page | https://github.com/AravindKumar2504/klaxon/actions/runs/44037113149 (week 7's review run: 12 jobs green, 2 h 43 min), then the repo page with the CI badge; a strip: "Built: weeks 1 to 7 (incl. LangGraph, Kubernetes, web panel, CI)" / "Planned by Dec 4: multi-agent, Go receiver, 72-run comparison, safety pass" | Headless Chrome, signed out | No |
| B14 | 22.6 | L5 two-column card | "What I have": university Claude seat through Claude Code in headless mode; Docker Desktop and kind on my Mac; GitHub Actions, free for public repos. "Its limits": no API key, no token credits; seat usage limits, so big batches run overnight; $ figures are Claude Code's estimates at API prices, not charges | HTML card | No |
| B15 | 9.0 | L9 GitHub page | https://github.com/AravindKumar2504/klaxon/commits/main: the week review commits ("Docs: week 7 reviewed by Aravind and done", ...) | Headless Chrome, signed out; outline box on one "reviewed by Aravind" line | No |
| B16 | 12.6 | L10 PART CARD + terminal card | Header "4. Evaluation"; `make eval-cases` real output (the eight cases, each with its right answer) | Run in the scratch copy (offline, calls nothing); HTML terminal card, 3 reveal steps | No |
| B17 | 21.8 | L2 browser, full frame | Panel `/evaluation?from=week5&graders=shown`: the Opus 5.5 table header (Named the cause: rule, judge; Action right; Named where none fits) | Headless Chrome, slow horizontal pan across the header | No |
| B18 | 12.0 | L3 zoom | Same page: Opus rows for the six faults ("3 of 3" in both grader columns), the "Named where none fits" column (0), and "In all: 24 runs (0 not run), 191 model calls, $10.00." | Crop at scale 2, one outline box at a time | No |
| B19 | 18.6 | L4 split | Left: the false-alarm rows (Opus 1 of 3 by each grader; Sonnet 0 of 3). Right: three labels: "No action named", "1 run in 6 said plainly: nothing is wrong", "Every fault was known while it was built" | Crop + HTML half card | No |
| B20 | 17.7 | L11 END CARD | Two columns, "It works if" / "It fails if", as narrated; then "Klaxon · Aravind Sundaravadivelu · github.com/AravindKumar2504/klaxon" | HTML card | No |
| B21 | 4.0 | L12 APPENDIX CARD, silent | The sources (short form, from SOURCES.md) and the AI-use line | HTML card | No |

## Review cut (2026-11-20): where it differs from the list above

- B03 uses the fallback (the panel's "Signals at the alert" card, from the same run); Grafana stays an optional swap.
- B04: the left side is the verification card's three bullets, "healthy" outlined green, then "the money is not
  right" outlined red, before the right-hand line appears.
- B08: the money table shows three of its four columns. The fourth (posted_exactly_once) has its header clipped by
  the panel's own layout (the table is 21 px wider than its box), so it was left out rather than shown cut.
- B11: the saved 1440 px screenshot is shown at 1.2x (1728 px, the full content box) so its text is readable; a
  slight softening, labeled "Saved by the panel during the run".
- B12: the right side is the deploy log's two lines plus three chips from the verification record ("Healthy: yes",
  "Cause removed: yes", "Money right: no") instead of the money table, which B08 already shows.
- B13: the strip lists what is built and what is planned; week 8 is not merged on `main` (`fef450b` on 2026-11-20),
  so it says "Planned by Dec 4".
- B15: the commit page is captured full height and cropped lower, so both highlighted commits sit inside the frame.
- B16: the terminal card is a real excerpt, `make eval-cases | grep -E '^[a-z]|action that fits'` (names and the
  action that fits), not the full 33-line output.
- B17 and B18: the report is cropped at the "Refused by code" column; the panel's table scrolls sideways past it.
- B19: three of the report's columns (Case, Named the cause: rule and judge, Action right) are set side by side at
  the capture's own pixels, labeled "three of the report's columns".
- Pans (B02, B11, B17) have soft 28 px fades at the window's top and bottom edges.

## Optional: Grafana during fault 1 (needs the Docker stack, no model)

His pick named Grafana. Its strongest shot is the "Klaxon patient" dashboard staying normal while the money check
fails. It would replace B03's crop (or sit under B04's line).

- What runs: Docker Desktop on; in the scratch copy, `make up` on a fresh stack, then `make demo-fault
  FAULT=duplicate-delivery` (about 3 minutes, no model, writes its evidence inside the scratch copy); capture
  `http://127.0.0.1:3000`, dashboard "Klaxon patient", at minute 1 to 2 (headless Chrome; sign-in = the image's
  defaults in `compose.yaml`); then `make down` and Docker stopped.
- Conditions: his OK, and a time when no week 8 session uses Docker (one stack at a time on this Mac; week 8's
  72-run night and its stack checks also need it).
- Fallback, already real: the panel's "Signals at the alert" card from the same week 7 run (B03 as listed).
