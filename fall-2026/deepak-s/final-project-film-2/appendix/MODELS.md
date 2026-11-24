# Appendix: candidate local models (RESOURCES item 4)

No shortening or meaning-check model has been chosen yet. These are candidates. The film names none of them; it says only "public models that download and run locally".


Checked 2026-11-23 by Claude Code with curl, no login and no token: the Hugging Face model API (`/api/models/` plus the model id; fields `gated` and licence) and an anonymous ranged GET of `resolve/main/config.json`. A gated repository refuses every file, weights included.

| Model | Use | Licence | Gated | Anonymous download |
|---|---|---|---|---|
| microsoft/deberta-large-mnli | meaning check (NLI) | MIT | no | yes (HTTP 206) |
| cross-encoder/nli-deberta-v3-base | meaning check (NLI) | Apache-2.0 | no | yes (HTTP 206) |
| MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli | meaning check (NLI) | MIT | no | yes (HTTP 206) |
| Qwen/Qwen2.5-1.5B-Instruct | shortening | Apache-2.0 | no | yes (HTTP 206) |
| HuggingFaceTB/SmolLM2-1.7B-Instruct | shortening | Apache-2.0 | no | yes (HTTP 206) |
| microsoft/Phi-3.5-mini-instruct | shortening | MIT | no | yes (HTTP 206) |
| meta-llama/Llama-3.2-1B-Instruct | shortening | Llama 3.2 | manual | no (HTTP 401) |
| google/gemma-2-2b-it | shortening | Gemma | manual | no (HTTP 401) |
