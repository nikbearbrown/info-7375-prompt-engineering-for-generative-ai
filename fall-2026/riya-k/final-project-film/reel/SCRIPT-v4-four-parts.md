# Ground Truth SQL: final project film, v4 script (as built)

Final narration, 2026-11-23, generated from beat_sheet.json. Drafted by Claude 2026-11-22 from the v3 film;
Riya approved the draft (Claude Code for model access, the pass bar), then asked for two changes after watching:
a line from 'AI data assistant' to the report card (B05) and a clearer conclusion (B20: 'In conclusion' / 'So the takeaway is this').
Riya approved the 4:35 cut on 2026-11-23.

## Part 1: Executive summary

**B01** (12.39 s) Ground Truth SQL. I'm Riya Kapadnis, and this is my final project film. The problem: AI can write database code that runs with no errors, but gives the wrong answer.

**B02** (18.6 s) Picture an analyst asking an AI: what is our revenue by country? The AI writes SQL, the language for asking a database questions. It runs. No errors. It says the USA made four thousand six hundred sixty seven dollars. The real answer is five hundred twenty three.

**B03** (15.68 s) Why does this matter? People ask data questions in plain English, so most never see the SQL. The AI doesn't know your data. And wrong SQL doesn't crash. It just gives a number people trust, and that number ends up in reports and decisions.

**B04** (11.16 s) So I'm building Ground Truth SQL: a test for AI data assistants. Give it your own data and questions, and it tells you which answers the AI got wrong, and why.

**B05** (16.53 s) Where will it be used? Anywhere people ask data questions in plain English: store sales, finance, hospitals, marketing, and AI data assistants. Analysts learn what to double check. Teams test a tool before buying. Engineers see what to fix.

## Part 2: Introduction

**B06** (20.89 s) Others have tested AI on SQL. BIRD is a public benchmark: twelve thousand seven hundred fifty one questions over ninety five databases, scored by checking results. People score about ninety three percent, and the best AI still scores lower. But BIRD tests AI only on its own databases, not yours.

**B07** (13.1 s) Tools like Vanna write SQL on your own data, and come with a built-in answer test. But that test looks for words, not right numbers. On my data, it passed the answer that was nine times too high.

**B08** (12.93 s) So there's a gap. Benchmarks check numbers, but not on your data. Tools work on your data, but don't check the numbers. Ground Truth SQL does both, so you find the wrong answers before anyone trusts them.

## Part 3: Methods

**B09** (10.84 s) The data: Chinook, a free sample music store database. Eleven tables, fifty nine customers, and four hundred twelve orders from two thousand nine to twenty thirteen.

**B10** (9.39 s) Step one: write about fifty questions, each with a checked answer. I check every answer a second way, in plain Python, straight from the raw tables.

**B11** (10.97 s) Step two: Claude answers each question three times. It sees only the table layout and the question, and may run one read-only query. It can never change the data.

**B12** (9.96 s) Step three: judge by results, not wording, since one answer can be written many ways. These two queries look different, but both give five hundred twenty three.

**B13** (12.52 s) Step four: a report card that sorts every miss by its cause: counting an order once per song, mixing up milliseconds and seconds, counting purchases instead of people, or linking the wrong columns.

**B14** (12.37 s) What I need: a laptop, Python, and the free database. No cloud servers, and no extra token credits: Claude answers through my Claude Code plan, the same way it did in my first runs.

**B15** (10.77 s) The finished project will have one sample database, about fifty test questions, and Claude as the AI it tests. It won't be a chat app, and it never changes the data.

## Part 4: Evaluation

**B16** (10.18 s) First, does the checker judge correctly? On nine test queries that I labeled by hand, comparing wording judged six right. Comparing results: all nine.

**B17** (12.46 s) Then I had Claude answer my eight questions, three times. The checker passed twenty two of twenty four. The two fails were a tie my question never settled. Claude wasn't wrong; my question was.

**B18** (16.23 s) It also caught a mistake in my answer key. One question asked about twenty twenty three, but the data ends in twenty thirteen. The right answer was empty, so broken SQL returning nothing looked correct. Now the tool rejects empty answers.

**B19** (19.03 s) It worked if the checker agrees with my hand labels every time, every answer key passes the second check, and every miss on the report card has a named cause. It didn't work if Claude gets everything right, because that means my questions are too easy. Today it nearly does, so the next fifty questions must be harder.

**B20** (18.45 s) In conclusion: AI can give wrong answers that look right. Ground Truth SQL tests the AI on your own data and shows what's wrong, and why. Today the checker works. Next: fifty harder questions. So the takeaway is this: running SQL is easy. Being right is the test.
