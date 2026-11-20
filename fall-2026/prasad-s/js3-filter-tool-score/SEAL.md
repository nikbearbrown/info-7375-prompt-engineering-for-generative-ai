# SEAL.md — Job-Search Agent 3: the sealed sets and the draw

**Author:** Prasad Shinde
**Written:** 2026-11-15, before any draw
**Version:** v1.7 — 2026-11-20
**Rests on:** FILTER.md v1 (JS3-CP1), §3 (the corpus) and §5 (the hand verdicts). This file is committed before any draw, for the same reason FILTER.md came before the build: a rule written after the draw could be bent to fit it.

## 1. The two sets

The draw takes two sets out of the pool, and they are not for the same thing.

- **The final's set** is ids only. Nothing in it is opened in JS3, and nothing in it is labeled in JS3. It is drawn now, while the pool is untouched, so the final project inherits a set nobody has seen, and it is left alone until then.
- **JS3's held-out set** is the measuring set. I label it on Monday, by hand, under FILTER.md §5, without looking at the rule's verdicts. On Friday it is used to measure changes to the filter — one change at a time, each version scored against the same labels, so a difference in the numbers belongs to the change and to nothing else.

## 2. The pool

The pool is FILTER.md §3's corpus: the 20 frozen responses, one copy per posting, keyed by (board, id) as in GATE §3.

Every posting already seen is left out of the pool. "Seen" means opened, labeled, judged or sampled in JS1 or JS2: the 20 JS1 hand labels, the sampling postings, the action-surface posting (8154295), the 29 postings JS1's run 2 judged, whose Claude replies are saved, and 8250475, the one new posting from JS2's run 2 — and anything else the earlier work looked at. The seen list is built by a script from the committed JS1 and JS2 files, not from memory, and I check it before the draw. A posting that was seen and still got drawn would spoil the set it landed in, because its label could no longer be written blind.

I have opened no posting since Friday 2026-11-13.

**Checked, 2026-11-15.** The seen list (vault/seen_ids.tsv) holds 51 ids, and every one of them is in the corpus. 8172510 is kept as seen: CONTRACT §1 quotes it as the example id from the raw file, so I have looked at that record — keeping it costs one posting, while drawing it could spoil a set. The corpus files were checked against the hashes recorded when they were collected: 18 match (8 in SHA256SUMS.txt, 10 in sidecars). The 2026-10-25 file matches the hash in CONTRACT §1 by my own shasum, which makes 19. The 2026-10-26 file has no recorded hash. None mismatches.

## 3. The two groups

The pool is split into two groups before anything is drawn.

- **The "product" group:** the posting's title, cleaned as in F1, contains "product" — case-insensitive, plain substring, the same matching as F2.
- **The "other" group:** everything else, including a posting with no title at all. A missing title is not a failed check here; it just puts the posting in "other".

The substring catches more than product roles — "Production" contains it, so a Production Manager lands in the product group. That is fine. The groups are not a judgment about any posting; they only split the pool so the draw takes from both sides of it, and a blunt, checkable line serves that purpose better than a clever one.

One consequence, stated now so it is not discovered later: because the draw is split by these groups and the pool leaves out everything already seen, the held-out numbers compare one filter version against another. They do not estimate the filter's accuracy across the whole corpus, and I will not report them as if they do.

## 4. Sizes

- JS3's held-out set: **22 product + 8 other** (30 postings).
- The final's set: **15 product + 5 other** (20 postings).

If the product group is too small to fill both sets at these sizes and still leave at least half of itself in the development pool, the sizes shrink until it can. The development pool keeps at least half of the product group either way, because the audit needs postings to work on that are not sealed.

The counts step runs first, before any draw, and prints counts only — group sizes, seen counts, pool sizes; no ids, no titles. The final sizes are written into this file, in a dated line under this section, before the draw runs.

**Counts, 2026-11-15.** The counts run (vault/counts.txt) gives a product group of 162 and an other group of 1,085 — a pool of 1,247, the 1,298 corpus postings less the 51 seen. The sizes stand as written: the final's set 15 + 5, JS3's set 22 + 8. Between them the sets take 37 product postings, which leaves 125 product postings in the development pool — more than half of 162.

## 5. Seed and ranking

The seed is **a6ac8bbb** — the first 8 characters of the CP1 commit, which holds FILTER.md v1. It cannot have been chosen to steer the draw: the hash was fixed by a commit made before this file existed, and no draw has been computed with it, or with any other seed, so there is no result it could have been chosen for.

**Seed note, 2026-11-15.** The seed is taken from JS3-CP1's hash as first committed: a6ac8bbb229a0dfcf0647e79ac4c89534f7bc207. JS3-CP1 will be rebased onto the shared main before pushing, and the rebase will give it a new hash. The seed does not change: it names the commit as first committed, not the hash the rebase produces.

Each posting's rank is the SHA-256 of `a6ac8bbb:<board key>:<id>`, written in lowercase hex. Within each group, postings are ordered by rank, lowest first.

The final's set takes the lowest ranks in each group; JS3's set takes the next ones after them. That order is deliberate: the final's set is fixed by the lowest ranks alone, so if JS3's set ever changes size, the change is absorbed after the final's set and the final's set does not move.

## 6. Where things are kept

Committed in this folder: the ids of both sets, the seed, the draw script, the corpus manifest, and the seen list. Anyone can re-run the draw from those and get the same sets.

JS3's labels are kept outside the repo, in `~/js3-vault/`. On Monday, when the labeling is done, only the SHA-256 of the label file is committed. On Friday the labels are revealed and the hash is checked against Monday's, so the labels that score the changes are provably the labels written before any change existed.

The final's set gets no labels in JS3 — none written, none kept anywhere.

**Drawn, 2026-11-15 (JS3-CP2d).** The draw was run with: `python3.13 tools/seal_draw.py draw --final 15 5 --js3 22 8` (sizes per §4). It wrote two files: vault/final_heldout_ids.tsv (the final's set) and vault/js3_heldout_ids.tsv (JS3's held-out set). I checked the output with the shell: (1) 20 + 30 postings — the final's set holds 20, JS3's holds 30; (2) the groups split 15/5 and 22/8, as §4 requires; (3) no posting is in both sets; (4) no drawn posting is on the seen list; (5) one rank recomputed with shasum, matching. The command and the checks are recorded here, in the file, because the submission zip has no .git folder: a reader of the zip would never see a commit message.

## 7. What I won't do

- Draw again with a different seed. If a bug in the draw is found and fixed, the rerun uses the same seed, and both outputs are kept.
- Open a sealed posting — except JS3's set, and that only for Monday's labeling.
- Look at any sealed posting's rule verdict before Friday.
- Change a sealed set, in either direction, because of anything seen in the development pool.

## 8. The first set is retired — 2026-11-16

This section is written and committed before the replacement draw runs.

**What happened.** On 2026-11-16, the first JS3 set's 30 labels, with short quotes from the postings, were pasted into the Claude.ai review chat before their hash was committed. Claude.ai helps choose the changes measured on Friday, so that set can no longer measure them blind.

**The decision.** The first set (vault/js3_heldout_ids.tsv) is retired as JS3's held-out set and becomes development data. Its file stays exactly as drawn. Its labels, kept in ~/js3-vault/js3_set1_exposed_labels.tsv, become development labels.

**The replacement.** Same seed, same pool, same ranking. In each group, the replacement takes the next ranks after the first set: product ranks 38 to 59 and other ranks 14 to 21, which makes 22 + 8. It is written to vault/js3_heldout_ids_v2.tsv. This is not a second draw with a different seed (§7): the seed and the ranking do not change. The final's set does not move, because it holds the lowest ranks, as §5 designed.

**The half-rule still holds.** The sealed product postings are 15 + 22 = 37, so the development pool keeps 125 of 162. That 125 includes the first set's 22.

From now on, "JS3's held-out set" means the v2 set, everywhere in this file.

**A new rule.** Nothing from the v2 set is pasted into any chat: not its ids, not its postings, not its labels. Its labels stay in ~/js3-vault/ until Friday.

**Replacement drawn, 2026-11-16 (JS3-CP3e).** The replacement was drawn with `python3.13 tools/seal_draw.py replace-js3 --final 15 5 --exposed 22 8 --js3 22 8`. Before writing anything, the tool re-derived the final's set and the first set from the ranking and found both committed files matched byte for byte; then it wrote vault/js3_heldout_ids_v2.tsv. I checked the output with the shell: (1) 30 postings, 22 product + 8 other; (2) 80 postings across the three sets, none in two of them; (3) none on the seen list; (4) the rank of the v2 set's first row, recomputed with shasum, matching. I ran these checks after the draw on 2026-11-16, and again, from freshly rebuilt files, before writing this line.

**Labeled, 2026-11-16 (JS3-CP3f).** I labeled the v2 set's 30 postings by hand under FILTER.md §5, in ~/js3-vault/js3_heldout_labels.tsv, and `python3.13 tools/label_view.py check` printed ok. Its SHA-256 is f144c95d62db6b5c3263216bb388932460b8ae8e533106d503dd83b4c4965cd9, recorded in vault/js3_heldout_labels.sha256; a backup outside the repo has the same hash. No posting raised a case §5 does not cover, so there are no notes and FILTER.md is unchanged. The file stays in ~/js3-vault/ until Friday. While I was fixing the file's format, one check output pasted into the review chat showed three v2 ids: ids only, no titles and no labels. The check's message will be changed to print positions only.

## 9. The reveal — written 2026-11-19, before it

The audit (AUDIT.md §7) found that my first-pass labels misapplied §5's level rule: I read Staff PM as an ordinary PM title. The held-out labels were written on 2026-11-16, before I knew that, so they may carry the same slip. They stay sealed and unchanged until the reveal, which runs in this order:

1. The labels file is checked against vault/js3_heldout_labels.sha256. A mismatch stops everything.
2. Before any filter version is run on the held-out set, every held-out label is re-checked under FILTER.md §5 as written, for the slips the audit found: a seniority title marked worth with no years of 3 or less quoted; a worth with no level evidence; a role §5 rules out (Product Operations, Engineering Manager and the like) marked worth; and an unclear that §5 can decide. Each posting in question is re-read with label_view, and each change is written with its §5 sentence.
3. The re-checked labels go in a new file, ~/js3-vault/js3_heldout_labels_r2.tsv, and its SHA-256 is committed before any filter version is scored. The sealed file is never edited.
4. Only then are the filter versions scored, against both files: the labels as sealed, and the re-checked labels. Both results are reported.

## 10. The reveal — 2026-11-20

It ran in §9's order. (1) The sealed labels file matched vault/js3_heldout_labels.sha256 (shasum -c: OK). (2) The re-check read every worth row: positions 15, 23 and 24 (there were no unclear rows). 15 states "Minimum requirements 8+ years" and 24 "Minimum requirements 10+ years", so both became not_worth on level; 23 states 5+ years only under Preferred Qualifications, and stays worth under FILTER.md §5 as clarified that day (v2.1). (3) The re-checked file's SHA-256 (3a95104f12c6…, vault/js3_heldout_labels_r2.sha256) was committed (JS3-CP11b) before any filter version was scored. (4) Both files were scored (output/measure_heldout_2026-11-20T205452Z/, JS3-CP11f). Each table records its file's SHA-256, and both match the committed hashes. After scoring, both label files, the re-check notes and the exposed first set's labels were copied into vault/ (JS3-CP11g), and shasum -c matched both again.

What the re-check could and could not do: it re-read only worth and unclear rows, so it could only move labels toward not_worth, which favours the stricter filters. That is why both files' results are reported (MEASURE.md). Two of the three worth labels as sealed had missed a minimum-years requirement, the same slip the audit found (AUDIT.md §7).

## Changelog

- **v1 — 2026-11-15.** Written and committed before any draw. The design (§§1–7) was proposed by Claude (Claude.ai); the decisions are mine.
- **v1.1 — 2026-11-15.** Three dated additions, all from checks run before any draw: §2 records the seen-list check (51 ids, all in the corpus; 8172510 kept as seen) and the corpus hash check (18 of 20 match, none mismatches); §4 records the counts (product 162, other 1,085; the pool is 1,247) and that the sizes stand, leaving 125 product postings in the development pool; §5 records the seed's full hash as first committed and that the coming rebase does not change the seed.
- **v1.2 — 2026-11-15.** Records the draw (§6, JS3-CP2d) and completes the checks: §2 gives 8172510's reason and the completed hash accounting (19 files match a recorded hash; the 2026-10-26 file has none; none mismatches), and the header cites FILTER.md v1 by its checkpoint (JS3-CP1) instead of the hash the rebase will replace. No rule changes.
- **v1.3 — 2026-11-16.** §8 added. The first JS3 set's labels were pasted into the Claude.ai review chat before their hash was committed, so the set is retired to development data and replaced by the next ranks under the same seed and ranking (product 38–59, other 14–21; vault/js3_heldout_ids_v2.tsv). The final's set does not move. §8 also adds the rule that nothing from the v2 set is pasted into any chat or leaves ~/js3-vault/ until Friday. No change to the seed, the ranking, the sizes, or the final's set.
- **v1.4 — 2026-11-16.** Formatting fixes (the Version line and the §8 heading) and one sentence in §8 saying it was written and committed before the replacement draw. No rule changes.
- **v1.5 — 2026-11-16.** §8 records the replacement draw (JS3-CP3e) and the labeling of the v2 set (JS3-CP3f): the command, the checks, the labels' SHA-256, and the three v2 ids that appeared in the review chat. §8's lead-ins are now bold, a blank line follows its first sentence, and its last rule now says the labels stay in ~/js3-vault/ (the v2 ids are committed in vault/, so "nothing from it" was too broad). Claude (Claude.ai) typed this version's text at my request; the facts and decisions are mine. No rule changes.
- **v1.6 — 2026-11-19.** §9 added: the reveal procedure, written before the reveal, after the audit found a level slip in my first-pass labels. Claude (Claude.ai) typed it at my request; the decision is mine. No change to the sealed sets or the labels.
- **v1.7 — 2026-11-20.** §10 records the reveal. Claude (Claude.ai) typed it at my request from the committed files; the facts are mine.