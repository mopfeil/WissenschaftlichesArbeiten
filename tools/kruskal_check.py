#!/usr/bin/env python3
"""Prueft den Kruskal-Count-Text des Uebungsblatts zu LE 3.

Liest den Text aus handouts/LE03.tex zwischen den Kommentarzeilen
% KRUSKAL-TEXT-BEGINN und % KRUSKAL-TEXT-ENDE und spielt die Zaehlregel
fuer alle Startzahlen durch:

  * Woerter sind durch Leerraum getrennt; Satzzeichen, Ziffern und
    LaTeX-Befehle zaehlen nicht. Umlaute zaehlen als ein Buchstabe.
  * Startwort ist das n-te Wort (n = 1..10).
  * Vom aktuellen Wort geht man so viele Woerter weiter, wie es
    Buchstaben hat.
  * Wuerde der naechste Sprung hinter dem letzten Wort landen, ist das
    aktuelle Wort das Schlusswort.

Ausgabe: Schlusswort je Startzahl und die Stelle, ab der alle Wege
zusammenlaufen. Endet mit Status 1, wenn nicht alle Starts auf demselben
Wort ankommen.

Aufruf:  python3 tools/kruskal_check.py [Datei] [hoechste Startzahl]
"""
import os, re, sys

HIER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATEI = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HIER, "handouts", "LE03.tex")
NMAX = int(sys.argv[2]) if len(sys.argv) > 2 else 10


def text_lesen(pfad):
    roh = open(pfad, encoding="utf-8").read()
    m = re.search(r"^%\s*KRUSKAL-TEXT-BEGINN.*?$(.*?)^%\s*KRUSKAL-TEXT-ENDE",
                  roh, re.S | re.M)
    if not m:
        sys.exit("Kommentarmarken KRUSKAL-TEXT-BEGINN/-ENDE nicht gefunden")
    zeilen = [z for z in m.group(1).splitlines() if not z.lstrip().startswith("%")]
    return "\n".join(zeilen)


def woerter(text):
    text = re.sub(r"\\[A-Za-z]+\*?", " ", text)      # LaTeX-Befehle weg
    roh = [re.sub(r"[^A-Za-zÄÖÜäöüß]", "", w) for w in text.split()]
    return [w for w in roh if w]


def weg(ws, n):
    p, pfad = n - 1, [n - 1]
    while p + len(ws[p]) < len(ws):
        p += len(ws[p])
        pfad.append(p)
    return pfad


def main():
    ws = woerter(text_lesen(DATEI))
    print(f"{len(ws)} Wörter im Text")
    if "ß" in "".join(ws):
        print("Hinweis: Text enthält ß (zählt hier als ein Buchstabe).")
    wege = {n: weg(ws, n) for n in range(1, NMAX + 1)}
    enden = set()
    for n, w in wege.items():
        enden.add(w[-1])
        print(f"Start {n:2d}: Schlusswort Nr. {w[-1] + 1:3d} "
              f"\"{ws[w[-1]]}\" nach {len(w) - 1} Sprüngen")
    gemeinsam = set.intersection(*(set(w) for w in wege.values()))
    if len(enden) == 1:
        erstes = min(gemeinsam)
        print(f"OK: alle {NMAX} Starts enden auf \"{ws[enden.pop()]}\"; "
              f"alle Wege laufen spätestens bei Wort Nr. {erstes + 1} "
              f"(\"{ws[erstes]}\") zusammen.")
        return 0
    print("FEHLER: verschiedene Schlusswörter:",
          sorted({ws[e] for e in enden}))
    return 1


if __name__ == "__main__":
    sys.exit(main())
