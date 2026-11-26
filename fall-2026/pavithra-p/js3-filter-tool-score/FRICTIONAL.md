# Frictional: Job-Search Agent 3

Pavithra Prasad · INFO 7375 · JS3 · all work on 2026-11-25 (times UTC)

## What I tried and expected

I started from my JS2 agent. Claude Code drafted the filter from my JS1 rule, and I approved it ("Approve, build") before any code was written (`d9b1cf1`). My old rule only said yes or no, so this time the filter has three gates and a score, which gives close calls to check.

Expected: I expected the initial filter to be mostly accurate because it used explicit rules for role, location, experience and technical skills. I also expected labelling to be straightforward, but distinguishing genuine role relevance from keyword matches required more judgment than I anticipated.

## Where it got hard, and what I did

* I couldn't see the years of experience on the labelling page, so Claude added a years line and I reloaded.
* I labelled 68 postings quickly, about 2 seconds each, mostly from the title, location and years line.
* I had said yes to jobs in London and Stockholm because I didn't check the location. I asked for those two to be changed to no; the original labels are kept in the file.
* I also said yes to Staff roles, internships and 4 to 5 year roles, which my own filter rules out. My JS1 TA had told me to decide labels vs rule first, and I didn't. When I relabelled the 27 engineering postings later, 13 changed to no.
* The audit showed the filter wrongly rejected 5 of 30 random rejects by my first labels. The false friend was "Helm": it matched an AI benchmark called HELM, not the Kubernetes tool.
* I kept changes A to E but said no to G (allowing Staff and intern titles), even though it matched my labels better. Rohan has already graduated, and Staff roles need more years.
* Claude Code was signed out in my terminal, which stopped the Claude calls until I logged in again.
* Reviews found a crash in my tool server and a version mismatch; both are fixed and tested. Two word-matching limits are written down in FILTER.md.
* In the shortlist, many of Claude's claims said more than their quote did. For example, a quote about remote work was used to claim a specific location. I marked those insufficient, and changed 5 of my own labels after reviews pointed out that they broke my rule. Only Android passed my abstention rule, even though its own claims say it is mobile work, so that became my counterexample.
* When Claude used my tool server, it said the tool was read-only because the server said so, not because it checked. That is why my tests check it instead of trusting the description.
* Testing Claude Code's own `claude mcp serve` (an idea I took from Ashwin's work, named in SOURCES.md), it read and wrote files outside its folder with no prompt. One bad request got no answer and my client hung, so I added a 20 second timeout.
* After the held-out check showed no change, I looked at why, but I did not change anything based on it, because that would be tuning on the held-out set.

## What I checked myself

* I labelled 68 postings blind, then 27 again, and checked all 37 shortlist claims against the posting text.
* I predicted three made-up postings (A keep, B reject, C keep) before their test was written; all three matched.
* The v1.1 choices were committed (`70ddf4b`), with my OK, before the held-out measurement, so the held-out set did not shape them.
* I had my work reviewed twice by an independent Claude agent and three times by ChatGPT, and only the findings that matched the files were fixed.

## Who did what

* I approved the filter, made every label (68, the 27 second-pass ones, and all 37 claims), gave my three predictions before their test, made every decision, and wrote my two reflection lines.
* Claude Code drafted the documents, wrote the code and tests, ran the commands, applied the two location changes I asked for, and ran an independent review.
* Claude (`claude -p`) wrote the 37 shortlist claims and 40 held-out verdicts, and used my tool server as a client.
* ChatGPT reviewed my drafts three times.
* I accepted the filter design, changes A to E, the one-tool read-only server, and the review fixes.
* I changed the shortlist to the top 8 so I could label every claim myself, and I overrode the checker on 18 claims.
* I rejected change G, the suggestion to check only 8 claims, and the checker wherever I disagreed.

Claude Code drafted this log from what I did and decided; the "Expected" and "Learned" lines are my own words. The full list of what Claude contributed is in `SOURCES.md`.

## What I learned, and what is still open

Learned: I learned that fixing issues found during the reject audit does not necessarily improve performance on unseen postings. Although v1.1 increased the number of retained postings from 7 to 15, both versions agreed with my labels on only 13 of the 20 held-out postings. This showed me that retrieving more postings does not necessarily make the filter more accurate.

On my second labels, v1.0 did better than v1.1 (21 vs 18 of 27), so I don't claim v1.1 is better.

Still open:
* My held-out set could barely contain any kept postings, so it couldn't really show a change.
* The abstention rule checks whether a claim is supported, not whether it is good for Rohan (Android).
* My labels were quick and not fully consistent.
* The two word-matching limits (company age read as years asked, "alongside senior engineers" read as a senior role) are recorded, not fixed.

Next time I would draw the held-out set first and label it slowly.

## Where to find it

* Commits:
  * `d9b1cf1` the filter alone;
  * `e02dffe` the starting agent and the collection;
  * `8b11679` the filter code and the sample, before any label;
  * `70ddf4b` my labels and v1.1, before the held-out check;
  * the final commit is in the Canvas submission.
* My key prompts: "Approve, build", "Yes, reject G", "Yes, commit", "Change to insufficient" (claims #29 and #32), and my predictions "A keep, B reject, C keep".
* Times: my labels 20:55 to 20:57, second pass 21:54 to 21:55, Claude's shortlist calls 21:09 to 21:10, the context test 21:59 to 22:00, the final tool transcripts 22:34.
* Tests: 159, run with `python3 -m unittest discover -s tests`. Among them:
  * `test_my_predictions.py` (my predictions);
  * `test_filter_v1_1.py` (each v1.1 change);
  * `test_toolserver.py` (the crash fix);
  * `test_mcp_client.py` (the timeout).
* Details: `AUDIT.md`, `SHORTLIST.md`, `SCORE-REPORT.md`, `EVAL-SERVERS.md`.
