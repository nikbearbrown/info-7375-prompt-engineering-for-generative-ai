import React from "react";
import { spring, useCurrentFrame, useVideoConfig } from "remotion";
import { SceneShell } from "../components/SceneShell";
import { RevealText, useProgress } from "../components/primitives";
import { at } from "../components/cues";
import { theme, TYPE, SPACE } from "../config/theme";
import { MONO } from "../components/fonts";

const ID = "s11_success";

const Panel: React.FC<{ x: number; title: string; tag: string; items: string[]; enter: number; accent: string }> = ({ x, title, tag, items, enter, accent }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const s = spring({ frame: frame - enter, fps, config: { damping: 200 } });
  return (
    <div style={{ position: "absolute", left: x, top: 230, width: 800, opacity: s, transform: `translateY(${(1 - s) * 30}px)`,
      border: `2px solid ${accent}`, borderRadius: 20, background: theme.bgSoft, padding: "36px 42px", boxSizing: "border-box" }}>
      <div style={{ fontFamily: MONO, fontSize: TYPE.label, letterSpacing: "0.14em", textTransform: "uppercase", color: accent }}>{tag}</div>
      <div style={{ marginTop: 10, fontSize: TYPE.h3 + 6, fontWeight: 800 }}>{title}</div>
      {items.map((t, i) => {
        const p = useProgress(enter + 12 + i * 8, 12);
        return <div key={t} style={{ marginTop: 22, fontSize: TYPE.body, opacity: p, display: "flex", gap: 16, alignItems: "baseline" }}><span style={{ color: accent }}>—</span>{t}</div>;
      })}
    </div>
  );
};

export const S11Success: React.FC = () => (
  <SceneShell id={ID}>
    <Panel x={SPACE.gutter} tag="Success looks like" title="Worth the complexity" enter={at(ID, "The project succeeds")} accent={theme.accent}
      items={["More grounded claims than the baseline", "Risks specific to the product", "Experiments you can actually run", "At an acceptable cost"]} />
    <Panel x={1000} tag="Also a valid result" title="Not worth it" enter={at(ID, "If the extra agents")} accent={theme.inkSoft}
      items={["No meaningful quality improvement", "Or cost and complexity out of proportion"]} />
    <div style={{ position: "absolute", left: SPACE.gutter, top: 800 }}>
      <RevealText text="Not “does it work?” but “is it worth using?”" start={at(ID, "It's to find out")} size={TYPE.h2} weight={800} />
    </div>
  </SceneShell>
);
