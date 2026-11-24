import React from "react";
import { interpolate, useCurrentFrame } from "remotion";
import { SceneShell } from "../components/SceneShell";
import { Badge, useProgress } from "../components/primitives";
import { AgentCard, Connector, SourceCard } from "../components/diagram";
import { at } from "../components/cues";
import { theme, TYPE, SPACE } from "../config/theme";
import { MONO } from "../components/fonts";

const ID = "s06_agents";

const SOURCES = [
  { kind: "Official site", title: "Product websites", cue: "official product websites" },
  { kind: "Docs", title: "Documentation", cue: "documentation," },
  { kind: "Reviews", title: "Customer reviews", cue: "customer reviews" },
  { kind: "Research", title: "Industry publications", cue: "industry publications" },
];
const AGENTS = [
  { t: "Market & Competition", sub: "Existing solutions, room to differentiate", cue: "The Market and", next: "The Customer and" },
  { t: "Customer & Adoption", sub: "Needs, pain points, adoption barriers", cue: "The Customer and", next: "The Failure and" },
  { t: "Failure & Risk", sub: "How it could fail, critical assumptions", cue: "The Failure and", next: "Each agent has" },
];

// Prompt contract excerpt, condensed from 03-Agent-Prompts.md (Failure and Risk Agent) and 02-Architecture.md (Risk type).
const CONTRACT = [
  ["agent", "failure_risk · prompt v0.1 (draft)"],
  ["role", "product pre-mortem"],
  ["rules", "use only supplied evidence · never invent sources"],
  ["output", "Risk[] { scenario, likelihood 1–5, impact 1–5,"],
  ["", "         earlySignal, mitigation, claimIds }"],
];

export const S06Agents: React.FC = () => {
  const frame = useCurrentFrame();
  const orch = at(ID, "An orchestrator");
  const contract = at(ID, "Each agent has");
  const shift = interpolate(frame, [contract - 6, contract + 18], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const c = useProgress(contract + 4, 20);
  const ys = [250, 470, 690];
  return (
    <SceneShell id={ID}>
      <div style={{ position: "absolute", inset: 0, transform: `translateX(${-shift * 380}px)`, opacity: 1 - shift * 0.85 }}>
        {SOURCES.map((s, i) => (
          <SourceCard key={s.title} x={SPACE.gutter} y={200 + i * 175} w={360} kind={s.kind} title={s.title} meta="public source" enter={at(ID, s.cue)} />
        ))}
        {SOURCES.map((s, i) => (
          <Connector key={i} d={`M 480 ${262 + i * 175} C 560 ${262 + i * 175}, 560 540, 620 540`} start={at(ID, s.cue) + 8} color={theme.line} />
        ))}
        <AgentCard x={620} y={470} w={300} title="Orchestrator" subtitle="Scope · research plan" enter={orch} activeFrom={orch} activeTo={at(ID, "The Market and")} doneAt={at(ID, "The Market and")} />
        {AGENTS.map((a, i) => (
          <React.Fragment key={a.t}>
            <Connector d={`M 920 540 C 990 540, 990 ${ys[i] + 70}, 1060 ${ys[i] + 70}`} start={orch + 20 + i * 6} color={theme.inkSoft} pulseAt={at(ID, a.cue) - 10} />
            <AgentCard x={1060} y={ys[i]} w={440} title={a.t} subtitle={a.sub} enter={orch + 24 + i * 6}
              activeFrom={at(ID, a.cue)} activeTo={at(ID, a.next)} doneAt={at(ID, a.next)} />
            <Connector d={`M 1500 ${ys[i] + 70} C 1560 ${ys[i] + 70}, 1560 540, 1620 540`} start={at(ID, a.next)} color={theme.inkSoft} />
          </React.Fragment>
        ))}
        <AgentCard x={1620} y={470} w={260} title="Findings" subtitle="consolidated" enter={at(ID, "Each agent has") - 10} doneAt={at(ID, "several focused tasks")} />
      </div>
      {/* prompt contract + structured output, sliding in as the narration explains them */}
      <div style={{
        position: "absolute", right: SPACE.gutter, top: 220, width: 1180, opacity: c, transform: `translateX(${(1 - c) * 60}px)`,
        background: theme.bgSoft, border: `1px solid ${theme.accent}`, borderRadius: 18, padding: "32px 36px", boxSizing: "border-box",
      }}>
        <div style={{ fontFamily: MONO, fontSize: TYPE.label, letterSpacing: "0.12em", textTransform: "uppercase", color: theme.accent }}>Prompt contract · draft</div>
        <div style={{ marginTop: 22, fontFamily: MONO, fontSize: 28, lineHeight: 1.6 }}>
          {CONTRACT.map(([k, v], i) => {
            const p = interpolate(frame, [contract + 14 + i * 8, contract + 26 + i * 8], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
            return (
              <div key={i} style={{ opacity: p, whiteSpace: "pre" }}>
                <span style={{ color: theme.inkSoft }}>{k ? `${k}:`.padEnd(8) : "        "}</span>{v}
              </div>
            );
          })}
        </div>
        <div style={{ marginTop: 26, fontSize: TYPE.small, color: theme.inkSoft, opacity: useProgress(at(ID, "several focused tasks"), 15) }}>
          One large research problem → several focused, checkable tasks.
        </div>
      </div>
      <Badge kind="concept" text="Concept · planned workflow" start={4} style={{ right: SPACE.gutter, bottom: 64 }} />
      <div style={{ position: "absolute", left: SPACE.gutter, bottom: 64, fontFamily: MONO, fontSize: TYPE.label, color: theme.inkSoft, opacity: useProgress(at(ID, "official product websites"), 15) }}>
        Example source types · public only
      </div>
    </SceneShell>
  );
};
