"""Contact sheets of the stills (and pan start/end frames) for an eye check. Run with $TTS_PY (a Python with Pillow)."""
import json, sys
from pathlib import Path
from PIL import Image
B = Path(__file__).resolve().parents[1]
(B / "frames").mkdir(exist_ok=True)
plan = json.loads((B / "out" / "plan.json").read_text())
which = sys.argv[1] if len(sys.argv) > 1 else "last"
tiles = []
for beat, p in plan.items():
    if p["kind"] == "steps":
        chosen = p["steps"] if which == "all" else [p["steps"][-1]]
        for st in chosen:
            tiles.append((Path(st["png"]).stem, Image.open(B / st["png"]).convert("RGB")))
    else:
        src = Image.open(B / p["src"]).convert("RGBA"); ov = Image.open(B / p["overlay"]).convert("RGBA")
        x, y, w, h = p["window"]
        for tag, yy in (("start", p["y0"]), ("end", p["y1"])):
            fr = Image.new("RGBA", (1920, 1080), (10, 14, 19, 255))
            fr.paste(src.crop((0, yy, w, yy + h)), (x, y))
            fr = Image.alpha_composite(fr, ov).convert("RGB")
            fr.save(B / "frames" / f"{beat}_pan_{tag}.png")
            tiles.append((f"{beat}_pan_{tag}", fr))
out = B / "frames"
per = 9
for i in range(0, len(tiles), per):
    sheet = Image.new("RGB", (1920, 1080), (40, 40, 40))
    for j, (name, im) in enumerate(tiles[i:i + per]):
        sheet.paste(im.resize((636, 358)), ((j % 3) * 642, (j // 3) * 362))
    sheet.save(out / f"sheet_{which}_{i // per + 1}.png")
    print(f"sheet_{which}_{i // per + 1}.png:", [n for n, _ in tiles[i:i + per]])
