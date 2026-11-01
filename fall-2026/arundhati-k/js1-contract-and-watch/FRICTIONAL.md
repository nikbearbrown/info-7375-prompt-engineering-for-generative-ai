# Friction Log

### 1. Wrong candidate persona — October 31, 2026

I initially used Maya as the fictional candidate, but later realized that her profile was more suited to a product manager than a software engineer. I changed the persona to Rohan Desai so that it matched the new-grad engineering roles I was evaluating.

### 2. Login issues — October 31, 2026

I had trouble logging in and accessing the required features. I tried different options, and selecting Premium Seat helped me get past the issue so I could continue working.

### 3. Changing row 13 before seeing results — October 31, 2026

I initially labeled row 13 as RELEVANT, but then noticed that it did not follow my own rule because the posting required a PhD and focused on an ML role. I corrected the label before looking at Claude's results. I also kept a note in `labels.csv` showing the original and corrected labels. This helped me avoid changing my labels just to match the model's answers.

### 4. Missing the US-location rule — October 31, 2026

While labeling postings 14–16, I missed the US-location requirement. I realized that my labels did not follow the rules consistently. I documented the mistake instead of treating the original labels as correct.

### 5. Ambiguity in the skills requirement — October 31, 2026

One confusing part was the sentence "We work mostly in Java..." I wasn't sure whether mentioning a language as something the company uses should count as a required skill or just a preference. This made the classification difficult because the wording did not clearly distinguish between required and preferred skills.

### 6. Using and reviewing AI suggestions — October 31, 2026

I used both Claude and ChatGPT during the project. Claude reviewed some of the ChatGPT-generated drafts and pointed out that they contained factual mistakes and did not fully reflect my own work. For example, it corrected the description of `run.py` and clarified that the allow-list was based on the host, not the company. I reviewed these corrections and used them to improve my documentation.

### Traceability

I kept notes and supporting evidence for these issues in the project files. For row 13, see the note in `labeling/labels.csv`. For the missed US-location requirement in postings 14–16, see the Honest Limits section in `PROMPT-EXPERIMENT.md`. The Rohan persona change is also reflected in contract commit `122d4f1`.
