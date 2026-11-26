# Reject audit — JS3 filter v1

**Source:** the saved November 10, 2026 JS2 snapshot; 215 postings from three boards. **Review:** I checked all 47 entries in `runs/js3/filter_v1/REVIEW_DRAFT.csv` against the saved postings on November 25, 2026 ET. I accepted the proposed verdicts, reasons, and excerpts into `LABEL_SHEET.csv` without changes. The sample keys and split were saved before I reviewed the entries.

## What the review found

| Group | Reviewed | Filter disagreements | What it covers |
|---|---:|---:|---|
| Random rejects | 30 | 0 | Drawn from 211 rejected postings with seed `js3-reject-audit-2026-11-25`. |
| Closest calls | 15 | 0 | All postings meeting FILTER.md’s closest-call definition; two also appear in the random sample. |
| Kept | 4 | 2 | Every kept posting in this snapshot. |

The random review found 0 wrongly rejected postings among 30 sampled rejects. The script’s approximate 95% Wilson interval is 0%–11.4% for the share among the 211 rejects in this one snapshot, assuming the verdicts are correct. This is a sample estimate, not a measured error rate for all rejects, all 215 postings, or future boards. Zero observed errors does not prove there are no missed jobs. The kept result is a complete review of the four kept postings in this snapshot.

## Randomly sampled rejects

- **A03 — Executive Assistant to the CEO** (`duolingo/8602840002`): filter `hard_rule_reject`, reviewed `not_relevant`. Executive-assistant role, not a target engineering role; listed for New York/Pittsburgh. Source `title`: “Executive Assistant to the CEO”
- **A04 — Senior Director of Engineering, New Subjects** (`duolingo/8584465002`): filter `hard_rule_reject`, reviewed `not_relevant`. Senior director of engineering is a leadership role in New York, not an early-career Boston/remote role. Source `title`: “Senior Director of Engineering, New Subjects”
- **A05 — Senior Lead Technical Program Manager - Infrastructure** (`klaviyo/7855726003`): filter `hard_rule_reject`, reviewed `not_relevant`. Senior lead technical program manager is a management role, not a target engineering position. Source `title`: “Senior Lead Technical Program Manager - Infrastructure”
- **A06 — Partner Account Manager** (`klaviyo/8005686003`): filter `hard_rule_reject`, reviewed `not_relevant`. Partner account manager is not an engineering role; platform describes partner education about the product. Source `description`: “introduce and educate agency partners on new enhancements to Klaviyo’s platform”
- **A08 — Head of Talent Management Programs and PMO** (`duolingo/8590178002`): filter `hard_rule_reject`, reviewed `not_relevant`. Head of talent-management programs is a people-program leadership role in Pittsburgh. Source `title`: “Head of Talent Management Programs and PMO”
- **A09 — Senior Software Engineer - Growth** (`klaviyo/7696724003`): filter `hard_rule_reject`, reviewed `not_relevant`. Senior growth engineer owns product-experience strategy, above the target seniority and outside the backend/platform emphasis. Source `title`: “Senior Software Engineer - Growth”
- **A10 — Principal Tech Partner Manager II** (`klaviyo/8042236003`): filter `hard_rule_reject`, reviewed `not_relevant`. Principal tech-partner manager is a partner-management role, not target engineering. Source `title`: “Principal Tech Partner Manager II”
- **A11 — Senior/Software Engineer II, Android** (`duolingo/8628658002`): filter `hard_rule_reject`, reviewed `not_relevant`. Android mobile role in New York/Pittsburgh; mobile is expressly outside the persona target. Source `title`: “Senior/Software Engineer II, Android”
- **A14 — Proctor Quality and Learning Manager, Scaling Operations** (`duolingo/8858331002`): filter `hard_rule_reject`, reviewed `not_relevant`. Proctor-quality and learning manager is an operations-management role, not target engineering. Source `title`: “Proctor Quality and Learning Manager, Scaling Operations”
- **A15 — Sr. AI Systems & Solutions Architect, Customer Success** (`klaviyo/7859208003`): filter `hard_rule_reject`, reviewed `not_relevant`. Customer-success solutions architect in Denver is outside the target role and geography. Source `title`: “Sr. AI Systems & Solutions Architect, Customer Success”
- **A16 — Account Executive, Large Enterprise** (`klaviyo/8013137003`): filter `hard_rule_reject`, reviewed `not_relevant`. Large-enterprise account executive is a sales role, not engineering. Source `title`: “Account Executive, Large Enterprise”
- **A17 — Senior Security Engineer - Detection & Response** (`klaviyo/7994067003`): filter `hard_rule_reject`, reviewed `not_relevant`. Senior detection-and-response security role in London, outside target role, seniority, and geography. Source `title`: “Senior Security Engineer - Detection & Response”
- **A18 — Large Enterprise Sales Manager** (`klaviyo/8009591003`): filter `hard_rule_reject`, reviewed `not_relevant`. Large-enterprise sales manager in Denver is outside target role and geography. Source `title`: “Large Enterprise Sales Manager”
- **A20 — Commercial Account Executive** (`klaviyo/7577984003`): filter `hard_rule_reject`, reviewed `not_relevant`. Commercial account executive is a sales role, despite the Boston location. Source `title`: “Commercial Account Executive”
- **A21 — Senior Product Manager, Growth** (`duolingo/8747171002`): filter `hard_rule_reject`, reviewed `not_relevant`. Senior product manager in New York/Pittsburgh is outside target role and geography. Source `title`: “Senior Product Manager, Growth”
- **A23 — Large Enterprise, Account Executive** (`klaviyo/8019632003`): filter `hard_rule_reject`, reviewed `not_relevant`. Large-enterprise account executive is a sales role in Munich. Source `title`: “Large Enterprise, Account Executive”
- **A26 — Product Designer, Thrive Intern** (`duolingo/8933791002`): filter `hard_rule_reject`, reviewed `not_relevant`. Product-designer internship in Pittsburgh is neither a target engineering role nor target geography. Source `title`: “Product Designer, Thrive Intern”
- **A27 — Lead Security Compliance Engineer** (`klaviyo/8000325003`): filter `hard_rule_reject`, reviewed `not_relevant`. Lead security-compliance engineer in Denver is outside target role, seniority, and geography. Source `title`: “Lead Security Compliance Engineer”
- **A28 — Account Executive, SMB - Eastern Europe (Polish)** (`klaviyo/8177509003`): filter `hard_rule_reject`, reviewed `not_relevant`. SMB account executive in Dublin is a sales role outside target geography. Source `title`: “Account Executive, SMB - Eastern Europe (Polish)”
- **A29 — Head of Global Compensation** (`klaviyo/7984272003`): filter `hard_rule_reject`, reviewed `not_relevant`. Head of global compensation is a compensation-leadership role, not engineering. Source `title`: “Head of Global Compensation”
- **A30 — Commercial Account Executive-ANZ** (`klaviyo/8178371003`): filter `hard_rule_reject`, reviewed `not_relevant`. Commercial account executive in Sydney is a sales role; platform is used as a career-growth metaphor. Source `description`: “Klaviyo provides a great platform to do so”
- **A32 — Principal Engineer, Enterprise Scalability (Remote - East Coast Only)** (`klaviyo/8179354003`): filter `hard_rule_reject`, reviewed `not_relevant`. Principal scalability engineer asks for 12+ years; Boston residents are not covered by its remote exception. Source `description`: “12+ years of relevant engineering experience”
- **A34 — Principal Engineer, Enterprise Scalability** (`klaviyo/8179279003`): filter `hard_rule_reject`, reviewed `not_relevant`. Principal scalability engineer asks for 12+ years, far beyond the persona. Source `description`: “12+ years of relevant engineering experience”
- **A35 — Managing Editor** (`duolingo/8637185002`): filter `hard_rule_reject`, reviewed `not_relevant`. Managing editor in Tokyo is not a target engineering role or location. Source `title`: “Managing Editor”
- **A36 — Senior Software Engineer - Data Automation** (`klaviyo/8012938003`): filter `hard_rule_reject`, reviewed `not_relevant`. Senior data-automation engineer asks for 7+ years, beyond the persona. Source `description`: “7+ years of experience in a software engineering discipline”
- **A37 — Customer Success Operations Analyst** (`klaviyo/8182739003`): filter `hard_rule_reject`, reviewed `not_relevant`. Customer-success operations analyst is not a target engineering role. Source `title`: “Customer Success Operations Analyst”
- **A39 — Global Mobility and Immigration Program Lead** (`klaviyo/8037134003`): filter `hard_rule_reject`, reviewed `not_relevant`. Global mobility and immigration program lead is a people-program role, not software engineering. Source `title`: “Global Mobility and Immigration Program Lead”
- **A43 — Head of Global Compensation** (`klaviyo/8034565003`): filter `hard_rule_reject`, reviewed `not_relevant`. Head of global compensation in Denver is not a target engineering role or location. Source `title`: “Head of Global Compensation”
- **A46 — Senior Internal IT Auditor** (`klaviyo/8037178003`): filter `hard_rule_reject`, reviewed `not_relevant`. Senior internal IT auditor in San Francisco is not a target engineering role or location. Source `title`: “Senior Internal IT Auditor”
- **A47 — Senior Creative, Social** (`duolingo/8810661002`): filter `hard_rule_reject`, reviewed `not_relevant`. Senior creative/social role in New York/Pittsburgh is unrelated to engineering. Source `title`: “Senior Creative, Social”

## Closest calls

- **A01 — Senior Software Engineer, Platform Engineering**: score 7, failed rules R2, filter `hard_rule_reject`, reviewed `not_relevant`. Senior platform role asks for 5+ years operating distributed systems; the persona has two.
- **A02 — Senior Software Engineer, Applied AI (Customer Agent)**: score 6, failed rules R2, filter `hard_rule_reject`, reviewed `not_relevant`. Senior applied-AI role asks for 7+ years of software engineering experience.
- **A09 — Senior Software Engineer - Growth**: score 7, failed rules R2, filter `hard_rule_reject`, reviewed `not_relevant`. Senior growth engineer owns product-experience strategy, above the target seniority and outside the backend/platform emphasis.
- **A13 — Software Engineer II - SMS International**: score 7, failed rules R4, filter `hard_rule_reject`, reviewed `not_relevant`. The posting is in London, with no explicit Boston or remote arrangement for this role.
- **A19 — Senior Software Engineer - Infrastructure Security**: score 7, failed rules R2, filter `hard_rule_reject`, reviewed `not_relevant`. Senior infrastructure-security engineer asks for 6+ years of operating cloud-native systems.
- **A22 — Software Engineer II (Mobile Developer - Android/Kotlin) - Remote**: score 7, failed rules R3, filter `hard_rule_reject`, reviewed `not_relevant`. The role primarily owns an Android SDK; mobile work is outside the persona target despite its remote arrangement and 1–3 year requirement.
- **A24 — Senior Software Engineer - Profiles, Lists and Segments**: score 7, failed rules R2, filter `hard_rule_reject`, reviewed `not_relevant`. Senior full-stack role asks for 5+ years and emphasizes React/Redux frontend skills.
- **A25 — Sr. Lead Software Engineer**: score 7, failed rules R2, filter `hard_rule_reject`, reviewed `not_relevant`. Sr. lead software engineer asks for 8+ years and backend leadership.
- **A31 — Full Stack Software Engineer - People Systems**: score 5, failed rules none, filter `below_threshold`, reviewed `not_relevant`. The title says software engineer, but the body seeks a lead People Technology engineer with 5+ years of engineering experience.
- **A33 — Senior Lead Software Engineer - Data Platform**: score 6, failed rules R2, filter `hard_rule_reject`, reviewed `not_relevant`. Senior lead data-platform engineer asks for 12+ years, far beyond the persona.
- **A36 — Senior Software Engineer - Data Automation**: score 7, failed rules R2, filter `hard_rule_reject`, reviewed `not_relevant`. Senior data-automation engineer asks for 7+ years, beyond the persona.
- **A40 — Senior Software Engineer - Identity and Access Management**: score 7, failed rules R2, filter `hard_rule_reject`, reviewed `not_relevant`. Senior identity-and-access engineer asks for 7+ years of production-software experience.
- **A42 — Senior Machine Learning Platform Engineer**: score 8, failed rules R2, filter `hard_rule_reject`, reviewed `not_relevant`. Senior ML-platform engineer asks for 7+ years; the machine-learning specialization is also beyond the target.
- **A44 — Senior Software Engineer, Applied AI (Customer Agent)**: score 6, failed rules R2, filter `hard_rule_reject`, reviewed `not_relevant`. Senior applied-AI engineer asks for 7+ years, beyond the persona.
- **A45 — Lead Software Engineer, CICD**: score 7, failed rules R2, filter `hard_rule_reject`, reviewed `not_relevant`. Lead CI/CD engineer asks for 7+ years and technical leadership.

## Kept postings

- **A07 — Software Engineer, Conversational Products & Agent Workflows** (`klaviyo/8041054003`): score 7, reviewed `relevant`. Boston software-engineering role builds backend APIs and agent workflows with matching Python and distributed-system skills; 3+ years makes it a stretch, worth review. Source: “Build and improve reliable backend systems and APIs that power AI-driven customer experiences.”
- **A12 — Software Engineer II, Test Frameworks & Tooling** (`klaviyo/7855793003`): score 7, reviewed `relevant`. Boston software-engineering role builds test frameworks and CI/CD tooling, with a 2+ years requirement matching the persona; worth review. Source: “You have 2+ years of software engineering experience with a focus on writing clean, maintainable code.”
- **A38 — Software Engineer, AI** (`patchmypc/a71b827b-c926-4966-9207-dcc4dff7719a`): score 7, reviewed `not_relevant`. AI software-engineering role requires 5+ years of C#/.NET development; it also explicitly disallows visa sponsorship. Source: “5+ years of professional software development with C# and the .NET ecosystem”
- **A41 — Software Engineer, Backend** (`patchmypc/21f4037e-2b38-4f87-8877-fd4096d36e7f`): score 7, reviewed `not_relevant`. Backend engineer is topical, but asks for 5+ years of C# development and explicitly disallows visa sponsorship. Source: “5+ years of professional development experience in C#”

## False friends and rule decisions

- **`platform` in A06:** the Partner Account Manager posting says “introduce and educate agency partners on new enhancements to Klaviyo’s platform.” The word names the company product, not platform-engineering work in this role. R5 matched it, while R1 and other gates still rejected the posting.
- **`platform` in A30:** the Commercial Account Executive posting says “Klaviyo provides a great platform to do so.” Here the word is a career-growth metaphor. R5 matched it, while the role and location gates rejected the posting.
- **Cut `platform` from R5 — considered, not adopted:** on the full 215-posting snapshot it changed 78 scores and no keep/reject fates. On the 11 development and 11 held-out labels it changed no verdicts or agreement. The two false-friend examples show why the word needs scrutiny, but this change did not fix the two wrongly kept roles.
- **Lower threshold from 6 to 5 — considered, not adopted:** it would promote only A31 on this snapshot. A31 was reviewed `not_relevant` because its body asks for a lead People Technology engineer with 5+ years. Agreement was unchanged on development and held-out because A31 was in neither set.

No additional rule was added in this audit. The two kept errors point to experience requirements as a possible future rule, but that candidate was not part of the predeclared held-out comparison and is not claimed as tested here.

