# Watch run 2026-10-31T144406-seeded-2

> **SEEDED RUN.** The input is a saved earlier response, not a fetch made by this run.

- Board: `anthropic`
- Source: SEEDED: saved earlier response runs/2026-10-31T144337/raw.json.gz (not fetched by this run)
- Started: 2026-10-31T14:44:06-04:00
- Status: **9 new posting(s)**
- Raw response: `raw.json.gz`, 9855369 bytes, sha256 `1e5b62fec42a5b1d83e1c491da70215c5b8f77776097b2ef26e1fb4e7b0a7e88`
- Postings in response: 675; ids seen before this run: 666; new: 9

## New postings

**Record** = the rule in CONTRACT.md; anyone can recompute it. **Judgment** = Claude under the prompt contract; an opinion, not a fact. Where they disagree, the record is the rule's verdict.

| id | title | location | Record (rule) | Judgment (Claude) | agree? |
|---|---|---|---|---|---|
| 5468266008 | Content Strategy Lead, Executive Programs | San Francisco, CA \| New York City, NY | not relevant | not relevant (high confidence) | yes |
| 5467233008 | Contracts Manager, GTM | San Francisco, CA | not relevant | not relevant (high confidence) | yes |
| 5462040008 | Customer Success Manager, Beneficial Deployments EMEA | London, UK | not relevant | not relevant (high confidence) | yes |
| 5468392008 | Data Center Electrical Engineer – Design | Remote-Friendly, United States | not relevant | not relevant (high confidence) | yes |
| 5468374008 | Data Center Power Generation and Microgrids Engineer | Remote-Friendly, United States | not relevant | not relevant (high confidence) | yes |
| 5468380008 | Data Center Substation, Protection & Automation Engineer | Remote-Friendly, United States | not relevant | not relevant (high confidence) | yes |
| 5464234008 | Data Engineer | San Francisco, CA \| New York City, NY; Seattle, WA | relevant | relevant (medium confidence) | yes |
| 5394403008 | Engineering Manager, Integrity and Attestation | San Francisco, CA \| Seattle, WA | not relevant | not relevant (high confidence) | yes |
| 5467690008 | Research Operations Lead, Biology | Boston, MA | not relevant | not relevant (high confidence) | yes |

### Justifications

**5468266008 — Content Strategy Lead, Executive Programs**

- Record (rule): not relevant. title "Content Strategy Lead, Executive Programs" matched no experience[].title word; content matched no skill; title has no management word; location: San Francisco, CA | New York City, NY (not used); failed: title test, skills test
- Judgment (Claude, claude-sonnet-5-5, 2026-10-31T14:44:06-04:00, prompt v1): not relevant, high confidence. Fields: experience[].title, skills / title, content. The posting "Content Strategy Lead, Executive Programs" is a senior product marketing/executive content role requiring C-level content experience, team management, and "12+ years" preferred. The candidate's only experience title is "AI Engineer Co-op" with technical skills ("Python", "Databricks", "LangGraph") that do not match the marketing, speaker coaching, and people-management requirements. Seniority and function are both mismatched.

**5467233008 — Contracts Manager, GTM**

- Record (rule): not relevant. title "Contracts Manager, GTM" matched no experience[].title word; content matched no skill; title contains management word(s): "Manager"; location: San Francisco, CA (not used); failed: title test, skills test, management test
- Judgment (Claude, claude-sonnet-5-5, 2026-10-31T14:44:12-04:00, prompt v1): not relevant, high confidence. Fields: experience[].title, skills / title, content. The posting "Contracts Manager, GTM" is a legal role requiring "substantial experience drafting, reviewing, and negotiating commercial contracts" and negotiating with customers' legal teams. The candidate's title "AI Engineer Co-op" and skills ("Python", "Databricks", "LangGraph", "MLflow") are technical/engineering with no contracts or legal experience, so there is no meaningful match.

**5462040008 — Customer Success Manager, Beneficial Deployments EMEA**

- Record (rule): not relevant. title "Customer Success Manager, Beneficial Deployments EMEA" matched no experience[].title word; content matched no skill; title contains management word(s): "Manager"; location: London, UK (not used); failed: title test, skills test, management test
- Judgment (Claude, claude-sonnet-5-5, 2026-10-31T14:44:15-04:00, prompt v1): not relevant, high confidence. Fields: experience[].title, skills / title, location.name, content. The posting "Customer Success Manager, Beneficial Deployments EMEA" in "London, UK" is a customer-facing role requiring "5+ years of experience in customer-facing roles (Customer Success, Consulting, Solutions Architecture, or similar)". The candidate's only listed title is "AI Engineer Co-op", an engineering co-op with technical skills like "Python" and "LangGraph" but no customer success background or years of experience. The technical fluency is a partial overlap, but the role's core is relationship management, so it is a poor fit.

**5468392008 — Data Center Electrical Engineer – Design**

- Record (rule): not relevant. title "Data Center Electrical Engineer – Design" matched experience[].title word(s) "Engineer"; content matched no skill; title has no management word; location: Remote-Friendly, United States (not used); failed: skills test
- Judgment (Claude, claude-sonnet-5-5, 2026-10-31T14:44:21-04:00, prompt v1): not relevant, high confidence. Fields: experience[].title, skills / title, content. The posting "Data Center Electrical Engineer – Design" requires "10+ years of electrical engineering experience in mission-critical facilities", NEC/IEEE codes expertise, and power systems studies in tools like "SKM, ETAP, or EasyPower". The candidate's only title is "AI Engineer Co-op" and skills ("Python", "SQL", "Databricks", "LangGraph") are software/data/AI, with no electrical engineering background. Clear mismatch in seniority and domain.

**5468374008 — Data Center Power Generation and Microgrids Engineer**

- Record (rule): not relevant. title "Data Center Power Generation and Microgrids Engineer" matched experience[].title word(s) "Engineer"; content matched no skill; title has no management word; location: Remote-Friendly, United States (not used); failed: skills test
- Judgment (Claude, claude-sonnet-5-5, 2026-10-31T14:44:25-04:00, prompt v1): not relevant, high confidence. Fields: experience[].title, skills / title, content. The posting "Data Center Power Generation and Microgrids Engineer" is a electrical power engineering role requiring "10+ years of engineering experience in power generation, microgrids, battery energy storage, or utility interconnection", plus gensets, IEEE 1547/2800 and tools like ETAP and PSCAD. The candidate's sole title is "AI Engineer Co-op" and skills ("Python", "Databricks", "LangGraph", "MLflow") are software/data/AI, with no power systems overlap and far less experience than required.

**5468380008 — Data Center Substation, Protection & Automation Engineer**

- Record (rule): not relevant. title "Data Center Substation, Protection & Automation Engineer" matched experience[].title word(s) "Engineer"; content matched no skill; title has no management word; location: Remote-Friendly, United States (not used); failed: skills test
- Judgment (Claude, claude-sonnet-5-5, 2026-10-31T14:44:31-04:00, prompt v1): not relevant, high confidence. Fields: experience[].title, skills / title, content. The posting "Data Center Substation, Protection & Automation Engineer" requires "10+ years of experience in power system protection engineering", relay settings, short-circuit and arc-flash studies, and IEC 61850 SCADA. The candidate's only listed title is "AI Engineer Co-op", with skills like "Python", "Databricks", "LangGraph" and "MLflow". These are software/AI data skills with no electrical power engineering overlap, and the seniority gap is large. Not worth applying.

**5464234008 — Data Engineer**

- Record (rule): relevant. title "Data Engineer" matched experience[].title word(s) "Engineer"; content matched skills: Python, SQL; title has no management word; location: San Francisco, CA | New York City, NY; Seattle, WA (not used)
- Judgment (Claude, claude-sonnet-5-5, 2026-10-31T14:44:35-04:00, prompt v1): relevant, medium confidence. Fields: experience[].title, skills / title, content, location.name. The posting "Data Engineer" asks for "Strong SQL and Python" and modern transformation and orchestration tooling on a cloud data warehouse. The candidate's skills list "Python", "SQL", "Databricks", "Delta Lake" and "AWS", which match well. The preferred "Experience using LLMs inside data pipelines and evaluating their output" fits the "AI Engineer Co-op" title and skills like "LangGraph" and "MLflow". Gaps: the candidate has only a co-op, while the posting prefers "5+ years", and shows no CRM or Salesforce experience. The role is in SF, NYC or Seattle, and the posting says "We do sponsor visas". It is a stretch but worth applying to.

**5394403008 — Engineering Manager, Integrity and Attestation**

- Record (rule): not relevant. title "Engineering Manager, Integrity and Attestation" matched experience[].title word(s) "Engineering"; content matched no skill; title contains management word(s): "Manager"; location: San Francisco, CA | Seattle, WA (not used); failed: skills test, management test
- Judgment (Claude, claude-sonnet-5-5, 2026-10-31T14:44:39-04:00, prompt v1): not relevant, high confidence. Fields: experience[].title, skills / title, content. The posting "Engineering Manager, Integrity and Attestation" requires "At least 5+ years managing engineering teams and 8+ years hands-on in platform, infrastructure, or security engineering", plus expertise in remote attestation, secure boot, TPM, and hardware roots of trust. The candidate's only listed experience title is "AI Engineer Co-op", with data and ML skills such as "Databricks", "LangGraph", and "MLflow". There is no management experience, no security or firmware background, and a large seniority gap, so applying is unlikely to pay off.

**5467690008 — Research Operations Lead, Biology**

- Record (rule): not relevant. title "Research Operations Lead, Biology" matched no experience[].title word; content matched no skill; title has no management word; location: Boston, MA (not used); failed: title test, skills test
- Judgment (Claude, claude-sonnet-5-5, 2026-10-31T14:44:42-04:00, prompt v1): not relevant, high confidence. Fields: experience[].title, skills / title, content. The posting "Research Operations Lead, Biology" is a wet-lab operations role. Its minimum qualifications require having "managed the day-to-day operations of a life sciences lab", plus hands-on procurement/vendor management and operating budget ownership. The candidate's only experience title is "AI Engineer Co-op" and skills ("Python", "Databricks", "LangGraph", "MLflow") are software/data/AI oriented, with no lab, procurement or facilities background. Only a minor preferred item about AI tools overlaps. The role is also senior, so it is a poor fit.

