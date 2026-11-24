# PySceneDetect: false detections, fades, minimum scene length (for B10)

- Fetched: 2026-10-14 (Claude Code, WebFetch)
- URL: https://www.scenedetect.com/docs/latest/api/detectors.html

Relevant lines (quoted as returned by the fetch):

- AdaptiveDetector: "This can help mitigate false detections in situations such as fast camera motions."
- AdaptiveDetector: "that can help mitigate false detections in situations such as camera movement."
- ThresholdDetector: "Detects both fast cuts and slow fades so long as an appropriate threshold is chosen"
- min_scene_len: "Once a cut is detected, this much time must pass before a new one can be added to the scene list."

The fetched page does not mention camera flashes or a flash filter by name.
