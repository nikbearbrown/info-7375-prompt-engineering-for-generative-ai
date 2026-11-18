# PROJECT-BRIEF — CheckedSQL

Siddhesh Nikam · INFO 7375 · Fall 2026 · Target role: Data Analyst (marketing analytics) · v2, 2026-10-24

## 1. What is it?

CheckedSQL will let a marketing analyst ask a campaign question in plain English, have Claude write the SQL, run it, and show the answer beside its query, scored against an answer key. When done, it will be a **GitHub repository** (Python, SQLite, Claude API) with a synthetic campaign dataset, the question tool, a test set of about 30 questions, and an evaluation log with a failure write-up. The first piece already runs: `checkedsql/`, the dataset, 10 questions, an answer key and a checker.

## 2. Why would anyone care?

It stops an analyst from trusting a number they can't check. Two real alternatives:
- **A fixed dashboard (Tableau).** My earlier marketing project links one, made with AI help (v1 of this brief wrongly said I built it). It answers only the questions planned in advance.
- **A general chat assistant. Tested 2026-10-24:** I gave ChatGPT `campaigns.csv` and asked which channel had the highest ROAS. It answered **Search, 3.98×**, which matches my key (`build/chat_test_full.png`). It was right, but that was one answer to one question: no record of its hit rate across my questions, and I couldn't see its query.

CheckedSQL's difference: every answer is run, shown with its query, scored against a fixed key, and logged.

## 3. Who opens it, and what do they do with it?

A **hiring manager** for a data-analyst role. In the first sixty seconds: open the README, see the score table, run one command. Today `python3 checker.py` prints the baseline table (10/10); later the same command will score Claude's queries.

## 4. What does it prove about me?

That I can get marketing metrics right (CTR, conversion rate, ROAS) and check them against a key, plus three course skills: a **prompt contract**, **verification** against known answers, and a repeatable **evaluation**. Verification and evaluation have evidence now (checker, score table); the contract, evaluation log and failure write-up come next. It will not prove the tool works on other schemas or on real company data.

## 5. What is in, what is out, what comes first?

- **In:** one synthetic campaign schema, read-only questions, the test set, the log.
- **Out:** it never changes the database. The checker already refuses anything but a single SELECT. No dashboards, no real company data.
- **First (done 2026-10-24):** the test set and checker before any Claude call. Ten questions, a key computed without SQL (`HAND-CHECK.md`), baseline SQL drafted with Claude: **10/10**. Two deliberately wrong row-average queries were both **failed**. **Next:** Claude gets the same ten.

## 6. What could sink it?

An answer that looks right but isn't. Averaging Email's eight row ROAS values gives **9.75** and makes Email the best channel; total revenue ÷ total spend gives **2.29**, and the best is **Search (3.98)**. My fix: the metric definition goes in the prompt contract, and the test set has ratio questions (Q06, Q07). The checker already caught the trap on purpose-built wrong queries.

## 7. Why this project?

**Mostly learning.** What I have is the domain: which campaign metrics matter and that a ratio must be total ÷ total. Evidence: I checked the key's ROAS answers on a calculator (FRICTIONAL, 2026-10-24). My earlier repos show that domain, but AI wrote most of their code, so they are not proof of coding skill. **New to me:** writing and checking SQL myself, calling Claude from Python, prompt contracts and evaluation. From here on I write the queries for new test questions myself. **I don't know yet** whether 30 questions is enough; I'll find out by watching whether new questions keep finding new kinds of failure.

---

**Exists today**
- My earlier repos `nikam0420/marketing-campaign-analytics` and `nikam0420/Individual_Siddhesh-Nikam_ExplorataryDataAnalysis` (built with substantial AI help)
- This brief, the beat sheet and the film
- `checkedsql/`: dataset, 10 questions, answer key, 10 baseline queries plus 2 trap queries (drafted with Claude), `checker.py` (10/10, traps caught 2/2)
- My ChatGPT test (2026-10-24)

**Will exist**
- The prompt contract (schema, ROAS = total revenue ÷ total spend, read-only SELECT, output format)
- The Claude step: question → Claude-written SQL → checker
- About 30 test questions
- The evaluation log and the failure write-up
