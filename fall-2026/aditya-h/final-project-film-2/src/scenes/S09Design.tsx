import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { SceneShell } from "../components/SceneShell";
import { Badge, useProgress } from "../components/primitives";
import { Connector } from "../components/diagram";
import { at } from "../components/cues";
import { theme, TYPE, SPACE } from "../config/theme";
import { MONO } from "../components/fonts";

const ID = "s09_design";

// Synthetic scenarios S01–S10 and configurations A/B/C from 04-Evaluation.md.
const SCENARIOS = ["Student budgeting app", "Lecture note summarizer", "Field inspection sketches", "SMB vendor compliance", "Fragrance recommender",
  "Football tactics planner", "Food-waste forecasting", "B2B passwordless login", "Campus used-book exchange", "Store accessibility checker"];
const CONFIGS = [
  { k: "A", t: "Single-prompt baseline", d: "one model call", cue: "a single-prompt baseline", agents: 0, evaluator: false },
  { k: "B", t: "Multi-agent, no evaluator", d: "specialists + synthesis", cue: "the multi-agent workflow", agents: 3, evaluator: false },
  { k: "C", t: "Complete ProductLens", d: "+ evaluator and one revision", cue: "the complete ProductLens", agents: 3, evaluator: true },
];

export const S09Design: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const scen = at(ID, "ten standardized product scenarios");
  const branch = at(ID, "each run three ways");
  const same = at(ID, "The model, the inputs");
  const ys = [250, 470, 690];
  return (
    <SceneShell id={ID}>
      <div style={{ position: "absolute", left: SPACE.gutter, top: 140, fontSize: TYPE.h2, fontWeight: 800, letterSpacing: "-0.02em", opacity: useProgress(4, 16) }}>Experimental design</div>
      {SCENARIOS.map((s, i) => {
        const p = interpolate(frame, [scen + i * 3, scen + i * 3 + 10], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
        return (
          <div key={s} style={{ position: "absolute", left: SPACE.gutter, top: 250 + i * 64, width: 470, height: 52, opacity: p, transform: `translateX(${(1 - p) * -20}px)`,
            display: "flex", alignItems: "center", gap: 14, padding: "0 16px", boxSizing: "border-box", border: `1px solid ${theme.line}`, borderRadius: 10, background: theme.bgSoft }}>
            <span style={{ fontFamily: MONO, fontSize: TYPE.label, color: theme.accent }}>S{String(i + 1).padStart(2, "0")}</span>
            <span style={{ fontSize: TYPE.small - 2 }}>{s}</span>
          </div>
        );
      })}
      {CONFIGS.map((c, i) => (
        <Connector key={c.k} d={`M 590 570 C 680 570, 680 ${ys[i] + 75}, 760 ${ys[i] + 75}`} start={branch + i * 5} color={theme.inkSoft} pulseAt={at(ID, c.cue) - 8} />
      ))}
      {CONFIGS.map((c, i) => {
        const s = spring({ frame: frame - at(ID, c.cue), fps, config: { damping: 200 } });
        return (
          <div key={c.k} style={{ position: "absolute", left: 760, top: ys[i], width: 560, height: 150, opacity: s, transform: `translateX(${(1 - s) * 30}px)`,
            border: `${c.evaluator ? 2 : 1}px solid ${c.evaluator ? theme.accent : theme.line}`, borderRadius: 16, background: theme.bgSoft, padding: "22px 26px", boxSizing: "border-box", display: "flex", gap: 22 }}>
            <div style={{ fontSize: TYPE.h1 - 12, fontWeight: 800, color: c.evaluator ? theme.accent : theme.ink, lineHeight: 1 }}>{c.k}</div>
            <div style={{ flex: 1 }}>
              <div style={{ fontSize: TYPE.body, fontWeight: 700 }}>{c.t}</div>
              <div style={{ fontSize: TYPE.small - 4, color: theme.inkSoft, marginTop: 4 }}>{c.d}</div>
              <div style={{ display: "flex", gap: 8, marginTop: 14 }}>
                {Array.from({ length: c.agents || 1 }).map((_, k) => <span key={k} style={{ width: 34, height: 22, borderRadius: 5, background: c.agents ? theme.line : theme.inkSoft }} />)}
                {c.evaluator && <span style={{ width: 34, height: 22, borderRadius: 5, background: theme.accent }} />}
              </div>
            </div>
          </div>
        );
      })}
      {CONFIGS.map((c, i) => (
        <Connector key={`o${c.k}`} d={`M 1320 ${ys[i] + 75} C 1390 ${ys[i] + 75}, 1390 570, 1440 570`} start={at(ID, "the complete ProductLens") + 20 + i * 4} color={theme.inkSoft} />
      ))}
      <div style={{ position: "absolute", left: 1440, top: 470, width: 360, opacity: useProgress(at(ID, "the complete ProductLens") + 24, 18),
        border: `1px solid ${theme.line}`, borderRadius: 16, background: theme.bgSoft, padding: "24px 26px", boxSizing: "border-box" }}>
        <div style={{ fontSize: TYPE.body, fontWeight: 700 }}>Compare</div>
        <div style={{ fontSize: TYPE.small - 4, color: theme.inkSoft, marginTop: 6, lineHeight: 1.35 }}>paired per scenario · report order randomized</div>
      </div>
      <div style={{ position: "absolute", left: 760, top: 880, display: "flex", gap: 14, opacity: useProgress(same, 16) }}>
        {["Same model", "Same inputs", "Same frozen evidence"].map((t) => (
          <span key={t} style={{ padding: "12px 20px", border: `1px solid ${theme.accent}`, borderRadius: 10, fontSize: TYPE.small, fontWeight: 600 }}>{t}</span>
        ))}
      </div>
      <Badge kind="proposed" text="Proposed design · not yet run" start={4} style={{ right: SPACE.gutter, bottom: 64 }} />
    </SceneShell>
  );
};
