# PROJECT-BRIEF — Cite or Refuse (working title)

**Student:** Swathi Baba Eswarappa · **Target roles:** AI/ML engineer, data engineer
**Status:** pitch only. Nothing in this project has been built yet.



## 1. What is it?
A tax helper for international students that answers questions only from official IRS publications, cites the exact passage and tax year, and refuses when the publications do not cover the question.
When done, it will be a GitHub repository containing: a pipeline that ingests several tax years of IRS publications, treaty data in Postgres, a retrieval system, a rules engine, a small out-of-scope classifier, an MCP server that lets Claude Code use these tools, and an evaluation report.

## 2. Why would anyone care?
Every year, international students must file forms like Form 8843 and work out whether a tax treaty applies to them. The rules are spread across long publications that change every year, and a wrong answer has real consequences.
Alternatives I looked at: on Oct 9, 2026, I asked ChatGPT, Gemini, and Claude the same three questions (Form 8843, the U.S.–India treaty, and whether I would get a refund), each in a fresh chat. This was a small informal test, not a benchmark. All three gave fluent, detailed answers, but none tied each claim to an exact IRS passage for a stated tax year. Gemini cited only third-party sites, including a Canadian tax page. On the refund question, none cleanly declined; two asked for my income or tax documents. ChatGPT gave two different standard deduction figures for tax year 2025 in two runs ($15,750 logged in, $15,000 logged out). The official 2025 Instructions for Form 1040-NR (page 7) list $15,750 for single students eligible under Article 21(2), so one run did not match the official document.
What mine will do differently: every answer will show the exact IRS passage and tax year it came from, the same question will always return the same checked number, and it will refuse questions the publications cannot answer instead of asking for personal financial data.

## 3. Who opens it, and what do they do?
A hiring manager or engineer reviewing me for an AI/ML or data engineering role. In the first sixty seconds they will open the README, run one command, ask a tax question and see a cited answer with its tax year, ask an out-of-scope question and see a refusal, and look at the evaluation scoreboard.

## 4. What does it prove about me?
That I can build an AI system whose output can be checked, using the mechanisms this course teaches: prompt contracts, source grounding, a bounded agent loop, read-only tool permissions, lexical retrieval, an MCP server, a small trained classifier, verification kept separate from generation, a human approval gate, and held-out evaluation.
Evidence will be the tests, the evaluation report (correct answers, wrong answers, correct refusals), and a log of cases where the system was wrong and how I caught it.

## 5. What is in, out, and first?
**Out:** it will not give personal tax advice, and it will not prepare or file returns.
**First:** ingest one tax year of one IRS publication and run ten held-out questions through lexical retrieval. Someone will know it ran because the tests pass on a fresh clone and the evaluation report shows which questions retrieved the correct section.

## 6. What could sink it?
Extracting tables and sections from IRS documents may be unreliable, and an extraction error would make a "verified" number wrong. I will start with one publication, check a sample of extracted values against the source by hand, and mark anything unchecked as unverified rather than trusted.

## 7. Why this project?
As an international student, I know how confusing these rules are, and most of us have no easy way to check what applies to us. My fintech co-op work with loan data also taught me that numbers people rely on need validation.
It is a mix of learning and showing off.
**New to me:** MCP servers, retrieval evaluation, rules engines combined with AI, training a classifier from scratch, approval gates.
**Already have:** Python data processing, data cleaning, and testing. Evidence: my Reallocation Engine pull request for this course (https://github.com/nikbearbrown/the-reallocation-engine/pull/6), a Python prototype over 30,000+ rows with a 67-check offline test suite. SQL and database pipelines come from my co-op and TA work, which aren't publicly viewable.

## Exists today
- This brief
- TEST-NOTES.md: dated notes from testing ChatGPT, Gemini, and Claude on Oct 9, 2026
- A check of the 2025 Instructions for Form 1040-NR (page 7 and pages 20–21) against the chatbot answers

## Will exist
- Ingestion pipeline for several tax years, with year-to-year change tracking
- Treaty data in Postgres
- Lexical + vector retrieval, compared on the evaluation set
- Rules engine for questions with exact answers
- Out-of-scope classifier
- MCP server used by Claude Code
- Human approval gate for new tax-year data
- Held-out evaluation running in CI
