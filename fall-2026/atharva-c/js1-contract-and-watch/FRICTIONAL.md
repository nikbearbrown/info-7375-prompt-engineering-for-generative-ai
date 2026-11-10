# FRICTIONAL — Job-Search Agent 1

**How this file was made.** Each entry has two parts:
- **What happened:** facts Claude Code compiled from the commit log and run
  files, with commit hashes from my local repo.
- **In my words:** my own answers, recorded word for word, uncorrected, in an
  interview on 2026-10-31.

I wrote no running log during the work. These reflections were given on
2026-10-31, looking back.

---

## 2026-10-29 (Thu): the contract

**What happened**
- My first commit of `CONTRACT.md` was empty (0 insertions).
- Terminal commands kept failing because the shell was in my home folder,
  not the project.
- Cloudflare's board showed 0 US matches, which showed that "US location"
  needed an exact definition.
- The contract was later written through an interview and amended into that
  first commit (`19bbfae`) before any code.

**In my words**
> Its hard at the start because i was not sure what the requirements were and what i had to do. so it took me some time to write contact at first

## 2026-10-30 (Fri): labeling, and what Claude got wrong

**What happened: labeling**
- My first four clicks were all "Relevant", including a Staff role and a
  Dublin role that my own rule excluded. I was asked again and changed them.
- I had answered two US+Canada postings differently, and settled on "must be
  purely US" (dated note in `LABELING_RULE.md`).
- Result: 1 of 20 relevant. I chose to keep the set and report it, rather
  than draw more postings.

**In my words**
> in the labeling process while clicking on the option i had 2/3 options which were similar or meet the requirements so it took me some time and than the same questions were asked and then i had to change my answers and think more deeply about it

On keeping the 1-of-20 set:
> it should be honest and as not all the requirements will meet all the time so i had 20 question because if the data set is more it has more data to select from and it can be more accurate

**What happened: Claude's mistakes I picked out**
- Claude's first code treated "Remote **in** Canada" as the US state Indiana
  (`IN`). It was caught before any run.
- In the experiment, Claude invented résumé fields that don't exist
  (`resume.experience_years`, `resume.experience.years`,
  `resume.work_experience_years`). The validator rejected all 5 of them.
- Claude said "not relevant" to my one "relevant" posting (7776179) every
  time, because it asks for 8+ years.

**In my words**
> we have to keep an eye on claude because it can change the requirements

- Would I have noticed the made-up field without the validator? **No.**
- Who was right about 7776179, the 8+ years posting? **Claude.** My label
  was wrong: my labeling rule ignored required years.

## 2026-10-31 (Sat): run 2 and getting it onto GitHub

**What happened**
- Run 2 found 18 new postings (746 total).
- Getting the work onto GitHub took most of the night:
  - I set the API key to the placeholder text twice.
  - A token with no permissions caused `403` errors.
  - A token was exposed in a screenshot I shared, so it has to be deleted.
  - VS Code was signed in as a second GitHub account of mine, not
    `Arc-211`. That account's name is left out here because the class repo
    stores no full names.
  - I declined VS Code's "Create Fork" offer.
  - What finally worked: the `gh` browser login as `Arc-211`, which opened
    PR nikbearbrown/info-7375-prompt-engineering-for-generative-ai#31.

**In my words**
> the tokens and the git hub part if possible i would have done it in more systematic way
> i tried it on everything i should i have been patience and looked at the possibility without rushing into it

## Unresolved

**What bothers me most:** the experiment had only 1 relevant posting.

**What I'd change next time:**
> label more of them, or change your labeling rule.

**Also open:**
- Skill matching counts English words ("react", "go-to-market").
- A second model (Haiku) appeared in run 2's usage, unexplained.
- My labeling rule ignored years, and I now think it should not have.
