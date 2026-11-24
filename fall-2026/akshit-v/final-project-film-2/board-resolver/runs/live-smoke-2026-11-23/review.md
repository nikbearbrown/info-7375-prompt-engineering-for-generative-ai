# G1 review — live-smoke-2026-11-23

Transport **live** · stop **done** · 7/30 requests · {'not-found': 1, 'proposed': 1}

Every row is a **proposal**. Open the board by hand, compare it with the company, then run the
`decide` command with the hash shown (that binds your decision to this exact saved response).
Lever and Ashby give no company name, so a hit there is only a slug that exists.

| Company | ATS | Slug (rule) | Evidence | Open by hand | SHA-256 |
|---|---|---|---|---|---|
| YEXT INC | greenhouse | `yext` (full) | name-match: “Yext” | https://boards.greenhouse.io/yext | `8b62492e7be9` |

Decide (approve / refuse / defer):

```
python resolver.py decide --run "C:\Users\Akshit Verma\PromptEngr\Assignment_Final Project Film v2\board-resolver\runs\live-smoke-2026-11-23" --company "<COMPANY>" --ats <ats> --slug <slug> \
  --decision approve --by "<your name>" --seen-sha256 <sha from the table>
```
