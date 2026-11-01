# FRICTIONAL: JS1

Entries are dated by when the work happened. I wrote this log on 2026-10-31 from my notes, the commits and
a factual session log Claude Code kept, so the earlier entries are **retrospective**. The "What happened"
and "Evidence" lines are facts organized by Claude Code. The reflection lines ("I tried / expected", "What I
did", "I understand now", "What I learned", "Unresolved") were drafted by Codex from my review and forwarded
by me. I confirmed the facts in them and made the decisions they describe; the wording is not mine.
Lines marked **In my own words** are mine, written on 2026-10-31.

## 2026-10-29: choosing a board

- **I tried / expected:** I wanted a public board with structured data so the results would be reproducible. I initially picked Cloudflare, but the later rule checks showed it did not give useful matching examples.
- **What happened:** Claude Code probed six public Greenhouse boards (Datadog, Cloudflare, Stripe, Airbnb,
  Databricks, Robinhood) for job counts and SWE/backend titles. I picked Cloudflare, and we saved a raw
  snapshot before writing the contract so its date would be in git first.
- **Evidence:** `083428b` (snapshot only).

## 2026-10-30: the contract, and switching boards twice

- **What happened:**
  - My first contract draft named Datadog. Applied by hand to a live Datadog fetch, my rule gave **0 relevant**:
    6 titles passed the title check, and all 6 failed seniority. Cloudflare also gave 0, because no office was in Boston or a "Remote - US" format.
  - Claude Code checked four Boston-area boards with the same rule. Klaviyo gave 4 of 156, so I rewrote the
    contract for Klaviyo. The Cloudflare snapshot stayed in the repo, unused.
  - In draft 2, Claude Code flagged that I wrote "nine fields" (the JSON has 8), "Claude API request" (we use
    `claude -p`), and that validation rule 8 allowed an empty quote. I renamed the persona to Supriya Sharma.
- **What I did:** I accepted the corrections from nine fields to eight, the CLI wording, and the requirement for nonempty evidence quotes. I also changed the fictional persona's name to Supriya Sharma.
- **Evidence:** `470fae3` (contract, before any code); edits listed in SOURCES.md.

## 2026-10-30: implementation, my test run, run 1

- **What happened:**
  - Claude Code implemented against the contract (`15d6b3f`). I ran the tests myself: 48/48 OK.
  - I ran the live baseline at 23:25:13 UTC, before the UTC date changed, so run 2 the next day would be a second calendar day. 156 postings, 0 reported new (`d093ecf`).
  - Checking the worked example against the real posting showed it says "Postgres", not "PostgreSQL", so my
    rule correctly does not count it (`93687a1`).
  - A development smoke call had Claude answer NOT_RELEVANT on my worked example ("2+ years"), while my rule says RELEVANT.
- **I understand now / still do not:** The first run established the baseline and correctly reported nothing as new. That did not demonstrate Claude judging a newly discovered posting.
- **In my own words, what I expected before run 1:** I expected it to check the jobs, but I wasn't fully clear at first that the baseline would save the IDs and report nothing as new.

## 2026-10-31: run 2

- **What happened:** live run at 16:09:43 UTC: the same 156 ids, **0 new**. 8 postings had a changed
  `updated_at` and none was reported as new, which is the by-id behavior I specified.
- **Evidence:** `26bf8fe`.

## 2026-10-31: the seed, and running steps out of order

- **What happened:**
  - I typed `--seed YOUR_NUMBER` literally from the instructions, then tried `label`, `sample` and
    `experiment` before a selection existed. Each one stopped with "selection.json does not exist yet".
  - After asking what a seed is, I chose 2608 (`9ed2e88`).
- **What I did / learned:** I initially typed the placeholder literally and tried later steps before creating the selection. I learned that the seed makes the shuffle reproducible and the selection must exist before labeling and experiments.

## 2026-10-31: writing the labeling rule

- **What happened:** my point 3 said "up to 2 years". Claude Code asked how that treats a posting that says "2+ years".
  I added: "2+ years" counts as 2 and is acceptable; "3+ years" is Not Relevant (`20b01fb`).
- **Note:** this question came from my worked-example posting, which later landed in the held-out set (see the next entry).

## 2026-10-31: all 20 labels came out Not Relevant

- **What happened:**
  - My 20 labels were all NOT_RELEVANT (`6773f06`). The seed had picked mostly Senior, Staff and Lead roles.
    Only 7 of the 52 engineering postings are non-senior.
  - An always-no prompt would have scored 10/10, so the experiment could not show anything.
  - I chose to add every unused non-senior posting (4) as a disclosed supplement, under the same seed and protocol. My original files were left unchanged (`dbf0ef4`, `04bcea5`, `f9bd958`).
  - I labeled 2 Relevant and 2 Not Relevant.
- **Side issue:** Claude Code first said a `&amp;` I saw was a display bug in its tool. It checked, found the
  tool was fine (it was how the chat showed the output), and said so.
- **Why I decided this way / what I am unsure about:** All 20 original labels were Not Relevant, so an always-no answer would score perfectly. I added all four unused non-senior candidates under a stated rule, while keeping the original results separate. The supplement was chosen after seeing the original labels, which limits the comparison.
- **In my own words, why the supplement:** All 20 labels were Not Relevant, so saying no to everything would get a perfect score. I wanted some Relevant examples too so the comparison would be useful.

## 2026-10-31: sampling and the prompt experiment

- **What happened:**
  - Sampling: 20 calls, all valid and unanimous. On SE II Test Frameworks, Claude said NOT_RELEVANT 4/4 against my RELEVANT,
    each time because "2+ years" is "above New Grad".
  - I chose the one change: a sentence stating my experience threshold. Dev 11/12 → 12/12; held-out 11/12 → 12/12.
  - The held-out gain is one posting, and it was my worked example.
- **Evidence:** `76bd1ce`, `d932e3b`, `d10abd6`, `914d40d`; `sampling/REPORT.md`, `experiment/REPORT.md`.
- **What I learned:** Claude gave the same wrong answer four times on the Engineer II posting, so consistency did not establish correctness. Stating my experience threshold fixed that case, but the held-out gain was only one posting and it was already familiar.

## 2026-10-31: action surfaces

- **What happened:** I pasted the filled prompt into claude.ai and pasted back its reply. Claude Code ran the
  file-read version. Both said RELEVANT and both passed the validator. I chose the watch (`7cde01c`, `a13d3ca`).

## 2026-10-31: reviewing the drafts with Codex

- **What happened:** I used Codex to review Claude Code's drafts. It reran the tests on Python 3.9.6 and
  3.12.15, checked the saved response hashes, and confirmed 0 new ids and 8 changed timestamps. Its findings:
  1. `posting_field: []` made the validator crash with `TypeError` instead of recording a validation failure;
  2. the comparison used an experiment verdict as the watch's result, but the live runs judged no new posting;
  3. the full file-read envelope and tool trace were not saved, so those claims had to be narrowed;
  4. the watch defaults to `baseline-v1` while the comparison used `revision-v2`;
  5. placeholders and premature claims that I had signed or confirmed my review.
- **What I did:** I asked Claude Code to address all five before the final version, and not to push yet.
- **Evidence:** the validator fix with a test that fails without it (`c42f2c6`); the corrected
  `action-surfaces/COMPARISON.md`, README and SOURCES (the commit after `c42f2c6`, "docs(js1): address the review findings").
- **Done since:** the validator crash, the action-surface evidence claims and the default-prompt explanation
  were fixed in `c42f2c6` and `1ec6051`.
- **In my own words, what I still cannot explain confidently:** I understand that the seed makes the split repeatable, but I still couldn't confidently explain how the shuffle works internally.
- **Unresolved / next step:** finish my personal review, decide whether any additional demonstration is
  needed, then matching GitHub and Canvas delivery. The signature stays withheld until my review is done.
- **Later, 2026-10-31:** I finished my review and signed the sign-off. Then I asked Claude Code to post the
  folder to GitHub and build the Canvas zip.

## 2026-10-31: second Codex review, and a seeded watch replay

- **What happened:**
  - Codex's rubric review found more: a stale test count; authorship credit for the reflection and sign-off wording
    it had drafted; stale "next steps"; surface 3 never actually judging the posting; held-out wording that
    needed to stay explicit; and `scripts/validate_course.py` failing because of files elsewhere in the
    course repository (none in this folder).
  - At my request, Claude Code ran one seeded replay of 7855793003 through the real watch with `revision-v2`:
    run 2's unmodified response and a scratch state with that id removed. Result: one real Claude call, valid;
    rule and Claude both RELEVANT. The committed state and live runs were not changed.
  - The saved seeded report says "this file was modified on purpose", which is wrong for this run (the state was
    seeded, not the file). The template was corrected afterwards, and the saved report was left as written.
  - Claude Code had earlier told me in chat that the course validator passed; it had read only the last line of the
    output. It does not pass.
- **Evidence:** `action-surfaces/3-watch-seeded/NOTES.md`; the commit "docs(js1): seeded watch replay, Codex credit,
  held-out and validator wording".
