# What moves the score (Chapter 9)

## Where every number came from
| Number | Value | Origin |
|---|---|---|
| Title weight | 4 | Hand-set (FILTER.md §7) |
| Skill categories and their keywords | 8 categories, 1 point each | Inherited from Alex's résumé (data/persona_alex.json); weight hand-set |
| Skill cap | 8 | Hand-set |
| Target-location weight | 2 | Hand-set |
| Other US city weight | 0 | Hand-set; C3 tested 2 and was rejected |
| Threshold | 8 | Hand-set; never changed |
| Years cutoff | 8 in v1.0, **5 in v1.1** | Hand-set, then changed after looking at my audit labels (closest to "fitted on my labels", but chosen by hand, not by an optimizer) |
| Description minimum | 50 words | Hand-set |
| Random seeds | 7375 (audit), 7376 (held-out) | Hand-set, fixed before drawing |
| 95% intervals | Wilson, z = 1.96 | Inherited (standard statistics) |
| MCP protocol versions | up to 2025-06-18 | Inherited from the MCP specification |

There is **no Claude prompt in this scorer**: FILTER.md is a deterministic rule. The JS1/JS2 judge prompts in prompts/ are not used for scoring in JS3.

## One change to one object at a time, measured on held-out labels
Development labels: my 48 blind audit verdicts (audit/). Held-out labels: 20 random target-title postings I judged blind afterwards (heldout/). Every change was applied through a config file; code defaults stayed v1.0.

| Object changed | Change | Development (48) | Held-out (20) | Decision |
|---|---|---|---|---|
| Filter rule (FILTER.md §2.5) | C1: years cutoff 8 → 5 | 37 → 40 agree | 18 → 18 agree | Added in v1.1, with the caveat that the gain appears only on the postings that suggested it |
| Filter weight (FILTER.md §2.4) | C3: other US cities 0 → 2 | 37 → 37 | 18 → 18; of the 12 postings it adds, 3 relevant (25%; 95% interval 9–53%) | Rejected |
| Context (what text the scorer sees) | C2: read Lever's `lists` field | not measured | not measured | Considered, not tested; all 3 Palantir misses point to it (A30 confirmed; H02 and H27 not verified) |
| Setting | C4: threshold 8 → 7 | not measured | not measured | Considered, not tested |
| Tool list | Claude Code gained `score_posting` through .mcp.json | — | — | Shown in out/transcripts/server-2026-11-25T060303.jsonl; not scored |

Sources: out/measure/2026-11-23T153111/report.md, heldout/comparison_2026-11-23.txt, FILTER.md §10.

## What this can and cannot show
- 20 held-out postings is very little: 18/20 has a 95% interval of 70–97%. A one-posting difference would be invisible inside that range, so "no change" means "no difference this sample can detect", not "no effect".
- Development and held-out labels are both my judgment, not ground truth.
- C1 was chosen by reading the same 48 postings it improved, so the development gain is optimistic by design.

## Persistence is not proof of training
The agent's behavior changed between v1.0 and v1.1, and it stays changed in every later session, but nothing was trained. The change lives in a file (config/filter_v1_1.json). Delete the file or pass a different config, and the old behavior returns. Likewise, Claude Code "knowing" score_posting in a new session comes from .mcp.json being read at startup (the tool list), not from Claude learning anything. A behavior that persists across sessions shows that some input persists; it does not show that a model's weights changed.
