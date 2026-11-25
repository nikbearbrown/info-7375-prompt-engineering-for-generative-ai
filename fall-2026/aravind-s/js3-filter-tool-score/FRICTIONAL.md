# FRICTIONAL.md: Job-Search Agent 3

My dated notes while building JS3. The Friday entry is as I typed it. From Sunday on, I write rough notes and Claude
Code organizes them at my request, checks them against the record and adds the evidence line, as the Frictional
guide allows ("AI can organize your notes; you must supply the actual experience"); the experiences and decisions
are mine, and my notes are kept word for word outside the repo. Entries keep the day they are about and say when
they were written.

## Friday 2026-11-20 (written the same night, about 11:30 PM ET)

**Tried and expected.** I ran the agent at 6:39 AM and expected it to process the available job boards, check the postings and show me which jobs matched Jane's requirements. I expected an individual posting with missing information to be handled separately.

**Surprise.** I was surprised that one posting with a blank title caused the entire OpenAI board to be refused. I decided that only the posting with the missing title should be marked as "cannot tell" while the remaining postings should still be processed.

**My changes.** Across the four drafts, I changed the rules based on how they affected actual job postings. I made level restrictions hard again, decided to reject jobs outside the US, made years of experience required by default unless clearly optional, and added more specific rules for locations, start dates and technical keywords.

**Claude's part.** Claude helped review my rules against the saved postings, pointed out problems and suggested changes. After I asked Claude to stop asking me about every remaining decision and make the draft, it prepared Sections 2 to 7, which I can review and adjust.

**Still unsure.** I am still not completely sure whether the 60-point cutoff and the top 10 shortlist are the right choices. I want to see the actual results from the built filter and the audit before deciding whether the scoring and ranking need further changes.

*Evidence:* my run `runs/2026-11-20T113915Z` and the starting-point commit `34aa5d6`; FILTER.md v1.0 in
`66e26d9`, with my four drafts in `filter-drafts/`.

## Sunday 2026-11-22 (written the same night, about 3:15 AM ET; my notes, organized by Claude Code)

**Tried and expected.** I expected the filter to keep most suitable software engineering roles and reject obvious mismatches. I thought the hard part would be deciding whether a job was relevant to Jane, especially when the title looked right but the responsibilities were different. Tonight I judged 55 audit cards (1:20 to 1:37 AM) and 30 held-out cards (2:48 AM), then labeled 105 claims (2:55 to 3:05 AM); each set was committed before its answers were opened.

**Surprise.** The biggest surprise was card 17. I had kept it, and it became the audit's one miss, but the posting requires a U.S. person: the line "U.S. Person Required" was missing from my card because the text splitter cut it at "U.S.". Once I saw the line, I rejected the posting; with that answer the audit has 0 misses in 30 random rejects instead of 1 (upper bound 9.5% instead of 14.9%). I also saw that ordinary phrases can match for the wrong reason: "build systems" (a verb and a noun) gave a kept posting 5 points for developer tools, and "from the start" was picked up as a start-date sentence. I caught both in my labels (09.8c and 09.6). Claude Code found a third in the audit data: "growth", read as a company word by the years rule (card 34).

**My changes.** I first marked claim 09.6 S, because "from the start" was not about the job's start date; when Claude Code pointed to the kit's rule (S needs a passage that states the claim), I changed it to I for the same reason. After reviewing the four disagreements with the checker and the sentences Claude Code found, I changed 05.8d to I and kept the other three labels. I also confirmed that card 17 should have been rejected.

**Claude's part.** Claude Code built the filter, the audit and held-out cards, the claim checker and the scripts that compare my labels with the sealed answers. After card 17 it fixed how the cards split text, so no status line is cut at "U.S." (the filter's own splitter is still on the v1.1 list), and rebuilt the held-out cards before I judged them. It showed me where the checker disagreed with me and found the sentence behind each disagreement. I made every judgment, reviewed the disagreements and decided which labels to change.

**Learned, and still unsure.** I learned that matching a keyword is not enough: the sentence has to describe work that belongs to this role, not just mention a related topic. I am still unsure how the filter should treat vague export-control language when a posting does not say what the legal requirements are; all six of my "?" verdicts came from it or from clearance lines. That is my call for v1.1: whether the line costs points or stays a caution.

*Evidence:* audit verdicts `45fc2c0`, scored in `79df09c` (`js3/audit/2026-11-21T044414Z/RESULTS.md`; card 17 in
`AFTER-REVEAL.md`); the card fix and rebuilt held-out cards `f629b8c`; held-out verdicts `1e2b1e1` (still sealed);
claim labels `1608a04`, scored in `57041c4`, flip checks `cb4943a`.

## Sunday 2026-11-22, after 3:15 AM ET and that evening (written on 2026-11-24; my notes, organized by Claude Code)

**Tried and expected.** Before any v1.1 call I checked two things myself. At 3:18 AM I ran my own test
(`tests/test_aravind_own_rule.py`, written from my R1: an internship posting must be rejected, with R1 deciding), and
it passed. At 3:19 AM I reran `tools/score_audit.py` and `tools/score_claims.py`: the same numbers, and both
RESULTS.md files byte for byte the same. Then I made my three calls for v1.1. I wanted the score to put first the
postings that pass the important requirements, without technical keywords being the only way onto the shortlist.

**Surprise.** I realized that some phrases can look like technical topics without describing the work. "build
systems" was a good example (my claim label 09.8c): it can mean building systems in general, not build tools for
developers. Matching words is not enough; the context matters.

**My changes.** I set the shortlist cutoff at 50, the score every posting starts with, so a suitable posting is not
left off just because it names no extra topic; on my held-out cards a cutoff of 60 had left out 5 of my 12 Keeps (22
of 27 agreed at 60, 27 of 27 at 50). An export-control line now costs 10 points: the posting stays kept, not
rejected, but ranks lower, because the line does not say whether Jane is eligible. I dropped "build systems" from
Developer tools because it created false matches. These three calls are FILTER.md v1.1. I felt more comfortable
signing off after them, and I signed that evening at 8:20 PM ET, although I knew the filter was not perfect and needed
more testing.

**Claude's part.** Claude Code laid out each call with the held-out numbers behind it. I took its recommended cutoff
of 50; on the other two it recommended neither option, and I chose "cost 10 points" over leaving the line a caution
with no points, and "drop it" over keeping "build systems". It then wrote v1.1 around my calls with its two
implementation fixes (the sentence splitter and the company words), applied v1.1 to all 1,509 postings, ran the 82
planted mistakes again, and kept the MCP server on v1.0, the version I had evaluated.

**Still unsure.** My calls came from the held-out results, so that set could no longer test them: when I signed,
v1.1 had not been tested on postings I had not seen.

*Evidence:* my test `3ed19d2`; the recomputation in `js3/SIGNOFF.md`; the held-out measurement `cb1b50c`; FILTER.md
v1.1 `5dff01f` and its run `eb8ebd7`; the held-out set marked development data `4e8089e`; the 82 planted mistakes
again `c9417c6`; the sign-off signed `c8fbb73`.

## Tuesday 2026-11-24 (written the same evening, before the scores; my notes, organized by Claude Code)

**Tried.** I judged 20 fresh cards, postings I had never been shown, to test my three v1.1 calls on labels that
played no part in them. The set was sealed before I saw any card, and my verdicts were committed before its answers
were opened.

**Claude's part.** Claude Code drew the cards by a written rule, sealed the answers and wrote down its predictions
before I saw them. Its first chat version of the cards replaced each description with its own summary, so it
withdrew that version and sent cards made by a script from the sealed file before I judged them. It then scored my
verdicts and prepared the comparison.

**Still unsure.** While judging, I noticed that some roles are hard to classify from their titles and short
descriptions alone. Robotics, machine learning, frontend productivity and infrastructure roles can overlap with
software engineering but may not match Jane's experience equally well. I marked three postings "?" because their
export-control lines do not say who is eligible. I want to make sure the agent does not confuse a related technical
area with a genuinely suitable job.

**The scores** (added by Claude Code from RESULTS.md after the scoring): on the 12 postings v1.1 newly recommends, I
kept 10 and rejected 2, the frontend productivity role (card 03) and the robotics control-systems role (card 05), so
v1.1's cutoff agreed with me on 10 and v1.0's on 2. Those two are the first postings the filter kept that I rejected:
both titles contain "Software Engineer", which my R4 passes, and both scored 50 with no topic group. I marked all three
export-control postings "?", and the five control cards came out as expected.

*Evidence:* the sealed set `9cdf591` (seed 2026112401, predictions in `PREDICTIONS.md`); the chat view and the
withdrawn first version `62df039` (`CHANGES.md`); my verdicts `1bbbcf6`; the scores `c01dc04`
(`js3/fresh/2026-11-22T084738Z/RESULTS.md`).
