# FRICTIONAL — honest log

I started JS3 by writing FILTER.md before any code, as in JS2. I made the decisions and Claude Code drafted the wording, the code and
the tests. What made this assignment hard was not the code. It was finding out that my own labels, my own audit and Claude's claim
labels each needed checking, and that a sample of 30 can say much less than it seems to. This log goes through those moments with the
commits, prompts and tests behind them.

## 1. Starting point and the filter before the build

I set up a new local repo and copied only what JS3 builds on: my JS2 code, tests, config, the Evan Gordon persona and the Oct 31
baseline (c09a161, 113 tests passing). FILTER.md v1 came next (5813935), before any JS3 code. Claude had put placeholder numbers in
the score, so I said "ask me the placeholder and i will answer them". The questions it then asked turned the guesses into my choices.

## 2. My decisions on the filter

I asked "can you make it so the max is a 100 point system?", which became 8 points per skill (at most 8 skills), +16 for years,
+10 for Boston or +5 for remote US, and +10 for visa sponsorship (aa8b063). Then I asked "is it possible to add visa sponsorship rule
now in the new filter?". When Claude proposed making it a hard rule, I said instead "Allow all jobs that fit, just job that offer
sponsorship get points for sponsorship". So visa only adds points and never rejects a posting. I added the BI titles. I also corrected
the years preference: "3 years or less is preferred but consider and jobs asking for up to 5 years". Claude pointed out that v1.1 had
actually given the bonus for 4 or fewer, so this became v1.2 (33062cb). I kept "Data Engineering" out of the role phrases (whole
phrase only), and it later showed up as a false friend.

## 3. The snapshot

JS2's Greenhouse responses had no job descriptions, so the filter could not run on them. A fresh snapshot with `?content=true` took 10
read-only requests and returned 2,629 postings (acf136d). Kraken was empty again and the 404 board was "not observed", as FILTER.md
predicted. The raw files came to 33 MB, so I chose to gzip them, which got them down to 2.7 MB. The sha256 of the original bytes is
checked every time the snapshot is loaded.

## 4. Shaping the label sheet

I chose to label every data-related title (141 postings), not a smaller sample. Then I cut it down: "remove the ones which are
outside the US. Don't remove the remote jobs" (1075876), and "I don't what any job posting that requires 6 years of experience or
more". Claude listed all 25 removals with the quoted years phrase before deleting anything (092b255). That list showed a posting the
filter's own years rule would read wrong: "3+ years managing" followed by "7+ years in software development". Later I asked for the
labeling tool to "also add years expereince requirement mentioned and also if sponsorship details are mentioned". The first posting it
showed asked for "10+ years" and had slipped through the cut, because "experience" was more than 60 characters away. Ten more like it
were removed in place (532ecc3). By narrowing the sheet I gave up the chance to test the location and years rules with my labels, and
REJECT_AUDIT.md says so.

## 5. Three labeling windows at once

When Claude went to remove those ten postings, it found three copies of the labeling tool running in my terminals. Each copy saves
the whole file, so they could have silently overwritten one another's labels. Claude did not change the file until I had closed all of
them, and it then checked that my 12 saved labels and every other row were unchanged.

## 6. My labels broke my own rule

After the first pass, 22 postings were labeled relevant, and 11 of them broke rule 1 of my own labeling rule: Data Scientists, a sales
analyst, a customer-success analyst, a product manager. Most of my notes just said "data role". That is the same mistake I made in JS1:
labeling by title. I saved the first pass as its own file (7037135) and did a second pass with --redo. I changed exactly the 11 that
Claude had listed, all from relevant to not relevant (f5f97ba). That means the second pass was steered by Claude's list, in one
direction only, and I am recording that here. The held-out hash was locked in the same commit, before the filter had ever run on the
snapshot.

## 7. The audit agreed with everything, which was the problem

I judged 36 postings: 30 random rejects, the only closest call, and all 5 kept postings. I first marked all 36 as right. One of them
was the Zoox "Contract Student Worker - Data Analyst (Part-time)". In my blind label I had called it not relevant ("not data role"). In
the audit, after seeing that the filter kept it, I called it a "relevent data role". When Claude pointed out the conflict, I asked "what
do you recommend for this project?". I went with the blind label, so the verdict is now "wrong", and both answers are in the row
(2003644). 0 wrong out of 30 random rejects only bounds the error rate at about 9.5%. The errors that mattered (7 of my 11 relevant
postings rejected by the role rule) never showed up in the random sample, only in my labels.

## 8. The tool server's own claims

Claude wrote the server from scratch, with tests first (59f714c). The dry runs disproved two of the claims I was about to make about
it (8f8d9ac). First, the tracing hook missed the persona file being read, because the read happens while the code loads. Second, once
the hook was installed earlier, the trace showed the Python interpreter writing a .pyc cache file, so "writes no files" was false
until the server was started with -B. The real transcript (c9f7d71) showed a third problem: a rejected Canada posting comes back with
score 64, higher than kept postings.

## 9. The other server

I chose to evaluate the official fetch server. At first Claude only read its source at a pinned commit (6235791), saying it couldn't
run it because "this machine has 3.9.6". That claim went into TOOL_SERVER.md and into the sign-off I had already signed. When I asked
whether this would cost marks, and then "isn't there a local python version which is 3.11 or newer that can be used?", Claude checked
and found Python 3.11, 3.13 and 3.14 already installed: it had only looked at the default python3. I told it to run the server. It
ran in a throwaway Python 3.11 environment with the exact evaluated version, whose files were byte-identical to the source it had
read. Both configurations were recorded with the same tracer used on my server. Claude also changed the tracer first, because it was
skipping writes under /lib/python, which would have hidden the very install we wanted to see.

What the source predicted is now observed. In tools/list the description really tells the model "Although originally you did not have
internet access… this tool now grants you internet access". A tool annotated readOnlyHint started npm install on the first web page
and added 33 packages. The metadata address was refused. My restricted configuration (only the two job-board hosts, no Node.js reader)
refused example.com and started nothing. My trust decision: not by default; yes only in that restricted form, with its output treated
as untrusted. I also had Claude record a second transcript of my own server under v1.3, so the evidence matches the current code.

## 10. What moved the score

Five single changes were tried on the tuning labels (426f0f5). Only A, letting engineer titles with "Data" or "Pipeline" through the
role rule, changed anything. I chose to give baseline, A and D one look each at the held-out labels (9186aa2). A raised recall from 2/7
to 6/7, but it also let in an internship, because "intern" as a whole word does not match "Internship". D flipped: on tuning the years
bonus seemed to help the ranking, and on held-out it seemed to hurt. I adopted A, added "internship" while marking it as unmeasured,
and rejected B–E (148f405).

## 11. What I accepted, changed and rejected from Claude

- **Rejected:** a hard visa rule, which became points only; "Data Engineering" counting as a role phrase; Claude's first guess at
  score weights.
- **Changed:** the years preference (4 → 3 years); the label pool (141 → 107 → 82 → 72); the labeling tool's display, so it shows
  the years and visa lines.
- **Accepted after checking:** gzip for the raw files, after seeing the hashes re-verified on load; the 25 removals, after reading
  each quoted phrase; the blind label over my audit answer; change A, after it held on the held-out labels.

Claude also caught its own mistakes:
- the stale "(v1)" heading in FILTER.md
- a sign-off line saying the measurement tests came before the code, when they came in the same commit
- 10 of 46 claim labels from its own checker that were wrong

One mistake I caught by asking: the false "only Python 3.9.6" reason for not running fetch. Because it was in a signed sign-off, I
re-signed only after it was corrected.

## 12. What I learned, traceability, and what is still open

A sample that agrees with everything can be telling me about my own anchoring, not about the filter. My labels need the same checking
as Claude's, and a number that moves on tuning can reverse on held-out. Persisting across sessions is not learning: the scorer changed
because I edited a file, and Claude remembered my decisions because they were written to memory files.

**Traceability.** The prompts quoted above are from 2026-11-24 and 2026-11-25. The commits run from c09a161 (the starting point),
through 148f405 (v1.3), to the fetch-run and final commits. The tests are the full suite of 157, including test_W1–W10, the server
tests and scripts/js3_sabotage_check.py (9/9). The server evidence is in evidence/mcp/: both transcripts of my server and both fetch
runs.

**Still open:**
- the 39 new claim labels in v1.3 were not checked
- the "internship" fix is unmeasured
- the student-worker false friend is still kept
- what fetch's npm install downloaded was not reviewed, and its proxy and prompt paths were not run
- no real MCP client has connected to my server
- everything rests on one day's snapshot, with 7 relevant held-out postings
