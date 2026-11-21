# FACTCHECK: Klaxon Final Project Film

Every narrated claim in SCRIPT.md (and every number on a card Claude Code writes), checked on 2026-11-20 by Claude
Code against Klaxon's public `main` (`fef450b`, the same commit as GitHub's `main`, checked with `gh api` on
2026-11-20) or a web page read that day. Verdicts: PASS (supported as written), CORRECTED (the draft was wrong or
too strong; the fix is in SCRIPT.md), EXEMPT (a stated plan or criterion, not a result). The rows are Claude Code's checks;
Aravind approved the finished film with no changes on 2026-11-22.

Status: 66 rows; 58 PASS, 6 CORRECTED, 2 EXEMPT. Footage numbers (panel screenshots, report tables, CI page) come
straight from the records they show.

| # | Beat | Claim | Verdict | Source | Fix |
|---|---|---|---|---|---|
| 1 | B01 | "this is a synthetic voice reading the script" | PASS | Kokoro `am_onyx` voice, as in the pitch film (PR #13, commit `8164179`, first line "this is a synthetic voice reading my pitch") | Disclosure, kept. "my script" changed to "the script" (2026-11-20): Claude Code drafted it from the record |
| 2 | B01 | "my final project, Klaxon" | PASS | README.md@fef450b: "a final project for two Northeastern University courses (CSYE 7374 ... and INFO 7375 ...)" | |
| 3 | B02 | "an AI on-call engineer for a payments system" | PASS | README.md@fef450b, line 2 | |
| 4 | B02 | "works out what went wrong, shows its evidence" | PASS | README.md@fef450b: a diagnosis "that cites its evidence"; contract.py | |
| 5 | B02 | "asks a person before changing anything" | PASS | README.md@fef450b: "every action that changes something needs a person's approval"; gate.py | |
| 6 | B02 | "checks ... whether the money is right" | PASS | README.md@fef450b: verify.py, a money check right after the action and one a minute later | |
| 7 | B03 | "a bad deploy made the ledger count some payments more than once" | PASS | evidence/week7/2026-11-17T042300Z_gated-run_duplicate-delivery (panel screenshot `4-verified.png`): evt_000308 booked three times, "six other events, five charges and one refund, were booked twice" | The 7 events are 6 charges and 1 refund; "some payments" covers the charges |
| 8 | B03 | "The other alert rules stayed quiet" | PASS | Same run, panel card "Signals at the alert": latency p95 0.027 s, 5xx share 3.4%, both consumer lags 0, books settled, all green; only MoneyCheckFailed red | |
| 9 | B03 | "our books were $461 ahead of the payment provider's" | PASS | Same run's alert text (`2-waiting-for-approval.png`): "our ledger is $461.00 ahead of the provider's balance" | |
| 10 | B04 | "while the books are still wrong" | CORRECTED | Klaxon's own wording decision: in this fault the provider charged once, so only our books are wrong ("counted twice", never "double charge") | Draft said "customers' money is still wrong" |
| 11 | B04 | "a fix isn't done until the money is checked" | PASS | README.md@fef450b, verify.py | |
| 12 | B05 | "The industry calls this an AI SRE" | PASS | TechCrunch headline 2026-02-04 ("AI SRE Resolve AI confirms..."); traversal.com/blog/launch-announcement ("the AI SRE for the Enterprise"); both read 2026-11-20 | |
| 13 | B05 | "Resolve AI raised $125 million at a $1 billion valuation in February" | PASS | https://techcrunch.com/2026/02/04/ai-sre-resolve-ai-confirms-125m-raise-unicorn-valuation/ (read 2026-11-20): "a $125 million Series A at a $1 billion valuation" | |
| 14 | B05 | "Traversal $120 million in November" | PASS | https://www.goodwinlaw.com/en/news-and-events/news/2026/11/announcements-technology-goodwin-advises-traversal-120-million-series-b (2026-11-04); Dealroom 2026-11-03; both read 2026-11-20 | The $1 billion valuation is only in secondary reports: not narrated |
| 15 | B05 | "Datadog, AWS and Microsoft now offer their own" | PASS | Datadog press release 2025-12-02 (Bits AI SRE); https://aws.amazon.com/about-aws/whats-new/2026/03/aws-devops-agent-generally-available/ (2026-03-31); Microsoft Tech Community post 2026-03-10 (Azure SRE Agent GA); all read 2026-11-20 | |
| 16 | B06 | "Microsoft says its agent has mitigated over 35,000 incidents in its own services" | PASS | https://techcommunity.microsoft.com/blog/appsonazureblog/announcing-general-availability-for-the-azure-sre-agent/4500682 (read 2026-11-20): "1,300+ agents deployed, 35,000+ incidents mitigated" across its own services | A vendor's own claim, so the narration says "says" |
| 17 | B06 | "agents on state-of-the-art models resolved only 11.4% of its SRE scenarios" | CORRECTED | https://proceedings.mlr.press/v267/jha25a.html (ITBench, ICML 2025, read 2026-11-20): "agents powered by state-of-the-art models resolve only 11.4% of SRE scenarios" | RESEARCH.md (10/9) paraphrased it as "the best agents"; now the paper's wording |
| 18 | B07 | "The open-source agent I looked at, HolmesGPT" | PASS | Aravind read its README and deployment-verification page on 2026-10-09 (his answer, recorded then); CNCF blog 2026-01-07: "accepted as a CNCF Sandbox project in October 2025" (on screen) | Aravind to confirm (OPEN-QUESTIONS 1) |
| 19 | B07 | "can check a deploy by asking a model to compare error rates, latency, restarts and logs" | PASS | https://holmesgpt.dev/latest/operator/deployment-verification/ (read 2026-11-20), its example query: "Compare error rates, latency, restarts, and logs before vs after the rollout and flag any regressions." | |
| 20 | B07 | "In its docs, I didn't find a built-in check that the money is right" | PASS | His 10/09 reading and Claude Code's 11/20 reading of that page; RESEARCH.md's rule: say "we did not find", never "it has none" | Scoped to its docs, as the rule says |
| 21 | B08 | "Klaxon is a small copy of this idea" | PASS | README.md@fef450b ("in an early form"); the 10/9 pivot to replicate the AI SRE category at small scale | |
| 22 | B08 | "after a fix, code, not the model, checks the money" | PASS | README.md@fef450b: "verification after an action that ran, by code, not the model" | |
| 23 | B08 | "Klaxon changes nothing until a person approves it" | PASS | README.md@fef450b, gate.py; the faults are injected by the harness, not by Klaxon | |
| 24 | B09 | "It all runs on synthetic data" | PASS | README.md@fef450b: "All data is synthetic, and the payment provider is a simulator" | |
| 25 | B09 | "an API, a fake provider that sends signed webhooks, Kafka, and a double-entry ledger ... in Docker on my Mac" | PASS | README.md@fef450b, "The patient" (HMAC-signed webhooks, at least once, with retries; Docker Compose) | |
| 26 | B09 | "Simulated customers make payments" | PASS | README.md@fef450b, traffic.py ("synthetic customers") | |
| 27 | B09 | "six faults with known causes are injected on purpose" | PASS | README.md@fef450b, faults.py | |
| 28 | B10 | "asks Claude for one step at a time: call one of eight read-only tools ... or give a diagnosis" | PASS | README.md@fef450b, loop.py and tools.py (eight tools) | |
| 29 | B10 | "served by an MCP server written from scratch" | PASS | README.md@fef450b, mcp_server.py | |
| 30 | B10 | "a diagnosis that cites the tool calls behind it" | CORRECTED | README.md@fef450b, contract.py: "evidence citing the tool calls of this run by id" | Draft said "every claim must cite"; the contract cites per evidence item |
| 31 | B11 | "a real run from week seven" | CORRECTED | STATUS.md@fef450b, week 7 item 2: folder 2026-11-17T042300Z is UTC, which was Mon 11/16, 11:23 PM in Boston | Draft said "from November 17th" |
| 32 | B11 | "in 25 seconds and three tool calls, Klaxon found the cause" | PASS | STATUS.md@fef450b: "diagnosed in 4 steps and 3 tool calls (25.4 s) ... by the rule it names the cause"; panel: 25.412 s, 3 of 8 tool calls | "Found" = the grading rule's verdict plus the diagnosis text |
| 33 | B11 | "a ledger deploy that books every message without checking for duplicates" | PASS | The run's diagnosis: "This handler books every Kafka message it receives and never checks whether that event_id was already posted." | |
| 34 | B11 | "It asked to roll that deploy back" | PASS | Request r-33b5, rollback_deploy on ledger-consumer (panel; STATUS week 7) | |
| 35 | B12 | "I approved it by typing its id in my own terminal, 70 seconds later" | PASS | STATUS.md@fef450b: request at 04:25:01 UTC, "he approved it at his terminal at 04:26:11, 70 s later"; gate trail "approved typed at a terminal" | |
| 36 | B12 | "healthy, cause removed, but the money still wrong" | PASS | STATUS.md@fef450b: "Verification passed: healthy, the cause removed, the money not right (20 events counted more than once; our books $1,178.22 ahead of the provider's)" | |
| 37 | B12 | "because a rollback repairs nothing" | PASS | The run's verification text: "A rollback repairs nothing: this damage stays until a person repairs it." | |
| 38 | B12 (screen) | Events counted more than once: 7 at the alert, 9 at the request, 20 at the action | PASS | STATUS.md@fef450b, week 7 item 2; panel verification table | On screen only |
| 39 | B13 | "Weeks one to seven are built and public" | PASS | STATUS.md@fef450b ("Weeks 1 to 7 are done"); GitHub main = fef450b (gh api, 2026-11-20); CI on main passed (run 44188797067) | |
| 40 | B13 (screen) | Built: a LangGraph version, Kubernetes (kind), a web panel, CI on GitHub | PASS | README.md@fef450b, weeks 6 and 7 | On screen only |
| 41 | B13 | "Planned by December 4th: a multi-agent version, the webhook receiver in Go, a 72-run comparison of the loops, and a safety pass" | PASS | PLAN.md@fef450b, "The schedule to Dec 4" (multi-agent, the Go service, comparison runs; week 9 safety pass); the week 8 plan `9cfc249` (branch claude/week-8-plan, not merged to main on 2026-11-20): the Go service is the webhook receiver; 72 runs = 3 loops x 8 cases x 3 seeds | Said as a plan. Items 1 and 2 are being built on unreviewed branches (`731e670`, `77318a6`); the film does not claim them |
| 42 | B13 | OpenHands on a local model (the directive listed it under resources) | CORRECTED | `9cfc249`: OpenHands runs on qwen3:8b, "Its model is not Claude, so its runs stay out of INFO 7375's materials" | Left out of this INFO film (OPEN-QUESTIONS 2) |
| 43 | B14 | "There is no API key and no token credits" | PASS | README.md@fef450b (Claude Code headless on his seat); STATUS.md@fef450b, week 6 item 2 ("Claude Code on his seat ... so no API key is needed"); he bought no API credit (his answer, 2026-10-22) | |
| 44 | B14 | "every call goes through my university's Claude seat, using Claude Code in headless mode" | PASS | README.md@fef450b, model.py and claude_code.py: "Claude through Claude Code in headless mode (claude -p) on Aravind's university seat" | |
| 45 | B14 | "It isn't billed per call, but it has usage limits, so big batches run overnight" | PASS | STATUS.md@fef450b ("The seat is not billed per call, but it has usage limits"; week 5's 40 runs ran 05:57 to 08:49 UTC); `9cfc249` ("one night") | |
| 46 | B14 | "Dollar figures are estimates at API prices, not money spent" | PASS | STATUS.md@fef450b ("Claude Code's estimate at API prices"); `9cfc249` ("none of it is charged to him") | |
| 47 | B14 | "Compute is my Mac and GitHub's free CI" | PASS | README.md@fef450b (Docker Desktop, kind); STATUS week 7 item 3 ("GitHub Actions, free for public repositories on GitHub's standard machines") | |
| 48 | B15 | "I made the decisions" | PASS | DECISIONS.md@fef450b records his decisions for every week (e.g. the week 7 plan's four) | Many were picks among options Claude Code laid out; the sentence stays true |
| 49 | B15 | "reviewed and accepted every week" | PASS | STATUS.md and README.md@fef450b: weeks 1 to 7 each reviewed and accepted by him, with dates | |
| 50 | B15 | "typed every approval myself" | PASS | gate.py (only the request's id, typed at a terminal, approves); every approved request in STATUS (weeks 4, 6, 7) was his | |
| 51 | B15 | "Claude Code wrote the code under my direction" | PASS | Aravind's answer, 2026-11-20: he wrote none of Klaxon's code ("No, Claude Code wrote it"); README.md@fef450b, line 4, says "Claude Code writing most of the code under his direction" | The course's AI-use line. Changed from "most of the code" on 2026-11-20 at his answer; the README's "most" is the more cautious wording of the same fact |
| 52 | B16 | "Eight test cases, each with its right answer written before any run" | PASS | README.md@fef450b, evaluation.py; STATUS week 5 item 1 ("each right answer committed before any run on it") | |
| 53 | B16 | "the six faults, a false alarm, and a fault where the tools can't see the deploys" | PASS | Same: false-alarm; missing-deploys = fault 1 with docker withheld from recent_deploys and service_health | |
| 54 | B17 | "A keyword rule written in advance" | PASS | README.md@fef450b, grading.py ("committed before the first live runs") | |
| 55 | B17 | "a Claude judge that never sees which model wrote it" | PASS | README.md@fef450b, judge.py ("never the model that wrote it or the rule's verdict") | |
| 56 | B17 | "checked against my own blind labels" | PASS | STATUS.md@fef450b: `make label`, blind, typed at his terminal (17 runs on 2026-11-08, 4 on 11-12, 6 on 11-15) | |
| 57 | B17 | "Did it name an action only where one fits?" | PASS | evidence/week5/report.md@fef450b, columns "Action right" and "Named where none fits" | |
| 58 | B17 | "when I approve an action, does code find the system healthy and the money right?" | PASS | verify.py; the gated runs of weeks 4, 6 and 7 | |
| 59 | B18 | "48 runs on two Claude models" | PASS | evidence/week5/report.md@fef450b: 24 on claude-opus-5-5, 24 on claude-sonnet-5-5 | |
| 60 | B18 | "Opus named the cause in all 18 of its fault runs, by both graders" | PASS | Same report: the six fault rows each "3 of 3" by the rule and by the judge; STATUS: "on faults 1 to 6, Opus 18 of 18 by both" | |
| 61 | B18 | "No run named an action where none fits" | PASS | Same report: "Named where none fits" is 0 in all 16 rows; README status line | |
| 62 | B19 | "on the false alarm, no run named an action" | CORRECTED | Same report: false-alarm "Action right 3 of 3" on both models | Draft said "took an action", which is always true in evaluation mode (nothing runs there) |
| 63 | B19 | "each grader found only one run in six that said plainly that nothing was wrong" | PASS | Same report: false alarm, Opus 1 of 3 by the rule and 1 of 3 by the judge; Sonnet 0 and 0 | He labeled 3 of those runs "names the cause", so the graders were stricter than him; week 6's re-run with a 5-minute warm-up: still 1 of 6 by the rule |
| 64 | B19 | "every fault was known while I built Klaxon, so this is not yet a test on faults it has never seen" | PASS | STATUS.md@fef450b, week 5: "a held-out fault (every fault so far was known while Klaxon's prompt, tools and alert rules were built)"; week 7: still not done | OPEN-QUESTIONS 3 |
| 65 | B20 | "the 72 comparison runs" | EXEMPT | `9cfc249` plan | A plan, said as one |
| 66 | B20 | Works if / fails if | EXEMPT | Success criteria written for this film | Criteria, not results |

## Checked and left out

- Resolve AI at a $1.5 billion valuation (April 2026): only secondary reports (Beri, Doolpa); not used.
- Traversal's $1 billion valuation: secondary (Dealroom); not narrated. Its earlier $48M seed and Series A (traversal.com launch post, read 2026-11-20) is true but not needed.
- New Relic SRE agent and Cleric (RESEARCH.md, 10/9): not re-checked, not used.
- Week 8 work in progress (multi-agent loop `731e670`, Go receiver `77318a6`): unreviewed, unmerged; not claimed.
- Any claim from his co-op: not used in this film.
