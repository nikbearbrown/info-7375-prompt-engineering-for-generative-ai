# Seeded replay: posting 7855793003 through the real watch

**SEEDED REPLAY, not a live observation.** Run once by Claude Code on 2026-10-31T18:44:21Z, at Ashwin's
request, with `python3 action-surfaces/seeded_watch.py`. The exact watch command is in `command.txt`.

**What was seeded.**
- The board data was **not** modified: `runs/2026-10-31T18-44-21Z/raw-response.json` is byte-identical to run 2's live
  response (`runs/2026-10-31T16-09-43Z/raw-response.json`, SHA-256 `79ac8124…6ec908`, collected 2026-10-31T16:09:43Z).
- What was modified is the **starting state**: a copy of the committed `state/seen_ids.json` (after run 2) with
  the single id `7855793003` removed. It is kept as `state-before-seeded.json` (155 ids).

**What happened.** The watch read the persona and parsed the 156 postings. It reported exactly one as new
(7855793003) and wrote the rule record: RELEVANT, all four checks PASS. It made **one real `claude -p` call**
with `prompts/revision-v2.md` (model `claude-opus-5-5`), which the validator accepted: RELEVANT, no
disagreement. It wrote the reply (`runs/*/claude/7855793003.txt`), `report.json` and `report.md`, and last
updated the scratch state to 156 ids (`state/seen_ids.json` here). Those 156 ids equal the committed state's.

**What was not touched.** The committed `state/seen_ids.json` and both live run folders: checked by
SHA-256 before and after.

**One wording error in the saved report.** `report.md` says "this file was modified on purpose". For this
run that is wrong: the file was unchanged and the state was seeded. The template was corrected afterwards to
"the replayed file or the starting state was modified on purpose". The saved report was left as written.

**What it shows.** That the watch's own path (new by id → rule → Claude → validator → report → state) works
end to end on real posting text. It does not show a posting that really appeared overnight.
