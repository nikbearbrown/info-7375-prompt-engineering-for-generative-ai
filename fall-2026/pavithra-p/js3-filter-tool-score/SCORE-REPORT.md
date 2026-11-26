# What moves the score (Chapter 9)

What changes this system's behaviour: training, prompts, context, tools or settings? For each number in it, where it came from, then one change at a time, measured on labels I held out.

## 1. Every number, and where it came from

"Hand-set" means I chose it, with Claude's help, without fitting it to labels. "Fitted on my labels" means it was chosen by comparing candidates against my tuning labels (by hand, not by an optimiser). "Inherited" means it came from my earlier work, a source, or a default.

| Object | Number | Value | Origin |
|---|---|---|---|
| Filter file | S1 full role points | 3 | hand-set, so that a full role title plus two skills reaches the v1.0 threshold, as JS1's rule did |
| Filter file | S1 plain Engineer or Developer points | 1 | hand-set (new in JS3, no data behind it) |
| Filter file | S2 points per skill, and the cap | 1, at most 5 | hand-set |
| Filter file | Threshold | 5 in v1.0, 4 in v1.1 | v1.0 hand-set (equal to JS1's "role and two skills"); v1.1 fitted on my tuning labels (change A) |
| Filter file | Close-call band | scores 4 to 5 (v1.0), 3 to 4 (v1.1) | hand-set: the threshold and one point below it |
| Filter file | G3 years limit | 3 in v1.0, 5 in v1.1 | v1.0 inherited from JS1 rule 3 (`fall-2026/pavithra-p/js2-loop-tools-diff/CONTRACT-JS1.md`, a copy of my JS1 contract); v1.1 fitted on my tuning labels (change B) |
| Filter file | A range counts as its lowest number | | inherited from JS2 (`0ecb3d5`) |
| Filter file | Role, seniority and US word lists | | inherited from JS1 rule 1, 3 and 4 |
| Filter file | US city list (change C) | 8 cities with their state | hand-set from the locations seen in this collection |
| Filter file | Skills | 15 skills in 4 lists | inherited from the fictional persona (Reallocation Engine example, `d08afdd`) |
| Shortlist | Size | 8 | hand-set: about as many as I would read closely at once |
| Claude prompt (`prompts/justify-v1.txt`) | Claims per posting, quote length | 4 or 5 claims; one each for role, experience and location; quotes at most 30 words | hand-set |
| Claude prompt (`prompts/judge-v1.txt`) | Verdicts and reply shape | yes, no or cannot tell, with one sentence | hand-set |
| Context given to Claude | What of the posting Claude sees | full posting, or title and location only | hand-set; the one change in section 2b |
| Claude setting | Model | the Claude Code CLI default on the day (`claude-opus-5-5`) | inherited (I did not choose a model) |
| Evidence checker | Years that contradict "about two years fits" | 3 or more | inherited from JS1 rule 3; kept at 3 when G3 moved to 5, because a claim about Rohan's fit is not the filter's tolerance |
| Audit | Seed, sample sizes | 20261125; 30, 6, 20 | hand-set (30 is the brief's minimum) |
| Audit | Interval | 95% Wilson | inherited convention |
| Collector | Budgets | 10 requests, 60 s, 10 s timeout, 2 s retry wait | inherited from my JS2 `GATE.md` (`fall-2026/pavithra-p/js2-loop-tools-diff/GATE.md`) |
| Tool server | job_id length | 1 to 64 | hand-set |

Nothing in this agent is trained. No number was learned by a model, and my labels were never sent to Claude: in section 2b, Claude saw only the posting and the persona.

## 2. One change at a time, on the held-out labels

The 20 held-out postings (FILTER.md section 7, `AUDIT.md` section 2) were drawn before I labelled and were not used to choose any change. The choices were committed in `70ddf4b` before this measurement ran.

Each row is v1.0 with exactly one change, made in one object (the filter file):

```bash
python3 -m agent measure filters/v1.0.json filters/changes/A-threshold-4.json filters/changes/B-max-years-5.json filters/changes/C-us-cities.json filters/changes/D-helm-case.json filters/changes/E-senior-in-text.json filters/changes/G-drop-intern-staff.json filters/v1.1.json
```

| Filter file | Tuning sets (48): agrees with my label | Held-out (20): agrees with my label | Held-out kept | Held-out false keeps | Held-out false rejects |
|---|---|---|---|---|---|
| v1.0 | 35 | 13 (95% Wilson 43% to 82%) | 0 | 0 | 7 |
| A threshold 4 | 38 | 13 | 0 | 0 | 7 |
| B years limit 5 | 37 | 13 | 0 | 0 | 7 |
| C US cities | 35 | 13 | 0 | 0 | 7 |
| D Helm as written | 35 | 13 | 0 | 0 | 7 |
| E senior in the text | 35 | 13 | 0 | 0 | 7 |
| G (rejected) Intern and Staff allowed | 37 | 13 | 0 | 0 | 7 |
| v1.1 (A to E) | 40 | 13 | 0 | 0 | 7 |

My held-out labels: 7 yes, 13 no, 0 cannot tell. No filter version kept any held-out posting, so every version found 0 of my 7 yes postings (recall 0 of 7), and its 13 agreements are all postings it rejected and I said no to.

## 2b. One change to a second object: the context Claude is given

The filter file is one object. To test a different one, Claude judged the same 20 held-out postings twice with the same prompt (`prompts/judge-v1.txt`) and the same model. The only change was the context: the full posting, or the title and location only. These were real calls (`python3 -m agent judge full` at 21:59:56 UTC, `python3 -m agent judge title` at 22:00:27). Every reply is saved in `runs/20261125T204144Z/judge-full/` and `judge-title/`. All 40 were valid. Claude's "yes" counts as keep; "no" and "cannot tell" both count as not keep, so a "cannot tell" on a posting I said no to counts as agreement.

| Context | Agrees with my label (20) | Claude said yes | cannot tell | False keeps | False rejects |
|---|---|---|---|---|---|
| Full posting | 13 (95% Wilson 43% to 82%) | 4 | 0 | 2 | 5 |
| Title and location only | 13 (43% to 82%) | 0 | 9 | 0 | 7 |
| For comparison: filter v1.0 and v1.1 | 13 | 0 kept | | 0 | 7 |

* The change moved Claude's behaviour a lot: 9 of the 20 verdicts differ between the two runs. With only the title, Claude said "cannot tell" on 9 postings and yes on none. With the full posting, it said yes on 4, and 2 of those are postings I said yes to and every filter version rejects ("Software Engineer, Growth Platform" and "Software Engineer, Backend, Accounts Receivable").
* The agreement count did not move: 13 of 20 both times. The same number hides different mistakes (2 false keeps against 0, and 5 false rejects against 7). One number is not enough to say whether a change helped.
* As in section 2, 20 postings cannot show a small difference.

## 3. What this shows, and what it does not

* No change moved a single held-out verdict. The gain on the tuning sets (35 to 40 of 48) did not carry over. On this evidence I cannot claim v1.1 is better than v1.0: it is better on the postings I chose it from, and the same on the postings I held out.
* After measuring, I looked at why. Of the 7 held-out postings I said yes to, v1.1 rejects:
  * two Staff titles (G2, which I kept on purpose);
  * two that ask for 5 years (B moved the limit to 5, not past it);
  * two whose descriptions name none of the résumé's skills, one of them now caught by G4 because its text asks for a senior backend engineer;
  * one Solutions Engineer title (score 2).

  Any change I made from that look would be fitted on the held-out set, so I made none.
* The way the held-out set was drawn made this result close to certain, and that matters more than its size. The held-out pool (82 US engineering postings) excluded every posting already in the audit, and the audit's "kept" set held all 7 of v1.0's keeps. So:
  * v1.0 could keep none of the held-out postings, by design;
  * of v1.1's 8 new keeps, 7 were in the tuning sets and only 1 was in the pool at all (Spotify, Backend Engineer - Data Infrastructure), and it was not drawn.

  The held-out set could show false rejects, but almost no false keeps, for any version. It was close to blind to the changes I made. This is a flaw in my design, found in review. A fair held-out set would be drawn first, at random from all postings, or stratified by the filter's verdict so it holds keeps, close calls and rejects, before anything is put into the tuning sets.
* With 20 postings and 7 yes labels, a change that fixed one posting would move agreement by 5 points, well inside the 43% to 82% interval. So even a well-drawn set this size could only show a large improvement.
* My second pass on the 27 engineering postings in the tuning sets (`AUDIT.md` section 8) agrees with v1.0 on 21 of 27 and with v1.1 on only 18. Changes A and B fitted my first, quick labels; by my second labels they made the filter worse on those postings. I kept v1.1 as the version the shortlist and the tool use, and I state this here instead of claiming v1.1 is better.
* The labels are my own quick labels (`AUDIT.md` section 3). Four of the seven held-out yes labels are Staff titles or 5-year asks, which my own FILTER.md rules out for Rohan. So part of the disagreement is between my rules and my labels, not a fault of the filter.

## 4. Persistence is not proof of training

Behaviour that changes across sessions in this project, and why none of it is training:

* The state file. `runs/state/seen_ids.json` makes the next `watch` report fewer new postings than the first. It changed because a file was saved, not because the agent learned anything.
* The filter file. v1.1 keeps 15 postings where v1.0 kept 7, because I edited a JSON file. Its numbers were set by me (section 1), not learned.
* Claude. If Claude writes a different justification for the same posting tomorrow, that can come from sampling, a change in my prompt or context, or a model update by Anthropic. None of it means Claude learned from my labels: they were never sent to it. Claude Code's own memory and CLAUDE.md files persist between sessions as text that is read into the context, which is also not training. That is why every Claude call here runs from an empty folder (`agent/shortlist.py`, `scripts/transcript_claude_client.py`).
* The tool. Claude can score a posting in one session and not in another only because the tool server was or was not listed in that session's configuration. That is the tool list changing, not Claude.

## 5. Honesty notes

* While checking that the two corrections changed only two labels, Claude Code ran a `diff` that printed about 25 row numbers with their labels (no titles), before the changes were chosen. Those rows were not matched to the held-out set. The changes were chosen from `python3 scripts/tune_changes.py`, which reads only the tuning sets.
* The tuning numbers count the 48 distinct tuning postings. Two kept postings are also close calls and are counted once.
