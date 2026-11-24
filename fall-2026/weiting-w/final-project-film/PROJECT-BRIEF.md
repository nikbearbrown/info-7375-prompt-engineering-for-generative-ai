# PROJECT-BRIEF.md

**Weiting Wang** · INFO 7375, Fall 2026 · 2026-10-13, header updated 2026-11-22
**Working title:** Stringwatch · **Target role:** Unity tools / gameplay engineer, or
AI-assisted developer tooling · **Runtime:** Python with Claude, a command-line tool

*The film is now built in four parts — executive summary, introduction, methods, evaluation.
This one-page brief maps onto them: §1 and §2 are the executive summary, the comparison in §2
and the prior work in `APPENDIX.md` §2 are the introduction, §5 and §6 are the methods, and §6
with `APPENDIX.md` §4 is the evaluation. `APPENDIX.md` holds the detail that does not belong on
screen: the sources behind the introduction, the file formats and steps behind the methods, and
the measurement protocol behind the evaluation.*

**1. What is it?** A read-only command-line tool that indexes the names a Unity project keeps
outside its code — shader properties first, then animator parameters, then tags, layers and
Input Actions — checks every string reference in the C# against that index, and reports the
ones it cannot find. The artifact is a public GitHub repository: the indexer, a prompt
contract, the verifier, a synthetic Unity fixture project, an evaluation log carrying a hit
rate and a false-alarm rate, and a written failure analysis.

**2. Why would anyone care?** C# can reach those names only as strings —
`material.SetFloat("_GlowActive", 1f)`. A wrong class name is caught by the compiler; a wrong
shader property is caught by nothing. Unity's manual says a call for a property the current
shader does not have "will have no effect", and nothing is reported: it compiles, the console
stays quiet, the game runs, the effect never happens. Not every string is silent — Unity does
log `Parameter 'X' does not exist` for a wrong animator parameter, but only once that line
runs, so an untested branch stays quiet anyway. A static check catches both before anything
runs.

The alternative I have used myself is CoplayDev/unity-mcp through Cursor, on my own game in
spring 2026. It bridges a model into the Unity Editor and acts on the project directly: I asked
it to lay out a scene and it placed the objects wrongly, so I went back to building scenes by
hand. What I got was not a warning, it was a broken scene to undo. Stringwatch never writes
anything — it reports, and where it cannot resolve a reference it says "cannot determine"
instead of guessing. A tool that edits your project has to earn trust first; one that only
reports does not.

**3. Who opens it, and what do they do?** The user is a Unity gameplay programmer who codes
with an AI assistant; the reviewer is a hiring manager or engineer looking at tools work. First
sixty seconds: clone, run one command against the fixture inside the repository, read the
report naming the references that do not resolve, then open the evaluation log and see both
numbers — planted errors caught, and correct references wrongly flagged.

**4. What does it prove about me?** Source grounding, because answers come from an index built
out of the project's own assets rather than a model's recollection of Unity; verification,
because every string in the model's output is checked against that index before it is trusted;
prompt contracts, because the model must declare the symbols it relied on in a form that can be
checked; and evaluation, because it is scored on a labelled set with both rates published. If
the log and the failure analysis end up in the repository, a reviewer could fairly conclude I
can build a verification layer and measure whether it works. I am not claiming that today —
section 7 says why.

**5. In, out, first.** In, in this order: shader properties, because Unity never reports them;
animator parameters, which it reports only at the moment the line runs; then tags, layers and
Input Actions, whose behaviour I have not checked yet. Deliberately out: it will not modify a
file, offer autofix, or run inside the Unity Editor — report only, by choice rather than for
lack of time. First to run: the shader property path end to end — parse `.shadergraph` and
`.shader` for the properties a material really exposes, scan `.cs` for the literals passed to
`SetFloat`, `SetColor`, `SetTexture` and `SetVector`, compare, print. I will know it ran when
the report names exactly the wrong names planted in the fixture and nothing else.

**6. What could sink it?** False alarms. A string is not always written out in full — it may be
concatenated or read from a constant — and a naive indexer will flag correct code. A checker
that cries wolf gets run once. So version one handles literals only, anything it cannot resolve
statically is "cannot determine" rather than "does not exist", and the false-alarm rate is
published next to the hit rate instead of being dropped in favour of the flattering number.

**7. Why this project?** Mostly learning, not showing off. Already have, with something real to
point to: Unity 6 and URP, C#, Shader Graph, and hands-on experience writing the string-driven
material code this tool is about — all of it in *Escape from the Depths* (CSYE 7270, spring
2026), whose sword glow runs on `material.SetFloat("_GlowActive", 1f)` against a Shader Graph
property. New to me: evaluation-set design, prompt contracts as a structured output format, and
reporting measured precision and recall. I have done none of these, and that is the main reason
I picked this. The Unity half is what makes a fixture possible at all — I know the correct
answer, so I can grade the model.

---

**Exists today.** *Escape from the Depths*, my Unity 6 / URP action dungeon game for CSYE 7270,
spring 2026, containing the string-coupled material code above. Mine, and I can show it.
Nothing else: no part of Stringwatch has been written.

**Will exist.** The asset indexer, shader properties first. The prompt contract. The verifier,
with a "cannot determine" outcome. A synthetic Unity fixture with labelled planted errors. An
evaluation set of roughly thirty questions, half answerable from the fixture and half designed
to induce invented names. An evaluation log reporting both rates. A written failure analysis.
