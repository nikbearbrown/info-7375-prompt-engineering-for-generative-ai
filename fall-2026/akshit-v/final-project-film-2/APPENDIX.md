# APPENDIX: SponsorScout, the detail behind the film

Akshit Verma · INFO 7375 · Final Project Film · 2026-11-23

The film keeps to the four parts. This appendix holds the detail. Past tense means it exists and can be
checked here; "will" means proposed. Every number below is in [film/FACTCHECK.md](film/FACTCHECK.md)
with its source.

## 1. What and why (part 1, in one paragraph)

SponsorScout tells an international student looking for data jobs, sponsor by sponsor, whether to
**apply, network, check by hand, or skip**, and shows the public record behind each verdict. A strong
H-1B sponsor with no entry-level data job open today isn't dropped: it goes on a networking list. It
never applies, emails or contacts anyone. The person decides. It matters because a student on a short
clock wastes applications on sponsors with nothing open. I'm job hunting too.

## 2. What others have done (part 2)

| What exists | How I know | What it does | What it doesn't do |
|---|---|---|---|
| MyVisaJobs | I looked, 2026-10-07 | lists H-1B sponsors and their past job counts | turn a sponsor with nothing open into a networking target |
| H1BGrader | Claude's web search, 2026-11-23 ([example employer page](https://h1bgrader.com/h1b-sponsors/quorum-labs-inc-ew2xqzey03)) | grades employers on past H-1B approvals and denials | look at what is open today |
| Interstride | Claude's web search, 2026-11-23 ([Cornell career centre](https://career.cornell.edu/blog/2025/02/06/how-can-the-interstride-platform-help-you-with-your-job-search/)) | shows employers' sponsorship history; filters jobs by visa type | the same routing |
| Reallocation Engine scorer | ran 2026-10-03 (Assignment 1, `runs/engine-baseline/role-scores.md`) | scores a sponsor with no live posting 0.000 and skips it | keep that sponsor |

The gap, worded as narrowly as the evidence allows: **none that I found** turns a proven sponsor with
nothing open into a networking target, with the record attached. I haven't looked at H1BGrader or
Interstride myself.

## 3. Methods (part 3)

### 3.1 Data (all public; the job seeker is fictional)

| Source | Used for | Label |
|---|---|---|
| 80 Days to Stay sponsorship CSV (in the Reallocation Engine repo) | which companies sponsored data roles | record |
| SEC Form D samples (same repo) | recent funding | record |
| Greenhouse, Lever and Ashby public job-board APIs | which boards exist; what is open today | record |
| [board-resolver/inputs/](board-resolver/inputs/PROVENANCE.md) | the 123 sponsors and 16 confirmed boards from 2026-10-03, copied with SHA-256 | record / your-input |
| Persona "Jack Spencer" (`@example.com`) | the job seeker | fictional |

### 3.2 Step by step

1. **Three checks per sponsor** (prototype, ran 2026-10-03, Assignment 1): sponsored data roles (H-1B)?
   Recent funding (Form D)? An entry-level data job open on its board today? The answers set the verdict.
   Run-2: 123 sponsors → 2 apply · 1 network · 107 check by hand · 13 skip.
2. **The bottleneck:** only 16 of 123 had a known board, so 107 answers were "check by hand".
3. **The board resolver** (built 2026-11-23, [board-resolver/](board-resolver/README.md); rules in
   [CONTRACT.md](board-resolver/CONTRACT.md)). A loop per company: observe → decide the next name-derived
   slug × ATS → act (one GET) → record the raw response with its SHA-256 → stop.
   - Tool policy, in code: GET only, https only, three hosts only; offline unless `--live`; files only in `runs/`.
   - Stops: done · budget (`--budget`) · upstream errors (`--max-errors` in a row) · canary failed
     (a made-up slug must return 404 on every API before the loop starts).
4. **Human gate G1:** the resolver only proposes. `decide` records approve / refuse / defer, and is
   refused unless `--seen-sha256` matches the saved response the person looked at.
5. **Coverage** counts only approved boards. Proposals never count.
6. **Next (will):** re-run the verdicts with the 50 boards, then the evaluation in §4.2.

### 3.3 Resources

Claude Code (my existing access); the three public job-board APIs (no keys, no accounts); Python 3.12
standard library; local Kokoro, Manim and ffmpeg for the film. Paid compute: none. Cost: $0.00.

## 4. Evaluation (part 4)

### 4.1 What has been measured (live run, 2026-11-23)

| Measure | Result | Where |
|---|---|---|
| Requests | 629 GETs, all to the three allowed hosts; stop `done` | `board-resolver/runs/live-2026-11-23/summary.json`, `log.jsonl` |
| Candidates found | 39 companies (38 proposed, 1 mismatch-only); 67 no board under the names tried; 1 timed out | `proposals.json` |
| **Coverage after my review** | **16 → 50 / 123** (34 approved, 5 refused) | `coverage.md`, `decisions.json` |
| Wrong-company boards | 5 caught and refused (e.g. a childcare centre, a different company's talent page) | `decisions.json` notes, `raw/` |
| Name-check false negative | Weight Watchers marked a mismatch; right company | `proposals.json` |
| Approved but weak | 5 empty boards (0 postings) and Rise (unclear): 6 of the 50 | [FRICTIONAL.md](FRICTIONAL.md) Entry 3 |
| Tests | 28 offline, all pass; 5 safeguards mutated, each caught | [board-resolver/README.md](board-resolver/README.md) |
| A bug no test caught | Windows console: approval saved, then the command crashed; regression test added | FRICTIONAL Entry 2 |

### 4.2 How the verdicts will be judged (proposed)

- **Held-out set**, set aside before any tuning: hand-checked sponsors I don't look at again until the test.
- **Pass line (approved by me, 2026-11-23):** at least **9 in 10 apply verdicts right** on that set.
  Below it, the verdicts didn't work.
- **14-day re-check:** re-open the networking targets' boards after 14 days and log whether a posting
  appeared. That tests the hypothesis that recent funding predicts hiring.
- **What this sample can show:** what the tool gets wrong, on a small, public, hand-checked set.
  **What it can't show:** that anyone gets hired.

### 4.3 Known limits

- Lever and Ashby return no company name, so a hit there shows only that a slug exists.
- Short generic names (HUMAN, TALENT) collide with other companies' boards.
- Brand names (Social Finance → SoFi, Neutron Holdings → Lime) need a person to supply aliases.
- Empty boards share one hash, so for them the gate can't prove which board the approver opened.
- [CONTRACT.md](board-resolver/CONTRACT.md) is still Claude's draft, not reviewed or signed by me.

## 5. How the film was made

Script, voice, drawings, gates and captions: [film/README.md](film/README.md),
[film/SOURCES.md](film/SOURCES.md) (who did what), and the gate log
[film/_qc/gates-2026-11-23.txt](film/_qc/gates-2026-11-23.txt).
