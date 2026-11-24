import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { SceneShell } from "../components/SceneShell";
import { Badge, Eyebrow, useProgress } from "../components/primitives";
import { at } from "../components/cues";
import { theme, TYPE, SPACE } from "../config/theme";
import { MONO } from "../components/fonts";

const ID = "s05_idea";

// Concept intake screen (no app exists yet). The example is scenario S01 from 04-Evaluation.md.
const FIELDS = [
  { label: "Product idea", value: "AI-powered personal finance app", cue: "For example" },
  { label: "Audience", value: "International students in the United States", cue: "international students in" },
  { label: "Objective", value: "Simplify budgeting, expense tracking and financial planning", cue: "international students in", delay: 40 },
];

const Typed: React.FC<{ text: string; start: number; cps?: number }> = ({ text, start, cps = 1.6 }) => {
  const frame = useCurrentFrame();
  const n = Math.max(0, Math.min(text.length, Math.floor((frame - start) * cps)));
  const caret = frame >= start && n < text.length && Math.floor(frame / 8) % 2 === 0;
  return <>{text.slice(0, n)}<span style={{ opacity: caret ? 1 : 0, color: theme.accent }}>|</span></>;
};

export const S05Idea: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const win = spring({ frame: frame - at(ID, "A user enters"), fps, config: { damping: 200 } });
  const press = at(ID, "hand it to");
  const pressed = frame >= press && frame < press + 8;
  const scope = useProgress(at(ID, "will define the research scope"), 20);
  return (
    <SceneShell id={ID}>
      <div style={{ position: "absolute", left: SPACE.gutter, top: 150 }}>
        <Eyebrow start={4}>How it's designed to work</Eyebrow>
        <div style={{ height: 14 }} />
        <div style={{ fontSize: TYPE.h2, fontWeight: 800, letterSpacing: "-0.02em", opacity: useProgress(8, 18) }}>Start with a product idea</div>
      </div>
      {/* concept intake window */}
      <div style={{
        position: "absolute", left: SPACE.gutter, top: 330, width: 1080, opacity: win, transform: `translateY(${(1 - win) * 30}px)`,
        background: theme.bgSoft, border: `1px solid ${theme.line}`, borderRadius: 20, overflow: "hidden",
      }}>
        <div style={{ height: 52, borderBottom: `1px solid ${theme.line}`, display: "flex", alignItems: "center", gap: 10, padding: "0 22px" }}>
          {[0, 1, 2].map((i) => <span key={i} style={{ width: 12, height: 12, borderRadius: 6, background: theme.line }} />)}
          <span style={{ marginLeft: 16, fontFamily: MONO, fontSize: TYPE.label, color: theme.inkSoft }}>ProductLens AI · New analysis</span>
        </div>
        <div style={{ padding: "34px 40px 40px" }}>
          {FIELDS.map((f) => (
            <div key={f.label} style={{ marginBottom: 26 }}>
              <div style={{ fontFamily: MONO, fontSize: TYPE.label, letterSpacing: "0.12em", textTransform: "uppercase", color: theme.inkSoft }}>{f.label}</div>
              <div style={{ marginTop: 10, minHeight: 64, border: `1px solid ${theme.line}`, borderRadius: 12, padding: "16px 20px", boxSizing: "border-box", fontSize: TYPE.body }}>
                <Typed text={f.value} start={at(ID, f.cue) + (f.delay ?? 0)} />
              </div>
            </div>
          ))}
          <div style={{
            display: "inline-block", marginTop: 6, padding: "16px 30px", borderRadius: 12, fontSize: TYPE.body, fontWeight: 700,
            background: theme.accent, color: theme.accentInk, transform: `scale(${pressed ? 0.95 : 1})`,
          }}>Start analysis →</div>
        </div>
      </div>
      {/* research scope produced from the input */}
      <div style={{ position: "absolute", left: 1300, top: 330, width: 500, opacity: scope, transform: `translateX(${(1 - scope) * 30}px)` }}>
        <div style={{ fontFamily: MONO, fontSize: TYPE.label, letterSpacing: "0.12em", textTransform: "uppercase", color: theme.accent }}>Research scope</div>
        {["Who already serves this need?", "What do students struggle with?", "How could it fail?"].map((q, i) => {
          const p = interpolate(frame, [at(ID, "will define the research scope") + 10 + i * 10, at(ID, "will define the research scope") + 24 + i * 10], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
          return <div key={q} style={{ marginTop: 18, opacity: p, padding: "18px 22px", border: `1px solid ${theme.line}`, borderRadius: 12, fontSize: TYPE.small }}>{q}</div>;
        })}
        <div style={{ marginTop: 24, fontSize: TYPE.small, color: theme.inkSoft, opacity: useProgress(press, 15) }}>→ handed to specialized agents</div>
      </div>
      <Badge kind="concept" text="Concept UI · illustrative, not built" start={at(ID, "A user enters")} style={{ right: SPACE.gutter, bottom: 64 }} />
    </SceneShell>
  );
};
