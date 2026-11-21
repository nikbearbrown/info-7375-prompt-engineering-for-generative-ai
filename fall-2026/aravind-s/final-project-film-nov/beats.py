# Beat list for the INFO 7375 Final Project Film (Klaxon). Caption = on-screen/soft-caption text (digits kept);
# spoken = what Kokoro reads (acronyms spelled, numbers in words). Timing from spoken words at 2.8 words/s + 0.6 s.
import json, re, sys
WPS = 2.8
B = []
def beat(id, part, layout, caption, spoken=None):
    B.append(dict(id=id, part=part, layout=layout, caption=caption, spoken=spoken or caption))

P1, P2, P3, P4, AP = ("1. Executive summary", "2. Introduction: what others have done", "3. Methods",
                      "4. Evaluation", "Appendix")
beat("B01", P1, "L1 title card",
     "Hi, I'm Aravind, and this is a synthetic voice reading the script. This film is about my final project, Klaxon.")
beat("B02", P1, "L2 panel in the browser, full frame",
     "Klaxon is an AI on-call engineer for a payments system. When something breaks, it works out what went wrong, "
     "shows its evidence, and asks a person before changing anything. Then it checks what a dashboard can miss: "
     "whether the money is right.",
     "Klaxon is an A I on-call engineer for a payments system. When something breaks, it works out what went wrong, "
     "shows its evidence, and asks a person before changing anything. Then it checks what a dashboard can miss: "
     "whether the money is right.")
beat("B03", P1, "L3 saved screenshot, cropped, one highlight",
     "That last check is why it matters. In one run on my own test system, a bad deploy made the ledger count some "
     "payments more than once. The other alert rules stayed quiet. Only the money check failed: our books were $461 "
     "ahead of the payment provider's.",
     "That last check is why it matters. In one run on my own test system, a bad deploy made the ledger count some "
     "payments more than once. The other alert rules stayed quiet. Only the money check failed: our books were four "
     "hundred sixty-one dollars ahead of the payment provider's.")
beat("B04", P1, "L4 split: footage left, one sentence right",
     "An engineer, or an AI agent, could close an incident like that because everything looks healthy, while the "
     "books are still wrong. With Klaxon, a fix isn't done until the money is checked.",
     "An engineer, or an A I agent, could close an incident like that because everything looks healthy, while the "
     "books are still wrong. With Klaxon, a fix isn't done until the money is checked.")
beat("B05", P2, "L5 fact list card, three rows",
     "The industry calls this an AI SRE, an AI site reliability engineer. Resolve AI raised "
     "$125 million at a $1 billion valuation in February, Traversal $120 million in November, and Datadog, AWS and "
     "Microsoft now offer their own.",
     "The industry calls this an A I S R E, an A I site reliability engineer. Resolve A I raised "
     "one hundred twenty-five million dollars at a one billion dollar valuation in February, Traversal one hundred "
     "twenty million in November, and Datadog, A W S and Microsoft now offer their own.")
beat("B06", P2, "L6 two-number card",
     "What did they get? Microsoft says its agent has mitigated over 35,000 incidents in its own services. But on "
     "ITBench, a research benchmark, agents on state-of-the-art models resolved only 11.4% of its SRE scenarios.",
     "What did they get? Microsoft says its agent has mitigated over thirty-five thousand incidents in its own "
     "services. But on I T Bench, a research benchmark, agents on state-of-the-art models resolved only eleven point "
     "four percent of its S R E scenarios.")
beat("B07", P2, "L7 quote card",
     "The open-source agent I looked at, HolmesGPT, can check a deploy by asking a model to compare error rates, "
     "latency, restarts and logs. In its docs, I didn't find a built-in check that the money is right.",
     "The open-source agent I looked at, Holmes G P T, can check a deploy by asking a model to compare error rates, "
     "latency, restarts and logs. In its docs, I didn't find a built-in check that the money is right.")
beat("B08", P2, "L4 split: their four signals left, Klaxon's money readings right",
     "So why build mine? Klaxon is a small copy of this idea, with the check I couldn't find: after a fix, code, not "
     "the model, checks the money. And Klaxon changes nothing until a person approves it.")
beat("B09", P3, "L8 flat diagram",
     "It all runs on synthetic data. A small payments system runs in Docker on my Mac: an API, a fake "
     "provider that sends signed webhooks, Kafka, and a double-entry ledger. Simulated customers make payments, and "
     "six faults with known causes are injected on purpose.",
     "It all runs on synthetic data. A small payments system runs in Docker on my Mac: an A P I, a fake "
     "provider that sends signed webhooks, Kafka, and a double-entry ledger. Simulated customers make payments, and "
     "six faults with known causes are injected on purpose.")
beat("B10", P3, "L2 panel in the browser, zoomed on the steps",
     "When an alert fires, Klaxon asks Claude for one step at a time: call one of eight read-only tools, served by an "
     "MCP server written from scratch, or give a diagnosis that cites the tool calls behind it.",
     "When an alert fires, Klaxon asks Claude for one step at a time: call one of eight read-only tools, served by an "
     "M C P server written from scratch, or give a diagnosis that cites the tool calls behind it.")
beat("B11", P3, "L3 saved screenshot, slow vertical pan",
     "Here is a real run from week seven. The money alert fired, and in 25 seconds and three tool calls, Klaxon "
     "found the cause: a ledger deploy that books every message without checking for duplicates. It asked to roll "
     "that deploy back.",
     "Here is a real run from week seven. The money alert fired, and in twenty-five seconds and three tool "
     "calls, Klaxon found the cause: a ledger deploy that books every message without checking for duplicates. It "
     "asked to roll that deploy back.")
beat("B12", P3, "L4 split: the gate's trail left, the money readings right",
     "I approved it by typing its id in my own terminal, 70 seconds later. Code then checked the result: healthy, "
     "cause removed, but the money still wrong, because a rollback repairs nothing.",
     "I approved it by typing its I D in my own terminal, seventy seconds later. Code then checked the result: "
     "healthy, cause removed, but the money still wrong, because a rollback repairs nothing.")
beat("B13", P3, "L9 GitHub page in the browser",
     "Weeks one to seven are built and public. Planned by December 4th: a multi-agent version, the webhook receiver "
     "in Go, a 72-run comparison of the loops, and a safety pass.",
     "Weeks one to seven are built and public. Planned by December fourth: a multi-agent version, the webhook "
     "receiver in Go, a seventy-two run comparison of the loops, and a safety pass.")
beat("B14", P3, "L5 two-column card: what I have / its limits",
     "Do I have what I need? There is no API key and no token credits: every call goes through my university's Claude "
     "seat, using Claude Code in headless mode. It isn't billed per call, but it has usage limits, so big batches run "
     "overnight. Dollar figures are estimates at API prices, not money spent. Compute is my Mac and GitHub's free CI.",
     "Do I have what I need? There is no A P I key and no token credits: every call goes through my university's "
     "Claude seat, using Claude Code in headless mode. It isn't billed per call, but it has usage limits, so big "
     "batches run overnight. Dollar figures are estimates at A P I prices, not money spent. Compute is my Mac and "
     "GitHub's free C I.")
beat("B15", P3, "L9 GitHub commit list in the browser",
     "I made the decisions, reviewed and accepted every week, and typed every approval myself. Claude Code wrote the "
     "code under my direction.")
beat("B16", P4, "L10 terminal card from real output",
     "How will I know it works? Eight test cases, each with its right answer written before any run: the six faults, "
     "a false alarm, and a fault where the tools can't see the deploys.")
beat("B17", P4, "L2 panel evaluation page in the browser",
     "I check three things. Did it name the real cause? A keyword rule written in advance and a Claude judge that "
     "never sees which model wrote it both grade that, checked against my own blind labels. Did it name an action "
     "only where one fits? And when I approve an action, does code find the system healthy and the money right?")
beat("B18", P4, "L3 zoom on the report table, one highlight",
     "The first results, from 48 runs on two Claude models: Opus named the cause in all 18 of its fault runs, by both "
     "graders. No run named an action where none fits.",
     "The first results, from forty-eight runs on two Claude models: Opus named the cause in all eighteen of its "
     "fault runs, by both graders. No run named an action where none fits.")
beat("B19", P4, "L4 split: the false-alarm rows left, three short labels right",
     "What didn't work yet: on the false alarm, no run named an action, but each grader found only one run in six that "
     "said plainly that nothing was wrong. And every fault was known while I built Klaxon, so this is not yet a test "
     "on faults it has never seen.")
beat("B20", P4, "L11 end card: works if / fails if",
     "So it works if the 72 comparison runs keep naming causes with no wrong actions, the false alarm gets called "
     "false, and code keeps catching fixes that leave the money wrong. It fails on a confident wrong cause, or an "
     "action where none fits. Klaxon, by Aravind Sundaravadivelu.",
     "So it works if the seventy-two comparison runs keep naming causes with no wrong actions, the false alarm gets "
     "called false, and code keeps catching fixes that leave the money wrong. It fails on a confident wrong cause, or "
     "an action where none fits. Klaxon, by Aravind Sundaravadivelu.")
beat("B21", AP, "L12 appendix card, silent (4 s): sources and the repo link", "", "")

for b in B:
    toks = re.findall(r"[A-Za-z0-9'$%.,-]+", b["spoken"]) if b["spoken"] else []
    w = round(sum(0.45 if re.fullmatch(r"[A-Z]\.?,?", t) else 1 for t in toks), 1)
    b["spoken_words"] = w
    b["seconds"] = round(w / WPS + 0.6, 1) if w else 4.0
assert not any("\u2014" in (b["caption"] + b["spoken"]) for b in B), "em dash found"
json.dump(B, open(sys.argv[1], "w"), indent=1)
tot = sum(b["seconds"] for b in B)
for part in (P1, P2, P3, P4, AP):
    s = sum(b["seconds"] for b in B if b["part"] == part); print(f"{part}: {s:.1f} s")
print(f"TOTAL {tot:.1f} s = {int(tot//60)}:{tot%60:04.1f}; words {sum(b['spoken_words'] for b in B)}")
