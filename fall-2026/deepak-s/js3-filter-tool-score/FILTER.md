# FILTER.md: what reaches me, and why (v1)

Job-Search Agent 3, "The Filter, the Tool, and the Score". Deepak Kumaran T S, INFO 7375, fall 2026.

Provenance: sections 3 to 7 were drafted in a claude.ai chat (Claude Opus 5.5, 2026-11-25). My edits to the drafted sections: the five Gate 0 and Phase 1a edits, and my Gate 1 decisions on the Claude Code review (claude-opus-5-5, 2026-11-25), some worded with a claude.ai chat. Sections 0 to 2 formatted in claude.ai chat from my answers. Claude Code worded the F07 to F09 'What it gets wrong' cells, which I approved.

Started from: my JS2 agent (personal repo commit b2ac533), which carries the JS1 RECORD rule. Lectern and the Reallocation Engine were not used.

| Version | Date | What changed | Commit |
|---|---|---|---|
| v1 | 2026-11-25 | first version, written before the build | see git log |

## 0. Who this filter is for, and how I label

- Persona: Riley Okafor, the fictional résumé from JS1 (examples/persona_resume.json). Target role: an entry-to-mid-level Machine Learning or AI Engineer, or Applied Scientist, building, training, evaluating, deploying or maintaining ML models and LLM-based systems.
- Labeling rule. A posting is relevant when all of these hold, and not_relevant otherwise:
  - Job family: machine learning engineering, AI engineering, applied science, data science, LLM engineering, or applied ML research.
  - Seniority: entry level through mid level. Intern, Staff, Senior Staff, Principal, Director, Lead, Head and management roles are not relevant. A Senior role is relevant only when the stated minimum experience requirement is five years or less.
  - Location: Boston, New York or NYC, Seattle, or a remote position that explicitly allows working from the United States.
  - Title versus text: the actual responsibilities and minimum qualifications take priority over the title. A suitable title does not rescue a posting whose minimum required experience is more than five years (the same line as rule E01).
  - When I am unsure, the label is not_relevant.
- Every hand verdict I give follows this rule. A verdict that departs from it is marked OVERRIDE with a reason, and the reasons are reported. (In JS1, about half my labels contradicted my own rule. This line exists so that does not happen again.)

## 1. Relevance rules (v1)

Matching: case-insensitive, whole-word token matching after the JS1 normalization steps (two html.unescape passes, tags stripped, whitespace collapsed) but without its 6000-character truncation, because quotes are checked against the full text (147 of 172 Notion descriptions would be cut). Multi-word phrases match as consecutive tokens. Body matches ignore boilerplate (section 3).

Tokens are produced using JS1 tokenization: str.lower() and maximal runs of isalnum() or +#.

A sentence ends at ., ! or ? when followed by whitespace or the end of the text, or at the end of an HTML block element (p, li, h1 to h6, div, br). Split before HTML tags are stripped.

Order: first html.unescape; then split into sentences (M4); then, within each sentence, strip tags, html.unescape again and collapse whitespace.

Each text field is normalized separately, then joined in section 5 order with a single newline. Every field boundary, including each lists[].text heading, ends a sentence. Character offsets refer to this joined text.

Within a field, normalized sentences are joined with a single space.

Title and location are each normalized as a single field by the same steps, and are quoted from their normalized form.

No stemming in v1; this is a known limitation.

Clarifications recorded at Gate 2, before any filter code (they state choices made in the dataset builder, jobwatch/text.py): empty sentences and empty fields are dropped; a sentence ends at the end of a block element, so text before an opening block tag runs on into the next sentence. Body terms match within one non-boilerplate sentence; a multi-word term cannot span two sentences.

Inherited rows come from the JS1 persona file (examples/persona_resume.json, targets.roles, targets.locations, targets.exclude_title_terms). Weights are in section 2.

| ID | Kind | Words or pattern | Matched in | Weight | Origin | Reason (one line) |
|---|---|---|---|---|---|---|
| X01 | exclude | Senior Staff | title | reject | inherited (JS1 persona) | above Riley's entry-to-mid level |
| X02 | exclude | Staff | title | reject | inherited (JS1 persona) | above Riley's entry-to-mid level |
| X03 | exclude | Principal | title | reject | inherited (JS1 persona) | above Riley's entry-to-mid level |
| X04 | exclude | Director | title | reject | inherited (JS1 persona) | a management role, not hands-on ML work |
| X05 | exclude | Intern | title | reject | inherited (JS1 persona) | below the target level; Riley wants a full-time role |
| X06 | exclude | Manager | title | reject | inherited (JS1 persona) | a management role, not hands-on ML work |
| X07 | exclude | Lead | title | reject | hand-set | a lead role sits above entry-to-mid level |
| X08 | exclude | Head | title | reject | hand-set | a head-of-function role, far above the target level |
| X09 | conditional | Senior | title | see E01 | hand-set | Senior can still fit when the minimum experience asked for is five years or less |
| R01 | role | Machine Learning Engineer | title | gate | inherited (JS1 persona) | the core target role |
| R02 | role | ML Engineer | title | gate | inherited (JS1 persona) | the same role under its common short name |
| R03 | role | AI Engineer | title | gate | inherited (JS1 persona) | builds and ships AI and LLM systems |
| R04 | role | Applied Scientist | title | gate | inherited (JS1 persona) | applied model building, in the target family |
| R05 | role | Data Scientist | title | gate | inherited (JS1 persona) | data science is in the target family |
| R06 | role | Research Engineer | title | gate | hand-set | applied ML research engineering is in the target family |
| R07 | role | Research Scientist | title | gate | hand-set | applied ML research is in the target family |
| R08 | role | Machine Learning Scientist | title | gate | hand-set | the same work as an applied scientist under another name |
| R09 | role | LLM Engineer | title | gate | hand-set | LLM engineering is in the target family |
| R10 | role | Applied AI Engineer | title | gate | hand-set | the same work as an AI engineer under another name |
| L01 | location | Boston | location | 2 | inherited (JS1 persona) | a target city |
| L02 | location | New York | location | 2 | inherited (JS1 persona) | a target city |
| L03 | location | NYC | location | 2 | inherited (JS1 persona) | the same city under its short name |
| L04 | location | Seattle | location | 2 | inherited (JS1 persona) | a target city |
| L05 | location | Remote | location | 2 | term inherited (JS1 persona); US condition hand-set | counts only when the location field also contains one of the tokens us, usa, united states, or u s (the tokenization of U.S.). A location with Remote and no US token gives I cannot tell (section 4, rule 2). |
| T01 | topic | Python | body | 1 | hand-set | the working language of most ML roles |
| T02 | topic | PyTorch | body | 1 | hand-set | a core deep-learning framework |
| T03 | topic | TensorFlow | body | 1 | hand-set | a core deep-learning framework |
| T04 | topic | Keras | body | 1 | hand-set | a deep-learning framework |
| T05 | topic | scikit-learn | body | 1 | hand-set | the standard classical-ML library |
| T06 | topic | Machine Learning | body | 1 | hand-set | names the field of the work itself |
| T07 | topic | Deep Learning | body | 1 | hand-set | names the field of the work itself |
| T08 | topic | LLM | body | 1 | hand-set | LLM-based systems are in the target role |
| T09 | topic | NLP | body | 1 | hand-set | a common applied-ML area |
| T10 | topic | Model Training | body | 1 | hand-set | hands-on model work, not just use of a product |
| T11 | topic | Model Evaluation | body | 1 | hand-set | evaluation is part of the target role |
| T12 | topic | Inference | body | 1 | hand-set | deploying and serving models is part of the target role |
| T13 | topic | Fine-tuning | body | 1 | hand-set | hands-on model adaptation |
| T14 | topic | RAG | body | 1 | hand-set | a common LLM-system pattern |
| T15 | topic | Embeddings | body | 1 | hand-set | a core building block of LLM and retrieval systems |
| T16 | topic | Transformers | body | 1 | hand-set | the dominant model architecture |
| T17 | topic | MLOps | body | 1 | hand-set | deploying and maintaining models is part of the target role |
| T18 | topic | Computer Vision | body | 1 | hand-set | a common applied-ML area |
| E01 | text | the minimum required experience is more than five years | body | reject | hand-set | Riley is entry-to-mid level; a preferred qualification asking for more does not count. Reading rule: the rule applies to the minimum required experience, not to any number of years mentioned in the posting. Count 'N years', 'N+ years' and 'N or more years' only in a sentence that also contains experience or experienced. Skip boilerplate sentences (section 3) and any sentence containing preferred, nice to have, bonus, ideally or plus. N consists of one or more digits. An N-M years or N to M years range counts as N. The range dash may be -, – or —. The skip words are matched as whole-word tokens. Experience and experienced are matched as whole-word tokens. If several remain, the largest N is the minimum required experience. If none remain, no requirement was found: a non-Senior posting passes E01, and a Senior (X09) posting gives I cannot tell (section 4, rule 2). Known limit: a sentence about experience that is not a requirement can still match; the reject audit checks for this. |

Notes:
- Benefits and culture statements are excluded from body matching only when they are boilerplate under section 3; otherwise they are ordinary body text.
- Forward Deployed Engineer is deliberately not a role word: generic forward-deployed roles are not in the target family.

## 2. Score, threshold and close calls

All numbers in this section are hand-set.
- Order: (1) an exclusion term X01 to X08 in the title rejects; (2) no role word R01 to R10 in the title rejects (the role word is a hard gate); (3) no qualifying location L01 to L05 rejects: the location list is a hard gate, matching my labeling rule. Boston, New York/NYC, Seattle and US-qualified Remote are deliberately the only target markets; other US cities (for example San Francisco) are rejected. A known nonmatching location rejects. A missing or empty location gives I cannot tell (section 4, rule 2; subject to the precedence bullet below). A location whose only possible match is bare Remote without a US token also gives I cannot tell; (4) rule E01 rejects, and for a Senior title (X09) it must find a minimum of five years or less; (5) otherwise the posting is scored.
- Evaluate all deterministic rejection gates before returning I cannot tell. If any hard rejection condition is met, the decision is reject. Otherwise, if any condition requires abstention, the decision is I cannot tell. A score below T counts as a hard rejection only when it stays below T for every possible value of the missing field. So a missing location with no topic words rejects (its score can be at most 7), and a missing or empty description gives I cannot tell (section 4, rule 1). The same applies to a bare Remote location without a US token and to a Senior posting where E01 finds no requirement: if the score stays below T for every possible resolution, the posting rejects; otherwise it gives I cannot tell. A posting whose best possible score stays below T while a field is unresolved is rejected with a null score, like gate rejects and abstentions.
- Score = 5 for the role word (once, however many role words match) + 2 for a qualifying location (L01 to L05, once) + 1 for each topic word T01 to T18 found in the body (each counted at most once). Reason: Role and location are gates, so for kept postings they add a constant 7; only the topic weight ranks. T = 8 then means at least one topic word.
- Because location is a gate, every kept posting gets the location +2. It stays in the score so that it can be changed as a setting in Phase 6.
- Threshold T = 8. A posting is kept when score >= 8. Reason: a posting should show both a relevant title and substantive ML or AI content in its text. With location as a gate, 5 + 2 = 7, so one topic word is enough. I accept that a single word such as Python can tip a posting over; the reject audit's close calls will show whether that is too loose.
- Ties: score descending, then board, then posting id ascending, compared as strings. The board key is system:slug, compared lexicographically as a string.
- Close calls: the 10 rejected and the 5 kept postings whose scores are nearest T. Gate-rejected postings receive a null score and are excluded from nearest-threshold selection. Only scored postings are eligible for the close-call audit. Ties are broken at random with the recorded audit seed. If fewer than 10 scored rejects or 5 scored keeps exist, all of them are audited, and the shortfall is reported. Reason: 10 rejected and 5 kept postings provide manageable close-call audit samples. Abstained postings also receive a null score and are not close-call eligible. Audit groups are drawn in the order close calls, random rejects, random keeps; each draw excludes postings already drawn.
- Near-decision group (added after measuring v1): every posting that has a role word (R01 to R10) in its title but is rejected (by exclusion, location or E01), excluding the held-out set and anything already drawn. All of them are audited; no sampling. Reason: with role and location as gates, v1 has 0 scored rejects, so these are the postings nearest the actual decision boundary.
- Every random draw (tie-breaks, audit samples, the held-out set) sorts the candidates by the section 2 tie order first, then draws with Python's random.Random(seed).sample, and records the seed.

## 3. Evidence rules

The posting's own text is its title, location and description fields as fetched in a committed run, after the section 1 normalization. Nothing else counts as evidence: not the company's website, not my knowledge of the company, not another posting.

A claim is one short statement in a shortlist justification, with the field it is about and an exact quote from the posting text, located by character offsets.

- **Supported:** the quote exists in the posting text, it is not boilerplate, and read in its sentence it states the claim.
- **Contradicted:** a quote in the posting text states something incompatible with the claim (for example, the claim says remote and the text says on-site in one city).
- **Insufficient:** no quote can be found, the only quote is boilerplate, or the quote is about something else.

**Boilerplate:** a sentence that appears verbatim in at least 50% of one board's postings in the same collection run. Boilerplate can never support a claim about the role. The 50% is hand-set. Reason: A sentence shared by most of one board's postings describes the company, not the role. Boilerplate matching compares the same normalized sentence string after Section 1 normalization.

**Who labels:** a checker pre-labels each claim (quote found or not, boilerplate or not). My hand label is final, and every disagreement with the pre-label is reported.

## 4. Abstention: when the agent must say "I cannot tell"

For a posting, the agent answers "I cannot tell: <reason>" instead of keep or reject when:
1. the description field is missing or empty, or the board failed in that run;
2. the decision depends on a field that is missing (for example, the score crosses T only through the location rule and the location is empty);
3. a claim that the keep decision needs is labeled insufficient.

Rule 3 applies to the shortlist in Phase 4, not to the filter run in Phase 3.

A description is considered missing or empty when the combined Section 5 text fields, after joining and normalization, contain no tokens.

A failed board's I cannot tell is reported once per failed board, not per posting.

An abstention is reported as an abstention, never as a reject.

## 5. Expected sources

One row per board in config/boards.json. Field names as recorded in evidence/manual-capture/CAPTURE.md (capture 20261125T182322Z). The stripe-js2-nonexistent board was not in that capture; it uses the Greenhouse field names.

| System | Slug | Host | Title | Location | Text | When something is missing |
|---|---|---|---|---|---|---|
| greenhouse | stripe | boards-api.greenhouse.io | `title` | `location.name` | `content` (escaped HTML; requested with `?content=true`) | a failed board gives "I cannot tell: board failed in this run" for that board, and nothing from it reaches the shortlist; a missing or empty description or location follows section 4 |
| greenhouse | stripe-js2-nonexistent (`deliberate_failure: true`) | boards-api.greenhouse.io | `title` | `location.name` | `content` (escaped HTML; requested with `?content=true`) | a failed board gives "I cannot tell: board failed in this run" for that board, and nothing from it reaches the shortlist; a missing or empty description or location follows section 4 |
| lever | lever | api.eu.lever.co | `text` | `categories.location` | `description`, `lists[].text`, `lists[].content`, `additional` (order in the Lever sentence below) | a failed board gives "I cannot tell: board failed in this run" for that board, and nothing from it reaches the shortlist; a missing or empty description or location follows section 4 |
| lever | palantir | api.lever.co | `text` | `categories.location` | `description`, `lists[].text`, `lists[].content`, `additional` (order in the Lever sentence below) | a failed board gives "I cannot tell: board failed in this run" for that board, and nothing from it reaches the shortlist; a missing or empty description or location follows section 4 |
| ashby | linear | api.ashbyhq.com | `title` | `location` | `descriptionHtml` (HTML, normalized using section 1) | a failed board gives "I cannot tell: board failed in this run" for that board, and nothing from it reaches the shortlist; a missing or empty description or location follows section 4 |
| ashby | notion | api.ashbyhq.com | `title` | `location` | `descriptionHtml` (HTML, normalized using section 1) | a failed board gives "I cannot tell: board failed in this run" for that board, and nothing from it reaches the shortlist; a missing or empty description or location follows section 4 |

Lever text is description, then each lists[].text heading followed by its lists[].content, then additional; all of it is the posting's own text.

Use Ashby's descriptionHtml, normalized using Section 1.

Secondary locations and allLocations are not used for location matching. Only the primary location field determines the location gate.

Expected exit: INCOMPLETE (3) because the deliberate failure board fails. Any other exit stops the build.

## 6. Wrong versions the tests must catch

| ID | Wrong version | What it gets wrong |
|---|---|---|
| F01 | Substring matching instead of whole words | "ml" inside "html", "ai" inside "maintain" or "retail" |
| F02 | Topic words counted inside boilerplate | every posting at a company whose About text says "AI" scores the same |
| F03 | A topic word counted every time it appears | long postings rank first |
| F04 | A missing location treated as a match | postings with no location pass the location rule |
| F05 | Insufficient treated as supported | the abstention rule never fires |
| F06 | Ties broken by fetch order | the shortlist changes between identical runs |
| F07 | E01 incorrectly counts years appearing in a sentence containing preferred, nice to have, bonus, ideally or plus. | a preferred qualification rejects the posting |
| F08 | L05 incorrectly treats a bare Remote location without a US token as a US remote match. | a bare Remote passes the location gate instead of giving I cannot tell |
| F09 | Location matching incorrectly uses secondaryLocations or allLocations instead of the primary location field. | a posting whose primary location is outside the target markets passes the location gate |

## 7. Labels: the held-out set

- Drawn once, with a recorded seed, from one committed collection run, before any filter code exists. It is disjoint from every audit sample.
- Pool: two strata. A: titles with ml, machine, learning, ai, scientist or data (30 draws). B: titles in the broad 14-word list but not in A (10 draws). Results are reported per stratum and never pooled; the stratum sizes are counted on the collection run used for the draw and recorded in the draw commit and in the labels/heldout.csv header; the results say nothing about postings outside that pool. Reason: Weighted toward stratum A, where most relevant postings are expected, within about 40 labels I can judge carefully.
- Labeled by me, blind: I see title, location and text, never the filter's score.
- Committed (sealed) before any rule, weight, threshold or prompt is chosen. Used only for the Phase 6 measurements.
- Abstentions are counted separately and excluded from precision and recall. Report their number and denominator.
- For the held-out set, which has no scores, candidates are sorted by board key then posting id (both compared as strings), and each stratum is drawn separately with its own recorded seed.

## 8. Changelog: rules added, cut or rejected after measuring

| Version | Date | Change | Measured on | Before → after | Decision (added, cut, rejected) | Commit |
|---|---|---|---|---|---|---|
| v1 | 2026-11-25 | the two clarifications above | not measured (recorded before the filter existed) | n/a | clarification | see git log |
| v1 | 2026-11-25 | the two clarifications above | not measured (recorded before any verdicts) | n/a | clarification | see git log |
| v1 | 2026-11-25 | near-decision audit group added | filter v1 on run 20261125T200226Z: 0 scored rejects, 17 role-matched gate rejects | close-call rejects 0 → near-decision 12 | added | see git log |
| v1+C1 (candidate) | 2026-11-25 | C1: add "Forward Deployed" as an exclusion term (X10) | the 45 audit rows, Deepak's verdicts at 65c9863 (audit/snapshots/audit-v1@65c9863.csv; audit/changes/C1.md) | filter errors 15/45 → 16/45 (fixed 0, created 1) | rejected (Deepak's Gate 3b criterion) | see git log |
| v1+C2 (candidate) | 2026-11-25 | C2: add title role patterns R11-R14: "Software Engineer, Machine Learning", "Engineer, Machine Learning", "Software Engineer, AI", "Machine Learning" | the 45 audit rows, Deepak's verdicts at 65c9863 (audit/snapshots/audit-v1@65c9863.csv; audit/changes/C2.md) | filter errors 15/45 → 15/45 (fixed 0, created 0) | rejected (Deepak's Gate 3b criterion) | see git log |
| v1+C3 (candidate) | 2026-11-25 | C3: replace T12 "Inference" with "model inference" | the 45 audit rows, Deepak's verdicts at 65c9863 (audit/snapshots/audit-v1@65c9863.csv; audit/changes/C3.md) | filter errors 15/45 → 15/45 (fixed 0, created 0) | rejected (Deepak's Gate 3b criterion) | see git log |
| v1+C4 (candidate) | 2026-11-25 | C4: treat a location of "N/A" as missing (I cannot tell) | the 45 audit rows, Deepak's verdicts at 65c9863 (audit/snapshots/audit-v1@65c9863.csv; audit/changes/C4.md) | filter errors 15/45 → 15/45 (fixed 0, created 0) | rejected (Deepak's Gate 3b criterion) | see git log |
| v1+C5 (candidate) | 2026-11-25 | C5: add "Internship" as an exclusion term next to X05 Intern (X05b) | the 45 audit rows, Deepak's verdicts at 65c9863 (audit/snapshots/audit-v1@65c9863.csv; audit/changes/C5.md) | filter errors 15/45 → 15/45 (fixed 0, created 0) | rejected (Deepak's Gate 3b criterion) | see git log |
