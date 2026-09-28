# Font probe — NOT part of the video. Checks that Manim/Pango resolves the
# Windows-installed families by name. Row 3 is a deliberately fake family as a
# control: if it looks identical to rows 1-2, those rows are falling back too.
from manim import BLACK, DOWN, Scene, Text, VGroup, config

config.background_color = "#F5F0E8"


class FontProbe(Scene):
    def construct(self):
        rows = [
            ("EB Garamond", "EB Garamond - expected 665.24, observed 630"),
            ("Oswald", "OSWALD - EXPECTED 665.24, OBSERVED 630"),
            ("NoSuchFontXYZ", "NoSuchFontXYZ (control) - expected 665.24"),
        ]
        group = VGroup(*[Text(t, font=f, color=BLACK, font_size=44) for f, t in rows])
        group.arrange(DOWN, buff=0.6)
        self.add(group)
