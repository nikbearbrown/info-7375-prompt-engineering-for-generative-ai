# What moves the score: results (generated)

Generated 2026-11-17T17:18:41Z by `python3 -m js3.experiments report`. Batch 1 lock 2026-11-17T06:33:35Z (sha256 of prompt P1, the 3 batch-1 filter files, labels, persona and scorer/textutil/mcp_server code; the runner refuses to make new runs for a batch whose locked files changed). Files changed after lock 1: `js3/scorer.py`, `js3/textutil.py`, `js3/mcp_server.py`. Batch-1 results were all produced before those changes (see asked_utc / computed_utc). Batch 2 lock 2026-11-17T06:38:27Z; unchanged since. F0 recomputed under batch-2 code: identical to batch 1. Model claude-sonnet-5-5 through `claude -p`, one fresh session per call, no session persistence, no settings files. Held-out set: Omkar's 20 JS1 labels (11 relevant, 9 not_relevant).

| Cond | One change vs baseline | Answered | Correct (of answered) | Abstained | FP | FN | Verdicts changed vs baseline | Invalid |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| F0 | filter v1.4 as in force | 20/20 | 10/20 | 0 | 0 | 10 | — | 0 |
| E1 | filter file: T3 seniority -2.0 → 0.0 | 20/20 | 11/20 | 0 | 0 | 9 | 1 | 0 |
| E2 | setting: threshold 5.0 → 4.0 | 20/20 | 11/20 | 0 | 0 | 9 | 1 | 0 |
| C0 | Claude P1, posting only, no tools | 20/20 | 10/20 | 0 | 0 | 10 | — | 0 |
| C0b | nothing changed (fresh sessions): the noise floor | 20/20 | 10/20 | 0 | 0 | 10 | 0 | 0 |
| E3 | prompt: + one abstention instruction | 17/20 | 10/17 | 3 | 0 | 7 | 3 | 0 |
| E4 | context: + the filter's result | 20/20 | 10/20 | 0 | 0 | 10 | 0 | 0 |
| E5 | tool list: + score_posting offered | 20/20 | 10/20 | 0 | 0 | 10 | 0 | 0 |
| E6 | filter file: v1.4 → v1.5 (`N+ years` alone) [batch 2] | 20/20 | 10/20 | 0 | 0 | 10 | 0 | 0 |
| E7 | filter file: v1.5 → v1.6 (sub-requirements ignored) [batch 2] | 20/20 | 10/20 | 0 | 0 | 10 | 0 | 0 |

FP = said relevant, Omkar said not_relevant. FN = said not_relevant, Omkar said relevant. Accuracy is over answered postings; abstentions are counted apart, never as right.

## Every held-out posting

| id | Title | Omkar | F0 | E1 | E2 | C0 | C0b | E3 | E4 | E5 | E6 | E7 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 7696724003 | Senior Software Engineer - Growth | R | **n✗** | R | R | **n✗** | **n✗** | ? | **n✗** | **n✗** | **n✗** | **n✗** |
| 7776017003 | Commercial Account Executive (Portuguese Speaking) | n | n | n | n | n | n | n | n | n | n | n |
| 7802701003 | Lead Engineer, Applied AI (Customer Agent) | R | **n✗** | **n✗** | **n✗** | **n✗** | **n✗** | ? | **n✗** | **n✗** | **n✗** | **n✗** |
| 7806010003 | Senior GTM Partner Systems Engineer (Salesforce) | R | **n✗** | **n✗** | **n✗** | **n✗** | **n✗** | ? | **n✗** | **n✗** | **n✗** | **n✗** |
| 7855726003 | Senior Lead Technical Program Manager - Infrastructure | R | **n✗** | **n✗** | **n✗** | **n✗** | **n✗** | **n✗** | **n✗** | **n✗** | **n✗** | **n✗** |
| 7861843003 | Sr. Staff Engineer, Applied AI (Customer Agent) | R | **n✗** | **n✗** | **n✗** | **n✗** | **n✗** | **n✗** | **n✗** | **n✗** | **n✗** | **n✗** |
| 7916089003 | Partner Account Manager, Mid Enterprise | n | n | n | n | n | n | n | n | n | n | n |
| 7979747003 | Director, Customer Success - Enterprise | n | n | n | n | n | n | n | n | n | n | n |
| 8009591003 | Large Enterprise Sales Manager | n | n | n | n | n | n | n | n | n | n | n |
| 8011054003 | PIPELINE - L5 Principal Software Engineer  | R | **n✗** | **n✗** | **n✗** | **n✗** | **n✗** | **n✗** | **n✗** | **n✗** | **n✗** | **n✗** |
| 7660012003 | Senior Security Engineer - Detection and Response | R | **n✗** | **n✗** | **n✗** | **n✗** | **n✗** | **n✗** | **n✗** | **n✗** | **n✗** | **n✗** |
| 7802698003 | Sr. Lead Engineer, Applied AI (Customer Agent) | R | **n✗** | **n✗** | **n✗** | **n✗** | **n✗** | **n✗** | **n✗** | **n✗** | **n✗** | **n✗** |
| 7829675003 | Sr. AI Systems & Solutions Architect, Global Services | R | **n✗** | **n✗** | **n✗** | **n✗** | **n✗** | **n✗** | **n✗** | **n✗** | **n✗** | **n✗** |
| 7855798003 | Software Engineer II - Recommendations | R | R | R | R | R | R | R | R | R | R | R |
| 7989990003 | Senior CS Compensation Analyst | n | n | n | n | n | n | n | n | n | n | n |
| 7990569003 | Lead Software Engineer, CICD | R | **n✗** | **n✗** | **n✗** | **n✗** | **n✗** | **n✗** | **n✗** | **n✗** | **n✗** | **n✗** |
| 7991733003 | Senior Security Engineer - Detection & Response | n | n | n | n | n | n | n | n | n | n | n |
| 8004318003 | Large Enterprise Sales Manager | n | n | n | n | n | n | n | n | n | n | n |
| 8015691003 | Email Marketing Lead, Lifecycle Marketing - EMEA (12 mo | n | n | n | n | n | n | n | n | n | n | n |
| 8041534003 | Order to Cash Track Lead, Finance Engineering | n | n | n | n | n | n | n | n | n | n | n |

R relevant · n not_relevant · ? cannot_tell · ✗ disagrees with Omkar.

## Tool use in E5

Claude called score_posting in 0 of 20 E5 sessions. When it called the tool, its verdict matched the filter's (F0) in 0 of 0.

Quotes not found verbatim in the posting (first 60 chars): 0. Total Claude cost: $2.57.
