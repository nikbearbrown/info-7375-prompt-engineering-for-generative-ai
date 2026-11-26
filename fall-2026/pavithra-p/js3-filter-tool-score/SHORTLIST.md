# The source-grounded shortlist (Chapter 7)

## How it was made

* Filter v1.1 kept 15 of the 589 postings. The shortlist is the 8 with the highest score, with ties in collection order (`agent/shortlist.py`, `SHORTLIST_SIZE = 8`). I capped it at 8 so that I could label every claim myself. The other 7 kept postings (scores 4 and 5, listed in `runs/20261125T204144Z/filter-v1.1/summary.md`) have no justification and no claim labels, so nothing in this file covers them.
* For each of the 8, Claude wrote a justification: 4 or 5 claims, exactly one each about role, experience and location, and one or two about skills. Each claim comes with a quote copied from the posting (`prompts/justify-v1.txt`).
* Real calls: `python3 -m agent shortlist`, on 2026-11-25 between 21:09:14 and 21:10:53 UTC. Claude Code 2.1.294 in print mode, model `claude-opus-5-5`.
  * It had no tools at all (`--tools ""`) and no MCP servers, and ran from an empty folder.
  * Each reply was saved before parsing, in `runs/20261125T204144Z/shortlist-v1.1/claude/`.
  * All 8 replies were valid; none needed or got any fixing.
* Labels:
  1. The checker in `agent/evidence.py` gave every claim a first label (FILTER.md section 4).
  2. Then I labelled all 37 claims myself, against the posting's own text. My labels are in `audit/claim-labels.csv`, with the checker's next to them; I typed them as a numbered list.
  3. My label is the one that counts.

The rule I followed: a claim is supported only if its own quote says everything the claim says about the posting. If the claim adds a detail its quote does not contain, it is insufficient, even when the detail is true somewhere else in the posting.

## Results

| | Claims |
|---|---|
| Supported (mine) | 19 |
| Insufficient (mine) | 18 |
| Contradicted (mine) | 0 |
| The checker agreed with me | 19 of 37 |
| The checker said supported (quote found) and I agreed | 17 of 32 |

The 15 claims where the quote was really in the posting but I said insufficient are the gap between finding a quote and proving a claim. The checker can only do the first.

Five labels changed after review. First, after a consistency check, #29 and #32 (Figma, Software Engineer - C++). I had marked them supported. On review, both add a detail their quote does not say:
* #29 says the fit is "mostly through its TypeScript and API work", but its quote mentions Javascript, not TypeScript or APIs;
* #32 says the role "centers on" C++ and WebAssembly, but its quote does not mention WebAssembly.

By my own rule both are insufficient, and I changed them (the `changed_after_review` column).

Then, after a second review, three more that break the same rule, which I first marked supported and changed to insufficient:
* #6 calls the role "new-grad", which comes from the title, not its quote;
* #8 says the role is "listed as Remote, US as well as San Francisco", which its quote does not say;
* #14 names "Spotify's Data Infrastructure team", from the title.

No abstention result changed.

## Relevance is not entailment: Ramp, Software Engineer, Android

The filter kept this posting with score 6: the title has "Software Engineer", and the text names TypeScript, Python and SQL, three of Rohan's skills. By my words it is relevant. But the posting does not support the claim that it fits Rohan's backend search:
* the role claim (#19, supported) quotes "As an Android Engineer at Ramp, you'll enhance our successful and rapidly growing mobile app";
* the experience claim (#20, supported) quotes "Minimum 1 year of experience in mobile development", which Rohan does not have;
* Python and SQL appear only in a nice-to-have line, "Experience with backend technologies (Python, Flask, SQL, OpenAPI)". The skills claim built on it (#23) also says the role requires Kotlin and Compose, which that quote does not say, so I labelled it insufficient.

The words matched. What the posting asks for is mobile work.

## The abstention rule, and a counterexample

The rule (FILTER.md section 4): a shortlisted posting gets "I cannot tell if this fits" instead of a recommendation if any claim about role, experience or location is not supported, or is missing.

On my labels it abstains on 7 of the 8. Most of these are not bad postings; Claude's claims added details their quotes did not cover. Only one posting passes the rule, and that is Android.

The counterexample is Android itself. Its role, experience and location claims are all supported, so the rule lets it through as "recommended to read". But those supported claims say it is mobile work that needs mobile experience Rohan does not have. The rule checks whether each claim is backed by the posting; it does not check whether the claim is in Rohan's favour. A justification that honestly says "this is a weak fit" passes, because it is well supported.

A second limit: the rule only sees the claims Claude chose to make. If Claude had left out the experience claim, the rule would abstain for the missing claim, but it cannot know which important fact was left out.

I did not change the rule. A fix would need each claim to say whether it is for or against the fit, which would be a change to the prompt and the reply format. That is listed in `SIGNOFF.md`.

## What the checker got wrong

* It marked #15 (Spotify, experience) contradicted, because the posting asks for 3+ years. But the claim itself says the posting asks for 3+ years and Rohan falls short, and the quote says exactly that, so I labelled it supported. The checker compared the posting with Rohan; it should compare the claim with the posting. Fixed after my labels: an experience claim that itself states the years or the seniority the posting asks for is no longer marked contradicted by them (`agent/evidence.py`, `test_experience_claim_that_states_the_years_is_not_contradicted`). Re-run on the saved claims (no new Claude call), the fixed checker agrees with my labels on 20 of 37 instead of 19. #15 now matches me, and #30 (Figma C++) moves from contradicted to "supported, check by hand", where I said insufficient. The tables below show the checker's labels as they were when the shortlist ran.
* It marked #37 (Support Engineer, skills) insufficient, because the quote names none of the résumé's skill words. The claim is about owning production software, and the quote says that.

The #37 case is not fixed: the skills rule still asks for a résumé skill word in the quote. More generally, the checker matches text and numbers: it can prove a quote is missing and see a few contradictions, but it cannot tell whether a quote means what the claim says. That is why every "supported" it gives is marked for a hand check, and why its labels are a first pass and never the final word.

Note: in four of the iOS claims (#24, #25, #27, #28) Claude refers to the candidate as "he" and "his". The claims are shown exactly as Claude wrote them.

## Every claim

The tables below are generated by `python3 scripts/shortlist_table.py` from the saved replies and `audit/claim-labels.csv`.

### 1. Software Engineer, Forward Deployed, AI Solutions (`ashby:ramp:b614563f-3ce6-4dca-b5ba-0e5a6c8bda27`, score 7)

Claude asked 2026-11-25T21:09:14Z. Abstention rule on my labels: I cannot tell if this fits.

| # | About | Claude's claim | Claude's quote | Checker | Mine |
|---|---|---|---|---|---|
| 1 | role | This is a client-facing forward deployed software engineering role: building production AI agents, automations, and integrations for customers and turning them into reusable platform capabilities. It is adjacent to backend/platform work but leans heavily toward customer engagement, and it requires travel of up to about 50%. | This is a deeply client-facing, hands-on building role based in New York, with occasional travel depending on engagements. | supported | insufficient |
| 2 | experience | The posting does not state a required number of years, so about two years is not ruled out. However, it requires hands-on experience building LLM systems (agents, RAG, evals), which the candidate's profile does not show. This is a real gap. | Hands-on experience building LLM systems — agents, RAG, evals, and monitoring — and sound judgment on trade-offs like quality, latency, cost, and model choice. | supported | insufficient |
| 3 | location | The role is based in New York HQ, not Boston, so the candidate would need to relocate within the US. Ramp offers relocation expense coverage to NYC. | Relocation expense coverage to NYC or SF (if needed) | supported | insufficient |
| 4 | skills | The posting asks for strong coding in Python, TypeScript/JavaScript, or Java, and the candidate has all three. | Strong coding ability in Python, TypeScript/JavaScript, Java, Go, or similar. | supported | supported |
| 5 | skills | The posting asks for comfort with APIs, integrations, data pipelines, and AWS cloud infrastructure. This matches the candidate's experience with AWS, Kafka, Node.js services, Kubernetes, and Docker. | Comfort working across APIs, integrations, data pipelines, and cloud infrastructure (AWS, GCP, or Azure), and designing systems that are secure and scale. | supported | supported |

### 2. University Grad Software Engineer 2027 (USA) (`greenhouse:pinterest:7838591`, score 6)

Claude asked 2026-11-25T21:09:34Z. Abstention rule on my labels: I cannot tell if this fits.

| # | About | Claude's claim | Claude's quote | Checker | Mine |
|---|---|---|---|---|---|
| 6 | role | This is a new-grad software engineering role, and depending on the team the work can include backend and full-stack engineering, which matches the candidate's target of backend, platform or full-stack roles. | Contribute to engineering work across backend, full stack, mobile, web, and security domains, depending on team | supported | insufficient (changed, see below) |
| 7 | experience | The posting asks for at least one year of programming experience, so the candidate's two years as a software engineer plus a co-op meets it. The role is aimed at university grads, though, so it may sit below the candidate's level. | At least one year of programming experience through internships, research, coursework, teaching, personal projects, open source, or hackathons | supported | insufficient |
| 8 | location | The role is listed as Remote, US as well as San Francisco, so the candidate could likely work from Boston if Massachusetts is an approved remote location. That would be confirmed during the offer process. | some will work fully remote within approved locations. | supported | insufficient (changed, see below) |
| 9 | skills | The posting names Python, Java and TypeScript as example languages, and the candidate has all three. | Experience with one or more programming languages such as Python, Java, JavaScript/TypeScript, Go, or C++ | supported | supported |

### 3. Software Engineer - Full Stack (`greenhouse:figma:5691911004`, score 6)

Claude asked 2026-11-25T21:09:45Z. Abstention rule on my labels: I cannot tell if this fits.

| # | About | Claude's claim | Claude's quote | Checker | Mine |
|---|---|---|---|---|---|
| 10 | role | This is a full-stack software engineering role spanning front-end features and scalable back-end systems, which matches the candidate's interest in backend and full-stack work. | Design, build, and ship high-quality features across the stack, from polished front-end experiences to scalable back-end systems | supported | supported |
| 11 | experience | The posting gives no minimum years of experience and covers openings at several seniority levels, so about two years of experience plausibly fits one of the levels. | This opportunity applies to openings at varying seniority levels across our teams | supported | insufficient |
| 12 | location | The role can be done remotely anywhere in the US, so the candidate can work from Boston. Onboarding must be attended in person. | This is a full-time role that can be held from one of our US hubs or remotely in the United States. | supported | insufficient |
| 13 | skills | The posting asks for TypeScript, Python and PostgreSQL, and the candidate has all three. React is also listed, and the candidate's summary does not mention it. | Strong proficiency in modern front-end frameworks (e.g., React/TypeScript) and back-end technologies (e.g., Ruby, Python, Go, C++, PostgreSQL) | supported | supported |

### 4. Backend Engineer - Data Infrastructure (`lever:spotify:ced2c220-6b5c-4e74-8e06-37d50985097c`, score 6)

Claude asked 2026-11-25T21:10:00Z. Abstention rule on my labels: I cannot tell if this fits.

| # | About | Claude's claim | Claude's quote | Checker | Mine |
|---|---|---|---|---|---|
| 14 | role | This is a backend and platform engineering role on Spotify's Data Infrastructure team. The work is building Java services, libraries and data ingestion pipelines, which fits the candidate's goal of backend or platform work. | Build, maintain, and improve Java backend services, libraries, and data ingestion pipelines that power Spotify's analytics platform. | supported | insufficient (changed, see below) |
| 15 | experience | The posting asks for 3+ years, and the candidate has about two and a half years (two years full-time plus a five-month co-op). That falls short of the stated minimum, so this is a stretch application, though the backend focus of that experience matches. | You have 3+ years of experience developing backend services or working with distributed data systems. | contradicted | supported |
| 16 | location | The role is based in New York, not Boston, so the candidate would need to relocate or commute for in-person meetings. Some work-from-home flexibility is offered, and the role is US-based, which suits the candidate's search. | This role is based in New York, NY | supported | insufficient |
| 17 | skills | The posting requires Java backend programming, and the candidate has about two years building Java services for a retail bank. | You're comfortable programming in Java and enjoy building reliable, maintainable backend applications. | supported | supported |
| 18 | skills | The posting names Kubernetes and AWS as infrastructure technologies, and both are on the candidate's skill list, along with related tools such as Docker and Helm. | You've worked with, or are interested in learning, infrastructure technologies such as Kubernetes, Terraform, and cloud platforms like Google Cloud Platform or AWS. | supported | supported |

### 5. Software Engineer, Android (`ashby:ramp:f564dcf9-9390-4a3f-896f-8047a5086040`, score 6)

Claude asked 2026-11-25T21:10:14Z. Abstention rule on my labels: recommended to read.

| # | About | Claude's claim | Claude's quote | Checker | Mine |
|---|---|---|---|---|---|
| 19 | role | This is an Android mobile engineering role building features for Ramp's Android app. It is not the backend, platform or full-stack work the candidate is targeting, so it is a weak fit on role type. | As an Android Engineer at Ramp, you’ll enhance our successful and rapidly growing mobile app. | supported | supported |
| 20 | experience | A one-year minimum fits within about two years of total experience. However, the year must be in mobile development, and the candidate's experience is in Java backend services and TypeScript/SQL, with no stated mobile work, so the requirement is likely not met. | Minimum 1 year of experience in mobile development | supported | supported |
| 21 | location | The role is open to remote work in the US, so the Boston-based candidate can work from where they are. | Remote (US) (USA) | supported | supported |
| 22 | skills | The candidate's TypeScript matches a listed nice-to-have for web app experience. | Experience with web apps (React, TypeScript) | supported | supported |
| 23 | skills | The candidate's Python and SQL match the backend nice-to-haves. These are optional extras, though, and the candidate lacks the required Kotlin and Compose. | Experience with backend technologies (Python, Flask, SQL, OpenAPI) | supported | insufficient |

### 6. Software Engineer, iOS (`ashby:ramp:4859cd5e-f2a9-44d7-81f7-8bfc0e62369f`, score 6)

Claude asked 2026-11-25T21:10:26Z. Abstention rule on my labels: I cannot tell if this fits.

| # | About | Claude's claim | Claude's quote | Checker | Mine |
|---|---|---|---|---|---|
| 24 | role | This is a mobile iOS engineering role building Ramp's iOS app, not the backend, platform or full-stack work the candidate is looking for. That is a significant mismatch with his target roles. | As an iOS Engineer at Ramp, you’ll enhance our successful and rapidly growing mobile app. | supported | supported |
| 25 | experience | The posting asks for only one year of experience, which his two years would meet. But it must be mobile development, and the candidate has none, so his experience does not fit the requirement. | Minimum 1 year of experience in mobile development. | supported | supported |
| 26 | location | The role is open to remote work anywhere in the US, so the candidate can work from Boston without relocating. | Location: New York, NY (HQ); Remote (Canada); San Francisco, CA; Remote (US) (USA) | insufficient | insufficient |
| 27 | skills | The candidate has the backend skills the posting lists as a nice-to-have, namely Python and SQL. These are optional extras, though; the required skills are Swift and SwiftUI, which he lacks. | Experience with backend technologies (Python, Flask, SQL, OpenAPI). | supported | insufficient |
| 28 | skills | The candidate's TypeScript matches the web-app nice-to-have. He has no listed React experience, and this skill is also optional rather than core to the role. | Experience with web apps (React, TypeScript). | supported | supported |

### 7. Software Engineer - C++ (`greenhouse:figma:5552530004`, score 5)

Claude asked 2026-11-25T21:10:38Z. Abstention rule on my labels: I cannot tell if this fits.

| # | About | Claude's claim | Claude's quote | Checker | Mine |
|---|---|---|---|---|---|
| 29 | role | This is a client-side/frontend infrastructure role building C++/WebAssembly systems and multiplayer protocols in the browser. It is not the backend or platform-services work the candidate mainly targets, so it is at best a partial fit, mostly through its TypeScript and API work. | You will be developing high-performance client-side systems in C++/WebAssembly, extending the multiplayer protocols that make collaborative design possible, and building out the communications layer between C++ and Javascript. | supported | insufficient (changed, see below) |
| 30 | experience | The posting asks for 4+ years of professional experience, so the candidate's roughly two years plus a co-op does not meet the stated bar. Figma does say it encourages applicants whose experience doesn't align perfectly. | 4+ years of professional Software Engineering experience shipping user-facing features or products | contradicted | insufficient |
| 31 | location | The role can be done remotely anywhere in the United States, so the candidate can hold it from Boston. | This is a full-time role that can be held from one of our US hubs or remotely in the United States. | supported | supported |
| 32 | skills | The posting accepts strong skills in TypeScript or Python, and the candidate has both. The candidate lacks the C++ and WebAssembly that the role centers on. | Strong programming skills in one or more languages relevant to our frontend such as TypeScript, C++, React, Go, Rust, or Python | supported | insufficient (changed, see below) |

### 8. Support Engineer, AI Infrastructure & Tooling (`greenhouse:figma:5802956004`, score 5)

Claude asked 2026-11-25T21:10:53Z. Abstention rule on my labels: I cannot tell if this fits.

| # | About | Claude's claim | Claude's quote | Checker | Mine |
|---|---|---|---|---|---|
| 33 | role | Despite the 'Support Engineer' title, this is a hands-on software engineering role building backend integrations and automated actions for AI support agents. That fits the candidate's backend and integration work, though the AI-agent focus is new territory for them. | combining applied AI engineering with strong software development to connect conversational systems to the context, tools, and backend capabilities they need to act. | supported | supported |
| 34 | experience | The posting gives no number of years, so it is unclear whether about two years fits. The $169,000–$245,000 salary range and the requirement for production AI-agent experience suggest a mid-to-senior level the candidate may not fully meet. | (none) | insufficient | insufficient |
| 35 | location | The role can be held remotely anywhere in the US, so the candidate can work from Boston (in-person onboarding is required). | This is a full-time role that can be held from one of our US hubs or remotely in the United States. | supported | insufficient |
| 36 | skills | The posting asks for strong programming in Python or TypeScript, and the candidate has both. | Strong programming skills in Python, TypeScript, or a comparable language | supported | supported |
| 37 | skills | The posting asks for ownership of production software through ongoing operation, which matches the candidate's two years running Java services for a bank plus Kubernetes, Jenkins and Fluent Bit operations experience. | owning production software from implementation through ongoing operation. | insufficient | supported |

