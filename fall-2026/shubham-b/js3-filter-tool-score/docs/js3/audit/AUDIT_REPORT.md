# Reject audit — results

Hand verdicts by **Shubham Bagwe** on 2026-11-25 (`experiments/js3/audit/hand_verdicts.json`), made on the blind worksheet. This report is generated from them by `uv run python -m job_search_agent.js3 audit-report`; the numbers are recomputable.

## FILTER v0.1

| Stratum | n | Filter wrong | Filter right | Cannot tell |
|---|---:|---:|---:|---:|
| random_rejects | 40 | 0 | 40 | 0 |
| close_rejected | 8 | 4 | 4 | 0 |
| close_kept | 8 | 5 | 2 | 1 |
| random_kept | 12 | 10 | 0 | 2 |
| changed_or_contested | 14 | 14 | 0 | 0 |

**Random rejects (v0.1).** I judged 0 of 40 decided postings relevant (missed by the filter); exact 95% interval for the share of all 1170 v0.1 rejects that are relevant: 0.0% to 8.8%, which is roughly 0 to 103 postings, against 65 kept. Counting every `CANNOT_TELL` as a miss: 0 of 40, interval 0.0% to 8.8%. This is an estimate from 40 postings, not a measured rate.

## FILTER v0.3

| Stratum | n | Filter wrong | Filter right | Cannot tell |
|---|---:|---:|---:|---:|
| random_rejects | 40 | 0 | 40 | 0 |
| close_rejected | 8 | 4 | 4 | 0 |
| close_kept | 8 | 3 | 4 | 1 |
| random_kept | 12 | 9 | 1 | 2 |
| changed_or_contested | 14 | 2 | 12 | 0 |

## Every posting the filter got wrong (either version)

| Key | Title | v0.1 | v0.3 | My verdict | My reason |
|---|---|---|---|---|---|
| `ashby/ramp/8fa367de-71ba-409e-befd-175a163acb1b` | Software Engineer, Fraud & Identity | rejected (6) | rejected (6) | RELEVANT | US backend software engineering role requiring 3+ years, which the candidate’s about 4 years meets, and matching the SWE target. |
| `ashby/ramp/42527ca9-03b9-499e-a5c4-18e4245af138` | Software Engineer, Backend, Developer API | kept (7) | kept (7) | NOT_RELEVANT | The role requires 5+ years of backend experience, above the candidate’s about 4 years. |
| `greenhouse/figma/5691886004` | Software Engineer - AI Platforms | kept (8) | kept (8) | NOT_RELEVANT | The role requires 5+ years of software engineering and 3+ years in AI, search, or developer platforms. |
| `greenhouse/stripe/8332718` | Software Engineer, Fraud System Interventions | kept (8) | kept (8) | NOT_RELEVANT | The posting requires 5 years of post-bachelor’s engineering experience plus specialized fraud and trust-and-safety experience. |
| `greenhouse/stripe/8306475` | Security Engineer, Privy | kept (7) | rejected (4) | NOT_RELEVANT | This is a specialized security engineering role requiring prior hands-on security operations and incident-response experience. |
| `greenhouse/stripe/8174965` | Security Engineer | kept (7) | rejected (5) | NOT_RELEVANT | This is a specialized abuse-control and security engineering position requiring a security-focused background. |
| `greenhouse/stripe/8197135` | Software Engineer, High Availability and Disaster Recovery | kept (7) | kept (7) | NOT_RELEVANT | The role requires 3 years with Go, Ruby, or Java plus database-internals expertise not established in the candidate profile. |
| `greenhouse/stripe/8073092` | Security Engineer, Privy | kept (7) | rejected (4) | NOT_RELEVANT | This is a security engineering role requiring prior security investigations, incident response, and security tooling experience. |
| `greenhouse/figma/6233040004` | Data & Integration Engineer, Business Systems | kept (7) | rejected (4) | NOT_RELEVANT | The data and integration engineering role requires 5+ years of specialized enterprise integration and production data-pipeline experience. |
| `ashby/linear/0c7c2e26-0a98-42cf-a47c-9a3999fb513b` | Product Engineer | rejected (6) | rejected (6) | RELEVANT | The North America Product Engineer role asks for 2–5 years and React/TypeScript full-stack skills aligned with the candidate’s background. |
| `greenhouse/figma/6223155004` | Compliance Engineer | kept (7) | rejected (4) | NOT_RELEVANT | The compliance engineering role requires 5+ years of specialized security and compliance engineering experience. |
| `greenhouse/stripe/8227563` | Partner Solutions Engineer, Ecosystem | kept (7) | rejected (4) | NOT_RELEVANT | The partner solutions engineering role requires 6+ years in a hands-on technical customer or partner-facing role. |
| `greenhouse/stripe/7867389` | Cloud Security Engineer | kept (7) | rejected (4) | NOT_RELEVANT | This is a specialized cloud security engineering role rather than a general software engineering opportunity. |
| `greenhouse/stripe/7377101` | Technical Solutions Engineer | kept (7) | rejected (5) | NOT_RELEVANT | The technical solutions role requires 4+ years of full-stack development and Mountain or Pacific time-zone residence. |
| `greenhouse/stripe/7230452` | Forward Deployed Engineer, Privy | kept (7) | kept (7) | NOT_RELEVANT | The FDE role requires 5+ years of full-stack development and web3 application experience not established in the profile. |
| `greenhouse/stripe/7230670` | Software Engineer, Data Orchestration | kept (8) | kept (8) | NOT_RELEVANT | The data orchestration engineering role requires 8+ years of professional software development experience. |
| `greenhouse/stripe/8198280` | Software Engineer, Backend | kept (8) | kept (8) | NOT_RELEVANT | The backend role requires a master’s degree in computer science or a related field plus 6 years of experience and several years in specified languages. |
| `ashby/ramp/428f41e2-48e8-409d-b5e3-8053f7fc7a27` | Software Engineer, Backend, Growth | kept (7) | kept (7) | NOT_RELEVANT | The backend growth role requires 5+ years of production backend engineering experience, above the candidate’s experience level. |
| `ashby/ramp/6a7e382f-240a-4952-b9e5-7fe2b3856bc9` | Applied AI Engineer, Fullstack | rejected (6) | rejected (6) | RELEVANT | The US full-stack Applied AI role emphasizes React, TypeScript, backend APIs, and shipped product experiences that align with the candidate’s skills and projects. |
| `greenhouse/stripe/8233889` | Offensive Security Engineer | kept (7) | rejected (5) | NOT_RELEVANT | The offensive security role requires 5+ years of penetration testing or red-team experience and specialized security tooling. |
| `greenhouse/figma/6158162004` | Forward Deployed Engineer | kept (7) | kept (7) | NOT_RELEVANT | The US Forward Deployed Engineer role requires 5+ years shipping production software and customer-embedded engineering experience. |
| `greenhouse/stripe/8075570` | Integration Engineer, Professional Services | kept (7) | rejected (5) | NOT_RELEVANT | The professional-services integration role requires 10+ years of full-stack development and software consulting experience. |
| `greenhouse/stripe/7462961` | Infrastructure Engineer, Privy | kept (7) | rejected (6) | NOT_RELEVANT | The infrastructure engineering role requires 8+ years building highly available production systems. |
| `greenhouse/stripe/8197891` | Software Engineer, Online Database Infrastructure | kept (9) | kept (9) | NOT_RELEVANT | The database infrastructure role requires 5 years of post-bachelor’s software development experience and specialized database infrastructure skills. |
| `ashby/ramp/7cd46077-05fe-4cd7-816f-5528638342f1` | Software Engineer, Frontend, Growth | kept (9) | kept (9) | NOT_RELEVANT | The frontend growth role requires 5+ years of front-end or design engineering experience. |
| `ashby/ramp/47a75895-24af-49b7-9858-1be0ec0e7c71` | Software Engineer, Backend, Accounts Receivable | rejected (6) | rejected (6) | RELEVANT | This is a US backend software engineering role involving APIs, data models, and asynchronous workflows, aligned with the candidate’s backend experience. |
| `greenhouse/stripe/8198323` | Solutions Engineer, AI Build Team | kept (7) | rejected (4) | NOT_RELEVANT | The AI solutions engineering role requires 7+ years of customer-facing technical delivery experience. |
| `greenhouse/stripe/7982720` | Software Engineer, Secure Devices | kept (7) | kept (7) | NOT_RELEVANT | The secure-devices role requires 4+ years in Go, Swift, or Objective-C and endpoint security experience not shown in the profile. |
| `ashby/ramp/7bfa613e-151c-469b-9973-c89ee3d14838` | Backend Engineer, Ops Engineering | kept (9) | kept (9) | NOT_RELEVANT | The backend operations engineering role requires 5+ years of production software engineering experience, above the candidate’s level. |

## The v0.2/v0.3 changes, judged

| Key | Title | v0.1 → v0.3 | My verdict | Change right? |
|---|---|---|---|---|
| `greenhouse/figma/6223155004` | Compliance Engineer | kept → rej | NOT_RELEVANT | yes |
| `greenhouse/figma/6233040004` | Data & Integration Engineer, Business Systems | kept → rej | NOT_RELEVANT | yes |
| `greenhouse/stripe/7377101` | Technical Solutions Engineer | kept → rej | NOT_RELEVANT | yes |
| `greenhouse/stripe/7462961` | Infrastructure Engineer, Privy | kept → rej | NOT_RELEVANT | yes |
| `greenhouse/stripe/7867389` | Cloud Security Engineer | kept → rej | NOT_RELEVANT | yes |
| `greenhouse/stripe/8073092` | Security Engineer, Privy | kept → rej | NOT_RELEVANT | yes |
| `greenhouse/stripe/8075570` | Integration Engineer, Professional Services | kept → rej | NOT_RELEVANT | yes |
| `greenhouse/stripe/8174965` | Security Engineer | kept → rej | NOT_RELEVANT | yes |
| `greenhouse/stripe/8198323` | Solutions Engineer, AI Build Team | kept → rej | NOT_RELEVANT | yes |
| `greenhouse/stripe/8227563` | Partner Solutions Engineer, Ecosystem | kept → rej | NOT_RELEVANT | yes |
| `greenhouse/stripe/8233889` | Offensive Security Engineer | kept → rej | NOT_RELEVANT | yes |
| `greenhouse/stripe/8306475` | Security Engineer, Privy | kept → rej | NOT_RELEVANT | yes |
| `greenhouse/figma/6158162004` | Forward Deployed Engineer | kept → kept | NOT_RELEVANT | — |
| `greenhouse/stripe/7230452` | Forward Deployed Engineer, Privy | kept → kept | NOT_RELEVANT | — |
