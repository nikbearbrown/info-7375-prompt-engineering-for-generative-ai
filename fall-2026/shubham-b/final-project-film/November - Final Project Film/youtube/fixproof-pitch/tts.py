"""Run the toolkit's Kokoro audio script from this deep folder.

shortcut: bundled espeak-ng rejects data paths over 159 chars and this session folder is deeper,
so we chdir next to the data and hand espeak a relative path. Drop this once the toolkit lives
in a short folder (or a system espeak-ng is installed).
Usage: python3 tts.py <args for generate_audio_kokoro.py>
"""
import os, runpy, sys, pathlib
import espeakng_loader

data = pathlib.Path(espeakng_loader.get_data_path())
args = [str(pathlib.Path(a).resolve()) if pathlib.Path(a).exists() else a for a in sys.argv[1:]]
os.chdir(data.parent)
espeakng_loader.get_data_path = lambda: data.name
script = pathlib.Path(__file__).resolve().parents[2] / "vendor/brutalist.art/runtime/scripts/generate_audio_kokoro.py"
sys.path.insert(0, str(script.parent))
sys.argv = [str(script), *args]
runpy.run_path(str(script), run_name="__main__")
