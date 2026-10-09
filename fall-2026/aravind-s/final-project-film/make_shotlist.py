#!/usr/bin/env python3
"""make_shotlist.py: write SHOTLIST.md from beat_sheet.json (run after make_sheet.py)."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
sheet = json.loads((HERE / "beat_sheet.json").read_text())
rows = [
    "# Shot list: Klaxon pitch film",
    "",
    "One picture per beat. Drawn beats are Manim (the show-tell kit plus its 25 approved original props); the two "
    "opening bookends and one data card are Remotion. Every beat is filled by the pipeline; no slot is left for a "
    "person to fill.",
    "",
    "| Beat | Lane | Picture (what moves) | On-screen tag | Why a card |",
    "|---|---|---|---|---|",
]
for b in sheet["beats"]:
    shot = b["shot"]
    if shot.get("remotion"):
        lane = "Remotion " + shot["remotion"]["pattern"]
        picture = b.get("motion_claim") or "Terms card: webhook, idempotent."
    else:
        lane = "Manim " + shot["manim"]["class"]
        picture = shot["visual_intent"]
    tag = b.get("honesty_tag", "")
    if b["beat_id"] == "B12":
        tag = "heading: Real run, Oct 9, synthetic data"
    rows.append(f"| {b['beat_id']} | {lane} | {picture} | {tag} | {b.get('why_card', '')} |")
(HERE / "SHOTLIST.md").write_text("\n".join(rows) + "\n")
print("wrote SHOTLIST.md,", len(sheet["beats"]), "beats")
