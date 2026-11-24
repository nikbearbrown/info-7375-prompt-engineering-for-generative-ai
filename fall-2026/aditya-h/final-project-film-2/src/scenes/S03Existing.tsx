import React from "react";
import { spring, useCurrentFrame, useVideoConfig } from "remotion";
import { SceneShell } from "../components/SceneShell";
import { RevealText, useProgress } from "../components/primitives";
import { at } from "../components/cues";
import { theme, TYPE, SPACE } from "../config/theme";
import { MONO } from "../components/fonts";

const ID = "s03_existing";

// Name cards (no logos: trademarks aren't ours to reuse). Descriptions follow each company's own wording, read
// 2026-11-23: Perplexity help center ("answers… with sources and citations"); productboard.com ("Centralize all product
// feedback", "Align teams on the right priorities"). ChatGPT/Claude: the script's generic "brainstorm and analyze".
const TOOLS = [
  { name: "ChatGPT", kind: "General AI assistant", does: "Brainstorm and analyze ideas", cue: "ChatGPT and Claude" },
  { name: "Claude", kind: "General AI assistant", does: "Brainstorm and analyze ideas", cue: "Claude can help" },
  { name: "Perplexity", kind: "AI search engine", does: "Answers with cited sources", cue: "Perplexity answers" },
  { name: "Productboard", kind: "Product management platform", does: "Centralize feedback, align on priorities", cue: "Productboard helps" },
];

export const S03Existing: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const each = at(ID, "Each one covers");
  const eachP = useProgress(each, 18);
  return (
    <SceneShell id={ID}>
      <div style={{ position: "absolute", left: SPACE.gutter, top: 170 }}>
        <RevealText text="What already exists" start={6} size={TYPE.h1} weight={800} />
      </div>
      {TOOLS.map((t, i) => {
        const s = spring({ frame: frame - at(ID, t.cue), fps, config: { damping: 200 } });
        const x = SPACE.gutter + i * 430;
        return (
          <div key={t.name} style={{
            position: "absolute", left: x, top: 400, width: 400, height: 330, opacity: s, transform: `translateY(${(1 - s) * 30}px)`,
            background: theme.bgSoft, border: `1px solid ${theme.line}`, borderRadius: 20, padding: "34px 32px", boxSizing: "border-box",
            display: "flex", flexDirection: "column",
          }}>
            <div style={{ fontFamily: MONO, fontSize: TYPE.label, letterSpacing: "0.12em", textTransform: "uppercase", color: theme.inkSoft }}>{t.kind}</div>
            <div style={{ marginTop: 18, fontSize: TYPE.h3 + 4, fontWeight: 800, letterSpacing: "-0.02em" }}>{t.name}</div>
            <div style={{ marginTop: "auto", fontSize: TYPE.body, lineHeight: 1.3, color: theme.ink }}>{t.does}</div>
          </div>
        );
      })}
      <div style={{ position: "absolute", left: SPACE.gutter, top: 800, opacity: eachP, transform: `translateY(${(1 - eachP) * 14}px)`, fontSize: TYPE.h3, fontWeight: 600 }}>
        Each covers a valuable <span style={{ color: theme.accent }}>part</span> of product management.
      </div>
      <div style={{ position: "absolute", left: SPACE.gutter, bottom: 56, fontFamily: MONO, fontSize: TYPE.label, color: theme.inkSoft, opacity: eachP }}>
        Descriptions from each company's own website, read Nov 23, 2026. Names only; no affiliation.
      </div>
    </SceneShell>
  );
};
