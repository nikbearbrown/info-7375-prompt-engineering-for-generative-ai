# FILTER v2 candidates — measured 2123 postings (70 relevant under v1), hand labels from audit/hand_verdicts.csv

Only v1-relevant postings can change (every candidate is stricter). "fixed" = a hand-labeled sample where Isaac disagreed with v1 and agrees with the variant; "broken" = Isaac agreed with v1 and disagrees with the variant.

| variant | v1 relevant → cut (all postings) | relevant left | hand-labeled samples: disagreements (v1 = 8) | fixed | broken |
|---|---|---|---|---|---|
| A | 3 | 67 | 6 | S01, S20 | — |
| B1 | 0 | 70 | 8 | — | — |
| B2 | 8 | 62 | 7 | S16 | — |
| C | 22 | 48 | 9 | S01, S17, S24, S46 | S04, S14, S25, S30, S50 |
| A+B2+C | 31 | 39 | 7 | S01, S16, S17, S20, S24, S46 | S04, S14, S25, S30, S50 |

Caution: the candidates were found by reading these same hand-labeled samples, so the "fixed" column is not an independent test; it shows only that each variant does what it was built for. "broken" and the full-list cuts below are the part worth checking.

## A — postings cut

| board | posting id | title | why |
|---|---|---|---|
| openai | 55150071-fce8-48f5-aea4-14ed78b83511 | Software Engineer, Applied Emerging Talent (2027) | ceiling 1 years < Aarav's 2 |
| stripe | 8128744 | Software Engineer, New Grad | ceiling 1.5 years < Aarav's 2 |
| stripe | 8212508 | Software Engineer, Early Career — Immediate Start | ceiling 1.5 years < Aarav's 2 |

## B1 — postings cut

| board | posting id | title | why |
|---|---|---|---|

## B2 — postings cut

| board | posting id | title | why |
|---|---|---|---|
| openai | 2cba0d45-7a4f-4f38-ac73-3f8633bf0349 | Software Engineer, Developer Productivity | max 5 years > 4 |
| openai | 3c67f712-697d-48d8-b05c-01be896e61da | Software Engineer, Scaled Abuse | max 5 years > 4 |
| openai | 460b4295-3803-4dda-983d-3b0fea0b0fc4 | Software Engineer, Habitat (Online Data) | max 8 years > 4 |
| openai | 52c72cb9-7c44-4cba-b440-e05262a38491 | Full-Stack Software Engineer, Intelligence & Investigations | max 7 years > 4 |
| stripe | 7396679 | Software Engineer, Secrets Infrastructure | max 5 years > 4 |
| stripe | 8197135 | Software Engineer, High Availability and Disaster Recovery | max 5 years > 4 |
| stripe | 8198280 | Software Engineer, Backend | max 6 years > 4 |
| stripe | 8332718 | Software Engineer, Fraud System Interventions | max 5 years > 4 |

## C — postings cut

| board | posting id | title | why |
|---|---|---|---|
| openai | 1fec5ecd-5b7b-45bc-bc8c-ac7184565551 | Software Engineer, Core Network Engineering | rule 3 1 found < 2 |
| openai | 21bfde35-ffec-42d2-a2c6-8a03dad789d5 | Software Engineer, Core Services | rule 3 1 found < 2 |
| openai | 38e3c4bf-a632-405e-9619-b87382ca2472 | Applied AI Software Engineer, GTM Growth Engineering | rule 3 1 found < 2 |
| openai | 40f2f959-20f8-40ca-8b8c-154b6774193a | Software Engineer, Compute Foundations | rule 3 1 found < 2 |
| openai | 56d541d3-02b5-44d8-b40b-4df72cdd0405 | Software Engineer, AI for Chip Design | rule 3 1 found < 2 |
| openai | 60573bf4-13ad-4933-aba7-729f428e9f69 | Control Systems Software Engineer, Robotics | rule 3 1 found < 2 |
| openai | 6b47238e-025a-4350-b270-2f3564002fcc | Full Stack Software Engineer, ChatGPT ImageGen | rule 3 1 found < 2 |
| openai | 70aaaafa-fe2f-4409-9a72-c0faf50d7d01 | Software Engineer - Data Aquisition (systems) | rule 3 1 found < 2 |
| openai | 783704d7-5afa-45aa-899b-1d6799f73004 | Software Engineer, Agent Platform | rule 3 1 found < 2 |
| openai | 7ade7a12-845c-4e3a-af23-c028420bd181 | Software Engineer, Codex Core Agents | rule 3 1 found < 2 |
| openai | 9248eab6-74e0-4940-98eb-ca09b17da532 | Software Engineer, AI accelerator Runtime | rule 3 1 found < 2 |
| openai | 9b2c68f2-5ce8-44f9-a30c-d8016ac66d86 | Connectivity Software Engineer, Consumer Devices | rule 3 1 found < 2 |
| openai | 9d48e2e6-41a9-4a90-8b3b-6cc960e95c2f | Software Engineer, Developer Productivity - Inference Runtime | rule 3 1 found < 2 |
| openai | a58add97-1968-4d5c-b504-ab62bea12df3 | Software Engineer, Fleet Infrastructure | rule 3 1 found < 2 |
| openai | ca300a6d-a2a7-4580-aad7-323fbdfee7b1 | Software Engineer, Compute Infrastructure | rule 3 1 found < 2 |
| openai | e44bfa94-0b82-4d0c-b224-02155b76eea9 | Software Engineer, Infrastructure - Analytics Platform | rule 3 1 found < 2 |
| stripe | 6042172 | Backend Engineer, Core Technology | rule 3 1 found < 2 |
| stripe | 7235875 | Software Engineer, Privy | rule 3 1 found < 2 |
| stripe | 7982720 | Software Engineer, Secure Devices | rule 3 1 found < 2 |
| stripe | 8128744 | Software Engineer, New Grad | rule 3 1 found < 2 |
| stripe | 8212508 | Software Engineer, Early Career — Immediate Start | rule 3 1 found < 2 |
| stripe | 8265763 | Software Engineer, Internal Identity | rule 3 1 found < 2 |

## A+B2+C — postings cut

| board | posting id | title | why |
|---|---|---|---|
| openai | 1fec5ecd-5b7b-45bc-bc8c-ac7184565551 | Software Engineer, Core Network Engineering | rule 3 1 found < 2 |
| openai | 21bfde35-ffec-42d2-a2c6-8a03dad789d5 | Software Engineer, Core Services | rule 3 1 found < 2 |
| openai | 2cba0d45-7a4f-4f38-ac73-3f8633bf0349 | Software Engineer, Developer Productivity | max 5 years > 4 |
| openai | 38e3c4bf-a632-405e-9619-b87382ca2472 | Applied AI Software Engineer, GTM Growth Engineering | rule 3 1 found < 2 |
| openai | 3c67f712-697d-48d8-b05c-01be896e61da | Software Engineer, Scaled Abuse | max 5 years > 4 |
| openai | 40f2f959-20f8-40ca-8b8c-154b6774193a | Software Engineer, Compute Foundations | rule 3 1 found < 2 |
| openai | 460b4295-3803-4dda-983d-3b0fea0b0fc4 | Software Engineer, Habitat (Online Data) | max 8 years > 4 |
| openai | 52c72cb9-7c44-4cba-b440-e05262a38491 | Full-Stack Software Engineer, Intelligence & Investigations | max 7 years > 4 |
| openai | 55150071-fce8-48f5-aea4-14ed78b83511 | Software Engineer, Applied Emerging Talent (2027) | ceiling 1 years < Aarav's 2 |
| openai | 56d541d3-02b5-44d8-b40b-4df72cdd0405 | Software Engineer, AI for Chip Design | rule 3 1 found < 2 |
| openai | 60573bf4-13ad-4933-aba7-729f428e9f69 | Control Systems Software Engineer, Robotics | rule 3 1 found < 2 |
| openai | 6b47238e-025a-4350-b270-2f3564002fcc | Full Stack Software Engineer, ChatGPT ImageGen | rule 3 1 found < 2 |
| openai | 70aaaafa-fe2f-4409-9a72-c0faf50d7d01 | Software Engineer - Data Aquisition (systems) | rule 3 1 found < 2 |
| openai | 783704d7-5afa-45aa-899b-1d6799f73004 | Software Engineer, Agent Platform | rule 3 1 found < 2 |
| openai | 7ade7a12-845c-4e3a-af23-c028420bd181 | Software Engineer, Codex Core Agents | rule 3 1 found < 2 |
| openai | 9248eab6-74e0-4940-98eb-ca09b17da532 | Software Engineer, AI accelerator Runtime | rule 3 1 found < 2 |
| openai | 9b2c68f2-5ce8-44f9-a30c-d8016ac66d86 | Connectivity Software Engineer, Consumer Devices | rule 3 1 found < 2 |
| openai | 9d48e2e6-41a9-4a90-8b3b-6cc960e95c2f | Software Engineer, Developer Productivity - Inference Runtime | rule 3 1 found < 2 |
| openai | a58add97-1968-4d5c-b504-ab62bea12df3 | Software Engineer, Fleet Infrastructure | rule 3 1 found < 2 |
| openai | ca300a6d-a2a7-4580-aad7-323fbdfee7b1 | Software Engineer, Compute Infrastructure | rule 3 1 found < 2 |
| openai | e44bfa94-0b82-4d0c-b224-02155b76eea9 | Software Engineer, Infrastructure - Analytics Platform | rule 3 1 found < 2 |
| stripe | 6042172 | Backend Engineer, Core Technology | rule 3 1 found < 2 |
| stripe | 7235875 | Software Engineer, Privy | rule 3 1 found < 2 |
| stripe | 7396679 | Software Engineer, Secrets Infrastructure | max 5 years > 4 |
| stripe | 7982720 | Software Engineer, Secure Devices | rule 3 1 found < 2 |
| stripe | 8128744 | Software Engineer, New Grad | ceiling 1.5 years < Aarav's 2; rule 3 1 found < 2 |
| stripe | 8197135 | Software Engineer, High Availability and Disaster Recovery | max 5 years > 4 |
| stripe | 8198280 | Software Engineer, Backend | max 6 years > 4 |
| stripe | 8212508 | Software Engineer, Early Career — Immediate Start | ceiling 1.5 years < Aarav's 2; rule 3 1 found < 2 |
| stripe | 8265763 | Software Engineer, Internal Identity | rule 3 1 found < 2 |
| stripe | 8332718 | Software Engineer, Fraud System Interventions | max 5 years > 4 |

## L1 on top of v2 — add ['ny', 'sea', 'sf', 'nyc', 'seattle', 'san francisco', 'new york'] to profile.locations

Verdicts that change: **0** of 2123.

| board | posting id | title | location | v2 → v2 + L1 |
|---|---|---|---|---|

Still cut at rule 2 with L1 (53), most common locations:

| location | postings |
|---|---|
| London, UK; United Kingdom | 6 |
| Hybrid; London, United Kingdom | 3 |
| Dublin; Ireland Locations | 3 |
| In-Office; Lisboa, Lisboa, Portugal; London, United Kingdom | 2 |
| N/A; Canada Locations | 2 |
| Dublin, Ireland; Ireland Locations | 2 |
| Bangalore; India Locations | 2 |
| Sao Paulo; Brazil Locations | 2 |
| Toronto; Toronto, Ontario, Canada | 2 |
| Barcelona; Spain Locations | 2 |
| In-Office; Remote India | 1 |
| Hybrid; Lisboa, Lisboa, Portugal; London, United Kingdom | 1 |
| Hybrid; Remote India | 1 |
| Hybrid; Lisboa, Lisboa, Portugal | 1 |
| Hybrid; Singapore; Sydney, New South Wales, Australia; Japan, 東京都東京都 | 1 |
