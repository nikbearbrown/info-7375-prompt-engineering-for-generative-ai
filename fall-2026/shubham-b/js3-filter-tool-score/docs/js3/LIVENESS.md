# Are the shortlisted postings still open? (optional live check, 2026-11-25)

The JS3 corpus is what JS1 and JS2 collected (newest raw 2026-11-11); no posting was re-fetched for
the filter or the audit. As a separate check, `uv run python scripts/js3_liveness.py` made one GET
per board to its public list endpoint (allow-listed hosts only, no content), on 2026-11-25, and
checked whether each of the 53 v0.3 shortlisted postings is still listed. It wrote only
`data/js3/liveness/2026-11-25.json` (with each response's SHA-256); the corpus, board state and
audit were not touched.

| Board | Shortlisted | Still listed | Gone |
|---|---:|---:|---:|
| greenhouse/stripe | 31 | 17 | 14 |
| ashby/ramp | 13 | 11 | 2 |
| greenhouse/figma | 9 | 8 | 1 |
| **All** | **53** | **36** | **17** |

**When they went:** 15 of the 17 were still on the board in the newest saved raw (2026-11-11) and
closed in the two weeks since. **Two were already gone when the newest data was collected**, and
the corpus kept them anyway: Stripe "Frontend Engineer, Data Product Experiences" (8194606, last
seen in the 2026-10-30 raw) and Ramp "Software Engineer, Bill Pay & Procurement" (last seen
2026-11-09). This is a property of the corpus loader (`js3/corpus.py`): it takes every posting from
every saved raw, newest copy wins, so a posting that left the board stays in the corpus. That was
the right choice for a fixed, reproducible audit population, and the wrong one for "what can I
apply to today". A shortlist meant for use would need to drop postings absent from the newest raw,
and then a live check like this one.

Not checked: whether a posting missing from the list endpoint is closed rather than moved or
re-posted under a new ID; the 1,182 non-shortlisted postings.
