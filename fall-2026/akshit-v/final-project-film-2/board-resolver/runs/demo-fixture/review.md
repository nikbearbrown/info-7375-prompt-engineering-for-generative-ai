# G1 review — demo-fixture

Transport **fixture:demo-transport.json** · stop **done** · 21/1000 requests · {'proposed': 3, 'not-found': 1, 'incomplete': 1}

Every row is a **proposal**. Open the board by hand, compare it with the company, then run the
`decide` command with the hash shown (that binds your decision to this exact saved response).
Lever and Ashby give no company name, so a hit there is only a slug that exists.

| Company | ATS | Slug (rule) | Evidence | Open by hand | SHA-256 |
|---|---|---|---|---|---|
| HUMAN INC | greenhouse | `human` (full) | name-partial: “Human Interest” | https://boards.greenhouse.io/human | `ea76c8cd6ca7` |
| NUTANIX INC | lever | `nutanix` (full) | exists-no-name: 2 postings | https://jobs.lever.co/nutanix | `e8fe644c1685` |
| YEXT INC | greenhouse | `yext` (full) | name-match: “Yext” | https://boards.greenhouse.io/yext | `19447e27fbdf` |

Decide (approve / refuse / defer):

```
python resolver.py decide --run "C:\Users\Akshit Verma\PromptEngr\Assignment_Final Project Film v2\board-resolver\runs\demo-fixture" --company "<COMPANY>" --ats <ats> --slug <slug> \
  --decision approve --by "<your name>" --seen-sha256 <sha from the table>
```
