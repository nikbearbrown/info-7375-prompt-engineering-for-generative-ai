#!/usr/bin/env python3
"""appendix_pdf.py: APPENDIX.md -> APPENDIX.html -> APPENDIX.pdf, with python-markdown and headless Chrome.

Relative links to evidence files stay as text in the PDF. The Markdown file is the source. Written by Claude Code,
2026-11-21.
Run: python3 tools/appendix_pdf.py
"""
import subprocess
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent.parent
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
CSS = """
body { font-family: Georgia, 'EB Garamond', serif; font-size: 10.5pt; line-height: 1.42; color: #1d1b16;
       max-width: 7.3in; margin: 0 auto; }
h1 { font-size: 19pt; margin-bottom: 2pt; } h2 { font-size: 13pt; margin-top: 16pt; border-bottom: 1px solid #ccc; }
table { border-collapse: collapse; width: 100%; font-size: 9pt; margin: 6pt 0; }
th, td { border: 1px solid #bbb; padding: 3pt 5pt; vertical-align: top; text-align: left; }
th { background: #f1ede4; } code { font-family: Menlo, monospace; font-size: 8.5pt; background: #f4f1ea; padding: 0 2px; }
em { color: #4a463d; } a { color: #1d1b16; }
@page { size: Letter; margin: 0.7in; }
"""

md = (ROOT / "APPENDIX.md").read_text()
body = markdown.markdown(md, extensions=["tables", "fenced_code"])
html = f"<!doctype html><html><head><meta charset='utf-8'><title>Fine Print — Appendix</title><style>{CSS}</style></head><body>{body}</body></html>"
(ROOT / "APPENDIX.html").write_text(html)
subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                f"--print-to-pdf={ROOT / 'APPENDIX.pdf'}", (ROOT / "APPENDIX.html").as_uri()],
               check=True, capture_output=True)
print("APPENDIX.pdf:", (ROOT / "APPENDIX.pdf").stat().st_size // 1024, "KB")
