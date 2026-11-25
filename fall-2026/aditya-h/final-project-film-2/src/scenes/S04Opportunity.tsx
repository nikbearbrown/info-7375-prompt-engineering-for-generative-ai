import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { SceneShell } from "../components/SceneShell";
import { Badge, useProgress } from "../components/primitives";
import { at } from "../components/cues";
import { theme, TYPE, SPACE } from "../config/theme";
import { MONO } from "../components/fonts";

const ID = "s04_opportunity";

const FRAGMENTS = [
  { t: "Market research", x: 140, y: 250, r: -4 },
  { t: "Customer insights", x: 1180, y: 230, r: 3 },
  { t: "Failure analysis", x: 220, y: 720, r: 3 },
  { t: "Validation planning", x: 1160, y: 700, r: -3 },
];
const PILLARS = [
  { t: "Assumptions", cue: "questions assumptions" },
  { t: "Evidence", cue: "links claims to evidence" },
  { t: "Risks", cue: "turns risks into" },
  { t: "Experiments", cue: "measurable experiments" },
];

export const S04Opportunity: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const merge = at(ID, "combined into one");
  const m = spring({ frame: frame - merge, fps, config: { damping: 200, mass: 1.4 } });
  const test = at(ID, "Whether that actually");
  return (
    <SceneShell id={ID}>
      {/* scattered activities joined by dashed "manual work" lines, then pulled into one brief */}
      <svg width={1920} height={1080} style={{ position: "absolute", inset: 0, opacity: 1 - m }}>
        {[[0, 1], [1, 3], [3, 2], [2, 0]].map(([a, b], i) => {
          const A = FRAGMENTS[a], B = FRAGMENTS[b];
          return <line key={i} x1={A.x + 230} y1={A.y + 50} x2={B.x + 230} y2={B.y + 50} stroke={theme.line} strokeWidth={3} strokeDasharray="10 12"
            opacity={useProgress(30 + i * 8, 20)} />;
        })}
      </svg>
      <div style={{ position: "absolute", left: 760, top: 470, width: 400, textAlign: "center", fontFamily: MONO, fontSize: TYPE.label, letterSpacing: "0.12em", textTransform: "uppercase", color: theme.inkSoft, opacity: (1 - m) * useProgress(40, 20) }}>
        Manual work in between
      </div>
      {FRAGMENTS.map((f, i) => {
        const s = spring({ frame: frame - i * 6, fps, config: { damping: 200 } });
        const x = interpolate(m, [0, 1], [f.x, 730]), y = interpolate(m, [0, 1], [f.y, 300 + i * 4]);
        return (
          <div key={f.t} style={{
            position: "absolute", left: x, top: y, width: 460, opacity: s * (1 - m * 0.9),
            transform: `rotate(${f.r * (1 - m)}deg) scale(${1 - m * 0.3})`,
            background: theme.bgSoft, border: `1px solid ${theme.line}`, borderRadius: 16, padding: "26px 30px", boxSizing: "border-box",
            fontSize: TYPE.h3 - 6, fontWeight: 600,
          }}>{f.t}</div>
        );
      })}
      {/* the unified brief */}
      <div style={{
        position: "absolute", left: 460, top: 300, width: 1000, opacity: m, transform: `scale(${0.92 + 0.08 * m})`,
        background: theme.bgSoft, border: `2px solid ${theme.accent}`, borderRadius: 22, padding: "40px 48px", boxSizing: "border-box",
      }}>
        <div style={{ fontFamily: MONO, fontSize: TYPE.label, letterSpacing: "0.14em", textTransform: "uppercase", color: theme.accent }}>One coordinated workflow</div>
        <div style={{ marginTop: 14, fontSize: TYPE.h2, fontWeight: 800, letterSpacing: "-0.02em" }}>Product Decision Brief</div>
        <div style={{ marginTop: 34, display: "flex", gap: 16, flexWrap: "wrap" }}>
          {PILLARS.map((p) => {
            const q = interpolate(frame, [at(ID, p.cue), at(ID, p.cue) + 12], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
            return <div key={p.t} style={{ opacity: q, transform: `translateY(${(1 - q) * 10}px)`, padding: "12px 20px", border: `1px solid ${theme.line}`, borderRadius: 12, fontSize: TYPE.small, fontWeight: 600 }}>{p.t}</div>;
          })}
        </div>
      </div>
      <Badge kind="proposed" text="Hypothesis · to be tested in this project" start={test} style={{ left: 460, top: 640 }} />
      <Badge kind="concept" start={merge} style={{ right: SPACE.gutter, bottom: 64 }} />
    </SceneShell>
  );
};
