import React from "react";
import { AbsoluteFill, Audio, Series, staticFile } from "remotion";
import { SCENES, sceneFrames } from "./config/timeline";
import durations from "./config/durations.json";
import { SCENE_COMPONENTS } from "./scenes";
import { Subtitles } from "./components/Subtitles";
import { theme } from "./config/theme";

export const SHOW_SUBTITLES = false; // the .srt ships separately; set true to burn captions into the MP4

export const Film: React.FC = () => (
  <AbsoluteFill style={{ background: theme.bg }}>
    <Series>
      {SCENES.map((s) => {
        const C = SCENE_COMPONENTS[s.id];
        const hasAudio = (durations as Record<string, number>)[s.id] !== undefined;
        return (
          <Series.Sequence key={s.id} durationInFrames={sceneFrames(s)} name={s.id}>
            {C ? <C /> : null}
            {hasAudio && <Audio src={staticFile(`audio/${s.id}.wav`)} />}
          </Series.Sequence>
        );
      })}
    </Series>
    {SHOW_SUBTITLES && <Subtitles />}
  </AbsoluteFill>
);
