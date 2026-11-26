# SOURCES

## What I started from

| Source | What I took | How |
|---|---|---|
| My JS2 (`../js2-loop-tools-diff/agent/`) | `ats.py`, `transport.py`, `policy.py`, `rule.py`, `persona.py` | **copied byte for byte** into `js3/js2/` (sha256 identical, checked 2026-11-17). Not edited. The User-Agent string still says `js2-loop-tools-diff/1.0` |
| My JS1 (`../js1-contract-and-watch/`) | the fictional persona (`persona/aarav-patel.example.json`, byte-identical); Omkar's **20 hand labels**, the postings they were made on, and his `LABELING-RULE.md` | copied unchanged into `labels/heldout-js1/`, used as the held-out set |
| Reallocation Engine, greenhouse-watch skill (`.claude/skills/greenhouse-watch/scheme.default.json`, github.com/nikbearbrown/the-reallocation-engine) | the weights `title` 3.0, `title_partial` 1.5, `skill` 1.0, `skill_unshipped` 0.25, `max_skill_hits` 8; 5 of the excluded title words; the idea that justification lines sum to the score (its commit `015843d`) | numbers **inherited** (listed in SCORE.md), code not copied |
| Reallocation Engine, `scripts/score/role-scorer.mjs` | the idea that every weight carries its provenance in the config | idea only |
| Instructor's Lectern (`fall-2026/nik-bear-brown/lectern/`: `keywords.json`, `audit_rejects.py`, `title_families.json`) | the filter as a versioned document with every added, cut and rejected word measured; the two-part reject audit (uniform sample + near-misses); the "false friend" idea ("training" at an AI company) | read as a reference; **no code copied**. My audit adds parts G and K, blind cards and an exact interval |
| Model Context Protocol specification (modelcontextprotocol.io) | the message shapes: `initialize`, `notifications/initialized`, `tools/list`, `tools/call`, JSON-RPC error codes, tool `annotations` | written from scratch from the message shapes; no SDK used |

## AI use (Claude)

**Claude Code** (Anthropic, CLI 2.1.292; model Claude Opus 5.5) did most of the building on 2026-11-17, at Omkar's request ("complete the assignment, then test it end to end as QA"). It wrote **all the code and tests** in `js3/` and `tests/` (the files in `js3/js2/` are Omkar's JS2 copies). It wrote FILTER.md v1.0 and every later version; drew the audit sample; ran every collection, experiment and tool-server session; and drafted this file, README.md, AUDIT.md, SHORTLIST.md, TOOL-SERVER.md and SCORE.md. It ran the end-to-end checks and fixed the bugs they found (FRICTIONAL Part 2).

**Claude as a component of the agent** (claude-sonnet-5-5 through `claude -p`, every call dated in its file):

| Use | Calls | File |
|---|---:|---|
| second rater on the 49 audit cards | 49 | `audit/claude-second-rater.jsonl` |
| held-out experiments C0, C0b, E3, E4, E5 | 100 | `experiments/runs/*.jsonl` |
| MCP client sessions (score one posting; injected posting) | 2 | `transcripts/claude-client-*.stream.jsonl` |

**Anthropic's `claude mcp serve`** is the "other tool server" evaluated in TOOL-SERVER.md (initialize and list only).

**What is Omkar's.** The parts marked **[Omkar]**: the hand verdicts (`audit/omkar-verdicts.csv`), the claim hand checks, the FILTER.md confirmations, the decisions in SCORE.md section 4, the sign-off, the driver's-seat "why" column, and FRICTIONAL Part 1. Also, from earlier work: the labeling rule and the 20 held-out labels (JS1, 2026-10-26/27). Omkar is responsible for everything submitted.

## Data

Public job-board APIs only, read with GET, with no login and no keys: `boards-api.greenhouse.io` (Klaviyo, HubSpot, Toast, Datadog, Webflow), `api.ashbyhq.com` (Linear, Webflow), `api.lever.co` (Spotify). The raw responses are kept gzip-compressed in `data/raw/2026-11-17T06-16-31Z/`, with their sha256 in `data/runs/…/sources.json`. Posting texts belong to the employers and are kept only as evidence for this coursework.
