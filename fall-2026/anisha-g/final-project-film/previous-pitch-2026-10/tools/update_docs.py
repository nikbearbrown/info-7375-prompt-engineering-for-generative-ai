"""One-time update of FRICTIONAL.md, BUILD-PROMPT.md and README.md for the 2026-10-13 fixes.
Keeps everything already filled in. Safe to run twice (it skips what is already there)."""
import re
def edit(path, fn):
    s = open(path).read(); t = fn(s)
    if t != s: open(path, 'w').write(t); print('updated', path)
    else: print('no change', path)

NEW_FRICTIONAL = """**2026-10-13, ~9:50 am** — Asked Claude to check the submission against the rubric. It ran the toolkit's own Gate V (`runtime/qc/final_frame_check.py`) on a test build and it FAILED: the soft corner shading made the gate read the whole background as content (edge-bleed + low-contrast on every frame), and the subtitle box sat below the title-safe line. Fixed: shading made subtler (within the gate's tolerance), subtitles raised, camera drift reduced. Check frames then passed (0 blockers, 0 major). Also: the class repo's GitHub check emailed me a failure; it comes from another student's `.tsx` files (the repo only allows Python), not from my folder.

**2026-10-13, ~10:00 am** — Question 2 originally said I had looked at a chatbot, but I hadn't actually tried one yet, so I did. ChatGPT could not open the LinkedIn link. With the posting text pasted (Staples, Financial Analytics Intern) it summarised well and said "Salary: Not disclosed", but showed no source for any field and added "Staples is headquartered near Boston", which is not in the posting. Screenshots in `evidence/` (cropped to remove my personal details). Updated question 2 and the narration to say what I actually saw.

**2026-10-13, ~10:05 am** — Question 7 said my Python evidence was "earlier course assignments", which was vague. Replaced it with my MBTA Transit Reliability Pipeline (github.com/anishagaikar0420/mbta-reliability-pipeline), a Python ELT pipeline with tests and a quality gate.

"""
def fr(s):
    if 'Gate V (`runtime/qc/final_frame_check.py`)' in s: return s
    s = s.replace("No Brutalist gate reports, since I didn't use its renderer; I used the checklist in BUILD-PROMPT.md instead.",
                  "(first build, before the gate fixes below)")
    return s.replace("**What I'd do differently:**", NEW_FRICTIONAL + "**What I'd do differently:**")
edit('FRICTIONAL.md', fr)

def bp(s):
    if 'run_gate_v.sh' in s: return s
    s = s.replace("## 2. Brutalist", """- 2026-10-13: "have we pushed everything and covered every requirement … I don't want to lose marks" → Claude ran the toolkit's Gate V, fixed the design until it passed, and added `tools/run_gate_v.sh`
- 2026-10-13: tried ChatGPT myself on a real posting for question 2 (screenshots in `evidence/`); gave my MBTA pipeline repo as question 7 evidence

## 2. Brutalist""")
    s = s.replace("## 4. My own checks (Brutalist's gates were not run)", """## 4. Checks
Toolkit gate (Brutalist GATE V, `runtime/qc/final_frame_check.py`), run on the finished film:
```bash
bash tools/run_gate_v.sh      # clones brutalist.art if needed, writes reports/GATE-V-REPORT.md
```
My own checklist:""")
    return s
edit('BUILD-PROMPT.md', bp)

def rd(s):
    if 'run_gate_v.sh' in s: return s
    return s.replace("| `BUILD-PROMPT.md` |", """| `evidence/` | My dated screenshots of the chatbot alternative (question 2) |
| `reports/` | The toolkit's Gate V report and contact sheet for the final film |
| `tools/run_gate_v.sh` | Runs the toolkit's Gate V on the film |
| `BUILD-PROMPT.md` |""")
edit('README.md', rd)
