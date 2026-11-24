// Editable look of the whole film. Change ACTIVE_THEME to switch palettes; every scene reads from here.
//
// "brand": ProductLens AI's existing identity, taken from the portfolio card (productlens-feature.tsx, Nov 2026):
//          off-white paper, near-black ink, signal red.
// "dark":  the brief's fallback for when no brand exists: dark editorial with restrained blue accents.

export type Theme = {
  name: string;
  bg: string;          // canvas
  bgSoft: string;      // raised surfaces (cards)
  ink: string;         // primary text
  inkSoft: string;     // secondary text
  line: string;        // hairlines, borders
  accent: string;      // the one accent colour
  accentInk: string;   // text that sits on the accent
  verified: string;    // "verified fact" marker
  hypothesis: string;  // "unvalidated hypothesis" marker
  warn: string;        // evaluator flag (insufficient evidence)
};

export const THEMES: Record<"brand" | "dark", Theme> = {
  brand: {
    name: "brand",
    bg: "#F3F0E8", bgSoft: "#FFFFFF", ink: "#111111", inkSoft: "#5A5750", line: "#D9D4C7",
    accent: "#F04438", accentInk: "#111111", verified: "#111111", hypothesis: "#8A857A", warn: "#B54708",
  },
  dark: {
    name: "dark",
    bg: "#0B0D10", bgSoft: "#14171C", ink: "#F2F4F7", inkSoft: "#98A2B3", line: "#262B33",
    accent: "#4C8DFF", accentInk: "#0B0D10", verified: "#F2F4F7", hypothesis: "#98A2B3", warn: "#F5A524",
  },
};

export const ACTIVE_THEME: keyof typeof THEMES = "dark";
export const theme: Theme = THEMES[ACTIVE_THEME];

export const VIDEO = { width: 1920, height: 1080, fps: 30 };

// Type scale (px at 1920×1080). Body text never goes below 28px, so it stays readable when the video is shrunk.
export const TYPE = { hero: 132, h1: 88, h2: 60, h3: 42, body: 32, small: 28, label: 24 };
export const SPACE = { gutter: 120, gap: 40 };
