# FRICTIONAL — honest log

The **What happened** notes were initially drafted from the commit history and session record. The reflections below record my stated checks and decisions; the cited commits show when the work happened.

## 1. The first board would have judged everything irrelevant

**What happened.**
- **The plan:** Contract v1 (`2091127`) named the `greenhouse` board.
- **The problem:** checking it live showed 20 jobs, none in Boston and none containing "remote". The rule would have marked all 20 `not_relevant`.
- **The fix:** probing other public Greenhouse boards found Klaviyo, which had 156 jobs and several Boston engineering roles. Contract v2 (`021999d`) switched to `klaviyo`, added seniority and role-type conditions, and spelled out skill normalization.

**My reflection:** I checked the first board and Klaviyo myself, including the wider set of board probes. I chose Klaviyo because the first board had no Boston or remote jobs for this rule to evaluate meaningfully. I learned that a technically working watch is not useful if its source has no plausible matches.

## 2. The contract read fields the résumé did not have

**What happened.**
- **The problem:** v1 read `target_titles`, `visa`, and `years_experience`, but none was in `resumes/aarav-patel.json`.
- **The fix:** I added them in `994646d`, including `target_role.excluded` as an array with "mobile roles".

**My reflection:** The mismatch was pointed out to me. I chose the missing fields and reviewed their fictional values after they were added, especially the mobile exclusion and the two-year experience count. A contract that names fields absent from its input cannot be applied as written.

## 3. My review of Claude's first implementation

**What happened.** After `1397a6f` I reviewed the code and wrote these decisions.
- **Accepted:**
  - the five-condition rule;
  - the conservative seniority and mobile exclusions;
  - case-sensitive matching of résumé list values;
  - refusing duplicate ids;
  - sending only selected résumé fields to Claude.
- **Modified:** the skills evidence. Its single combined `resume_field` was not a résumé path; it became one exact path per matched skill.
- **Modified:** the validator and prompt, which disagreed. I confirmed that an output citing `years_experience` as the string `"2"` passed the validator, although the prompt asked for a number. The validator now requires the same JSON type, and the prompt no longer says "verbatim".
- **Rejected as a claim:** treating the baseline prompt as applying my five conditions. It asks a different question ("worthwhile application"), and a validator pass proves format and citations, not a correct verdict.
- **Asked for tests:** rule evidence must be true, not just well-shaped, and a failed output write must leave state unchanged.

Applied in `87f68dd`. The new tests failed on the old code. One of them, the write-failure test, failed only because the old code raised a raw `OSError`; the old code already left state unchanged.

**My reflection:** I read the contract, rule, validator, and prompt and requested changes to evidence citations, numeric types, prompt wording, and write-failure handling. I ran the original contract tests but did not read their assertions closely. I later read the new review tests and checked that they failed on the old version and passed after the fixes. Passing the original suite had not established that every contract detail was covered.

## 4. Live run 2 crashed on the first try

**What happened.**
- **The failure:** at 05:47 UTC, run 2 crashed with an uncaught SDK `TypeError`. No API key was visible to the process: I had set it in a different way from how I ran the command.
- **What was safe:** the raw response had been saved (as the contract requires). No run file or state was written, so state stayed at run 1.
- **The fix:** Claude added a credential check before any fetch (`b1aa320`). The failed attempt's evidence file is kept and recorded in `evidence/PROVENANCE.md`.
- **The retry:** run 2 succeeded at 05:51 UTC (`5fc0b68`).

**My reflection:** I ran the failed live command, checked that the raw response was saved while state stayed at 154 IDs, and reran it successfully once the key was available to the process. I learned to check credentials before a fetch can leave partial evidence behind.

## 5. The only Claude failures were formatting, not judgment

**What happened.**
- **Across 60 experiment and sampling calls,** 4 outputs were `invalid`. Three cited `devops_cicd` without the `skills.` prefix, and one was broken JSON with a code-like expression inside a field.
- **All 56 valid outputs matched my reviewed labels.**
- **What that means for the experiment:** the pass-rate differences between the baseline and revision 1 are one rejection each, in opposite directions.
- **I did not loosen the validator after seeing this.** Doing so would have changed the measurement after the results.

**My reflection:** I inspected the four rejected responses and confirmed that their failures were citation paths or broken JSON, not different visible verdicts. I kept the validator unchanged after seeing the results; loosening it then would have changed how the experiment was scored. Format compliance and agreement with my labels are separate claims.

## 6. Unintended edits caught by diff

**What happened.**
- **The note fix:** Claude's first attempt to correct one note in `labels.csv` rewrote every line, because it switched line endings.
- **How it was caught:** `git diff --stat` showed 21 changed lines.
- **The fix:** the file was restored and the edit redone as a one-line change (`335d280`).

**My reflection:** I saw that the diff changed 21 lines for a one-note correction, restored the file, and checked that the final edit affected only the intended row. I learned to inspect the diff even for a small CSV change.

## 7. The chat surfaces: a wrong window, then my own data

**What happened.**
- **Surface 1, first try:** I pasted the prompt into the Claude Code session building this project instead of a new claude.ai chat, and saved that reply as the result. Claude Code compared the file with its own earlier reply, found them identical, and said it could not count: that session already knew my hand label. I reran it in a new claude.ai chat; that reply passed the validator.
- **Surface 2, first run:** the reply named two of my real projects, which were in neither the prompt nor the attached file, and gave me résumé advice. The committed copy redacts them; the raw reply stays in `private/`.
- **Surface 2, second run:** after I removed claude.ai memory, the projects no longer appeared. Both runs ignored the JSON format.

**My reflection:** The wrong-window paste was caught by comparing its reply with an earlier answer from the session that already knew the label; I reran the paste in a fresh chat. The file run then used real projects outside the fictional input, so I removed account memory and tried again. The second file reply no longer named those projects, but both file replies were prose. These few runs show why I must check the active session and its context, while leaving the cause of the formatting difference unresolved.

## Open or unresolved

- **The labeling pace.** The empty sheet was created at 01:28 local time and the 20 filled rows were committed at 01:35. An AI assistant drafted the rows from the saved postings during that interval; it was not 20 independent full reads by me in seven minutes. After the rows were committed at 01:35 and before the split at 02:02, I read all 20 full postings and checked each decision against my rule. That read changed no label: the only later edit to `labels.csv` was one note (`335d280`, 02:01). I also reviewed the proposed rule and added the posting-selection and split-seed details before labeling. The labels are my reviewed judgments, with assisted drafting disclosed; their small, senior-heavy set still limits what the experiment can show.
- **Why the file surface ignored the format.** Two file runs returned prose where one paste run returned JSON. The runs are too few to tell why.
- **Prompt injection.** No posting with injected instructions was ever tested.
- **The judge saw less than I did.** Claude receives no `experience` or `projects`, and my labels used them.
