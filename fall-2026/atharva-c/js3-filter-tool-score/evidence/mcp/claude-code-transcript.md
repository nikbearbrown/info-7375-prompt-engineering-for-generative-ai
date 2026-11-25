# Claude Code session against js3-job-filter

Recorded 2026-11-24T06:03:20Z (UTC, Nov 24, 2026) with `claude -p` (Claude Code 2.1.283, model `claude-opus-5-5`), `--strict-mcp-config` with only this server, and only its four tools allowed. This is a response I actually got; generated from `claude-code-transcript.jsonl`, with the matching server-side log in `claude-code-server-log.jsonl`.

## Prompt

> You are helping a fictional new-grad software engineer, Sam Rivera (US-based; Python, Go, React, TypeScript, SQL, Java). Using only the js3-job-filter tools, find the Software Engineer I postings in the saved run, check whether each would be kept by the filter, and for the best one show the shortlist claims with their quotes. Then say plainly what the tools cannot tell you. Do not invent anything the tools did not return.

(Passed as the `claude -p` argument; stream-json output does not echo it.)

## Tool calls (in order)

- `ToolSearch` {"query": "select:mcp__js3-job-filter__get_posting,mcp__js3-job-filter__judge_posting,mcp__js3-job-filter__search_postings,mcp__js3-job-filter__shortlist_entry", "max_results": 4}
- `search_postings` {"query": "Software Engineer I", "limit": 50}
- `judge_posting` {"uid": "affirm:8181183003"}
- `judge_posting` {"uid": "affirm:8181185003"}
- `judge_posting` {"uid": "affirm:8201471003"}
- `judge_posting` {"uid": "affirm:8201469003"}
- `judge_posting` {"uid": "affirm:8011718003"}
- `judge_posting` {"uid": "affirm:8196691003"}
- `judge_posting` {"uid": "affirm:8017342003"}
- `judge_posting` {"uid": "affirm:8017340003"}
- `shortlist_entry` {"uid": "affirm:8017340003"}

## Final answer (verbatim)

Eight postings in the saved run (Nov 23, 2026) are Software Engineer I roles, all at Affirm. Robinhood and Wealthfront had none. Three of the eight are kept by the filter (FILTER.md v1.2).

## Software Engineer I postings

| Posting | Location | Keep | Score | Gate failed | Skills matched |
|---|---|---|---|---|---|
| affirm:8181183003 – Backend (Continuous Delivery) | Remote US | **yes** | 0.8 | — | Python |
| affirm:8181185003 – Backend (Continuous Delivery) | Remote Canada | no | 0.8 | G3 | Python |
| affirm:8201469003 – Backend (Streaming Infra) | Remote US | **yes** | 0.8 | — | Python |
| affirm:8201471003 – Backend (Streaming Infra) | Remote Canada | no | 0.8 | G3 | Python |
| affirm:8011718003 – Early Career (London) | London | no | 0.7 | G3 | — |
| affirm:8017340003 – Fullstack (Search) | Remote US | **yes** | 0.8 | — | Python, TypeScript |
| affirm:8017342003 – Fullstack (Search) | Remote Canada | no | 0.8 | G3 | Python, TypeScript |
| affirm:8196691003 – Fullstack (Disputes Platform) | Remote Canada | no | 0.8 | G3 | Python, React |

The five rejected postings all failed gate G3, and every one of them is in Canada or London. That points to G3 being the US-location gate, but the tool only gives the gate's name, not what it checks. The search also matched 23 Software Engineer II postings and one intern posting because their titles contain "Software Engineer I". I left those out.

## Best match: affirm:8017340003, Software Engineer I, Fullstack (Search), Remote US

All three kept postings scored 0.8, so the filter doesn't rank one above the others. I chose this one because it matched two of Sam's skills and the other two matched one. The shortlist tool puts it in the **ranked** list.

| Claim | Label | Quote |
|---|---|---|
| This is a software engineering role. | supported | "Software Engineer" |
| It asks for at most 2 years of experience. | **insufficient** | *(none; looked for "'N years' near 'experience', or 'no fixed minimum'")* |
| It is written for an entry-level engineer. | supported | "You have previous work or internship experience working with Javascript/Typescript." |
| It is open to someone in the US. | supported | "Remote US" |
| The role uses at least one of Sam's skills. | supported | "You have previous work or internship experience designing, developing and launching backend systems at scale and are experienced using Python or Kotlin." |

**Two weak spots in these claims:**
- **Entry level:** the quote mentions "internship experience", which fits an entry-level role but doesn't say the job is entry level.
- **Role:** the quote is only the job title.

## What the tools cannot tell you

- **How much experience it requires.** No years figure was found in any of the eight postings, and the claim about at most 2 years is marked insufficient.
- **What G3 actually checks.** The tool reports which gate failed but doesn't describe the rule.
- **Anything outside the saved run.** The data covers only Robinhood, Affirm and Wealthfront as collected on Nov 23, 2026, with no live requests. The tools can't say whether a posting is still open.
- **Anything Sam's skill list doesn't capture.** The tools say nothing about pay, visa sponsorship, team quality, interview process, chance of getting an offer, or whether Sam would actually want the job.
- **Whether the filter is right.** A keep or a score is the v1.2 rule's output, not a verified judgment.
- **Anything the title search can't see.** Matching is on titles only, so roles with a different title (such as "New Grad" or "Associate") wouldn't turn up under this query.

---
Turns: 12. Cost reported by Claude Code: $0.33.
