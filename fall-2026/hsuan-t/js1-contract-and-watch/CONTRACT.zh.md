# CONTRACT — Job-Search Agent 1

<!-- Who wrote what (for SOURCES.md / driver's seat):
     - 2026-10-29: Claude drafted the skeleton (headings + guiding questions). Isaac wrote the content in Chinese.
     - 2026-10-30: at Isaac's request, Claude unified field names, filled the gaps from its review
       (paths, hosts, API key, status/error_message, run summary, wrong-version tests), and wrote the
       Examples by running Isaac's rule on the saved 10/29 Stripe data. Isaac reviews all of it.
     - 2026-10-30 (later): Isaac added checks 4–6 (years, visa, salary) and their profile fields;
       Claude wrote them out as rules, the phrase list, Known limits, and re-ran the Examples.
     - Later, at Isaac's request: Claude rewrote the Claude row in In (claude -p by default, API optional),
       added the claude -p limit to Refuses #1, added Out item 4 (claude_raw.jsonl), and added two
       validator examples (code fence, empty quote). Isaac's decision: D18.
     - Later, at Isaac's request: check 2 now passes when the posting has no location
       (empty, N/A, na, or a bare "Remote"); Claude re-ran the Examples counts. Isaac's decision: D21.
     - Translation to English: Claude, after Isaac approves this version. -->

Author: Isaac Tai · Written: 2026-10-29 (before any code ran) · Revised: 2026-10-30

## In

| 輸入 | 內容 | 缺少或壞掉時 |
|---|---|---|
| **board** | Greenhouse，公司 `stripe`：`https://boards-api.greenhouse.io/v1/boards/stripe/jobs?content=true` | 抓不到（非 200、不是 JSON）→ 報錯停止，不更新 state |
| **resume** | `personas/aarav-patel.resume.json`，虛構 persona Aarav Patel，格式 JSON Resume（https://jsonresume.org/schema/） | 報錯停止，指出缺哪個欄位 |
| **profile** | `personas/aarav-patel.profile.json`，使用者的求職偏好（欄位見下） | 報錯停止，指出缺哪個欄位 |
| **state** | `state/stripe.state.json`（見下） | 檔案不存在 → baseline；檔案壞掉 → 報錯停止 |
| **內建同義詞表** | `data/skill_aliases.json`，工具內建、跟著 repo 一起提供（見下） | 檔案不存在或壞掉 → 報錯停止 |
| **內建「不 sponsor」片語表** | `data/no_sponsorship_phrases.json`，工具內建（見下） | 檔案不存在或壞掉 → 報錯停止 |
| **Claude** | 預設：`claude -p`（Claude Code，用自己的訂閱登入），不需要 API key。選用：`--claude-via api` + 環境變數 `ANTHROPIC_API_KEY`（需要 API credits），**key 不寫進任何檔案、不 commit** | 找不到 `claude`、沒登入（或 api 模式沒有 key）→ Claude judge 報錯；rule judge 照常跑 |

### resume 必要欄位（JSON Resume）
`resume.basics.name`、`resume.basics.email`、`resume.basics.phone`、`resume.basics.profiles[]`、`resume.work[]`、`resume.projects[]`、`resume.skills[].keywords[]`。
缺任何一個 → 報錯停止，錯誤訊息寫出缺的欄位（例如 `missing resume.skills[].keywords`）。不會產生任何 verdict。

### profile 欄位
| 欄位 | 型別 | 例子 |
|---|---|---|
| `profile.target_roles[]` | 想要的職稱片語 | `["software engineer", "backend"]` |
| `profile.exclude_title_words[]` | title 出現就不要的字 | `["senior", "quant"]` |
| `profile.locations[]` | 可以接受的地點片語 | `["boston", "us remote", "us"]` |
| `profile.skill_aliases` | （選填）使用者自己補的同義詞，格式跟內建表一樣 | `{"PostgreSQL": ["pg"]}` |
| `profile.years_experience` | （選填）自己的工作年資，數字 | `2` |
| `profile.years_stretch` | （選填）JD 要求比自己多幾年還願意申請，數字 | `2` |
| `profile.needs_sponsorship` | （選填）需不需要公司 sponsor 簽證（例如 H-1B），true / false | `true` |
| `profile.min_salary` | （選填）可以接受的最低年薪，美元 | `100000` |

前三個必填，至少要有一個值。其他可以不寫：沒寫的那一關**跳過**，justification 寫 `skipped`（`years_experience` 和 `years_stretch` 要兩個都有，第 4 關才會跑）。

### 同義詞（skill aliases）
同一個技能，JD 和 résumé 常常寫法不同（JD 寫 `postgres`，résumé 寫 `PostgreSQL`）。第 3 關比對時，résumé 的每個關鍵字，**它本身或它的任何一個同義詞**出現在 JD 裡，就算找到。同義詞來自兩個地方，兩邊都會用：

1. **內建表** `data/skill_aliases.json`：工具預先寫好的常見寫法，保持很小（約 10–20 組），例如：
   ```json
   {"PostgreSQL": ["postgres"], "Kubernetes": ["k8s"], "JavaScript": ["js"], "Node.js": ["nodejs"], "Go": ["golang"]}
   ```
   résumé 的關鍵字本身和它的同義詞**全部都搜**（résumé 寫 `Go` → 找 `go` 和 `golang`）。表裡不額外加一般英文單字當同義詞（例如 Node.js 不加 `node`：分散式系統裡的「each node」）。
2. **使用者自己補**：在自己的 profile 檔加 `profile.skill_aliases`（格式跟內建表一樣）。內建表沒有的寫法加在這裡就好，**不用改工具本身**。跟內建表的同一個技能都寫了的話，兩邊的同義詞合併使用。

**告訴使用者去哪裡加**：
- README 有一段「Add a skill spelling」，寫出 profile 檔的位置和格式範例。
- 每次 run 的 summary 最後一行固定提示：`Missed a skill written another way? Add it under "skill_aliases" in personas/aarav-patel.profile.json`（路徑是當次實際用的 profile 檔）。
- justification 第 3 關的結果會寫出是用哪個寫法找到的（例如 `"found: PostgreSQL (as postgres)"`），使用者看得出同義詞有沒有生效。

### 「不 sponsor」片語表
`data/no_sponsorship_phrases.json`：JD 裡寫明**不提供** visa sponsorship 的常見句子。工具內建，跟著 repo 一起提供：
```json
["no sponsorship", "unable to sponsor", "not able to sponsor", "cannot sponsor", "will not sponsor",
 "do not sponsor", "does not sponsor", "not provide sponsorship", "not offer sponsorship",
 "not eligible for sponsorship", "without sponsorship", "sponsorship is not available", "sponsorship not available"]
```
這些片語用**整句比對**（見 The rule），不是一般的拆字比對。

### state file
`state/stripe.state.json`，內容：
```json
{"board": "stripe", "seen_ids": [8172510, 6042172], "last_run_at": "2026-10-30T15:00:00Z"}
```
- 不存在 → 當成 baseline：回報 0 筆新職缺，然後建立 state。
- 壞掉（不是合法 JSON、缺欄位）→ 報錯停止。不能靜靜地當成空檔案，否則所有職缺都會被當成新的，等於重跑一次 baseline。

## Out

每次 run 產生四樣東西：

1. **raw response**：`evidence/raw/<UTC 時間>/stripe_content.json`（原始資料，當證據）
2. **更新後的 state**：`state/stripe.state.json`
3. **run 結果**：`runs/<UTC 時間>/verdicts.json` + `runs/<UTC 時間>/summary.md`
4. **Claude 原文**：`runs/<UTC 時間>/claude_raw.jsonl`（每個職缺 Claude 回的原文，被 validator 拒收的也存；有新職缺時才有）

### 每個新職缺的 verdict（`verdicts.json`）

- `status`：`"ok"` 或 `"error"`。**先看 status**：`ok` 時 verdict 才有意義；`error` 時看 `error_message`。
- `verdict`：只能是 `"relevant"` 或 `"not_relevant"`。`status` 是 `error` 時一律是 `"not_relevant"`。
- `judge` + `kind`：rule 的是 `"rule"` + `"record"`；Claude 的是 `"claude"` + `"judgment"`。
- `justification`：每一行就是一個檢查：職缺的哪個欄位、跟誰比、結果如何。要寫出具體欄位名稱，不能只給結論。`status` 是 `ok` 時不能是空的。被刷掉的職缺，justification 寫到刷掉它的那一關為止（最後一行就是原因）。
- 沒有新職缺（包括第一次 baseline）→ `"verdicts": []`。

```json
{
  "posting_id": 6042172,
  "status": "ok",
  "error_message": null,
  "verdict": "relevant",
  "judge": "rule",
  "kind": "record",
  "justification": [
    {"posting_field": "title", "compared_to": "profile.exclude_title_words[]", "result": "no match"},
    {"posting_field": "title", "compared_to": "profile.target_roles[]", "result": "match: backend"},
    {"posting_field": "location.name", "compared_to": "profile.locations[]", "result": "match: us remote"},
    {"posting_field": "content", "compared_to": "resume.skills[].keywords[]", "result": "1 found: Java"},
    {"posting_field": "content", "compared_to": "profile.years_experience + profile.years_stretch", "result": "min 2 years ≤ 4"},
    {"posting_field": "content", "compared_to": "data/no_sponsorship_phrases.json", "result": "no phrase found"},
    {"posting_field": "content", "compared_to": "profile.min_salary", "result": "skipped: no salary in posting"}
  ]
}
```

error 的例子（JD 是空的，skills 檢查做不了）：
```json
{
  "posting_id": 12345,
  "status": "error",
  "error_message": "posting.content is empty, skills check cannot run",
  "verdict": "not_relevant",
  "judge": "rule",
  "kind": "record",
  "justification": []
}
```

### Claude judge（judgment）
Claude 的輸出跟上面的格式**一樣**，只有兩個差別：

1. **justification 的每一行多一個 `quote`**：從該 `posting_field` 的原文抄一段話當證據，讓人看得出 Claude 是根據什麼判斷的。
2. **`judge` 和 `kind` 由程式填**（`"claude"` + `"judgment"`），不讓 Claude 自己寫，避免標錯。

Claude 看到的：一個職缺（`title`、`location.name`、`content`，content 拿掉 HTML）、résumé、profile。只能回傳這個 JSON：
```json
{
  "posting_id": 6042172,
  "verdict": "relevant",
  "justification": [
    {"posting_field": "title", "compared_to": "profile.target_roles[]",
     "result": "backend role matches", "quote": "Backend Engineer, Core Technology"},
    {"posting_field": "content", "compared_to": "resume.skills[].keywords[]",
     "result": "requires Java, which the résumé lists", "quote": "programming languages like Go, Java, C/C++"}
  ]
}
```

**validator**：Claude 回傳之後、存檔之前，程式先檢查一次。任何一項不符 → 拒收，這筆記成 `status: "error"`、`verdict: "not_relevant"`，`error_message` 寫出原因（例如 `"quote not found in posting.content"`），不重試。

| 檢查 | 會被拒收的例子 |
|---|---|
| 是合法 JSON，而且只有 JSON | 回一段文字 "This job looks like a good fit!"；或用 ```` ```json ```` 包起來 |
| 欄位剛好是 `posting_id`、`verdict`、`justification`，不多不少 | 少了 `justification`，或多了 `confidence` |
| `posting_id` 跟送進去的一樣 | 送 6042172，回 8138044 |
| `verdict` 是 `relevant` 或 `not_relevant` | `"maybe"` |
| `justification` 至少一行，每行剛好 4 個欄位，每個欄位都是非空字串 | `[]`，或少了 `quote`，或 `"quote": ""`（空字串在任何原文裡都「找得到」） |
| `posting_field` 是 `title`、`location.name`、`content` 之一 | `"posting_field": "salary"` |
| `compared_to` 是 `resume.` 或 `profile.` 開頭 | `"compared_to": "common sense"` |
| `quote` 真的出現在那個欄位的原文裡（拿掉 HTML、轉小寫、多個空格算一個之後比對） | `"quote": "5+ years of Rust required"`，但 JD 沒有這句 |

validator 只能確認 Claude **有照格式回答、證據真的存在**。證據能不能撐起結論（那句話真的代表職缺要求 Java 嗎）是 judgment，要靠 sampling report 和手標來檢查。

### run 摘要（`summary.md`，也印在 terminal）

```
Run 2026-10-30T15:00:00Z · board: stripe
State file: state/stripe.state.json · updated: 2026-10-30T15:00:00Z
Raw response: evidence/raw/2026-10-30T150000Z/stripe_content.json
```

| | rule (record) | Claude (judgment) |
|---|---|---|
| 抓到的職缺 | 737 | — |
| 新職缺 | 28 | 28 |
| 刷掉：1a 排除詞 | 12 | — |
| 刷掉：1b 職稱 | 10 | — |
| 刷掉：2 地點 | 4 | — |
| 刷掉：3 技能 | 1 | — |
| 刷掉：4 年資 | 1 | — |
| 刷掉：5 visa | 0 | — |
| 刷掉：6 薪資 | 0 | — |
| error | 0 | 0 |
| **relevant** | **1** | 2 |
| 兩個 judge 不一致 | 1 | |

（數字是示意。Claude 只給 relevant / not_relevant，不分是哪一關刷掉的，所以那幾格是 —。）

```
Missed a skill written another way? Add it under "skill_aliases" in personas/aarav-patel.profile.json
```

## Refuses

| 不做的事 | 怎麼做到 / 怎麼看得出來 |
|---|---|
| 抓 allow-list 以外的 host | allow-list 只有 `boards-api.greenhouse.io` 和 `api.anthropic.com`。程式自己發的每個 request 先檢查 host，不在清單上 → 報錯停止。有 test 驗證。**限制**：預設用 `claude -p` 時，送給 Claude 的 request 是 Claude Code 發的，程式查不到它的 host；程式只保證自己不連 allow-list 以外的 host，並且啟動 `claude` 時關掉所有工具和 MCP、不載入任何設定，拿掉 `ANTHROPIC_API_KEY`、`ANTHROPIC_BASE_URL` |
| 在畫面上或 GitHub 顯示真實 résumé | 只讀 `personas/` 底下的檔案；`resume.basics.email` 不是 `@example.com` 結尾 → 報錯停止。`.gitignore` 擋掉 `my_resume/`、`*.pdf`。terminal 和 summary 只印欄位名和比對到的關鍵字，不印整份 résumé |
| 把模型的判斷當成事實 | Claude 的每筆輸出都標 `kind: "judgment"`，summary 表格的欄位也寫「Claude (judgment)」。validator 拒收沒有這個標籤的 Claude 輸出 |

上面任何一條被觸發 → 回傳錯誤訊息並停止執行。

## The rule

### How words are matched (read this first)
Every check compares words, not raw text. Before comparing, both sides are turned
into a list of words:

1. Lowercase everything.
2. Split at every character that is not a letter or a digit: spaces, "/", ",", "-",
   "(", tabs ... Empty pieces are dropped.

   "Backend/API Engineer, Money"  ->  [backend, api, engineer, money]
   "Backend / API Engineer"       ->  [backend, api, engineer]

A target phrase matches a title when **every word of that phrase is in the title's
word list**. Order does not matter, and extra words in the title are ignored:

   title  "market software engineer" -> [market, software, engineer]
   target "software engineer"        -> [software, engineer]
   software ✓  engineer ✓  -> match ("market" is simply ignored)

   title  "security engineer"        -> [security, engineer]
   target "software engineer"        -> software ✗  -> no match

Why: companies write the same title in different ways ("Backend/API Engineer",
"Backend / API Engineer"), and often longer than my target, so I compare words
instead of exact text. But one shared word is not enough: matching on any single word
of my targets ("engineer", "platform", ...) let 163 of 737 Stripe titles through on
2026-10-29, including "Android Engineer, Identity", "Designer, Web Presence & Platform"
and "SaaS Platform and AI Partner Marketing Lead". Requiring every word of one target
phrase cut that to 92.

**Exception — whole phrases (check 5 only).** The "no sponsorship" phrases are matched as a
**whole phrase**: the words must appear together, in the same order. Lowercase-and-split
first, so "No  Sponsorship" or "no-sponsorship" still match:

   JD     "... must be authorized to work without sponsorship ..."
   phrase "without sponsorship"  -> found -> fail

   JD     "No degree required. Visa sponsorship is available."
   phrase "no sponsorship"       -> not found (the words are not together) -> pass

Why not the normal word matching: the second JD has both "no" and "sponsorship", so it
would be wrongly failed, even though it says sponsorship IS available.

**Numbers (checks 4 and 6).** Read straight from the JD text with HTML removed:

- Years: every number written right before "year", "years" or "yrs": "5 years", "5+ years",
  "2-12 years", "2–12+ years" (a range counts as its first number). Take the **smallest**.
- Salary: every dollar amount written with commas, like "$156,800". Take the **largest**.

### The checks
A posting goes through the checks in this order. The first check that fails gives
not_relevant. If all pass, the verdict is relevant.

| 順序 | 檢查 | 比對 | 通過條件 |
|---|---|---|---|
| 1a | 排除詞 | `posting.title` ↔ `profile.exclude_title_words[]` | title 的字**不含**任何一個排除詞 |
| 1b | 職稱 | `posting.title` ↔ `profile.target_roles[]` | 至少一個 target 片語的字全部在 title 裡 |
| 2 | 地點 | `posting.location.name` ↔ `profile.locations[]` | 至少一個地點片語的字全部在 location 裡（同樣的拆字方法）。location 沒寫（空白、`N/A`、`na`）或只寫 `Remote` → 通過，justification 寫 `skipped: no location in posting` |
| 3 | 技能 | `posting.content` ↔ `resume.skills[].keywords[]`（＋同義詞：`data/skill_aliases.json`、`profile.skill_aliases`） | 先拿掉 HTML 標籤，再用同樣的拆字方法；résumé 的關鍵字（本身或任一同義詞）**至少 1 個**出現在 JD 裡 |
| 4 | 年資 | `posting.content` ↔ `profile.years_experience` + `profile.years_stretch` | JD 裡最小的年資數字 ≤ years_experience + years_stretch。JD 沒寫年資 → 通過 |
| 5 | visa | `posting.content` ↔ `data/no_sponsorship_phrases.json` | 只在 `profile.needs_sponsorship` 是 true 時檢查。片語表任一句整句出現在 JD → 不通過；都沒出現 → 通過 |
| 6 | 薪資 | `posting.content` ↔ `profile.min_salary` | JD 裡最大的金額 ≥ min_salary。JD 沒寫薪資 → 通過 |

- 第 3 關是反過來數：拿 résumé 的每個關鍵字去 JD 裡找。因為 Greenhouse 沒有「技能清單」欄位，`content` 只是一整篇 HTML，「JD 列了幾個技能」不用 AI 算不出來。
- 第 3 關是唯一用到 résumé 的檢查（brief 要求 justification 要寫出 résumé 欄位和 posting 欄位）。
- 第 2 關「沒寫就通過」跟第 4–6 關同一個方向：board 沒給的資訊，不拿來刷掉職缺。
- 第 4–6 關的資料只在 JD 內文裡（Greenhouse 沒有年資、visa、薪資欄位；`pay_input_ranges` 在 2026-10-30 查過 Stripe 和 WPP 都是空的），所以都是「JD 有寫才檢查，沒寫就通過」。
- 第 4 關取最小的數字、第 6 關取最大的金額，都是往寬鬆的方向取：寧可多留一個職缺讓人看，也不要因為讀錯數字而刷掉。
- `posting.content` 是空的 → `status: "error"`、`verdict: "not_relevant"`。

### Known limits（這個 rule 已知會判錯的地方）
這個 rule 的目的是可預測、能重算，不是最準。下面這些錯誤是事先知道的：照著 rule 手算也會得到同樣的錯誤結果。需要理解語意的判斷交給 Claude judge。

- **有出現 ≠ 有要求**：第 3 關只看關鍵字有沒有出現在 JD 裡，不分「必須」還是「加分」（nice to have），也看不懂「Java or Go」、「migrating away from Redis」這種句子。
- **整篇 JD 都會搜**，包括公司介紹那段。實測（2026-10-29 Stripe）：title 通過的 60 個職缺裡，改成只搜「Minimum requirements」段落，只有 2 個結果不同（41 → 39）。沒有改用段落搜尋，因為段落標題是各家公司自己定的，換公司就不一定有。
- **門檻 ≥ 1 很寬鬆**：Java、SQL、AWS 這類常見字，只對到一個就通過。
- **同一個技能的不同寫法**：例如 JD 寫 `postgres`，résumé 寫 `PostgreSQL`（2026-10-29 Stripe 有 2 個 JD 這樣寫）。用同義詞表處理，但表永遠不完整：沒收進內建表、使用者也沒補的寫法還是會漏。
- **一般英文單字的技能名稱會誤判**：像 Go 本身就是常見英文字，rule 分不出「Python, Go, Java」（語言）和「Go-to-Market」、「go further」（一般英文）。實測（2026-10-29 Stripe）：737 個 JD 裡有 283 個出現 `go`，大多是 Go-to-Market；但 title 通過的 60 個工程職缺裡，27 個有 `go`，其中 17 個是真的要求 Go、8 個是公司介紹句（見下一條）、2 個只是 Go-to-Market。也就是說，title 那關已經擋掉大部分誤判。要讀懂句子的部分交給 Claude judge。（Aarav 的技能沒有 Go，這次的結果不受影響。）
- **公司固定的介紹句也會被比到**：Stripe 有 11 個 JD 有同一句「We work mostly in Java, Ruby, JavaScript, Scala, and Go」，這是公司技術介紹，不是這個職缺的要求，但 Java 會因為這句通過第 3 關。
- **年資數字可能不是在講要求**：第 4 關抓的是任何寫在 "years" 前面的數字，也會抓到不是在講工作經驗的數字（2026-10-29 Stripe 有 7 個 JD 寫「At least 1 year of university education」），或「5+ years … 2+ years with Kafka」裡比較小的那個。因為取最小的，多半是讓職缺多通過，而不是誤刷。實測（2026-10-29 Stripe）：737 個裡 654 個有年資數字，常見寫法是「2–12+ years」。
- **visa：沒寫 ≠ 會 sponsor**：第 5 關只能刷掉「明確寫不 sponsor」的職缺。實測（2026-10-29 Stripe）：737 個 JD 沒有一個出現片語表裡的句子；"sponsor" 這個字出現 18 次，全是「executive sponsor」這類用法。所以這關在 Stripe 不會刷掉任何職缺，但 Stripe 有沒有 sponsor 仍然不知道。片語表也不可能列完所有寫法。
- **薪資很少寫，格式也有限**：第 6 關只認「$156,800」這種有逗號的美元金額。實測（2026-10-29 Stripe）：737 個裡只有 24 個寫了薪資。時薪（"/hr"）、其他幣別、「$1,000,000 in funding」這種不是薪資的金額都分不出來。
- **地點只認字面**：`Seattle, WA`、`San Francisco, New York` 這種在美國、但字面上沒有 `us` 的地點，第 2 關會刷掉（2026-10-31 Stripe：地點被刷掉的 49 個裡很多是這樣）。只寫 `Remote` 一律通過，可能其實是別國的 remote。
- **工作型態**：hybrid / on-site 不檢查。Job Board API 沒有提供這個欄位，只有一些 JD 內文有提到，所以不算在檢查範圍。remote 透過 `profile.locations[]` 檢查。
- **全職 / 約聘**：沒有欄位，用 `profile.exclude_title_words[]` 處理（title 寫 "Intern"、"Contract" 的就排除）。title 沒寫、只在內文寫的抓不到。

### Examples
用 2026-10-29 存的 Stripe 資料（`evidence/raw/2026-10-30T033237Z/stripe_content.json`）和下面這份**示範用 profile** 實際跑出來的：

```json
{"target_roles": ["software engineer", "backend", "platform engineer", "devops engineer", "site reliability engineer"],
 "exclude_title_words": ["senior", "staff", "principal", "lead", "manager", "director", "head", "quant", "sales", "intern", "frontend", "contract"],
 "locations": ["boston", "us remote", "us"],
 "years_experience": 2, "years_stretch": 2,
 "needs_sponsorship": true,
 "min_salary": 100000}
```
（Aarav 是 F-1 STEM OPT，之後需要 H-1B，所以 `needs_sponsorship: true`。`min_salary` 是示範用的數字。）
resume 關鍵字（Aarav 的 17 個）：TypeScript, Python, Java, SQL, Node.js, Kafka, Redis, MSSQL, PostgreSQL, AWS, Kubernetes, Docker, Helm, Fluent Bit, Jenkins, Rust, Terraform

| posting_id | posting.title | posting.location.name | 1a 排除詞 | 1b 職稱 | 2 地點 | 3 技能 | 4 年資（≤ 4） | 5 visa | 6 薪資 | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| 8138044 | Account Executive, AI Sales | San Francisco, CA | ❌ sales | — | — | — | — | — | — | not_relevant |
| 8172510 | Abuse Investigator | Seattle, San Francisco, New York City | ✅ | ❌ 沒有 target 片語 | — | — | — | — | — | not_relevant |
| 8198280 | Software Engineer, Backend | Seattle, WA | ✅ | ✅ software engineer, backend | ❌ 沒有 boston / us / remote | — | — | — | — | not_relevant |
| 8089353 | Software Engineer, Vulnerability Management | US - Remote | ✅ | ✅ software engineer | ✅ us remote | ❌ 0 個 | — | — | — | not_relevant |
| 8127182 | Software Engineer, Revenue and Financial Automation | San Francisco, New York City, Seattle, Chicago, US-Remote | ✅ | ✅ software engineer | ✅ us remote | ✅ 1 個：Java | ❌ 最小 5（"5–12+ years"） | — | — | not_relevant |
| 6176758 | Backend/API Engineer, Money as a Service | US | ✅ | ✅ backend | ✅ us | ✅ 3 個：AWS, Kubernetes, Docker | ✅ 最小 2 | ✅ 沒有片語 | ✅ 沒寫，跳過 | **relevant** |
| 6042172 | Backend Engineer, Core Technology | US-Remote, Chicago, Seattle, San Francisco | ✅ | ✅ backend | ✅ us remote | ✅ 1 個：Java | ✅ 最小 2 | ✅ 沒有片語 | ✅ 沒寫，跳過 | **relevant** |
| 7292520 | Backend Engineer, Developer & End-user Experience Platform | Toronto Canada, San Francisco, Remote in US, Remote in Canada | ✅ | ✅ backend, platform engineer | ✅ us remote（remote、us 都在） | ✅ 3 個：AWS, Kubernetes, Docker | ✅ 最小 2 | ✅ 沒有片語 | ✅ 沒寫，跳過 | **relevant** |

同一份 profile 跑全部 737 個：1a 刷掉 355、1b 刷掉 322、2 刷掉 49、3 刷掉 4、4 刷掉 2、5 刷掉 0、6 刷掉 0，**relevant 5 個**（上表 3 個，加上 2 個 location 寫 `na` 的工程職缺）。第 2 關改成「沒寫就通過」之前是：2 刷掉 55、3 刷掉 1、4 刷掉 1、relevant 3。

## Wrong versions

1. **label 配錯職缺**：A 職缺的 verdict 被配到 B 職缺。
   - plausible：判定完直接把 label 寫進 output，沒有確認對應的 posting_id。筆數對、格式對，只看整體看不出來。
   - test：一次放 2 個預期結果相反的 mock posting（一個 relevant、一個 not_relevant），檢查每個 `posting_id` 拿到的是它自己的 verdict。
2. **justification 是空的，或只寫「good fit」**
   - plausible：verdict 是對的，大家只看結論，不會檢查理由。
   - test：所有 `status: "ok"` 的輸出，`justification` 不能是空的，而且每一行的 `posting_field` / `compared_to` 都要是真的存在的欄位名稱。另外，給一個 `content` 空白的 mock posting，必須回傳 `status: "error"` + `error_message`，不能回傳 `relevant`。Claude judge 這邊：給 validator 一個 `quote` 不在原文裡的假 Claude 回答，必須被拒收（`status: "error"`）。
3. **state 沒存好，或沒讀到**
   - plausible：把每個職缺都當成新的，沒有正確比對 state，或抓完之後沒有更新 state。第一次 run 看起來完全正常。
   - test：跑兩次，第一次 5 筆，第二次 5 筆但有 2 筆重複，應該回報 3 筆新職缺；如果 state 沒存好，會回報 5 筆。
4. **大小寫或空格導致判斷錯誤**
   - plausible：判定時沒有轉小寫，或沒有處理空格、符號。
   - 做法：所有關卡比對前都呼叫**同一個**拆字 function（轉小寫 + 切字），不各自處理。
   - test：直接測這個 function，給它每一關會遇到的不同樣式的 input：

     | 模擬哪一關 | input | 應該得到 |
     |---|---|---|
     | 1 title | `"\tSoftware   Engineer/Backend"` | `[software, engineer, backend]` |
     | 2 location | `"US-Remote, Chicago"` | `[us, remote, chicago]` |
     | 3 JD 內文（HTML 已拿掉） | `"Experience with JAVA, Node.js"` | `[experience, with, java, node, js]` |
     | 3 résumé 關鍵字 | `"Fluent Bit"` | `[fluent, bit]` |
     | 5 visa 片語 | `"Without  Sponsorship"` | `[without, sponsorship]` |

     沒轉小寫，或沒有用符號和空格切字的話，結果就會不一樣。
5. **judge 標籤標錯**
   - plausible：rule 的輸出被標成 Claude，或 Claude 的被標成 rule，格式完全正確，只差一個標籤。
   - test：rule judge 的每筆輸出都必須是 `judge: "rule"` + `kind: "record"`；Claude judge 的每筆都必須是 `judge: "claude"` + `kind: "judgment"`。
6. **visa 片語用了一般的拆字比對**
   - plausible：直接沿用前面「字都在就算」的比對方法，程式少寫一段，而且真正寫「no sponsorship」的 JD 一樣會被刷掉，看起來是對的。
   - test：`needs_sponsorship: true`。mock posting A 的 JD 是 "No degree required. Visa sponsorship is available."，第 5 關應該**通過**（沒有 "no sponsorship" 這句）；用一般拆字比對的話 "no" 和 "sponsorship" 兩個字都在，會被誤刷。mock posting B 寫 "must be authorized to work without sponsorship"，應該**不通過**。

## What a failure looks like

2026-10-29: 這個 agent 失敗的情況是：重複抓到已經判定過的職缺；或判定錯誤，明明不適合卻被判定為 relevant，或明明適合卻被判定為 not_relevant；最慘的是抓不到資料，或抓到的資料不正確；還有比錯 justification，明明 skills 應該跟 JD 的 requirements 比，卻去比 title 或其他欄位。
