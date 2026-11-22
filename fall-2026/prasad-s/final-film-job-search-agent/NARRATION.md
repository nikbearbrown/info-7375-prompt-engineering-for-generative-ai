# WorthLoop: narration for the final project film

Final Project Film, INFO 7375. Prasad Shinde. Written 2026-11-22.

My words, to be voiced by Kokoro am_onyx, a synthetic voice. I read each
source on 2026-11-22. The spoken beats are B1 to B16; the opening card
and "On screen:" lines are on-screen text, not spoken.

## Opening card (on screen, not spoken)

WorthLoop · Prasad Shinde

Narration: synthetic voice (Kokoro am_onyx). Words: Prasad Shinde.

## Part 1: Executive summary

B1 — I'm Prasad. I'm building WorthLoop, an agent that watches job boards for one person. It judges each new posting, and it prepares an application only for the ones worth their time.

B2 — For a posting that passes, it shows its evidence and drafts a packet: the posting, the answers, and why it fits. The person approves that exact packet, or it goes nowhere. WorthLoop never submits anything itself.

B3 — Why it matters: hiring is flooded. In July 2026, Greenhouse — whose software runs many job pages — said job ads on its platform draw about 254 applicants each. Job seekers waste hours on postings that were never a fit, and employers drown in applications.

## Part 2: What others have done

B4 — First, tools that apply for you. Employers say they put the wrong information in the wrong fields. One company's HR chief called them snake oil.

B5 — Second, open-source agents score jobs and let you press Submit. One checked 740 listings for its maker: 68 applications, 12 interviews, one offer.

B6 — Third, approval checks come from AI payments. One standard, AP2, says the asking screen must be plain code, not AI. In October I pitched that check for payments; others built it well, so I carried it to job applications.

B7 — What I didn't find in theirs: a test locked before tuning, or approval tied to the exact packet. My last test showed why: my filter missed the one posting worth applying to, reading "prefers five years" as a hard rule.

## Part 3: Methods

B8 — WorthLoop works for Alex Rivera, a fictional job seeker — no real person's data is in it. It reads the public job boards of four companies.

On screen: Stripe, Robinhood, Duolingo — Greenhouse; Notion — Ashby.

B9 — Here is one made-up posting, labeled constructed. WorthLoop checks it against Alex's rules and shows its evidence: title fits, level fits, place fits, years fit. It will become a packet: the posting, draft answers from Alex's profile, and the evidence.

B10 — Claude reaches the first tool, the scorer, through a standard plug; the rest come next. Rules in the code say what each tool may do, and each run stops at ten requests or sixty seconds.

B11 — Release will need the person's approval, through plain code, not AI — the AI cannot approve for you. The approval will be tied to a fingerprint of the packet: change one word, and the fingerprint changes.

B12 — It runs on my laptop, with free tools and no paid credits; Claude comes through my university's access. Built so far: the watcher, the filter, the scorer. Next: the packet and the gate.

## Part 4: Evaluation

B13 — The test set was locked before any tuning, and my tools are built to skip its postings. Worth-it postings are rare — about one in thirty in my last test — so twenty postings will likely hold none, or one. I'll report the exact count; if it holds none, I'll add more by a rule written first.

B14 — It worked only if every check passes — misses none, keeps at most two of the rest, every claim matches Alex's profile, every fingerprint matches, all five traps handled. One failure anywhere, and it didn't. Pass or fail, not a success rate.

B15 — Five traps are set on purpose, each with its right answer written first. Two: a Staff title is too senior for Alex, who looks for roles asking three years or less. And "prefers five years" is not a rejection; prefers still invites fewer — the mistake my last test caught.

B16 — The controlled failure: I write the expected result down first. Then I change a packet after approval, on purpose. A separate check must catch it, refuse it, and make me approve again. Last, someone who didn't build it runs it from the instructions, on a clean machine.
