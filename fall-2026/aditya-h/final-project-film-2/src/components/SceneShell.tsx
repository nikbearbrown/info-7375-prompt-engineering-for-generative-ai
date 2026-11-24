import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { Stage, SectionMarker } from "./primitives";
import { SCENES, SECTIONS, sceneFrames } from "../config/timeline";

/** Every scene sits in this shell: same canvas, the section marker for its academic part, and a short fade in/out
 *  so cuts between scenes feel like one film rather than slides. */
export const SceneShell: React.FC<{ id: string; children: React.ReactNode; marker?: boolean }> = ({ id, children, marker = true }) => {
  const frame = useCurrentFrame();
  const entry = SCENES.find((s) => s.id === id);
  const total = entry ? sceneFrames(entry) : 300;
  const opacity = interpolate(frame, [0, 10, total - 12, total], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const sec = entry ? SECTIONS[entry.section] : undefined;
  return (
    <Stage>
      <AbsoluteFill style={{ opacity }}>
        {marker && sec && entry?.section !== "closing" && <SectionMarker index={sec.index} title={sec.title} />}
        {children}
      </AbsoluteFill>
    </Stage>
  );
};
