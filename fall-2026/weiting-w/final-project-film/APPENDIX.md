# APPENDIX — Stringwatch

**Weiting Wang** · INFO 7375, Fall 2026 · 2026-11-22

The film is four acts: executive summary, introduction, methods, evaluation. This appendix
holds the detail that does not belong on screen — the sources behind act 2, the file formats
and steps behind act 3, and the measurement protocol behind act 4. `PROJECT-BRIEF.md` is the
one-page brief; this is what sits behind it.

Nothing described here is built yet. Everything in the future tense is a plan.

---

## 1. Executive summary

A Unity project keeps most of its real names outside its code: the properties of a shader live
in the shader asset, the parameters of an animator live in the controller, tags live in
`TagManager.asset`, input actions live in an `.inputactions` file. C# reaches all of them as
quoted strings. A wrong class name is a compile error. A wrong shader property name is nothing
at all — the call runs and has no effect.

**Stringwatch** is a read-only command-line tool that reads those assets, builds an index of
the names that really exist, checks every quoted name in the C# against that index, and prints
the ones it cannot find, with file and line. One command, run before the game.

It matters now because of how this code gets written. An assistant that reads only the `.cs`
files cannot see the asset that defines the name, so it produces a plausible name — and the
compiler, the console and the build all accept it.

---

## 2. Introduction — what already exists

| What | What it does | What it does not do | Source |
|---|---|---|---|
| **Unity Input System**, "Generate C# Class" | Generates a typed C# wrapper from an `.inputactions` asset, so action names become members. Unity's own words: it lets you "refer to your actions in a type-safe manner from code" and "avoid looking up your actions by string". | Covers input actions only. Nothing equivalent ships for shader properties, animator parameters or tags. | Input System 1.8 manual, *Input Action Assets* → "Type-safe C# API Generation" |
| **JetBrains Rider / ReSharper**, inspection `Unity.PreferAddressByIdToGraphicsParams` | Flags name-based `Get`/`Set` calls on `Animator`, `Material` and `Shader` and offers a quick fix that caches the ID from `Shader.PropertyToID` / `Animator.StringToHash`. Its own title: "String based graphics property lookup is inefficient". | The fix is about the cost of hashing the string on every call. Neither page claims the name is checked against the shader or controller. | Rider help page; JetBrains `resharper-unity` wiki |
| **Microsoft.Unity.Analyzers** (Roslyn, 46 analyzers) | UNT0041 "Use Animator.StringToHash for repeated Animator method calls" and UNT0046 "Cache Shader.PropertyToID calls" — both categorised **Performance**. | No rule in the set checks that a shader property, animator parameter, tag, layer or input action name exists. | `doc/index.md` rules table |
| **Unity Project Auditor** (built into Unity 6.4 and later) | Reports 25 categories of issue: AnimationClip, AnimatorController, Assembly, AssetIssue, AudioClip, Avatar, AvatarMask, BuildFile, BuildStep, BuildSummary, Code, CodeCompilerMessage, ComputeShaderVariant, DomainReload, Material, Mesh, Metadata, Package, PrecompiledAssembly, ProjectSetting, Shader, ShaderCompilerMessage, ShaderVariant, SpriteAtlas, Texture. | None of the documented categories compares a string in the code with a name defined in an asset. | `IssueCategory` API page + Project Auditor 1.1 manual |
| **The runtime APIs themselves** | `Material.HasProperty(string)` — "Checks if material's shader has a property of a given name." On the animator side, people loop over `Animator.parameters` and write their own `HasParameter` helper. | You call it yourself, per object, in code you remember to write. It is not a sweep over a project, and it runs only when that line runs. | Unity Scripting API; Unity Discussions thread on checking whether an animator parameter exists |
| **Editor-integrated AI tools** (e.g. CoplayDev/unity-mcp through Cursor — the one I used) | Puts a model inside the editor and lets it act on the project directly. | In my own use in spring 2026, what came back from a scene-layout request was wrongly placed objects and no warning — work to undo rather than a report to read. I make no claim about the tool's behaviour today. | My own project notes, spring 2026 |

**The gap.** Each of these is good at its own job. Between them, nobody reads the whole project
and lists every name the code asks for that the project does not have. I searched for a tool
that does and did not find one; that is stated in the film as what I could not find, not as a
claim that none exists.

---

## 3. Methods

### 3.1 Where the data comes from

The only input is the Unity project itself. No dataset is collected, bought or downloaded.

| Name kind | Defined in | Read by Stringwatch as |
|---|---|---|
| Shader property | `.shader` (the `Properties { }` block), `.shadergraph` (JSON, the blackboard properties) | text / JSON parse |
| Animator parameter | `.controller` (YAML) | YAML parse |
| Tag, layer | `ProjectSettings/TagManager.asset` (YAML) | YAML parse |
| Input action | `.inputactions` (JSON) | JSON parse |
| The references | `.cs` sources in `Assets/` | string literals passed to a known set of calls |

### 3.2 The steps

1. **Index.** Walk the project, parse the asset files above, and write one table: name → kind →
   the asset that defines it.
2. **Collect.** Walk the `.cs` files and find the quoted names: the literal arguments to
   `SetFloat`, `SetColor`, `SetTexture`, `SetVector`, `SetInt`, `GetFloat` …, to the `Animator`
   `SetBool` / `SetTrigger` / `SetFloat` / `SetInteger` family, to `CompareTag` and
   `GameObject.FindWithTag`, and to input-action lookups by name.
3. **Compare.** Every collected name that is not in the index becomes a finding: file, line,
   the name, the kind it was used as, and the closest existing names.
4. **Report.** Print the findings and three counts — found, not found, cannot determine. Exit
   non-zero when something was not found, so it can run in a build.

Read-only, by design: Stringwatch opens files and writes a report. It never edits the project,
offers an autofix, or runs inside the editor.

### 3.3 Scope of version one

Only names written out in full are resolved. A name built at runtime — concatenated, read from
a constant, passed in as a variable — is counted as **cannot determine** and never reported as
missing. The count is printed with the others, so a quiet run is visible rather than flattering.

### 3.4 Build order

Shader properties first, because that is the one Unity never reports. Then animator parameters
(Unity reports them, but only when the line runs), then tags, then input actions.

### 3.5 What it needs

Python 3, the Unity project's own files, and a laptop. No API key, no token credits, no cloud
compute, no paid account, no GPU. The Unity project the tool is developed against —
*Escape from the Depths* — already exists and is mine. Development happens with an AI assistant,
but the tool itself calls no model at runtime: it is a parser and a set comparison.

### 3.6 Risks

- **False alarms** are the one that kills it. See §4.
- **Format drift**: `.shadergraph` and `.inputactions` are undocumented JSON shapes and can
  change between Unity versions. Mitigation: parse defensively, and treat a file it cannot
  parse as "cannot determine" rather than as an empty index, which would flag everything.
- **Dynamic names** are common in real code; if the "cannot determine" count swamps the others
  on a real project, the tool is quiet rather than useful. That number is reported for exactly
  this reason.

---

## 4. Evaluation

### 4.1 The sets

1. **A fixture project**: a small Unity project I build, containing shaders, an animator
   controller and C# that uses them, with a known list of planted wrong names (three for the
   first milestone). Because I plant them, I know the correct answer for every line.
2. **My own shipped game**, *Escape from the Depths* — real code I did not write for this test.
   There are no planted errors here, so anything the tool reports is either a real bug or a
   false alarm, and I have to read each one and say which.

### 4.2 What is measured

| Number | Definition |
|---|---|
| **Caught** | planted wrong names that appear in the report |
| **Missed** | planted wrong names that do not |
| **False alarms** | names reported as missing that do exist in the project |
| **Cannot determine** | references the tool declined to resolve |

Recall is caught ÷ (caught + missed). Precision is caught ÷ (caught + false alarms). All four
counts get published together, including the unflattering ones.

### 4.3 Pass marks

- **Milestone one (shader properties):** the report names all three planted names and raises
  **zero** false alarms on the untouched code in the fixture. One false alarm and it has failed,
  because a checker that cries wolf is run once and then ignored.
- **On my own game:** every reported finding is inspected by hand and classified as a real
  mismatch or a false alarm, and that classification is published. There is no target number
  here — the point is an honest measurement on code that was not written for the test.

### 4.4 What would tell me it did not work

A false alarm on correct code; a "cannot determine" count so large that the tool is silent on
most real references; or a planted name the index misses because the asset format was parsed
wrongly. Each of those is a line in the evaluation log, not a reason to quietly change the test.

---

## 5. Exists today, and what will exist

**Exists today.** *Escape from the Depths*, my Unity 6 / URP action dungeon game for CSYE 7270,
spring 2026, containing the string-coupled material code this project is about. Mine, and I can
show it. Nothing else: no part of Stringwatch has been written.

**Will exist.** The asset indexer, shader properties first. The reference collector. The
comparison and the report, with a "cannot determine" outcome. A Unity fixture with labelled
planted errors. An evaluation log reporting all four counts. A written failure analysis.
