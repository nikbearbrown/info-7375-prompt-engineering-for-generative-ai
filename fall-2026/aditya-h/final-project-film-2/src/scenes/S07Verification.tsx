import React from "react";
import { interpolate, useCurrentFrame } from "remotion";
import { SceneShell } from "../components/SceneShell";
import { Badge, Eyebrow, RevealText, useProgress } from "../components/primitives";
import { AgentCard, ClaimRow, Connector } from "../components/diagram";
import { at } from "../components/cues";
import { theme, TYPE, SPACE } from "../config/theme";
import { MONO } from "../components/fonts";

const ID = "s07_verification";

// Illustrative claim and revision from the storyboard (Scene 07). Not output from a real run.
const BEFORE = "International students prefer AI-based budgeting tools.";
const AFTER = "International students may benefit from AI-assisted budgeting. This preference requires user testing.";
const CHECKS = [
  { t: "Unsupported claims", cue: "unsupported claims" },
  { t: "Inconsistencies", cue: "inconsistencies" },
  { t: "Missing evidence", cue: "missing evidence" },
  { t: "Vague recommendations", cue: "too vague to" },
];

export const S07Verification: React.FC = () => {
  const frame = useCurrentFrame();
  const evalIn = at(ID, "An Evaluator Agent");
  const flag = at(ID, "When it finds");
  const revise = at(ID, "revised and checked");
  const labels = at(ID, "And every claim");
  const flagP = useProgress(flag, 14);
  const revP = useProgress(revise + 6, 22);
  const lab = useProgress(labels, 18);
  const top = interpolate(lab, [0, 1], [0, -60]);
  return (
    <SceneShell id={ID}>
      <div style={{ position: "absolute", left: SPACE.gutter, top: 150 }}>
        <RevealText text="Convincing isn't the same as correct." start={6} size={TYPE.h2} weight={800} />
      </div>
      <div style={{ position: "absolute", inset: 0, transform: `translateY(${top}px)`, opacity: 1 - lab }}>
        {/* the claim under review */}
        <div style={{ position: "absolute", left: SPACE.gutter, top: 330, width: 900 }}>
          <Eyebrow start={evalIn - 10}>Draft finding · illustrative</Eyebrow>
          <div style={{
            marginTop: 16, padding: "28px 32px", borderRadius: 16, fontSize: TYPE.h3 - 6, fontWeight: 600, lineHeight: 1.3,
            background: theme.bgSoft, border: `2px solid ${flagP > 0.5 && revP < 0.5 ? theme.warn : theme.line}`, opacity: useProgress(evalIn - 10, 16),
          }}>
            {revP < 0.5 ? BEFORE : AFTER}
          </div>
          <div style={{
            marginTop: 16, display: "inline-block", fontFamily: MONO, fontSize: TYPE.label, letterSpacing: "0.1em", textTransform: "uppercase",
            padding: "8px 14px", borderRadius: 8, opacity: flagP,
            border: `2px ${revP < 0.5 ? "solid" : "dashed"} ${revP < 0.5 ? theme.warn : theme.hypothesis}`, color: revP < 0.5 ? theme.warn : theme.hypothesis,
          }}>{revP < 0.5 ? "Flagged · insufficient evidence" : "Hypothesis · validation required"}</div>
        </div>
        {/* evaluator and its checklist */}
        <AgentCard x={1180} y={330} w={600} title="Evaluator Agent" subtitle="Reviews every finding" enter={evalIn} activeFrom={evalIn} activeTo={revise + 20} doneAt={revise + 20} />
        {CHECKS.map((c, i) => {
          const p = interpolate(frame, [at(ID, c.cue), at(ID, c.cue) + 10], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
          return (
            <div key={c.t} style={{ position: "absolute", left: 1210, top: 520 + i * 64, opacity: p, fontSize: TYPE.small, display: "flex", gap: 14, alignItems: "center" }}>
              <span style={{ width: 22, height: 22, border: `2px solid ${theme.inkSoft}`, borderRadius: 5 }} />{c.t}
            </div>
          );
        })}
        {/* targeted revision loop: evaluator → back to the finding → checked again */}
        <Connector d="M 1180 420 C 1100 420, 1100 560, 1020 560" start={flag} color={theme.warn} pulseAt={flag + 6} />
        <Connector d="M 1020 620 C 1110 640, 1120 470, 1180 455" start={revise} color={theme.inkSoft} pulseAt={revise + 8} dashed />
        <div style={{ position: "absolute", left: 1040, top: 640, fontFamily: MONO, fontSize: TYPE.label, color: theme.inkSoft, opacity: useProgress(revise, 15) }}>revise → check again</div>
      </div>
      {/* every claim carries a status */}
      <div style={{ opacity: lab }}>
        <ClaimRow x={SPACE.gutter} y={470} w={1680} text="Example: a claim whose cited source actually says it" status="supported" enter={labels} />
        <ClaimRow x={SPACE.gutter} y={580} w={1680} text={AFTER} status="hypothesis" enter={labels + 10} />
        <div style={{ position: "absolute", left: SPACE.gutter, top: 720, fontSize: TYPE.h3 - 4, fontWeight: 600, opacity: useProgress(at(ID, "so uncertainty becomes"), 18) }}>
          Uncertainty becomes an <span style={{ color: theme.accent }}>explicit</span> part of the result.
        </div>
      </div>
      <Badge kind="concept" text="Illustrative example · not a real run" start={evalIn - 10} style={{ right: SPACE.gutter, bottom: 64 }} />
    </SceneShell>
  );
};
