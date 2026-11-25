# SCRIPT — Fine Print (Final Project Film)

**Drafted by Claude Code from the records in [FACTCHECK.md](FACTCHECK.md); approved by the student on 2026-11-21 ("Approve it").** B07 and B16 use the student's own words from Frictional entry 1, and B17 is the student's own bar, word for word. The narration is spoken in the first person, as the student, by the synthesized voice am_eric.

Stamps (top left on screen) say what each picture is: `real · …` means it ran or was checked; `constructed · not built` means it's the plan.

## 1 · What and why

**BIDEA** ·    0–11 s (measured) · stamp: `—`

> Hi, I'm Suketh Produtoor. I'm an international student on F-1, looking for new-grad machine learning roles. Before I tailor an application, I need to know one thing: does this posting rule me out?

**B01** ·   11–25 s (measured) · stamp: `real · from my A3 work · fictional applicant`

> Titles can't tell me. Earlier this term, a recipe Claude Code and I built screened eight real postings for a fictional new grad, by title and sponsor record. When an AI reviewer read them in full, six asked for two to twelve-plus years of experience, or excluded new graduates.

**B02** ·   25–36 s (measured) · stamp: `constructed · not built`

> So I'm building Fine Print. It will read each new posting, show me the exact sentence behind every requirement that could rule me out, and wait for my approval before anything reaches my shortlist.

**B03** ·   36–47 s (measured) · stamp: `real · live run, Nov 21`

> And postings keep coming. In under two weeks, the three boards I watch showed one hundred seventy-two postings that weren't in my November eighth snapshot. One piece of Fine Print already runs: the watcher. The reader is next.

## 2 · What exists

**B04** ·   47–61 s (measured) · stamp: `real · my A3 work · my LinkedIn check, Oct 14`

> What already exists? My own first try matched on title and sponsor record, and couldn't tell fit. On LinkedIn, I checked two graduate ML postings, from Qualcomm and TikTok. Both separated minimum from preferred qualifications. Neither stated sponsorship.

**B05** ·   61–80 s (measured) · stamp: `real · sources checked Nov 21`

> Others have built pieces. Government H-1B data counts an employer's past approvals and denials, not what a posting asks for. Jobscan scores a résumé against a posting and lists missing keywords. One paper flags whether experience and education are required or preferred. And a 2024 study found language models find skills but miss their exact wording.

**B06** ·   80–94 s (measured) · stamp: `constructed · not built`

> Fine Print will put those pieces together for one question: should I apply? Each requirement will carry the posting's own sentence, checked word for word by code. Required will stay apart from preferred, silence on sponsorship will mean unknown, and nothing will reach my shortlist until I approve.

## 3 · How

**B07** ·   94–109 s (measured) · stamp: `real · how jobwatch works (JS2)`

> Now, how. In October I planned to build the reader first, and now I can build it on top of jobwatch, which already monitors three job boards. Its data: public job-board feeds, read only from an allow-list, each response saved with a fingerprint before anything reads it. The applicant is fictional.

**B08** ·  109–122 s (measured) · stamp: `real · ran Nov 21 · replay of the saved terminal log`

> On November twenty-first, Claude Code ran it from a fresh copy. All one hundred sixty-four tests passed. Then a live run read three boards, Anthropic, Databricks and Linear, and found one hundred seventy-two postings it hadn't seen on November eighth.

**B09** ·  122–132 s (measured) · stamp: `real · ran Nov 21 · replay of the saved terminal log`

> Its simple word rule, from my first agent, rejected all one hundred seventy-two for the fictional applicant. Were those rejections right? A word rule can't say. That's the gap the reader will fill.

**B10** ·  132–144 s (measured) · stamp: `real · Nov 21 run · Nov 8 run typed by me`

> The run also refused to save its memory, because I hadn't approved that: it ended incomplete, state unchanged. On November eighth, I typed that approval myself, for one run and one file, and only then did it save.

**B11** ·  144–156 s (measured) · stamp: `real · my JS1–JS2 record`

> So far, in both job-search agents, I wrote the rules first, before any code. Claude Code wrote the code, all but five of the tests, and ran most checks. I ran my own checks, and twice I withheld my sign-off until the record was right.

**B12** ·  156–173 s (measured) · stamp: `constructed · not built`

> Next, step by step. By November twenty-fifth, the reader: each claim labelled supported, contradicted or insufficient by the posting's own text, or 'I cannot tell'. By December first, every quote checked against the saved posting. By December thirteenth, my approval tied to the exact shortlist. December twentieth: the full evaluation.

**B13** ·  173–188 s (measured) · stamp: `real · JS1 judge run, Oct 31`

> Do I have what I need? No API credits: model calls will go through my Claude Code login, as my first agent's judge did for twenty-seven postings in October. Public boards need no accounts; a laptop runs it. The limits: boards can refuse automated reads, and usage caps mean a daily reading budget.

## 4 · Did it work?

**B14** ·  188–198 s (measured) · stamp: `constructed · not built`

> How will I know it worked? I'll label real public postings by hand, including a random sample of the ones my rule rejected, and lock a held-out group away before tuning anything.

**B15** ·  198–211 s (measured) · stamp: `constructed · not built`

> I'll measure four things: whether every quote really appears in the posting; misreads, like 'preferred' read as 'required'; two errors kept apart, clearing the applicant for a requirement they don't meet, and ruling out a posting they'd qualify for; and how often it says 'I cannot tell'.

**B16** ·  211–226 s (measured) · stamp: `constructed · not built`

> I'll break it on purpose at least five times: a quote with one word changed, an either-or rule, a posting silent on sponsorship, a board that refuses. And the failure I'm predicting now: a quote copied word for word, but 'five years preferred' treated as a requirement, caught by a separate check.

**B17** ·  226–245 s (measured) · stamp: `plan · my bar, set Nov 21`

> It worked if at least twenty-seven of thirty held-out decisions match my labels and my checks catch every deliberate failure. It didn't work if the reader misquotes a posting, clears even one unmet requirement, or wrongly rules out more than one eligible posting, regardless of the overall score. I'll label about sixty postings by hand, including thirty randomly picked rejects, and set thirty aside before tuning.

**B18** ·  245–251 s (measured) · stamp: `constructed · not built`

> One honest limit: a set this small can show me where it fails. It can't prove it works on every posting.

## Close

**BOUT** ·  251–254 s (measured) · stamp: `—`

> Fine Print. Suketh Reddy Produtoor.

Total so far: 254 s (4.2 min) of a 300 s cap.
