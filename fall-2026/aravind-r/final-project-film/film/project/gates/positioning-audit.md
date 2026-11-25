# Positioning audit — Readback project film

Gate (my brief, 23 Nov 2026): every mention of meetings, recaps, AMI (or an AMI meeting ID) or C4 sits in Methods or Evaluation, in a scene tagged "test case"; the executive summary has none; the first minute says Readback is for any AI feature's acceptance criteria. Narration from `beat_sheet.json`; on-screen strings from every frame of every scene (`strings_dump.py`, 24 fps). Spoken "Reed-back" is shown as Readback.

## 1 · Narration that mentions the test case

| Beat | Part | Starts | Sentence | Terms | Verdict |
|---|---|---|---|---|---|
| B09 | methods | 1:32.0 | I chose a meeting-recap feature on the AMI Meeting Corpus, because AMI ships human-written decision lists. | AMI, meeting, Meeting, recap | OK |
| B09 | methods | 1:32.0 | I use ten of its meetings, which hold eighty-six decisions. | meetings | OK |
| B10 | methods | 1:48.4 | The feature under test is a meeting recap: my own prompt, running on Claude. | meeting, recap | OK |
| B10 | methods | 1:48.4 | I ran it on every meeting on October fourteenth, so ten real recaps already exist. | meeting, recaps | OK |
| B11 | methods | 1:57.6 | The decisions clause is anchored to AMI's list, so there's a right answer to check against. | AMI | OK |
| B12 | methods | 2:09.6 | Before any judge runs, I'll mark which of AMI's decisions each recap covers. | AMI, recap | OK |
| B13 | methods | 2:19.2 | Then three judges score every recap: Claude, a second provider's model, and a local open-weight model. | recap | OK |
| B14 | methods | 2:30.8 | In one real recap, two quick yeses became a decision. | recap | OK |
| B15 | methods | 2:42.2 | The data and the ten recaps are in my repository, and Claude runs here on my subscription. | recaps | OK |
| B18 | evaluation | 3:23.0 | The PM revises the flagged clause, and I re-measure judge agreement on meetings held out from the revision. | meetings | OK |

## 2 · On-screen strings that mention the test case

| Scene | Part | On screen (s into the beat) | String | Terms | Scene tagged "test case"? | Verdict |
|---|---|---|---|---|---|---|
| B09_TestBench | methods | 2.2–16.3 | AMI data | AMI | yes | OK |
| B09_TestBench | methods | 5.4–13.2 | a meeting-recap | meeting, recap | yes | OK |
| B09_TestBench | methods | 7.8–13.2 | the AMI Meeting | AMI, Meeting | yes | OK |
| B09_TestBench | methods | 7.8–16.3 | AMI corpus · CC BY 4.0 | AMI | yes | OK |
| B09_TestBench | methods | 13.5–16.3 | IS1004d | IS1004d | yes | OK |
| B09_TestBench | methods | 13.6–16.3 | IS1009d | IS1009d | yes | OK |
| B09_TestBench | methods | 13.6–16.3 | ES2006d | ES2006d | yes | OK |
| B09_TestBench | methods | 13.7–16.3 | ES2008c | ES2008c | yes | OK |
| B09_TestBench | methods | 13.7–16.3 | ES2010b | ES2010b | yes | OK |
| B09_TestBench | methods | 13.8–16.3 | ES2011b | ES2011b | yes | OK |
| B09_TestBench | methods | 13.8–16.3 | ES2013d | ES2013d | yes | OK |
| B09_TestBench | methods | 13.8–16.3 | IS1003c | IS1003c | yes | OK |
| B09_TestBench | methods | 13.8–16.3 | IS1005c | IS1005c | yes | OK |
| B09_TestBench | methods | 13.9–16.3 | ES2007a | ES2007a | yes | OK |
| B10_Feature | methods | 0.0–0.7 | AMI corpus · CC BY 4.0 | AMI | yes | OK |
| B10_Feature | methods | 0.0–0.7 | IS1003c | IS1003c | yes | OK |
| B10_Feature | methods | 0.0–0.7 | ES2011b | ES2011b | yes | OK |
| B10_Feature | methods | 0.0–0.7 | ES2006d | ES2006d | yes | OK |
| B10_Feature | methods | 0.0–0.7 | ES2010b | ES2010b | yes | OK |
| B10_Feature | methods | 0.0–0.7 | IS1004d | IS1004d | yes | OK |
| B10_Feature | methods | 0.0–8.5 | AMI data | AMI | yes | OK |
| B10_Feature | methods | 0.0–0.7 | ES2008c | ES2008c | yes | OK |
| B10_Feature | methods | 0.0–0.7 | IS1005c | IS1005c | yes | OK |
| B10_Feature | methods | 0.0–0.7 | ES2013d | ES2013d | yes | OK |
| B10_Feature | methods | 0.0–0.7 | ES2007a | ES2007a | yes | OK |
| B10_Feature | methods | 0.0–0.7 | IS1009d | IS1009d | yes | OK |
| B10_Feature | methods | 1.5–8.5 | AMI ES2007a transcript · CC BY 4.0 | AMI, ES2007a | yes | OK |
| B10_Feature | methods | 2.5–5.2 | CONSTRUCTED · my recap prompt | recap | yes | OK |
| B11_Rubric | methods | 0.0–11.6 | AMI data | AMI | yes | OK |
| B11_Rubric | methods | 0.0–11.6 | Recaps | Recaps | yes | OK |
| B11_Rubric | methods | 0.0–0.7 | 10 real recaps · claude-opus-5-5 · 14 Oct 2026 | recaps | yes | OK |
| B11_Rubric | methods | 0.0–0.7 | AMI ES2007a transcript · CC BY 4.0 | AMI, ES2007a | yes | OK |
| B11_Rubric | methods | 1.8–11.6 | Every decision … appears in the recap | recap | yes | OK |
| B11_Rubric | methods | 4.7–11.6 | C4 · Don't report open | C4 | yes | OK |
| B11_Rubric | methods | 8.5–11.6 | … 7 in this meeting | meeting | yes | OK |
| B11_Rubric | methods | 8.5–11.6 | AMI ES2007a · CC BY 4.0 | AMI, ES2007a | yes | OK |
| B11_Rubric | methods | 8.5–11.6 | ES2007a · DECISIONS | ES2007a | yes | OK |
| B12_Labels | methods | 0.0–0.6 | AMI ES2007a · CC BY 4.0 | AMI, ES2007a | yes | OK |
| B12_Labels | methods | 0.0–0.6 | Every decision … appears in the recap | recap | yes | OK |
| B12_Labels | methods | 0.0–8.9 | Recaps | Recaps | yes | OK |
| B12_Labels | methods | 0.0–8.9 | AMI data | AMI | yes | OK |
| B12_Labels | methods | 0.0–1.1 | C4 · Don't report open | C4 | yes | OK |
| B12_Labels | methods | 0.0–0.6 | ES2007a · DECISIONS | ES2007a | yes | OK |
| B12_Labels | methods | 0.0–0.6 | … 7 in this meeting | meeting | yes | OK |
| B12_Labels | methods | 0.8–8.9 | C4 | C4 | yes | OK |
| B12_Labels | methods | 1.5–8.9 | IS1004d | IS1004d | yes | OK |
| B12_Labels | methods | 1.7–8.9 | ES2006d | ES2006d | yes | OK |
| B12_Labels | methods | 1.9–8.9 | IS1009d | IS1009d | yes | OK |
| B12_Labels | methods | 2.0–8.9 | ES2008c | ES2008c | yes | OK |
| B12_Labels | methods | 2.1–8.9 | ES2010b | ES2010b | yes | OK |
| B12_Labels | methods | 2.2–8.9 | ES2011b | ES2011b | yes | OK |
| B12_Labels | methods | 2.4–8.9 | ES2013d | ES2013d | yes | OK |
| B12_Labels | methods | 2.5–8.9 | IS1003c | IS1003c | yes | OK |
| B12_Labels | methods | 2.6–8.9 | IS1005c | IS1005c | yes | OK |
| B12_Labels | methods | 2.7–8.9 | ES2007a | ES2007a | yes | OK |
| B13_Judges | methods | 0.0–0.6 | ES2008c | ES2008c | yes | OK |
| B13_Judges | methods | 0.0–0.6 | ES2011b | ES2011b | yes | OK |
| B13_Judges | methods | 0.0–11.2 | C4 | C4 | yes | OK |
| B13_Judges | methods | 0.0–0.6 | IS1003c | IS1003c | yes | OK |
| B13_Judges | methods | 0.0–0.6 | IS1009d | IS1009d | yes | OK |
| B13_Judges | methods | 0.0–11.2 | AMI data | AMI | yes | OK |
| B13_Judges | methods | 0.0–0.6 | ES2007a | ES2007a | yes | OK |
| B13_Judges | methods | 0.0–0.6 | ES2010b | ES2010b | yes | OK |
| B13_Judges | methods | 0.0–0.6 | ES2013d | ES2013d | yes | OK |
| B13_Judges | methods | 0.0–0.6 | IS1005c | IS1005c | yes | OK |
| B13_Judges | methods | 0.0–11.2 | Recaps | Recaps | yes | OK |
| B13_Judges | methods | 0.0–0.6 | IS1004d | IS1004d | yes | OK |
| B13_Judges | methods | 0.0–0.6 | ES2006d | ES2006d | yes | OK |
| B14_Trace | methods | 0.0–10.8 | AMI data | AMI | yes | OK |
| B14_Trace | methods | 0.0–10.8 | Recaps | Recaps | yes | OK |
| B14_Trace | methods | 0.0–10.8 | C4 | C4 | yes | OK |
| B14_Trace | methods | 5.2–10.8 | ES2010b · AMI · CC BY 4.0 | AMI, ES2010b | yes | OK |
| B14_Trace | methods | 6.3–10.8 | real recap · claude-opus-5-5 · 14 Oct 2026 | recap | yes | OK |
| B14_Trace | methods | 6.3–10.8 | AMI's DECISIONS list: “will consider including … a locator function” | AMI | yes | OK |
| B14_Trace | methods | 10.3–10.8 | C4 · revised by the PM | C4 | yes | OK |
| B15_Have | methods | 0.0–0.6 | AMI data | AMI | yes | OK |
| B15_Have | methods | 0.0–0.6 | C4 | C4 | yes | OK |
| B15_Have | methods | 0.0–0.6 | real recap · claude-opus-5-5 · 14 Oct 2026 | recap | yes | OK |
| B15_Have | methods | 0.0–0.6 | AMI's DECISIONS list: “will consider including … a locator function” | AMI | yes | OK |
| B15_Have | methods | 0.0–0.6 | ES2010b · AMI · CC BY 4.0 | AMI, ES2010b | yes | OK |
| B15_Have | methods | 0.0–0.6 | C4 · revised by the PM | C4 | yes | OK |
| B15_Have | methods | 0.0–0.6 | Recaps | Recaps | yes | OK |
| B15_Have | methods | 1.1–13.2 | AMI data · 10 meetings | AMI, meetings | yes | OK |
| B15_Have | methods | 1.1–13.2 | 10 real recaps | recaps | yes | OK |
| B16_Planted | evaluation | 0.0–0.5 | 10 real recaps | recaps | yes | OK |
| B16_Planted | evaluation | 0.0–0.5 | AMI data · 10 meetings | AMI, meetings | yes | OK |
| B16_Planted | evaluation | 5.6–14.2 | C4 | C4 | yes | OK |
| B16_Planted | evaluation | 6.2–14.2 | planted in C4 · one variant per clause, C1–C5 | C4 | yes | OK |
| B17_Kappa | evaluation | 0.0–0.6 | C4 | C4 | yes | OK |
| B17_Kappa | evaluation | 0.0–0.6 | planted in C4 · one variant per clause, C1–C5 | C4 | yes | OK |
| B18_BeforeAfter | evaluation | 2.1–11.5 | C4 | C4 | yes | OK |
| B18_BeforeAfter | evaluation | 2.5–11.5 | C4 · revised | C4 | yes | OK |
| B18_BeforeAfter | evaluation | 6.3–11.5 | held-out meetings | meetings | yes | OK |
| B19_Scorecard | evaluation | 0.0–5.6 | held-out meetings | meetings | yes | OK |
| B19_Scorecard | evaluation | 0.0–0.6 | C4 | C4 | yes | OK |
| B19_Scorecard | evaluation | 0.0–0.6 | C4 · revised | C4 | yes | OK |
| B20_Close | evaluation | 0.0–0.6 | held-out meetings | meetings | yes | OK |

## 3 · Executive summary (B01, B02, B03)

References to meetings, recaps, AMI or C4, spoken or on screen: **0**.

## 4 · The first minute (0:00–1:00): what Readback is for

Every line heard before 1:00 that says what Readback is for, with the time it starts (from `mp3/words.json`):

- **B01 · 0:00.0** — "AI features ship against acceptance criteria a PM wrote."
- **B01 · 0:04.0** — "Those criteria become a rubric: the checklist an AI judge grades the output against."
- **B01 · 0:09.0** — "When a judge reads a criterion differently than the PM meant it, the eval passes, and the wrong behaviour ships."
- **B02 · 0:17.8** — "And where an eval is the launch gate, a misread criterion ships wrong behaviour at scale, with a passing score attached."
- **B03 · 0:27.3** — "Readback will find the criterion the judges read differently, and ask the PM what they meant, before anyone trusts the score."
- **B03 · 0:33.3** — "It's module one of a bigger vision: a copilot for what PMs write for AI."
- **B03 · 0:37.8** — "Readback is planned; nothing has run yet."

## Result: **PASS**

