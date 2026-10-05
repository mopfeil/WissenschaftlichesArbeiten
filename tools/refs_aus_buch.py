#!/usr/bin/env python3
"""Baut refs.bib aus den Bibliographien des WuZ-Buchs.

Sammelt alle Zitierschluessel aus chapters/ und handouts/, holt die
zugehoerigen Eintraege (mit abstract-Feld) aus den .bib-Dateien des Buchs
und haengt refs_extra.bib (Quellen, die nur dieses Skript braucht) an.
Fehlende Schluessel werden gemeldet; das Skript endet dann mit Status 1.

Aufruf:  python3 tools/refs_aus_buch.py [Pfad zum Buchordner ClaudeOutput]
"""
import glob, os, re, sys

HIER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUCH = sys.argv[1] if len(sys.argv) > 1 else \
    "/home/shared/wuz/Wissenschaft_und_Zauberkunst/ClaudeOutput"

CITE = re.compile(r"\\(?:paren|text|foot|auto|full)?cites?\*?(?:\[[^\]]*\]){0,2}\{([^}]*)\}")

def schluessel_im_text():
    keys = set()
    for f in glob.glob(os.path.join(HIER, "chapters", "*.tex")) + \
             glob.glob(os.path.join(HIER, "handouts", "*.tex")):
        text = open(f, encoding="utf-8").read()
        text = re.sub(r"(?<!\\)%.*", "", text)
        for m in CITE.finditer(text):
            keys.update(k.strip() for k in m.group(1).split(",") if k.strip())
    return keys

def eintraege(pfad):
    """Zerlegt eine .bib-Datei in {schluessel: eintragstext} (Klammerzaehlung)."""
    text = open(pfad, encoding="utf-8").read()
    out, i = {}, 0
    while True:
        i = text.find("@", i)
        if i < 0:
            break
        m = re.match(r"@(\w+)\s*\{\s*([^,\s]+)\s*,", text[i:])
        if not m or m.group(1).lower() in ("comment", "string", "preamble"):
            i += 1
            continue
        tiefe, j = 0, i + text[i:].find("{")
        while j < len(text):
            if text[j] == "{":
                tiefe += 1
            elif text[j] == "}":
                tiefe -= 1
                if tiefe == 0:
                    break
            j += 1
        out.setdefault(m.group(2), text[i:j + 1])
        i = j + 1
    return out

def main():
    keys = schluessel_im_text()
    extra_pfad = os.path.join(HIER, "refs_extra.bib")
    extra = eintraege(extra_pfad) if os.path.exists(extra_pfad) else {}
    buch = {}
    for f in sorted(glob.glob(os.path.join(BUCH, "*.bib"))):
        for k, v in eintraege(f).items():
            buch.setdefault(k, v)
    teile, fehlend = [], []
    for k in sorted(keys):
        if k in extra:
            continue
        if k in buch:
            teile.append(buch[k])
        else:
            fehlend.append(k)
    kopf = ("% Automatisch erzeugt von tools/refs_aus_buch.py -- nicht von Hand aendern.\n"
            "% Eintraege aus dem WuZ-Buch; eigene Quellen gehoeren in refs_extra.bib.\n\n")
    with open(os.path.join(HIER, "refs.bib"), "w", encoding="utf-8") as fh:
        fh.write(kopf + "\n\n".join(teile) + "\n\n")
        fh.write("\n\n".join(extra.values()) + "\n")
    print(f"{len(teile)} Eintraege aus dem Buch, {len(extra)} aus refs_extra.bib")
    if fehlend:
        print("FEHLEND:", ", ".join(fehlend))
        sys.exit(1)

if __name__ == "__main__":
    main()
