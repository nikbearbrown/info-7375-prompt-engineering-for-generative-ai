# FILTER.md: Job-Search Agent 3

Pavithra Prasad · INFO 7375 · JS3 · version 1.0 written 2026-11-25 before the filter code (`d9b1cf1`); version 1.1 the same day after the audit (section 7)

The filter decides which collected postings reach the candidate, the fictional Rohan Mehta (`data/rohan-mehta.resume.json`): about two years as a software engineer plus a co-op, backend and platform skills, based in Boston. It starts from my JS1 relevance rule (four checks, all must pass), which the JS2 agent still uses. JS1's rule gives only a yes or no, so it has no close calls to audit. Version 1.0 keeps its checks but splits them into gates and a score with a threshold.

## 1. Verdicts

Each posting gets one of three verdicts:

* keep: passes every gate and scores at or above the threshold.
* reject: fails a gate, or scores below the threshold.
* cannot tell: a field the filter needs is missing, so it does not guess (section 3).

## 2. The filter, version 1.0

Words are matched as whole words, ignoring case, so "Java" does not match "JavaScript" and "AI" does not match "maintain". This is inherited from JS1.

### Gates (any gate fails: reject)

| Gate | Rule | Reason |
|---|---|---|
| G1 Location | The location field names the United States: "United States", "USA" or "US". | Rohan is in Boston and is looking in the US. State codes alone do not count, because Pinterest writes "CA" for both California and Canada (JS1 rule 4). |
| G2 Seniority in the title | The title has none of: Senior, Sr, Staff, Principal, Lead, Manager, Director, Head, Distinguished, Intern. | These titles ask for more experience than about two years, or (Intern) are for students. JS1 rule 3. |
| G3 Years asked | The description does not ask for 3 or more years. A range counts as its lowest number ("3-5 years" is 3). | Same reason as G2. The range reading is the JS2 change I approved (`0ecb3d5`). |

### Score (only for postings that pass every gate)

| Part | Points | Reason |
|---|---|---|
| S1 Role in the title | 3 if the title has "Engineer" and one role word: Software, Backend, Back-end, Full-stack, Full Stack, Fullstack, Cloud, AI. 1 if it has "Engineer" or "Developer" without a role word. 0 otherwise. | The title is the clearest signal of the kind of work. A plain "Engineer" or "Developer" title may still fit, so it gets a little credit instead of none. |
| S2 Skills in the description | 1 for each skill from the résumé's languages, backend_automation, database_cloud and devops_cicd lists that the description names, at most 5. | Shared skills show Rohan could do the work. The cap stops a long tool list from outweighing the role. |

Threshold: keep if the score is 5 or more. A full role match plus two skills (3 + 2) reaches it, which is what JS1's rule asked for. A plain "Engineer" title needs four skills.

Close calls: postings that pass every gate and score 4 or 5, that is, at the threshold or one point below it. These go into the audit.

## 3. Expected sources

| Board | System | Fields the filter reads | Notes |
|---|---|---|---|
| pinterest | Greenhouse | `title`, `location.name`, `content` (HTML) | Locations end in a country code ("San Francisco, CA, US"). |
| figma | Greenhouse | the same | Some locations are cities only ("San Francisco, CA • New York, NY"), with no country. |
| spotify | Lever | `text`, `categories.allLocations` plus `country`, `description` plus `lists` plus `additional` | The country comes in brackets ("New York, NY (US)"). |
| ramp | Ashby | `title`, `location` plus `secondaryLocations` plus the address country, `descriptionHtml` | The country comes last ("(USA)"). |
| no-such-board | Lever | none | Fails on purpose (HTTP 404). |

When something is missing:

* A board that fails is reported as failed. None of its postings count as rejected, and it is never shown as "0 jobs".
* A posting with no description gets "cannot tell": G3 and S2 cannot be checked.
* A posting with an empty location gets "cannot tell": G1 cannot be checked.
* A posting with no title or id is bad data, and its board fails (inherited from JS2).

## 4. The evidence rules (for the shortlist)

For each kept posting, Claude writes a short justification: a list of claims, each with a quote copied from the posting. Each claim is labelled against the posting's own text (title, location and description), not against the filter's score:

* supported: the quote is in the posting word for word, and it states what the claim says.
* contradicted: the posting states the opposite (for example, the claim says "entry level" and the posting asks for "5+ years", or a body sentence says "Senior").
* insufficient: the posting does not say either way, the quote is not in the posting, or the quote contains the word but in another sense (relevance is not entailment).

A matching word is never enough on its own to make a claim supported. "Python" in a list of nice-to-haves does not support "the role uses Python every day".

When the agent must say "I cannot tell":

* the posting has no description, or no location;
* the board failed in this run;
* the claim is about something the posting does not cover (salary, visa sponsorship, team size, interview steps);
* abstention rule: a shortlisted posting gets "I cannot tell if this fits" instead of a recommendation if any claim about role, experience or location is not supported.

## 5. Wrong versions my tests must catch

1. Substring matching: words matched inside other words, so "Java" matches "JavaScript" and "US" matches "focus". The tests give it a constructed posting and must see it keep a posting the real filter rejects.
2. Ranking by skill count alone: a "Senior Staff Backend Engineer" posting with eight skills goes to the top of the shortlist. The tests must catch any gate-failing posting on the shortlist.
3. Keyword equals support: a claim labelled supported because its key word appears anywhere in the posting, even when the quote is not in the posting or the word is used in another sense. The tests must catch a supported label on a quote the posting does not contain.

## 6. False friends I expect to look for

Written before the audit. The audit will say whether each one happened.

* "AI" as a role word in a title that is not engineering work, for example a support role.
* "Software" in a mobile title (iOS, Android), which matches the role words but is not backend work.
* A résumé skill name used for something else, such as "Helm".

What the audit found (`AUDIT.md`):

* "Helm" happened. In Ramp's "Research Engineer, Benchmarks & Evaluation", "Helm" matched "HELM", an evaluation benchmark ("lm-evaluation-harness, HELM or similar"), not the Kubernetes tool on the résumé. It added one point to a close call.
* "AI" and "Software" depend on my labels. On my first pass I said yes to the Support Engineer, iOS and Android postings, so they matched for a reason I accepted. On my second pass I said no to all three, so by those labels they are false friends: the title word matched, but the work is support or mobile, not backend (`AUDIT.md` sections 6 and 8). No rule was changed for them.
* One I did not predict: Lever's country tag. "Toronto; New York, NY (CA)" is tagged CA (Canada) after its first city, so G1 found no US word, although New York is one of its places.

## 7. Version 1.1 (2026-11-25, after the reject audit)

Every change below was chosen on the audit's tuning sets (48 postings: the random rejects, the close calls, the kept postings and the gate close calls), with my hand labels (including the two location corrections in `AUDIT.md`). The 20 held-out postings were not used to choose. Each change is its own filter file in `filters/changes/`, so it can be measured alone (`SCORE-REPORT.md`). `filters/v1.1.json` is v1.0 plus A to E.

| Change | Rule | Decision | Reason | Tuning sets (agrees with my label, of 48; v1.0 is 35) |
|---|---|---|---|---|
| A | Threshold 5 to 4: a full role title plus one résumé skill is enough | added | Ramp and Pinterest descriptions often name no language at all, so real backend roles scored 3 or 4 and were rejected | 38, with one new false keep (Machine Learning Engineer II, Responsible AI) |
| B | G3 rejects only an ask of 5 or more years, not 3 | added | I said yes to postings asking 3 or 4 years; Rohan has about two and a half years plus a master's degree | 37, no new false keep |
| C | G1 also accepts US cities written with their state ("New York, NY") | added | the Lever country tag and Figma's city-only locations hide US places | 35, no verdict changes in the tuning sets |
| D | The skill "Helm" counts only as written, not "HELM" | added | the false friend above | 35, no verdict changes at threshold 5 |
| E | G4: reject when the description asks for a senior engineer ("We're looking for a Senior Backend Engineer") | added | a Ramp backend title without "Senior" asks for one in its text; the title gate misses it | 35, no verdict changes in the tuning sets |
| G | Drop Intern and Staff from G2 | rejected | my labels said yes to 4 Intern or Staff postings, but Rohan finished the degree in May 2026, so internships for students do not fit, and Staff titles ask for many more years than Rohan has. I kept those labels as they are and did not change the filter to match them | 37 |

Measured again later: on my second pass over the 27 engineering postings in the tuning sets (`AUDIT.md` section 8), v1.0 agrees with my labels on 21 and v1.1 on 18, because A and B were fitted to my first, quick labels. I kept v1.1 as the version the shortlist and the tool use, and I do not claim it is better than v1.0 (`SCORE-REPORT.md`).

## 8. Known limits of the word rules (found in review, not fixed)

Both are found by matching words, not by reading meaning, so they can reject a posting for the wrong reason:

* G3 counts any "N years", not only an ask: "Our company has been operating for 10 years" is read as asking for 10 years.
* G4 counts any "senior ... engineer", not only the role asked for: "You will work alongside senior software engineers" is read as a senior role.

`tests/test_filter_v1_1.py` (`KnownLimits`) records both on constructed postings, so a later fix would show. I did not fix them in v1.1: the audit and held-out numbers were measured with these rules, and changing them now would change what was measured.

## Change log

| Version | Date | What changed | Why |
|---|---|---|---|
| 1.0 | 2026-11-25 | First version: JS1's four checks split into three gates and a score with a threshold, plus "cannot tell" | JS1's yes or no rule has no close calls to audit |
| 1.0 wording | 2026-11-25, after review | The close-call sentence in section 2 corrected from "one point either side of the line" to "at the threshold or one point below it". The rule itself (scores 4 and 5) did not change | the old wording did not match the rule |
| 1.1 | 2026-11-25 | Changes A to E added, G rejected (section 7) | the reject audit: 13 of 48 tuning postings disagreed with my labels under v1.0 |
