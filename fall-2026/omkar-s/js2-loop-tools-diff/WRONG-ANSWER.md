# A finished wrong answer, and the independent check that caught it

## The run that ended cleanly and was wrong

**Live, not seeded.** Claude Code ran these on 2026-11-09 with the **pre-patch** loop (`review/before/loop.py`), using `config/wrong-answer-watchlist.json`: Klaviyo (Greenhouse), Linear (Ashby) and Webflow (Greenhouse). These are three boards on two systems with no deliberate failure. Webflow is listed as Greenhouse `webflow` because that is where the instructor's Lectern verified it on 2026-09-26, with 27 postings.

```bash
python3 -m agent.loop --watchlist config/wrong-answer-watchlist.json --out runs/wrong-answer-demo --label wrong-answer-prepatch       # 08:07:38Z, baseline
python3 -m agent.loop --watchlist config/wrong-answer-watchlist.json --out runs/wrong-answer-demo --label wrong-answer-prepatch-run2  # 08:07:44Z, watch
```

The second run's report (`runs/wrong-answer-demo/2026-11-09T08-07-44Z-wrong-answer-prepatch-run2/report.md`):

```text
# Run 2026-11-09T08-07-44Z-wrong-answer-prepatch-run2: **FINISHED** (exit code 0)
> every board returned postings
| `greenhouse:klaviyo` | ok | http_200 | 152 | 0 | 0 | 1 |
| `ashby:linear`       | ok | http_200 |  32 | 0 | 0 | 1 |
| `greenhouse:webflow` | ok | http_200 |   0 | 0 | 0 | 1 |
## New postings since the last run
None among boards that answered.
```

**Why it is wrong.** The agent said, with exit code 0, that it watched Webflow and Webflow had no new jobs. In fact Webflow's Greenhouse board is still alive (`/v1/boards/webflow` returns `{"name":"Webflow"}`, HTTP 200) but holds **0** postings. Webflow's real postings are on **Ashby**, which had **22** at that moment. A watch of this board would say "no new Webflow jobs" every day, forever. No exception, no error, nothing in the agent's own report would show it, and a scheduler would see exit 0.

**What was real and what was planned (disclosure).** The **data** is real and was not staged. Webflow's empty Greenhouse board was found by `curl` at 08:00:21, before any code existed (`evidence/probes/`). The **defect in the agent was planned**: GATE.md §4 already said an empty board must be `empty_unverified`, and Claude Code built the first loop *without* that rule on purpose. The aim was to reproduce the failure on a live run and then fix it through a reviewed diff. A student who forgot the rule would get the same run; this one was set up deliberately, and it is labelled that way here.

## The independent check

`verify/independent_check.py` is a separate program. **It does not import the loop or the ATS parsers.** It reads the run folder (report, trace and raw files) and re-derives the facts itself:

| Check | What it does | Result on the wrong run |
|---|---|---|
| C1 | sha256 of every raw file vs the trace | OK ×3: the evidence is intact |
| C2 | recount postings from the raw bytes with its own parser vs `report.json` | OK ×3: the agent did not miscount. **The count is right; the conclusion is wrong.** |
| **C3** | for each board reported with 0 postings: (a) a reference count written down by someone else (`config/reference-counts.json` → Lectern ATS.md, 27 on 2026-09-26); (b) a **live** probe of the same company slug on the other allow-listed ATSs (through the same permission policy) | **CONTRADICTED**: "reference says 27 postings on 2026-09-26; **ashby has 22 postings for 'webflow' right now**" |

```bash
python3 -m verify.independent_check runs/wrong-answer-demo/2026-11-09T08-07-44Z-wrong-answer-prepatch-run2   # exit 1 = contradiction
```

The output is saved as `independent-check.md`/`.json` in that run folder. The three probe responses are in `independent-probes/`: Greenhouse 0, **Ashby 22**, and Lever 404.

C1 and C2 both pass, so a check that only re-verified the agent's own numbers would have passed this run too. What catches it is **evidence from outside the agent**: a number someone else wrote down, and a different system queried directly.

## What changed after the catch

1. The defect went to the review packet (REVIEW-PACKET.md). The patch makes an empty board `empty_unverified` with `new: null`, and the run becomes `incomplete` rather than `finished`.
2. The same watch list, rerun on the patched code (`runs/wrong-answer-demo/2026-11-09T08-10-08Z-wrong-answer-postpatch/`), now exits **`incomplete` (3)**: "no answer from: greenhouse:webflow (empty_unverified)".
3. **Not done, on purpose:** the watch list still says `greenhouse:webflow`. Moving Webflow to `ashby:webflow` is a watch-list change. GATE §5 says that is Omkar's written decision, and the agent cannot write `config/` anyway (policy: ASK).

## Limits of the check (also in the sign-off)

- C3 only looks at boards with **exactly 0** postings. A board that silently lost 90% of its postings (27 → 3) would pass C3.
- The cross-probe uses the same slug on the other ATSs. A company that moved to a **different slug**, or to an ATS outside the allow-list (Workday, for example), would come back `UNCONFIRMED`, not `CONTRADICTED`.
- `config/reference-counts.json` holds three hand-entered rows, copied by Claude Code from Lectern's ATS.md and the JS1 run files. Omkar has not re-read them against those sources.
