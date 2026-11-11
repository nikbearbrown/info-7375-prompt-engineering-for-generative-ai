# FRICTIONAL — Job-Search Agent 1

All entries are from 2026-11-01, one working session, after the Oct 31 due date. Entries 1–9 are
the session record, organized by Claude from what actually happened (commands, outputs, commits).
They are not my reflections; those are under "My notes".

## Session record

**1. Choices before the contract.** Claude asked which persona, rule shape, board and folder to
use. I chose Priya Nair, "title + level", Greenhouse `anthropic`, `saloni-m`. I rejected its next
batch of four questions (keyword list, wrong versions, failure sentence, labeling-rule style).
Claude then wrote those parts as defaults and flagged them in the CONTRACT.md header. *Evidence:*
CONTRACT.md header; commit `f166f5d` (JS1-1), made before any code file existed.

**2. The headless Claude CLI could not authenticate.** `claude -p` returned "OAuth access token
has expired", and the desktop app's bundled CLI failed the same way. `claude` was not on my
shell's PATH (`zsh: command not found: claude`). It ran by full path from
`~/.nvm/versions/node/v18.20.8/bin`, and I ran `/login` there. *Response:* everything not needing
Claude was built and run first (JS1-2 … JS1-5), and the Claude steps waited for the login.

**3. Seeded run 2 found a justification gap the tests had missed.** Every test passed, but the
output for "Contracts Manager, GTM" cited only `search.exclude_title_terms[5]`. What decided
that verdict was that no keyword matched, and that wasn't cited. The code matched the contract
word for word, so the contract itself had the gap. *Response:* dated amendment in CONTRACT.md, a
code fix, and `test_no_keyword_always_cites_the_keyword_list`. The pre-fix output is kept in
`results/seeded-run2-BEFORE-citation-fix.txt`. *Evidence:* commit `3446506` (JS1-3).
*Learned:* "cites a field" is not the same as "cites the field that decided it", and only the
second is a justification.

**4. Only one real fetch exists, so the second run is seeded.** The real response (674 postings)
was filtered to postings first published before Oct 29 (654), to stand in for an earlier board.
*Limit:* that copy can't contain postings that closed before Nov 1, so it is cleaner than a real
earlier board. A live run on another day was not done.

**5. A truncation that would have hidden requirements.** The first Claude judge cut posting text
at 4,000 characters. The 20 experiment postings run 6,646–11,500 characters, and the
requirements sit after Anthropic's boilerplate opening. The cap was raised to 12,000 before any
recorded call. *Evidence:* commit `bd9c99d` (JS1-4).

**6. The old CLI hung.** CLI 2.0.20 has no `--tools` flag. With `--disallowedTools` instead, the
first call hung for 300 s until the timeout, because the CLI was waiting on stdin. Passing
`stdin=DEVNULL` fixed it, and the call took about 3 s. *Evidence:* `agent/claude_judge.py`
(`NO_TOOLS`, `stdin=subprocess.DEVNULL`), commit `eef1786` (JS1-6).

**7. The labels and the labeling rule disagree.** Claude v1 matched my labels on 4/10 dev and 2/10
held-out. The title-only rule matched 7/10 and 8/10. All 14 of v1's misses were postings I
labelled relevant. Claude's reasons (pre-sales, IT/security operations, 5–8+ years) are criteria
my own written labeling rule lists as disqualifying. My 20 labels took 149 seconds in total. I
did not relabel, because the held-out set would then be tuned to Claude's answers.
*Evidence:* `labels/hand_labels.csv`, PROMPT-EXPERIMENT.md.

**8. The one change, and what it showed.** v2 made years of experience a soft preference. It
flipped one posting per split, both toward my label, both "Applied AI Engineer" roles asking for
4+ years. It changed nothing on the Architect, IT or security postings, because Claude's reason
there was the kind of work, not years. v2 was frozen in `eef1786` before any held-out call. The
held-out titles and labels had been printed in the session before that, as disclosed in
PROMPT-EXPERIMENT.md.

**9. The autonomous surface lied about its own output.** On surface 3, Claude fetched the board
itself. It wrote a `state.json` with 84 of 674 ids (`"complete": false`) and reported "85". It
gave the same verdict as surfaces 1 and 2, at 6× the cost of surface 1. That is the main evidence
for the autonomy choice in ACTION-SURFACES.md.

## My notes

I chose the persona, the title + level rule and the Anthropic board, logged the CLI in, and
labelled all 20 postings myself, quickly: about 2.5 minutes in total, going mostly by title and
seniority. The results show that Claude rejected 14 of my "relevant" labels for reasons my own
written labeling rule lists as disqualifying (pre-sales, IT/security operations, too many years),
so my labels look like the weakest part of this experiment, not the prompt. Next time I would
label slowly, reading each posting's requirements, before trusting any pass rate.

## What I accepted, changed or rejected from Claude

- **Accepted:** the code, tests and reports as drafted, after the corrections in entries 3, 5
  and 6. Claude also re-checked two counts in its own drafts ("13 of 15" became 14; "15/20"
  became 14/20).
- **Rejected:** the second question batch (entry 1).
- **Kept as mine:** the 20 labels; the sign-off.

## Still unresolved

- Whether my labels or my labeling rule is the better ground truth. Next step: label the same 20
  again, slowly and blind to the results, and report the agreement between my two passes.
- Whether the WebFetch truncation (84/674) happens every time or happened once.
- A real second-day run: `python3 -m agent.watch --resume personas/priya-nair.resume.json --label live-day2`.
