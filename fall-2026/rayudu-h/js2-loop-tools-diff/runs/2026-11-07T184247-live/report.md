# Loop run 2026-11-07T184247-live

- Config: `boards.json`
- **Exit: incomplete**
- HTTP requests sent: 6

| board | status | postings | new | note |
|---|---|---|---|---|
| greenhouse:anthropic | ok | 675 | 61 |  |
| ashby:notion | ok | 154 | 18 |  |
| ashby:perplexity | ok | 137 | 5 |  |
| ashby:notion-does-not-exist-js2 | **failed** | — | **no result** | HTTP 404 (permanent; not retried) |
| ashby:openai | **failed** | — | **no result** | timeout: timed out (transient; retried once) |

## New postings

**Record** = the rule (recomputable). **Judgment** = Claude under prompt contract v2, an opinion.

**greenhouse:anthropic — AI Outcomes Manager, Strategic Tech (Spanish-speaking)** (`5465639008`, San Francisco, CA | Seattle, WA | New York City, NY | Washington, DC)

- Record (rule): not relevant. title "AI Outcomes Manager, Strategic Tech (Spanish-speaking)" matched experience[].title word(s) "AI"; content matched no skill; title contains management word(s): "Manager"; location: San Francisco, CA | Seattle, WA | New York City, NY | Washington, DC (not used); failed: skills test, management test
- Judgment (Claude, claude-sonnet-5-5, 2026-11-07T18:42:49-05:00): not relevant, high confidence. The posting "title" is "AI Outcomes Manager, Strategic Tech (Spanish-speaking)". It shares the whole word "AI" with the candidate's "experience[].title" ("AI Engineer Co-op"), but it also contains "Manager", which the rule excludes. Condition 3 fails, so the posting is not relevant whatever the "content" says about skills.

**greenhouse:anthropic — Applied AI Architect** (`5450798008`, Sydney, Australia)

- Record (rule): relevant. title "Applied AI Architect" matched experience[].title word(s) "AI"; content matched skills: Python; title has no management word; location: Sydney, Australia (not used)
- Judgment (Claude, claude-sonnet-5-5, 2026-11-07T18:42:54-05:00): relevant, high confidence. The posting title "Applied AI Architect" contains the whole word "AI", which is a word in the candidate's experience title "AI Engineer Co-op" (other than "Co-op"). The content names the candidate's skill "Python" in "Comfortable with Python". The title contains none of "Manager", "Director" or "Head". Location (Sydney) does not affect the verdict.

**greenhouse:anthropic — Applied AI Architect, Beneficial Deployments (Global & Public Health)** (`5471361008`, San Francisco, CA | New York City, NY)

- Record (rule): not relevant. title "Applied AI Architect, Beneficial Deployments (Global & Public Health)" matched experience[].title word(s) "AI"; content matched no skill; title has no management word; location: San Francisco, CA | New York City, NY (not used); failed: skills test
- Judgment (Claude, claude-sonnet-5-5, 2026-11-07T18:42:58-05:00): not relevant, high confidence. The title "Applied AI Architect, Beneficial Deployments (Global & Public Health)" contains "AI", a word from the candidate's experience title "AI Engineer Co-op", and has no "Manager", "Director" or "Head", so conditions 1 and 3 hold. But the content names none of the candidate's skills ("Python", "SQL", "Databricks", "Unity Catalog", "Power BI", "LangGraph", "MLflow", "Mem0", "Delta Lake", "AWS") as whole words. It only mentions LLM APIs, Claude and health topics, so condition 2 fails.

**greenhouse:anthropic — Applied AI Architect, Democratic Partnerships** (`5473198008`, San Francisco, CA | New York City, NY)

- Record (rule): relevant. title "Applied AI Architect, Democratic Partnerships" matched experience[].title word(s) "AI"; content matched skills: Python; title has no management word; location: San Francisco, CA | New York City, NY (not used)
- Judgment (Claude, claude-sonnet-5-5, 2026-11-07T18:43:04-05:00): relevant, high confidence. The posting "title" is "Applied AI Architect, Democratic Partnerships". It contains the whole word "AI", which comes from the candidate's "experience[].title" entry "AI Engineer Co-op" (the word is not "Co-op"). The "content" names the candidate's skill "Python" in "Python preferred". The title has no "Manager", "Director" or "Head". Neither field is empty, and location is ignored. All three conditions hold.

**greenhouse:anthropic — Applied AI Architect ( Global Customers)** (`5461252008`, Bangalore, India)

- Record (rule): relevant. title "Applied AI Architect ( Global Customers)" matched experience[].title word(s) "AI"; content matched skills: Python; title has no management word; location: Bangalore, India (not used)
- Judgment (Claude, claude-sonnet-5-5, 2026-11-07T18:43:09-05:00): relevant, high confidence. The posting "title" is "Applied AI Architect ( Global Customers)". It contains "AI" as a whole word, which is a word in the candidate's "experience[].title" entry "AI Engineer Co-op" and is not "Co-op". The "content" says "Comfortable with Python", and "Python" is in the candidate's "skills". The title contains none of "Manager", "Director" or "Head"; "Technical Account Manager" appears only in the content, not the title. All three conditions hold. Location is not used.

**greenhouse:anthropic — Applied AI Architect, International Policy** (`5473195008`, San Francisco, CA | New York City, NY)

- Record (rule): relevant. title "Applied AI Architect, International Policy" matched experience[].title word(s) "AI"; content matched skills: Python; title has no management word; location: San Francisco, CA | New York City, NY (not used)
- Judgment (Claude, claude-sonnet-5-5, 2026-11-07T18:43:13-05:00): relevant, high confidence. The posting "title" is "Applied AI Architect, International Policy", which contains the whole word "AI" from the candidate's "experience[].title" entry "AI Engineer Co-op" ("Co-op" is excluded and not needed). The "content" says "Python preferred", which matches the candidate's "skills" entry "Python". The title has no "Manager", "Director" or "Head". All three conditions hold, and location is ignored.

**greenhouse:anthropic — Applied AI Architect, Partnerships** (`5472677008`, Sydney, Australia)

- Record (rule): not relevant. title "Applied AI Architect, Partnerships" matched experience[].title word(s) "AI"; content matched no skill; title has no management word; location: Sydney, Australia (not used); failed: skills test
- Judgment (Claude, claude-sonnet-5-5, 2026-11-07T18:43:19-05:00): not relevant, high confidence. The posting "title" contains "AI", which is a word from the candidate's "experience[].title" ("AI Engineer Co-op"), and it has no "Manager", "Director" or "Head". The posting "content" names none of the candidate's "skills" ("Python", "SQL", "Databricks", "Unity Catalog", "Power BI", "LangGraph", "MLflow", "Mem0", "Delta Lake", "AWS") as a whole word. It only mentions generic "cloud" and "LLM frameworks". Condition 2 fails, so the posting is not relevant.

**greenhouse:anthropic — Applied AI Architect, Public Sector (State & Local Government)** (`5455618008`, San Francisco, CA)

- Record (rule): relevant. title "Applied AI Architect, Public Sector (State & Local Government)" matched experience[].title word(s) "AI"; content matched skills: Python; title has no management word; location: San Francisco, CA (not used)
- Judgment (Claude, claude-sonnet-5-5, 2026-11-07T18:43:24-05:00): relevant, high confidence. The candidate's experience title "AI Engineer Co-op" contains the word "AI" (other than "Co-op"), and the posting title "Applied AI Architect, Public Sector (State & Local Government)" contains "AI" as a whole word. The posting content lists "Familiar with Python", and "Python" is one of the candidate's skills. The title contains none of "Manager", "Director" or "Head". All three conditions hold. Location is not used.

**greenhouse:anthropic — Applied Scientist, Engineering** (`5468939008`, San Francisco, CA)

- Record (rule): relevant. title "Applied Scientist, Engineering" matched experience[].title word(s) "Engineering"; content matched skills: Python; title has no management word; location: San Francisco, CA (not used)
- Judgment (Claude, claude-sonnet-5-5, 2026-11-07T18:43:28-05:00): relevant, high confidence. The candidate's experience title "AI Engineer Co-op" includes "Engineer", so the posting title "Applied Scientist, Engineering" matches on "Engineering". The content names the skill "Python" in "Basic programming proficiency, for example in Python". The title has no "Manager", "Director" or "Head". All three conditions hold. Location is not considered.

**greenhouse:anthropic — Brand Strategy Lead, Brand Architecture & Naming** (`5475321008`, San Francisco, CA | New York City, NY)

- Record (rule): not relevant. title "Brand Strategy Lead, Brand Architecture & Naming" matched no experience[].title word; content matched no skill; title has no management word; location: San Francisco, CA | New York City, NY (not used); failed: title test, skills test
- Judgment (Claude, claude-sonnet-5-5, 2026-11-07T18:43:32-05:00): not relevant, high confidence. The candidate's experience title "AI Engineer Co-op" gives the usable words "AI" and "Engineer" ("Co-op" is excluded, and "Engineering" also counts). The posting title "Brand Strategy Lead, Brand Architecture & Naming" contains none of them, so the title rule fails. The "content" is about brand architecture and naming and does not name any of the candidate's skills. It mentions "engineers" only in the company blurb, and that is not in the title anyway. The title does not contain "Manager", "Director" or "Head", but the rule needs all three conditions. Location does not matter.

**greenhouse:anthropic — Business Recruiter** (`5471118008`, Dublin, IE)

- Record (rule): not relevant. title "Business Recruiter" matched no experience[].title word; content matched no skill; title has no management word; location: Dublin, IE (not used); failed: title test, skills test
- Judgment (Claude, claude-sonnet-5-5, 2026-11-07T18:43:37-05:00): not relevant, high confidence. The posting title is "Business Recruiter". The candidate's experience title "AI Engineer Co-op" gives the words "AI" and "Engineer" ("Co-op" is excluded, and "Engineering" also counts). None of these appears in the title as a whole word, so condition 1 fails. The content is a recruiting role and does not name any of the candidate's skills such as "Python", "SQL" or "AWS", so condition 2 also fails.

**greenhouse:anthropic — Business Recruiter, London** (`5471100008`, London, UK)

- Record (rule): not relevant. title "Business Recruiter, London" matched no experience[].title word; content matched no skill; title has no management word; location: London, UK (not used); failed: title test, skills test
- Judgment (Claude, claude-sonnet-5-5, 2026-11-07T18:43:42-05:00): not relevant, high confidence. The posting title "Business Recruiter, London" contains none of the usable words from the candidate's experience title "AI Engineer Co-op". Those words are "AI" and "Engineer", plus "Engineering"; "Co-op" is excluded. Condition 1 fails. The "content" field also names none of the candidate's skills, such as "Python", "SQL" or "AWS", so condition 2 fails too. The title has no "Manager", "Director" or "Head", but that does not change the verdict.

**greenhouse:anthropic — Corporate Finance & Strategy, Strategic Transactions** (`5430263008`, San Francisco, CA)

- Record (rule): not relevant. title "Corporate Finance & Strategy, Strategic Transactions" matched no experience[].title word; content matched no skill; title has no management word; location: San Francisco, CA (not used); failed: title test, skills test
- Judgment (Claude, claude-sonnet-5-5, 2026-11-07T18:43:46-05:00): not relevant, high confidence. The candidate's experience title "AI Engineer Co-op" gives the usable words "AI" and "Engineer" (plus "Engineering"), since "Co-op" is excluded. The posting title "Corporate Finance & Strategy, Strategic Transactions" contains none of them as a whole word, so condition 1 fails and the posting is not relevant regardless of the skills match in the content.

**greenhouse:anthropic — Customer Program Manager, Executive Briefings** (`5463187008`, London, UK)

- Record (rule): not relevant. title "Customer Program Manager, Executive Briefings" matched no experience[].title word; content matched no skill; title contains management word(s): "Manager"; location: London, UK (not used); failed: title test, skills test, management test
- Judgment (Claude, claude-sonnet-5-5, 2026-11-07T18:43:50-05:00): not relevant, high confidence. The posting "title" is "Customer Program Manager, Executive Briefings". It has none of the words from the candidate's "experience[].title" value "AI Engineer Co-op" ("AI", "Engineer", with "Co-op" excluded), so condition 1 fails. The title also contains "Manager", which fails condition 3. Either failure alone makes the posting not relevant.

**greenhouse:anthropic — Data Center Asset Management, Commercial Associate** (`5468352008`, San Francisco, CA | New York City, NY)

- Record (rule): not relevant. title "Data Center Asset Management, Commercial Associate" matched no experience[].title word; content matched no skill; title has no management word; location: San Francisco, CA | New York City, NY (not used); failed: title test, skills test
- Judgment (Claude, claude-sonnet-5-5, 2026-11-07T18:43:54-05:00): not relevant, high confidence. Condition 1 fails. The candidate's experience title "AI Engineer Co-op" gives the usable words "AI" and "Engineer", plus "Engineering", with "Co-op" excluded. The posting title "Data Center Asset Management, Commercial Associate" contains none of them as a whole word. The content describes a commercial and contract negotiation role and does not name the candidate's technical skills such as "Python" or "SQL".

**greenhouse:anthropic — Data Center Energy Lead** (`5454474008`, Remote-Friendly (Travel-Required) | San Francisco, CA | Seattle, WA | New York City, NY)

- Record (rule): not relevant. title "Data Center Energy Lead" matched no experience[].title word; content matched no skill; title has no management word; location: Remote-Friendly (Travel-Required) | San Francisco, CA | Seattle, WA | New York City, NY (not used); failed: title test, skills test
- Judgment (Claude, claude-sonnet-5-5, 2026-11-07T18:43:59-05:00): not relevant, high confidence. The candidate's experience title "AI Engineer Co-op" gives the usable words "AI" and "Engineer" ("Co-op" is excluded, and "Engineering" also counts). The posting title "Data Center Energy Lead" contains none of them as a whole word, so condition 1 fails and the posting is not relevant regardless of the description or skills.

**greenhouse:anthropic — Data Center Facility Operations Lead** (`5386214008`, Sydney, Australia)

- Record (rule): not relevant. title "Data Center Facility Operations Lead" matched no experience[].title word; content matched no skill; title has no management word; location: Sydney, Australia (not used); failed: title test, skills test
- Judgment (Claude, claude-sonnet-5-5, 2026-11-07T18:44:03-05:00): not relevant, high confidence. The candidate's only experience title is "AI Engineer Co-op". Excluding "Co-op", the usable words are "AI" and "Engineer" (plus "Engineering"). The posting title "Data Center Facility Operations Lead" contains none of these as a whole word, so condition 1 fails and the posting is not relevant. The title has no "Manager", "Director" or "Head", but that does not change the outcome.

**greenhouse:anthropic — Data Center Strategic Sourcing Lead - Construction** (`5468875008`, San Francisco, CA | New York City, NY)

- Record (rule): not relevant. title "Data Center Strategic Sourcing Lead - Construction" matched no experience[].title word; content matched no skill; title has no management word; location: San Francisco, CA | New York City, NY (not used); failed: title test, skills test
- Judgment (Claude, claude-sonnet-5-5, 2026-11-07T18:44:08-05:00): not relevant, high confidence. The candidate's only experience title is "AI Engineer Co-op", which leaves "AI" and "Engineer" (plus "Engineering") as the words that can count. The posting title "Data Center Strategic Sourcing Lead - Construction" contains none of them as a whole word, so condition 1 fails. The title has no "Manager", "Director" or "Head", but that does not change the verdict.

**greenhouse:anthropic — Energy Special Projects** (`5469339008`, San Francisco, CA | New York City, NY)

- Record (rule): not relevant. title "Energy Special Projects" matched no experience[].title word; content matched no skill; title has no management word; location: San Francisco, CA | New York City, NY (not used); failed: title test, skills test
- Judgment (Claude, claude-sonnet-5-5, 2026-11-07T18:44:11-05:00): not relevant, high confidence. The posting title "Energy Special Projects" contains none of the words from the candidate's experience title "AI Engineer Co-op" (other than "Co-op"): no "AI" or "Engineer", and "Engineering" is absent too. Rule 1 fails. The "content" also names none of the candidate's skills such as "Python", "SQL" or "AWS", so rule 2 fails as well. The title has no "Manager", "Director" or "Head", but the other two rules decide the verdict.

**greenhouse:anthropic — Energy Supply  Lead - Power Supply and PPA** (`5469341008`, San Francisco, CA | New York City, NY)

- Record (rule): not relevant. title "Energy Supply  Lead - Power Supply and PPA" matched no experience[].title word; content matched no skill; title has no management word; location: San Francisco, CA | New York City, NY (not used); failed: title test, skills test
- Judgment (Claude, claude-sonnet-5-5, 2026-11-07T18:44:17-05:00): not relevant, high confidence. The only candidate title is "AI Engineer Co-op". Excluding "Co-op", the qualifying words are "AI" and "Engineer" (and "Engineering"). The posting title "Energy Supply  Lead - Power Supply and PPA" contains none of them as a whole word, so condition 1 fails and the posting is not relevant. Skills and location do not change this.

**greenhouse:anthropic — Enterprise Account Executive - FSI** (`5470905008`, Seoul, South Korea)

- Record (rule): not relevant. title "Enterprise Account Executive - FSI" matched no experience[].title word; content matched no skill; title has no management word; location: Seoul, South Korea (not used); failed: title test, skills test
- Judgment (Claude, claude-sonnet-5-5, 2026-11-07T18:44:22-05:00): not relevant, high confidence. The candidate's experience[].title is "AI Engineer Co-op", so the qualifying words are "AI" and "Engineer" (and "Engineering"). The posting title "Enterprise Account Executive - FSI" contains none of them as a whole word, so condition 1 fails. The title has no "Manager", "Director" or "Head", but the rule needs all three conditions, so the verdict is not relevant. Location is not considered.

**greenhouse:anthropic — Enterprise Account Executive - Healthcare & Life Science** (`5470906008`, Seoul, South Korea)

- Record (rule): not relevant. title "Enterprise Account Executive - Healthcare & Life Science" matched no experience[].title word; content matched no skill; title has no management word; location: Seoul, South Korea (not used); failed: title test, skills test
- Judgment (Claude, claude-sonnet-5-5, 2026-11-07T18:44:26-05:00): not relevant, high confidence. The candidate's experience title "AI Engineer Co-op" gives the usable words "AI" and "Engineer" (plus "Engineering"), once "Co-op" is excluded. The posting title "Enterprise Account Executive - Healthcare & Life Science" contains none of them as a whole word, so condition 1 fails. The title has no "Manager", "Director" or "Head", but that does not change the result. The content is a sales role and does not appear to name the candidate's skills such as "Python" or "SQL". Location is not a factor.

**greenhouse:anthropic — Equity Accounting and Reporting** (`5463197008`, San Francisco, CA)

- Record (rule): not relevant. title "Equity Accounting and Reporting" matched no experience[].title word; content matched no skill; title has no management word; location: San Francisco, CA (not used); failed: title test, skills test
- Judgment (Claude, claude-sonnet-5-5, 2026-11-07T18:44:31-05:00): not relevant, high confidence. The posting "title" is "Equity Accounting and Reporting". The candidate's "experience[].title" is "AI Engineer Co-op", which leaves "AI" and "Engineer" once "Co-op" is excluded. "Engineering" also counts, but none of these three words appears in the posting title as a whole word. Criterion 1 fails, so the posting is not relevant whatever the "content" says about skills.

**greenhouse:anthropic — Finance Systems Lead, International** (`5475456008`, Dublin, IE)

- Record (rule): not relevant. title "Finance Systems Lead, International" matched no experience[].title word; content matched skills: Python, SQL; title has no management word; location: Dublin, IE (not used); failed: title test
- Judgment (Claude, claude-sonnet-5-5, 2026-11-07T18:44:35-05:00): not relevant, high confidence. The posting "title" is "Finance Systems Lead, International". The candidate's "experience[].title" is "AI Engineer Co-op", which leaves the words "AI" and "Engineer" (plus "Engineering") once "Co-op" is excluded. None of these appear as a whole word in the title, so condition 1 fails. The "content" does name the skills "SQL" and "Python", and the title has no "Manager", "Director" or "Head". Those two conditions don't make up for the title mismatch.

**greenhouse:anthropic — Gas Supply and Transport Lead, US and Canada** (`5469337008`, San Francisco, CA | New York City, NY)

- Record (rule): not relevant. title "Gas Supply and Transport Lead, US and Canada" matched no experience[].title word; content matched no skill; title has no management word; location: San Francisco, CA | New York City, NY (not used); failed: title test, skills test
- Judgment (Claude, claude-sonnet-5-5, 2026-11-07T18:44:40-05:00): not relevant, high confidence. The posting "title" is "Gas Supply and Transport Lead, US and Canada". The candidate's "experience[].title" is "AI Engineer Co-op", so the qualifying words are "AI" and "Engineer" (and "Engineering"), since "Co-op" is excluded. None of them appears as a whole word in the posting title, so condition 1 fails and the posting is not relevant whatever the "content" says.

**greenhouse:anthropic — Head of ASEAN, Applied AI** (`5424312008`, Singapore)

- Record (rule): not relevant. title "Head of ASEAN, Applied AI" matched experience[].title word(s) "AI"; content matched no skill; title contains management word(s): "Head"; location: Singapore (not used); failed: skills test, management test
- Judgment (Claude): none: Claude budget used up

**greenhouse:anthropic — Head of Enablement Experience & Innovation** (`5461190008`, San Francisco, CA | New York City, NY)

- Record (rule): not relevant. title "Head of Enablement Experience & Innovation" matched no experience[].title word; content matched no skill; title contains management word(s): "Head"; location: San Francisco, CA | New York City, NY (not used); failed: title test, skills test, management test
- Judgment (Claude): none: Claude budget used up

**greenhouse:anthropic — Head of Partner Services Delivery and Success** (`5471925008`, Remote-Friendly (Travel Required) | San Francisco, CA)

- Record (rule): not relevant. title "Head of Partner Services Delivery and Success" matched no experience[].title word; content matched no skill; title contains management word(s): "Head"; location: Remote-Friendly (Travel Required) | San Francisco, CA (not used); failed: title test, skills test, management test
- Judgment (Claude): none: Claude budget used up

**greenhouse:anthropic — Incident Manager - Detection & Response** (`5397751008`, Zürich, CH)

- Record (rule): not relevant. title "Incident Manager - Detection & Response" matched no experience[].title word; content matched no skill; title contains management word(s): "Manager"; location: Zürich, CH (not used); failed: title test, skills test, management test
- Judgment (Claude): none: Claude budget used up

**greenhouse:anthropic — Internal Communications Manager, Product** (`5444002008`, San Francisco, CA)

- Record (rule): not relevant. title "Internal Communications Manager, Product" matched no experience[].title word; content matched no skill; title contains management word(s): "Manager"; location: San Francisco, CA (not used); failed: title test, skills test, management test
- Judgment (Claude): none: Claude budget used up

**greenhouse:anthropic — Learning & Education Specialist** (`5462661008`, San Francisco, CA | New York City, NY)

- Record (rule): not relevant. title "Learning & Education Specialist" matched no experience[].title word; content matched no skill; title has no management word; location: San Francisco, CA | New York City, NY (not used); failed: title test, skills test
- Judgment (Claude): none: Claude budget used up

**greenhouse:anthropic — Legal Specialist, Law Enforcement** (`5474559008`, San Francisco, CA | New York City, NY)

- Record (rule): not relevant. title "Legal Specialist, Law Enforcement" matched no experience[].title word; content matched no skill; title has no management word; location: San Francisco, CA | New York City, NY (not used); failed: title test, skills test
- Judgment (Claude): none: Claude budget used up

**greenhouse:anthropic — Manager, Enterprise Sales, DACH & CEE** (`5469530008`, Munich, Germany)

- Record (rule): not relevant. title "Manager, Enterprise Sales, DACH & CEE" matched no experience[].title word; content matched no skill; title contains management word(s): "Manager"; location: Munich, Germany (not used); failed: title test, skills test, management test
- Judgment (Claude): none: Claude budget used up

**greenhouse:anthropic — Manager, Forward Deployed Engineering** (`5442048008`, Munich, Germany)

- Record (rule): not relevant. title "Manager, Forward Deployed Engineering" matched experience[].title word(s) "Engineering"; content matched no skill; title contains management word(s): "Manager"; location: Munich, Germany (not used); failed: skills test, management test
- Judgment (Claude): none: Claude budget used up

**greenhouse:anthropic — Manager, Forward Deployed Engineering** (`5471721008`, Paris, France)

- Record (rule): not relevant. title "Manager, Forward Deployed Engineering" matched experience[].title word(s) "Engineering"; content matched no skill; title contains management word(s): "Manager"; location: Paris, France (not used); failed: skills test, management test
- Judgment (Claude): none: Claude budget used up

**greenhouse:anthropic — Marketing Lead, Claude Frontier Academy** (`5467561008`, San Francisco, CA | New York City, NY)

- Record (rule): not relevant. title "Marketing Lead, Claude Frontier Academy" matched no experience[].title word; content matched no skill; title has no management word; location: San Francisco, CA | New York City, NY (not used); failed: title test, skills test
- Judgment (Claude): none: Claude budget used up

**greenhouse:anthropic — Partner Account Manager - France** (`5471026008`, Paris, France)

- Record (rule): not relevant. title "Partner Account Manager - France" matched no experience[].title word; content matched no skill; title contains management word(s): "Manager"; location: Paris, France (not used); failed: title test, skills test, management test
- Judgment (Claude): none: Claude budget used up

**greenhouse:anthropic — Partner Specializations Lead** (`5464485008`, San Francisco, CA | New York City, NY)

- Record (rule): not relevant. title "Partner Specializations Lead" matched no experience[].title word; content matched skills: SQL; title has no management word; location: San Francisco, CA | New York City, NY (not used); failed: title test
- Judgment (Claude): none: Claude budget used up

**greenhouse:anthropic — People Services Partner, Compliance** (`5461871008`, San Francisco, CA | New York City, NY | Seattle, WA)

- Record (rule): not relevant. title "People Services Partner, Compliance" matched no experience[].title word; content matched no skill; title has no management word; location: San Francisco, CA | New York City, NY | Seattle, WA (not used); failed: title test, skills test
- Judgment (Claude): none: Claude budget used up

**greenhouse:anthropic — Political Economist, Rule of Law** (`5474544008`, San Francisco, CA | New York City, NY; Washington, DC)

- Record (rule): not relevant. title "Political Economist, Rule of Law" matched no experience[].title word; content matched no skill; title has no management word; location: San Francisco, CA | New York City, NY; Washington, DC (not used); failed: title test, skills test
- Judgment (Claude): none: Claude budget used up

**greenhouse:anthropic — Procurement Operations Business Partner - Workplace, Security and People** (`5425680008`, San Francisco, CA | Seattle, WA)

- Record (rule): not relevant. title "Procurement Operations Business Partner - Workplace, Security and People" matched no experience[].title word; content matched no skill; title has no management word; location: San Francisco, CA | Seattle, WA (not used); failed: title test, skills test
- Judgment (Claude): none: Claude budget used up

**greenhouse:anthropic — Product Finance & Strategy, Claude Platform, Forecasting & Rhythms** (`5358096008`, San Francisco, CA)

- Record (rule): not relevant. title "Product Finance & Strategy, Claude Platform, Forecasting & Rhythms" matched no experience[].title word; content matched skills: SQL; title has no management word; location: San Francisco, CA (not used); failed: title test
- Judgment (Claude): none: Claude budget used up

**greenhouse:anthropic — Public Policy, Strategic Advisory** (`5473110008`, San Francisco, CA; Washington, DC)

- Record (rule): not relevant. title "Public Policy, Strategic Advisory" matched no experience[].title word; content matched no skill; title has no management word; location: San Francisco, CA; Washington, DC (not used); failed: title test, skills test
- Judgment (Claude): none: Claude budget used up

**greenhouse:anthropic — Recruiter, Applied AI** (`5475240008`, San Francisco, CA | New York City, NY)

- Record (rule): not relevant. title "Recruiter, Applied AI" matched experience[].title word(s) "AI"; content matched no skill; title has no management word; location: San Francisco, CA | New York City, NY (not used); failed: skills test
- Judgment (Claude): none: Claude budget used up

**greenhouse:anthropic — Recruiter, GTM** (`5366882008`, San Francisco, CA | New York City, NY)

- Record (rule): not relevant. title "Recruiter, GTM" matched no experience[].title word; content matched no skill; title has no management word; location: San Francisco, CA | New York City, NY (not used); failed: title test, skills test
- Judgment (Claude): none: Claude budget used up

**greenhouse:anthropic — Recruiter, GTM  - Seoul** (`5473862008`, Seoul, South Korea)

- Record (rule): not relevant. title "Recruiter, GTM  - Seoul" matched no experience[].title word; content matched no skill; title has no management word; location: Seoul, South Korea (not used); failed: title test, skills test
- Judgment (Claude): none: Claude budget used up

**greenhouse:anthropic — Recruiter, GTM - Singapore** (`5470680008`, Singapore)

- Record (rule): not relevant. title "Recruiter, GTM - Singapore" matched no experience[].title word; content matched no skill; title has no management word; location: Singapore (not used); failed: title test, skills test
- Judgment (Claude): none: Claude budget used up

**greenhouse:anthropic — Regional Research Economist, Economic Research** (`5460524008`, Bangalore, India)

- Record (rule): not relevant. title "Regional Research Economist, Economic Research" matched no experience[].title word; content matched skills: Python, SQL; title has no management word; location: Bangalore, India (not used); failed: title test
- Judgment (Claude): none: Claude budget used up

**greenhouse:anthropic — Research Engineer, Cybersecurity RL (Reinforcement Learning)** (`5463598008`, San Francisco, CA | New York City, NY)

- Record (rule): not relevant. title "Research Engineer, Cybersecurity RL (Reinforcement Learning)" matched experience[].title word(s) "Engineer"; content matched no skill; title has no management word; location: San Francisco, CA | New York City, NY (not used); failed: skills test
- Judgment (Claude): none: Claude budget used up

**greenhouse:anthropic — Research Engineer / Scientist, Pre-training** (`5468947008`, Remote-Friendly (Travel-Required) | San Francisco, CA | Seattle, WA | New York City, NY)

- Record (rule): relevant. title "Research Engineer / Scientist, Pre-training" matched experience[].title word(s) "Engineer"; content matched skills: Python; title has no management word; location: Remote-Friendly (Travel-Required) | San Francisco, CA | Seattle, WA | New York City, NY (not used)
- Judgment (Claude): none: Claude budget used up

**greenhouse:anthropic — Research Product Manager, Labs** (`5096878008`, San Francisco, CA | New York City, NY)

- Record (rule): not relevant. title "Research Product Manager, Labs" matched no experience[].title word; content matched no skill; title contains management word(s): "Manager"; location: San Francisco, CA | New York City, NY (not used); failed: title test, skills test, management test
- Judgment (Claude): none: Claude budget used up

**greenhouse:anthropic — Research Scientist, Discovery (Engineering & Applied Sciences)** (`5468937008`, San Francisco, CA)

- Record (rule): relevant. title "Research Scientist, Discovery (Engineering & Applied Sciences)" matched experience[].title word(s) "Engineering"; content matched skills: Python; title has no management word; location: San Francisco, CA (not used)
- Judgment (Claude): none: Claude budget used up

**greenhouse:anthropic — Scaled Account Manager, Beneficial Deployments** (`5473216008`, San Francisco, CA | New York City, NY)

- Record (rule): not relevant. title "Scaled Account Manager, Beneficial Deployments" matched no experience[].title word; content matched no skill; title contains management word(s): "Manager"; location: San Francisco, CA | New York City, NY (not used); failed: title test, skills test, management test
- Judgment (Claude): none: Claude budget used up

**greenhouse:anthropic — Senior Data Center Pre-Construction and Capacity Delivery Manager, EMEA** (`5469367008`, London, UK)

- Record (rule): not relevant. title "Senior Data Center Pre-Construction and Capacity Delivery Manager, EMEA" matched no experience[].title word; content matched no skill; title contains management word(s): "Manager"; location: London, UK (not used); failed: title test, skills test, management test
- Judgment (Claude): none: Claude budget used up

**greenhouse:anthropic — Staff+ Software Engineer, Platform Intelligence** (`5472201008`, San Francisco, CA | New York City, NY)

- Record (rule): relevant. title "Staff+ Software Engineer, Platform Intelligence" matched experience[].title word(s) "Engineer"; content matched skills: AWS; title has no management word; location: San Francisco, CA | New York City, NY (not used)
- Judgment (Claude): none: Claude budget used up

**greenhouse:anthropic — Staff+ Software Engineer, STEM** (`5468901008`, San Francisco, CA | New York City, NY | Seattle, WA)

- Record (rule): not relevant. title "Staff+ Software Engineer, STEM" matched experience[].title word(s) "Engineer"; content matched no skill; title has no management word; location: San Francisco, CA | New York City, NY | Seattle, WA (not used); failed: skills test
- Judgment (Claude): none: Claude budget used up

**greenhouse:anthropic — Strategic Partner Development, Product Partnerships** (`5475830008`, San Francisco, CA | New York City, NY)

- Record (rule): not relevant. title "Strategic Partner Development, Product Partnerships" matched no experience[].title word; content matched no skill; title has no management word; location: San Francisco, CA | New York City, NY (not used); failed: title test, skills test
- Judgment (Claude): none: Claude budget used up

**greenhouse:anthropic — Technical CBRN-E  Threat Investigator** (`5066997008`, San Francisco, CA | New York City, NY | Washington, DC)

- Record (rule): not relevant. title "Technical CBRN-E  Threat Investigator" matched no experience[].title word; content matched skills: Python, SQL; title has no management word; location: San Francisco, CA | New York City, NY | Washington, DC (not used); failed: title test
- Judgment (Claude): none: Claude budget used up

**greenhouse:anthropic — Technical Deployment Lead** (`5467153008`, Paris, France)

- Record (rule): not relevant. title "Technical Deployment Lead" matched no experience[].title word; content matched no skill; title has no management word; location: Paris, France (not used); failed: title test, skills test
- Judgment (Claude): none: Claude budget used up

**greenhouse:anthropic — Technical Deployment Lead** (`5467159008`, Munich, Germany)

- Record (rule): not relevant. title "Technical Deployment Lead" matched no experience[].title word; content matched no skill; title has no management word; location: Munich, Germany (not used); failed: title test, skills test
- Judgment (Claude): none: Claude budget used up

**greenhouse:anthropic — Web Design Manager** (`5472952008`, San Francisco, CA | New York City, NY)

- Record (rule): not relevant. title "Web Design Manager" matched no experience[].title word; content matched no skill; title contains management word(s): "Manager"; location: San Francisco, CA | New York City, NY (not used); failed: title test, skills test, management test
- Judgment (Claude): none: Claude budget used up

**ashby:notion — Solutions Consultant, Mid Market, MEA (Middle East Africa)** (`499cda6b-522b-4596-8a4c-30efbb1e6b2a`, Dublin, Ireland)

- Record (rule): not relevant. title "Solutions Consultant, Mid Market, MEA (Middle East Africa)" matched no experience[].title word; content matched no skill; title has no management word; location: Dublin, Ireland (not used); failed: title test, skills test
- Judgment (Claude): none: Claude budget used up

**ashby:notion — Solutions Consultant, Mid-Market, France** (`14c52e6b-b00b-42b5-96fb-195919ef6bab`, Paris, France)

- Record (rule): not relevant. title "Solutions Consultant, Mid-Market, France" matched no experience[].title word; content matched no skill; title has no management word; location: Paris, France (not used); failed: title test, skills test
- Judgment (Claude): none: Claude budget used up

**ashby:notion — Solutions Consultant, Mid-Market, Benelux** (`9392cc22-547f-4089-8677-54f0d80c77a6`, Dublin, Ireland)

- Record (rule): not relevant. title "Solutions Consultant, Mid-Market, Benelux" matched no experience[].title word; content matched no skill; title has no management word; location: Dublin, Ireland (not used); failed: title test, skills test
- Judgment (Claude): none: Claude budget used up

**ashby:notion — Technical Program Manager, EPD** (`73b0e05e-317f-4f84-8fb2-58dc8c3790a6`, San Francisco, California)

- Record (rule): not relevant. title "Technical Program Manager, EPD" matched no experience[].title word; content matched no skill; title contains management word(s): "Manager"; location: San Francisco, California (not used); failed: title test, skills test, management test
- Judgment (Claude): none: Claude budget used up

**ashby:notion — Onboarding Enablement Manager, APAC** (`a356be47-4b45-41c8-9fc9-9e3754d337bc`, Tokyo, Japan)

- Record (rule): not relevant. title "Onboarding Enablement Manager, APAC" matched no experience[].title word; content matched no skill; title contains management word(s): "Manager"; location: Tokyo, Japan (not used); failed: title test, skills test, management test
- Judgment (Claude): none: Claude budget used up

**ashby:notion — Manager, Commercial Outcome Architects (Customer Success)** (`82819e88-adf1-4ab6-a9d1-e091cc3330d2`, New York, New York)

- Record (rule): not relevant. title "Manager, Commercial Outcome Architects (Customer Success)" matched no experience[].title word; content matched no skill; title contains management word(s): "Manager"; location: New York, New York (not used); failed: title test, skills test, management test
- Judgment (Claude): none: Claude budget used up

**ashby:notion — Software Engineer, Growth** (`f524ef6b-6a8a-4d73-b7ff-eac85bd6c887`, San Francisco, California)

- Record (rule): not relevant. title "Software Engineer, Growth" matched experience[].title word(s) "Engineer"; content matched no skill; title has no management word; location: San Francisco, California (not used); failed: skills test
- Judgment (Claude): none: Claude budget used up

**ashby:notion — Solutions Consultant, Commercial, CEE** (`5a7fce72-6fbd-4ccd-b559-db5ca2578361`, Dublin, Ireland)

- Record (rule): not relevant. title "Solutions Consultant, Commercial, CEE" matched no experience[].title word; content matched no skill; title has no management word; location: Dublin, Ireland (not used); failed: title test, skills test
- Judgment (Claude): none: Claude budget used up

**ashby:notion — Solutions Consultant, Commercial, DACH** (`6c53f83d-c1c2-4e62-bb4a-8532838409da`, Dublin, Ireland)

- Record (rule): not relevant. title "Solutions Consultant, Commercial, DACH" matched no experience[].title word; content matched no skill; title has no management word; location: Dublin, Ireland (not used); failed: title test, skills test
- Judgment (Claude): none: Claude budget used up

**ashby:notion — Solutions Consultant, Mid-Market, DACH** (`021f4891-c95f-41de-b8fc-66d285f57851`, Munich, Germany)

- Record (rule): not relevant. title "Solutions Consultant, Mid-Market, DACH" matched no experience[].title word; content matched no skill; title has no management word; location: Munich, Germany (not used); failed: title test, skills test
- Judgment (Claude): none: Claude budget used up

**ashby:notion — Software Engineering Intern, Frontend (Summer 2027)** (`43ffba97-b64a-4c6a-ac13-c803253c9413`, New York, New York)

- Record (rule): not relevant. title "Software Engineering Intern, Frontend (Summer 2027)" matched experience[].title word(s) "Engineering"; content matched no skill; title has no management word; location: New York, New York (not used); failed: skills test
- Judgment (Claude): none: Claude budget used up

**ashby:notion — Software Engineering Intern, iOS (Summer 2027)** (`27090d0f-07d3-419b-adaa-837b5e22f947`, New York, New York)

- Record (rule): relevant. title "Software Engineering Intern, iOS (Summer 2027)" matched experience[].title word(s) "Engineering"; content matched skills: Python; title has no management word; location: New York, New York (not used)
- Judgment (Claude): none: Claude budget used up

**ashby:notion — Solutions Consultant, Enterprise, Nordics** (`3038ee95-ed44-49a5-9808-1382c4e6cfe9`, Dublin, Ireland)

- Record (rule): not relevant. title "Solutions Consultant, Enterprise, Nordics" matched no experience[].title word; content matched no skill; title has no management word; location: Dublin, Ireland (not used); failed: title test, skills test
- Judgment (Claude): none: Claude budget used up

**ashby:notion — Solutions Consultant, Mid-Market, CEE** (`d6298237-6607-4d2b-956b-1ca6b20a12c4`, Dublin, Ireland)

- Record (rule): not relevant. title "Solutions Consultant, Mid-Market, CEE" matched no experience[].title word; content matched no skill; title has no management word; location: Dublin, Ireland (not used); failed: title test, skills test
- Judgment (Claude): none: Claude budget used up

**ashby:notion — Business Development Representative, MEDIT** (`11ea8ad6-b380-4041-a4cc-40eeccddffef`, Dublin, Ireland)

- Record (rule): not relevant. title "Business Development Representative, MEDIT" matched no experience[].title word; content matched no skill; title has no management word; location: Dublin, Ireland (not used); failed: title test, skills test
- Judgment (Claude): none: Claude budget used up

**ashby:notion — Solutions Consultant, Enterprise, Medit** (`8109628c-ff17-4e90-b388-d159dc1c53ca`, Dublin, Ireland)

- Record (rule): not relevant. title "Solutions Consultant, Enterprise, Medit" matched no experience[].title word; content matched no skill; title has no management word; location: Dublin, Ireland (not used); failed: title test, skills test
- Judgment (Claude): none: Claude budget used up

**ashby:notion — Solutions Consultant, Commercial, MEA (Middle East Africa)** (`10760f33-dd07-4343-ad30-3f26db7f8eee`, Dublin, Ireland)

- Record (rule): not relevant. title "Solutions Consultant, Commercial, MEA (Middle East Africa)" matched no experience[].title word; content matched no skill; title has no management word; location: Dublin, Ireland (not used); failed: title test, skills test
- Judgment (Claude): none: Claude budget used up

**ashby:notion — Business Development Representative, Nordics** (`a13fa271-f819-4421-b5fa-a9777672758e`, Dublin, Ireland)

- Record (rule): not relevant. title "Business Development Representative, Nordics" matched no experience[].title word; content matched no skill; title has no management word; location: Dublin, Ireland (not used); failed: title test, skills test
- Judgment (Claude): none: Claude budget used up

**ashby:perplexity — Content Designer** (`0807f77b-4499-498a-b2bf-3cd44d965138`, San Francisco)

- Record (rule): not relevant. title "Content Designer" matched no experience[].title word; content matched no skill; title has no management word; location: San Francisco (not used); failed: title test, skills test
- Judgment (Claude): none: Claude budget used up

**ashby:perplexity — Member of Technical Staff (GTM Engineer, Growth)** (`3b523d3a-23bd-4887-8e3c-239d14d66b06`, San Francisco)

- Record (rule): relevant. title "Member of Technical Staff (GTM Engineer, Growth)" matched experience[].title word(s) "Engineer"; content matched skills: Python, SQL, AWS; title has no management word; location: San Francisco (not used)
- Judgment (Claude): none: Claude budget used up

**ashby:perplexity — University Recruiter** (`9ffca709-f4e1-40e7-81bf-270ff73c7a50`, San Francisco)

- Record (rule): not relevant. title "University Recruiter" matched no experience[].title word; content matched no skill; title has no management word; location: San Francisco (not used); failed: title test, skills test
- Judgment (Claude): none: Claude budget used up

**ashby:perplexity — Counsel, Product** (`5930b6bf-b4b1-4134-a183-832d69dd085f`, San Francisco)

- Record (rule): not relevant. title "Counsel, Product" matched no experience[].title word; content matched no skill; title has no management word; location: San Francisco (not used); failed: title test, skills test
- Judgment (Claude): none: Claude budget used up

**ashby:perplexity — Member of Technical Staff (Software Engineer, AI Policy and Strategic Initiatives)** (`1056951e-8a42-4330-b72c-90162b3cd1c9`, San Francisco)

- Record (rule): not relevant. title "Member of Technical Staff (Software Engineer, AI Policy and Strategic Initiatives)" matched experience[].title word(s) "AI", "Engineer"; content matched no skill; title has no management word; location: San Francisco (not used); failed: skills test
- Judgment (Claude): none: Claude budget used up

