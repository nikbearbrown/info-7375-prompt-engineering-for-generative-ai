import React from "react";
import { Stage, RevealText, Eyebrow, Badge, SectionMarker } from "../components/primitives";
import { theme, TYPE, SPACE } from "../config/theme";

// Temporary style frame used to check fonts, colours and the render pipeline before the real scenes exist.
export const StyleFrame: React.FC = () => (
  <Stage>
    <SectionMarker index={1} title="Executive summary" />
    <div style={{ position: "absolute", left: SPACE.gutter, top: 330 }}>
      <Eyebrow start={0}>ProductLens AI</Eyebrow>
      <div style={{ height: 28 }} />
      <RevealText text="Should we build this feature?" start={8} size={TYPE.hero} weight={800} />
      <div style={{ height: 36 }} />
      <RevealText text="An evidence-backed decision brief, before you build." start={30} size={TYPE.h3} weight={500} color={theme.inkSoft} />
    </div>
    <Badge kind="concept" start={40} style={{ right: SPACE.gutter, bottom: 72 }} />
  </Stage>
);
