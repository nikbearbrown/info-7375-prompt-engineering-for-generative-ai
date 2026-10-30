# FRICTIONAL — Job-Search Agent 1

## Oct 25, 2026

### Choosing the board
Today, I started by understanding the assignment requirements and exploring different job boards to see which one would work best for my agent. With Claude's help, I compared seven companies based on their job postings, Data/AI roles, and whether their APIs were accessible. I also looked into how to identify new postings using job IDs instead of update dates.

Claude recommended Databricks, and mentioned that watching all five Greenhouse boards would raise the odds of seeing a new posting. I decided to stick with Databricks for now instead of monitoring all five boards. It had the highest number of job postings and more Data/AI-related roles, which fit what I wanted my agent to focus on. Also, since this is the first assignment, I felt it would be better to get one board working properly and test everything before making it more complicated.

### Changing my rule
Today, I made two changes to my relevance rule. First, I added early-career Software Engineer roles because I realized Priya could be a good fit for those jobs even if the title doesn't mention AI or Data.

Later, Claude applied my rule to the real Databricks job titles and showed me where it gave results I didn't expect. I decided my rule was missing keywords like GenAI and Data Science, and was also allowing some senior roles and internships that weren't suitable for Priya. So I updated the keywords and exclusions so the rule matched what I actually meant. My cases 9, 10 and 12 failed before the change and passed after, and the baseline went from 9 relevant postings to 8.

These changes helped me understand that my original rule wasn't perfect and that testing it against real job postings is important.

### What surprised me
I was surprised that out of 896 postings, only 8 passed my rule. Initially, I thought at least a few of them would be suitable for Priya, but after reading all 8 job descriptions myself, I realized none were actually a good fit. 4 required 6+ years, 1 required 8+ years, 1 required 3+ years of legal/contracts work, 1 said it wasn't for new grads, and 1 required citizenship. This made me realize that matching keywords in job titles isn't enough to decide whether a job is relevant.

### What I accepted and rejected from Claude
I accepted Claude's suggestion to use Databricks and its help with the implementation and tests. I also used the issues Claude found in my rule to make some changes, like adding missing keywords and excluding senior roles and internships.

I rejected the suggestion to monitor five boards because I wanted to get one board working properly first. I also didn't just accept Claude's comment that two jobs were close to Priya's target roles based on their titles. I checked all 8 descriptions myself and decided none were suitable. This helped me understand why I shouldn't rely completely on Claude's judgments.

## Oct 26, 2026

Today was more tedious than I expected, but I learned a lot from actually reading the postings one by one. The biggest surprise was that some jobs looked like a really good match at first, but one small requirement completely changed the label, like the AI Engineer role that was a good fit except that it said it was not for new grads. It was also surprising that none of the 20 jobs I labeled were relevant. That made me realize that, in my 20, Databricks didn't have roles that fit someone with Priya’s background right now, even when the job titles sound promising.
Claude Code also caught a couple of things I probably would have missed, especially the difference between just saying “Remote” and actually meaning remote in the US, and the fact that jobs I had already read should not go into the held-out set. One decision I made myself was that if experience is not clearly stated, I should look at the responsibilities and skills instead of automatically rejecting the job. The most frustrating part was honestly fixing the label sheet because I had to deal with the Numbers/CSV format, a typo, and the missing header before it was finally correct.

## Oct 27, 2026

What surprised me most was that just changing one sentence in my prompt made such a big difference. The baseline made the same mistake in 9 out of 10 held-out jobs, but the revised prompt didn't make that mistake at all. I was also surprised that the chat response had formatting issues that made it fail validation, while the agent used another model without me choosing it. This made me realize that giving AI more freedom doesn't always make it better.

One thing I still couldn't figure out is how well my agent identifies good jobs, because all 20 postings I labeled were not relevant. In JS2, I would first improve my relevance rule so it looks at the actual job descriptions instead of just titles. I realized that titles alone can be misleading, and I don't want my agent to miss suitable opportunities or recommend the wrong ones.

When Claude Code found mistakes in my sign-off, I was a little frustrated because I thought I was almost done. But it also made me realize how important it is to verify what I actually did instead of just assuming everything was correct.
