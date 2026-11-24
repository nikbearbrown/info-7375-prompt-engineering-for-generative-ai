import React from "react";
import { interpolate, useCurrentFrame } from "remotion";
import { SceneShell } from "../components/SceneShell";
import { Badge, useProgress } from "../components/primitives";
import { at } from "../components/cues";
import { theme, TYPE, SPACE } from "../config/theme";
import { MONO } from "../components/fonts";

const ID = "s10_metrics";

// Proposed thresholds from 04-Evaluation.md ("Status: proposed, no results claimed"). Nothing here is a measurement.
const ROWS = [
  { m: "Factual grounding", q: "Cited sources actually support the claim", target: "≥ 90%", cue: "Factual grounding" },
  { m: "Unsupported claims", q: "Complete system vs single-prompt baseline", target: "≥ 30% fewer", cue: "are claims actually supported" },
  { m: "Risk relevance", q: "Specific to this product (human rubric)", target: "≥ 4 / 5", cue: "Relevance" },
  { m: "Actionability", q: "Experiments can be run and measured", target: "≥ 4 / 5", cue: "Actionability" },
  { m: "Evaluator error detection", q: "Planted errors caught", target: "≥ 80%", cue: "plant deliberate errors" },
  { m: "Structured output validity", q: "Reports that pass the schema", target: "≥ 95%", cue: "structured outputs are valid" },
  { m: "Tokens · latency · cost", q: "Per report, including retries", target: "Tracked", cue: "compare token use", tracked: true },
];

export const S10Metrics: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <SceneShell id={ID}>
      <div style={{ position: "absolute", left: SPACE.gutter, top: 140, fontSize: TYPE.h2, fontWeight: 800, letterSpacing: "-0.02em", opacity: useProgress(4, 16) }}>What I'll measure</div>
      <div style={{ position: "absolute", left: SPACE.gutter + 620, top: 160, fontFamily: MONO, fontSize: TYPE.label, letterSpacing: "0.12em", textTransform: "uppercase", color: theme.warn, opacity: useProgress(10, 16),
        border: `2px dashed ${theme.warn}`, borderRadius: 8, padding: "8px 14px" }}>Proposed targets · not observed results</div>
      <div style={{ position: "absolute", left: SPACE.gutter, top: 270, width: 1680 }}>
        <div style={{ display: "flex", borderBottom: `2px solid ${theme.ink}`, paddingBottom: 12, fontFamily: MONO, fontSize: TYPE.label, letterSpacing: "0.12em", textTransform: "uppercase", color: theme.inkSoft, opacity: useProgress(8, 14) }}>
          <div style={{ width: 560 }}>Metric</div><div style={{ width: 760 }}>What it checks</div><div style={{ width: 360, textAlign: "right", color: theme.accent }}>Proposed target</div>
        </div>
        {ROWS.map((r) => {
          const c = at(ID, r.cue);
          const p = interpolate(frame, [c, c + 12], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
          return (
            <div key={r.m} style={{ display: "flex", alignItems: "center", height: 84, borderBottom: `1px solid ${theme.line}`, opacity: p, transform: `translateX(${(1 - p) * 30}px)` }}>
              <div style={{ width: 560, fontSize: TYPE.body, fontWeight: 700 }}>{r.m}</div>
              <div style={{ width: 760, fontSize: TYPE.small, color: theme.inkSoft }}>{r.q}</div>
              <div style={{ width: 360, textAlign: "right", fontSize: TYPE.h3 - 4, fontWeight: 800, color: r.tracked ? theme.inkSoft : theme.ink }}>{r.target}</div>
            </div>
          );
        })}
      </div>
      <Badge kind="proposed" text="Proposed · from my evaluation protocol" start={8} style={{ right: SPACE.gutter, bottom: 64 }} />
    </SceneShell>
  );
};
