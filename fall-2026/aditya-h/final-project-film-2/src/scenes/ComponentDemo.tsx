import React from "react";
import { Stage, SectionMarker, Badge } from "../components/primitives";
import { AgentCard, Connector, SourceCard, ClaimRow, DataTable } from "../components/diagram";

// QA composition: every reusable piece on one canvas, to check sizing, contrast and motion before scenes use them.
export const ComponentDemo: React.FC = () => (
  <Stage>
    <SectionMarker index={3} title="Methods" />
    <SourceCard x={120} y={180} kind="Official docs" title="Example source title" meta="accessed 2026-11-23" enter={0} />
    <Connector d="M 540 240 C 640 240, 640 330, 740 330" start={10} pulseAt={30} />
    <AgentCard x={740} y={260} title="Market & Competition" subtitle="Alternatives and differentiation" enter={10} activeFrom={20} />
    <AgentCard x={1180} y={260} title="Evaluator" subtitle="Checks every citation" enter={14} doneAt={20} />
    <ClaimRow x={120} y={520} text="Example claim backed by a stored excerpt" status="supported" enter={20} />
    <ClaimRow x={120} y={600} text="Example claim with no supporting source yet" status="hypothesis" enter={24} />
    <DataTable x={120} y={700} enter={28} highlightCol={2}
      cols={[{ label: "Metric", w: 520 }, { label: "Config A", w: 260, align: "center" }, { label: "Proposed target", w: 360, align: "center" }]}
      rows={[["Schema validity", "—", "≥ 95%"], ["Evidence support", "—", "≥ 90%"]]} />
    <Badge kind="concept" style={{ right: 120, bottom: 72 }} />
  </Stage>
);
