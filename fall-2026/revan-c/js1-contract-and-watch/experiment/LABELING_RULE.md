# Hand-labeling rule for the prompt experiment

**Reviewed and revised by:** Revan Somshekhar Chonnad · **First draft:** AI-assisted · **Revised:** 2026-10-31, before labeling the 20 experiment postings and before any Claude experiment calls. The posting-selection and split-seed details were added before labeling. Record any later revision before looking at experiment results.

## What “worth applying” means

For the fictional Aarav Patel résumé in `resumes/aarav-patel.json`, label a posting **`relevant`** when I would spend roughly 20–30 minutes tailoring and submitting an application based on the posting as written. This is an application decision, not a claim that Aarav would get an interview, satisfy every preference, or meet an employer's authorization requirements. Use the posting's title, location, and full description together; do not use the agent's or Claude's verdict to decide the hand label.

Label **`relevant` only if all five checks below pass**. Otherwise label **`not_relevant`** and record the first decisive reason plus any other material reasons.

1. **Work and role.** The main work is software engineering with a substantial backend, platform, infrastructure, DevOps, or reliability component. A general software engineer or full-stack role passes if the description makes that component substantial. Reject a role whose main work is mobile or front-end development, management, sales, recruiting, IT administration, security compliance, or ML research rather than building software systems. Reject unpaid work and third-party staffing pass-throughs when the posting identifies them.
2. **Place.** The posting permits work in the Boston area, or explicitly permits remote work from Massachusetts or anywhere in the United States. Read both the listed location and location restrictions in the description. A role tied to another city without a stated Boston or eligible remote option fails. If the work location cannot be determined, fail this check and note the uncertainty.
3. **Level.** Reject titles marked Senior, Sr., Staff, Lead, Principal, Director, or Manager. Reject a stated **required** minimum of four or more years of relevant experience; Aarav's résumé records two years. A three-year requirement may be a reasonable stretch if the work and skills fit. A year count or technology marked only “preferred” or “nice to have” is not a hard requirement. Reject a stated mandatory credential or specialist background that the résumé does not show.
4. **Credible fit.** Identify at least two concrete requirements or central duties supported by Aarav's listed experience, projects, or shipped skills. At least one must relate to backend services, distributed systems, platform tooling, cloud infrastructure, or operations. Do not count a technology mentioned only in generic company text, an optional technology list, or `skills.familiar_with_not_shipped` as shipped experience. A plausible adjacent skill may support a stretch role, but it does not satisfy an explicit mandatory qualification by itself.
5. **Application barrier.** Reject an explicit restriction that rules out this persona, such as “no sponsorship now or in the future,” a citizenship requirement, or a required clearance the résumé does not show. Silence about sponsorship or E-Verify is **unknown**, not proof of eligibility and not an automatic rejection. Note that uncertainty for follow-up; do not claim the employer can sponsor or participates in E-Verify.

## Which postings, and how they are split

Chosen 2026-10-31, before any posting was labeled:

- **Selection:** every posting in `evidence/klaviyo_2026-10-31_preimplementation_live.json` whose title contains one of the résumé's `target_titles` phrases, as a lowercase substring. That is exactly 20 postings, with no sampling. Known limitation: 13 of the 20 titles contain Senior, Sr., Lead, or Principal, so check 3 decides many labels by title alone.
- **Split:** after all 20 are labeled, a stratified split into 10 development and 10 held-out postings by hand label, made once with seed **7375** (`experiment.split`).
- **Sampling report:** its 5 postings come from the development set only.

## How to record each hand label

Before running either prompt on a posting, save its posting ID, title, source snapshot or URL, label date, binary label, the decisive posting phrases, matching résumé fields, and any uncertainty. Distinguish **required** from **preferred** language in the note. Keep the 10 held-out labels and their posting contents out of prompt revision decisions until the revision is frozen. If information needed for a check is absent, use `not_relevant` with an `insufficient information` note rather than guessing.

This hand rule deliberately differs from the agent's mechanical rule in `CONTRACT.md`: it reads the whole description, separates required from preferred qualifications, checks actual work location restrictions, and notices explicit application barriers. Any disagreement between the two verdicts is a result to explain, not a label to silently correct.
