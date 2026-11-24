# FRICTIONAL — Final Project Film

## November 23, 2026

### Project Decision

My original project idea was a question-answering tool for GitHub Actions documentation. However, I have decided to continue with my job-search agent because the final project requires an agentic system, and my original project was mainly a question-answering tool.

I have already built and tested several parts of the job-search agent through JS1 and JS2 and have been working on the filtering component in JS3.

Continuing with this project will allow me to improve my existing work and build a more complete agent.

### My Predictions

Before comparing my agent with existing job-search tools, I expect:

- Existing job-search tools will have a better user interface and access to more job postings.
- At least one tool will provide a job recommendation or match score without clearly explaining why the candidate is suitable.
- At least one tool will not provide enough evidence to independently verify its recommendation.
- My agent will make its decisions easier to verify through written rules, saved evidence, and independent checks.
- The hardest part of making the film will be explaining the technical implementation in simple words.

### What I Will Do Next

I will compare LinkedIn, an AI job-matching tool, and Claude with my job-search agent.

I will save dated screenshots, record my observations, and compare the results with my original predictions.

After that, I will prepare my film, demonstrate the work I have completed so far, explain my plans for JS4 and JS5, and define how I will evaluate the final agent.

### LinkedIn Comparison — November 23, 2026

I searched for Machine Learning Engineer positions at Databricks in the United States. LinkedIn returned 99+ results, including Staff-level positions.

I reviewed the Staff Backline Engineer – ML/AI posting. The posting contained Python, MLflow, and Delta Lake, which match Priya's skills. However, the position involves senior-level responsibilities and is not suitable for a candidate with only eight months of professional experience under my filtering rules.

LinkedIn also displayed a medium job-match rating. However, this rating was based on my personal profile and résumé, not Priya's fictional résumé. Therefore, I cannot directly compare this rating with my agent's verdict.

This example shows why my agent needs to consider seniority and experience requirements instead of relying only on matching skills.

I saved three screenshots as evidence of my observations.

### Jobright Comparison — November 23, 2026

I uploaded Priya Nair's fictional résumé to Jobright and searched for Databricks positions.

Jobright displayed a 57% overall match score for the AI Engineer – Forward Deployed Engineering position. It also provided individual scores of 30% for experience level, 40% for skills, and 41% for industry experience.

I found that Jobright provides more information about its recommendations than I initially expected. It shows matching skills and separates the match score into different categories. However, I could not determine how the overall score was calculated from the information displayed.

I also noticed that Jobright marked PyTorch and Scikit-learn as skills Priya possesses, even though neither skill appears in the original résumé.

The job description states that the position is intended for experienced engineers and requires extensive industry experience. Priya has only eight months of professional experience, so I would label this posting as not relevant.

This comparison helped me understand the importance of checking résumé evidence and experience requirements instead of relying only on a numerical match score.

I saved screenshots of the recommendations, match scores, and qualifications as evidence.

### Claude Comparison — November 23, 2026

I asked Claude Sonnet 5.5 to find currently available AI Engineering, Machine Learning Engineering, and Data Engineering positions at Databricks using Priya's skills and professional experience.

Claude could not find a suitable position that it could verify as currently available. Instead of recommending unverified jobs, it explained why several positions did not meet the candidate's requirements.

Claude rejected the AI Engineer – Forward Deployed Engineering position because it was intended for experienced engineers rather than entry-level candidates. This is the same position that Jobright gave a 57% match score.

Claude performed better than I initially expected because it explained its decisions, provided sources, and acknowledged its limitations.

However, it could not reliably access the current Databricks job listings and suggested using the live Greenhouse job board instead. I also noticed that Claude accessed memory during this experiment, so the comparison was not fully isolated.

My agent directly collects postings from public job-board APIs and saves the raw responses for later verification.

I saved two screenshots showing my prompt and Claude's response.

### Overall Comparison Findings — November 23, 2026

After comparing LinkedIn, Jobright, and Claude, I found that each tool has different strengths and limitations.

LinkedIn provides a convenient interface for discovering jobs and reviewing job descriptions. However, I could not directly compare its personalized match rating because it used my personal profile instead of Priya's fictional résumé.

Jobright provides numerical match scores, matching skills, and experience-related scores. However, I observed that it identified two skills that were not explicitly mentioned in Priya's résumé.

Claude provided clear explanations and avoided recommending jobs that it could not verify. However, it had difficulty accessing current job-board data.

My initial predictions were partially correct. Existing tools provided better user interfaces and useful recommendations, but they also provided more explanations than I initially expected.

My agent is not intended to replace these tools. Instead, I want to focus on reproducibility, written filtering rules, saved evidence, independent verification, and human approval.

### Making the Film — November 23, 2026

After completing my comparison of LinkedIn, Jobright, and Claude, I started working on the final project film.

Initially, I considered using slides and a terminal demonstration. However, I decided to use the Brutalist toolkit because I had already used it for my previous films and was familiar with the process.

I used Claude Code to help prepare the narration, animations, and scenes. I also used Kokoro for voice generation and Manim for animations.

### Challenges I Faced

- The initial audio generation failed because FFmpeg was not available in the shell's PATH. This was fixed by updating the PATH.
- Several quality gates failed because of overlapping text, incorrect spacing, low contrast, and elements extending outside the safe area.
- Some scenes had to be modified and rendered multiple times before they passed all the quality gates.
- Even after all the gates passed, I noticed that the Approve and Refuse elements overlapped while watching the film. This was not detected by the automated checks. The scene was corrected, and the film was rendered again.
- I also blurred my LinkedIn profile photo to avoid including unnecessary personal information in the submission.

### Comparing My Predictions with the Results

Initially, I expected that explaining the technical implementation in simple words would be the hardest part of making the film.

Although simplifying the technical details was challenging, the repeated rendering, layout corrections, and quality checks also required a significant amount of effort.

### What I Learned

One important thing I learned is that passing automated quality checks does not necessarily mean that the final output is correct. I still needed to watch the film myself and check for problems that the automated gates did not detect.

This also relates to my job-search agent. Even if an agent passes its automated tests, human review is still important before relying on its results.

### Final Outcome

The final film is 5 minutes and 23 seconds long and includes all four required sections: executive summary, introduction, methods, and evaluation.

All the required quality gates passed after the corrections. The gate reports, build files, screenshots, narration script, and supporting documentation are included in my project folder.

### What I Will Do Next

I will continue building my job-search agent through JS4 and JS5, focusing on planning, verification, memory, and human approval. I will also evaluate the completed agent using relevant and irrelevant postings and deliberate failure cases.