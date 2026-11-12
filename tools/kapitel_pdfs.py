#!/usr/bin/env python3
"""Split the built Skript or Folien PDF into one PDF per chapter.

Usage: kapitel_pdfs.py docu|slides outdir suffix

Reads the chapter start pages from <job>.toc (in both documents the printed
page number equals the physical page) and cuts <job>.pdf with mutool merge.
Chapters 0-13 become LE00_<suffix>.pdf ... LE13_<suffix>.pdf; the appendix
(only in the Skript) becomes Anhang_<suffix>.pdf, the bibliography
Literatur_<suffix>.pdf. Title page and table of contents are left out; they
are in the complete PDF.
"""
import re
import subprocess
import sys
from pathlib import Path

job, outdir, suffix = sys.argv[1], Path(sys.argv[2]), sys.argv[3]
toc = Path(f"{job}.toc").read_text(encoding="utf-8")
pdf = Path(f"{job}.pdf")

info = subprocess.run(["pdfinfo", pdf], capture_output=True, text=True, check=True).stdout
npages = int(re.search(r"Pages:\s+(\d+)", info).group(1))

# \contentsline {chapter}{\numberline {3}Titel}{36}{chapter.3}%
entries = []
for m in re.finditer(r"\\contentsline \{chapter\}\{(.*)\}\{(\d+)\}\{([^}]*)\}%", toc):
    title, page, anchor = m.groups()
    if anchor.startswith("chapter."):
        name = f"LE{int(anchor.split('.')[1]):02d}"
    elif anchor.startswith("appendix.") and "numberline" in title:
        name = "Anhang"
    elif title.endswith("Literatur"):
        name = "Literatur"
    else:
        sys.exit(f"{job}.toc: unbekannter Kapiteleintrag {m.group(0)}")
    entries.append((name, int(page)))

if not entries:
    sys.exit(f"{job}.toc: keine Kapitel gefunden")

outdir.mkdir(parents=True, exist_ok=True)
for i, (name, start) in enumerate(entries):
    end = entries[i + 1][1] - 1 if i + 1 < len(entries) else npages
    dst = outdir / f"{name}_{suffix}.pdf"
    subprocess.run(["mutool", "merge", "-o", dst, pdf, f"{start}-{end}"], check=True)
    print(f"{dst}: S. {start}-{end}")
