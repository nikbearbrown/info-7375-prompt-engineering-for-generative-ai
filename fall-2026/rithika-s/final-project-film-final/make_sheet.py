#!/usr/bin/env python3
"""make_sheet.py — beat_sheet.json + SHOTLIST.md for agentic-retrieval-lab-final (show-tell).

INFO 7375 final film for "Agentic Retrieval Lab", by Rithika Sankar Rajeswari. Hard cap 4:00.
Narration is ../FILM-BRIEF.md WORD FOR WORD, in its four parts (list markers are layout, not
narration). This script re-reads the brief and refuses to write if any beat's script_text,
joined in order, differs from the brief's narration for that part.

`script_text` = the brief, verbatim. `narration_text` = what Kokoro voices: identical except for
the audio-only respellings in PRONUNCIATION (on-screen text keeps the standard spelling). Every
respelling must be whisper-checked after audio.

Each part opens with a short title card ("1 · Executive summary" …). The first beat of each part
carries lead_silence_s = TITLE_HOLD: the title card is held over that silence, then shrinks to a
small header while the narration starts. generate_audio_kokoro.py has no lead-silence option, so
the silence is padded onto the head of that mp3 after generation (same method as BOUT's 1.0 s
tail), and actual_duration_s re-measured.

On-screen numbers: every digit string in a beat's `on_screen` list must appear in the brief, or
this script refuses to write (the "numbers match the brief exactly" rule).

Audio (later, not now): generate_audio_kokoro.py <reel> --speed 1.0, pad the four part openers
(head) and BOUT (tail), write ffprobe durations back. Re-running this file DROPS measured audio fields.
"""
import json, re
from pathlib import Path

HERE = Path(__file__).resolve().parent
BRIEF = HERE.parent / "FILM-BRIEF.md"
SLUG = "agentic-retrieval-lab-final"
TITLE = "Agentic Retrieval Lab"
HANDLE = "Rithika Sankar Rajeswari · github.com/rithika-sr"   # her own, as in the October reel
VOICE = "af_bella"
SPEED = 1.0
WPS = 2.5            # 150 words per minute: the brief's planning rate (af_bella measured 2.86 wps in October)
TITLE_HOLD = 1.2     # seconds of silent title card at the head of each part

PRONUNCIATION = [    # audio only, applied in order; whole-word regexes
    (r"\bBM25\+bge\b", "B M twenty-five plus B G E"),
    (r"\bBM25", "B M twenty-five"),
    (r"\bMS MARCO\b", "em-ess Marco"),
    (r"\bQ2D-Web\b", "Q two D Web"),
    (r"\bbge-small\b", "B G E small"), (r"\bbge\b", "B G E"),
    (r"\be5-small\b", "E five small"), (r"\be5\b", "E five"),
    (r"\bClaude Haiku 4\.5\b", "Claude Haiku four point five"),
    (r"\bM5\b", "M five"), (r"\b16 GB\b", "sixteen gigabytes"),
    (r"\$0\.63\b", "sixty-three cents"), (r"\+0\.32\b", "plus zero point three two"),
    (r"\b95%", "ninety-five percent"), (r"\bLLM\b", "L L M"), (r"\bRAG\b", "rag"),
    (r"\bagent-written\b", "agent written"),          # October B04: Kokoro slurred the hyphen
    (r"\bpass/fail\b", "pass-fail"), (r"\bvs\b", "versus"),
]


def spoken(text):
    for a, b in PRONUNCIATION:
        text = re.sub(a, b, text)
    return text


SPARSE = ("show-tell style: one drawn scene on a cream stage per beat, labels only, the voice carries the "
          "explanation. Only underfill and clustered are waived; edge-bleed, empty-frame and contrast still apply.")

PARTS = {1: ("1 · Executive summary", "executive-summary"), 2: ("2 · What others have done", "introduction"),
         3: ("3 · Methods", "methods"), 4: ("4 · Evaluation", "evaluation")}

B = []


def beat(bid, part, cls, script, visual, on_screen, cues, exits=(), real=None, title=False, sparse=True):
    """cues/exits: (phrase, event). `at` = share of the script's characters before the phrase starts
    (cues) or after it ends (exits) — the same clock as the kit's until(); refined from word_times.json
    once audio exists."""
    def at(phrase, end=False):
        i = script.find(phrase)
        assert i >= 0, f"{bid}: cue phrase not in script: {phrase!r}"
        return round((i + (len(phrase) if end else 0)) / len(script), 2)
    show = ([{"at": 0.0, "event": f"title card '{PARTS[part][0]}' held over the {TITLE_HOLD} s lead silence, then shrinks to the top-left header"}] if title else [])
    show += [{"at": at(p), "on": p, "event": e} for p, e in cues]
    show += [{"at": at(p, True), "after": p, "event": e} for p, e in exits]
    show.sort(key=lambda s: s["at"])
    words = len(script.split())
    b = {"beat_id": bid, "part": part, "act": PARTS[part][1], "lane": "manim", "proof_gate": "SHOW",
         "script_text": script, "narration_text": spoken(script),
         "estimated_duration_s": round(words / WPS + (TITLE_HOLD if title else 0), 1),
         "voice": VOICE, "engine": "kokoro",
         "shot": {"type": "GRAPHIC", "source": "own", "visual_intent": visual, "on_screen": on_screen,
                  "show": show, "manim": {"class": cls}, "motion_claim": visual}}
    if title:
        b["title_card"] = {"text": PARTS[part][0], "hold_s": TITLE_HOLD}
        b["lead_silence_s"] = TITLE_HOLD
        b["lead_silence_note"] = "padded onto the head of the mp3 after generation; the title card holds over it"
    if real:
        b["real_example"] = real
    if sparse:
        b["qc"] = {"sparse_by_design": True, "sparse_reason": SPARSE}
    B.append(b)


# ───────────────────────── PART 1 · Executive summary (no BM25 / embeddings / recall / corpus / MS MARCO, on screen either)
beat("B01", 1, "B01_AgentsWrite",
     "In RAG systems, AI agents now write the search queries, not people.",
     "Title card. A person's hand-typed question card slides aside; the robot (the AI agent) rolls in and types a query card of its own into a search box.",
     ["1 · Executive summary", "RAG: search, then answer", "AI agent", "writes the search query"],
     [("RAG systems", "label 'RAG: search, then answer' pops beside the search box"),
      ("AI agents", "robot rolls in; label 'AI agent'"),
      ("write the search queries", "robot types its own query card; label 'writes the search query'"),
      ("not people", "the person's question card slides out")],
     exits=[("not people.", "robot stays (same cast next beat); labels dim")], title=True)

beat("B02", 1, "B02_WrongPassage",
     "If an agent's query finds the wrong passage, the answer built on it is wrong, and nobody sees why.",
     "The robot's query card pulls one page off a shelf — the wrong one; an answer card builds on top of it and gets an ✗; a grey curtain slides over the chain.",
     ["wrong passage", "answer: wrong", "why? hidden"],
     [("finds the wrong passage", "page lifts off the shelf; label 'wrong passage'"),
      ("the answer built on it is wrong", "answer card stacks on the page; ✗; label 'answer: wrong'"),
      ("nobody sees why", "curtain slides over the chain; label 'why? hidden'")],
     exits=[("nobody sees why.", "robot rolls out")])

beat("B03", 1, "B03_TheLab",
     "I built Agentic Retrieval Lab to measure, on public data, whether agent-written queries find the right passage as well as the original human question, and which search method handles them best.",
     "Rithika (October character) walks in beside a lab bench titled Agentic Retrieval Lab; a balance scale: human question card on one pan, agent query card on the other; two search-method carts wait behind (unlabelled tools, no method names in part 1).",
     ["Agentic Retrieval Lab", "public data", "human question", "agent-written query", "right passage?", "which search method?"],
     [("I built", "Rithika walks in, waves"),
      ("Agentic Retrieval Lab", "lab bench + title"),
      ("on public data", "open-box stamp 'public data'"),
      ("agent-written queries", "agent query card lands on the right pan; label 'agent-written query'"),
      ("the right passage", "label 'right passage?'"),
      ("original human question", "human question card lands on the left pan; label 'human question'"),
      ("which search method", "two carts roll in behind; label 'which search method?'")],
     exits=[("handles them best.", "Rithika exits left")])

beat("B04", 1, "B04_SoFar",
     "So far, the agent's rewrites didn't beat the original human question with any search method.",
     "The balance scale tips toward the human card on each of four small scales in a row (one per search method, unnamed); a check lands beside 'human question ahead'.",
     ["so far", "human question ahead", "every search method"],
     [("So far", "four small scales slide in"),
      ("didn't beat", "each scale tips to the human side, one after another"),
      ("with any search method", "label 'every search method' + check by 'human question ahead'")])

beat("B05", 1, "B05_WhyItMatters",
     "This matters to anyone choosing a search method for an AI agent: it's a cheap, repeatable check, and every number in it traces back to a file.",
     "The robot at a fork of two carts; a stamp 'cheap', a loop arrow 'repeatable'; then a laptop shows +0.32 and an ink arrow draws from it to a results file icon.",
     ["choosing a search method", "cheap", "repeatable", "+0.32", "results file", "traces back to a file"],
     [("choosing a search method", "robot pauses between two carts; label"),
      ("cheap", "stamp 'cheap'"), ("repeatable", "loop arrow 'repeatable'"),
      ("every number", "laptop: '+0.32'"),
      ("traces back to a file", "arrow draws from the number to a 'results file' icon")],
     exits=[("for an AI agent", "robot exits right")])

# ───────────────────────── PART 2 · What others have done
beat("B06", 2, "B06_Q2DWeb",
     "Q2D-Web, from Perplexity, studies search with agent-written queries over about 190 million web documents, but it keeps its corpus, queries and judgments private: the public gets a leaderboard, not the data.",
     "Title card. A big vault labelled Q2D-Web · Perplexity; robot query cards fly into it; a '190 million web documents' plate; the locking bar slides shut over three drawers (corpus, queries, judgments); a small public leaderboard board stands outside.",
     ["2 · What others have done", "Q2D-Web", "Perplexity", "agent-written queries", "190 million web documents",
      "private: corpus · queries · judgments", "public leaderboard", "not the data"],
     [("Q2D-Web", "vault + 'Q2D-Web'"), ("from Perplexity", "'Perplexity' plate"),
      ("agent-written queries", "robot cards fly into the vault; label"),
      ("190 million web documents", "'190 million web documents' plate"),
      ("keeps its corpus, queries and judgments private", "three drawers labelled, bar slides shut; 'private'"),
      ("the public gets a leaderboard", "leaderboard board stands up outside; label 'public leaderboard'"),
      ("not the data", "label 'not the data' under the locked bar")], title=True)

beat("B07", 2, "B07_MSMARCO",
     "MS MARCO, from Microsoft, is the standard public set of real search questions with a marked correct passage, but its queries are human only.",
     "An open box labelled MS MARCO · Microsoft; real question cards rise from it (real MS MARCO dev queries); one passage page gets a check ('marked correct passage'); a hand-written tag 'human only'.",
     ["MS MARCO", "Microsoft", "public", "when is ski season over", "what is the shingles jab?", "marked correct passage", "human only"],
     [("MS MARCO", "open box + 'MS MARCO'"), ("from Microsoft", "'Microsoft' plate"),
      ("standard public set", "'public' chip"),
      ("real search questions", "two real question cards rise"),
      ("a marked correct passage", "passage page + check; label"),
      ("human only", "tag 'human only'")],
     real={"queries": ["when is ski season over (951820, queries_human.jsonl line 108)",
                       "what is the shingles jab? (846513, queries_human.jsonl line 93)"]})

beat("B08", 2, "B08_Librarians",
     "BM25 is the classic keyword search. bge and e5 are widely used small embedding models that search by meaning.",
     "October cast: the keyword librarian (magnifier) slides in from the left over a book with the same words; the meaning librarian (lightbulb) slides in from the right; the bulb lights a book with different words, same meaning.",
     ["BM25: keyword search", "same words", "bge · e5: embedding models", "search by meaning", "same meaning"],
     [("BM25", "keyword librarian slides in LEFT; label 'BM25: keyword search'"),
      ("keyword search", "magnifier sweeps a same-words book; label 'same words'"),
      ("bge and e5", "meaning librarian slides in RIGHT; label 'bge · e5: embedding models'"),
      ("search by meaning", "bulb lights a same-meaning book; labels")],
     exits=[("classic keyword search.", "keyword librarian dims (stays: next line compares them)"),
            ("search by meaning.", "both librarians slide out (left / right)")])

beat("B09", 2, "B09_TheGap",
     "The gap: there's no small, open experiment that compares human and agent queries across these search methods, that anyone can rerun on a laptop. That's what this project is.",
     "Three tiles in a row from the previous beats (locked vault, human-only box, the two librarians' tools) and an empty dotted fourth tile; Rithika's laptop slides into the empty tile and it turns solid: 'this project'.",
     ["the gap", "small · open", "human vs agent", "across search methods", "rerun on a laptop", "this project"],
     [("The gap", "three tiles + empty dotted tile; label 'the gap'"),
      ("small, open experiment", "'small · open'"),
      ("compares human and agent queries", "'human vs agent'"),
      ("across these search methods", "'across search methods'"),
      ("rerun on a laptop", "laptop slides into the tile"),
      ("That's what this project is", "tile turns solid; 'this project'; Rithika pops up beside it")],
     exits=[("what this project is.", "Rithika exits")])

# ───────────────────────── PART 3 · Methods
beat("B10", 3, "B10_Data",
     "Data: 300 MS MARCO questions (fixed seed 42). Claude Haiku 4.5 rewrote each one into 1 main and 3 supporting agent queries, 1,200 in total.",
     "Title card. A stack of question cards drops from the MS MARCO box ('300 questions', 'seed 42'); the robot ('Claude Haiku 4.5') takes one card and fans it into 1 main + 3 supporting cards; a counter climbs to 1,200.",
     ["3 · Methods", "300 questions", "MS MARCO", "seed 42", "Claude Haiku 4.5", "1 main", "3 supporting", "1,200 agent queries"],
     [("300 MS MARCO questions", "card stack drops; '300 questions'"), ("fixed seed 42", "'seed 42' tag"),
      ("Claude Haiku 4.5", "robot rolls in; 'Claude Haiku 4.5'"),
      ("1 main and 3 supporting", "one card fans into 1 main + 3 supporting"),
      ("1,200 in total", "counter lands on '1,200 agent queries'")],
     exits=[("1,200 in total.", "robot stays (next beat checks its rewrites)")], title=True)

beat("B11", 3, "B11_LeakCheck",
     "A leak check flagged rewrites that gave away the answer.",
     "A scan line sweeps the rewrite cards; one real flagged support query lifts out with the answer word it gave away.",
     ["leak check", "lincoln kentucky hodgenville childhood", "answer: Hodgenville, Kentucky", "gave away the answer"],
     [("A leak check", "scan line sweeps; label 'leak check'"),
      ("flagged rewrites", "real card 'lincoln kentucky hodgenville childhood' lifts out"),
      ("gave away the answer", "'answer: Hodgenville, Kentucky' tag + 'gave away the answer'")],
     exits=[("gave away the answer.", "robot exits")],
     real={"query": "1003210_s2 'lincoln kentucky hodgenville childhood' (queries_agent.jsonl); caught by leak rule v3 (results/foundation/2026-10-08_leak_v3/leak_v3_sanity.json)"})

beat("B12", 3, "B12_TestCorpus",
     "Test corpus: 200,000 passages, made of every correct passage, BM25's top-100 near-misses, and random fill.",
     "A crate fills in three layers as each is named: a thin layer of checked pages, a thick layer of grey near-miss pages poured by the keyword librarian's cart, a layer of plain random pages; plate '200,000 passages'.",
     ["test corpus", "200,000 passages", "every correct passage", "BM25's top-100 near-misses", "random fill"],
     [("Test corpus", "empty crate; label 'test corpus'"), ("200,000 passages", "plate '200,000 passages'"),
      ("every correct passage", "checked pages layer"),
      ("BM25's top-100 near-misses", "keyword cart pours the grey layer; label"),
      ("random fill", "plain pages layer; label")],
     exits=[("top-100 near-misses", "keyword cart rolls out")])

beat("B13", 3, "B13_FourRetrievers",
     "Four retrievers: BM25, bge-small, e5-small, and a BM25+bge hybrid.",
     "Four carts line up on a start line, each named as spoken: keyword librarian's cart, two meaning-librarian carts, and a joined cart carrying both the magnifier and the bulb.",
     ["four retrievers", "BM25", "bge-small", "e5-small", "BM25+bge hybrid"],
     [("Four retrievers", "start line; label"), ("BM25,", "cart 1 (magnifier)"), ("bge-small", "cart 2 (bulb)"),
      ("e5-small", "cart 3 (bulb)"), ("BM25+bge hybrid", "cart 4 (magnifier + bulb)")])

beat("B14", 3, "B14_Measures",
     "Measures: whether the correct passage is in the top 100, and how high it ranks.",
     "THE REAL EXAMPLE. Two query cards from the data, word for word: human 'what is the shingles jab?' and agent 'what is the shingles vaccine'. BM25's top-100 pile: the correct page sits inside the pile for the human card (check), outside it for the agent card (✗). Then a rank ladder: the page climbs to show 'how high it ranks'.",
     ["top 100", "human: what is the shingles jab?", "agent: what is the shingles vaccine", "BM25", "in the top 100 ✓", "not in the top 100 ✗", "how high it ranks"],
     [("Measures", "both real query cards slide in, tags 'human' / 'agent'"),
      ("in the top 100", "BM25 pile: correct page inside for the human card ✓, outside for the agent card ✗"),
      ("how high it ranks", "rank ladder; the page climbs; label 'how high it ranks'")],
     real={"query_id_human": "846513", "query_id_agent": "846513_p",
           "human_text": "what is the shingles jab?", "agent_text": "what is the shingles vaccine",
           "evidence": "evidence/example_846513.jsonl (verbatim lines: queries_human.jsonl 93, queries_agent.jsonl 369); "
                       "evidence/example_846513_bm25_per_query.csv (per_query.csv lines 94 and 670: recall@100 1.0 vs 0.0)",
           "note": "ranks (3 vs 258) are not shown on screen: those numbers are not in the brief"})

beat("B15", 3, "B15_Bootstrap",
     "Each comparison is query by query, with 95% bootstrap intervals.",
     "Pairs of human/agent cards line up question by question; a dot with a whisker interval draws on a zero line.",
     ["query by query", "95% bootstrap interval", "0"],
     [("query by query", "card pairs line up one by one"), ("95% bootstrap intervals", "dot + whisker on a zero line; label")])

beat("B16", 3, "B16_Resources",
     "Resources, all in hand: one M5 laptop with 16 GB (each embedding model ran in about 8 minutes), my own Anthropic API credits (the logged cost for all LLM calls was $0.63), and a free Hugging Face account. 135 automated tests.",
     "A desk fills item by item: laptop 'M5 · 16 GB' with a timer '≈ 8 minutes per embedding model'; a coin stack 'Anthropic API credits' with a receipt '$0.63, all LLM calls'; a 'free Hugging Face account' badge; finally a check stamps '135 automated tests'.",
     ["all in hand", "M5 laptop · 16 GB", "about 8 minutes per embedding model", "Anthropic API credits", "$0.63 · all LLM calls", "free Hugging Face account", "135 automated tests ✓"],
     [("one M5 laptop with 16 GB", "laptop drops in; label"),
      ("about 8 minutes", "timer sweeps; label"),
      ("Anthropic API credits", "coin stack; label"),
      ("$0.63", "receipt '$0.63 · all LLM calls'"),
      ("free Hugging Face account", "badge"),
      ("135 automated tests", "check stamp '135 automated tests ✓'")])

beat("B17", 3, "B17_Next",
     "Next: a length-matched control corpus, harder distractors chosen by dense models, two larger embedding models, and an LLM relevance judge.",
     "Four dotted, not-yet-built crates in a row, each turning to a solid outline as it is named; the meaning librarian picks distractors for crate 2.",
     ["next", "length-matched control corpus", "harder distractors (dense-picked)", "two larger embedding models", "LLM relevance judge"],
     [("Next", "label 'next'"), ("length-matched control corpus", "crate 1"),
      ("harder distractors chosen by dense models", "crate 2; meaning librarian drops pages in"),
      ("two larger embedding models", "crate 3"), ("LLM relevance judge", "crate 4 (robot with gavel)")],
     exits=[("chosen by dense models", "meaning librarian exits right")])

# ───────────────────────── PART 4 · Evaluation (checklist with verdicts)
CHECK = "checklist (4 rows): 1 Trust · 2 Length · 3 Dense vs BM25 · 4 Human vs agent; verdict boxes"
beat("B18", 4, "B18_Rules",
     "I set these pass/fail rules before the Milestone 2 runs (drafted with Claude, adopted by me):",
     "Title card. A clipboard checklist slides in with four rule rows and empty verdict boxes; a small tag 'before Milestone 2 · drafted with Claude, adopted by me'.",
     ["4 · Evaluation", "pass/fail rules", "1 Trust", "2 Length", "3 Dense vs BM25", "4 Human vs agent", "before Milestone 2", "drafted with Claude · adopted by me"],
     [("pass/fail rules", "clipboard + four empty rows"), ("before the Milestone 2 runs", "tag 'before Milestone 2'"),
      ("drafted with Claude, adopted by me", "tag 'drafted with Claude · adopted by me'")], title=True)

beat("B19", 4, "B19_Trust",
     "Trust: every test passes and every number links to a dated results folder. Met.",
     "Checklist row 1 enlarges: '135 tests ✓', an arrow from a number to a 'dated results folder'; verdict box stamps MET; row shrinks back.",
     ["1 Trust", "135 tests ✓", "dated results folder", "Met"],
     [("every test passes", "'135 tests ✓'"), ("dated results folder", "arrow to folder icon; label"),
      ("Met.", "verdict stamp 'Met'")])

beat("B20", 4, "B20_Length",
     "Length: if picking the shortest passages beats random, dense results are provisional. It did, by a small margin, so they're provisional.",
     "Row 2: a ruler sorts pages short-first; two unnumbered bars, 'shortest first' slightly taller than 'random'; verdict stamps PROVISIONAL.",
     ["2 Length", "shortest first", "random", "small margin", "Provisional"],
     [("picking the shortest passages", "ruler sorts pages; bar 'shortest first'"), ("beats random", "bar 'random'"),
      ("by a small margin", "the small gap highlights; label 'small margin'"),
      ("so they're provisional", "verdict stamp 'Provisional'")])

beat("B21", 4, "B21_DenseVsBM25",
     "Dense beats BM25 only if the 95% interval is above zero. It was, by +0.32 recall, but my corpus is made of BM25's near-misses, so it flatters dense models.",
     "Row 3: the interval whisker from B15 lands above the zero line at +0.32; the meaning librarian steps up; then the test-corpus crate from B12 reappears with its grey near-miss layer and a tilted spotlight on the meaning librarian ('flatters dense models'); verdict PROVISIONAL-FLATTERED.",
     ["3 Dense vs BM25", "95% interval", "0", "+0.32 recall", "BM25's near-misses", "flatters dense models", "Provisional-flattered"],
     [("the 95% interval is above zero", "zero line + whisker; label"), ("+0.32 recall", "whisker lands above zero; '+0.32 recall'; meaning librarian steps in"),
      ("BM25's near-misses", "B12 crate returns, grey layer highlighted"),
      ("so it flatters dense models", "spotlight on the meaning librarian; label; verdict 'Provisional-flattered'")],
     exits=[("flatters dense models.", "meaning librarian exits")])

beat("B22", 4, "B22_HumanVsAgent",
     "Human vs agent: the human question came out ahead with every search method; the gap shrank from 5 points with keyword search to about 1 point with the meaning-based models, too small to call for e5.",
     "Row 4: four small scales (from B04) now named BM25, bge-small, e5-small, hybrid, all tipped to 'human'; a gap bracket '5 points' beside the keyword librarian shrinks to 'about 1 point' beside the meaning librarian; the e5 scale gets a '?' 'too small to call'; verdict HUMAN AHEAD.",
     ["4 Human vs agent", "human ahead", "BM25", "bge-small", "e5-small", "hybrid", "5 points · keyword search", "about 1 point · meaning-based", "too small to call for e5", "Human ahead"],
     [("came out ahead with every search method", "four scales tip to 'human'"),
      ("5 points with keyword search", "keyword librarian + bracket '5 points'"),
      ("about 1 point with the meaning-based models", "bracket shrinks; meaning librarian; 'about 1 point'"),
      ("too small to call for e5", "'?' on the e5 scale; label"),
      ("e5.", "verdict stamp 'Human ahead'")],
     exits=[("5 points with keyword search", "keyword librarian exits left"), ("too small to call for e5.", "meaning librarian exits right")])

# BOUT: the brief's last three sentences; drawn in Manim with her own title and handle (no stock ClaudeTitleOutro:
# it hard-codes the instructor's handle and mascot). No narration added.
beat("BOUT", 4, "BOUT_Close",
     "It worked if: the numbers reproduce and the limits are stated. It failed if: a fixed corpus erases the dense advantage. Next, I'll build that fixed corpus.",
     "Completed checklist shrinks left; two columns 'worked if' / 'failed if' fill; a dotted 'fixed corpus' crate solidifies under 'next'; title Agentic Retrieval Lab + her handle; Rithika waves, then the frame holds.",
     ["worked if", "numbers reproduce", "limits stated", "failed if", "fixed corpus erases the dense advantage", "next: fixed corpus",
      "Agentic Retrieval Lab", "Rithika Sankar Rajeswari · github.com/rithika-sr"],
     [("It worked if", "column 'worked if'"), ("the numbers reproduce", "'numbers reproduce' ✓"),
      ("the limits are stated", "'limits stated' ✓"), ("It failed if", "column 'failed if'"),
      ("a fixed corpus erases the dense advantage", "label"), ("Next, I'll build that fixed corpus", "dotted crate solidifies; title + handle; Rithika waves")])
bout = B[-1]
bout["act"] = "outro"
bout["shot"]["remotion"] = {"props": {"title": TITLE, "handle": HANDLE, "subline": ""}}   # read by bookend_check; no pattern → nothing renders in Remotion
bout["tail_silence_s"] = 1.0
bout["estimated_duration_s"] = round(bout["estimated_duration_s"] + 1.0, 1)
bout["outro_note"] = ("As in the October reel (Rithika, 2026-10-10): drawn in Manim with her own title and handle. "
                      "The stock ClaudeTitleOutro hard-codes the instructor's handle and mascot. The 1.0 s silent tail is padded onto the mp3.")

# ───────────────────────── checks: narration verbatim, numbers on screen match the brief
brief = BRIEF.read_text()
secs = re.split(r"^## ", brief, flags=re.M)[1:]
for n, sec in enumerate(secs, 1):
    body = sec.split("\n", 1)[1]
    body = re.sub(r"^\s*(-|\d+\.)\s+", "", body, flags=re.M)
    want = " ".join(body.split())
    got = " ".join(" ".join(b["script_text"] for b in B if b["part"] == n).split())
    assert got == want, f"part {n} narration differs from FILM-BRIEF.md:\nBRIEF: {want}\nSHEET: {got}"
brief_nums = set(re.findall(r"\d[\d,.]*", brief.replace("$", "").replace("+", "")))
for b in B:
    for s in b["shot"]["on_screen"]:
        for num in re.findall(r"\d[\d,.]*", s.replace("$", "").replace("+", "")):
            num = num.rstrip(".,")
            assert num in brief_nums or num.rstrip("0").rstrip(".") in brief_nums, f"{b['beat_id']}: on-screen number {num!r} ({s!r}) is not in the brief"

sheet = {"metadata": {
    "slug": SLUG, "title": TITLE, "topic": "INFO 7375 · FINAL PROJECT FILM", "skill": "show-tell", "style_preset": "show-tell",
    "channel": "rithika-sr", "channel_title": HANDLE, "persona": "Rithika Sankar Rajeswari (first person)",
    "author": "Rithika Sankar Rajeswari", "course": "INFO 7375",
    "voice": VOICE, "voice_kokoro": VOICE, "engine": "kokoro", "kokoro_speed": SPEED,
    "voice_reason": ("Same as the October reel: Kokoro af_bella, first person, as Rithika. The skill's LIAM BY DEFAULT law belongs "
                     "to the instructor's channel; this student film carries no instructor identity."),
    "clock": "narration", "palette": "claude", "register": "Plain", "fps": 24, "aspect_ratio": "16:9", "width": 3840, "height": 2160,
    "runtime_cap_s": 240, "runtime_target_s": 225,
    "narration_source": "../FILM-BRIEF.md, word for word (checked by this script)",
    "parts": [{"part": k, "title_card": v[0]} for k, v in PARTS.items()],
    "caption_policy": "none", "caption_reason": "As in October: no captions; the compiler has no burn-in step.",
    "bookend_exempt": ["cold-open", "bvdt", "bhtf"],
    "bookend_exempt_reason": ("Rithika's brief fixes the film as four parts of her own narration under a 4:00 cap, opened by her own "
                              "part title cards. The hesitant writer, key terms card and Your Turn composer would add narration that is "
                              "not in the brief and carry the instructor's identity. The outro is never exempt: BOUT is drawn in Manim "
                              "with her own title and handle, as in October."),
    "people_rule": ("Cartoon people authorised by Rithika (2026-10-11) and reused with her permission (2026-11-23): me (Rithika), "
                    "keyword librarian = BM25, meaning librarian = embedding models, copied verbatim from the October reel into "
                    "cast_october.py. The robot stays the AI agent. No instructor portrait, likeness or name; the toolkit's "
                    "portrait house rule does not apply to this student film."),
    "visual_rules": ["real readable text only, no placeholder squiggles (the kit's scribble() helpers are not used)",
                     "every key term labelled on screen when it is spoken (cues keyed to the phrase)",
                     "characters exit when their line ends (exit cues)",
                     "visuals enter and leave in sync with the narration (cue times from phrase position; refined from word_times.json after audio)",
                     "numbers on screen match the brief exactly (checked by this script)"],
    "pronunciation": [{"pattern": a, "spoken": b} for a, b in PRONUNCIATION],
    "audience": "the INFO 7375 grader; hiring managers later",
    "source_doc": "../FILM-BRIEF.md; ~/agentic-retrieval-lab results/foundation/ and results/m2/ (read-only); Schall et al. 2026 arXiv:2609.08887v2",
    "playlist": "INFO 7375 final projects", "tags": ["retrieval", "RAG", "BM25", "embeddings", "MS MARCO", "agentic search"]},
    "beats": B}
(HERE / "beat_sheet.json").write_text(json.dumps(sheet, indent=2, ensure_ascii=False) + "\n")

# SHOTLIST.md (typed work order) from the same data
L = ["# SHOTLIST — agentic-retrieval-lab-final", "",
     "Typed work order, generated by `make_sheet.py` from the beat sheet (re-run it, don't hand-edit). Every slot is drawn in Manim; "
     "no pantry media, captures or generated clips.", "",
     "- **Cards:** none. No beat passes the card test better than a drawing of the cast; part title cards are drawn in Manim as the "
     "opening of each part's first beat (Rithika's brief).",
     "- **Cast (copied from the October reel, `cast_october.py`):** `me` (Rithika), `keyword_librarian` (BM25), `meaning_librarian` "
     "(embedding models), `robot` (the AI agent). Librarians enter LEFT/RIGHT and exit when their line ends.",
     "- **Recurring objects:** the balance scales (B03, B04, B22), the test-corpus crate (B12, B21, BOUT), the interval whisker (B15, B21), the checklist (B18–BOUT).",
     "- **Real data on screen:** B07 question cards, B11 leak example, B14 shingles example (evidence/).",
     "- **Skill doctrine broken on purpose (as in October):** labels often exceed the 1–3 word law because Rithika's rules require "
     "every key term labelled when spoken; part title cards are text by her request.",
     "- **Seconds** are estimates at 150 wpm (the brief's rate) plus the 1.2 s title hold / 1.0 s outro tail; measured audio replaces them.", "",
     "| Beat | Part | Est. s | Manim class | Picture and motion | On-screen text |", "|---|---|---|---|---|---|"]
for b in B:
    L.append(f"| {b['beat_id']} | {b['part']} | {b['estimated_duration_s']} | `{b['shot']['manim']['class']}` | {b['shot']['visual_intent']} | "
             + " · ".join(b["shot"]["on_screen"]) + " |")
(HERE / "SHOTLIST.md").write_text("\n".join(L) + "\n")
tot = sum(b["estimated_duration_s"] for b in B)
print(len(B), "beats; est", round(tot, 1), "s =", f"{int(tot // 60)}:{tot % 60:04.1f}")
