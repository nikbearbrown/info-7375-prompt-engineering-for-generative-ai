# My research and evaluation answers — Final Project Film

## Executive summary

**What this is:** my own answers to four questions for the film: two existing tools I searched myself, why anyone
should care about my tool, what I need to finish it, and how I will judge it after adding a second data source.
**Why read it:** these are the film's Part 2 (what others have done) and the judgement lines in Parts 3 and 4.
**What it found:** OpenSanctions and GLEIF both hold company information, and GLEIF links SoFi to Social Finance, but
neither is built to find H-1B sponsoring employers.

## Record

Written by Arundhati Kandelkar and sent to Claude on **2026-11-23 at 15:59 EST** (the time she sent them). The searches
were run by me, not Claude. The text below is mine, pasted verbatim; Claude added only this header and the summary above.
The 10-25 USCIS hub search for Capital One was also mine (see `../final-project-film/SOURCES.md`).

---

## Final Project – Research and Evaluation

### 1. What are two existing tools you examined? What did you search, what did you find, and how are they different from your tool?

**Tool 1: OpenSanctions**
Website: https://www.opensanctions.org/
I explored OpenSanctions by searching for Robinhood, SoFi, and Chime.

* Robinhood: It returned multiple related entities, including Robinhood Securities, LLC and Robinhood Financial LLC, along with unrelated results.
* SoFi: It returned SoFi Securities LLC, but also several unrelated people and other entities.
* Chime: It returned 11 results, mostly unrelated individuals. It did not show Chime Financial Inc. in the results I reviewed.

OpenSanctions is mainly designed for sanctions and risk screening. Its search results show how a brand-name search can return multiple related entities or irrelevant matches. It is useful for exploring entity information, but it is not specifically designed to identify H-1B sponsoring employers.

**Tool 2: GLEIF – LEI Search**
Website: https://www.gleif.org/en/lei-search
I searched for Robinhood and SoFi on GLEIF.

* Robinhood: I found ROBINHOOD MARKETS, INC., with an active entity status and an LEI.
* SoFi: I found SOCIAL FINANCE, LLC. GLEIF also listed SOCIAL FINANCE, INC. as a previous legal name.

GLEIF provides legal entity identification information, including legal names, entity status, and Legal Entity Identifiers (LEIs). It was particularly useful for connecting a brand name to its registered legal entity.

**How are these tools different from my project?**
Both tools provide useful company or entity information, but neither is specifically focused on identifying employers that sponsor H-1B visas.
My project focuses on finding and verifying potential sponsoring employers using relevant sources, including the USCIS H-1B employer data. It also addresses the problem of brand names being different from the legal names stored in datasets. The goal is to surface relevant candidates while keeping the final verification with a human rather than automatically selecting a company.

### 2. Why should anyone care about my tool?

Finding companies that sponsor H-1B visas can take time, especially when a company's brand name is different from its legal name in the available datasets. My tool aims to make this process easier by bringing relevant company information together, identifying possible name variations, and allowing users to verify the results instead of blindly trusting an automatic match.

### 3. What resources do I need to finish the project? Will I use an AI model?

I mainly need my laptop, Python, GitHub, and access to the relevant data sources, including the USCIS H-1B employer data.
I may also use Claude or Claude Code as a development assistant while working on the project. However, the core sponsor lookup and name-matching logic can be implemented using Python without requiring an AI model at runtime. I want the matching process to remain predictable and transparent, with human verification for uncertain results.

### 4. What is my pass/fail criteria after adding the USCIS hub as a second source?

Pass criteria:

* The tool can retrieve relevant employer information from both sources.
* It can identify known sponsoring employers, including cases where the brand name differs from the legal company name.
* It displays the source information so users can verify where the results came from.
* It surfaces possible matches for human review rather than automatically choosing a company.
* The results are consistent and can be tested against the evaluation dataset.

Fail criteria:

* The tool misses known employers that should be found in the available data.
* It returns incorrect companies as confirmed matches.
* It cannot show which source supports a result.
* It automatically selects or confirms a company without human verification.
* Adding the second source does not improve the coverage or usefulness of the results.

---

## Added 2026-11-23 19:23 EST — two sharper lines for the film (sent by me)

**3b. Resources (BRES):** I have what I need to build and test this: my laptop, Python, GitHub, the public USCIS data, and Claude Code access through Northeastern. I don't need paid AI credits because the tool doesn't use an AI model at runtime.

**4b. Pass/fail (BBAR):** I'll consider the hub join successful if at least 20 of the 25 companies get a verified match, with zero incorrect automatic sponsor answers. Anything uncertain must remain unknown or go to human review.

(20 of 25 is a proposed target, not a result already achieved.)
