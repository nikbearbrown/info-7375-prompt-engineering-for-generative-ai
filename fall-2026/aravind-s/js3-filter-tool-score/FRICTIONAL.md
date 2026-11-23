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
