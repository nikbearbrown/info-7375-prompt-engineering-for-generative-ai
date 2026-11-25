// Central timeline. One entry per scene, in film order. Narration text lives in src/narration/<id>.txt;
// tools/tts.py voices each file to public/audio/<id>.wav and writes the measured lengths to durations.json.
// A scene lasts exactly as long as its audio plus `padSeconds`; `fallbackSeconds` is used only before audio exists.
import durations from "./durations.json";
import scenesJson from "./scenes.json";
import { VIDEO } from "./theme";

export type Section = "summary" | "introduction" | "methods" | "evaluation" | "closing";

export type SceneEntry = {
  id: string;              // matches src/narration/<id>.txt, public/audio/<id>.wav and the component key in scenes/index.ts
  section: Section;
  fallbackSeconds: number; // planning length before narration is recorded
  padSeconds?: number;     // breathing room after the last word (default 0.6 s)
};

export const SECTIONS: Record<Section, { index: number; title: string; window: string }> = {
  summary: { index: 1, title: "Executive summary", window: "0:00–0:55" },
  introduction: { index: 2, title: "Introduction", window: "0:55–1:40" },
  methods: { index: 3, title: "Methods", window: "1:40–3:20" },
  evaluation: { index: 4, title: "Evaluation", window: "3:20–4:30" },
  closing: { index: 5, title: "Closing", window: "4:30–4:45" },
};

// Scene order and planning lengths live in scenes.json (shared with tools/*.py).
export const SCENES: SceneEntry[] = scenesJson as SceneEntry[];

const measured = durations as Record<string, number>;

export const sceneFrames = (s: SceneEntry) =>
  Math.ceil(((measured[s.id] ?? s.fallbackSeconds) + (s.padSeconds ?? 0.6)) * VIDEO.fps);

export const totalFrames = () => Math.max(1, SCENES.reduce((n, s) => n + sceneFrames(s), 0));

/** Start frame of every scene, for the timeline report and subtitles. */
export const sceneStarts = () => {
  let t = 0;
  return SCENES.map((s) => { const start = t; t += sceneFrames(s); return { id: s.id, section: s.section, start, frames: sceneFrames(s) }; });
};
