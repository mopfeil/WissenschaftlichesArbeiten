# Wissenschaftliches Arbeiten (WuZ)

Vorlesungsmaterial zum Modul *Wissenschaftliches Arbeiten* in der Fassung
*Wissenschaft und Zauberkunst* (Prof. Dr. Markus Pfeil, RWU). Grundlage ist das
13-Wochen-Curriculum aus Kapitel 15 des Buches *Wissenschaft und Zauberkunst –
Wie wir uns ein besseres Bild von der Welt machen*. Jede Lehreinheit beginnt mit
einem Staunmoment (Zauberkunststück oder Selbstversuch), der das Methodenthema
der Woche vorwegnimmt.

| Ordner / Datei   | Inhalt                                                        |
|------------------|---------------------------------------------------------------|
| `pdf/`           | Skript, Folien und Handouts, fertig zum Lesen und Drucken     |
| `chapters/`      | Quelltext der Lehreinheiten (LE00 Modul, LE01–LE13, Anhang)   |
| `handouts/`      | Handout und Übungsblatt (Teil A/B) je Lehreinheit             |
| `fonts/`         | Barlow Semi Condensed, die RWU-Hausschrift (SIL OFL)          |
| `tools/`         | Hilfsskripte (Literaturliste aus dem Buch, Prüfskripte)       |

## Skript, Folien, Handouts

- [Skript (A4)](pdf/WuZ_WissArbeiten_Skript.pdf) – vollständige Fassung für Lehrende:
  Theorie, Folieninhalte, Vorbereitung jedes Kunststücks, Ablauf der
  Doppelstunde, Handouts, Übungsblätter mit Erwartungshorizont
- [Folien (A5 quer)](pdf/WuZ_WissArbeiten_Folien.pdf) – was in der Stunde gezeigt wird
- [Handouts und Übungsblätter (A4)](pdf/WuZ_WissArbeiten_Handouts.pdf) – Druckvorlage
  für die Studierenden, ohne Regie- und Lösungshinweise
- Getrennt zum Austeilen, je Lehreinheit eine PDF ([Übungsblätter](pdf/Uebungsblaetter/),
  [Zusammenfassungen](pdf/Zusammenfassungen/)):
  - Übungsblatt Teil A: zu Beginn der Stunde, verrät den Staunmoment nicht
  - Übungsblatt Teil B: nach dem Staunmoment (Reflexion, Hausaufgaben)
  - Zusammenfassung (Handout): am Ende der Stunde
  - Sammeldateien: [alle Teil A](pdf/WuZ_WissArbeiten_Uebungsblaetter_A.pdf),
    [alle Teil B](pdf/WuZ_WissArbeiten_Uebungsblaetter_B.pdf),
    [alle Zusammenfassungen](pdf/WuZ_WissArbeiten_Zusammenfassungen.pdf)

## Die 13 Lehreinheiten

| LE | Thema                              | Staunmoment                        | Kernbegriff                 |
|----|------------------------------------|------------------------------------|-----------------------------|
| 1  | Staunen als Erkenntnishaltung      | Ideomotor-Pendel                   | Prediction Error            |
| 2  | Die Forschungsfrage                | Das geheime Objekt                 | Operationalisierung         |
| 3  | Literaturrecherche                 | Kruskal Count                      | Suchstrategie               |
| 4  | Quellenkritik                      | Apophenie / Das letzte Abendmahl   | Apophenie / Bias            |
| 5  | Hypothesen und Falsifizierbarkeit  | Switchboard / Black Box            | Falsifikation               |
| 6  | Forschungsdesign                   | Kontrollierte Seilroutine          | Experimentelle Kontrolle    |
| 7  | Kognitive Verzerrungen             | Charpentier-Illusion               | Confirmation Bias           |
| 8  | Quantitative Methoden              | Chop Cup / Monty Hall              | Bedingte Wahrscheinlichkeit |
| 9  | Qualitative Methoden               | Das Patter                         | Intersubjektivität          |
| 10 | Datenanalyse und Interpretation    | Die unveränderliche Summe          | Determinismus               |
| 11 | Wissenschaftliches Schreiben       | Patter-Umbau in Fachsprache        | Präzision und Struktur      |
| 12 | Präsentation und Glaubwürdigkeit   | CRED-Strategien                    | Credibility Cues            |
| 13 | Wissenschaftsethik und Grenzarbeit | Boundary Work: Was verrät man?     | Forschungsethik             |

## Bauen

```
make            baut docu.pdf (Skript), slides.pdf (Folien), handouts.pdf
make script     nur das Skript
make slides     nur die Folien
make handouts   nur Handouts und Übungsblätter
make einzeln    Übungsblatt A, B und Zusammenfassung getrennt, je LE (make -j8 einzeln)
make publish    baut alles und kopiert die PDFs nach pdf/
make clean      entfernt LaTeX-Hilfsdateien
```

Benötigt TeX Live mit latexmk, lualatex und biber. `make PDFTEX=1` baut mit
pdflatex und Latin Modern statt der RWU-Schrift.

## Aufbau

```
docu.tex (Skript, A4)    slides.tex (Folien, A5 quer)    handouts.tex (A4)
        \                         |                         /
         +------------- preamble.tex ----------------------+   Pakete, RWU-Farben und -Schrift, biblatex
         +------------- mathmacros.tex (+ -sl für Folien) -+   \bi, \ite, \defn, \nsl, \os, ...
         +------------- wuzmacros.tex ---------------------+   Staunbox, Vorbereitung, Ablauf, Handout, ...
         |
      text.tex  ->  chapters/LE00_modul.tex, LE01 ... LE13, Anhang_Material
                          \-> handouts/LEnn.tex (am Kapitelende im Skript)
```

Skript und Folien stammen aus denselben Dateien (wie im Projekt Embedded Computing):

- `\nsl{...}`: nur im Skript
- `\os{...}`: nur auf den Folien (meist `\os{\newpage}` = Folienwechsel)
- Umgebungen `vorbereitung`, `ablauf`, `lehrhinweis`: nur im Skript
- `handout`, `uebungsblatt` (Teil A), `uebungsblattb` (Teil B): im Skript und in `handouts.tex`

## Literatur

`refs.bib` wird aus den Bibliographien des Begleitbuchs erzeugt und enthält
nur die zitierten Einträge (mit Abstract):

```
python3 tools/refs_aus_buch.py [Pfad zum Buchordner]
```

Quellen, die nicht im Buch stehen, gehören in `refs_extra.bib`.

## Hinweis zur Geheimhaltung

Methoden kommerzieller und klassischer Zauberkunststücke (Switchboard, Chop
Cup, Seilroutine, Becherroutinen) sind hier bewusst nicht beschrieben. Für sie
gilt die Anleitung des Herstellers bzw. die Standardliteratur. Beschrieben ist,
was das Begleitbuch selbst offenlegt.
