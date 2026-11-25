# The 20-posting split (sealed 2026-10-29, before any Claude call)

- **Source:** `runs/2026-10-29-1/raw.json`, the committed live baseline (68 postings), sha256
  `3c10b536e3805bb5a4fca46800ac5caf4c521fa84c9beec30a8ab0beb995c2b7`. The script refuses a file that
  doesn't match this hash.
- **Script:** `experiment/make_split.py`, Python standard library, `random.Random(20261029)`.
- **Seed:** **20261029**
- **Balancing:** postings were sorted by id and grouped by whether the title contains, as a whole word
  and ignoring case, one of data, analytics, analyst, scientist, machine learning, ML (25 postings) or
  not (43). This is only for a balanced sample; it is not a label. 10 were drawn from each group with
  `rng.sample`, each group's 10 were shuffled, and 5 from each went to development and 5 to held-out.
  The split is random within each group, so each set has the same balance.
- **Result:** 10 development, 10 held-out.

| File | sha256 |
|---|---|
| `experiment/heldout_ids.json` | `1cc26d9d144abe6ecfd2862f17fa39ceec331d6cb3d349ec3bb486aec163b5cc` |
| `experiment/dev_ids.json` | `fa756026f87952b47b99083fcc5db212eee5f529a7c893c884087193d7ff022a` |

To check the seal: `sha256sum experiment/heldout_ids.json` (or `Get-FileHash` in PowerShell) must
print the hash above. `.gitattributes` marks both id files `-text`, so Git never changes their bytes.
The script refuses to run again once `heldout_ids.json` exists.

**The held-out rule:** the held-out postings are not shown to Claude and not used to change a prompt
until the revision is frozen. If one is used before then, it is recorded here and counted as
development evidence from that point on.

## Exposure log

- 2026-10-29: the held-out titles and locations (not their posting text or my labels) were shared with Claude in claude.ai while I asked how the rule reads. No prompt was written or changed from that conversation. The seal applies to the claude -p judge, which had not seen any of these postings before the held-out evaluation.
