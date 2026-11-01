# Label audit (2026-10-31T21:44:48Z, after the experiment)

Made by `python3 -m agent audit` from the saved replies in `evidence/claude/experiment/`. No Claude call. My hand labels (`experiment/labels.csv`, commit `7327ccd`) are read as they are and not changed.

| Compared with | Baseline, dev | Revision, dev | Baseline, held-out | Revision, held-out |
|---|---|---|---|---|
| My hand labels | 3/10 | 7/10 | 4/10 | 8/10 |
| The written rule (record) | 10/10 | 6/10 | 10/10 | 6/10 |

My hand labels agree with the written rule on 3/10 dev and 4/10 held-out postings.

| Split | Job ID | Company | Title | My label | Rule (record) | Rule parts not met | Baseline | Revision |
|---|---|---|---|---|---|---|---|---|
| dev | 7697137 | Pinterest | Machine Learning Engineer II, Visual AI | Not Relevant | Not Relevant | skills | Not Relevant | Not Relevant |
| held-out | 7838591 | Pinterest | University Grad Software Engineer 2027 (USA) | Not Relevant | Relevant | none | Relevant | Relevant |
| dev | 8015547 | Pinterest | Security Software Engineer II, Detection and Response | Not Relevant | Not Relevant | skills | Not Relevant | Not Relevant |
| held-out | 8162046 | Pinterest | Machine Learning Engineer II, Responsible AI | Not Relevant | Not Relevant | skills | Not Relevant | Not Relevant |
| dev | 8213988 | Pinterest | Software Engineer II, Data Analytics & Engineering | Not Relevant | Relevant | none | Relevant | Relevant |
| held-out | 8227344 | Pinterest | Software Engineer II, EPD Ads | Not Relevant | Not Relevant | skills | Not Relevant | Not Relevant |
| dev | 7661919 | Twilio | Software Engineer - Video | Relevant | Not Relevant | experience | Not Relevant | Relevant |
| held-out | 7816159 | Twilio | Software Engineer L2-Messaging API | Relevant | Relevant | none | Relevant | Relevant |
| dev | 8009057 | Twilio | Software Engineer L3 | Relevant | Not Relevant | experience | Not Relevant | Relevant |
| held-out | 8026207 | Twilio | Software Engineer, Platform Engineering (L2) | Not Relevant | Relevant | none | Relevant | Relevant |
| dev | 8026211 | Twilio | Software Engineer, Platform Access (L2) | Not Relevant | Relevant | none | Relevant | Relevant |
| held-out | 8100236 | Twilio | Software Engineer (L2) | Relevant | Not Relevant | experience | Not Relevant | Relevant |
| dev | 5551532004 | Figma | Software Engineer - Machine Learning | Not Relevant | Not Relevant | skills, experience | Not Relevant | Not Relevant |
| held-out | 5551686004 | Figma | Software Engineer - Data Infrastructure | Relevant | Not Relevant | experience | Not Relevant | Relevant |
| dev | 5551730004 | Figma | Software Engineer - AI Product | Relevant | Not Relevant | skills, experience | Not Relevant | Not Relevant |
| held-out | 5552530004 | Figma | Software Engineer - C++ | Relevant | Not Relevant | experience | Not Relevant | Relevant |
| dev | 5552549004 | Figma | Software Engineer - Distributed Systems | Relevant | Not Relevant | experience | Not Relevant | Relevant |
| held-out | 5552560004 | Figma | Software Engineer - Growth & Monetization | Relevant | Not Relevant | experience | Not Relevant | Relevant |
| dev | 5691886004 | Figma | Software Engineer - AI Platforms | Relevant | Not Relevant | experience | Not Relevant | Relevant |
| held-out | 5691911004 | Figma | Software Engineer - Full Stack | Relevant | Relevant | none | Relevant | Relevant |
