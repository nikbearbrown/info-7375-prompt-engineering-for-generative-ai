import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { SceneShell } from "../components/SceneShell";
import { RevealText } from "../components/primitives";
import { at } from "../components/cues";
import { theme, TYPE, SPACE } from "../config/theme";
import { MONO } from "../components/fonts";

const ID = "s01_problem";

// Four questions product teams face, each arriving on the matching spoken phrase.
const QUESTIONS = [
  { q: "Will customers use it?", cue: "understand their customers", x: 150, y: 520, r: -3 },
  { q: "Who are our competitors?", cue: "evaluate competitors", x: 1010, y: 470, r: 2.5 },
  { q: "What could go wrong?", cue: "identify risks", x: 300, y: 770, r: 2 },
  { q: "How do we validate it?", cue: "challenge their assumptions", x: 1080, y: 760, r: -2 },
];

export const S01Problem: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const gather = at(ID, "What if this process");
  const g = spring({ frame: frame - gather, fps, config: { damping: 200, mass: 1.2 } });
  const days = at(ID, "That can take days");
  return (
    <SceneShell id={ID}>
      <div style={{ position: "absolute", left: SPACE.gutter, top: 190 }}>
        <RevealText text="Is this product worth building?" start={8} size={TYPE.hero} weight={800} maxWidth={1600} />
      </div>
      {QUESTIONS.map((c, i) => {
        const enter = at(ID, c.cue);
        const s = spring({ frame: frame - enter, fps, config: { damping: 18, mass: 0.8 } });
        const drift = Math.sin((frame + i * 40) / 45) * 6 * (1 - g);
        // when the cards gather, they line up in a tidy 2×2 grid on the right
        const tx = 820 + (i % 2) * 520, ty = 520 + Math.floor(i / 2) * 170;
        const x = interpolate(g, [0, 1], [c.x, tx]), y = interpolate(g, [0, 1], [c.y, ty]) + drift;
        return (
          <div key={c.q} style={{
            position: "absolute", left: x, top: y, width: 480, opacity: s,
            transform: `scale(${0.9 + 0.1 * s}) rotate(${c.r * (1 - g)}deg)`,
            background: theme.bgSoft, border: `1px solid ${g > 0.5 ? theme.accent : theme.line}`, borderRadius: 16,
            padding: "26px 30px", fontSize: TYPE.h3 - 4, fontWeight: 600, boxSizing: "border-box",
          }}>{c.q}</div>
        );
      })}
      <div style={{
        position: "absolute", left: SPACE.gutter, top: 960, width: 700, fontFamily: MONO, fontSize: TYPE.label, letterSpacing: "0.14em",
        textTransform: "uppercase", color: theme.inkSoft,
        opacity: interpolate(frame, [days, days + 15, gather, gather + 10], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
      }}>Research that can take days</div>
      <div style={{
        position: "absolute", left: SPACE.gutter, top: 560, width: 680, opacity: g,
        fontSize: TYPE.h2 - 6, fontWeight: 700, lineHeight: 1.1, letterSpacing: "-0.02em", whiteSpace: "nowrap",
      }}>More structured.<br /><span style={{ color: theme.accent }}>More evidence-driven.</span></div>
    </SceneShell>
  );
};
