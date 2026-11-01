# Labeling rule — how I hand-label a posting

Author: Isaac Tai. Written before labeling any posting (R23).

我站在 Aarav Patel 的立場判斷（résumé：`personas/aarav-patel.resume.json`；profile：`personas/aarav-patel.profile.json`）。
這是我自己讀 JD 時的判斷方式，不是程式的 rule：我讀的是整篇 JD 的意思，不是比對字。

照順序看，**任何一步不符合就標 `not_relevant`，不用再往下看**；六步都過才標 `relevant`。

1. **Title**：跟 engineer 相關的，我才會再看下去。
2. **地點**：看是不是在美國（包括 US remote）。是，才繼續看。**location 沒寫（空白、`N/A`、`na`），或只寫 `Remote` 沒說哪個國家 → 一律算合格，繼續看。**（這條是標完第 1–3 號之後才補的；那 3 個都有寫地點，不受影響。）
3. **Skills**：直接跳到 skills 的段落（如果有的話），沒有就全文搜尋，看它提到要用哪些技能。**有兩、三個是 Aarav 會的**（résumé 的 `skills[].keywords[]`），才繼續看。
4. **Sponsor**：Aarav 需要 visa sponsorship。JD 寫明不 sponsor → 不符合；沒寫 → 繼續看。
5. **薪水**：有寫薪水的話，看有沒有達到 Aarav 能接受的最低年薪（profile 的 `min_salary`）。沒寫 → 繼續看。
6. **其他要求**：看有沒有額外強調的部分，例如工作經驗。要求明顯超出 Aarav 的程度（profile：2 年經驗，最多再多 2 年）→ 不符合。

**Nice to have 當作 must have**（第 3 步和第 6 步都是）：JD 既然列出來，就是要有，因為一定會有符合這些條件的人來申請。所以「Nice to have」、「Preferred」、「Bonus」底下的技能和要求，跟「Requirements」底下的一樣算。

每個標註寫一句理由：在哪一步不符合、JD 裡的哪一句讓我這樣判斷。
