# FRICTIONAL.md: Job-Search Agent 3

Deepak Kumaran T S · INFO 7375 · fall 2026

I write an entry at each gate, with the real time, while the episode is fresh. Any entry written later is marked (retrospective). Claude Code wrote nothing of its own in this file; at my request it inserted my blocks verbatim. If an AI tool helps me organize or phrase an entry, I say so in that entry.

## Entries

I wrote these entries after the work, from private/SESSION_LOG.md and the commits, with help from a claude.ai chat to organize them. Where an entry uses my words from the chat, it says so.

### 2026-11-25, before 13:21 ET: planning JS3 (retrospective)
- Tried / expected: to extend JS2 into a filter, a tool server and a score.
- What happened: the plan found that JS2 never fetched Greenhouse descriptions, and that a random held-out set would hold almost no relevant postings.
- What I did: accepted collecting with content=true and a two-stratum held-out design.
- Claude: the claude.ai chat proposed both; I accepted them.
- Understand now: a filter about posting text needs the text collected first.
- Evidence: cce270f, 3fe5a78.

### 2026-11-25, Gate 1 (committed 494cfdd): three Claude Code review rounds of FILTER.md, plus a claude.ai critique (retrospective)
- Tried / expected: a filter document I could commit quickly.
- What happened: Claude Code's reviews found missing items, contradictions, gaps the code would have decided, and a rule that did not fit the earliest phase (K1).
- What I did: decided every item, and some differently from the suggestions (U2, S1, X08). In my words at the time: "C1 surprised me most. A missing location and a known unsuitable location are fundamentally different." And: "I accept the resulting false negatives as a deliberate v1 limitation" (primary location only).
- Claude: Claude Code reviewed; the claude.ai chat proposed wording; I chose.
- Understand now: a deterministic filter needs every tie, order and missing case written down.
- Evidence: 494cfdd (the later clarification commits 9c3a903 and 685d231 came at Gates 2 and 3a).

### 2026-11-25 15:17 to 16:38 ET: labeling went wrong three times (retrospective)
- Tried / expected: to label the held-out and audit sheets once.
- What happened: my first audit pass marked jobs like Corporate Counsel relevant; I likely read r as "reject". The second pass changed only 5 rows. The checklist pass still had 15 answers contradicting the questions, and override reasons like "yes". My held-out relabel committed an empty file (e6fe828).
- What I did: chose to stop relabeling for time (Option B), restored my first held-out labels (3d130ae), and disclosed all of it.
- Claude: Claude Code's consistency checks caught each problem; the claude.ai chat proposed the checklist and family modes. I did not finish the family pass.
- Understand now / still do not: my labels are the weakest part of this submission. I still do not know how many of my held-out labels are mis-keys.
- Evidence: ad58e97, 2c9665e, 65c9863, f0568bc, e6fe828, 3d130ae.

### 2026-11-25, Phase 3d to 4: rule changes and the shortlist (retrospective)
- Tried / expected: that at least one of C1 to C5 would help.
- What happened: all five were rejected by my criterion; the shortlist has 3 postings, and I labeled all 29 claims supported.
- Claude: Claude Code measured the changes and ran Step 2 before I said "labels done", and skipped the Gate 4a stop. I accepted the results but recorded the deviation.
- Understand now: a posting can match my words and still not support the claim they suggest ("statistical inference"), and my own verdicts can disagree with a note in my own spec (Forward Deployed).
- Evidence: 41caa97 to 6bccd02, cec6a48.

### 2026-11-25, Phase 5: the tool server (retrospective)
- Tried / expected: a server speaking initialize, as the brief describes.
- What happened: the probe showed Claude Code opens with server/discover (2026-07-28), so the server targets that revision. The real client session read my sealed held-out file with its own tools.
- Claude: Claude Code built and ran both servers.
- Understand now: a protocol does not limit what a client can read; the client's permissions do.
- Evidence: 4680a75, ae74ac0, 4bcabca.

### 2026-11-25, Phase 6: null results (retrospective)
- Tried / expected: to see a change move the score.
- What happened: every filter arm rejected all 40 held-out postings, and the judge said "not relevant" 120 times out of 120.
- Understand now / next step: the filter is too strict for any of these changes to show; the next step is relabeling the held-out set properly and testing C2.
- Evidence: 3f782ce, fefe60e, db0670b.
