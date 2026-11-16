# SEAL.md — Job-Search Agent 3: the sealed sets and the draw

**Author:** Prasad Shinde
**Written:** 2026-11-15, before any draw
**Version:** v1 — 2026-11-15
**Rests on:** FILTER.md v1 (a6ac8bb), §3 (the corpus) and §5 (the hand verdicts). This file is committed before any draw, for the same reason FILTER.md came before the build: a rule written after the draw could be bent to fit it.

## 1. The two sets

The draw takes two sets out of the pool, and they are not for the same thing.

- **The final's set** is ids only. Nothing in it is opened in JS3, and nothing in it is labeled in JS3. It is drawn now, while the pool is untouched, so the final project inherits a set nobody has seen, and it is left alone until then.
- **JS3's held-out set** is the measuring set. I label it on Monday, by hand, under FILTER.md §5, without looking at the rule's verdicts. On Friday it is used to measure changes to the filter — one change at a time, each version scored against the same labels, so a difference in the numbers belongs to the change and to nothing else.

## 2. The pool

The pool is FILTER.md §3's corpus: the 20 frozen responses, one copy per posting, keyed by (board, id) as in GATE §3.

Every posting already seen is left out of the pool. "Seen" means opened, labeled, judged or sampled in JS1 or JS2: the 20 JS1 hand labels, the sampling postings, the action-surface posting (8154295), the 29 postings JS1's run 2 judged, whose Claude replies are saved, and 8250475, the one new posting from JS2's run 2 — and anything else the earlier work looked at. The seen list is built by a script from the committed JS1 and JS2 files, not from memory, and I check it before the draw. A posting that was seen and still got drawn would spoil the set it landed in, because its label could no longer be written blind.

I have opened no posting since Friday 2026-11-13.

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

## 5. Seed and ranking

The seed is **a6ac8bbb** — the first 8 characters of the CP1 commit, which holds FILTER.md v1. It cannot have been chosen to steer the draw: the hash was fixed by a commit made before this file existed, and no draw has been computed with it, or with any other seed, so there is no result it could have been chosen for.

Each posting's rank is the SHA-256 of `a6ac8bbb:<board key>:<id>`, written in lowercase hex. Within each group, postings are ordered by rank, lowest first.

The final's set takes the lowest ranks in each group; JS3's set takes the next ones after them. That order is deliberate: the final's set is fixed by the lowest ranks alone, so if JS3's set ever changes size, the change is absorbed after the final's set and the final's set does not move.

## 6. Where things are kept

Committed in this folder: the ids of both sets, the seed, the draw script, the corpus manifest, and the seen list. Anyone can re-run the draw from those and get the same sets.

JS3's labels are kept outside the repo, in `~/js3-vault/`. On Monday, when the labeling is done, only the SHA-256 of the label file is committed. On Friday the labels are revealed and the hash is checked against Monday's, so the labels that score the changes are provably the labels written before any change existed.

The final's set gets no labels in JS3 — none written, none kept anywhere.

## 7. What I won't do

- Draw again with a different seed. If a bug in the draw is found and fixed, the rerun uses the same seed, and both outputs are kept.
- Open a sealed posting — except JS3's set, and that only for Monday's labeling.
- Look at any sealed posting's rule verdict before Friday.
- Change a sealed set, in either direction, because of anything seen in the development pool.

## Changelog

- **v1 — 2026-11-15.** Written and committed before any draw. The design (§§1–7) was proposed by Claude (Claude.ai); the decisions are mine.
