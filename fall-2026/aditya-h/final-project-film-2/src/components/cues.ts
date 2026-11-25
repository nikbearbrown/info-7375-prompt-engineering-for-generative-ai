import cues from "../config/cues.json";
import { VIDEO } from "../config/theme";

const norm = (w: string) => w.toLowerCase().replace(/[^a-z0-9']/g, "");

/** Frame (relative to the scene start) at which `phrase` is first spoken in scene `id`, minus a small lead.
 *  Falls back to `fallback` frames if the phrase isn't found, and logs it so a typo can't fail silently. */
export const at = (id: string, phrase: string, lead = 6, fallback = 0): number => {
  const ws = ((cues as unknown as Record<string, [string, number][]>)[id] ?? []);
  const target = phrase.split(/\s+/).map(norm);
  for (let i = 0; i + target.length <= ws.length; i++) {
    if (target.every((t, k) => norm(ws[i + k][0]) === t)) return Math.max(0, Math.round(ws[i][1] * VIDEO.fps) - lead);
  }
  console.warn(`[cues] "${phrase}" not found in ${id}`);
  return fallback;
};
