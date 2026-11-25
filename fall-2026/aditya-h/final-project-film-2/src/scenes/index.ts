import React from "react";
import { S01Problem } from "./S01Problem";
import { S02Introducing } from "./S02Introducing";
import { S03Existing } from "./S03Existing";
import { S04Opportunity } from "./S04Opportunity";
import { S05Idea } from "./S05Idea";
import { S06Agents } from "./S06Agents";
import { S07Verification } from "./S07Verification";
import { S08Resources } from "./S08Resources";
import { S09Design } from "./S09Design";
import { S10Metrics } from "./S10Metrics";
import { S11Success } from "./S11Success";
import { S12Closing } from "./S12Closing";

// Scene id (as in config/scenes.json) -> component.
export const SCENE_COMPONENTS: Record<string, React.FC> = {
  s01_problem: S01Problem,
  s02_introducing: S02Introducing,
  s03_existing: S03Existing,
  s04_opportunity: S04Opportunity,
  s05_idea: S05Idea,
  s06_agents: S06Agents,
  s07_verification: S07Verification,
  s08_resources: S08Resources,
  s09_design: S09Design,
  s10_metrics: S10Metrics,
  s11_success: S11Success,
  s12_closing: S12Closing,
};
