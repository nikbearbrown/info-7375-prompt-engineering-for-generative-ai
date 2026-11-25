# Prompt experiment (Chapter 2)

**Ran:** 2026-10-31 · **Model:** claude-sonnet-5-5 via `claude -p` (fresh process per posting, no tools) · **Script:** `experiments/prompt_experiment.py`
**Written by:** drafted by Claude from `experiments/results/*.json`. The labeling rule, the hand labels and the choice of the one change are mine (Vrajesh).

## Labels
- **Labeling rule, written first:** CONTRACT.md, Rule R1–R4 (closed 2026-10-31, before any labels).
- **Postings:** 20 real postings from the 2026-10-31 live Commure fetch (`data/raw/2026-10-31/ashby_commure.json`), chosen by `experiments/make_label_sheet.py` with seed 7375.
  - The first plain random draw had no plausible-relevant posting, so "always not_relevant" would have scored 20/20. I discarded it before labeling.
  - The redraw is stratified: all 9 non-senior software titles, 7 senior software titles and 4 others, split alternately into 10 dev and 10 held-out.
- **The label sheet did not show the rule's verdict.**
- **Hand labels** (`experiments/labels.csv`): my reply in chat, 2026-10-31, was "5,16 yes other's No i guess". So relevant = #5 Software Engineer, AI Integrations (dev) and #16 Software Engineer, Scribe AI (held-out).
- **One label changed after seeing results:** #8 Fullstack Engineer, Ambient AI (dev) went from not_relevant to relevant after the first baseline dev run showed my rule disagreed. My words: "Oh i Labeled it yes at start, let me look into it more, i also think it's yes". This is a dev label, but it was changed after seeing model and rule output. The first run is kept as `results/baseline-dev-labels-v1.json`, where Claude scored 9/10 and the rule 9/10.

## Prompts
- `experiments/prompts/baseline.txt`: my own 10-24 contract words plus the fixed JSON output format.
- `experiments/prompts/revision.txt`: the same, plus **one** sentence (my choice, from options Claude offered):
  > Sponsorship is a blocker only if the posting itself says it will not sponsor; the candidate needing sponsorship is not a blocker on its own.

  Why this change: in the baseline dev failures, Claude named "the candidate needs sponsorship … blocker". `diff baseline.txt revision.txt` shows only that line.

## Results (pass = Claude's verdict equals my hand label; a rejected answer counts as a fail; none were rejected)

| Prompt | Dev (n=10) | Held-out (n=10), run last with `--final` |
|---|---|---|
| baseline | 8/10 | 9/10 |
| revision | 8/10 | 10/10 |
| written rule (for comparison) | 10/10 | 10/10 |

Failures:
- **Dev, baseline:** #5 AI Integrations ("needs visa sponsorship (F-1), which the criteria treat as a blocker, and … 2+ years") and #8 Ambient AI ("requires sponsorship … not entry level").
- **Dev, revision:** the same two postings. The sponsorship reason is **gone** ("with no stated sponsorship refusal"), but Claude still says not_relevant: "2+ years of professional experience, which is not entry level" and "asks for professional experience … mentoring … not entry level".
- **Held-out, baseline:** #16 Scribe AI ("needs visa sponsorship (F-1) … 1-4 years … lacks iOS/Swift").
- **Held-out, revision:** none.

## What this shows, and how little
- The change did what it targeted. Claude stopped treating the candidate's own sponsorship need as a blocker in every failing case I read.
- On dev it did **not** change a single verdict. Under the sponsorship reason sat a second disagreement: what "entry level" means. My rule says 0–2 years is fine; Claude treats 2+ years, or "professional experience" with no number, as not entry level. I did not make a second change, because the assignment allows one.
- On held-out the revision gained one posting (Scribe AI, 9 → 10). That is **one posting out of ten**. With n=10, one flip is well within what re-running the same prompt might change, since I ran each prompt once per posting. It is not evidence that the revision is better in general.
- Both sets are mostly easy negatives: 8 of the 10 held-out postings are senior, non-US or sales. Only 2 postings per set are labeled relevant, so the real test is about 4 postings across both sets.
- The written rule's 20/20 is close to circular: I labeled with that same rule. It shows the code computes what I wrote, not that the rule picks good jobs.
- One company, one day, one model, one fictional resume.
