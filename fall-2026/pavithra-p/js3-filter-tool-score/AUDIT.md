# The reject audit (Chapter 7)

Filter v1.0 (`filters/v1.0.json`, FILTER.md section 2) on everything the agent collected in run `20261125T204144Z` (2026-11-25 20:41 UTC), judged against my own hand labels. The full tables, with every posting, my label and the filter's reason, are in `audit/results.md` (`python3 -m agent audit`).

## 1. What the filter did

| | Postings |
|---|---|
| Collected from 4 boards (pinterest 167, figma 143, spotify 96, ramp 183) | 589 |
| keep | 7 |
| reject | 582 (577 outside the close calls) |
| cannot tell | 0 (every posting had a description and a location) |
| no-such-board (HTTP 404) | failed; none of its postings counted as rejected |

Gate failures (a posting can fail more than one): G1 location 185, G2 seniority 366, G3 years 354.

## 2. The sample, drawn before any label

`python3 -m agent draw-sample` with seed 20261125, committed in `8b11679` (15:48 local) before I labelled anything (`audit/sample.json`):

| Set | Size | Drawn from |
|---|---|---|
| Random rejects | 30 | the 577 rejects outside the close calls, at random |
| Close calls | 7 | every posting that passed all gates with score 4 or 5 (5 rejected, 2 kept) |
| Kept | 7 | every kept posting (2 of them are also close calls) |
| Gate close calls | 6 | at random from the 20 postings that failed exactly one gate but scored 5 or more |
| Held-out | 20 | at random from the 82 other US postings with Engineer or Developer in the title. Used only in `SCORE-REPORT.md` |

All 68 went into one labelling page (`audit/label-sheet.html`), in random order, showing:
* the title, board and location;
* the posting's link and full text;
* a line quoting the posting's own words around any "N years".

The page showed no verdict, score or set name, so my labels were blind to the filter. The years line was added after I started and asked where the years were, and I reloaded the page. It quotes the posting; it is not the filter's reading. The page keeps only the last click for each posting; the saved clicks run from 20:55:02 to 20:57:47 UTC.

## 3. How I labelled

* I labelled all 68 in one pass (`audit/hand-labels.csv`): yes (worth Rohan's time), no, or cannot tell. The page saved the time of every click. All 68 fall between 20:55:02 and 20:57:47 UTC: under three minutes, with a median of 2 seconds between clicks. That is too fast to have read most descriptions, so my labels come from the title, the location and the years line.
* Two corrections: afterwards I saw that I had said yes to two postings in London and Stockholm, because I had not looked at the location. I asked Claude to change every yes whose location has no US place to no. It changed exactly two: Spotify's "Backend Engineer - Subscriptions" and "Backend Engineer - Data Platform". I did not re-read them, and no other label changed. The file keeps the original label of every row and says why these two changed. The numbers below use the corrected labels.
* Which is the truth. My JS1 TA asked me to decide, before labelling, whether my labels or my written rule is the truth. In this audit my hand label is the reference, because the brief asks for my own judgment, and the filter is what is measured against it. I did not write that down before labelling. My first pass then drifted from my own rules, the same thing the TA noted in JS1. My second pass (section 8) follows my rules much more closely.
* My labels are not fully consistent with my own FILTER.md. I said yes to "Staff Software Engineer, App Promotion" but no to "Sr. Staff Software Engineer, AI Platform". I also said yes to two internships and to postings asking for 4 or 5 years. This is the same drift I found in JS1: when labelling quickly, my label follows "is this a software job?" more than "does this fit about two years, in the US?".

## 4. Results, by set (with the two corrections)

| Set | Filter wrong by my label | 95% interval (Wilson) |
|---|---|---|
| Random rejects | 5 of 30 | 7% to 34% |
| Close calls | 4 of 7 | 25% to 84% |
| Kept | 0 of 7 | 0% to 35% |
| Gate close calls | 4 of 6 (6 of 6 before the two corrections) | 30% to 90% |

The 5 random rejects I would have sent to Rohan, and the rule that rejected each:

| Posting | Rule that rejected it |
|---|---|
| Pinterest, Software Engineer II, EPD Ads | S2: score 3, the description names none of the résumé's skills |
| Figma, Software Engineer - C++ | G3: asks for 4 years |
| Spotify, Security Engineer - Product Security ("Toronto; New York, NY (CA)") | G1: Lever's country tag says CA, although New York is one of its places |
| Ramp, Software Engineering Intern, iOS | G2: Intern |
| Pinterest, Staff Software Engineer, App Promotion | G2: Staff |

The 4 close calls I would have sent: three Ramp roles that scored 4 with a full role title but one skill (Backend, Credit; Applied AI Engineer, Fullstack; Production Engineering), and "Research Engineer, Benchmarks & Evaluation" (score 4, with the false friend below).

The kept postings: on the first pass I agreed with all 7, including Android, iOS and the Support Engineer role I had expected to be false friends. My second pass disagreed with those three (section 8).

## 5. What a sample this size can and cannot show

* 5 of 30 random rejects were wrong by my label. That is not a measured rate for all 577 rejects. With 30 postings, the 95% interval runs from 7% to 34%. Across 577 rejects, that would be anywhere from about 40 to about 195 postings I might want. The sample cannot narrow that down.
* What it can show: the filter does reject postings I would want, even outside the close calls, and it shows which rules did it. Two causes appear more than once: no résumé skill named in the description (S2), and the years and seniority gates (G2, G3).
* 0 of 7 kept were wrong. That does not mean the filter never keeps a bad posting: with 7, the interval reaches 35%.
* All of this is against my own quick labels (section 3). My own second pass changed 13 of 27 labels (section 8). That is a separate source of doubt, which the sampling interval does not include. No second person labelled them.

## 6. The false friend

"Helm". On the résumé, Helm is the Kubernetes package manager. Ramp's "Research Engineer, Benchmarks & Evaluation" asks for experience with "eval frameworks (verifiers, lm-evaluation-harness, HELM or similar)". HELM there is an evaluation benchmark, but the whole-word, ignore-case match counted it as Rohan's skill and gave the posting one point (score 4, a close call). Change D in v1.1 matches "Helm" only as written. In Lavanya's corpus, her server reported 6 "Helm" matches and returned 5 (my limit was 5), all the Kubernetes tool. So whether "Helm" is a false friend depends on the data, not only on the word.

The other two I predicted depend on which of my passes is used:
* "AI" in a support title (Support Engineer, AI Infrastructure & Tooling);
* "Software" in a mobile title (Software Engineer, Android and iOS).

On my first pass I said yes to all three postings, so the words matched for a reason I accepted. On my second pass I said no to all three (section 8). By those labels, "AI" and "Software" matched for the wrong reason: the role word was there, but the work is support or mobile, not backend. Both are false friends on the second pass. "Helm" is one on either pass.

One I did not predict is the Lever country tag in G1 (table above).

## 7. Rules added, cut or rejected after measuring

All in FILTER.md section 7 and `filters/changes/`:
* added: A (threshold 4), B (years limit 5), C (US cities behind a country tag), D (Helm as written) and E (senior asked in the text);
* rejected: G (letting Intern and Staff titles through), although it matched my labels better.

They were chosen on these 48 tuning postings only (`python3 scripts/tune_changes.py`: 35 of 48 for v1.0, 40 of 48 for v1.1). The held-out result is in `SCORE-REPORT.md`.

## 8. A second pass on the engineering postings

After the audit, the shortlist and the claim labels, I labelled again every posting in the tuning sets with Engineer, Engineering or Developer in the title (27 postings, `python3 -m agent reread-page`). The page was the same, in a new random order (seed 2026112502), and did not show my earlier labels or the filter's verdict. I judged from the title, the location and the years line shown on the page. The labels are in `audit/reread-labels.csv`, made between 21:54:14 and 21:55:40 UTC.

This pass was not blind to what I had learned that day: I had already seen the filter's reasons in the audit, and Claude's claims about some of these postings.

| | Of 27 |
|---|---|
| Same label as my first pass | 14 |
| Changed from yes to no | 13 (none from no to yes) |
| Filter v1.0 agrees with the second pass | 21 |
| Filter v1.1 agrees with the second pass | 18 |
| Filter v1.0 agrees with the first pass | 14 |
| Filter v1.1 agrees with the first pass | 19 |

The 13 changes were Android, iOS, the two internships, the two Staff titles, the 4- and 5-year roles (Software Engineer - C++, and the two Ramp security roles), the Toronto and New York security role, Research Engineer (HELM), Applied AI Engineer and Support Engineer. The second pass also said no to the two London and Stockholm postings, the same as my two corrections.

What this shows:
* My labels are not stable. On the postings where yes or no is a real decision, I gave a different answer to about half of them the second time. The intervals in section 5 cover only the sampling, not this, so the error counts above also depend on which pass is used.
* The second pass follows my own FILTER.md much more closely (no Staff, no internships, under 3 years). The first pass followed "is it a software job".
* v1.1's changes A and B were chosen on the first pass. On the second pass they make the filter worse (18 against 21). Section 7 and `SCORE-REPORT.md` say this. I kept v1.1, and I do not claim it is better than v1.0.

The audit of filter v1.0 again, with each re-read posting using its second-pass label and every other posting its first label (`python3 scripts/audit_second_pass.py`):

| Set | First pass: filter wrong | Second pass: filter wrong | 95% Wilson, second pass |
|---|---|---|---|
| Random rejects | 5 of 30 | 1 of 30 (Software Engineer II, EPD Ads) | 1% to 17% |
| Close calls | 4 of 7 | 3 of 7 (Backend, Credit; Production Engineering; Support Engineer, kept) | 16% to 75% |
| Kept | 0 of 7 | 3 of 7 (iOS, Android, Support Engineer) | 16% to 75% |
| Gate close calls | 4 of 6 | 0 of 6 | 0% to 39% |

The result changes:
* On the first pass, the filter's mistakes were rejects I wanted (too strict).
* On the second pass, its mistakes are mostly keeps I did not want (Android, iOS and Support Engineer), where "Software" and "AI" in the title earned the role points (section 6). Its rejects are almost all right.

So what the audit says about the filter depends on which of my labels is used. I report both. Sections 4 and 5 stay on the first pass, because that is the blind labelling of the drawn sample.
