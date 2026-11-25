# False keyword matches in filter v1.0

Drafted by Claude Code on 2026-11-25 at Ashwin's request. The finding rests only on posting text and the filter's own
recorded reason. It does not rest on any verdict, AI-assisted or human.

## "manager" in "Software Engineer - Mission Manager" (demonstrated)

**What matched.** `filters/v1.0.json` lists `manager` among `seniority_terms`, the words that exclude a
management-level title (FILTER.md section 2). In `runs/v1.0/decisions-dev.json`, both development postings with this
title were rejected for exactly that reason, `title contains excluded seniority term "manager"`:

| Audit row | Key | Location | Score without the gate |
|---:|---|---|---:|
| 47 | `lever/palantir/e168a922-a2f0-45d0-912c-678d66e15118` | Seattle, WA | 7 |
| 58 | `lever/palantir/c0b60d64-1244-4270-9d55-14115c97c24b` | New York, NY | 7 |

**Why it is the wrong reason.** In these postings, "Mission Manager" is the name of a software product, not a
management position. The two postings have identical text, and it says:

> "The Role Mission Manager is Palantir’s PaaS for enabling US Government customers and vendors to run software
> securely and compliantly in the most sensitive environments"

> "The Mission Manager offering is still in its earliest days"

The rule was meant to exclude people-management roles. Here it fired on a product name.

**What this does not settle.** Whether Supriya would want these jobs is a separate question. The same postings ask
for "3+ years of professional software development experience" and "1+ years of experience as a mentor, tech lead or
leading an engineering team". The match is false whatever that answer is. Correcting the reason would not by
itself make the decision right.

**Scope in the corpus.** Three of the 805 postings have this title: the 2 development postings above and 1 held-out
posting. Nothing about the held-out posting's prediction or measurement has been looked at. Claude Code has seen its
human label (see `drafting/EVALUATION-SETS.md`).

## Proposed fix: not implemented

The narrow option would be an exception so that the seniority term `manager` does not fire when it is part of the
phrase "mission manager". It would change exactly those 3 titles: on the development set, rows 47 and 58 would go
from REJECT to KEEP at score 7. Every other posting would get an identical decision by construction. As of
2026-11-25, Ashwin has decided to leave it unimplemented.

### Can an unused sample evaluate it?

No.

- **Cloudflare snapshot:** of the 463 postings in
  `../js1-contract-and-watch/snapshots/cloudflare-2026-10-29T23-55-50Z.json`, 0 have "mission manager" in the title.
  This was a count only, checked 2026-11-25; no titles, text or decisions were printed. With the narrow fix, v1.0 and
  v1.1 would make the same decision on every one of them. Any measurement there would come out identical for both
  versions, which is no evidence that the fix improves accuracy. (70 Cloudflare titles contain "manager". They
  would matter only for a broader rule, such as removing `manager` from the seniority terms. That would be a
  different change.)
- **The original 30 held-out postings:** 1 affected posting, and that set is potentially contaminated
  (`drafting/EVALUATION-SETS.md`).
- **A fresh fetch of the five boards:** would include these postings only under their existing keys, which are
  excluded as already used. It would test the fix only if Palantir had posted new Mission Manager roles.

The evidence for this change therefore comes from the posting text: the reason was false. Whether its effect on
these 2–3 postings is right is a human judgment about each posting, not an accuracy rate.
