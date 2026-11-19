#!/usr/bin/env python3
"""Interaktive LE-6-Folien (Knöpfe für das VBA-Modul) in die volle PPTX einfügen.

Usage: pptx_live_einfuegen.py folien.pptx live.pptx slides.pdf

folien.pptx  die von pdf2pptx.py erzeugte Fassung (ein Bild je Seite), wird
             überschrieben
live.pptx    material/LE06/ZGS_Test_Bayes.pptx (16:9, 13,333 x 7,5 Zoll)
slides.pdf   die Folien-PDF, aus der folien.pptx entstand; darin werden die
             Einfügestellen über den Folientitel gesucht

Die Live-Folien werden auf die Breite des Foliensatzes skaliert (Positionen,
Größen, Schriftgrade, Linienstärken, Innenabstände) und vertikal zentriert.
Die Formnamen (btn..., zgsFeld, zgsBar01, ...) bleiben erhalten; danach in
PowerPoint StatistikLive.bas importieren, Einrichten ausführen und als .pptm
speichern (material/LE06/ANLEITUNG.md).
"""
import copy
import re
import subprocess
import sys

from pptx import Presentation

# (Folie im Live-Deck, Titel der Folie in slides.pdf, hinter der sie landet)
EINFUEGEN = [
    (6, "Weiterwürfeln am Rechner"),
    (23, "Der Posterior wandert mit jedem Wurf"),
    (31, "Wo ist mein Schlüssel?"),
    (34, "Welche Beobachtung trennt die Positionen?"),
]

A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
P = "{http://schemas.openxmlformats.org/presentationml/2006/main}"
R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"


def seitentitel(pdf):
    """Erste Textzeile jeder PDF-Seite (ohne Abschnittsnummer)."""
    text = subprocess.run(["pdftotext", "-layout", pdf, "-"], capture_output=True,
                          text=True, check=True).stdout
    titel = []
    for seite in text.split("\f"):
        zeilen = [z.strip() for z in seite.splitlines() if z.strip()]
        titel.append(" ".join(zeilen[:2]) if zeilen else "")
    return titel


def skaliere(el, k):
    """Alle Längen in einem Formbaum mit k skalieren."""
    for e in el.iter():
        tag = e.tag
        if tag == A + "off" or tag == A + "chOff":
            for att in ("x", "y"):
                if att in e.attrib:
                    e.set(att, str(round(int(e.get(att)) * k)))
        elif tag in (A + "ext", A + "chExt"):
            for att in ("cx", "cy"):
                if att in e.attrib:
                    e.set(att, str(round(int(e.get(att)) * k)))
        elif tag in (A + "rPr", A + "defRPr", A + "endParaRPr") and "sz" in e.attrib:
            e.set("sz", str(max(100, round(int(e.get("sz")) * k))))
        elif tag == A + "ln" and "w" in e.attrib:
            e.set("w", str(round(int(e.get("w")) * k)))
        elif tag == A + "bodyPr":
            for att in ("lIns", "tIns", "rIns", "bIns"):
                if att in e.attrib:
                    e.set(att, str(round(int(e.get(att)) * k)))
        elif tag == A + "spcPts":
            e.set("val", str(round(int(e.get("val")) * k)))
        elif tag == A + "gridCol":
            e.set("w", str(round(int(e.get("w")) * k)))
        elif tag == A + "tr":
            e.set("h", str(round(int(e.get("h")) * k)))
    return el


def main():
    ziel, live, pdf = sys.argv[1:4]
    prs = Presentation(ziel)
    quelle = Presentation(live)
    k = prs.slide_width / quelle.slide_width
    dy = round((prs.slide_height - quelle.slide_height * k) / 2)
    leer = prs.slide_layouts[6]
    titel = seitentitel(pdf)
    if len(titel) - 1 > len(prs.slides) or len(prs.slides) > len(titel):
        print(f"Warnung: {len(prs.slides)} Folien, {len(titel)} PDF-Seiten")

    # Einfügestellen bestimmen, bevor sich die Reihenfolge ändert
    stellen = []
    for nr, anker in EINFUEGEN:
        treffer = [i for i, t in enumerate(titel) if anker in t]
        if len(treffer) != 1:
            sys.exit(f"Titel '{anker}': {len(treffer)} Treffer in {pdf}")
        stellen.append((treffer[0], nr))

    ids = prs.slides._sldIdLst
    alte = list(ids)
    for seite, nr in sorted(stellen, reverse=True):
        src = quelle.slides[nr - 1]
        if any(r.reltype.endswith("/image") or r.reltype.endswith("/hyperlink")
               for r in src.part.rels.values()):
            sys.exit(f"Live-Folie {nr} hat Bilder oder Links; Kopieren nicht vorgesehen")
        neu = prs.slides.add_slide(leer)
        baum = neu.shapes._spTree
        for sh in list(baum)[2:]:
            baum.remove(sh)
        for sh in src.shapes:
            # Seitenzahl des Live-Decks weglassen
            if sh.has_text_frame and re.fullmatch(r"\d+", sh.text_frame.text.strip()):
                continue
            el = skaliere(copy.deepcopy(sh._element), k)
            # nur das äußere xfrm verschieben (Gruppenkinder liegen relativ)
            for xfrm in (el.find(f"{P}spPr/{A}xfrm"), el.find(f"{P}grpSpPr/{A}xfrm"),
                         el.find(f"{P}xfrm")):
                if xfrm is not None and xfrm.find(A + "off") is not None:
                    off = xfrm.find(A + "off")
                    off.set("y", str(int(off.get("y")) + dy))
            # Formen über die volle Folienhöhe (Seitenbalken) wieder voll strecken
            if sh.top == 0 and sh.height == quelle.slide_height:
                xfrm = el.find(f"{P}spPr/{A}xfrm")
                xfrm.find(A + "off").set("y", "0")
                xfrm.find(A + "ext").set("cy", str(prs.slide_height))
            baum.append(el)
        if src.has_notes_slide:
            neu.notes_slide.notes_text_frame.text = src.notes_slide.notes_text_frame.text
        # neue Folie hinter die Seite 'seite' (0-basiert) der ursprünglichen Reihenfolge
        sld = list(ids)[-1]
        ids.remove(sld)
        ids.insert(list(ids).index(alte[seite]) + 1, sld)
        print(f"Live-Folie {nr} hinter Folie {seite + 1} eingefügt")

    prs.save(ziel)
    print(f"{ziel}: {len(prs.slides)} Folien")


if __name__ == "__main__":
    main()
