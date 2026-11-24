import React from "react";
import { interpolate, useCurrentFrame } from "remotion";
import { SceneShell } from "../components/SceneShell";
import { Badge, useProgress } from "../components/primitives";
import { at } from "../components/cues";
import { theme, TYPE, SPACE } from "../config/theme";
import { MONO } from "../components/fonts";

const ID = "s08_resources";

// Proposed stack from 02-Architecture.md. Resource status per Aditya (2026-11-23): all pending, none confirmed.
const STACK = [
  { t: "Next.js · TypeScript", d: "web app", cue: "a modern web stack" },
  { t: "LLM provider adapter", d: "Claude or configured model", cue: "large language models" },
  { t: "Versioned prompt contracts", d: "+ schema validation (Zod)", cue: "structured prompts" },
  { t: "Orchestration with run state", d: "bounded retries · one revision", cue: "an orchestration layer" },
];
const RESOURCES = [
  { t: "Model API access", cue: "model API access" },
  { t: "Token credits", cue: "token credits" },
  { t: "Research / search access", cue: "research access" },
  { t: "Execution & deployment", cue: "somewhere to run" },
];
const BRIEF = [
  { t: "Competitive insights", cue: "competitive insights" },
  { t: "Customer pain points", cue: "customer pain points" },
  { t: "Ranked failure risks", cue: "ranked failure risks" },
  { t: "Recommended experiments", cue: "recommended experiments" },
  { t: "Measurable success criteria", cue: "measurable success criteria" },
  { t: "Source registry · every claim linked", cue: "each linked" },
];

const Row: React.FC<{ y: number; x: number; w: number; cue: number; children: React.ReactNode }> = ({ y, x, w, cue, children }) => {
  const frame = useCurrentFrame();
  const p = interpolate(frame, [cue, cue + 12], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return <div style={{ position: "absolute", left: x, top: y, width: w, opacity: p, transform: `translateX(${(1 - p) * 24}px)` }}>{children}</div>;
};

export const S08Resources: React.FC = () => {
  const frame = useCurrentFrame();
  const deliver = at(ID, "The final deliverable");
  const out = interpolate(frame, [deliver - 8, deliver + 12], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const brief = useProgress(deliver, 20);
  const pending = at(ID, "still being confirmed");
  const track = at(ID, "Token use");
  return (
    <SceneShell id={ID}>
      <div style={{ opacity: out }}>
        <div style={{ position: "absolute", left: SPACE.gutter, top: 150, fontSize: TYPE.h2, fontWeight: 800, letterSpacing: "-0.02em", opacity: useProgress(4, 16) }}>Stack and resources</div>
        <div style={{ position: "absolute", left: SPACE.gutter, top: 260, fontFamily: MONO, fontSize: TYPE.label, letterSpacing: "0.12em", textTransform: "uppercase", color: theme.inkSoft }}>Proposed stack</div>
        {STACK.map((s, i) => (
          <Row key={s.t} x={SPACE.gutter} y={310 + i * 120} w={760} cue={at(ID, s.cue)}>
            <div style={{ padding: "20px 26px", border: `1px solid ${theme.line}`, borderRadius: 14, background: theme.bgSoft }}>
              <div style={{ fontSize: TYPE.body, fontWeight: 700 }}>{s.t}</div>
              <div style={{ fontSize: TYPE.small - 2, color: theme.inkSoft, marginTop: 4 }}>{s.d}</div>
            </div>
          </Row>
        ))}
        <div style={{ position: "absolute", left: 1000, top: 260, fontFamily: MONO, fontSize: TYPE.label, letterSpacing: "0.12em", textTransform: "uppercase", color: theme.inkSoft }}>Resources needed</div>
        {RESOURCES.map((r, i) => (
          <Row key={r.t} x={1000} y={310 + i * 96} w={800} cue={at(ID, r.cue)}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "20px 26px", border: `1px solid ${theme.line}`, borderRadius: 14 }}>
              <span style={{ fontSize: TYPE.body, fontWeight: 600 }}>{r.t}</span>
              <span style={{
                fontFamily: MONO, fontSize: TYPE.label, letterSpacing: "0.1em", textTransform: "uppercase", color: theme.warn,
                border: `2px dashed ${theme.warn}`, borderRadius: 8, padding: "6px 12px", opacity: useProgress(pending, 14),
              }}>Pending</span>
            </div>
          </Row>
        ))}
        <div style={{ position: "absolute", left: 1000, top: 720, display: "flex", gap: 14, opacity: useProgress(track, 15) }}>
          <span style={{ fontFamily: MONO, fontSize: TYPE.label, color: theme.inkSoft, alignSelf: "center" }}>TRACKED</span>
          {["Tokens", "Cost", "Processing time"].map((t) => <span key={t} style={{ padding: "10px 18px", border: `1px solid ${theme.line}`, borderRadius: 10, fontSize: TYPE.small }}>{t}</span>)}
        </div>
      </div>
      {/* the deliverable assembles section by section */}
      <div style={{
        position: "absolute", left: 460, top: 150, width: 1000, opacity: brief, transform: `translateY(${(1 - brief) * 30}px)`,
        background: theme.bgSoft, border: `1px solid ${theme.line}`, borderRadius: 20, padding: "40px 48px", boxSizing: "border-box",
      }}>
        <div style={{ fontFamily: MONO, fontSize: TYPE.label, letterSpacing: "0.14em", textTransform: "uppercase", color: theme.accent }}>Final deliverable</div>
        <div style={{ marginTop: 12, fontSize: TYPE.h2, fontWeight: 800, letterSpacing: "-0.02em" }}>Product Decision Brief</div>
        <div style={{ marginTop: 26 }}>
          {BRIEF.map((b, i) => {
            const p = interpolate(frame, [at(ID, b.cue), at(ID, b.cue) + 12], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
            return (
              <div key={b.t} style={{ display: "flex", alignItems: "center", gap: 20, height: 74, borderTop: `1px solid ${theme.line}`, opacity: p, transform: `translateY(${(1 - p) * 14}px)` }}>
                <span style={{ fontFamily: MONO, fontSize: TYPE.label, color: theme.inkSoft, width: 40 }}>{String(i + 1).padStart(2, "0")}</span>
                <span style={{ fontSize: TYPE.body, fontWeight: 600 }}>{b.t}</span>
              </div>
            );
          })}
        </div>
      </div>
      <Badge kind="concept" text="Proposed stack · resources pending" start={4} style={{ right: SPACE.gutter, bottom: 64 }} />
    </SceneShell>
  );
};
