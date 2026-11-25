# Claim labels against the checker, filter run 2026-11-21T044414Z

Computed by `tools/score_claims.py` from Aravind's labels in LABELS.md (committed before the checker's labels were opened) and `sealed/checker-labels.json` (SHA-256 `c464b7a96222c0b4304f3dae8a2c2715c095b3c937e38e6244b95ad1d856bc2d`, the hash the kit's README published before any human label). Claude Code wrote the script and this file; the labels are his. Only he may mark a claim supported, so this measures the checker against him.

**Overall:** the checker agrees with him on 101 of 105 claims.

## By claim type

| Claim type | Claims | Checker agrees | His labels (S / C / I) | Checker's (S / C / I) |
|---|---:|---:|---|---|
| 1. full time (R1) | 10 | 10 | 10 / 0 / 0 | 10 / 0 / 0 |
| 2. place (R2) | 10 | 10 | 10 / 0 / 0 | 10 / 0 / 0 |
| 3. no level word (R3) | 10 | 10 | 10 / 0 / 0 | 10 / 0 / 0 |
| 4. software engineering title (R4) | 10 | 10 | 10 / 0 / 0 | 10 / 0 / 0 |
| 5. no status requirement (R5) | 10 | 10 | 0 / 0 / 10 | 0 / 0 / 10 |
| 6. no start before May 2027 (R6) | 10 | 10 | 0 / 0 / 10 | 0 / 0 / 10 |
| 7. years (R7) | 10 | 10 | 1 / 0 / 9 | 1 / 0 / 9 |
| 8. topic group (the score) | 35 | 31 | 34 / 0 / 1 | 32 / 0 / 3 |

## Every pair of labels

| His label | Checker's label | Claims |
|---|---|---:|
| insufficient | insufficient | 29 |
| insufficient | supported | 1 |
| supported | insufficient | 3 |
| supported | supported | 72 |

## Every disagreement

| Claim | Posting | Claim | His label | His note | Checker | Checker's reason |
|---|---|---|---|---|---|---|
| 04.8a | Software Engineer, Compute Foundations | It describes work in the topic group APIs ("APIs"). | supported |  | insufficient | it names 'APIs' with an action word, but nothing in it says this is the role's work; it may describe the company |
| 04.8c | Software Engineer, Compute Foundations | It describes work in the topic group Cloud infrastructure ("Kubernetes"). | supported |  | insufficient | it names 'Kubernetes' with an action word, but nothing in it says this is the role's work; it may describe the company |
| 05.8d | Software Engineer, Compute Infrastructure | It describes work in the topic group Developer tools ("developer tools"). | supported |  | insufficient | it names 'developer tools' with an action word, but nothing in it says this is the role's work; it may describe the company |
| 09.8c | Software Engineer, Ads Integrity | It describes work in the topic group Developer tools ("build systems"). | insufficient | the sentence mentions distributed systems but does not establish that this role involves developer tools or build systems | supported | it names 'build systems' with an action word, and is about the role (the word 'you') |

## Flip checks (FLIP-CHECKS.md, chapter 7)

For each disagreement, Claude Code found the sentence that bears most directly on the claim, after the checker's labels were opened, and Aravind said whether it changed his label. LABELS.md is unchanged.

| Claim | His frozen label | Checker | His label after | His words |
|---|---|---|---|---|
| 04.8a | supported | insufficient | supported | "04.8a stays" |
| 04.8c | supported | insufficient | supported | "04.8c stays" |
| 05.8d | supported | insufficient | insufficient | "05.8d → I" |
| 09.8c | insufficient | supported | insufficient | "09.8c stays" |

After the flip checks, the checker agrees with him on 102 of 105 claims (frozen: 101 of 105).

## Relevance is not entailment: topic claims on kept postings he did not find supported

Every posting here was kept and shortlisted, and each topic group below added to its score. The quoted sentence is relevant (it contains the topic word), but he found that it does not say this role's work is in that group.

| Claim | Posting (score) | Group | His note |
|---|---|---|---|
| 09.8c | Software Engineer, Ads Integrity (65) | Developer tools | the sentence mentions distributed systems but does not establish that this role involves developer tools or build systems |
