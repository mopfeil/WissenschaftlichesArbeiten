#!/usr/bin/env python3
"""Baut den Live-Foliensatz material/LE06/ZGS_Test_Bayes.pptx (Ergaenzung zu LE 6).

Die Folien sind editierbar (Textfelder, keine Folienbilder). Drei Folien
enthalten benannte Formen fuer die VBA-Simulationen aus material/LE06/StatistikLive.bas
(Wuerfel-Labor, Muenze live, Schluesselsuche). Sprechernotizen erklaeren
jede Folie.

    python3 tools/le06_live_figuren.py            # zuerst die Grafiken
    <venv>/bin/python tools/le06_live_folien.py

Benoetigt python-pptx.
"""
import os

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.dml import MSO_LINE_DASH_STYLE
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Inches, Pt, Emu

HIER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG = os.path.join(HIER, "material", "LE06", "bilder")
ZIEL = os.path.join(HIER, "material", "LE06", "ZGS_Test_Bayes.pptx")

VIOLETT = RGBColor(0x66, 0x38, 0xB6)
VIOLETT_HELL = RGBColor(0xC9, 0xB8, 0xE8)
VIOLETT_BLASS = RGBColor(0xF1, 0xEC, 0xFA)
CYAN = RGBColor(0x00, 0x7F, 0x9A)
CYAN_BLASS = RGBColor(0xE3, 0xF5, 0xFE)
ROT = RGBColor(0xC0, 0x39, 0x2B)
ROT_BLASS = RGBColor(0xFB, 0xEA, 0xE7)
GRAU = RGBColor(0x73, 0x73, 0x73)
GRAU_HELL = RGBColor(0xD9, 0xD9, 0xD9)
TINTE = RGBColor(0x22, 0x22, 0x22)
WEISS = RGBColor(0xFF, 0xFF, 0xFF)
SCHRIFT = "Calibri"

prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)
LEER = prs.slide_layouts[6]
SW, SH = prs.slide_width, prs.slide_height
FUSS = "LE 6 Statistik · Zentraler Grenzwertsatz, Test und Bayes"
nummer = [0]


# ---------------------------------------------------------------------------
# Bausteine
# ---------------------------------------------------------------------------

def textfeld(folie, x, y, w, h, absaetze, groesse=20, farbe=TINTE, fett=False, ausrichtung=PP_ALIGN.LEFT,
             anker=MSO_ANCHOR.TOP, name=None):
    """absaetze: Liste aus str oder (str, dict) mit Optionen groesse/farbe/fett/kursiv/punkt/abstand."""
    tb = folie.shapes.add_textbox(x, y, w, h)
    if name:
        tb.name = name
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anker
    tf.margin_left = tf.margin_right = Inches(0.05)
    for i, a in enumerate(absaetze):
        text, opt = (a, {}) if isinstance(a, str) else a
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = opt.get("ausrichtung", ausrichtung)
        p.space_after = Pt(opt.get("abstand", 6))
        punkt = opt.get("punkt", False)
        if punkt:
            text = ("•  " if punkt is True else punkt) + text
        r = p.add_run()
        r.text = text
        f = r.font
        f.name = opt.get("schrift", SCHRIFT)
        f.size = Pt(opt.get("groesse", groesse))
        f.bold = opt.get("fett", fett)
        f.italic = opt.get("kursiv", False)
        f.color.rgb = opt.get("farbe", farbe)
    return tb


def kasten(folie, x, y, w, h, absaetze, fuellung=VIOLETT_BLASS, rand=VIOLETT, groesse=18, name=None,
           ausrichtung=PP_ALIGN.LEFT, anker=MSO_ANCHOR.MIDDLE, form=MSO_SHAPE.ROUNDED_RECTANGLE, farbe=TINTE):
    s = folie.shapes.add_shape(form, x, y, w, h)
    if name:
        s.name = name
    if form == MSO_SHAPE.ROUNDED_RECTANGLE:
        s.adjustments[0] = 0.08
    s.fill.solid()
    s.fill.fore_color.rgb = fuellung
    if rand is None:
        s.line.fill.background()
    else:
        s.line.color.rgb = rand
        s.line.width = Pt(1.25)
    s.shadow.inherit = False
    tf = s.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anker
    tf.margin_left = tf.margin_right = Inches(0.15)
    tf.margin_top = tf.margin_bottom = Inches(0.08)
    for i, a in enumerate(absaetze):
        text, opt = (a, {}) if isinstance(a, str) else a
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = opt.get("ausrichtung", ausrichtung)
        p.space_after = Pt(opt.get("abstand", 4))
        r = p.add_run()
        r.text = text
        r.font.name = SCHRIFT
        r.font.size = Pt(opt.get("groesse", groesse))
        r.font.bold = opt.get("fett", False)
        r.font.italic = opt.get("kursiv", False)
        r.font.color.rgb = opt.get("farbe", farbe)
    return s


def knopf(folie, x, y, w, h, text, name, fuellung=VIOLETT, groesse=15):
    s = kasten(folie, x, y, w, h, [(text, {"fett": True, "farbe": WEISS, "groesse": groesse})], fuellung=fuellung,
               rand=None, name=name, ausrichtung=PP_ALIGN.CENTER)
    s.adjustments[0] = 0.25
    return s


def bild(folie, datei, x, y, w=None, h=None):
    return folie.shapes.add_picture(os.path.join(FIG, datei), x, y, w, h)


def bild_einpassen(folie, datei, x, y, w, h):
    """Bild proportional in den Rahmen (x, y, w, h) einpassen, zentriert."""
    from PIL import Image
    with Image.open(os.path.join(FIG, datei)) as im:
        bw, bh = im.size
    s = min(w / bw, h / bh)
    nw, nh = int(bw * s), int(bh * s)
    return bild(folie, datei, x + (w - nw) // 2, y + (h - nh) // 2, nw, nh)


def notizen(folie, text):
    folie.notes_slide.notes_text_frame.text = text.strip()


def neue_folie(titel, untertitel=None, teil=None):
    nummer[0] += 1
    f = prs.slides.add_slide(LEER)
    leiste = f.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(0.18), SH)
    leiste.fill.solid()
    leiste.fill.fore_color.rgb = VIOLETT
    leiste.line.fill.background()
    if teil:
        textfeld(f, Inches(0.55), Inches(0.22), Inches(8), Inches(0.35), [teil], groesse=13, farbe=CYAN, fett=True)
    textfeld(f, Inches(0.55), Inches(0.48), Inches(12.3), Inches(0.8), [titel], groesse=32, farbe=VIOLETT,
             fett=True)
    if untertitel:
        textfeld(f, Inches(0.55), Inches(1.18), Inches(12.3), Inches(0.5), [untertitel], groesse=18, farbe=GRAU)
    linie = f.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(0.55), Inches(7.05), Inches(12.8), Inches(7.05))
    linie.line.color.rgb = GRAU_HELL
    textfeld(f, Inches(0.55), Inches(7.07), Inches(9), Inches(0.35), [FUSS], groesse=11, farbe=GRAU)
    textfeld(f, Inches(11.8), Inches(7.07), Inches(1), Inches(0.35), [str(nummer[0])], groesse=11, farbe=GRAU,
             ausrichtung=PP_ALIGN.RIGHT)
    return f


def abschnitt(nr, titel, text):
    nummer[0] += 1
    f = prs.slides.add_slide(LEER)
    hg = f.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, SW, SH)
    hg.fill.solid()
    hg.fill.fore_color.rgb = VIOLETT
    hg.line.fill.background()
    textfeld(f, Inches(1), Inches(2.2), Inches(11), Inches(0.8), [nr], groesse=24, farbe=VIOLETT_HELL, fett=True)
    textfeld(f, Inches(1), Inches(2.9), Inches(11.3), Inches(1.4), [titel], groesse=44, farbe=WEISS, fett=True)
    textfeld(f, Inches(1), Inches(4.4), Inches(11), Inches(1.5), [text], groesse=22, farbe=WEISS)
    return f


def punkte(folie, x, y, w, h, zeilen, groesse=20):
    absaetze = []
    for z in zeilen:
        if isinstance(z, tuple):
            absaetze.append((z[0], dict({"punkt": True, "abstand": 10}, **z[1])))
        else:
            absaetze.append((z, {"punkt": True, "abstand": 10}))
    return textfeld(folie, x, y, w, h, absaetze, groesse=groesse)


LINKS = Inches(0.55)
OBEN = Inches(1.75)
BREIT = Inches(12.25)
HOCH = Inches(5.15)

# ---------------------------------------------------------------------------
# Titel und Fahrplan
# ---------------------------------------------------------------------------
nummer[0] += 1
f = prs.slides.add_slide(LEER)
hg = f.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, SW, SH)
hg.fill.solid()
hg.fill.fore_color.rgb = VIOLETT
hg.line.fill.background()
textfeld(f, Inches(1), Inches(1.9), Inches(11.3), Inches(1.0), ["Statistik"], groesse=24, farbe=VIOLETT_HELL,
         fett=True)
textfeld(f, Inches(1), Inches(2.5), Inches(11.3), Inches(2.0),
         ["Vom Würfel zum Test –", "und zurück mit Bayes"], groesse=48, farbe=WEISS, fett=True)
textfeld(f, Inches(1), Inches(4.4), Inches(11.3), Inches(1.2),
         ["Zentraler Grenzwertsatz · Standardfehler · t-Test · Satz von Bayes · Bayes im Alltag"],
         groesse=22, farbe=WEISS)
textfeld(f, Inches(1), Inches(6.2), Inches(11.3), Inches(0.5), ["Prof. Dr. Markus Pfeil"], groesse=18,
         farbe=VIOLETT_HELL)
notizen(f, """
Ziel der Einheit: Die Studierenden sehen an Würfel und Münze, warum Mittelwerte normalverteilt sind,
lesen daraus den Standardfehler ab und bauen daraus selbst einen Test. Danach dieselben Daten mit Bayes:
Was ändert sich an der Aussage? Zum Schluss Bayes ohne Messwerte (Schlüssel, Quellen).
Ergänzt LE 6 (Skript und Folien) um Live-Simulationen. Interaktiv: drei Live-Folien (VBA, siehe material/LE06/ANLEITUNG.md) und das Colab-Notebook ZGS_Test_Bayes.ipynb.
""")

f = neue_folie("Fahrplan")
kasten(f, LINKS, OBEN, Inches(3.9), Inches(3.0), [
    ("A  Vom Zufall zum Test", {"fett": True, "farbe": VIOLETT, "groesse": 22}),
    ("Der gezinkte Würfel", {"groesse": 18}),
    ("Zentraler Grenzwertsatz", {"groesse": 18}),
    ("Standardfehler ablesen", {"groesse": 18}),
    ("z- und t-Test, Münze", {"groesse": 18}),
], anker=MSO_ANCHOR.TOP)
kasten(f, Inches(4.7), OBEN, Inches(3.9), Inches(3.0), [
    ("B  Praxis: Abfüllanlage", {"fett": True, "farbe": CYAN, "groesse": 22}),
    ("Stichprobe aus der Linie", {"groesse": 18}),
    ("t-Test Schritt für Schritt", {"groesse": 18}),
    ("Eichrecht: α = 0,5 %", {"groesse": 18}),
    ("Was der p-Wert wirklich sagt", {"groesse": 18}),
], fuellung=CYAN_BLASS, rand=CYAN, anker=MSO_ANCHOR.TOP)
kasten(f, Inches(8.85), OBEN, Inches(3.95), Inches(3.0), [
    ("C  Bayes", {"fett": True, "farbe": VIOLETT, "groesse": 22}),
    ("Der Satz als Flächenbild", {"groesse": 18}),
    ("Münze und Würfel", {"groesse": 18}),
    ("Mittelwert der Anlage", {"groesse": 18}),
    ("Schlüssel suchen, Quellen prüfen", {"groesse": 18}),
], anker=MSO_ANCHOR.TOP)
notizen(f, """
Roter Faden: dieselbe Frage zweimal stellen.
Frequentistisch: Wie überraschend wären meine Daten, wenn die Hypothese stimmt?
Bayesianisch: Wie plausibel ist die Hypothese, nachdem ich die Daten gesehen habe?
""")

# ---------------------------------------------------------------------------
# Teil A
# ---------------------------------------------------------------------------
abschnitt("Teil A", "Vom Zufall zum Test", "Ein gezinkter Würfel, viele Mittelwerte und eine Glockenkurve")

T_A = "A  Vom Zufall zum Test"
f = neue_folie("Ein gezinkter Würfel", "Bei diesem Würfel kommt die Sechs in 25 % statt in 16,7 % der Würfe.", T_A)
bild_einpassen(f, "f01_wuerfel.png", LINKS, OBEN, Inches(7.6), Inches(4.6))
punkte(f, Inches(8.4), OBEN + Inches(0.2), Inches(4.4), Inches(4.5), [
    "Ein einzelner Wurf verrät fast nichts: Eine Sechs kommt bei beiden Würfeln oft vor.",
    "Der Mittelwert vieler Würfe verschiebt sich nur von 3,5 auf 3,75.",
    ("Wie viele Würfe brauchen wir, um 0,25 Augen Unterschied sicher zu sehen?", {"fett": True,
                                                                               "farbe": VIOLETT}),
], groesse=19)
notizen(f, """
Einstieg mit echtem Würfel (oder Münze) im Hörsaal: Lassen Sie drei Studierende je 10-mal würfeln
und den Mittelwert an die Tafel schreiben. Die Mittelwerte streuen deutlich, obwohl der Würfel derselbe ist.
Zahlen: fair μ = 3,5, σ = √(35/12) = 1,71. Gezinkt: P(6) = 0,25, P(1..5) = 0,15 → μ = 3,75, σ = 1,79.
Leitfrage: Ab wann ist ein höherer Mittelwert ein Indiz und kein Zufall?
""")

f = neue_folie("Der Zentrale Grenzwertsatz", "Mittelwerte werden normalverteilt – egal wie schief die Einzelwerte sind.",
               T_A)
bild_einpassen(f, "f02_zgs.png", LINKS, OBEN, BREIT, Inches(3.6))
kasten(f, LINKS, Inches(5.55), BREIT, Inches(1.3), [
    ("x̄  ~  N( μ ;  σ / √n )       Form: Glocke   ·   Mitte: μ   ·   Breite: σ / √n  (der Standardfehler)",
     {"groesse": 22, "fett": True, "ausrichtung": PP_ALIGN.CENTER}),
])
notizen(f, """
Jedes Feld: 20 000 simulierte Stichproben. n = 1 ist die Verteilung des Würfels selbst (mit dem Sechser-Turm).
Bei n = 2 entsteht schon ein Dreieck, bei n = 5 eine Glocke, bei n = 30 eine schmale Glocke.
Wichtig: Die Kurve wird nicht nur glockenförmig, sie wird auch schmaler – um den Faktor 1/√n.
Das ist die Aussage Var(x̄) = σ²/n (Skript LE 6, Abschnitt „Von der Stichprobe zur Grundgesamtheit“).
Live zeigen: nächste Folie (VBA) oder im Notebook Abschnitt 1.
""")

f = neue_folie("Live: Würfel-Labor", "Klicken Sie im Vortragsmodus auf die Knöpfe. Jeder Klick zieht neue Stichproben.",
               T_A)
FX, FY, FW, FH = Inches(0.7), Inches(1.85), Inches(8.6), Inches(4.2)
feld = f.shapes.add_shape(MSO_SHAPE.RECTANGLE, FX, FY, FW, FH)
feld.name = "zgsFeld"
feld.fill.solid()
feld.fill.fore_color.rgb = RGBColor(0xFA, 0xFA, 0xFA)
feld.line.color.rgb = GRAU_HELL
NB = 26  # Mittelwerte 1,0 / 1,2 / ... / 6,0; Bereich 0,9 bis 6,1
bw = FW / NB
for i in range(NB):
    b = f.shapes.add_shape(MSO_SHAPE.RECTANGLE, int(FX + i * bw), FY + FH - Emu(1), int(bw), Emu(1))
    b.name = f"zgsBar{i + 1:02d}"
    b.fill.solid()
    b.fill.fore_color.rgb = VIOLETT_HELL
    b.line.color.rgb = WEISS
    b.line.width = Pt(0.5)
for k in range(1, 7):
    x = FX + int(FW * (k - 0.9) / 5.2)
    textfeld(f, x - Inches(0.25), FY + FH + Inches(0.02), Inches(0.5), Inches(0.35), [str(k)], groesse=14,
             farbe=GRAU, ausrichtung=PP_ALIGN.CENTER)
textfeld(f, FX, FY + FH + Inches(0.32), FW, Inches(0.35), ["Mittelwert x̄ der Stichprobe"], groesse=14,
         farbe=GRAU, ausrichtung=PP_ALIGN.CENTER)
kasten(f, Inches(9.6), Inches(1.85), Inches(3.2), Inches(2.05),
       [("Noch keine Stichprobe.", {"groesse": 15}),
        ("Vortragsmodus starten und auf „100 Stichproben“ klicken.", {"groesse": 13, "farbe": GRAU})],
       name="zgsInfo", anker=MSO_ANCHOR.TOP)
textfeld(f, Inches(9.6), Inches(4.0), Inches(3.2), Inches(0.3), ["Würfe pro Stichprobe"], groesse=13, farbe=GRAU)
knopf(f, Inches(9.6), Inches(4.3), Inches(0.98), Inches(0.45), "n = 1", "btnN1", CYAN)
knopf(f, Inches(10.71), Inches(4.3), Inches(0.98), Inches(0.45), "n = 5", "btnN5", CYAN)
knopf(f, Inches(11.82), Inches(4.3), Inches(0.98), Inches(0.45), "n = 30", "btnN30", CYAN)
textfeld(f, Inches(9.6), Inches(4.85), Inches(3.2), Inches(0.3), ["Würfel"], groesse=13, farbe=GRAU)
knopf(f, Inches(9.6), Inches(5.15), Inches(1.53), Inches(0.45), "fair", "btnFair", CYAN)
knopf(f, Inches(11.27), Inches(5.15), Inches(1.53), Inches(0.45), "gezinkt", "btnGezinkt", CYAN)
knopf(f, Inches(9.6), Inches(5.8), Inches(1.53), Inches(0.5), "1 Stichprobe", "btnZiehe1", groesse=12)
knopf(f, Inches(11.27), Inches(5.8), Inches(1.53), Inches(0.5), "100 Stichproben", "btnZiehe100", groesse=12)
knopf(f, Inches(9.6), Inches(6.42), Inches(3.2), Inches(0.42), "Zurücksetzen", "btnZgsReset", GRAU)
notizen(f, """
VBA-Folie (Makros aus material/LE06/StatistikLive.bas, Anleitung in material/LE06/ANLEITUNG.md).
Ablauf im Hörsaal:
1. n = 1, fair, 100 Stichproben: flache Verteilung von 1 bis 6.
2. Zurücksetzen, n = 5: Glocke entsteht. Die cyanfarbene Kurve ist N(μ; σ/√n) aus dem ZGS.
3. n = 30: schmale Glocke, empirische Streuung der Mittelwerte ≈ theoretischer SE = 1,71/√30 = 0,31.
4. Auf „gezinkt“ umschalten: Die Glocke rückt nach 3,75. Bei n = 30 überlappen fair und gezinkt noch stark –
   deshalb braucht man viele Würfe.
Der Infokasten zeigt Anzahl Stichproben, Mittelwert der Mittelwerte, deren Standardabweichung (= empirischer SE)
und den theoretischen SE.
Ohne Makros: Notebook Abschnitt 1 (Schieberegler für n und Würfeltyp).
""")

f = neue_folie("Den Standardfehler ablesen", "Die Breite der Glocke ist der Standardfehler des Mittelwerts.", T_A)
bild_einpassen(f, "f03_se_ablesen.png", LINKS, OBEN, Inches(7.8), Inches(5.1))
punkte(f, Inches(8.6), OBEN + Inches(0.1), Inches(4.2), Inches(5), [
    "Vom Gipfel bis zum Wendepunkt der Kurve: genau 1 SE.",
    "± 1 SE um μ: 68 % aller Mittelwerte.",
    "± 2 SE um μ: 95 % aller Mittelwerte.",
    ("SE = σ / √n", {"fett": True, "farbe": VIOLETT, "groesse": 24}),
    "Ist σ unbekannt, schätzen wir es mit s aus der Stichprobe: SE ≈ s / √n.",
], groesse=19)
notizen(f, """
Der Standardfehler ist die Standardabweichung der Mittelwerte – nicht die der Einzelwerte.
Ablesen an der Kurve: Der Wendepunkt (wo die Kurve von „nach unten gekrümmt“ zu „nach oben gekrümmt“ wechselt)
liegt genau eine Standardabweichung vom Gipfel entfernt. Bei 30 Würfen eines fairen Würfels: 1,71/√30 = 0,31.
Faustregel 68/95: 95 % aller 30er-Mittelwerte liegen zwischen 2,88 und 4,12.
Frage ans Publikum: Ein Mittelwert von 3,75 nach 30 Würfen – ist das auffällig? (Nein, unter 1 SE.)
""")

f = neue_folie("Das √n-Gesetz", "Genauigkeit wird teuer: Für den halben Fehler braucht man vier Mal so viele Daten.",
               T_A)
bild_einpassen(f, "f04_wurzel_n.png", LINKS, OBEN, Inches(7.2), Inches(5.0))
kasten(f, Inches(8.2), OBEN + Inches(0.3), Inches(4.6), Inches(3.6), [
    ("Wie viele Würfe für den gezinkten Würfel?", {"fett": True, "farbe": VIOLETT}),
    ("Unterschied der Mittelwerte: 0,25", {"groesse": 17}),
    ("Damit er 2 SE groß ist, muss gelten", {"groesse": 17}),
    ("SE = 1,71 / √n ≤ 0,125", {"groesse": 19, "fett": True}),
    ("→ n ≥ (1,71 / 0,125)² ≈ 187 Würfe", {"groesse": 19, "fett": True, "farbe": VIOLETT}),
], anker=MSO_ANCHOR.TOP)
notizen(f, """
Rechnung: 2·SE ≤ 0,25 ⇒ SE ≤ 0,125 ⇒ √n ≥ 1,71/0,125 = 13,7 ⇒ n ≥ 187.
Das ist eine grobe Fallzahlplanung: Mit ca. 190 Würfen liegt der gezinkte Mittelwert im Schnitt 2 SE über 3,5.
(Für eine Power von 80 % bräuchte man mehr: (1,96+0,84)²·σ²/0,25² ≈ 366 Würfe.)
Übertrag: Jede Umfrage, jede Messreihe folgt diesem Gesetz.
""")

f = neue_folie("Vom Standardfehler zum Test", "60 Würfe, Mittelwert 3,95. Ist dieser Würfel fair?", T_A)
bild_einpassen(f, "f05_test_wuerfel.png", LINKS, OBEN, Inches(7.6), Inches(5.0))
textfeld(f, Inches(8.4), OBEN, Inches(4.4), Inches(5.2), [
    ("1  Gegenwelt annehmen", {"fett": True, "farbe": VIOLETT}),
    ("H₀: Der Würfel ist fair, μ₀ = 3,5", {"groesse": 17, "abstand": 10}),
    ("2  Breite dieser Welt", {"fett": True, "farbe": VIOLETT}),
    ("SE = 1,71 / √60 = 0,22", {"groesse": 17, "abstand": 10}),
    ("3  Abstand in Standardfehlern", {"fett": True, "farbe": VIOLETT}),
    ("z = (3,95 − 3,5) / 0,22 = 2,04", {"groesse": 17, "abstand": 10}),
    ("4  Fläche jenseits des Abstands", {"fett": True, "farbe": VIOLETT}),
    ("p = 0,041  (zweiseitig)", {"groesse": 17, "abstand": 10}),
    ("p < 0,05 → H₀ verwerfen: „signifikant“", {"groesse": 17, "fett": True, "farbe": ROT}),
], groesse=19)
notizen(f, """
Das ist der ganze Test in vier Schritten – mehr steckt im z-Test nicht.
Der Testwert z ist nichts anderes als der Abstand vom Sollwert, gemessen in Standardfehlern.
p ist die Fläche unter der H₀-Kurve, die mindestens so weit weg liegt wie unsere Beobachtung (beidseitig,
weil auch ein zu kleiner Mittelwert verdächtig wäre).
Hier ist σ = 1,71 bekannt (Würfelmodell), deshalb Normalverteilung (z-Test).
""")

f = neue_folie("Wenn σ unbekannt ist: der t-Test", "In der Praxis kennen wir nur die Stichprobe – und schätzen σ durch s.",
               T_A)
bild_einpassen(f, "f06_t_vs_z.png", LINKS, OBEN, Inches(7.0), Inches(4.6))
kasten(f, Inches(7.9), OBEN + Inches(0.1), Inches(4.9), Inches(1.4), [
    ("t = (x̄ − μ₀) / (s / √n)", {"groesse": 28, "fett": True, "ausrichtung": PP_ALIGN.CENTER}),
    ("Freiheitsgrade: df = n − 1", {"groesse": 18, "ausrichtung": PP_ALIGN.CENTER}),
])
punkte(f, Inches(7.9), OBEN + Inches(1.8), Inches(4.9), Inches(3.2), [
    "Gleiche Logik wie beim z-Test: Abstand in Standardfehlern.",
    "s schwankt selbst von Stichprobe zu Stichprobe → dickere Ränder.",
    "Ab n ≈ 30 sind t- und Normalverteilung kaum zu unterscheiden.",
], groesse=19)
notizen(f, """
Formal ist t = Z / √(χ²/df); hier genügt die Intuition:
Teilt man durch ein zufällig zu kleines s, wird t zu groß. Deshalb sind extreme t-Werte häufiger als extreme z-Werte.
Für den Test ändert sich nur die Tabelle bzw. die Python-Funktion (stats.t statt stats.norm).
""")

f = neue_folie("Dasselbe mit einer Münze", "100 Würfe, 61-mal Kopf. Ist die Münze fair?", T_A)
bild_einpassen(f, "f07_muenze_test.png", LINKS, OBEN, Inches(7.6), Inches(5.0))
textfeld(f, Inches(8.4), OBEN, Inches(4.4), Inches(5.2), [
    ("Ein Wurf: Kopf = 1, Zahl = 0", {"fett": True, "farbe": VIOLETT}),
    ("fair: μ = 0,5;  σ = √(0,5 · 0,5) = 0,5", {"groesse": 17, "abstand": 12}),
    ("Anteil Kopf in 100 Würfen", {"fett": True, "farbe": VIOLETT}),
    ("SE = 0,5 / √100 = 0,05  (= 5 Köpfe)", {"groesse": 17, "abstand": 12}),
    ("Abstand", {"fett": True, "farbe": VIOLETT}),
    ("z = (0,61 − 0,50) / 0,05 = 2,2", {"groesse": 17}),
    ("p = 0,028 (Normal-Näherung)", {"groesse": 17}),
    ("p = 0,035 (exakt, Binomialtest)", {"groesse": 17, "abstand": 12}),
], groesse=19)
notizen(f, """
Die Münze zeigt: Auch ein Anteil ist ein Mittelwert (von Nullen und Einsen). Der ZGS gilt also auch hier.
Die Balken sind die exakte Binomialverteilung, die Kurve die Normal-Näherung. Der kleine Unterschied im p-Wert
(0,028 vs. 0,035) kommt von der Diskretheit. In Python: stats.binomtest(61, 100, 0.5).
Diese Münze kommt in Teil C wieder: Dort fragen wir, wie wahrscheinlich sie gezinkt ist.
""")

# ---------------------------------------------------------------------------
# Teil B: Abfüllanlage
# ---------------------------------------------------------------------------
abschnitt("Teil B", "Praxis: die Abfüllanlage", "Füllt die Linie zu wenig Mehl in die 500-g-Packungen?")
T_B = "B  Praxis: Abfüllanlage"

f = neue_folie("Die Stichprobe aus der Linie", "Qualitätskontrolle zieht 20 Packungen und wiegt sie nach.", T_B)
bild_einpassen(f, "f08_abfuell_daten.png", LINKS, OBEN, Inches(8.0), Inches(3.4))
punkte(f, LINKS, Inches(5.25), Inches(8.0), Inches(1.7), [
    "Daten: material/LE06/abfuellung.csv (simulierter, realistischer Datensatz)",
    "x̄ = 497,8 g,  s = 4,6 g,  n = 20",
], groesse=18)
kasten(f, Inches(8.85), OBEN, Inches(3.95), Inches(5.0), [
    ("Was das Gesetz verlangt", {"fett": True, "farbe": CYAN, "groesse": 20}),
    ("Fertigpackungsverordnung (FPackV, Anlage 3):", {"groesse": 15}),
    ("Der Mittelwert eines Loses darf die Nennfüllmenge nicht unterschreiten.", {"groesse": 15}),
    ("Geprüft wird mit einer Stichprobe:", {"groesse": 15}),
    ("x̄ ≥ 500 g − k · s", {"groesse": 19, "fett": True}),
    ("n = 20  →  k = 0,640", {"groesse": 15}),
    ("k ist das 99,5-%-Quantil der t-Verteilung geteilt durch √n: 2,861 / √20 = 0,640.",
     {"groesse": 14, "farbe": GRAU}),
], fuellung=CYAN_BLASS, rand=CYAN, anker=MSO_ANCHOR.TOP)
notizen(f, """
Realer Hintergrund: Fertigpackungsverordnung, Anlage 3 (Prüfung des Mittelwerts). Die Tabelle dort nennt
für die zerstörende Prüfung n = 20 und k = 0,640, für n = 50 den Faktor k = 0,379.
Diese Faktoren sind nichts anderes als t(0,995; n−1)/√n – das Eichrecht schreibt also einen einseitigen t-Test
mit α = 0,5 % vor. (Bitte vor der Vorlesung die aktuelle Fassung unter gesetze-im-internet.de/fpackv/anlage_3.html
gegenprüfen; die Losgrößenklassen unterscheiden sich zwischen Fassungen.)
Die Daten sind simuliert, aber in Größenordnung typisch: σ ≈ 4–5 g bei 500-g-Schüttgut.
""")

f = neue_folie("Der t-Test Schritt für Schritt", "H₀: μ = 500 g (Anlage in Ordnung)   ·   H₁: μ < 500 g (füllt zu wenig)",
               T_B)
schritte = [
    ("1", "Standardfehler", "SE = s / √n = 4,6 / √20 = 1,03 g"),
    ("2", "Abstand vom Soll", "x̄ − μ₀ = 497,8 − 500 = −2,2 g"),
    ("3", "in Standardfehlern", "t = −2,2 / 1,03 = −2,14   (df = 19)"),
    ("4", "Fläche links davon", "p = P(T ≤ −2,14) = 0,023  (einseitig)"),
    ("5", "Entscheidung", "α = 5 %: verwerfen.   α = 0,5 % (Eichrecht): nicht verwerfen."),
]
for i, (nr, was, rechnung) in enumerate(schritte):
    y = OBEN + Inches(0.05 + i * 1.0)
    kasten(f, LINKS, y, Inches(0.75), Inches(0.8), [(nr, {"fett": True, "farbe": WEISS, "groesse": 26,
                                                         "ausrichtung": PP_ALIGN.CENTER})],
           fuellung=VIOLETT if i < 4 else CYAN, rand=None)
    textfeld(f, Inches(1.5), y + Inches(0.12), Inches(3.4), Inches(0.6), [was], groesse=22, fett=True,
             farbe=VIOLETT if i < 4 else CYAN)
    textfeld(f, Inches(4.9), y + Inches(0.12), Inches(7.9), Inches(0.6), [rechnung], groesse=22)
notizen(f, """
Einseitig, weil nur Unterfüllung den Kunden schadet (Überfüllung kostet nur den Hersteller).
Mit den Rohdaten aus der CSV liefert scipy: t = −2,142, p = 0,0227 (s = 4,59 nach Rundung der Einzelwerte).
Schritt 5 ist der Kern der Diskussion auf der nächsten Folie: Dieselben Daten, zwei Entscheidungen –
je nachdem, wie teuer ein Fehlalarm ist.
""")

f = neue_folie("Im Datenraum: Wo liegt unsere Stichprobe?", None, T_B)
bild_einpassen(f, "f09_abfuell_test.png", LINKS, Inches(1.4), Inches(7.9), Inches(5.5))
punkte(f, Inches(8.7), Inches(1.6), Inches(4.1), Inches(5.3), [
    "Grau: so streuen Mittelwerte von 20 Packungen, wenn die Anlage stimmt.",
    "Interne Qualitätssicherung (α = 5 %): Alarm ab 498,2 g → Anlage nachjustieren.",
    "Eichamt (α = 0,5 %): Beanstandung erst unter 497,1 g → keine Beanstandung.",
    ("α ist keine Naturkonstante, sondern eine Abwägung: Was kostet ein Fehlalarm, was ein übersehener Fehler?",
     {"fett": True, "farbe": VIOLETT}),
], groesse=18)
notizen(f, """
Die Grafik zeigt den Test in Gramm statt in t-Einheiten – so wie im Colab-Notebook „Datenraum“.
Das Eichamt schützt mit α = 0,5 % auch den Hersteller vor Fehlalarmen: Ein ehrlich arbeitender Abfüller
soll fast nie zu Unrecht beanstandet werden. Die interne QS will Abweichungen früh sehen und nimmt mehr
Fehlalarme in Kauf. Zugleich steigt mit kleinem α der Fehler 2. Art (eine wirklich zu niedrig füllende
Anlage wird übersehen).
""")

f = neue_folie("Die Rechnung in Python", "Notebook ZGS_Test_Bayes.ipynb, Abschnitt 3", T_B)
code = [
    "import pandas as pd",
    "from scipy import stats",
    "",
    "daten = pd.read_csv('abfuellung.csv')",
    "x = daten['gewicht_g']",
    "",
    "print(x.mean(), x.std(ddof=1))          # 497.8   4.59",
    "",
    "t, p = stats.ttest_1samp(x, popmean=500, alternative='less')",
    "print(f't = {t:.2f},  p = {p:.3f}')       # t = -2.14,  p = 0.023",
    "",
    "# Eichrecht: Grenze 500 - k*s mit k = t(0,995; 19)/sqrt(20)",
    "k = stats.t.ppf(0.995, df=19) / 20**0.5   # 0.640",
    "print(500 - k * x.std(ddof=1))             # 497.06",
]
kasten(f, LINKS, OBEN, BREIT, Inches(4.9), [(z if z else " ", {"groesse": 18, "abstand": 0}) for z in code],
       fuellung=RGBColor(0xF6, 0xF6, 0xF6), rand=GRAU_HELL, anker=MSO_ANCHOR.TOP)
for p in f.shapes[-1].text_frame.paragraphs:
    for r in p.runs:
        r.font.name = "Consolas"
notizen(f, """
Die CSV liegt in material/LE06/. Im Notebook wird sie direkt erzeugt, damit es in Colab ohne Upload läuft.
alternative='less' macht den Test einseitig (H₁: μ < 500).
""")

f = neue_folie("Was der p-Wert genau sagt", "Wir simulieren 10 000 Stichproben aus einer Anlage, die exakt 500 g abfüllt.",
               T_B)
bild_einpassen(f, "f10_welten.png", LINKS, OBEN, Inches(7.4), Inches(4.4))
kasten(f, Inches(8.2), OBEN, Inches(4.6), Inches(2.45), [
    ("Richtig", {"fett": True, "farbe": CYAN, "groesse": 20}),
    ("„Wenn die Anlage im Mittel genau 500 g abfüllt, liefern nur etwa 2 % aller Stichproben einen so kleinen "
     "oder noch kleineren Mittelwert.“", {"groesse": 17}),
], fuellung=CYAN_BLASS, rand=CYAN, anker=MSO_ANCHOR.TOP)
kasten(f, Inches(8.2), OBEN + Inches(2.6), Inches(4.6), Inches(2.0), [
    ("Falsch", {"fett": True, "farbe": ROT, "groesse": 20}),
    ("„Mit 97,7 % Wahrscheinlichkeit füllt die Anlage zu wenig ab.“", {"groesse": 17}),
    ("„Mit 2,3 % ist die Anlage in Ordnung.“", {"groesse": 17}),
], fuellung=ROT_BLASS, rand=ROT, anker=MSO_ANCHOR.TOP)
kasten(f, LINKS, Inches(6.25), BREIT, Inches(0.65), [
    ("p = P( Daten so extrem oder extremer  |  H₀ stimmt )   –   eine Aussage über die Daten, nicht über die Hypothese",
     {"fett": True, "groesse": 18, "ausrichtung": PP_ALIGN.CENTER}),
], rand=None)
notizen(f, """
Die Simulation macht die frequentistische Logik greifbar: Wir erfinden eine Welt, in der H₀ gilt, und schauen,
wie oft dort so etwas wie unsere Daten passiert. 219 von 10 000 simulierten Stichproben (2,2 %) sind mindestens so
extrem – das passt zum berechneten p = 2,3 % (Simulationsrauschen).
In dieser Logik ist die Hypothese fest und die Daten sind zufällig. Eine Wahrscheinlichkeit für die Hypothese
kommt darin gar nicht vor – deshalb ist der rote Kasten falsch.
Live im Notebook: Abschnitt 4 (Anzahl der Simulationen und wahren Mittelwert verstellen).
""")

f = neue_folie("Die Umkehrung ist nicht dasselbe", None, T_B)
kasten(f, Inches(0.9), Inches(1.7), Inches(5.6), Inches(2.0), [
    ("P( katholisch | Papst )", {"fett": True, "groesse": 28, "ausrichtung": PP_ALIGN.CENTER}),
    ("≈ 100 %", {"groesse": 28, "farbe": CYAN, "fett": True, "ausrichtung": PP_ALIGN.CENTER}),
], fuellung=CYAN_BLASS, rand=CYAN)
kasten(f, Inches(6.85), Inches(1.7), Inches(5.6), Inches(2.0), [
    ("P( Papst | katholisch )", {"fett": True, "groesse": 28, "ausrichtung": PP_ALIGN.CENTER}),
    ("≈ 1 zu 1,4 Milliarden", {"groesse": 28, "farbe": VIOLETT, "fett": True, "ausrichtung": PP_ALIGN.CENTER}),
])
kasten(f, Inches(0.9), Inches(4.1), Inches(5.6), Inches(1.6), [
    ("P( Daten | H₀ )", {"fett": True, "groesse": 26, "ausrichtung": PP_ALIGN.CENTER}),
    ("liefert der p-Wert", {"groesse": 20, "ausrichtung": PP_ALIGN.CENTER}),
], fuellung=CYAN_BLASS, rand=CYAN)
kasten(f, Inches(6.85), Inches(4.1), Inches(5.6), Inches(1.6), [
    ("P( H₀ | Daten )", {"fett": True, "groesse": 26, "ausrichtung": PP_ALIGN.CENTER}),
    ("wollen wir eigentlich wissen → Bayes", {"groesse": 20, "ausrichtung": PP_ALIGN.CENTER}),
])
textfeld(f, Inches(0.9), Inches(6.0), Inches(11.5), Inches(0.8), [
    "Um von links nach rechts zu kommen, fehlt eine Zutat: Wie plausibel war H₀ schon vorher?"],
    groesse=20, fett=True, farbe=VIOLETT, ausrichtung=PP_ALIGN.CENTER)
notizen(f, """
Klassisches Beispiel für die Verwechslung bedingter Wahrscheinlichkeiten („Prosecutor's Fallacy“).
Überleitung zu Bayes: Der Satz von Bayes ist genau die Rechenregel, die P(Daten | H) in P(H | Daten) umrechnet –
und dafür braucht er die Vorab-Plausibilität P(H), den Prior.
""")

# ---------------------------------------------------------------------------
# Teil C: Bayes
# ---------------------------------------------------------------------------
abschnitt("Teil C", "Dieselbe Frage mit Bayes", "Gegeben die Daten: Wie wahrscheinlich ist die Hypothese?")
T_C = "C  Bayes"

f = neue_folie("Der Satz von Bayes", None, T_C)
kasten(f, Inches(1.5), Inches(1.5), Inches(10.3), Inches(1.5), [
    ("P( H | D )  =  P( D | H ) · P( H )  /  P( D )", {"fett": True, "groesse": 36, "ausrichtung": PP_ALIGN.CENTER}),
])
teile = [("P(H | D)", "Posterior", "Glaube an H nach den Daten", VIOLETT),
         ("P(D | H)", "Likelihood", "Wie gut erklärt H die Daten?", CYAN),
         ("P(H)", "Prior", "Glaube an H vor den Daten", GRAU),
         ("P(D)", "Evidenz", "Summe über alle Hypothesen: Normierung", GRAU)]
for i, (formel, name, erkl, farbe) in enumerate(teile):
    x = Inches(0.9 + i * 2.95)
    kasten(f, x, Inches(3.3), Inches(2.75), Inches(1.75), [
        (formel, {"fett": True, "groesse": 22, "farbe": farbe, "ausrichtung": PP_ALIGN.CENTER}),
        (name, {"fett": True, "groesse": 18, "ausrichtung": PP_ALIGN.CENTER}),
        (erkl, {"groesse": 15, "ausrichtung": PP_ALIGN.CENTER}),
    ], fuellung=WEISS, rand=farbe)
kasten(f, Inches(1.5), Inches(5.35), Inches(10.3), Inches(1.4), [
    ("Für zwei Hypothesen als Chancen (Odds):", {"groesse": 17, "ausrichtung": PP_ALIGN.CENTER}),
    ("Posterior-Chance  =  Prior-Chance  ×  Bayes-Faktor P(D | H₁) / P(D | H₀)",
     {"fett": True, "groesse": 22, "ausrichtung": PP_ALIGN.CENTER}),
], fuellung=CYAN_BLASS, rand=CYAN)
notizen(f, """
Herleitung: P(H ∩ D) = P(D | H)·P(H) = P(H | D)·P(D).
Der p-Wert steckt in der Likelihood-Ecke: Er ist eine Aussage über P(D | H₀).
Die Odds-Form ist für Kopfrechnen ideal und kommt bei „Glaube ich dieser Quelle?“ wieder.
""")

f = neue_folie("Bayes als Flächenbild", "Eine Kiste mit fünf Münzen: vier faire, eine gezinkte (Kopf in 70 %). "
                                         "Wir ziehen eine, werfen – Kopf.", T_C)
bild_einpassen(f, "f11_bayes_flaeche.png", LINKS, OBEN, BREIT, Inches(4.4))
textfeld(f, LINKS, Inches(6.3), BREIT, Inches(0.6), [
    "Der Posterior ist der Anteil der gezinkten Fläche an allem, was mit der Beobachtung noch vereinbar ist."],
    groesse=19, fett=True, farbe=VIOLETT, ausrichtung=PP_ALIGN.CENTER)
notizen(f, """
Schritt 1: Die Breite der Spalten ist der Prior (20 % gezinkt, 80 % fair).
Schritt 2: In jeder Spalte färben wir den Anteil, der „Kopf“ liefert (Likelihood: 70 % bzw. 50 %).
Alle „Zahl“-Flächen fallen weg, weil wir Kopf gesehen haben.
Schritt 3: Was übrig bleibt, wird auf 100 % gestreckt (das ist die Division durch P(D)).
0,14 / (0,14 + 0,40) = 26 %. Ein Kopf macht die gezinkte Münze nur wenig plausibler.
Zum Mitmachen an der Tafel: Einheitsquadrat zeichnen, Studierende schätzen lassen.
""")

f = neue_folie("Wurf für Wurf: Der Posterior wird zum neuen Prior", None, T_C)
bild_einpassen(f, "f12_muenze_pfade.png", LINKS, Inches(1.45), Inches(7.6), Inches(5.4))
punkte(f, Inches(8.4), Inches(1.6), Inches(4.4), Inches(5.2), [
    "Kopf: Faktor 0,7 / 0,5 = 1,4 für „gezinkt“.",
    "Zahl: Faktor 0,3 / 0,5 = 0,6 für „gezinkt“.",
    "Nach jedem Wurf wird der Posterior zum neuen Prior.",
    "Einzelne Würfe schubsen hin und her, auf Dauer setzt sich die Wahrheit durch.",
    ("Bayes liefert nach jedem Wurf eine Antwort – kein festes n, kein Signifikanzniveau.",
     {"fett": True, "farbe": VIOLETT}),
], groesse=19)
notizen(f, """
Drei Simulationen mit gezinkter Münze (violett), drei mit fairer (cyan), jeweils Start beim Prior 20 %.
Die dicken Linien sind je ein Beispiel, die dünnen zeigen, wie unterschiedlich Pfade verlaufen.
Bayes-Faktor pro Wurf: 1,4 bzw. 0,6 – das ist die Odds-Form von der vorigen Folie.
Live: nächste Folie (VBA) oder Notebook Abschnitt 5.
""")

f = neue_folie("Live: Ist diese Münze gezinkt?", "Kopf/Zahl klicken (echte Münze im Hörsaal) oder zehn Würfe einer verdeckten Münze simulieren.",
               T_C)
BX, BY, BW, BH = Inches(0.7), Inches(1.85), Inches(8.0), Inches(3.9)
feld = f.shapes.add_shape(MSO_SHAPE.RECTANGLE, BX, BY, BW, BH)
feld.name = "bayFeld"
feld.fill.solid()
feld.fill.fore_color.rgb = RGBColor(0xFA, 0xFA, 0xFA)
feld.line.color.rgb = GRAU_HELL
NB2 = 50
bw = BW / NB2
for i in range(NB2):
    b = f.shapes.add_shape(MSO_SHAPE.RECTANGLE, int(BX + i * bw), BY + BH - Emu(1), int(bw), Emu(1))
    b.name = f"bayBar{i + 1:02d}"
    b.fill.solid()
    b.fill.fore_color.rgb = VIOLETT_HELL if i < 25 else VIOLETT
    b.line.color.rgb = WEISS
    b.line.width = Pt(0.5)
mitte = f.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, BX + BW // 2, BY, BX + BW // 2, BY + BH)
mitte.line.color.rgb = GRAU
mitte.line.dash_style = MSO_LINE_DASH_STYLE.DASH
for k, lab in enumerate(["0", "0,25", "0,5", "0,75", "1"]):
    textfeld(f, BX + int(BW * k / 4) - Inches(0.35), BY + BH + Inches(0.02), Inches(0.7), Inches(0.35), [lab],
             groesse=14, farbe=GRAU, ausrichtung=PP_ALIGN.CENTER)
textfeld(f, BX, BY + BH + Inches(0.32), BW, Inches(0.35),
         ["Kopf-Wahrscheinlichkeit p der Münze (Hypothese) – Höhe: wie plausibel nach den Daten"], groesse=14,
         farbe=GRAU, ausrichtung=PP_ALIGN.CENTER)
kasten(f, Inches(9.0), Inches(1.85), Inches(3.8), Inches(2.6),
       [("Noch keine Würfe.", {"groesse": 16}),
        ("Alle p von 0 bis 1 sind gleich plausibel.", {"groesse": 14, "farbe": GRAU})],
       name="bayInfo", anker=MSO_ANCHOR.TOP)
knopf(f, Inches(9.0), Inches(4.65), Inches(1.8), Inches(0.55), "Kopf", "btnKopf")
knopf(f, Inches(11.0), Inches(4.65), Inches(1.8), Inches(0.55), "Zahl", "btnZahl")
knopf(f, Inches(9.0), Inches(5.35), Inches(3.8), Inches(0.55), "10 Würfe der verdeckten Münze", "btnMuenze10", CYAN)
knopf(f, Inches(9.0), Inches(6.05), Inches(3.8), Inches(0.45), "Neue Münze / Zurücksetzen", "btnMuenzeReset", GRAU)
notizen(f, """
VBA-Folie. Gitter-Bayes über 50 Werte von p, flacher Prior.
Der Infokasten zeigt nebeneinander:
- frequentistisch: exakter zweiseitiger Binomialtest gegen p = 0,5 (p-Wert),
- bayesianisch: P(p > 0,5 | Daten) und das 95-%-Glaubwürdigkeitsintervall.
„Neue Münze“ wählt verdeckt zufällig eine faire (p = 0,5) oder gezinkte Münze (p = 0,7). Das Publikum tippt
nach einigen Klicks auf „10 Würfe“, welche es ist; die Auflösung steht erst nach 100 Würfen im Infokasten.
Gut zu zeigen: Bei wenigen Würfen ist die Kurve breit (viel Unsicherheit), sie wird mit jedem Wurf schmaler (√n!).
""")

f = neue_folie("Wie stark ist die Münze gezinkt?", "Statt „fair oder nicht“ schätzen wir die Kopf-Wahrscheinlichkeit p selbst.",
               T_C)
bild_einpassen(f, "f13_muenze_beta.png", LINKS, OBEN, BREIT, Inches(3.9))
kasten(f, LINKS, Inches(5.85), Inches(6.0), Inches(1.0), [
    ("Frequentistisch: p-Wert = 0,035", {"fett": True, "farbe": CYAN, "groesse": 18}),
    ("„61 Köpfe wären bei einer fairen Münze selten.“", {"groesse": 16}),
], fuellung=CYAN_BLASS, rand=CYAN)
kasten(f, Inches(6.8), Inches(5.85), Inches(6.0), Inches(1.0), [
    ("Bayesianisch: P(p > 0,5 | Daten) = 98,6 %", {"fett": True, "farbe": VIOLETT, "groesse": 18}),
    ("„Die Münze bevorzugt Kopf, vermutlich mit p zwischen 0,51 und 0,70.“", {"groesse": 16}),
])
notizen(f, """
Mathematik dahinter (optional): flacher Prior Beta(1, 1), nach k Köpfen in n Würfen Posterior Beta(k+1, n−k+1).
Hier Beta(62, 40). Das Gitterverfahren im Notebook (Abschnitt 5) liefert dieselbe Kurve.
Links: Nach 10 Würfen (6 Köpfe) ist fast alles noch möglich; nach 100 Würfen ist das Wissen scharf.
Rechts: Die Fläche rechts von 0,5 ist die Wahrscheinlichkeit, dass die Münze Kopf bevorzugt.
Merke: Die Breite des Posteriors schrumpft wie der Standardfehler mit 1/√n.
""")

f = neue_folie("Der Würfel: 16 Sechsen in 60 Würfen", "Erwartet: fair 10 Sechsen, gezinkt 15. Wie sicher ist „gezinkt“?",
               T_C)
bild_einpassen(f, "f14_wuerfel_bayes.png", LINKS, OBEN, BREIT, Inches(4.0))
kasten(f, LINKS, Inches(5.9), Inches(6.0), Inches(1.0), [
    ("Test: P(≥ 16 Sechsen | fair) = 0,034", {"fett": True, "farbe": CYAN, "groesse": 18}),
    ("„signifikant“ bei α = 5 %", {"groesse": 16}),
], fuellung=CYAN_BLASS, rand=CYAN)
kasten(f, Inches(6.8), Inches(5.9), Inches(6.0), Inches(1.0), [
    ("Bayes-Faktor 6,4 für „gezinkt“", {"fett": True, "farbe": VIOLETT, "groesse": 18}),
    ("Prior 50 % → 86 %.  Prior 5 % → nur 25 %.", {"groesse": 16}),
])
notizen(f, """
Bayes-Faktor: P(16 Sechsen | gezinkt) / P(16 Sechsen | fair) = 11,1 % / 1,7 % = 6,4.
Posterior-Chance = Prior-Chance × 6,4.
Prior 50 %: Chance 1:1 → 6,4:1 → 86 %. Prior 5 % (die meisten Würfel sind fair): 1:19 → 6,4:19 → 25 %.
Kernaussage: Ein „signifikantes“ Ergebnis kann trotzdem bedeuten, dass der Würfel wahrscheinlich fair ist –
wenn gezinkte Würfel selten sind. Das ist das Basisraten-Problem (vgl. „Positiv getestet – und jetzt?“ in LE 6).
""")

f = neue_folie("Bayes schätzt den Mittelwert der Abfüllanlage",
               "Dieselben 20 Packungen, Gitter-Bayes Packung für Packung (Notebook, Abschnitt 7)", T_C)
bild_einpassen(f, "f15_abfuell_bayes.png", LINKS, OBEN, BREIT, Inches(4.1))
punkte(f, LINKS, Inches(5.95), BREIT, Inches(1.0), [
    "Jede Packung verschiebt und schärft die Kurve: Hypothesen nahe den Messwerten gewinnen, ferne verlieren.",
    "Mit Vorwissen („die Anlage war auf 500 ± 1 g eingestellt“) rückt die Schätzung zum Soll – Daten und Erfahrung werden gewichtet.",
], groesse=16)
notizen(f, """
Links: 2001 Hypothesen für μ zwischen 490 und 510 g, flacher Prior, σ = 4,6 g als bekannt angenommen,
Update Packung für Packung (genau der Code aus dem Colab-Notebook, nur mit den Abfülldaten).
Rechts: Endergebnis mit flachem Prior (t-Verteilung um 497,8 g, Breite = SE):
P(μ < 500 | Daten) = 97,7 %, P(μ < 498 | Daten) ≈ 58 %.
Gestrichelt: informativer Prior N(500; 1 g) aus der Einrichtung der Anlage. Posterior: 498,9 ± 0,7 g,
P(μ < 500) ≈ 93 %. Die Daten ziehen die Schätzung vom Soll weg, aber das Vorwissen bremst.
Diskussion: Ist der Prior gerechtfertigt? Wer ihn wählt, muss ihn offenlegen – das ist die ehrliche Stelle von Bayes.
""")

f = neue_folie("Zwei Aussagen über dieselben Daten", None, T_C)
bild_einpassen(f, "f16_vergleich.png", LINKS, Inches(1.4), BREIT, Inches(3.9))
kasten(f, LINKS, Inches(5.4), Inches(6.0), Inches(1.5), [
    ("Frequentistisch", {"fett": True, "farbe": CYAN, "groesse": 19}),
    ("„Wäre die Anlage in Ordnung, kämen so niedrige Mittelwerte nur in 2,3 % der Stichproben vor.“",
     {"groesse": 16}),
], fuellung=CYAN_BLASS, rand=CYAN, anker=MSO_ANCHOR.TOP)
kasten(f, Inches(6.8), Inches(5.4), Inches(6.0), Inches(1.5), [
    ("Bayesianisch", {"fett": True, "farbe": VIOLETT, "groesse": 19}),
    ("„Gegeben die Daten (und einen flachen Prior) füllt die Anlage mit 97,7 % Wahrscheinlichkeit zu wenig ab.“",
     {"groesse": 16}),
], anker=MSO_ANCHOR.TOP)
notizen(f, """
Gleiche Kurvenform, gleiche Zahl (2,3 % + 97,7 % = 100 %) – aber die Achsen sind verschieden!
Links variieren die Daten bei festem μ = 500. Rechts variiert die Hypothese μ bei festen Daten.
Dass die Zahlen sich hier zu 100 % ergänzen, ist ein Sonderfall: einseitiger Test, Normalmodell, flacher Prior.
Mit Vorwissen (vorige Folie: 93 %) oder bei Punkthypothesen (Würfel: 25 % statt 97 %) fallen sie auseinander.
""")

f = neue_folie("Frequentistisch oder bayesianisch?", None, T_C)
zeilen = [
    ("", "Frequentistisch", "Bayesianisch"),
    ("Frage", "Wie überraschend sind die Daten, wenn H₀ stimmt?", "Wie plausibel ist H, nachdem ich die Daten kenne?"),
    ("Zufällig ist …", "die Stichprobe (Hypothese fest)", "unser Wissen über die Hypothese (Daten fest)"),
    ("Ergebnis", "p-Wert, Konfidenzintervall, Entscheidung", "Posterior, Glaubwürdigkeitsintervall, Bayes-Faktor"),
    ("Vorwissen", "fließt nicht formal ein", "als Prior – muss offengelegt werden"),
    ("Stärke", "objektive Regeln, Fehlerraten kontrolliert", "direkte Antwort, auch bei wenigen Daten und ohne Zahlen"),
    ("Abfüllanlage", "p = 0,023 → bei α = 5 % nachjustieren", "P(μ < 500 | D) = 97,7 %; P(μ < 498 | D) = 58 %"),
]
tab = f.shapes.add_table(len(zeilen), 3, LINKS, Inches(1.5), BREIT, Inches(5.2)).table
tab.columns[0].width = Inches(2.3)
tab.columns[1].width = Inches(4.975)
tab.columns[2].width = Inches(4.975)
for r, zeile in enumerate(zeilen):
    for c, txt in enumerate(zeile):
        zelle = tab.cell(r, c)
        zelle.text = txt or " "
        p = zelle.text_frame.paragraphs[0]
        p.runs[0].font.size = Pt(17 if r else 19)
        p.runs[0].font.name = SCHRIFT
        p.runs[0].font.bold = (r == 0 or c == 0)
        zelle.fill.solid()
        if r == 0:
            zelle.fill.fore_color.rgb = [VIOLETT, CYAN, VIOLETT][c]
            p.runs[0].font.color.rgb = WEISS
        else:
            zelle.fill.fore_color.rgb = [RGBColor(0xF2, 0xF2, 0xF2), CYAN_BLASS, VIOLETT_BLASS][c]
            p.runs[0].font.color.rgb = TINTE
notizen(f, """
Keine Glaubensfrage, sondern zwei Werkzeuge. In der Qualitätssicherung und in Zulassungsstudien dominieren
Tests mit festen Fehlerraten; bei Entscheidungen mit Vorwissen, kleinen Daten oder sequenziellen Daten
(A/B-Tests, Diagnose, Suche) ist Bayes oft natürlicher.
""")

# ---------------------------------------------------------------------------
# Teil D: Bayes ohne Messwerte
# ---------------------------------------------------------------------------
abschnitt("Teil D", "Bayes ohne Messwerte", "Wo ist mein Schlüssel? Glaube ich dieser Quelle?")
T_D = "D  Bayes im Alltag"

f = neue_folie("Wo ist mein Schlüssel?", "Keine Messwerte, aber Vorwissen und Beobachtungen – das reicht für Bayes.", T_D)
bild_einpassen(f, "f17_schluessel.png", LINKS, OBEN, BREIT, Inches(3.9))
punkte(f, LINKS, Inches(5.75), Inches(7.0), Inches(1.2), [
    "Prior: Gewohnheit (wo lag er sonst?).",
    "Likelihood: Wie sicher hätte ich ihn dort gefunden, wenn er da wäre?",
], groesse=17)
kasten(f, Inches(7.8), Inches(5.7), Inches(5.0), Inches(1.2), [
    ("„Nicht gefunden“ ist auch ein Befund.", {"fett": True, "farbe": VIOLETT, "groesse": 18}),
    ("Der Ort verliert, alle anderen gewinnen – im Verhältnis.", {"groesse": 15}),
])
notizen(f, """
Prior (Gewohnheit): Jackentasche 35 %, Schlüsselbrett 25 %, Schreibtisch 15 %, Auto 10 %, Küche 10 %, woanders 5 %.
Entdeckungswahrscheinlichkeit beim Nachschauen: Tasche 90 %, Brett 99 %, Schreibtisch 60 % (unordentlich!),
Auto 70 %, Küche 80 %, woanders 10 %.
Update nach erfolgloser Suche am Ort i: P(i) wird mit (1 − Entdeckung_i) multipliziert, dann alles normiert.
Jackentasche: 0,35·0,1 = 0,035 → nach Normierung 5 %. Das Brett springt auf 36 %.
Cyan: Wo lohnt sich das Suchen als Nächstes? Nicht einfach am wahrscheinlichsten Ort, sondern dort,
wo P(dort) × P(entdecke | dort) am größten ist. Nach zwei Fehlversuchen ist das der Schreibtisch,
obwohl Auto und Küche zusammen wahrscheinlicher sind.
Echte Anwendung: Bayessche Suchtheorie (Suche nach U-Booten, nach dem Wrack von Air France 447 im Jahr 2011).
""")

f = neue_folie("Live: Schlüsselsuche", "Der Schlüssel liegt verdeckt irgendwo (gezogen nach der Gewohnheit). Wo suchen Sie?",
               T_D)
KX, KY, KW, KH = Inches(0.7), Inches(1.95), Inches(8.6), Inches(3.4)
feld = f.shapes.add_shape(MSO_SHAPE.RECTANGLE, KX, KY, KW, KH)
feld.name = "keyFeld"
feld.fill.solid()
feld.fill.fore_color.rgb = RGBColor(0xFA, 0xFA, 0xFA)
feld.line.color.rgb = GRAU_HELL
ORTE = ["Jackentasche", "Schlüsselbrett", "Schreibtisch", "Auto", "Küche", "ganz woanders"]
PRIOR = [0.35, 0.25, 0.15, 0.10, 0.10, 0.05]
spalte = KW / 6
for i, (ort, pr) in enumerate(zip(ORTE, PRIOR)):
    x = int(KX + i * spalte)
    h = int(KH * 0.85 * pr / 0.4)
    b = f.shapes.add_shape(MSO_SHAPE.RECTANGLE, x + Inches(0.2), KY + KH - h, int(spalte) - Inches(0.4), h)
    b.name = f"keyBar{i + 1}"
    b.fill.solid()
    b.fill.fore_color.rgb = VIOLETT
    b.line.fill.background()
    textfeld(f, x, KY + KH - h - Inches(0.4), int(spalte), Inches(0.35), [f"{pr * 100:.0f} %"], groesse=15,
             fett=True, ausrichtung=PP_ALIGN.CENTER, name=f"keyPct{i + 1}")
    knopf(f, x + Inches(0.08), KY + KH + Inches(0.1), int(spalte) - Inches(0.16), Inches(0.62), ort, f"btnSuche{i + 1}",
          CYAN, groesse=12)
kasten(f, Inches(9.6), Inches(1.95), Inches(3.2), Inches(3.4),
       [("Noch nicht gesucht.", {"groesse": 16}),
        ("Klicken Sie unter einen Ort, um dort nachzusehen.", {"groesse": 14, "farbe": GRAU})],
       name="keyInfo", anker=MSO_ANCHOR.TOP)
knopf(f, Inches(9.6), Inches(5.45), Inches(3.2), Inches(0.62), "Neuer Fall / Zurücksetzen", "btnKeyReset", GRAU)
textfeld(f, KX, Inches(6.3), Inches(12), Inches(0.6), [
    "Chance, ihn beim Nachsehen zu entdecken: Tasche 90 %, Brett 99 %, Schreibtisch 60 %, Auto 70 %, Küche 80 %, "
    "woanders 10 %"], groesse=14, farbe=GRAU)
notizen(f, """
VBA-Folie. Ablauf: Publikum entscheidet, wo gesucht wird. Nach jedem Fehlversuch werden die Balken neu berechnet,
der Infokasten nennt den Ort mit dem höchsten „Suchwert“ (P × Entdeckungschance).
Findet man den Schlüssel, endet der Fall; „Neuer Fall“ versteckt ihn erneut zufällig gemäß Prior.
Diskussion: Warum kann es sinnvoll sein, die Jackentasche ein zweites Mal zu durchsuchen?
(Weil die Entdeckung dort nicht 100 % ist – nach einer Suche bleiben 5 %.)
""")

f = neue_folie("Glaube ich dieser Quelle?", "Behauptung: „Kaffee nach 16 Uhr verkürzt den Schlaf um eine Stunde.“", T_D)
textfeld(f, LINKS, OBEN, Inches(6.2), Inches(5.2), [
    ("1  Prior: Wie plausibel ist das vorher?", {"fett": True, "farbe": VIOLETT}),
    ("Bauchgefühl 30 %  →  Chance 30 : 70 = 3 : 7", {"groesse": 18, "abstand": 14}),
    ("2  Wie gut ist die Quelle?", {"fett": True, "farbe": VIOLETT}),
    ("P(Quelle behauptet es | stimmt) = 80 %", {"groesse": 18}),
    ("P(Quelle behauptet es | stimmt nicht) = 20 %", {"groesse": 18}),
    ("Bayes-Faktor = 80 / 20 = 4", {"groesse": 18, "fett": True, "abstand": 14}),
    ("3  Update", {"fett": True, "farbe": VIOLETT}),
    ("3 : 7  ×  4  =  12 : 7  →  12 / 19 = 63 %", {"groesse": 20, "fett": True}),
], groesse=20)
kasten(f, Inches(7.1), OBEN, Inches(5.7), Inches(3.3), [
    ("Was den Bayes-Faktor einer Quelle bestimmt", {"fett": True, "farbe": CYAN, "groesse": 19}),
    ("Behauptet sie oft Dinge, die sich als falsch herausstellen? (Nenner)", {"groesse": 16}),
    ("Hat sie Anreize, genau das zu sagen – egal ob es stimmt? (Nenner steigt)", {"groesse": 16}),
    ("Hat sie Zugang zu den Daten, prüft sie nach? (Zähler)", {"groesse": 16}),
    ("Eine Quelle, die immer dasselbe sagt, hat Bayes-Faktor 1: Sie bewegt nichts.",
     {"groesse": 16, "fett": True}),
], fuellung=CYAN_BLASS, rand=CYAN, anker=MSO_ANCHOR.TOP)
notizen(f, """
Das Beispiel ist bewusst aus dem Alltag gewählt; die Zahlen sind Einschätzungen, keine Messwerte.
Das ist der Punkt: Bayes zwingt dazu, die Einschätzungen explizit zu machen – und dann konsistent zu rechnen.
Der Bayes-Faktor misst, wie viel besser „Quelle sagt es“ unter „stimmt“ als unter „stimmt nicht“ erklärt wird.
Eine Quelle mit hoher Trefferquote, die aber fast alles behauptet, hat einen kleinen Bayes-Faktor.
Bezug zur Quellenkritik (SIFT, Lateral Reading): Man schätzt den Nenner, indem man prüft, was andere über die Quelle sagen.
""")

f = neue_folie("Mehrere Quellen: unabhängig oder abgeschrieben?", None, T_D)
bild_einpassen(f, "f18_quelle.png", LINKS, Inches(1.4), BREIT, Inches(4.2))
kasten(f, LINKS, Inches(5.8), BREIT, Inches(1.05), [
    ("Unabhängige Quellen: Bayes-Faktoren multiplizieren sich (4 × 4 = 16).   "
     "Abgeschrieben: die zweite Quelle bringt nichts (Faktor 1).", {"fett": True, "groesse": 18,
                                                                     "ausrichtung": PP_ALIGN.CENTER}),
])
notizen(f, """
Links: Wie weit eine Bestätigung den Glauben verschiebt, hängt vom Prior und vom Bayes-Faktor ab.
Eine Bestätigung durch eine schwache Quelle (BF 2) macht aus 30 % nur 46 %; eine replizierte Fachstudie (BF 20) macht 90 % daraus.
Rechts: Zwei unabhängige Quellen mit je BF 4: 3:7 × 16 = 48:7 → 87 %.
Hat Quelle B nur von A abgeschrieben, ist ihr Bayes-Faktor gegeben A gleich 1: Sie hätte es ohnehin gesagt.
Merksatz: Zehn Webseiten, die dieselbe Pressemitteilung zitieren, sind eine Quelle.
Die Bayes-Faktoren (2, 4, 20) sind Größenordnungen zur Illustration, keine empirischen Werte.
""")

f = neue_folie("Das Wichtigste", None)
punkte(f, LINKS, Inches(1.5), Inches(6.2), Inches(5.4), [
    "Mittelwerte sind normalverteilt (ZGS), ihre Breite ist der Standardfehler σ/√n.",
    "Ein Test misst den Abstand zur Nullhypothese in Standardfehlern.",
    "p = P(Daten so extrem | H₀) – nicht die Wahrscheinlichkeit der Hypothese.",
    "α ist eine Abwägung: Eichrecht 0,5 %, interne QS 5 %.",
], groesse=20)
punkte(f, Inches(6.9), Inches(1.5), Inches(5.9), Inches(5.4), [
    "Bayes: Posterior ist proportional zu Likelihood × Prior.",
    "Als Chancen: Posterior-Chance = Prior-Chance × Bayes-Faktor.",
    "Ein signifikanter Befund kann bei kleinem Prior trotzdem unwahrscheinlich bleiben.",
    "Bayes funktioniert auch ohne Messwerte: Schlüssel, Quellen, Diagnosen.",
    "Unabhängige Belege multiplizieren sich, abgeschriebene nicht.",
], groesse=20)
notizen(f, "Zusammenfassung zum Mitnehmen.")

f = neue_folie("Material zum Weiterarbeiten", None)
punkte(f, LINKS, Inches(1.5), BREIT, Inches(5.4), [
    ("ZGS_Test_Bayes.ipynb – Colab-Notebook mit Schiebereglern: ZGS, Standardfehler, t-Test, Simulation des p-Werts, "
     "Münze, Würfel, Mittelwert, Schlüssel, Quellen", {}),
    ("StatistikLive.bas – Makros für die drei Live-Folien (Würfel-Labor, Münze, Schlüssel); "
     "Einbau in ANLEITUNG.md", {}),
    ("abfuellung.csv – die 20 Packungsgewichte", {}),
    ("tools/le06_live_figuren.py – erzeugt alle Grafiken dieser Folien neu", {}),
    ("Vertiefung: Skript LE 6 (Kurs-Pool, Konfidenzintervall, Basisrate, Würfel-Detektive, "
     "Glaubwürdigkeits-Check)", {}),
], groesse=19)
notizen(f, "Dateien liegen im Ordner neben dieser Präsentation.")

prs.save(ZIEL)
print(f"{ZIEL}: {len(prs.slides)} Folien")
