# Blender open movie with an English subtitle track

- Checked: 2026-10-14 (Claude Code, curl of the directory listing and file headers; WebFetch of the film page)

Film: Tears of Steel (Blender Foundation, 2012)

- English subtitle file: https://download.blender.org/demo/movies/ToS/subtitles/TOS-en.srt
  - HTTP 200, content-length 4764 bytes, last-modified Wed, 17 Oct 2012 14:21:37 GMT, 76 cues (counted by "-->" lines).
  - The same folder holds 24 .srt files in other languages.
- Film licence: https://mango.blender.org/about/ says "Tears of Steel is licensed as Creative Commons Attribution 3.0".
- https://download.blender.org/demo/movies/ToS/copyright.txt is Creative Commons Attribution-NoDerivs 3.0, but it says "This license applies to the Original Soundtrack files of Tears of Steel." It does not cover the subtitles.
- The subtitle folder and the film page fetched do not state a separate licence for the .srt files. Before a subtitle file enters the CueGate repo, its licence needs confirming (for example by email to foundation@blender.org, which copyright.txt gives for licensing questions).

Also seen: https://download.blender.org/durian/subs/ lists Sintel subtitle files in many languages. Not checked further.

No subtitle text was copied into this repository.
