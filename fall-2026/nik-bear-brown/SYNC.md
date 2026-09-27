# This folder is not the master

## Executive summary

**What this is.** A pointer. The job-search tool in this folder is live-coded in three courses at once, and the canonical copy lives in **Computational Skepticism**, not here:

```
info-7375-computational-skepticism-for-ai/fall-2026/nik-bear-brown/
```

**Why read it.** Because editing `collect.py`, `sources.json`, `keywords.json`, or `ATS.md` *here* creates drift that nothing will catch for you. Those four files are copies. Change them in the master and run its `./lectern/sync.sh`.

**This class's emphasis.** *What is the recipe, and which labor belongs to Claude?* The eight-step dream-job recipe, the prompts, the handoff conditions. The tool is identical in all three; only the question changes.

---

## Copies here — edit in the master instead

| File | Where it is in this repo | Canonical location |
|---|---|---|
| `collect.py` · `sources.json` · `keywords.json` · `ATS.md` | `lectern/` | master's `lectern/` |
| `facts/professor-bear-cv.json` | `facts/` | master's `facts/` |
| `figma/` · `greenhouse-watch-demo/` | same paths | same paths in the master |

## Yours alone — never copied in either direction

`FRICTIONAL.md`, `README.md`, `CLAUDE.md`, every `assignment-*/` folder, and the dated run outputs (`all-jobs-*`, `jobs-of-interest-*`, `quality-report-*`). A log or an assignment overwritten by another class's version is a destroyed record, so `sync.sh` will not touch them.

## If you edited a shared file here anyway

It happens mid-class. Do not copy it back blindly:

1. In the master folder, run `./lectern/sync.sh --check` — it names every file that differs.
2. Decide which version is right. Usually the newer edit; not always.
3. Put the correct content in the **master**.
4. Run `./lectern/sync.sh` so all three match.
5. Record it in this class's `FRICTIONAL.md` — a drift that happened is a finding about the workflow, not an embarrassment.

The full rule, including why Computational Skepticism is master, is in that folder's [`SYNC.md`](https://github.com/nikbearbrown/info-7375-computational-skepticism-for-ai/blob/main/fall-2026/nik-bear-brown/SYNC.md).
