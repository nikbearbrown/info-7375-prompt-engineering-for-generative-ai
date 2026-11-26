# SOURCES

**Status: in progress (2026-11-25); completed in Phase 6.**

## Inherited
- **Persona:** `persona/` was copied unchanged from JS2 (fictional persona Maya Sehgal, from The Reallocation Engine). The prefs were corrected on 2026-11-25 (see `persona/SOURCE.md`).
- **Text helper:** `src/text.mjs` was copied unchanged from JS2.
- **Data:** `data/raw/` is a copy of one JS2 run (`data/MANIFEST.json`).

## Claude Code (this session, 2026-11-25)
Claude Code drafted most of the code, tests, tools, and documents in this folder, working from Aravind's decisions at each checkpoint. A file-by-file account follows in Phase 6.

Every hand verdict, hand label, false-friend name, and decision marked [DECIDED] is Aravind's.

## Claude responses used as data
- **Intended:** `claude -p`, tool-less, from `src/judge.mjs`. All 7 Phase 3 calls failed on the account's spend limit with no reply (`runs/claude/justify.v1-v1.1.0-e/failed/`, commit `3caf2978`).
- **Used instead:** claude.ai web (incognito chat), pasted by hand. The exact prompts are in `runs/claude/justify.v1-v1.1.0-e/manual/prompts/`, and the raw replies in `manual/responses/`. They were imported by `tools/import-manual.mjs`. Each record carries the date, the interface, the model as Aravind reports it, `manual_paste: true`, and the SHA-256 of the prompt and of the reply.
- **What differs from `claude -p`:** the model name is self-reported, and the web chat's own system prompt and settings are not controlled here (FILTER.md §4, deviation).
