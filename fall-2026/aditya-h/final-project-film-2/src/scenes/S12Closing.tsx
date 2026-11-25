import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { SceneShell } from "../components/SceneShell";
import { RevealText, useProgress } from "../components/primitives";
import { at } from "../components/cues";
import { SCENES, sceneFrames } from "../config/timeline";
import { theme, TYPE } from "../config/theme";
import { CREDITS } from "../config/credits";
import { MONO } from "../components/fonts";

const ID = "s12_closing";

export const S12Closing: React.FC = () => {
  const frame = useCurrentFrame();
  const total = sceneFrames(SCENES.find((s) => s.id === ID)!);
  const credits = at(ID, "Because building");
  const tag = at(ID, "validating before we build");
  const c = useProgress(credits, 24);
  const black = interpolate(frame, [total - 40, total - 5], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <SceneShell id={ID} marker={false}>
      <AbsoluteFill style={{ alignItems: "center", justifyContent: "center", flexDirection: "column", textAlign: "center" }}>
        <RevealText text={CREDITS.product} start={10} size={TYPE.hero} weight={800} />
        <div style={{ height: 20 }} />
        <div style={{ fontSize: TYPE.h3, fontWeight: 500, color: theme.accent, opacity: useProgress(tag, 20) }}>{CREDITS.tagline}</div>
        <div style={{ height: 90 }} />
        <div style={{ opacity: c, transform: `translateY(${(1 - c) * 14}px)` }}>
          <div style={{ fontSize: TYPE.h3 - 4, fontWeight: 700 }}>{CREDITS.author}</div>
          <div style={{ marginTop: 16, fontSize: TYPE.body, color: theme.inkSoft }}>{CREDITS.course}</div>
          <div style={{ marginTop: 8, fontSize: TYPE.body, color: theme.inkSoft }}>{CREDITS.degree}</div>
          <div style={{ marginTop: 22, fontFamily: MONO, fontSize: TYPE.label, letterSpacing: "0.16em", textTransform: "uppercase", color: theme.inkSoft }}>
            {CREDITS.university} · {CREDITS.year}
          </div>
        </div>
      </AbsoluteFill>
      <AbsoluteFill style={{ background: "#000", opacity: black }} />
    </SceneShell>
  );
};
