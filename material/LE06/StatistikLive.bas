Attribute VB_Name = "StatistikLive"
'=============================================================================
' StatistikLive - Live-Simulationen fuer den Foliensatz ZGS_Test_Bayes
'
'  1. Wuerfel-Labor     (Zentraler Grenzwertsatz, Standardfehler)
'  2. Muenze live       (Bayes-Update ueber p, daneben der p-Wert)
'  3. Schluesselsuche   (Bayes ohne Messwerte)
'
' Einbau (einmalig): Alt+F11 -> Datei -> Datei importieren -> diese Datei.
' Dann Makro "Einrichten" ausfuehren (Alt+F8) und die Praesentation als
' PowerPoint-Praesentation mit Makros (.pptm) speichern.
'
' Die Makros finden ihre Formen ueber die Namen (Auswahlbereich, Alt+F10):
' zgsFeld, zgsBar01..26, zgsInfo, bayFeld, bayBar01..50, bayInfo,
' keyFeld, keyBar1..6, keyPct1..6, keyInfo und die Knoepfe btn...
' Umlaute und Sonderzeichen werden ueber Platzhalter wie {ue} erzeugt,
' damit die Datei reines ASCII bleibt.
'=============================================================================
Option Explicit

Private Const VIOLETT As Long = 11941990    ' RGB(102, 56, 182)
Private Const VIOLETT_HELL As Long = 15251657 ' RGB(201, 184, 232)
Private Const CYAN As Long = 10125056       ' RGB(0, 127, 154)
Private Const GRAU As Long = 7566195        ' RGB(115, 115, 115)

Private bereit As Boolean

' --- Wuerfel-Labor ----------------------------------------------------------
Private Const ZGS_BINS As Long = 26         ' Mittelwerte 1,0 / 1,2 / ... / 6,0
Private zgsN As Long
Private zgsGezinkt As Boolean
Private zgsZaehl(1 To 26) As Long
Private zgsAnzahl As Long
Private zgsSumme As Double
Private zgsQuadrat As Double

' --- Muenze ----------------------------------------------------------------
Private Const BAY_BINS As Long = 50
Private bayWuerfe As Long
Private bayKopf As Long
Private baySimuliert As Long
Private bayVerdecktP As Double

' --- Schluessel -------------------------------------------------------------
Private keyPost(1 To 6) As Double
Private keyFund(1 To 6) As Double
Private keyOrt As Long
Private keyGefunden As Boolean
Private keySuchen As Long


'=============================================================================
' Einrichten: verbindet jeden Knopf "btn..." mit dem gleichnamigen Makro
'=============================================================================
Public Sub Einrichten()
    Dim s As Slide, sh As Shape, n As Long
    For Each s In ActivePresentation.Slides
        For Each sh In s.Shapes
            If Left$(sh.Name, 3) = "btn" Then
                With sh.ActionSettings(ppMouseClick)
                    .Action = ppActionRunMacro
                    .Run = sh.Name
                End With
                n = n + 1
            End If
        Next sh
    Next s
    MsgBox T(n & " Kn{oe}pfe mit Makros verbunden." & vbCr & _
             "Jetzt als PowerPoint-Pr{ae}sentation mit Makros (.pptm) speichern."), vbInformation
End Sub


'=============================================================================
' Hilfsfunktionen
'=============================================================================
Private Sub Start()
    If Not bereit Then
        Randomize
        bereit = True
        zgsN = 5
        keyFund(1) = 0.9: keyFund(2) = 0.99: keyFund(3) = 0.6
        keyFund(4) = 0.7: keyFund(5) = 0.8: keyFund(6) = 0.1
        bayVerdecktP = NeueMuenzeP()
        KeyPrior
        keyOrt = ZieheOrt()
    End If
End Sub

' Ersetzt Platzhalter durch Unicode-Zeichen
Private Function T(ByVal s As String) As String
    s = Replace(s, "{ae}", ChrW(228))
    s = Replace(s, "{oe}", ChrW(246))
    s = Replace(s, "{ue}", ChrW(252))
    s = Replace(s, "{Ae}", ChrW(196))
    s = Replace(s, "{Oe}", ChrW(214))
    s = Replace(s, "{Ue}", ChrW(220))
    s = Replace(s, "{ss}", ChrW(223))
    s = Replace(s, "{mu}", ChrW(956))
    s = Replace(s, "{sigma}", ChrW(963))
    s = Replace(s, "{approx}", ChrW(8776))
    s = Replace(s, "{xq}", "x" & ChrW(772))
    s = Replace(s, "{wurzel}", ChrW(8730))
    s = Replace(s, "{pfeil}", ChrW(8594))
    s = Replace(s, "{mal}", ChrW(215))
    T = s
End Function

' Zahl mit Dezimalkomma
Private Function Z(ByVal x As Double, ByVal stellen As Long) As String
    Z = Replace(Format$(x, "0." & String$(stellen, "0")), ".", ",")
    If stellen = 0 Then Z = Format$(x, "0")
End Function

Private Function Folie(ByVal formName As String) As Slide
    Dim s As Slide, sh As Shape
    For Each s In ActivePresentation.Slides
        For Each sh In s.Shapes
            If sh.Name = formName Then
                Set Folie = s
                Exit Function
            End If
        Next sh
    Next s
    MsgBox "Form '" & formName & "' nicht gefunden.", vbExclamation
End Function

' Schriftgrade und Linien sind fuer 16:9-Folien (960 pt breit) gewaehlt;
' in kleineren Foliensaetzen (volle Vorlesungs-PPTX) wird mitskaliert.
Private Function Massstab() As Single
    Massstab = ActivePresentation.PageSetup.SlideWidth / 960
End Function

Private Sub SetzeText(ByVal sh As Shape, ByVal kopf As String, ByVal rumpf As String)
    With sh.TextFrame.TextRange
        .Text = T(kopf) & vbCr & T(rumpf)
        .Font.Size = 14 * Massstab()
        .Font.Bold = msoFalse
        .Font.Color.RGB = RGB(34, 34, 34)
        .Paragraphs(1).Font.Size = 17 * Massstab()
        .Paragraphs(1).Font.Bold = msoTrue
        .Paragraphs(1).Font.Color.RGB = VIOLETT
    End With
End Sub

Private Sub Balken(ByVal sh As Shape, ByVal unten As Single, ByVal h As Single)
    If h < 0.5 Then h = 0.5
    sh.Height = h
    sh.Top = unten - h
End Sub

Private Sub Markiere(ByVal s As Slide, ByVal namen As Variant, ByVal aktiv As String)
    Dim i As Long
    For i = LBound(namen) To UBound(namen)
        If namen(i) = aktiv Then
            s.Shapes(namen(i)).Fill.ForeColor.RGB = VIOLETT
        Else
            s.Shapes(namen(i)).Fill.ForeColor.RGB = CYAN
        End If
    Next i
End Sub



'=============================================================================
' 1  Wuerfel-Labor
'=============================================================================
Public Sub btnN1(): Start: zgsN = 1: ZgsLeeren: ZgsZeichnen: End Sub
Public Sub btnN5(): Start: zgsN = 5: ZgsLeeren: ZgsZeichnen: End Sub
Public Sub btnN30(): Start: zgsN = 30: ZgsLeeren: ZgsZeichnen: End Sub
Public Sub btnFair(): Start: zgsGezinkt = False: ZgsLeeren: ZgsZeichnen: End Sub
Public Sub btnGezinkt(): Start: zgsGezinkt = True: ZgsLeeren: ZgsZeichnen: End Sub
Public Sub btnZiehe1(): Start: ZgsZiehe 1: ZgsZeichnen: End Sub
Public Sub btnZiehe100(): Start: ZgsZiehe 100: ZgsZeichnen: End Sub
Public Sub btnZgsReset(): Start: ZgsLeeren: ZgsZeichnen: End Sub

Private Function Wurf() As Long
    Dim u As Double
    u = Rnd()
    If zgsGezinkt Then
        If u < 0.75 Then Wurf = Int(u / 0.15) + 1 Else Wurf = 6
    Else
        Wurf = Int(u * 6) + 1
    End If
    If Wurf > 6 Then Wurf = 6
End Function

Private Sub ZgsLeeren()
    Dim i As Long
    For i = 1 To ZGS_BINS: zgsZaehl(i) = 0: Next i
    zgsAnzahl = 0: zgsSumme = 0: zgsQuadrat = 0
End Sub

Private Sub ZgsZiehe(ByVal stichproben As Long)
    Dim k As Long, j As Long, s As Double, m As Double, b As Long
    For k = 1 To stichproben
        s = 0
        For j = 1 To zgsN
            s = s + Wurf()
        Next j
        m = s / zgsN
        b = Int((m - 0.9) / 0.2 + 0.000001) + 1
        If b < 1 Then b = 1
        If b > ZGS_BINS Then b = ZGS_BINS
        zgsZaehl(b) = zgsZaehl(b) + 1
        zgsAnzahl = zgsAnzahl + 1
        zgsSumme = zgsSumme + m
        zgsQuadrat = zgsQuadrat + m * m
    Next k
End Sub

Private Sub ZgsZeichnen()
    Dim s As Slide, feld As Shape, i As Long, maxW As Double, mu As Double, sigma As Double
    Dim se As Double, unten As Single, hMax As Single, spitze As Double
    Set s = Folie("zgsFeld")
    If s Is Nothing Then Exit Sub
    Set feld = s.Shapes("zgsFeld")
    unten = feld.Top + feld.Height
    hMax = feld.Height * 0.9

    If zgsGezinkt Then
        mu = 3.75: sigma = 1.785357
    Else
        mu = 3.5: sigma = 1.707825
    End If
    se = sigma / Sqr(zgsN)

    ' Skala: groesster Balken oder Gipfel der Normalkurve
    For i = 1 To ZGS_BINS
        If zgsZaehl(i) > maxW Then maxW = zgsZaehl(i)
    Next i
    If zgsN > 1 Then
        spitze = zgsAnzahl * 0.2 / (se * Sqr(2 * 3.14159265358979))
        If spitze > maxW Then maxW = spitze
    End If
    If maxW < 1 Then maxW = 1

    For i = 1 To ZGS_BINS
        Balken s.Shapes("zgsBar" & Format$(i, "00")), unten, CSng(hMax * zgsZaehl(i) / maxW)
    Next i

    ' Normalkurve N(mu; sigma/sqrt(n)), skaliert auf die Anzahl Stichproben
    On Error Resume Next
    s.Shapes("zgsKurve").Delete
    On Error GoTo 0
    If zgsN > 1 And zgsAnzahl > 0 Then
        Dim ff As FreeformBuilder, x As Double, px As Single, py As Single, k As Long, y As Double
        For k = 0 To 120
            x = 0.9 + 5.2 * k / 120
            y = zgsAnzahl * 0.2 * Exp(-0.5 * ((x - mu) / se) ^ 2) / (se * Sqr(2 * 3.14159265358979))
            px = feld.Left + feld.Width * (x - 0.9) / 5.2
            py = unten - hMax * y / maxW
            If k = 0 Then
                Set ff = s.Shapes.BuildFreeform(msoEditingAuto, px, py)
            Else
                ff.AddNodes msoSegmentLine, msoEditingAuto, px, py
            End If
        Next k
        With ff.ConvertToShape
            .Name = "zgsKurve"
            .Fill.Visible = msoFalse
            .Line.ForeColor.RGB = CYAN
            .Line.Weight = 2.5 * Massstab()
        End With
    End If

    Markiere s, Array("btnN1", "btnN5", "btnN30"), "btnN" & zgsN
    If zgsGezinkt Then
        Markiere s, Array("btnFair", "btnGezinkt"), "btnGezinkt"
    Else
        Markiere s, Array("btnFair", "btnGezinkt"), "btnFair"
    End If

    Dim kopf As String, rumpf As String, m As Double, sd As Double
    If zgsGezinkt Then kopf = "Gezinkter W{ue}rfel, n = " Else kopf = "Fairer W{ue}rfel, n = "
    kopf = kopf & zgsN
    If zgsAnzahl = 0 Then
        rumpf = "Noch keine Stichprobe." & vbCr & "Theorie: SE = {sigma} / {wurzel}n = " & Z(sigma, 2) & _
                " / {wurzel}" & zgsN & " = " & Z(se, 3)
    Else
        m = zgsSumme / zgsAnzahl
        If zgsAnzahl > 1 Then sd = Sqr((zgsQuadrat - zgsAnzahl * m * m) / (zgsAnzahl - 1))
        rumpf = zgsAnzahl & " Stichproben" & vbCr & _
                "Mittel der {xq}: " & Z(m, 3) & "  (Theorie " & Z(mu, 2) & ")" & vbCr & _
                "Streuung der {xq}: " & Z(sd, 3) & vbCr & _
                "Theorie: SE = {sigma}/{wurzel}n = " & Z(se, 3)
    End If
    SetzeText s.Shapes("zgsInfo"), kopf, rumpf
End Sub


'=============================================================================
' 2  Muenze live: Bayes ueber p, daneben der Binomialtest
'=============================================================================
Public Sub btnKopf(): Start: bayWuerfe = bayWuerfe + 1: bayKopf = bayKopf + 1: BayZeichnen: End Sub
Public Sub btnZahl(): Start: bayWuerfe = bayWuerfe + 1: BayZeichnen: End Sub

Public Sub btnMuenze10()
    Dim i As Long
    Start
    For i = 1 To 10
        bayWuerfe = bayWuerfe + 1
        If Rnd() < bayVerdecktP Then bayKopf = bayKopf + 1
    Next i
    baySimuliert = baySimuliert + 10
    BayZeichnen
End Sub

Public Sub btnMuenzeReset()
    Start
    bayWuerfe = 0: bayKopf = 0: baySimuliert = 0
    bayVerdecktP = NeueMuenzeP()
    BayZeichnen
End Sub

Private Function NeueMuenzeP() As Double
    If Rnd() < 0.5 Then NeueMuenzeP = 0.5 Else NeueMuenzeP = 0.7
End Function

' log der Posterior-Dichte (flacher Prior) bis auf eine Konstante
Private Function LogPost(ByVal p As Double) As Double
    LogPost = bayKopf * Log(p) + (bayWuerfe - bayKopf) * Log(1 - p)
End Function

Private Sub BayZeichnen()
    Dim s As Slide, feld As Shape, i As Long, p As Double, w(1 To 50) As Double, maxL As Double
    Dim unten As Single, hMax As Single
    Set s = Folie("bayFeld")
    If s Is Nothing Then Exit Sub
    Set feld = s.Shapes("bayFeld")
    unten = feld.Top + feld.Height
    hMax = feld.Height * 0.9

    maxL = -1E+300
    For i = 1 To BAY_BINS
        p = (i - 0.5) / BAY_BINS
        w(i) = LogPost(p)
        If w(i) > maxL Then maxL = w(i)
    Next i
    For i = 1 To BAY_BINS
        Balken s.Shapes("bayBar" & Format$(i, "00")), unten, CSng(hMax * Exp(w(i) - maxL))
    Next i

    ' feines Gitter fuer Wahrscheinlichkeiten und Intervall
    Const FEIN As Long = 2000
    Dim d(1 To 2000) As Double, summe As Double, rechts As Double, kum As Double
    Dim lo As Double, hi As Double, maxF As Double
    maxF = -1E+300
    For i = 1 To FEIN
        d(i) = LogPost((i - 0.5) / FEIN)
        If d(i) > maxF Then maxF = d(i)
    Next i
    For i = 1 To FEIN
        d(i) = Exp(d(i) - maxF)
        summe = summe + d(i)
        If (i - 0.5) / FEIN > 0.5 Then rechts = rechts + d(i)
    Next i
    lo = -1: hi = -1
    For i = 1 To FEIN
        kum = kum + d(i) / summe
        If lo < 0 And kum >= 0.025 Then lo = (i - 0.5) / FEIN
        If hi < 0 And kum >= 0.975 Then hi = (i - 0.5) / FEIN
    Next i

    Dim kopf As String, rumpf As String
    kopf = bayKopf & " {mal} Kopf in " & bayWuerfe & " W{ue}rfen"
    If bayWuerfe = 0 Then
        rumpf = "Alle p von 0 bis 1 sind gleich plausibel."
    Else
        rumpf = "Bayes: P(p > 0,5 | Daten) = " & Z(100 * rechts / summe, 1) & " %" & vbCr & _
                "95 % glaubw{ue}rdig: " & Z(lo, 2) & " bis " & Z(hi, 2) & vbCr & _
                "Test gegen p = 0,5: p-Wert = " & Z(BinomPWert(bayKopf, bayWuerfe), 3)
        If baySimuliert >= 100 And baySimuliert = bayWuerfe Then
            If bayVerdecktP > 0.6 Then
                rumpf = rumpf & vbCr & "Aufl{oe}sung: Die verdeckte M{ue}nze ist gezinkt (p = 0,7)."
            Else
                rumpf = rumpf & vbCr & "Aufl{oe}sung: Die verdeckte M{ue}nze ist fair (p = 0,5)."
            End If
        End If
    End If
    SetzeText s.Shapes("bayInfo"), kopf, rumpf
End Sub

' exakter zweiseitiger Binomialtest gegen p = 0,5
Private Function BinomPWert(ByVal k As Long, ByVal n As Long) As Double
    Dim x As Long, abstand As Double, summe As Double
    If n = 0 Then BinomPWert = 1: Exit Function
    Dim lf() As Double
    ReDim lf(0 To n)
    For x = 1 To n
        lf(x) = lf(x - 1) + Log(x)
    Next x
    abstand = Abs(k - n / 2) - 0.000001
    For x = 0 To n
        If Abs(x - n / 2) >= abstand Then
            summe = summe + Exp(lf(n) - lf(x) - lf(n - x) - n * Log(2))
        End If
    Next x
    If summe > 1 Then summe = 1
    BinomPWert = summe
End Function


'=============================================================================
' 3  Schluesselsuche
'=============================================================================
Public Sub btnSuche1(): Suche 1: End Sub
Public Sub btnSuche2(): Suche 2: End Sub
Public Sub btnSuche3(): Suche 3: End Sub
Public Sub btnSuche4(): Suche 4: End Sub
Public Sub btnSuche5(): Suche 5: End Sub
Public Sub btnSuche6(): Suche 6: End Sub

Public Sub btnKeyReset()
    Start
    KeyPrior
    keyOrt = ZieheOrt()
    keyGefunden = False
    keySuchen = 0
    KeyZeichnen "Neuer Fall. Der Schl{ue}ssel ist versteckt.", _
                "Vorwissen aus Gewohnheit. Wo suchen Sie zuerst?"
End Sub

Private Sub KeyPrior()
    keyPost(1) = 0.35: keyPost(2) = 0.25: keyPost(3) = 0.15
    keyPost(4) = 0.1: keyPost(5) = 0.1: keyPost(6) = 0.05
End Sub

Private Function ZieheOrt() As Long
    Dim u As Double, i As Long, kum As Double
    Dim pr As Variant
    pr = Array(0.35, 0.25, 0.15, 0.1, 0.1, 0.05)
    u = Rnd()
    For i = 0 To 5
        kum = kum + pr(i)
        If u < kum Then ZieheOrt = i + 1: Exit Function
    Next i
    ZieheOrt = 6
End Function

Private Function OrtName(ByVal i As Long) As String
    OrtName = T(Choose(i, "Jackentasche", "Schl{ue}sselbrett", "Schreibtisch", "Auto", "K{ue}che", _
                       "ganz woanders"))
End Function

Private Sub Suche(ByVal i As Long)
    Dim j As Long, summe As Double
    Start
    If keyGefunden Then
        KeyZeichnen "Schon gefunden!", "F{ue}r einen neuen Fall auf " & ChrW(8222) & "Neuer Fall" & ChrW(8220) & " klicken."
        Exit Sub
    End If
    keySuchen = keySuchen + 1
    If keyOrt = i And Rnd() < keyFund(i) Then
        keyGefunden = True
        For j = 1 To 6: keyPost(j) = 0: Next j
        keyPost(i) = 1
        KeyZeichnen "Gefunden: " & OrtName(i) & "!", "nach " & keySuchen & " Suche(n)."
        Exit Sub
    End If
    ' Bayes-Update: P(dort) wird mit (1 - Entdeckungschance) multipliziert
    keyPost(i) = keyPost(i) * (1 - keyFund(i))
    For j = 1 To 6: summe = summe + keyPost(j): Next j
    For j = 1 To 6: keyPost(j) = keyPost(j) / summe: Next j

    Dim best As Long, bestW As Long
    best = 1: bestW = 1
    For j = 2 To 6
        If keyPost(j) * keyFund(j) > keyPost(best) * keyFund(best) Then best = j
        If keyPost(j) > keyPost(bestW) Then bestW = j
    Next j
    KeyZeichnen "Nicht gefunden: " & OrtName(i), _
                "Am wahrscheinlichsten jetzt: " & OrtName(bestW) & " (" & Z(100 * keyPost(bestW), 0) & " %)" & vbCr & _
                "Suchen lohnt am meisten: " & OrtName(best) & vbCr & _
                "(P " & ChrW(215) & " Entdeckungschance = " & Z(100 * keyPost(best) * keyFund(best), 0) & " %)"
End Sub

Private Sub KeyZeichnen(ByVal kopf As String, ByVal rumpf As String)
    Dim s As Slide, feld As Shape, j As Long, unten As Single, hMax As Single, skala As Double
    Dim b As Shape, lab As Shape
    Set s = Folie("keyFeld")
    If s Is Nothing Then Exit Sub
    Set feld = s.Shapes("keyFeld")
    unten = feld.Top + feld.Height
    hMax = feld.Height * 0.85
    skala = 0.4
    For j = 1 To 6
        If keyPost(j) > skala Then skala = keyPost(j)
    Next j
    For j = 1 To 6
        Set b = s.Shapes("keyBar" & j)
        Balken b, unten, CSng(hMax * keyPost(j) / skala)
        If keyGefunden And keyPost(j) = 1 Then
            b.Fill.ForeColor.RGB = CYAN
        Else
            b.Fill.ForeColor.RGB = VIOLETT
        End If
        Set lab = s.Shapes("keyPct" & j)
        lab.Top = b.Top - lab.Height - 2
        lab.TextFrame.TextRange.Text = Z(100 * keyPost(j), 0) & " %"
    Next j
    SetzeText s.Shapes("keyInfo"), kopf, rumpf
End Sub
