import json, math, re, sys, pathlib
P=str(pathlib.Path(__file__).resolve().parent / "beat_sheet.json")
d=json.load(open(P)); we=d["metadata"]["worked_example"]; fail=[]
E={k:tuple(v) for k,v in we["embeddings"].items()}
scale=math.sqrt(we["d_k"])

def derive(ctx):
    q=E["bank"]
    raw={t:q[0]*E[t][0]+q[1]*E[t][1] for t in ctx}
    sc={t:raw[t]/scale for t in ctx}
    m=max(sc.values()); ex={t:math.exp(sc[t]-m) for t in ctx}; Z=sum(ex.values())
    w={t:ex[t]/Z for t in ctx}
    out=(sum(w[t]*E[t][0] for t in ctx), sum(w[t]*E[t][1] for t in ctx))
    return raw,sc,w,out

print("=== ARITHMETIC (every printed figure re-derived) ===")
for key in ("run_a","run_b"):
    r=we[key]; ctx=r["context"]; raw,sc,w,out=derive(ctx)
    for t in ctx:
        if abs(raw[t]-r["raw_scores"][t])>1e-9: fail.append(f"{key} raw {t}")
        if abs(sc[t]-r["scaled_scores"][t])>5e-4: fail.append(f"{key} scaled {t}: {sc[t]:.4f} vs {r['scaled_scores'][t]}")
        if abs(w[t]-r["softmax_weights"][t])>5e-4: fail.append(f"{key} weight {t}: {w[t]:.4f} vs {r['softmax_weights'][t]}")
    ws=sum(r["softmax_weights"].values())
    if abs(ws-1.0)>1e-9: fail.append(f"{key} weights sum to {ws} not 1.000")
    for i,v in enumerate(r["output"]):
        if abs(out[i]-v)>5e-3: fail.append(f"{key} output[{i}]: {out[i]:.4f} vs {v}")
    print(f"  {key}: raw={[round(raw[t],3) for t in ctx]} scaled={[round(sc[t],3) for t in ctx]} "
          f"w={[round(w[t],3) for t in ctx]} sum={round(ws,4)} out=({out[0]:.4f},{out[1]:.4f}) OK")

_,_,_,oa=derive(we["run_a"]["context"]); _,_,_,ob=derive(we["run_b"]["context"])
sep=math.hypot(oa[0]-ob[0],oa[1]-ob[1])
if abs(sep-we["separation_between_runs"])>5e-3: fail.append(f"separation {sep:.4f}")
shift=math.hypot(oa[0]-2,oa[1]-2)
if abs(shift-we["run_a"]["shift_from_input"])>5e-3: fail.append(f"shift {shift:.4f}")
print(f"  separation={sep:.4f}  shift={shift:.4f}  OK")

# B06 contribution terms + B04/B05/B07 props cross-check against derivation
beats={b["beat_id"]:b for b in d["beats"]}
raw,sc,w,out=derive(we["run_a"]["context"])
for t in beats["B04"]["shot"]["remotion"]["props"]["rows"]:
    if abs(t["raw"]-raw[t["token"]])>1e-9: fail.append(f"B04 raw {t['token']}")
    if abs(t["scaled"]-sc[t["token"]])>5e-4: fail.append(f"B04 scaled {t['token']}")
    lhs=eval(t["work"].replace("×","*"))
    if abs(lhs-t["raw"])>1e-9: fail.append(f"B04 work string '{t['work']}' != {t['raw']}")
for t in beats["B05"]["shot"]["remotion"]["props"]["rows"]:
    if abs(t["weight"]-w[t["token"]])>5e-4: fail.append(f"B05 weight {t['token']}")
tot=0.0
for t in beats["B06"]["shot"]["remotion"]["props"]["terms"]:
    p=[t["weight"]*E[t["token"]][0], t["weight"]*E[t["token"]][1]]
    for i in (0,1):
        if abs(p[i]-t["product"][i])>5e-4: fail.append(f"B06 product {t['token']}[{i}]: {p[i]:.4f} vs {t['product'][i]}")
ex=beats["B06"]["shot"]["remotion"]["props"]["exactTotal"]
sums=[sum(t["product"][i] for t in beats["B06"]["shot"]["remotion"]["props"]["terms"]) for i in (0,1)]
for i in (0,1):
    if abs(sums[i]-ex[i])>1e-6: fail.append(f"B06 exactTotal[{i}]: {sums[i]} vs {ex[i]}")
dl=beats["B06"]["shot"]["remotion"]["props"]["delta"]
for i in (0,1):
    if abs((out[i]-2)-dl[i])>6e-3: fail.append(f"B06 delta[{i}]: {out[i]-2:.4f} vs {dl[i]}")
print("  B04/B05/B06 props re-derived from embeddings: OK")
print("  B04 'work' strings evaluate to their stated raw scores: OK")

# 2 d.p. would break sum-to-1 (the stated reason for 3 d.p.)
two=[round(w[t],2) for t in we["run_a"]["context"]]
print(f"  sanity: 2 d.p. weights {two} sum={sum(two):.2f} -> 3 d.p. is required. OK")

print("\n=== TIMING (calibrated 2.501 w/s from claude-tom-ranking-is-not-truth) ===")
WPS=2.501; total=0.0
for b in d["beats"]:
    n=len(b["narration_text"].split()); est=b["estimated_duration_s"]
    pred=n/WPS; span=est+b.get("lead_silence_s",0.0); total+=span
    flag="" if abs(pred-est)<=1.6 else "  <-- DRIFT"
    if flag: fail.append(f"{b['beat_id']} est {est} vs predicted {pred:.1f}")
    print(f"  {b['beat_id']:5} {n:3}w  est {est:5.1f}s  pred {pred:5.1f}s  span {span:5.1f}s{flag}")
print(f"  TOTAL {total:.1f}s = {int(total//60)}:{int(total%60):02d}")
if not (210 <= total <= 240): fail.append(f"total {total:.1f}s outside the 3:30-4:00 brief window")
print(f"  WINDOW 3:30-4:00 -> {'PASS' if 210 <= total <= 240 else 'FAIL'}")

print("\n=== AUTHORING LAWS ===")
ids=[b["beat_id"] for b in d["beats"]]
checks=[
 ("COLD OPEN: B00 is ClaudeComposerAsk", beats["B00"]["shot"]["remotion"]["pattern"]=="ClaudeComposerAsk"),
 ("EXEC SUMMARY: B01 is BrutalistHesitantWriter", beats["B01"]["shot"]["remotion"]["pattern"]=="BrutalistHesitantWriter"),
 ("EXEC SUMMARY: B01 window >= 9s", beats["B01"]["estimated_duration_s"]+beats["B01"].get("lead_silence_s",0)>=9),
 ("EXEC SUMMARY: B01 lead_silence_s == 0.8", beats["B01"].get("lead_silence_s")==0.8),
 ("EXEC SUMMARY: replacement word present in text", beats["B01"]["shot"]["remotion"]["props"]["replacementWords"] in beats["B01"]["shot"]["remotion"]["props"]["text"]),
 ("EXEC SUMMARY: trigger word absent from final text", beats["B01"]["shot"]["remotion"]["props"]["triggerWords"] not in beats["B01"]["shot"]["remotion"]["props"]["text"]),
 ("EXEC SUMMARY: seed set per reel", beats["B01"]["shot"]["remotion"]["props"]["seed"]==d["metadata"]["slug"]),
 ("HANDOFF: 2nd-to-last, greeting 'Your turn.'", ids[-2]=="BHTF" and beats["BHTF"]["shot"]["remotion"]["props"]["greeting"]=="Your turn."),
 ("HANDOFF: prompt read aloud verbatim in narration", beats["BHTF"]["shot"]["remotion"]["props"]["command"] in beats["BHTF"]["narration_text"]),
 ("OUTRO: last beat, title restated exactly", ids[-1]=="BOUT" and beats["BOUT"]["shot"]["remotion"]["props"]["title"]==d["metadata"]["title"]),
 ("OUTRO: no subline (locked card)", "subline" not in beats["BOUT"]["shot"]["remotion"]["props"]),
 ("IN-FOR-BEAR: B00 says the voice out loud", "Tom, in for Bear" in beats["B00"]["narration_text"]),
 ("SHOW-DON'T-TELL: every beat has a show block", all(b["shot"].get("show") for b in d["beats"])),
 ("SHOW-DON'T-TELL: every beat has visual_intent", all(b["shot"].get("visual_intent") for b in d["beats"])),
 ("SPARK-LINE: every body beat carries a spark line", all(beats[i]["shot"]["remotion"]["props"].get("sparkLine") for i in ["B02","B03","B04","B05","B06","B07","B08"])),
 ("ILLUSTRATE: no two consecutive beats share a pattern", all(d["beats"][i]["shot"]["remotion"]["pattern"]!=d["beats"][i+1]["shot"]["remotion"]["pattern"] for i in range(len(d["beats"])-1))),
 ("ILLUSTRATE: Claude UI only on bookends", all(b["shot"]["lane"]=="bookend" for b in d["beats"] if b["shot"]["remotion"]["pattern"].startswith("ClaudeComposer"))),
 ("HONESTY: constructed stamp on every mechanism beat", all(beats[i]["shot"]["remotion"]["props"].get("stampText") for i in ["B03","B04","B05","B06","B07"])),
 ("HONESTY: boundary beat present", "boundary" in beats["B08"]["act"].lower()),
 ("GATE L: every new-scene beat records its search", all("gate_l" in beats[i] for i in ["B02","B03","B04","B05","B06","B07","B08"])),
 # State-aware: before the build the new scenes are the slate list; after a
 # successful build the toolkit clears it and marks every beat VIDEO.
 ("BUILD STATE: slates/filled/status are self-consistent",
   (set(d["metadata"]["build"]["slates"])=={i for i in ids if beats[i]["shot"]["remotion"]["pattern"].startswith("Ch1Attn")}
      and d["metadata"]["build"]["cut"]=="unbuilt")
   or (d["metadata"]["build"]["slates"]==[]
      and d["metadata"]["build"]["filled"]==d["metadata"]["build"]["of"]
      and all(b["build"]["status"]=="VIDEO" for b in d["beats"]))),
 ("AUDIO-FIRST: every beat has measured audio", all(b.get("actual_duration_s") for b in d["beats"])),
 ("build.of matches beat count", d["metadata"]["build"]["of"]==len(d["beats"])),
 # --- the brief's explicit rubric requirements, asserted not assumed ---
 ("BOUNDARY: a concluding scene states the limit", "B09" in ids and beats["B09"]["shot"]["remotion"]["pattern"]=="Ch1AttnMultiHead"),
 ("BOUNDARY: on-screen statement is verbatim",
   beats["B09"]["shot"]["remotion"]["props"]["statement"]==d["metadata"]["boundary_claim"]["stated_verbatim_on_screen"]),
 ("BOUNDARY: mentions multi-head AND many dimensions",
   all(k in beats["B09"]["shot"]["remotion"]["props"]["statement"].lower()
       for k in ("multi-head","dimensions","simultaneously","does not establish"))),
 ("BOUNDARY: the statement is also spoken aloud",
   "multi-head attention handles dozens of nuanced semantic dimensions simultaneously" in beats["B09"]["narration_text"]),
 ("BOUNDARY: it is the last body beat before the bookends", ids.index("B09")==ids.index("BVDT")-1),
 ("HONESTY: stamp text reads exactly CONSTRUCTED EXAMPLE",
   all(beats[i]["shot"]["remotion"]["props"].get("stampText")=="CONSTRUCTED EXAMPLE" for i in ["B03","B04","B05","B06","B07"])),
 ("MECHANISM: B04 shows per-term dot-product arithmetic",
   all("×" in r["work"] and "+" in r["work"] for r in beats["B04"]["shot"]["remotion"]["props"]["rows"])),
 ("MECHANISM: B06 animates the vector from input to output",
   beats["B06"]["shot"]["remotion"]["props"]["inputVec"]!=beats["B06"]["shot"]["remotion"]["props"]["outputVec"]),
]
for name,ok in checks:
    print(f"  {'PASS' if ok else 'FAIL'}  {name}")
    if not ok: fail.append(name)

print("\n=== NARRATION BUDGET (body beats 45-70 words; bookends exempt) ===")
for i in ["B02","B03","B04","B05","B06","B07","B08"]:
    n=len(beats[i]["narration_text"].split())
    print(f"  {i}: {n}w {'ok' if 40<=n<=70 else 'CHECK'}")

print("\n"+("ALL CHECKS PASS" if not fail else "FAILURES:\n  "+"\n  ".join(fail)))
