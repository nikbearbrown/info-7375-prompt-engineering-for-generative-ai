import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { evolvePath, getLength, getPointAtLength } from "@remotion/paths";
import { theme, TYPE } from "../config/theme";
import { MONO } from "./fonts";
import { useProgress } from "./primitives";

/** Animated connection line (SVG path that draws itself), optionally with a dot travelling along it. */
export const Connector: React.FC<{
  d: string; start: number; dur?: number; color?: string; width?: number; pulseAt?: number; dashed?: boolean;
}> = ({ d, start, dur = 20, color = theme.line, width = 3, pulseAt, dashed }) => {
  const frame = useCurrentFrame();
  const p = useProgress(start, dur);
  const { strokeDasharray, strokeDashoffset } = evolvePath(p, d);
  const pulse = pulseAt === undefined ? -1 : interpolate(frame, [pulseAt, pulseAt + 24], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <svg style={{ position: "absolute", inset: 0, overflow: "visible", pointerEvents: "none" }} width={1920} height={1080}>
      <path d={d} fill="none" stroke={color} strokeWidth={width} strokeLinecap="round"
        strokeDasharray={dashed ? "8 10" : strokeDasharray} strokeDashoffset={dashed ? 0 : strokeDashoffset} opacity={dashed ? p : 1} />
      {pulse > 0 && pulse < 1 && <PathDot d={d} t={pulse} />}
    </svg>
  );
};

const PathDot: React.FC<{ d: string; t: number }> = ({ d, t }) => {
  // Pure path maths from @remotion/paths, so every frame renders the same way (no DOM measurement).
  const pt = getPointAtLength(d, getLength(d) * t);
  return <circle cx={pt.x} cy={pt.y} r={8} fill={theme.accent} />;
};

/** A card that pops in, then lights up (accent border + status dot) while it is "running". */
export const AgentCard: React.FC<{
  x: number; y: number; w?: number; h?: number; title: string; subtitle?: string; enter: number;
  activeFrom?: number; activeTo?: number; doneAt?: number; icon?: React.ReactNode;
}> = ({ x, y, w = 360, h = 150, title, subtitle, enter, activeFrom, activeTo, doneAt, icon }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const s = spring({ frame: frame - enter, fps, config: { damping: 200 } });
  const active = activeFrom !== undefined && frame >= activeFrom && (activeTo === undefined || frame < activeTo);
  const done = doneAt !== undefined && frame >= doneAt;
  const glow = active ? 0.5 + 0.5 * Math.sin((frame - (activeFrom ?? 0)) / 5) : 0;
  return (
    <div style={{
      position: "absolute", left: x, top: y, width: w, minHeight: h, opacity: s, transform: `translateY(${(1 - s) * 24}px)`,
      background: theme.bgSoft, border: `2px solid ${active ? theme.accent : theme.line}`, borderRadius: 18,
      padding: "22px 26px", boxSizing: "border-box", display: "flex", flexDirection: "column", justifyContent: "center",
      boxShadow: active ? `0 0 0 ${4 + glow * 4}px ${theme.accent}22` : "none",
    }}>
      <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
        {icon}
        <div style={{ fontSize: TYPE.h3 - 8, fontWeight: 700, letterSpacing: "-0.01em" }}>{title}</div>
        <div style={{ marginLeft: "auto", width: 14, height: 14, borderRadius: 7, background: done ? theme.ink : active ? theme.accent : theme.line }} />
      </div>
      {subtitle && <div style={{ marginTop: 10, fontSize: TYPE.small - 2, color: theme.inkSoft, lineHeight: 1.3 }}>{subtitle}</div>}
    </div>
  );
};

/** A research source entering the workflow: type tag, title, access date. Always labelled as an example when not real. */
export const SourceCard: React.FC<{ x: number; y: number; kind: string; title: string; meta: string; enter: number; w?: number }> = ({ x, y, kind, title, meta, enter, w = 420 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const s = spring({ frame: frame - enter, fps, config: { damping: 200 } });
  return (
    <div style={{
      position: "absolute", left: x, top: y, width: w, opacity: s, transform: `translateX(${(1 - s) * -60}px)`,
      background: theme.bgSoft, border: `1px solid ${theme.line}`, borderRadius: 14, padding: "18px 22px", boxSizing: "border-box",
    }}>
      <div style={{ fontFamily: MONO, fontSize: TYPE.label, letterSpacing: "0.14em", textTransform: "uppercase", color: theme.accent }}>{kind}</div>
      <div style={{ marginTop: 8, fontSize: TYPE.small, fontWeight: 600, lineHeight: 1.25 }}>{title}</div>
      <div style={{ marginTop: 6, fontFamily: MONO, fontSize: TYPE.label, color: theme.inkSoft }}>{meta}</div>
    </div>
  );
};

/** Claim row with an evidence status chip: verified fact vs unvalidated hypothesis (and disputed / insufficient). */
export const ClaimRow: React.FC<{
  x: number; y: number; w?: number; text: string; status: "supported" | "hypothesis" | "disputed" | "insufficient"; enter: number; statusAt?: number;
}> = ({ x, y, w = 900, text, status, enter, statusAt }) => {
  const p = useProgress(enter, 16);
  const q = useProgress(statusAt ?? enter + 12, 12);
  const label = { supported: "Verified · source-backed", hypothesis: "Hypothesis · unvalidated", disputed: "Disputed", insufficient: "Insufficient evidence" }[status];
  const solid = status === "supported";
  return (
    <div style={{ position: "absolute", left: x, top: y, width: w, display: "flex", alignItems: "center", gap: 20, opacity: p, transform: `translateY(${(1 - p) * 16}px)` }}>
      <div style={{ flex: 1, fontSize: TYPE.small, lineHeight: 1.3 }}>{text}</div>
      <div style={{
        opacity: q, fontFamily: MONO, fontSize: TYPE.label, letterSpacing: "0.1em", textTransform: "uppercase", whiteSpace: "nowrap",
        padding: "8px 12px", borderRadius: 8, border: `2px ${solid ? "solid" : "dashed"} ${solid ? theme.verified : theme.hypothesis}`,
        color: solid ? theme.verified : theme.hypothesis,
      }}>{label}</div>
    </div>
  );
};

/** Animated table: header first, then rows slide in one by one; optional highlighted column. */
export const DataTable: React.FC<{
  x: number; y: number; cols: { label: string; w: number; align?: "left" | "right" | "center" }[]; rows: React.ReactNode[][];
  enter: number; rowStagger?: number; highlightCol?: number; rowH?: number; fontSize?: number;
}> = ({ x, y, cols, rows, enter, rowStagger = 6, highlightCol, rowH = 64, fontSize = TYPE.small }) => {
  const head = useProgress(enter, 14);
  const frame = useCurrentFrame();
  const total = cols.reduce((n, c) => n + c.w, 0);
  return (
    <div style={{ position: "absolute", left: x, top: y, width: total }}>
      <div style={{ display: "flex", opacity: head, borderBottom: `2px solid ${theme.ink}`, paddingBottom: 12 }}>
        {cols.map((c, i) => (
          <div key={i} style={{ width: c.w, textAlign: c.align ?? "left", fontFamily: MONO, fontSize: TYPE.label, letterSpacing: "0.12em", textTransform: "uppercase", color: i === highlightCol ? theme.accent : theme.inkSoft }}>{c.label}</div>
        ))}
      </div>
      {rows.map((r, ri) => {
        const p = interpolate(frame, [enter + 10 + ri * rowStagger, enter + 22 + ri * rowStagger], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
        return (
          <div key={ri} style={{ display: "flex", alignItems: "center", height: rowH, borderBottom: `1px solid ${theme.line}`, opacity: p, transform: `translateX(${(1 - p) * 30}px)` }}>
            {r.map((cell, ci) => (
              <div key={ci} style={{ width: cols[ci].w, textAlign: cols[ci].align ?? "left", fontSize, fontWeight: ci === 0 ? 600 : 400, color: ci === highlightCol ? theme.ink : theme.ink }}>{cell}</div>
            ))}
          </div>
        );
      })}
    </div>
  );
};
