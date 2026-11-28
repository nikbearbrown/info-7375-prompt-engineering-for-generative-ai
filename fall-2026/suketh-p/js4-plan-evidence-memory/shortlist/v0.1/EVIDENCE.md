# The shortlist's evidence table

Written by `python3 -m jobwatch.js3 claims-final shortlist/v0.1` from the claims Claude drafted (`claims.jsonl`), the student's first labels (`claim-labels.json`), Claude's challenge (`flip/flip.jsonl`) and the student's decisions on it (`flip-decisions.json`). The label in the last column is the student's.

First labels: supported 48, contradicted 0, insufficient 16. Final: supported 40, contradicted 0, insufficient 24.

The student's note on every C8, as written: Each C8 supports the company-wide sponsorship statement as written. Sponsorship for a specific role or candidate remains unresolved.

## R1 · Research Engineer, Machine Learning (Reinforcement Learning) (greenhouse/anthropic 4613568008)

| ID | Kind | Claim | Quote (field; check) | First label (note) | Claude's challenge | Final label (note) |
| --- | --- | --- | --- | --- | --- | --- |
| R1-C1 | work | The role works on fundamental research in reinforcement learning for large language models. | “You'll work on fundamental research in reinforcement learning” (description; quote found) | supported | no sentence named | supported |
| R1-C2 | location | The role is listed in either San Francisco, CA or New York City, NY. | “San Francisco, CA \| New York City, NY” (location; quote found) | supported | no sentence named | **insufficient**, changed after the challenge (Every location claim leaves out the hybrid condition, so all eight become insufficient.) |
| R1-C3 | new_grads | I cannot tell whether this role accepts new graduates or early-career applicants. | none (no quote) | insufficient (The posting ties experience to internal job level and leaves new-graduate acceptance unstated.) | no sentence named | insufficient |
| R1-C4 | qualification | The minimum education is a Bachelor's degree or an equivalent combination of education, training, or experience. | “Minimum education: Bachelor’s degree or an equivalent combination of education, training, and/or experience” (description; quote found) | supported | no sentence named | supported |
| R1-C5 | qualification | The years of experience required depend on the internal job level for the position. | “Years of experience required will correlate with the internal job level requirements for the position” (description; quote found) | supported | no sentence named | supported |
| R1-C6 | qualification | A good fit is proficient in Python with async/concurrent programming. | “Are proficient in Python and async/concurrent programming” (description; quote found) | supported | no sentence named | supported |
| R1-C7 | work_authorization | I cannot tell what this posting requires for authorization to work. | none (no quote) | insufficient (The posting describes general visa sponsorship and leaves role-specific work authorization requirements unstated.) | no sentence named | insufficient |
| R1-C8 | sponsorship | The posting says Anthropic sponsors visas, though not for every role or candidate. | “We do sponsor visas! However, we aren't able to successfully sponsor visas for every role and every candidate.” (description; quote found) | supported | no sentence named | supported |

## R2 · ML/Research Engineer, Safeguards (greenhouse/anthropic 4949336008)

| ID | Kind | Claim | Quote (field; check) | First label (note) | Claude's challenge | Final label (note) |
| --- | --- | --- | --- | --- | --- | --- |
| R2-C1 | work | The role works on detecting misuse of Anthropic's AI systems. | “help detect and mitigate misuse of our AI systems” (description; quote found) | supported | no sentence named | supported |
| R2-C2 | location | The role is listed in San Francisco, CA or New York City, NY. | “San Francisco, CA \| New York City, NY” (location; quote found) | supported | no sentence named | **insufficient**, changed after the challenge (Every location claim leaves out the hybrid condition, so all eight become insufficient.) |
| R2-C3 | new_grads | I cannot tell whether this role accepts new graduates or early-career applicants. | none (no quote) | insufficient (The posting lists 4+ years under good-fit criteria and leaves new-graduate acceptance unstated.) | no sentence named | insufficient |
| R2-C4 | qualification | The posting lists 4+ years of experience in ML engineering, research engineering, or applied research as a sign of a good fit. | “Have 4+ years of experience in ML engineering, research engineering, or applied research” (description; quote found) | supported | no sentence named | supported |
| R2-C5 | qualification | The minimum education is a Bachelor's degree or an equivalent combination of education, training, or experience. | “Minimum education: Bachelor’s degree or an equivalent combination of education, training, and/or experience” (description; quote found) | supported | no sentence named | supported |
| R2-C6 | qualification | The posting lists proficiency in Python as a sign of a good fit. | “Have proficiency in Python” (description; quote found) | supported | no sentence named | supported |
| R2-C7 | work_authorization | I cannot tell what this posting requires for authorization to work. | none (no quote) | insufficient (The posting describes general visa sponsorship and leaves role-specific work authorization requirements unstated.) | no sentence named | insufficient |
| R2-C8 | sponsorship | The posting says Anthropic sponsors visas, though it cannot successfully sponsor every role or every candidate. | “We do sponsor visas! However, we aren't able to successfully sponsor visas for every role and every candidate.” (description; quote found) | supported | no sentence named | supported |

## R3 · Pre-training Data Infrastructure Engineer (greenhouse/anthropic 4973067008)

| ID | Kind | Claim | Quote (field; check) | First label (note) | Claude's challenge | Final label (note) |
| --- | --- | --- | --- | --- | --- | --- |
| R3-C1 | work | The role designs data processing infrastructure for large language model training. | “Design and implement data processing infrastructure for large language model training” (description; quote found) | supported | no sentence named | supported |
| R3-C2 | location | The role is located in San Francisco, CA. | “San Francisco, CA” (location; quote found) | supported | no sentence named | **insufficient**, changed after the challenge (Every location claim leaves out the hybrid condition, so all eight become insufficient.) |
| R3-C3 | new_grads | The role does not appear open to new graduates because it asks for 5+ years of experience outside of internships. | “5+ YOE outside of internships” (description; quote found) | insufficient (The posting describes a Staff role and lists 5+ years outside internships under good-fit criteria. That signals the target level and leaves new-graduate eligibility unresolved.) | “Minimum years of experience: Years of experience required will correlate with the internal job level requirements for the position” → supported (quote found) | **supported**, changed after the challenge (The sentence, with the Staff level, settles that the role is not open to new graduates.) |
| R3-C4 | qualification | The posting lists 5+ years of experience outside of internships as a qualification. | “5+ YOE outside of internships” (description; quote found) | supported | no sentence named | supported |
| R3-C5 | qualification | The minimum education is a bachelor's degree or an equivalent combination of education, training, or experience. | “Minimum education: Bachelor’s degree or an equivalent combination of education, training, and/or experience” (description; quote found) | supported | no sentence named | supported |
| R3-C6 | qualification | The posting lists an advanced degree in Computer Science or a related field as a qualification. | “Advanced degree in Computer Science or related field” (description; quote found) | supported | no sentence named | supported |
| R3-C7 | work_authorization | I cannot tell what the posting requires regarding authorization to work. | none (no quote) | insufficient (The posting describes general visa sponsorship and leaves role-specific work authorization requirements unstated.) | no sentence named | insufficient |
| R3-C8 | sponsorship | The posting says Anthropic sponsors visas, though it cannot successfully sponsor visas for every role or candidate. | “We do sponsor visas! However, we aren't able to successfully sponsor visas for every role and every candidate.” (description; quote found) | supported | no sentence named | supported |

## R4 · Applied AI Engineer, Enterprise (greenhouse/anthropic 5057647008)

| ID | Kind | Claim | Quote (field; check) | First label (note) | Claude's challenge | Final label (note) |
| --- | --- | --- | --- | --- | --- | --- |
| R4-C1 | work | The role serves as a trusted technical advisor to Enterprise Technology companies that are adopting the Claude API into their core products. | “trusted technical advisor to Enterprise Technology companies adopting the Claude API into their core products” (description; quote found) | supported | no sentence named | supported |
| R4-C2 | location | The role is located in San Francisco, CA or New York City, NY. | “San Francisco, CA \| New York City, NY” (location; quote found) | supported | no sentence named | **insufficient**, changed after the challenge (Every location claim leaves out the hybrid condition, so all eight become insufficient.) |
| R4-C3 | new_grads | I cannot tell whether this role accepts new graduates or early-career applicants. | none (no quote) | insufficient (The posting lists 4+ years under good-fit criteria and leaves new-graduate acceptance unstated.) | no sentence named | insufficient |
| R4-C4 | qualification | A good fit has 4+ years of experience in technical roles such as Forward Deployed Engineer, Product Engineer, Software Engineer, or Technical Product Manager. | “4+ years of experience in technical roles such as Forward Deployed Engineer, Product Engineer, Software Engineer, or Technical Product Manager” (description; quote found) | supported | “Former technical founders are also encouraged to apply.” → insufficient (quote found) | **insufficient**, changed after the challenge (The claim drops an alternative, so it does not preserve the posting's alternatives.) |
| R4-C5 | qualification | The minimum education is a Bachelor's degree or an equivalent combination of education, training, and/or experience. | “Minimum education: Bachelor’s degree or an equivalent combination of education, training, and/or experience” (description; quote found) | supported | no sentence named | supported |
| R4-C6 | qualification | A good fit has strong programming skills with proficiency in Python or TypeScript. | “Strong programming skills with proficiency in Python or TypeScript” (description; quote found) | supported | no sentence named | supported |
| R4-C7 | work_authorization | I cannot tell what this posting says about authorization to work. | none (no quote) | insufficient (The posting describes general visa sponsorship and leaves role-specific work authorization requirements unstated.) | no sentence named | insufficient |
| R4-C8 | sponsorship | The posting says Anthropic sponsors visas but cannot successfully sponsor visas for every role and every candidate. | “We do sponsor visas! However, we aren't able to successfully sponsor visas for every role and every candidate.” (description; quote found) | supported | no sentence named | supported |

## R5 · Research Engineer, Machine Learning (RL Velocity) (greenhouse/anthropic 5198108008)

| ID | Kind | Claim | Quote (field; check) | First label (note) | Claude's challenge | Final label (note) |
| --- | --- | --- | --- | --- | --- | --- |
| R5-C1 | work | The role builds and improves the core platform underpinning how Anthropic does reinforcement learning. | “build and improve the core platform that underpins how we do RL at Anthropic” (description; quote found) | supported | no sentence named | supported |
| R5-C2 | location | The role is listed as remote-friendly with travel required, or based in San Francisco, CA, or New York City, NY. | “Remote-Friendly (Travel-Required) \| San Francisco, CA \| New York City, NY” (location; quote found) | supported | “Location-based hybrid policy: Currently, we expect all staff to be in one of our offices at least 25% of the time.” → insufficient (quote found) | **insufficient**, changed after the challenge (Every location claim leaves out the hybrid condition, so all eight become insufficient.) |
| R5-C3 | new_grads | I cannot tell whether this role accepts new graduates or early-career applicants. | none (no quote) | insufficient (The posting ties experience to internal job level and leaves new-graduate acceptance unstated.) | no sentence named | insufficient |
| R5-C4 | qualification | The minimum education is a bachelor's degree or an equivalent combination of education, training, or experience. | “Minimum education: Bachelor’s degree or an equivalent combination of education, training, and/or experience” (description; quote found) | supported | no sentence named | supported |
| R5-C5 | qualification | The posting gives no fixed number of years of experience, tying it to internal job level requirements instead. | “Years of experience required will correlate with the internal job level requirements for the position” (description; quote found) | supported | no sentence named | supported |
| R5-C6 | qualification | The posting names strong software engineering fundamentals as a sign of a good fit. | “Have strong software engineering fundamentals” (description; quote found) | supported | no sentence named | supported |
| R5-C7 | work_authorization | I cannot tell what the posting says about authorization to work. | none (no quote) | insufficient (The posting describes general visa sponsorship and leaves role-specific work authorization requirements unstated.) | no sentence named | insufficient |
| R5-C8 | sponsorship | The posting says Anthropic sponsors visas, though it cannot successfully do so for every role or every candidate. | “We do sponsor visas! However, we aren't able to successfully sponsor visas for every role and every candidate.” (description; quote found) | supported | no sentence named | supported |

## R6 · Performance Engineer, Inference Systems (greenhouse/anthropic 5224564008)

| ID | Kind | Claim | Quote (field; check) | First label (note) | Claude's challenge | Final label (note) |
| --- | --- | --- | --- | --- | --- | --- |
| R6-C1 | work | The role runs cross-layer performance investigations of Anthropic's inference systems. | “Run cross-layer performance investigations” (description; quote found) | supported | no sentence named | supported |
| R6-C2 | location | The role is located in San Francisco, CA, New York City, NY, or Seattle, WA. | “San Francisco, CA \| New York City, NY \| Seattle, WA” (location; quote found) | supported | no sentence named | **insufficient**, changed after the challenge (Every location claim leaves out the hybrid condition, so all eight become insufficient.) |
| R6-C3 | new_grads | I cannot tell whether this role accepts new graduates or early-career applicants. | none (no quote) | insufficient (The posting ties experience to internal job level and leaves new-graduate acceptance unstated.) | no sentence named | insufficient |
| R6-C4 | qualification | The years of experience required depend on the internal job level for the position. | “Years of experience required will correlate with the internal job level requirements for the position” (description; quote found) | supported | no sentence named | supported |
| R6-C5 | qualification | The minimum education is a Bachelor’s degree or an equivalent combination of education, training, or experience. | “Minimum education: Bachelor’s degree or an equivalent combination of education, training, and/or experience” (description; quote found) | supported | no sentence named | supported |
| R6-C6 | qualification | The role lists proficiency in Python as a minimum qualification. | “Proficiency in Python” (description; quote found) | supported | no sentence named | supported |
| R6-C7 | work_authorization | I cannot tell what this posting says about authorization to work. | none (no quote) | insufficient (The posting describes general visa sponsorship and leaves role-specific work authorization requirements unstated.) | no sentence named | insufficient |
| R6-C8 | sponsorship | Anthropic sponsors visas but cannot sponsor visas for every role or candidate. | “We do sponsor visas! However, we aren't able to successfully sponsor visas for every role and every candidate.” (description; quote found) | supported | no sentence named | supported |

## R7 · Machine Learning Infrastructure Engineer, Safeguards Research (greenhouse/anthropic 5364804008)

| ID | Kind | Claim | Quote (field; check) | First label (note) | Claude's challenge | Final label (note) |
| --- | --- | --- | --- | --- | --- | --- |
| R7-C1 | work | The role builds infrastructure for Safeguards machine learning research. | “Build and scale the infrastructure and data pipelines behind Safeguards machine learning research” (description; quote found) | supported | no sentence named | supported |
| R7-C2 | location | The role is located in San Francisco, CA or New York City, NY. | “San Francisco, CA \| New York City, NY” (location; quote found) | supported | “Currently, we expect all staff to be in one of our offices at least 25% of the time.” → insufficient (quote found) | **insufficient**, changed after the challenge (Every location claim leaves out the hybrid condition, so all eight become insufficient.) |
| R7-C3 | new_grads | I cannot tell whether this role accepts new graduates or early-career applicants. | none (no quote) | insufficient (The posting ties experience to internal job level and leaves new-graduate acceptance unstated.) | no sentence named | insufficient |
| R7-C4 | qualification | The minimum years of experience depend on the internal job level for the position. | “Years of experience required will correlate with the internal job level requirements for the position” (description; quote found) | supported | no sentence named | supported |
| R7-C5 | qualification | The minimum education is a Bachelor's degree or an equivalent combination of education, training, or experience. | “Bachelor’s degree or an equivalent combination of education, training, and/or experience” (description; quote found) | supported | no sentence named | supported |
| R7-C6 | qualification | Proficiency in Python is listed as a minimum qualification. | “proficiency in Python” (description; quote found) | supported | no sentence named | supported |
| R7-C7 | work_authorization | I cannot tell what this posting says about authorization to work. | none (no quote) | insufficient (The posting describes general visa sponsorship and leaves role-specific work authorization requirements unstated.) | “But if we make you an offer, we will make every reasonable effort to get you a visa, and we retain an immigration lawyer to help with this.” → contradicted (quote found) | insufficient (unchanged) |
| R7-C8 | sponsorship | The posting says Anthropic sponsors visas, though it cannot successfully sponsor every role or candidate. | “We do sponsor visas! However, we aren't able to successfully sponsor visas for every role and every candidate.” (description; quote found) | supported | no sentence named | supported |

## R8 · Applied AI, Research Engineer (greenhouse/anthropic 5390811008)

| ID | Kind | Claim | Quote (field; check) | First label (note) | Claude's challenge | Final label (note) |
| --- | --- | --- | --- | --- | --- | --- |
| R8-C1 | work | The role owns the technical-to-go-to-market handoff for model launches. | “Own the technical < > GTM handshake for model and product launches” (description; quote found) | supported | no sentence named | supported |
| R8-C2 | location | The role is located in San Francisco, CA or New York City, NY. | “San Francisco, CA \| New York City, NY” (location; quote found) | supported | no sentence named | **insufficient**, changed after the challenge (Every location claim leaves out the hybrid condition, so all eight become insufficient.) |
| R8-C3 | new_grads | I cannot tell whether this role accepts new graduates or early-career applicants. | none (no quote) | insufficient (The posting lists 6+ years under good-fit criteria and leaves new-graduate acceptance unstated.) | no sentence named | insufficient |
| R8-C4 | qualification | The posting lists 6+ years of experience as a Software Engineer, Technical Product Manager, Forward Deployed Engineer, AI startup founder, or similar technical role as a sign of good fit. | “6+ years of experience as a Software Engineer, Technical Product Manager, Forward Deployed Engineer, AI startup founder, or similar technical role” (description; quote found) | supported | no sentence named | supported |
| R8-C5 | qualification | The minimum education is a Bachelor’s degree or an equivalent combination of education, training, or experience. | “Minimum education: Bachelor’s degree or an equivalent combination of education, training, and/or experience” (description; quote found) | supported | no sentence named | supported |
| R8-C6 | qualification | The posting lists meaningful experience building with large language models as a sign of good fit. | “Meaningful experience building with large language models” (description; quote found) | supported | no sentence named | supported |
| R8-C7 | work_authorization | I cannot tell what this posting requires regarding authorization to work. | none (no quote) | insufficient (The posting describes general visa sponsorship and leaves role-specific work authorization requirements unstated.) | no sentence named | insufficient |
| R8-C8 | sponsorship | The posting says Anthropic sponsors visas, though not for every role or candidate. | “We do sponsor visas! However, we aren't able to successfully sponsor visas for every role and every candidate.” (description; quote found) | supported | no sentence named | supported |
