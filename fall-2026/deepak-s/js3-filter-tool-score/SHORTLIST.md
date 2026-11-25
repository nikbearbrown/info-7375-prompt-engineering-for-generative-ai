# SHORTLIST.md: the source-grounded shortlist of filter v1

Job-Search Agent 3. Sections 1 to 6 are facts written by Claude Code (claude-opus-5-5) on 2026-11-25 from committed files (claim labels as of cec6a48); each cites its file. Section 7 is Deepak's.

## 1. The shortlist

The final filter version is v1 (no rule change was adopted; AUDIT.md section 6b). Its kept postings, in the FILTER.md section 2 tie order; FILTER.md sets no top N, so all are shortlisted (`shortlist/shortlist.json`, commit ca5754f):

| Rank | Posting | Title | Location | Score |
|---|---|---|---|---|
| 1 | greenhouse:stripe:8187574 | Machine Learning Engineer, Transaction Risk | Seattle, New York City | 13 |
| 2 | greenhouse:stripe:8243617 | Machine Learning Engineer, Radar | Seattle | 13 |
| 3 | lever:palantir:636fc05c-d348-4a06-be51-597cb9e07488 | Forward Deployed AI Engineer | New York, NY | 10 |

## 2. Every claim, with the checker's pre-label and Deepak's label

29 claims (`shortlist/claims.csv`): 23 written from a matched rule and its span (`jobwatch/shortlist.py` RULE claims), 6 written by the Claude judge. The judge: `claude -p` through the JS1 claude-cli backend's argv and environment (`jobwatch/claude_judge.py`), model `claude-sonnet-5-5` as reported by the CLI (version 2.1.332), 3 calls on 2026-11-25 between 21:16:27Z and 21:16:33Z, prompt `prompts/js3_claims_v1.md`; each call's exact prompt, argv, raw response and metadata are in `shortlist/judge/`.

The checker (FILTER.md section 3) pre-labels a claim insufficient when its quote is not found at its offsets in the posting's own text, or lies only in boilerplate sentences; otherwise "quote found, not boilerplate". All 29 quotes were found and none is boilerplate, so no claim is pre-labeled insufficient.

Deepak's hand labels (supported, contradicted, insufficient) are final under FILTER.md section 3. Deepak labeled every claim with `python -m jobwatch label shortlist/claims.csv`, committed in cec6a48: 29 of 29 supported (23 of 23 rule claims, 6 of 6 judge claims), 0 contradicted, 0 insufficient. One claim carries a note: claim 8 of greenhouse:stripe:8243617, note "s".

| Claim | Source | Claim text | Field [start:end] | Quote | Pre-label (checker) | Deepak's label |
|---|---|---|---|---|---|---|
| 1 of greenhouse:stripe:8187574 | rule:R01 | The role is a Machine Learning Engineer role. | title [0:25] | Machine Learning Engineer | quote found, not boilerplate | supported |
| 2 of greenhouse:stripe:8187574 | rule:L02 | The job is based in New York. | location [9:17] | New York | quote found, not boilerplate | supported |
| 3 of greenhouse:stripe:8187574 | rule:E01 | The minimum required experience stated is 5 years, five or fewer. | text [4114:4122] | 5+ years | quote found, not boilerplate | supported |
| 4 of greenhouse:stripe:8187574 | rule:T06 | The work involves Machine Learning. | text [572:588] | machine learning | quote found, not boilerplate | supported |
| 5 of greenhouse:stripe:8187574 | rule:T07 | The work involves Deep Learning. | text [5272:5285] | deep learning | quote found, not boilerplate | supported |
| 6 of greenhouse:stripe:8187574 | rule:T08 | The work involves LLM. | text [5306:5309] | LLM | quote found, not boilerplate | supported |
| 7 of greenhouse:stripe:8187574 | rule:T10 | The work involves Model Training. | text [4686:4700] | model training | quote found, not boilerplate | supported |
| 8 of greenhouse:stripe:8187574 | rule:T11 | The work involves Model Evaluation. | text [4379:4395] | model evaluation | quote found, not boilerplate | supported |
| 9 of greenhouse:stripe:8187574 | rule:T12 | The work involves Inference. | text [4714:4723] | inference | quote found, not boilerplate | supported |
| 10 of greenhouse:stripe:8187574 | judge | The role is hands-on ML work building, training, evaluating and deploying models, matching the target role's core duties. | text [2274:2419] | Build, train, evaluate, and deploy models that detect fraud and abuse across Stripe’s g... | quote found, not boilerplate | supported |
| 11 of greenhouse:stripe:8187574 | judge | It requires 5+ years of production ML experience, which is above an entry-to-mid-level target. | text [4114:4227] | 5+ years of experience developing, evaluating, and deploying machine learning models in... | quote found, not boilerplate | supported |
| 1 of greenhouse:stripe:8243617 | rule:R01 | The role is a Machine Learning Engineer role. | title [0:25] | Machine Learning Engineer | quote found, not boilerplate | supported |
| 2 of greenhouse:stripe:8243617 | rule:L04 | The job is based in Seattle. | location [0:7] | Seattle | quote found, not boilerplate | supported |
| 3 of greenhouse:stripe:8243617 | rule:E01 | The minimum required experience stated is 2 years, five or fewer. | text [3341:3349] | 2+ years | quote found, not boilerplate | supported |
| 4 of greenhouse:stripe:8243617 | rule:T06 | The work involves Machine Learning. | text [564:580] | machine learning | quote found, not boilerplate | supported |
| 5 of greenhouse:stripe:8243617 | rule:T07 | The work involves Deep Learning. | text [4345:4358] | deep learning | quote found, not boilerplate | supported |
| 6 of greenhouse:stripe:8243617 | rule:T08 | The work involves LLM. | text [4379:4382] | LLM | quote found, not boilerplate | supported |
| 7 of greenhouse:stripe:8243617 | rule:T10 | The work involves Model Training. | text [3830:3844] | model training | quote found, not boilerplate | supported |
| 8 of greenhouse:stripe:8243617 | rule:T11 | The work involves Model Evaluation. | text [3522:3538] | model evaluation | quote found, not boilerplate | supported |
| 9 of greenhouse:stripe:8243617 | rule:T12 | The work involves Inference. | text [3858:3867] | inference | quote found, not boilerplate | supported |
| 10 of greenhouse:stripe:8243617 | judge | The role centers on building, training, evaluating, and deploying ML models for fraud detection. | text [1821:1922] | Build, train, evaluate, and deploy models that detect fraud and abuse across Stripe’s g... | quote found, not boilerplate | supported |
| 11 of greenhouse:stripe:8243617 | judge | It requires 2+ years of production ML experience, which fits entry-to-mid level. | text [3341:3454] | 2+ years of experience developing, evaluating, and deploying machine learning models in... | quote found, not boilerplate | supported |
| 1 of lever:palantir:636fc05c-d348-4a06-be51-597cb9e07488 | rule:R03 | The role is a AI Engineer role. | title [17:28] | AI Engineer | quote found, not boilerplate | supported |
| 2 of lever:palantir:636fc05c-d348-4a06-be51-597cb9e07488 | rule:L02 | The job is based in New York. | location [0:8] | New York | quote found, not boilerplate | supported |
| 3 of lever:palantir:636fc05c-d348-4a06-be51-597cb9e07488 | rule:T01 | The work involves Python. | text [2238:2244] | Python | quote found, not boilerplate | supported |
| 4 of lever:palantir:636fc05c-d348-4a06-be51-597cb9e07488 | rule:T06 | The work involves Machine Learning. | text [1928:1944] | Machine Learning | quote found, not boilerplate | supported |
| 5 of lever:palantir:636fc05c-d348-4a06-be51-597cb9e07488 | rule:T08 | The work involves LLM. | text [1033:1036] | LLM | quote found, not boilerplate | supported |
| 6 of lever:palantir:636fc05c-d348-4a06-be51-597cb9e07488 | judge | The role centers on building and productionizing LLM-based workflows with customers. | text [429:541] | you will build end-to-end workflows, take them to production, and solve real world prob... | quote found, not boilerplate | supported |
| 7 of lever:palantir:636fc05c-d348-4a06-be51-597cb9e07488 | judge | It requires hands-on LLM experience and ML fundamentals including evaluation and training. | text [1907:1998] | Strong foundation in Machine Learning basics (Evaluation, Training, Problem Decompositi... | quote found, not boilerplate | supported |

## 3. Disagreements between pre-label and hand label

None. Every pre-label is "quote found, not boilerplate" and every hand label is "supported" (shortlist/claims.csv at cec6a48): 0 of 29 claims disagree.

## 4. Relevance is not entailment: candidates from this shortlist

Each candidate below is a claim whose posting matched the filter's words, with the sentence its quote sits in (`data/postings-20261125T200226Z.jsonl`, sentence offsets). Whether the sentence supports the claim is Deepak's label; these are candidates, not conclusions.

- greenhouse:stripe:8187574, claim 9, "The work involves Inference." (rule T12) and claim 7, "The work involves Model Training." (rule T10). Sentence: "Experience designing and operating production ML systems, including several of: large-scale data and feature pipelines, distributed model training, lo..." The quote is one option in a "several of" list of experience, not a statement of the work.
- lever:palantir:636fc05c-d348-4a06-be51-597cb9e07488, claim 3, "The work involves Python." (rule T01). Sentence: "Strong coder with demonstrated proficiency in programming languages such as Python, Java, C++, TypeScript/JavaScript, or similar." Python is one example of a language, not a stated part of the work.
- lever:palantir:636fc05c-d348-4a06-be51-597cb9e07488, claim 1, "The role is a AI Engineer role." (rule R03). Title: "Forward Deployed AI Engineer". FILTER.md section 1 notes that generic forward-deployed roles are not in the target family; the words match R03.
- greenhouse:stripe:8187574, claim 11 (judge): "It requires 5+ years of production ML experience, which is above an entry-to-mid-level target." Quote: "5+ years of experience developing, evaluating, and deploying machine learning models in a production environment." The same quote gives rule claim 3, "The minimum required experience stated is 5 years, five or fewer." (E01 passes at five years). The two claims read the same quote in opposite directions.

Deepak's labels for these candidates (cec6a48): all supported, including claim 11 of greenhouse:stripe:8187574 (the judge's "above an entry-to-mid-level target") and claim 3 of greenhouse:stripe:8187574 (E01, "five or fewer"), which read the same quote in opposite directions.

## 5. The abstention rule's outcomes on the dataset

- Filter v1 on all 1285 postings (`data/filter-v1.jsonl`): 0 postings gave I cannot tell; 1 board-level I cannot tell (greenhouse:stripe-js2-nonexistent, HTTP 404). Every posting met a hard rejection or was kept, so the section 2 precedence bullet never reached an abstention condition.
- Location states as the filter reads them (`jobwatch/filter.py` location_status over the dataset): match 366, known nonmatch 906, bare Remote without a US token 13, missing 0. No posting has an empty description (`text` with no tokens: 0).
- Section 4 rule 3 on the shortlist (`jobwatch/shortlist.py` decide): on the pre-labels and on Deepak's hand labels (cec6a48), all 3 shortlisted postings stay keep: role and location claims supported, and 6, 6 and 3 topic claims supported where 1 is needed. Rule 3 did not fire on this shortlist.

## 6. Candidate counterexamples to the abstention rule, found in the data

From the location fields of `data/postings-20261125T200226Z.jsonl`:
- 25 postings have the location "N/A". It has tokens, so the filter reads it as a known nonmatching location and rejects; it carries no location information, which section 2 says should give I cannot tell when the decision depends on it. (Candidate change C4 addressed this and was rejected under Deepak's criterion: on the audit rows it changed nothing, AUDIT.md section 6b.)
- 13 postings have a Remote location without a US token and give I cannot tell by FILTER.md section 2, including locations that state a non-US country: "Poland - Remote OR Romania - Remote", "Sweden (Remote)", "Toronto, Vancouver, Canada-Remote", "CA-Toronto; CA-Remote", "London, Dublin, UK-Remote". The evidence there is not missing; it names a country outside the target.
- "SF, NY, Remote" is a bare Remote under the rule, because "NY" is not one of the location terms (Boston, New York, NYC, Seattle); "Chicago, Atlanta, Remote" and "Chicago, Remote" likewise abstain although they name US cities.
- The checker cannot pre-label "the quote is about something else" (FILTER.md section 3, insufficient): every shortlisted quote was found and none is boilerplate, so section 4 rule 3 fires only on Deepak's hand labels. Deepak labeled all 29 claims supported (cec6a48), including the section 4 candidates, so rule 3 did not fire on any posting.

## 7. Conclusions

### My claim labels

I labeled all 29 claims (23 from the matched rules, 6 from the Claude judge) as supported, and none disagreed with the checker's pre-labels. Every quote I checked states its claim.

### Relevance is not entailment

The case comes from the audit's false-friend candidates (AUDIT.md section 6). A posting I judged not relevant matches my topic words, including T12 "inference", but its text uses the word in "statistical inference". The words are relevant to my filter; the claim they suggest, that the role involves model inference or serving, is not supported by the text. Within the shortlist itself I labeled all 29 claims supported, so the shortlist does not contain such a case.

### My abstention rule

The agent says "I cannot tell" when the posting text is empty, when a missing or unresolved field decides the outcome (an empty location, a bare Remote with no US token, a Senior title with no stated minimum), and, for the shortlist, when a claim the keep decision needs is insufficient. A definite reject always wins over an abstention.

### A counterexample that exposes its limits

A location of "N/A" is treated as a known nonmatching location, so the posting is rejected instead of giving "I cannot tell". "N/A" means the location is missing, but the rule only fires on empty fields, not on fields that are missing in meaning. The rule checks the form of the evidence, not what it says.
