import React from "react";
import { useCurrentFrame, useVideoConfig } from "remotion";
import cues from "../config/subtitles.json";
import { theme } from "../config/theme";

// Burned-in subtitles from tools/make_srt.py (same cues as the .srt). Toggle with SHOW_SUBTITLES in Film.tsx.
export const Subtitles: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  const cue = (cues as { start: number; end: number; text: string }[]).find((c) => t >= c.start && t < c.end);
  if (!cue) return null;
  return (
    <div style={{ position: "absolute", bottom: 40, left: 0, right: 0, display: "flex", justifyContent: "center" }}>
      <div style={{ maxWidth: 1400, padding: "10px 22px", borderRadius: 10, background: "rgba(0,0,0,0.72)", color: "#FFFFFF", fontSize: 32, lineHeight: 1.3, textAlign: "center" }}>
        {cue.text}
      </div>
    </div>
  );
};
