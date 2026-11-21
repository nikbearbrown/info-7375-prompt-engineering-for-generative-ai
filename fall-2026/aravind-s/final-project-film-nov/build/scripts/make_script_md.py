"""Write SCRIPT.md from beats.json (run from the film folder: python3 build/scripts/make_script_md.py)."""
import json
from pathlib import Path

F = Path(__file__).resolve().parents[2]
B = json.load(open(F / "beats.json"))
tot = sum(b["seconds"] for b in B)
out = ["# Klaxon: Final Project Film, script\n",
       "INFO 7375, Canvas assignment 3551817 (25 pts), due Mon 2026-11-23 11:30 PM ET. Brown's four parts, in his order "
       "(announcement of 2026-11-18). Form chosen by Aravind on 2026-11-20: real footage of Klaxon, a few clean title "
       "cards, and a disclosed synthetic voice (Kokoro, am_onyx).\n",
       f"**Target length: {int(tot//60)}:{tot%60:04.1f}** (estimate: spoken words at 2.8 per second plus 0.6 s per beat; "
       "a spelled letter counts as half a word; the appendix card is silent). The executive summary is "
       f"{sum(b['seconds'] for b in B if b['part'].startswith('1.')):.1f} s and contains no \"how\".\n",
       "Status: final. Aravind approved the film with no changes on 2026-11-22. Every claim is in FACTCHECK.md with its source; the footage for each "
       "beat is in SHOTLIST.md; `beats.json` holds the same text for the build (made by `beats.py`). The measured "
       "length of every beat is in TIMINGS.md (the build writes it to build/out/).\n",
       "How to read a beat: **Caption** is the on-screen and soft-caption text (digits kept). **Spoken** is what the "
       "voice reads, only where it differs (acronyms spelled, numbers in words).\n"]
part = None
for b in B:
    if b["part"] != part:
        part = b["part"]
        secs = sum(x["seconds"] for x in B if x["part"] == part)
        out.append(f"\n## Part {part} ({secs:.1f} s)\n")
    out.append(f"### {b['id']} · {b['seconds']} s · {b['layout']}\n")
    if b["caption"]:
        out.append(f"**Caption:** {b['caption']}\n")
        if b["spoken"] != b["caption"]:
            out.append(f"**Spoken:** {b['spoken']}\n")
    else:
        out.append("No narration. The card lists the sources (see SOURCES.md) and the repo link "
                   "https://github.com/AravindKumar2504/klaxon.\n")
txt = "\n".join(out)
assert "\u2014" not in txt
(F / "SCRIPT.md").write_text(txt)
print("SCRIPT.md written")
