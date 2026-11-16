# FILTER.md — Job-Search Agent 3: the filter, the evidence rules, the sources

**Author:** Prasad Shinde
**Written:** 2026-11-15, before any JS3 code and before any posting was opened for JS3
**Version:** v1 — 2026-11-15
**Started from:** JS2, js2-loop-tools-diff/ at 64e00c7: its rule (CONTRACT.md v0.8 §4) and GATE.md v0.3. The Reallocation Engine is not used. Lectern is reference only, as it was in JS2: cited in SOURCES.md, no code copied.
**Pointer:** This file supersedes, for JS3, CONTRACT §4's "If a field is missing, that condition is false" (→ F7 below) and CONTRACT §8 (→ §5 here). CONTRACT.md gets a v0.9 row in its §9 pointing here when the JS2 folder is copied in.

## 1. The filter
(Brief: "The filter, as a document … role words, topic words, any rule about the posting text. For every rule, one line of reasoning.")

v1 is JS2's rule exactly as agent/rule.py runs it at 64e00c7, plus two additions, F7 and F8, both decided before any data was looked at. Nothing else changes yet, on purpose: a rule earns a change by being measured first, and those changes belong in v2, each with its measurement behind it.

| ID | Rule | Reason (one line) | Origin |
|---|---|---|---|
| F1 | Cleanup: Greenhouse content goes through §4 steps 1–4 (parse the JSON, unescape the HTML, strip the tags, collapse whitespace); Ashby descriptionPlain gets step 4 only. Title and location are trimmed and whitespace-collapsed on both ATSs | Each ATS gets only the cleanup its own format needs: Greenhouse hands over escaped HTML, Ashby hands over plain text, and cleaning plain text as if it were HTML would change words the rule then has to match | §4; v0.5 item 3; v0.7 item 5; rule.py:6–21, :33–34 |
| F2 | Matching: case-insensitive plain substring. No whole-word rule, no synonyms, no stemming | Substring is the weakest matching rule there is, and every match can be checked by eye in the cleaned text; whether it catches the real cases is what the audit measures, and anything smarter would need evidence of its own | §4; rule.py:50 |
| F3 | Role words (C1): the title contains one of the target_titles — Associate Product Manager, Product Manager, Product Analyst | The title is the field the poster writes to name the role, so it is the gate; role words appearing in the body are a different claim (W6) | §4 C1; resume_persona.json |
| F4 | Location (C2): the location text contains one of the locations — New York, NYC, Remote — or the location is exactly "remote". On Ashby, the location text is the main location joined with every secondary location | Location is judged on words the posting states, never on a flag it sets: 86 of the 87 isRemote postings in the 2026-11-05 Notion snapshot were Hybrid (v0.5 item 3), so the text is the only evidence that can be checked | §4 C2; v0.5 item 3; rule.py:69–71 |
| F5 | Topic words (the score): the number of distinct skills found in the cleaned text, 0–5, each skill counting once however often it appears — Python, SQL, A/B testing, roadmapping, user research | Distinct skills measure breadth of fit; counting repeats would reward a posting for saying one word many times | §4 C3; rule.py:63, :72 |
| F6 | Verdict: relevant if C1 and C2 both pass and the score is 2 or more; otherwise not_relevant | This is §4 unchanged: the gates decide what the role is and where it is, the threshold is part of the verdict, and nothing outside the three conditions enters | §4; rule.py:9, :74–75 |
| F7 | Missing field (new in v1): a field is missing when it is absent, null, or empty after F1's cleanup. The posting is judged on the fields it has: if a checkable condition already fails — a present title that is not a target title, a present location that fails F4, a present text scoring under 2 — the verdict is not_relevant as usual. cannot_tell applies only when every checkable condition passes and the missing field is the one that would decide the verdict (a target title and score 2+, with no location). cannot_tell postings are reported in their own list, with the missing field named; they are never on the shortlist and never counted as rejects | §4's "missing means false" invented a verdict the text doesn't support; but a posting already settled by a field it has does not become undecidable because another field is absent | new; amends §4 |
| F8 | Ranking (new in v1): by score, high to low; ties broken by board key in alphabetical order — ashby:notion, greenhouse:duolingo, greenhouse:robinhood, greenhouse:stripe — then by posting id, ids compared as strings, as in GATE §3 | Alphabetical, so the order can be worked out from the keys alone; dates stay out because §4's rule never uses posting date (W7) | new |

**The score and §4.** The score is C3's own count, given a name — the same number §4 already computed, now written down so rankings and audits can cite it. Nothing new enters the verdict, and no other score is added to it or merged with it: not Claude's judgment (§6), not approval counts, not anything from outside the posting.

**Closest calls.** Postings one step from flipping: both gates pass and the score is 1 or 2 — one skill short of the threshold, or exactly on it — or the score is 2 or more and exactly one gate fails. The audit reads these first, because any rule change moves them before it moves anything else.

**Not in the rule.** Posting date, max_years_required, isRemote, workplaceType and Claude's judgment stay out — §4 and v0.5 item 3 keep them out, and v1 changes none of that.

**Known gaps, not yet rules.** CONTRACT §4's known consequences and v0.5 item 8 already list the gaps (SQL inside NoSQL counts; "roadmap" is not "roadmapping"; the rest). They are not restated here. The audit tests them first, and v2 decides each one after measuring.

## 2. Evidence rules
(Brief: "When a claim in your shortlist counts as supported, contradicted, or insufficient against the posting's own text, and when your agent must say 'I cannot tell'.")

**A claim** is one checkable statement in a shortlist justification — a single thing the posting is said to state or require, worded so a reader can go and look for it in the text. Invented example: "This role is based in New York."

**The posting's own text** is F1's cleaned title, location and text, taken from the corpus copy in §3, and nothing else. The response holds more than those three fields — dates, compensation, the rest — but they are outside F1's fields, so they never count as the posting's own text. And nothing outside the response counts either: not the company's other pages, and not anything I happen to know about the company.

- **Supported:** a span in that text states the claim; the label names the field and quotes the span. A word being present supports only "the word is there" — not "the role requires it", not "the team works this way", and not any stronger reading.
- **Contradicted:** a span states the opposite of the claim, or something that can't be true at the same time as the claim (the claim says the role is fully remote; the text says the role is in the office four days a week).
- **Insufficient:** no span either way. When two spans disagree — one states the claim, another states something that can't hold with it (the location field says Remote; the text asks for three office days in New York) — the claim is insufficient, the label cites both spans, and the agent says it cannot tell (see "When the agent must say I cannot tell" below). It never resolves a disagreement by preferring one span.

**When the agent must say "I cannot tell":** (1) a posting under F7, where the missing field is the one that would decide the verdict; (2) a claim labeled insufficient, including one where two spans disagree — the agent says what it can't tell instead of asserting the claim either way; (3) a board not checked (§3) — the agent says the board was not checked, and never turns that into "no relevant postings".

## 3. Expected sources
(Brief: "Which boards and fields your agent should see, and what its answer should be when something is missing.")

| Board key | ATS | Title / location / text field | Files |
|---|---|---|---|
| greenhouse:stripe | Greenhouse | title / location.name / content | 8 |
| greenhouse:duolingo | Greenhouse | title / location.name / content | 4 |
| greenhouse:robinhood | Greenhouse | title / location.name / content | 4 |
| ashby:notion | Ashby | title / location + secondaryLocations / descriptionPlain | 4 |

- **The corpus:** these 20 raw 200 responses, collected through JS2's run 2 (2026-11-08T01:54:38Z) and nothing later. The seal commit lists each file with its SHA-256, so the corpus can be checked file by file.
- **Who collected them:** the agent's runs collected the run files (JS1's two runs and JS2's two runs). I collected one file myself, by curl: the 2026-10-25 Stripe response in CONTRACT §1's evidence note. Claude Code, at my instruction, collected the probes and the snapshots. Who collected the 2026-10-26 file is not recorded in JS1's README — its only 2026-10-26 entry is the hand-written expected-outcome tables (commit 5969e44), which are constructed, not collected.
- **One copy per posting:** postings are keyed by (board, id), as in GATE §3; where more than one file contains the same posting, the copy from the latest file that contains it is the one that counts.
- **Frozen:** nothing fetched after run 2 enters JS3's corpus. Anything fetched later is a JS3-SNAP snapshot and feeds JS4, not this filter.
- **Count:** 1,298 postings (stripe 894 / robinhood 179 / notion 164 / duolingo 61), counted by Claude Code on 2026-11-13 in a read-only orientation, not committed; recounted by me at the seal, and the seal's count is the one that stands.
- **Out, one reason each:** Canva — not one of the four watched boards; the agent also refuses SmartRecruiters, which is where Canva posts (CONTRACT §3 item 1); way3_agent/raw.json — a board response (a Stripe Greenhouse body with 746 postings), but gitignored, so a TA can't see it; it has no timestamp, and it adds no new ids; the constructed EMPTY file — invented for the CP7 demo, not a response any board gave; the 404 bodies — failures, kept as GATE evidence, not postings; the ashby_openai probe — not one of the four watched boards, and only its SHA-256 is committed, not its body.
- **When something is missing:** a failed board: "not checked — <reason>", never "no relevant postings" (GATE §4, W3); a missing field: F7; a corpus file that can't be read: the run ends as error, names the file, and gives no verdicts (GATE §1's error exit).

## 4. Wrong versions
(Brief: "At least two plausible-but-wrong filters or rankings your tests must catch.")
W1–W5 are JS1's and JS2's (CONTRACT §5, GATE §6). Every test input below is invented and labeled "constructed".

- **W6 — Role words anywhere.** Does: matches the target_titles anywhere in the posting, title or body text, instead of in the title alone. Plausible because: a posting can name the role in the first line of the body, and searching everything feels more thorough. Breaks: F3. Caught by: a constructed posting — title "Engineering Manager, Platform", location "New York", body text "You will partner closely with a Product Manager and the design team. You bring Python and SQL." (score 2). Right: not_relevant — C1 fails, because the title names a different role. W6 gives: relevant.
- **W7 — Newest first.** Does: breaks score ties by posting date, newest first, instead of by board key and posting id. Plausible because: newest-first is what every job board does, and fresh postings feel more worth acting on. Breaks: F8. Caught by: two constructed postings, both score 3 — A: greenhouse:stripe, id "900001", the later date; B: ashby:notion, id "c-1002", the earlier date. Right: B first — ashby:notion comes before greenhouse:stripe alphabetically, and the dates are never consulted, because §4 keeps posting date out of the rule. W7 gives: A first.
- **W8 — Missing means no.** Does: treats a missing field as a failed condition — §4's old rule — so a posting with no location fails C2 outright. Plausible because: it was the rule for two assignments, it keeps one verdict path, and no third list is needed. Breaks: F7. Caught by: a constructed posting — title "Product Manager", no location field at all, body text naming Python and SQL (score 2). Right: cannot_tell, reported in its own list with "location" named as the missing field. W8 gives: not_relevant, counted as a reject.

## 5. Hand verdicts in JS3
(Amends CONTRACT §8 for JS3. Used by the reject audit and the held-out labels.)

- **The question:** is this posting worth Alex Rivera's time, judged from the posting's own text (§2) against the whole persona — role, level (max_years_required included), location and skills — as a person would judge it, not as the rule computes it?
- **Three verdicts:** worth / not_worth / unclear — named unlike the rule's relevant / not_relevant / cannot_tell, so a line like "hand: worth, rule: relevant" can never be misread as two verdicts on one scale.
- **Role:** the work counts if it is product management — deciding what gets built and why. Technical PM counts: it is the same job with a technical area. Product Analyst counts: it is one of Alex's target_titles, and its work — product metrics, analysis, experiments — is part of what he is aiming at; a hand standard that left it out would contradict the persona it judges against. Product Marketing Manager does not: it markets the product instead of managing it. Program Manager does not: it coordinates delivery across teams. Product Designer does not: it is the design craft. Product Operations does not: it supports the PM org rather than doing the PM work. These are judgments about the work, not the words — a posting with one of these titles whose text is all roadmap and discovery work is judged by its text.
- **Level:** read against a maximum of 3 years. "3+ years" is within it — the posting asks for 3. "4+ years" is over it on level alone. A range is read by its low end: "2–5 years" asks for 2 at minimum, so it is within the maximum. A title with no seniority word — Product Manager, Associate Product Manager, Product Analyst, Technical PM — with no years stated, passes on level: the posting states nothing that puts it over the maximum, and silence is not a seniority claim. Senior, Staff, Lead or Group in the title — and the same for any other word of that class, such as Principal, Director or Head of — with no years stated, reads as over the maximum: the title is the posting's own statement of level. Unless the text states a number of years within the maximum, in which case the stated number governs.
- **Location:** "Remote - US" counts as workable. "Remote" on its own, with no country or state named, counts: the posting states no restriction, and a restriction is not read into silence. "Remote - California" counts, unless the text says the worker must live in California. "Hybrid, New York" counts — New York is workable, and hybrid there is still New York. "New York or San Francisco" counts — the posting offers the choice, and one of the choices is workable. What does not count: a posting in another city with no remote option, and remote limited to another country — the remote on offer is not one Alex can take. A posting that gives no location at all cannot be decided on location; that is the unclear case below, not a failure.
- **Skills:** the five skills matter as evidence of fit, not as a count. Work that is Alex's work — analysis in Python and SQL, A/B testing, roadmapping, user research — makes a posting more worth his time than the same title asking for a different craft. But skills never rescue a wrong role or an over-level posting, and no worth verdict needs a minimum number of them; the rule already counts them, and the hand verdict reads what the work actually is.
- **How the three parts combine:** worth when role, level and location all pass; not_worth when any one of them fails; unclear only when none of them fails and one of them cannot be decided from the text — no location at all, or two spans that disagree, as in §2. This mirrors F7: a failure settles the verdict, and only an undecidable part, with nothing failed, leaves the verdict open.
- **Never used:** anything outside the posting's own text — no company reputation, no salary sites, nothing I know about the company from elsewhere — and never the rule's verdict or Claude's, neither of which I look at while labeling.
- **JS1 and JS2 labels:** they keep their §8 meaning and are not re-labeled under this section. §5's verdicts begin with JS3.

## 6. Changelog and measured changes
(Brief: "Version it" and "Record every rule you added, cut, or rejected after measuring.")

- **v1 — 2026-11-15.** Written before any JS3 code and before any posting was opened for JS3. Reviewed by Claude (Claude.ai), 2026-11-13 to 2026-11-15; the decisions are mine. Claude.ai proposed the section layout and rule IDs, the W6–W8 candidates, and the leans I adopted (F7, F8, §2's disagreeing spans, §3's unreadable file, the verdict names). Main contents: JS2's rule carried over unchanged as F1–F6; F7 (missing fields, cannot_tell) and F8 (ranking) added; evidence rules for shortlist claims (§2); the frozen 20-file corpus and its sources (§3); wrong versions W6–W8 (§4); hand verdicts for JS3 (§5).

| Date | Rule | Added / cut / rejected | Measured on | Before → after | Decision |
|---|---|---|---|---|---|
| (empty in v1; filled from the audit) | | | | | |
