import React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig, Easing } from "remotion";
import { theme, TYPE, SPACE } from "../config/theme";
import { SANS, MONO } from "./fonts";

/** Eased 0→1 progress between two frames (clamped). */
export const useProgress = (from: number, dur: number, ease = Easing.bezier(0.22, 1, 0.36, 1)) => {
  const f = useCurrentFrame();
  return interpolate(f, [from, from + dur], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: ease });
};

/** Canvas with a very subtle radial wash and paper grain: no glow, no busy gradients. */
export const Stage: React.FC<{ children?: React.ReactNode }> = ({ children }) => (
  <AbsoluteFill style={{ background: theme.bg, fontFamily: SANS, color: theme.ink }}>
    <AbsoluteFill
      style={{
        background: `radial-gradient(ellipse 80% 60% at 30% 20%, ${theme.bgSoft}66 0%, transparent 70%)`,
      }}
    />
    <AbsoluteFill
      style={{
        opacity: 0.05,
        backgroundImage:
          "url(\"data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='160' height='160'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2'/></filter><rect width='160' height='160' filter='url(%23n)'/></svg>\")",
      }}
    />
    {children}
  </AbsoluteFill>
);

/** Words rise and fade in one after another. */
export const RevealText: React.FC<{
  text: string; start?: number; stagger?: number; size?: number; weight?: number; color?: string;
  style?: React.CSSProperties; maxWidth?: number;
}> = ({ text, start = 0, stagger = 3, size = TYPE.h1, weight = 700, color = theme.ink, style, maxWidth }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const words = text.split(" ");
  return (
    <div style={{ fontSize: size, fontWeight: weight, lineHeight: 1.05, letterSpacing: "-0.02em", color, maxWidth, ...style }}>
      {words.map((w, i) => {
        const s = spring({ frame: frame - start - i * stagger, fps, config: { damping: 200, mass: 0.6 } });
        return (
          <span key={i} style={{ display: "inline-block", opacity: s, transform: `translateY(${(1 - s) * 0.35}em)`, marginRight: "0.25em" }}>
            {w}
          </span>
        );
      })}
    </div>
  );
};

/** Small monospace eyebrow, e.g. "01 · Executive summary". */
export const Eyebrow: React.FC<{ children: React.ReactNode; start?: number; color?: string }> = ({ children, start = 0, color = theme.inkSoft }) => {
  const p = useProgress(start, 18);
  return (
    <div style={{ fontFamily: MONO, fontSize: TYPE.label, letterSpacing: "0.18em", textTransform: "uppercase", color, opacity: p, transform: `translateY(${(1 - p) * 12}px)` }}>
      {children}
    </div>
  );
};

/** Honesty badge. Everything that pictures the unbuilt product or a planned target carries one. */
export const Badge: React.FC<{ kind: "concept" | "proposed" | "real"; text?: string; start?: number; style?: React.CSSProperties }> = ({ kind, text, start = 0, style }) => {
  const p = useProgress(start, 15);
  const label = text ?? (kind === "concept" ? "Concept · planned, not built" : kind === "proposed" ? "Proposed target · not a result" : "Real");
  const filled = kind === "real";
  return (
    <div
      style={{
        position: "absolute", fontFamily: MONO, fontSize: TYPE.label, letterSpacing: "0.12em", textTransform: "uppercase",
        padding: "8px 14px", border: `2px solid ${theme.ink}`, background: filled ? theme.accent : theme.bg, color: filled ? theme.accentInk : theme.ink,
        opacity: p, ...style,
      }}
    >
      {label}
    </div>
  );
};

/** Persistent section marker in the top-left, so the four required parts are always visible. */
export const SectionMarker: React.FC<{ index: number; title: string }> = ({ index, title }) => (
  <div style={{ position: "absolute", top: 64, left: SPACE.gutter, display: "flex", gap: 16, alignItems: "center", fontFamily: MONO, fontSize: TYPE.label, letterSpacing: "0.16em", textTransform: "uppercase", color: theme.inkSoft }}>
    <span style={{ color: theme.accent, fontWeight: 700 }}>{String(index).padStart(2, "0")}</span>
    <span style={{ width: 40, height: 2, background: theme.line }} />
    <span>{title}</span>
  </div>
);
