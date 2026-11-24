# FRICTIONAL — Final Project Film
Rithika Sankar Rajeswari · INFO 7375 · Agentic Retrieval Lab


## 2026-11-23 (Mon): reading the brief and choosing the scope
- Read Professor Bear's email. This film isn't the same as my October pitch: it has four fixed parts in order (executive summary, what others have done, methods, evaluation), and the executive summary can't contain any "how."
- Noticed the deadline is 11:30 pm, not 11:59.
- Runtime must stay under 4 minutes.
- I made the agentic-retrieval-lab repo public, so the film and README can link straight to the code and results.
- Decided not to film a plan full of "will." If parts of the project weren't done, I wanted to finish them first. I set a 6 pm cutoff for experiments so the film would still get made.

## Inventory before building
- Had Claude Code do a read-only inventory first. Milestone 1 was solid (103 tests, every number in a dated results folder), but nothing after it had started: no dense models, no experiments, no length baseline. The only commit since October was a docs fix.
- Two docs still called the repo private, so I had them fixed.
- Checked the API cost against the run logs. The three logged runs add up to $0.63, not the "$0.68" in my old notes (that figure included unitemized trial runs). The $0.63 covers all the LLM calls (rewrites, leak judge and answer extraction), and I paid it from my own API credits.
- My M5 laptop (16 GB, MPS) could run the small embedding models, so the plan was realistic for one afternoon.

## Pass/fail rules, set before the Milestone 2 runs
- Claude (chat) drafted four rules and I adopted them before any Milestone 2 result existed: (1) tests pass and every number traces to a file, (2) if length alone beats random, dense results are provisional, (3) dense beats BM25 only if the 95% interval is above zero, (4) human vs agent, judged the same way.
- I was told not to change rules 2 and 4 after seeing their results, because that would be moving the goalposts. I didn't.

## Milestone 2 part A: BM25 and the length check
- Claude Code built the evaluation harness (Recall@100, MRR@10, nDCG@10, paired bootstrap) with 16 new tests. The numbers matched ranx, an independent library, to 4 decimals.
- BM25 Recall@100: human 0.642, agent-primary 0.592, support 0.381. The human question beat the agent's main rewrite by 5 points, so the rewrites made keyword search slightly worse.
- Length check: ranking by passage length alone beat random (+0.021, CI 0.004–0.041). By my own rule 2, that made any dense result provisional.
- Claude Code skipped the predict-first step because I'd asked for one full run.

## Milestone 2 part B: dense models, hybrid, and three crashes
- Two full pytest runs crashed with "Python quit unexpectedly" (SIGSEGV, around 13:47). Claude Code traced it to three copies of the OpenMP library (from torch and faiss) loaded in one process, a known macOS clash. The fix was one line: faiss.omp_set_num_threads(1) at dense.py:137.
- I didn't just accept "tests pass." I had it find the crash reports, rerun the suite three times (135 passed each time), and prove that 1-thread and 10-thread search give identical rankings on the real bge embeddings.
- A third crash at 13:53 confused me at first. The dialog showed the process had started at 13:46, before the fix, so it was the old background run, which Claude Code had predicted would crash. The embedding cache survived intact.
- e5 encoded more slowly than bge and hit Claude Code's 10-minute foreground limit, but it finished cleanly in the background.
- Results: bge and e5 beat BM25 by about +0.32 Recall@100. The hybrid beat BM25 but lost to bge alone. The human question came out ahead with every method, and the gap shrank from 5 points to about 1 point with dense models.
- I'm not reading the dense win as real yet. My 200k corpus is built from BM25's near-misses, so it's hard for BM25 and easy for dense models. Dense top-10 passages are also about 10 words shorter, which matches the length bias I'd already confirmed.
- Stopped experimenting there, as planned.
- One thing I couldn't explain: a final check took over 300 s by the tool clock while pytest reported 4.88 s.

## Publishing the project
- Before pushing to a public repo, I ran the secret scan myself. No .env or .npy is tracked, and there's no key pattern in any file. Claude Code then also checked every past commit, and it was clean.
- Pushed M2 as commit 71c42ce. The README headline table is now filled in, with a "Read this first" note saying the results are provisional and why.

## Writing the brief
- Claude (chat) drafted the four-part brief, and Claude Code fact-checked every claim against my result files. It made three corrections I accepted: the $0.63 covers all LLM calls, not just rewrites; "never did better" needed qualifying; and it removed "rules written before results" because the repo couldn't prove it.
- I restored that line with honest wording ("set before the Milestone 2 runs, drafted with Claude, adopted by me"), because the rules were written in chat before Part A ran.
- I rewrote the human-vs-agent line because the e5 gap is too small to call.

## Building the film
- A new reel folder, so the October one stays untouched. I reused my October characters, including the two librarians for keyword vs meaning search.
- Each part opens with a title card, so the four-part structure is visible.
- The example is a real query from my data (ID 846513), where BM25 found the correct passage for the human question but not for the agent's rewrite.
- Gate T failed on the first final run. It read the balance scales' thin outlines as overlapping text (B03, B22), and one B04 label was 40 px against a 41 px minimum. After fixes and re-renders, every gate passed.
- Final master: 3:40.8, 3840×2160, sha256 c7b9d6ae…bf23.
- I watched it once at normal speed, with sound, against a checklist (order, no jargon in the first 45 s, numbers matching the voice, the example readable, no lingering characters). It looked good.

## Assembling the submission
- The pull fast-forwarded cleanly. Claude Code added scenes.py, make_sheet.py and word_times.json, because a fresh-clone rebuild can't work without them.
- The toolkit patch is the same title-safe fix as in October; nothing in the toolkit changed today.
- The course .gitignore excludes *.mp4, so the film has to be added with git add -f.

## Reflection
- Last time my film was mostly promises. This time I wanted most of it to be things I had actually run, and finishing Milestone 2 first made that possible. The results aren't the clean "dense wins" story I might have expected, but the film says exactly why they're provisional, and I'd rather defend that than an overclaim.
- The crash taught me to read the evidence (launch time vs crash time) before panicking or trusting a summary.
- Working one step at a time helped me. When I got several tasks at once it became confusing, so I asked for single steps.