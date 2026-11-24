import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { SceneShell } from "../components/SceneShell";
import { RevealText, Badge, useProgress } from "../components/primitives";
import { Connector } from "../components/diagram";
import { at } from "../components/cues";
import { theme, TYPE, SPACE } from "../config/theme";
import { CREDITS } from "../config/credits";
import { MONO } from "../components/fonts";

const ID = "s02_introducing";

const Box: React.FC<{ x: number; y: number; w: number; label: string; sub: string; enter: number; strong?: boolean }> = ({ x, y, w, label, sub, enter, strong }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const s = spring({ frame: frame - enter, fps, config: { damping: 200 } });
  return (
    <div style={{
      position: "absolute", left: x, top: y, width: w, opacity: s, transform: `translateY(${(1 - s) * 20}px)`,
      background: strong ? theme.accent : theme.bgSoft, color: strong ? theme.accentInk : theme.ink,
      border: `1px solid ${strong ? theme.accent : theme.line}`, borderRadius: 18, padding: "26px 28px", boxSizing: "border-box",
    }}>
      <div style={{ fontSize: TYPE.h3 - 4, fontWeight: 700 }}>{label}</div>
      <div style={{ marginTop: 8, fontSize: TYPE.small - 2, opacity: 0.8 }}>{sub}</div>
    </div>
  );
};

// What the brief covers, revealed on the narrated list.
const CONTENTS = [
  { t: "Competitors", cue: "competitors, customer" },
  { t: "Customer pain points", cue: "customer pain points" },
  { t: "Failure scenarios", cue: "potential failure scenarios" },
  { t: "Ways to validate", cue: "ways to validate it" },
];

export const S02Introducing: React.FC = () => {
  const frame = useCurrentFrame();
  const flow = at(ID, "It will take");
  const goal = at(ID, "The goal isn't");
  const titleUp = interpolate(frame, [flow - 10, flow + 10], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const goalP = useProgress(goal, 20);
  return (
    <SceneShell id={ID}>
      {/* product name + tagline: centred first, then slides up to make room for the flow */}
      <div style={{ position: "absolute", left: SPACE.gutter, top: interpolate(titleUp, [0, 1], [360, 170]) }}>
        <RevealText text={CREDITS.product} start={at(ID, "ProductLens AI", 4)} size={interpolate(titleUp, [0, 1], [TYPE.hero, TYPE.h1])} weight={800} />
        <div style={{ height: 18 }} />
        <RevealText text={CREDITS.tagline} start={at(ID, "ProductLens AI", 4) + 18} size={TYPE.h3} weight={500} color={theme.inkSoft} />
      </div>
      <Box x={SPACE.gutter} y={520} w={420} label="Product idea" sub="or a proposed feature" enter={flow} />
      <Connector d="M 540 590 L 700 590" start={flow + 12} color={theme.inkSoft} pulseAt={flow + 24} />
      <Box x={700} y={520} w={420} label={CREDITS.product} sub="research & decision support" enter={flow + 14} strong />
      <Connector d="M 1120 590 L 1280 590" start={flow + 26} color={theme.inkSoft} pulseAt={flow + 38} />
      <Box x={1280} y={520} w={520} label="Decision brief" sub="a structured assessment" enter={flow + 28} />
      {CONTENTS.map((c, i) => {
        const p = interpolate(frame, [at(ID, c.cue), at(ID, c.cue) + 12], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
        return (
          <div key={c.t} style={{
            position: "absolute", left: 1300, top: 700 + i * 62, opacity: p, transform: `translateX(${(1 - p) * 20}px)`,
            fontSize: TYPE.small, display: "flex", alignItems: "center", gap: 14,
          }}>
            <span style={{ width: 10, height: 10, borderRadius: 5, background: theme.accent }} />{c.t}
          </div>
        );
      })}
      <div style={{
        position: "absolute", left: SPACE.gutter, top: 760, width: 1040, opacity: goalP, transform: `translateY(${(1 - goalP) * 16}px)`,
        fontSize: TYPE.h3, fontWeight: 600, lineHeight: 1.25,
      }}>
        Not replacing product managers.<br /><span style={{ color: theme.inkSoft, fontWeight: 500 }}>Better-informed decisions, before time and money go into building.</span>
      </div>
      <div style={{ position: "absolute", right: SPACE.gutter, top: 64, fontFamily: MONO, fontSize: TYPE.label, letterSpacing: "0.14em", color: theme.inkSoft, opacity: useProgress(flow, 15) }}>
        IN DEVELOPMENT · {CREDITS.year}
      </div>
      <Badge kind="concept" start={flow} style={{ right: SPACE.gutter, bottom: 64 }} />
    </SceneShell>
  );
};
