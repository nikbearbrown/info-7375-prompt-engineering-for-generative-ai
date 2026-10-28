// Fixed settings from CONTRACT.md (In). Nothing here is read from the network or the environment.
import path from "node:path";
import { fileURLToPath } from "node:url";

export const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

export const BOARD = {
  name: "anthropic",
  host: "boards-api.greenhouse.io",
  url: "https://boards-api.greenhouse.io/v1/boards/anthropic/jobs",
};

// The only two hosts the agent may contact (CONTRACT.md, In, item 2).
export const ALLOWED_HOSTS = ["boards-api.greenhouse.io", "api.anthropic.com"];

export const MODEL = "claude-haiku-5-5";

export const PERSONA_PATH = path.join(ROOT, "persona", "priya-nair.resume.json");
export const PROMPT_PATH = path.join(ROOT, "prompts", "judge-v1.md");
