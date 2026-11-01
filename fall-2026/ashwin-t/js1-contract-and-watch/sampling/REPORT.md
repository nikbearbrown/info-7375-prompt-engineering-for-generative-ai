# Sampling report (Chapter 1)

**Question:** if Claude is asked the same contract question about the same posting in fresh
conversations, how much do its answers vary, and does agreeing with itself mean it is right?

Drafted by Claude Code from the saved data (see SOURCES.md for who did what).

## What ran

- **Command:** `python3 -m jobwatch.lab sample` (default `--repeats 4`, prompt `prompts/baseline-v1.md`,
  sha256 `761f24fb…`), run by Claude Code at the repository state `f9bd958`.
- **Calls:** 5 postings × 4 asks = **20 real `claude -p` calls**, each a new session (`--no-session-persistence`,
  no tools, empty working folder). Model reported: `claude-opus-5-5`. First call 2026-10-31T17:56:25Z,
  last 17:56:51Z. All 20 replies are saved unedited in `2026-10-31T17-56-56Z/replies/`, with the
  table data in `results.json`.
- **Postings:** the five in `experiment/supplement.json` → `sampling`: the two supplement dev postings plus the
  first three original dev postings. All five are dev postings; no held-out posting was shown to Claude here.
  (The original plan sampled `dev[:5]`, five Senior titles. It was changed after the hand labels came out
  all NOT_RELEVANT. See `experiment/REPORT.md` and FRICTIONAL.md.)
- **Hand labels:** Ashwin's, made before any of these calls, under `experiment/LABELING-PROTOCOL.md`.

## Results

| Posting | Title | Ashwin's label | Rule record | Claude, 4 asks | Agrees with Ashwin |
|---|---|---|---|---|---:|
| 8041054003 | Software Engineer, Conversational Products & Agent Workflows | NOT_RELEVANT | RELEVANT | N N N N | 4/4 |
| 7855793003 | Software Engineer II, Test Frameworks & Tooling | RELEVANT | RELEVANT | N N N N | **0/4** |
| 8012938003 | Senior Software Engineer - Data Automation | NOT_RELEVANT | NOT_RELEVANT | N N N N | 4/4 |
| 8017125003 | Senior Lead AI Engineer - G&A Systems | NOT_RELEVANT | NOT_RELEVANT | N N N N | 4/4 |
| 7780009003 | Senior Software Engineer, Applied AI (Customer Agent) | NOT_RELEVANT | NOT_RELEVANT | N N N N | 4/4 |

- **Valid replies:** 20/20. Every reply passed the contract's validator: bare JSON, the right posting id, and
  every quote found in the posting.
- **Verdict spread:** none. All five postings were unanimous (4/4 the same verdict).
- **Agreement with the hand label:** 16/20 calls, 4/5 postings.
- **Where the spread was:** in the evidence, not the verdict. The number of evidence items per reply
  varied from 3 to 6 (on 7855793003: 4, 5, 4, 6), and on three postings the set of résumé fields cited
  changed between asks. On 7855793003, the fourth reply added a hedge the other three lacked: "A reviewer
  could reasonably override this…".

## What this shows, and what it does not

- **Repeatable is not correct.** On 7855793003 Claude was perfectly consistent, and wrong by Ashwin's
  label all four times. Every reply gave the same reason: "Software Engineer II … 2+ years … above a
  New Grad level." The prompt never said what experience a New Grad can apply with, so Claude used a
  stricter reading than Ashwin's protocol (point 3 accepts "2+ years"). Asking more times would not have
  found this. Only the hand label did.
- **Claude and the written rule fail differently.** On 8041054003 ("3+ years") the rule says RELEVANT, because
  it has no experience check, while Claude and Ashwin both say NOT_RELEVANT. On 7855793003 the rule and
  Ashwin agree and Claude does not.
- **Limits.**
  - Five postings, three of them easy Senior titles, is too few to estimate a variance rate.
  - "0 verdict flips in 20" means no flip was seen at this setting on these postings, not that flips cannot happen.
  - All calls ran within 30 seconds on one model and one prompt; another day, model version or prompt
    wording might differ.
  - The labels are one person's judgment.
- **What it changed:** it pointed directly at the one sentence tested in the prompt experiment.
