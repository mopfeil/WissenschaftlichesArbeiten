# Live-Folien mit VBA einrichten

Vier Folien in `ZGS_Test_Bayes.pptx` sind interaktiv, wenn das Makro-Modul
`StatistikLive.bas` eingebaut ist:

| Folie | Titel | Was passiert |
|---|---|---|
| 6 | Live: Würfel-Labor | Stichproben aus n Würfen ziehen, Histogramm der Mittelwerte, Normalkurve aus dem ZGS, empirischer und theoretischer Standardfehler |
| 23 | Live: Ist diese Münze gezinkt? | Kopf/Zahl eingeben oder eine verdeckte Münze werfen; Posterior über p, P(p > 0,5), Glaubwürdigkeitsintervall und daneben der p-Wert des Binomialtests |
| 31 | Live: Schlüsselsuche | Schlüssel ist verdeckt versteckt; jede erfolglose Suche aktualisiert die Wahrscheinlichkeiten, unter jedem Ort steht der Bayes-Faktor der letzten Suche, die Formel (Posterior-Chance = Prior-Chance × Bayes-Faktor) bleibt eingeblendet |
| 34 | Live: Den Diamanten durchrechnen | Drei Erklärungen aus dem Diamanten (Idee, Gegenteil, Weder-noch); jede Beobachtung aus einer Spitze („beobachtet“ / „nicht beobachtet“) aktualisiert die Wahrscheinlichkeiten, unter jeder Erklärung stehen P(B \| H) und Bayes-Faktor, im Infokasten die paarweisen Bayes-Faktoren; die Formel bleibt eingeblendet |

Dieselben vier Folien stecken auch in der vollen Vorlesungsfassung
`pdf/WuZ_WissArbeiten_Folien.pptx`, jeweils direkt hinter der passenden Folie
(„Weiterwürfeln am Rechner“, „Der Posterior wandert mit jedem Wurf“, „Wo ist mein
Schlüssel?“, „Welche Beobachtung trennt die Positionen?“). `make publish` fügt sie mit `tools/pptx_live_einfuegen.py` ein und
skaliert sie auf das Folienformat; die Makros passen Schriftgrade selbst an. Der
Einbau unten funktioniert dort genauso, mit dieser Datei statt `ZGS_Test_Bayes.pptx`.

## Einmalig einrichten (PowerPoint für Windows)

1. `ZGS_Test_Bayes.pptx` öffnen.
2. **Alt + F11** öffnet den VBA-Editor. Falls das nicht klappt: Datei → Optionen →
   Menüband anpassen → Haken bei „Entwicklertools“, dann Entwicklertools → Visual Basic.
3. Im VBA-Editor: **Datei → Datei importieren …** → `StatistikLive.bas` wählen.
4. Editor schließen, in PowerPoint **Alt + F8** → Makro `Einrichten` → Ausführen.
   Es verbindet jeden Knopf (Formen mit Namen `btn…`) mit dem gleichnamigen Makro.
5. **Datei → Speichern unter** → Dateityp **PowerPoint-Präsentation mit Makros (*.pptm)**.

Beim nächsten Öffnen der `.pptm` fragt PowerPoint, ob Makros aktiviert werden sollen:
„Inhalt aktivieren“ wählen. Je nach Sicherheitseinstellung der Hochschule muss der
Speicherort als vertrauenswürdig eingetragen werden (Trust Center → Vertrauenswürdige Speicherorte).

## Benutzen

Die Knöpfe reagieren nur im **Vortragsmodus** (F5). Jeder Klick ändert die Formen auf der
Folie direkt. Der Zustand bleibt erhalten, bis Sie „Zurücksetzen“ klicken oder PowerPoint
schließen. Die Balken bleiben nach dem Vortrag so stehen, wie sie zuletzt waren; vor dem
Speichern einmal „Zurücksetzen“ klicken, wenn die Folie leer starten soll.

## Wenn etwas nicht geht

- **„Form … nicht gefunden“**: Eine Form wurde umbenannt oder gelöscht. Namen prüfen mit
  Start → Anordnen → Auswahlbereich (Alt + F10). Die Makros brauchen `zgsFeld`,
  `zgsBar01`–`zgsBar26`, `zgsInfo`, `bayFeld`, `bayBar01`–`bayBar50`, `bayInfo`,
  `keyFeld`, `keyBar1`–`keyBar6`, `keyPct1`–`keyPct6`, `keyBF1`–`keyBF6`, `keyInfo`,
  `diaFeld`, `diaBar1`–`diaBar3`, `diaPct1`–`diaPct3`, `diaL1`–`diaL3`, `diaBF1`–`diaBF3`, `diaObs1`–`diaObs3`,
  `diaInfo` und die Knöpfe `btn…`.
- **Import meldet Fehler oder der Code steht in einer Zeile** (die Datei hat dann Unix-Zeilenenden,
  z. B. nach dem Weg über die Dropbox): `StatistikLive.bas` im Editor öffnen, alles **ab der Zeile
  nach `Attribute VB_Name = …`** kopieren, im VBA-Editor Einfügen → Modul und den Text einfügen.
- **Klick tut nichts**: `Einrichten` noch einmal ausführen; prüfen, ob Makros aktiviert sind.
- **Die Folie aktualisiert sich nicht sichtbar**: einmal mit den Pfeiltasten weiter- und zurückblättern.
- **Mac**: Die Makros nutzen nur Standardobjekte von PowerPoint und sollten auch unter
  PowerPoint für Mac laufen; getestet ist das nicht.

Ohne Makros zeigt das Colab-Notebook `ZGS_Test_Bayes.ipynb` dieselben Simulationen
(Abschnitte 1, 5, 8 und 10).

## Hinweis

Die Makros sind nicht in PowerPoint selbst getestet, weil sie unter Linux erstellt wurden.
Logik und Geometrie sind in Python nachgerechnet. Bitte vor der Vorlesung einmal
durchklicken.
