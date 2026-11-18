#!/usr/bin/env python3
"""Grafiken fuer LE 6 (Ergaenzung) und den Live-Foliensatz material/LE06.

Erzeugt
- PNG-Dateien (200 dpi) in material/LE06/bilder/ fuer ZGS_Test_Bayes.pptx,
- PDF-Fassungen ausgewaehlter Grafiken als figures/LE06_*.pdf fuer Skript
  und Folien (Standardfehler ablesen, Abfuellanlage, p-Wert-Simulation,
  Bayes-Flaechenbild, Bayes-Mittelwert, zwei Aussagen, Schluessel, Quellen),
- den Beispieldatensatz material/LE06/abfuellung.csv.
Alle Simulationen haben feste Startwerte.

    python3 tools/le06_live_figuren.py

Benoetigt numpy, scipy, matplotlib. Schrift: Barlow Semi Condensed aus fonts/.
"""
import glob
import os

import numpy as np
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Rectangle
from matplotlib.ticker import FuncFormatter

HIER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HIER, "material", "LE06", "bilder")
PDF_OUT = os.path.join(HIER, "figures")
DATEN = os.path.join(HIER, "material", "LE06")
os.makedirs(OUT, exist_ok=True)
os.makedirs(DATEN, exist_ok=True)

for f in glob.glob(os.path.join(HIER, "fonts", "*.otf")):
    font_manager.fontManager.addfont(f)

VIOLETT = "#6638B6"
VIOLETT_HELL = "#C9B8E8"
CYAN = "#007F9A"
CYAN_HELL = "#99DDFD"
ROT = "#C0392B"
ROT_HELL = "#F2B8B0"
GRAU = "#737373"
GRAU_HELL = "#D9D9D9"
TINTE = "#222222"

plt.rcParams.update({
    "font.family": ["Barlow Semi Condensed", "DejaVu Sans"],
    "font.size": 13,
    "axes.titlesize": 14,
    "axes.labelsize": 13,
    "axes.edgecolor": GRAU,
    "axes.labelcolor": TINTE,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.titleweight": "semibold",
    "axes.titlecolor": TINTE,
    "xtick.color": GRAU,
    "ytick.color": GRAU,
    "xtick.labelcolor": TINTE,
    "ytick.labelcolor": TINTE,
    "legend.frameon": False,
    "mathtext.fontset": "custom",
    "mathtext.rm": "Barlow Semi Condensed",
    "mathtext.it": "Barlow Semi Condensed:italic",
    "savefig.dpi": 200,
})


def komma(x, _pos=None):
    s = f"{x:g}"
    return s.replace(".", ",").replace("-", "−")


def prozent(x, _pos=None):
    return f"{x * 100:.0f} %"


def zahl(x, nachkomma=2):
    return f"{x:.{nachkomma}f}".replace(".", ",").replace("-", "−")


def achsen_komma(ax, x=True, y=True):
    if x:
        ax.xaxis.set_major_formatter(FuncFormatter(komma))
    if y:
        ax.yaxis.set_major_formatter(FuncFormatter(komma))


# Grafiken, die auch im Skript und auf den LaTeX-Folien stehen (A5 quer)
PDF_NAMEN = {
    "f03_se_ablesen": "LE06_se_ablesen",
    "f08_abfuell_daten": "LE06_abfuell_daten",
    "f09_abfuell_test": "LE06_abfuell_test",
    "f10_welten": "LE06_pwert_simulation",
    "f11_bayes_flaeche": "LE06_bayes_flaeche",
    "f15_abfuell_bayes": "LE06_abfuell_bayes",
    "f16_vergleich": "LE06_zwei_aussagen",
    "f17_schluessel": "LE06_schluessel",
    "f18_quelle": "LE06_quellen",
}


def speichern(fig, name):
    fig.savefig(os.path.join(OUT, name + ".png"), bbox_inches="tight", facecolor="white")
    print("  material/LE06/bilder/" + name + ".png")
    if name in PDF_NAMEN:
        # breite Grafiken fuer die A5-Folien etwas verkleinern, damit die Schrift lesbar bleibt
        w, h = fig.get_size_inches()
        if w > 10:
            fig.set_size_inches(w * 0.8, h * 0.88)
            fig.tight_layout()
        fig.savefig(os.path.join(PDF_OUT, PDF_NAMEN[name] + ".pdf"), bbox_inches="tight")
        print("  figures/" + PDF_NAMEN[name] + ".pdf")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Modelle (dieselben Zahlen wie auf den Folien)
# ---------------------------------------------------------------------------
AUGEN = np.arange(1, 7)
P_FAIR = np.full(6, 1 / 6)
P_GEZINKT = np.array([0.15, 0.15, 0.15, 0.15, 0.15, 0.25])   # die Sechs kommt öfter
MU_FAIR, SIG_FAIR = 3.5, np.sqrt(35 / 12)                       # 3,5 und 1,71
MU_GEZ = float(AUGEN @ P_GEZINKT)                               # 3,75
SIG_GEZ = float(np.sqrt(AUGEN**2 @ P_GEZINKT - MU_GEZ**2))      # 1,79

# Abfüllanlage: 500-g-Packungen, Stichprobe n = 20
SOLL, N_ABF, XQ_ABF, S_ABF = 500.0, 20, 497.8, 4.6


def abfuelldaten():
    """20 Packungsgewichte mit genau x̄ = 497,8 g und s = 4,6 g (auf 0,1 g)."""
    rng = np.random.default_rng(7)
    roh = rng.normal(0, 1, N_ABF)
    z = (roh - roh.mean()) / roh.std(ddof=1)
    x = np.round(XQ_ABF + S_ABF * z, 1)
    # Rundung korrigieren, damit Mittelwert exakt passt
    x[np.argmax(x)] += round(N_ABF * XQ_ABF - x.sum(), 1)
    return x


# ---------------------------------------------------------------------------
# Teil A: Zentraler Grenzwertsatz, Standardfehler, Test
# ---------------------------------------------------------------------------

def f01_wuerfel():
    fig, ax = plt.subplots(figsize=(8, 4))
    b = 0.38
    ax.bar(AUGEN - b / 2, P_FAIR, b, color=GRAU_HELL, edgecolor=GRAU, label="fairer Würfel")
    ax.bar(AUGEN + b / 2, P_GEZINKT, b, color=VIOLETT, label="gezinkter Würfel")
    ax.set_xticks(AUGEN)
    ax.set_xlabel("Augenzahl")
    ax.set_ylabel("Wahrscheinlichkeit")
    ax.yaxis.set_major_formatter(FuncFormatter(prozent))
    ax.legend(loc="upper left")
    ax.text(6.2, 0.262, "25 %", color=VIOLETT, ha="center", fontsize=12)
    ax.set_title(f"Fair: μ = 3,5, σ = {zahl(SIG_FAIR)}     Gezinkt: μ = {zahl(MU_GEZ)}, σ = {zahl(SIG_GEZ)}",
                 fontweight="normal", fontsize=13)
    speichern(fig, "f01_wuerfel")


def f02_zgs():
    rng = np.random.default_rng(1)
    ns = [1, 2, 5, 30]
    fig, axs = plt.subplots(1, 4, figsize=(13, 3.6), sharey=False)
    for ax, n in zip(axs, ns):
        wuerfe = rng.choice(AUGEN, size=(20000, n), p=P_GEZINKT)
        m = wuerfe.mean(axis=1)
        if n < 30:
            werte, zaehl = np.unique(m, return_counts=True)
            breite = 1 / n
            ax.bar(werte, zaehl / zaehl.sum() / breite, width=breite * 0.9,
                   color=VIOLETT_HELL, edgecolor=VIOLETT if n < 5 else "none", lw=0.6)
        else:
            ax.hist(m, bins=np.arange(2.5, 5.0, 1 / 15) + 1 / 60, density=True, color=VIOLETT_HELL, lw=0)
        x = np.linspace(0.5, 6.5, 400)
        se = SIG_GEZ / np.sqrt(n)
        if n > 1:
            ax.plot(x, stats.norm.pdf(x, MU_GEZ, se), color=CYAN, lw=2.2)
        ax.set_xlim(0.5, 6.5)
        ax.set_xticks(range(1, 7))
        ax.set_yticks([])
        ax.spines["left"].set_visible(False)
        ax.set_title(f"Mittel aus n = {n} Würf{'en' if n > 1 else ''}".replace("Würf", "Würf" if n > 1 else "Wurf"))
        ax.text(0.03, 0.95, f"SE = {zahl(se)}", transform=ax.transAxes, va="top", color=CYAN, fontsize=12)
        ax.set_xlabel("x̄")
    axs[0].set_title("Ein Wurf (n = 1)")
    fig.text(0.5, -0.04, "Violett: 20 000 simulierte Stichproben aus dem gezinkten Würfel.  "
             "Cyan: Normalverteilung N(μ; σ/√n) nach dem Zentralen Grenzwertsatz.",
             ha="center", color=GRAU, fontsize=12)
    fig.tight_layout()
    speichern(fig, "f02_zgs")


def f03_se_ablesen():
    n = 30
    se = SIG_FAIR / np.sqrt(n)
    x = np.linspace(MU_FAIR - 4 * se, MU_FAIR + 4 * se, 600)
    y = stats.norm.pdf(x, MU_FAIR, se)
    fig, ax = plt.subplots(figsize=(9, 4.6))
    ax.fill_between(x, y, where=np.abs(x - MU_FAIR) <= 2 * se, color=CYAN_HELL, alpha=0.6, lw=0)
    ax.fill_between(x, y, where=np.abs(x - MU_FAIR) <= se, color=CYAN_HELL, lw=0)
    ax.plot(x, y, color=CYAN, lw=2.4)
    top = stats.norm.pdf(MU_FAIR, MU_FAIR, se)
    ax.axvline(MU_FAIR, color=GRAU, lw=1, ls="--")
    # Wendepunkt = 1 SE
    yw = stats.norm.pdf(MU_FAIR + se, MU_FAIR, se)
    ax.annotate("", xy=(MU_FAIR + se, yw), xytext=(MU_FAIR, yw),
                arrowprops=dict(arrowstyle="<->", color=VIOLETT, lw=2))
    ax.text(MU_FAIR + se + 0.04, yw + 0.06, f"1 SE = {zahl(se)}", color=VIOLETT, ha="left", fontsize=14,
            fontweight="semibold")
    ax.plot([MU_FAIR + se], [yw], "o", color=VIOLETT)
    ax.text(MU_FAIR + se + 0.03, yw - 0.12, "Wendepunkt", color=VIOLETT, fontsize=11)
    ax.text(MU_FAIR, top * 0.35, "68 %", ha="center", fontsize=16, color=TINTE, fontweight="semibold")
    for k, txt, yy in ((1, "± 1 SE: 68 %", -0.10), (2, "± 2 SE: 95 %", -0.20)):
        ax.annotate("", xy=(MU_FAIR + k * se, top * yy), xytext=(MU_FAIR - k * se, top * yy),
                    arrowprops=dict(arrowstyle="<->", color=CYAN, lw=1.6))
        ax.text(MU_FAIR + k * se + 0.03, top * yy, txt, va="center", color=CYAN, fontsize=12)
    ax.set_ylim(top * -0.27, top * 1.08)
    ax.set_xticks([MU_FAIR + k * se for k in range(-3, 4)])
    ax.set_xticklabels([zahl(MU_FAIR + k * se) for k in range(-3, 4)])
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    ax.set_xlabel("Mittelwert x̄ aus 30 Würfen (fairer Würfel)")
    ax.set_title(f"SE = σ / √n = {zahl(SIG_FAIR)} / √30 = {zahl(se)}", fontweight="normal")
    speichern(fig, "f03_se_ablesen")


def f04_wurzel_n():
    n = np.arange(1, 201)
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(n, SIG_FAIR / np.sqrt(n), color=VIOLETT, lw=2.4)
    for k in (1, 4, 16, 64):
        ax.plot(k, SIG_FAIR / np.sqrt(k), "o", color=CYAN)
        ax.text(k + 4, SIG_FAIR / np.sqrt(k) + 0.04, f"n = {k}: {zahl(SIG_FAIR / np.sqrt(k))}", color=CYAN,
                fontsize=12)
    ax.set_xlabel("Anzahl Würfe n")
    ax.set_ylabel("Standardfehler SE")
    achsen_komma(ax)
    ax.set_title("Vierfache Stichprobe → halber Standardfehler", fontweight="normal")
    speichern(fig, "f04_wurzel_n")


def flaeche_test(ax, mu0, se, beob, xlabel, seiten="zwei", farbe_beob=VIOLETT, krit=None):
    x = np.linspace(mu0 - 4.2 * se, mu0 + 4.2 * se, 800)
    y = stats.norm.pdf(x, mu0, se)
    ax.plot(x, y, color=GRAU, lw=2)
    ax.fill_between(x, y, color=GRAU_HELL, alpha=0.5, lw=0)
    d = abs(beob - mu0)
    if seiten == "zwei":
        ax.fill_between(x, y, where=x >= mu0 + d, color=ROT_HELL, lw=0)
        ax.fill_between(x, y, where=x <= mu0 - d, color=ROT_HELL, lw=0)
        ax.axvline(2 * mu0 - beob, color=farbe_beob, lw=1.2, ls=":")
    elif seiten == "links":
        ax.fill_between(x, y, where=x <= beob, color=ROT_HELL, lw=0)
    ax.axvline(beob, color=farbe_beob, lw=2.6)
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    ax.set_xlabel(xlabel)
    return x, y


def f05_test_wuerfel():
    n, xq = 60, 3.95
    se = SIG_FAIR / np.sqrt(n)
    z = (xq - MU_FAIR) / se
    p = 2 * stats.norm.sf(z)
    fig, ax = plt.subplots(figsize=(9, 4.4))
    flaeche_test(ax, MU_FAIR, se, xq, "Mittelwert aus 60 Würfen")
    top = stats.norm.pdf(0) / se
    ax.text(xq + 0.03, top * 0.8, f"beobachtet\nx̄ = {zahl(xq)}", color=VIOLETT, fontsize=13)
    ax.text(MU_FAIR, top * 0.45, f"Welt „Würfel fair“\nμ₀ = 3,5;  SE = {zahl(se)}", ha="center", color=TINTE,
            fontsize=12)
    ax.text(xq + 0.25, top * 0.08, f"p = {zahl(p, 3)}\n(beide Flächen)", color=ROT, fontsize=13,
            fontweight="semibold")
    ax.set_xticks([MU_FAIR + k * se for k in range(-3, 4)])
    ax.set_xticklabels([f"{k:+d} SE".replace("+0 SE", "3,5").replace("-", "−") for k in range(-3, 4)])
    ax.set_title(f"z = (3,95 − 3,5) / {zahl(se, 3)} = {zahl(z)}", fontweight="normal")
    speichern(fig, "f05_test_wuerfel")


def f06_t_vs_z():
    x = np.linspace(-4.5, 4.5, 600)
    fig, ax = plt.subplots(figsize=(7.5, 4))
    ax.plot(x, stats.norm.pdf(x), color=CYAN, lw=2.4, label="Normalverteilung (σ bekannt)")
    ax.plot(x, stats.t.pdf(x, 4), color=VIOLETT, lw=2.2, ls="--", label="t-Verteilung, n = 5 (df = 4)")
    ax.plot(x, stats.t.pdf(x, 19), color=VIOLETT, lw=1.6, label="t-Verteilung, n = 20 (df = 19)")
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    ax.legend(loc="upper left", fontsize=12)
    ax.set_xlabel("Abstand vom Sollwert in Standardfehlern")
    ax.text(3.0, 0.05, "dickere\nRänder", color=VIOLETT, fontsize=12)
    achsen_komma(ax, y=False)
    speichern(fig, "f06_t_vs_z")


def f07_muenze_test():
    n, k = 100, 61
    ks = np.arange(30, 71)
    pmf = stats.binom.pmf(ks, n, 0.5)
    fig, ax = plt.subplots(figsize=(9, 4.2))
    farben = [ROT_HELL if abs(kk - 50) >= abs(k - 50) else GRAU_HELL for kk in ks]
    ax.bar(ks, pmf, width=0.85, color=farben)
    x = np.linspace(30, 70, 400)
    ax.plot(x, stats.norm.pdf(x, 50, 5), color=CYAN, lw=2, label="Normal-Näherung: μ = 50, SE = 5")
    ax.axvline(k, color=VIOLETT, lw=2.4)
    ax.text(k + 0.6, 0.07, "beobachtet:\n61 × Kopf", color=VIOLETT, fontsize=13)
    p_ex = stats.binomtest(k, n, 0.5).pvalue
    ax.text(64, 0.025, f"p = {zahl(p_ex, 3)}\n(exakt, zweiseitig)", color=ROT, fontsize=12, fontweight="semibold")
    ax.set_xlabel("Anzahl Kopf in 100 Würfen, wenn die Münze fair ist")
    ax.set_ylabel("Wahrscheinlichkeit")
    ax.yaxis.set_major_formatter(FuncFormatter(prozent))
    ax.legend(loc="upper left", fontsize=12)
    speichern(fig, "f07_muenze_test")


def f08_abfuell_daten(x):
    fig, ax = plt.subplots(figsize=(9, 3.2))
    rng = np.random.default_rng(3)
    ax.scatter(x, rng.uniform(-0.25, 0.25, len(x)), s=70, color=VIOLETT, alpha=0.8, zorder=3)
    ax.axvline(SOLL, color=GRAU, lw=1.6, ls="--")
    ax.text(SOLL + 0.2, 0.42, "Sollwert 500 g", color=GRAU, fontsize=12)
    ax.axvline(x.mean(), color=CYAN, lw=2.6)
    ax.text(x.mean() - 0.2, 0.42, f"x̄ = {zahl(x.mean(), 1)} g", color=CYAN, fontsize=12, ha="right")
    ax.annotate("", xy=(x.mean() + x.std(ddof=1), -0.4), xytext=(x.mean() - x.std(ddof=1), -0.4),
                arrowprops=dict(arrowstyle="<->", color=CYAN))
    ax.text(x.mean() - 2.5, -0.55, f"± s = {zahl(x.std(ddof=1), 1)} g", color=CYAN, ha="center", va="top", fontsize=12)
    ax.set_ylim(-0.8, 0.6)
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    ax.set_xlabel("Füllgewicht der 20 Packungen in g")
    achsen_komma(ax, y=False)
    speichern(fig, "f08_abfuell_daten")


def f09_abfuell_test():
    se = S_ABF / np.sqrt(N_ABF)
    t = (XQ_ABF - SOLL) / se
    p = stats.t.cdf(t, N_ABF - 1)
    fig, ax = plt.subplots(figsize=(9, 4.4))
    x = np.linspace(SOLL - 4.2 * se, SOLL + 4.2 * se, 800)
    y = stats.t.pdf((x - SOLL) / se, N_ABF - 1) / se
    ax.plot(x, y, color=GRAU, lw=2)
    ax.fill_between(x, y, color=GRAU_HELL, alpha=0.5, lw=0)
    ax.fill_between(x, y, where=x <= XQ_ABF, color=ROT_HELL, lw=0)
    ax.axvline(XQ_ABF, color=VIOLETT, lw=2.6)
    k5 = SOLL + stats.t.ppf(0.05, N_ABF - 1) * se
    k05 = SOLL - 0.640 * S_ABF
    top = y.max()
    for k, txt, yy, ha, dx in ((k5, "Grenze α = 5 %", 0.75, "left", 0.08),
                               (k05, "Grenze Eichrecht\nα = 0,5 %", 0.45, "right", -0.08)):
        ax.axvline(k, color=CYAN, lw=1.3, ls="--")
        ax.text(k + dx, top * yy, txt + f"\n{zahl(k, 1)} g", color=CYAN, fontsize=11, ha=ha)
    ax.text(XQ_ABF - 0.12, top * 0.95, f"x̄ = {zahl(XQ_ABF, 1)} g", color=VIOLETT, fontsize=13, ha="right")
    ax.text(SOLL + 1.15, top * 0.6, f"Welt „Anlage füllt\nim Mittel 500 g“\nSE = {zahl(se)} g", color=TINTE,
            fontsize=12)
    ax.text(XQ_ABF - 2.6, top * 0.08, f"p = {zahl(p, 3)}", color=ROT, fontsize=14, fontweight="semibold")
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    ax.set_xlabel("Mittelwert von 20 Packungen in g")
    achsen_komma(ax, y=False)
    ax.set_title(f"t = (497,8 − 500) / {zahl(se, 3)} = {zahl(t)}   (df = 19, einseitig)", fontweight="normal")
    speichern(fig, "f09_abfuell_test")


def f10_welten():
    rng = np.random.default_rng(11)
    sims = 10000
    stich = rng.normal(SOLL, S_ABF, size=(sims, N_ABF))
    xq = stich.mean(axis=1)
    t = (xq - SOLL) / (stich.std(axis=1, ddof=1) / np.sqrt(N_ABF))
    t_beob = (XQ_ABF - SOLL) / (S_ABF / np.sqrt(N_ABF))
    anteil = np.mean(t <= t_beob)
    fig, ax = plt.subplots(figsize=(9, 4.2))
    bins = np.linspace(-5, 5, 81)
    h, kanten = np.histogram(t, bins)
    mitte = (kanten[:-1] + kanten[1:]) / 2
    ax.bar(mitte, h, width=kanten[1] - kanten[0], color=[ROT if m <= t_beob else GRAU_HELL for m in mitte])
    ax.axvline(t_beob, color=VIOLETT, lw=2.4)
    ax.text(t_beob - 0.1, h.max() * 0.85, f"unsere Stichprobe\nt = {zahl(t_beob)}", color=VIOLETT, ha="right",
            fontsize=13)
    ax.text(t_beob - 0.3, h.max() * 0.28, f"{np.sum(t <= t_beob)} von 10 000\n= {zahl(anteil * 100, 1)} %",
            color=ROT, ha="right", fontsize=13, fontweight="semibold")
    ax.set_xlabel("t-Wert der Stichprobe")
    ax.set_ylabel("Anzahl Stichproben")
    ax.set_title("10 000 Stichproben aus einer Anlage, die genau 500 g abfüllt", fontweight="normal")
    achsen_komma(ax)
    speichern(fig, "f10_welten")
    return anteil


# ---------------------------------------------------------------------------
# Teil B: Bayes
# ---------------------------------------------------------------------------
P_KOPF_GEZ = 0.7


def f11_bayes_flaeche():
    prior_g = 0.2
    lk_g, lk_f = P_KOPF_GEZ, 0.5
    fig, axs = plt.subplots(1, 3, figsize=(13, 4.3))
    titel = ["1  Vorwissen (Prior)", "2  Beobachtung: Kopf", "3  Nur Kopf-Welten zählen"]
    for ax, t in zip(axs, titel):
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_title(t, loc="left")
    # 1 Prior
    a = axs[0]
    a.add_patch(Rectangle((0, 0), prior_g, 1, color=VIOLETT, alpha=0.85))
    a.add_patch(Rectangle((prior_g, 0), 1 - prior_g, 1, color=GRAU_HELL))
    a.text(prior_g / 2, 0.5, "gezinkt\n20 %", ha="center", va="center", color="white", fontsize=12,
           fontweight="semibold")
    a.text(prior_g + (1 - prior_g) / 2, 0.5, "fair\n80 %", ha="center", va="center", fontsize=13)
    # 2 Likelihood
    a = axs[1]
    a.add_patch(Rectangle((0, 0), prior_g, lk_g, color=VIOLETT, alpha=0.85))
    a.add_patch(Rectangle((0, lk_g), prior_g, 1 - lk_g, color=VIOLETT, alpha=0.18))
    a.add_patch(Rectangle((prior_g, 0), 1 - prior_g, lk_f, color=GRAU))
    a.add_patch(Rectangle((prior_g, lk_f), 1 - prior_g, 1 - lk_f, color=GRAU_HELL, alpha=0.5))
    a.text(prior_g / 2, lk_g / 2, "Kopf\n70 %", ha="center", va="center", color="white", fontsize=11)
    a.text(prior_g + (1 - prior_g) / 2, lk_f / 2, "Kopf: 50 %", ha="center", va="center", color="white",
           fontsize=13)
    a.text(prior_g + (1 - prior_g) / 2, lk_f + (1 - lk_f) / 2, "Zahl (ausgeschlossen)", ha="center",
           va="center", color=GRAU, fontsize=12)
    # 3 Posterior
    a = axs[2]
    fg = prior_g * lk_g
    ff = (1 - prior_g) * lk_f
    post = fg / (fg + ff)
    a.add_patch(Rectangle((0, 0), post, 1, color=VIOLETT, alpha=0.85))
    a.add_patch(Rectangle((post, 0), 1 - post, 1, color=GRAU))
    a.text(post / 2, 0.5, f"gezinkt\n{zahl(post * 100, 0)} %", ha="center", va="center", color="white",
           fontsize=12, fontweight="semibold")
    a.text(post + (1 - post) / 2, 0.5, f"fair\n{zahl((1 - post) * 100, 0)} %", ha="center", va="center",
           color="white", fontsize=13)
    fig.text(0.5, 0.0, f"P(gezinkt | Kopf) = 0,2 · 0,7 / (0,2 · 0,7 + 0,8 · 0,5) = 0,14 / 0,54 = {zahl(post, 2)}",
             ha="center", fontsize=14, color=TINTE)
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    speichern(fig, "f11_bayes_flaeche")


def f12_muenze_pfade():
    rng = np.random.default_rng(5)
    n = 80
    fig, ax = plt.subplots(figsize=(9, 4.2))
    for p_wahr, farbe, name in ((P_KOPF_GEZ, VIOLETT, "Münze ist in Wahrheit gezinkt"),
                                (0.5, CYAN, "Münze ist in Wahrheit fair")):
        for wdh in range(3):
            w = rng.random(n) < p_wahr
            post = [0.2]
            for kopf in w:
                lg = P_KOPF_GEZ if kopf else 1 - P_KOPF_GEZ
                lf = 0.5
                pg = post[-1] * lg / (post[-1] * lg + (1 - post[-1]) * lf)
                post.append(pg)
            ax.plot(range(n + 1), post, color=farbe, lw=2 if wdh == 0 else 1.1, alpha=1 if wdh == 0 else 0.55,
                    label=name if wdh == 0 else None)
    ax.axhline(0.2, color=GRAU, ls=":", lw=1)
    ax.text(n + 0.5, 0.2, "Prior 20 %", color=GRAU, va="center", fontsize=11)
    ax.set_ylim(0, 1)
    ax.set_xlim(0, n + 10)
    ax.set_ylim(0, 1.18)
    ax.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1])
    ax.yaxis.set_major_formatter(FuncFormatter(prozent))
    ax.set_xlabel("Anzahl Würfe")
    ax.set_ylabel("P(gezinkt | bisherige Würfe)")
    ax.legend(loc="upper left", fontsize=12, ncol=2)
    speichern(fig, "f12_muenze_pfade")


def f13_muenze_beta():
    p = np.linspace(0, 1, 801)
    fig, axs = plt.subplots(1, 2, figsize=(13, 4.2), gridspec_kw={"width_ratios": [1, 1.25]})
    ax = axs[0]
    for (k, n), farbe, lw in (((0, 0), GRAU, 1.6), ((6, 10), CYAN, 2), ((61, 100), VIOLETT, 2.6)):
        d = stats.beta.pdf(p, k + 1, n - k + 1)
        ax.plot(p, d, color=farbe, lw=lw, label="vorher (alles gleich plausibel)" if n == 0 else f"nach {k} × Kopf in {n} Würfen")
    ax.set_xlabel("Kopf-Wahrscheinlichkeit p der Münze (Hypothese)")
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    ax.legend(loc="upper left", fontsize=11)
    achsen_komma(ax, y=False)
    ax.set_title("Wissen wird schärfer", loc="left")
    ax = axs[1]
    a, b = 62, 40
    d = stats.beta.pdf(p, a, b)
    lo, hi = stats.beta.interval(0.95, a, b)
    ax.plot(p, d, color=VIOLETT, lw=2.6)
    ax.fill_between(p, d, where=p > 0.5, color=VIOLETT_HELL, lw=0)
    ax.axvline(0.5, color=GRAU, ls="--", lw=1.2)
    ax.text(0.505, d.max() * 1.02, "fair: p = 0,5", color=GRAU, fontsize=11)
    pg = stats.beta.sf(0.5, a, b)
    ax.text(0.63, d.max() * 0.45, f"P(p > 0,5 | Daten)\n= {zahl(pg * 100, 1)} %", color=VIOLETT, fontsize=14,
            fontweight="semibold")
    ax.annotate("", xy=(hi, d.max() * 0.08), xytext=(lo, d.max() * 0.08),
                arrowprops=dict(arrowstyle="<->", color=CYAN, lw=1.8))
    ax.text((lo + hi) / 2, d.max() * 0.13, f"95 % glaubwürdig: {zahl(lo)} bis {zahl(hi)}", color=CYAN,
            ha="center", fontsize=12)
    ax.set_xlim(0.35, 0.85)
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    ax.set_xlabel("Kopf-Wahrscheinlichkeit p")
    achsen_komma(ax, y=False)
    ax.set_title("Nach 61 × Kopf in 100 Würfen", loc="left")
    fig.tight_layout()
    speichern(fig, "f13_muenze_beta")


def f14_wuerfel_bayes():
    n, s = 60, 16
    ks = np.arange(0, 31)
    fig, axs = plt.subplots(1, 2, figsize=(13, 4.3))
    ax = axs[0]
    b = 0.42
    ax.bar(ks - b / 2, stats.binom.pmf(ks, n, 1 / 6), b, color=GRAU, label="fairer Würfel (P(6) = 1/6)")
    ax.bar(ks + b / 2, stats.binom.pmf(ks, n, 0.25), b, color=VIOLETT, label="gezinkter Würfel (P(6) = 1/4)")
    ax.axvline(s, color=TINTE, lw=1.4, ls="--")
    lf, lg = stats.binom.pmf(s, n, 1 / 6), stats.binom.pmf(s, n, 0.25)
    ax.text(20.5, 0.06, f"16 Sechsen:\nfair {zahl(lf * 100, 1)} %\ngezinkt {zahl(lg * 100, 1)} %\n"
            f"Bayes-Faktor {zahl(lg / lf, 1)}", fontsize=12, color=TINTE)
    ax.set_xlim(0, 30)
    ax.set_ylim(0, 0.19)
    ax.set_xlabel("Anzahl Sechsen in 60 Würfen")
    ax.set_ylabel("Wahrscheinlichkeit")
    ax.yaxis.set_major_formatter(FuncFormatter(prozent))
    ax.legend(loc="upper right", fontsize=11)
    ax.set_title("Likelihood: Wie gut erklärt jede Hypothese die Daten?", loc="left", fontsize=13)
    ax = axs[1]
    lr = lg / lf
    pr = np.linspace(0.001, 0.999, 400)
    po = pr * lr / (pr * lr + 1 - pr)
    ax.plot(pr, po, color=VIOLETT, lw=2.6)
    ax.plot(pr, pr, color=GRAU, ls=":", lw=1)
    for p0 in (0.05, 0.5):
        p1 = p0 * lr / (p0 * lr + 1 - p0)
        ax.plot([p0], [p1], "o", color=CYAN, ms=8)
        ax.annotate(f"Prior {zahl(p0 * 100, 0)} % → Posterior {zahl(p1 * 100, 0)} %", xy=(p0, p1),
                    xytext=(p0 + 0.08, p1 - 0.12), color=CYAN, fontsize=12,
                    arrowprops=dict(arrowstyle="-", color=CYAN))
    ax.xaxis.set_major_formatter(FuncFormatter(prozent))
    ax.yaxis.set_major_formatter(FuncFormatter(prozent))
    ax.set_xlabel("Prior: P(gezinkt) vor dem Würfeln")
    ax.set_ylabel("P(gezinkt | 16 Sechsen)")
    ax.set_title("Posterior hängt vom Vorwissen ab", loc="left", fontsize=13)
    fig.tight_layout()
    speichern(fig, "f14_wuerfel_bayes")


def f15_abfuell_bayes(x):
    mu = np.linspace(490, 510, 2001)
    dmu = mu[1] - mu[0]
    sigma = S_ABF
    post = np.ones_like(mu)
    post /= post.sum() * dmu
    schnapp = {0: None, 1: None, 3: None, 10: None, 20: None}
    for i in range(len(x) + 1):
        if i in schnapp:
            schnapp[i] = post.copy()
        if i < len(x):
            post = post * stats.norm.pdf(x[i], mu, sigma)
            post /= post.sum() * dmu
    fig, axs = plt.subplots(1, 2, figsize=(13, 4.3))
    ax = axs[0]
    farben = [GRAU, CYAN_HELL, CYAN, VIOLETT_HELL, VIOLETT]
    for (i, d), f in zip(schnapp.items(), farben):
        m = np.sum(mu * d) * dmu
        sd = np.sqrt(np.sum(mu**2 * d) * dmu - m**2)
        ax.plot(mu, d, color=f, lw=2.2, label=f"nach {i} Packungen: {zahl(m, 1)} ± {zahl(sd, 1)} g" if i else
                "vorher: 490 bis 510 g gleich plausibel")
    ax.plot(x, np.zeros_like(x) - 0.01, "|", color=TINTE, ms=12)
    ax.set_xlabel("wahrer Mittelwert μ der Anlage (Hypothese) in g")
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    ax.legend(loc="upper right", fontsize=10.5)
    ax.set_xlim(490, 510)
    ax.set_ylim(top=ax.get_ylim()[1] * 1.45)
    ax.set_title("Packung für Packung: Grid-Update", loc="left", fontsize=13)
    achsen_komma(ax, y=False)
    # rechts: Endergebnis mit Wahrscheinlichkeitsaussagen (t-Posterior, flacher Prior)
    ax = axs[1]
    se = S_ABF / np.sqrt(N_ABF)
    m = np.linspace(493, 506, 900)
    d = stats.t.pdf((m - XQ_ABF) / se, N_ABF - 1) / se
    ax.plot(m, d, color=VIOLETT, lw=2.6, label="flacher Prior")
    ax.fill_between(m, d, where=m < SOLL, color=VIOLETT_HELL, lw=0)
    ax.fill_between(m, d, where=m < 498, color=VIOLETT, alpha=0.45, lw=0)
    p500 = stats.t.cdf((SOLL - XQ_ABF) / se, N_ABF - 1)
    p498 = stats.t.cdf((498 - XQ_ABF) / se, N_ABF - 1)
    ax.axvline(SOLL, color=GRAU, ls="--", lw=1.2)
    ax.text(SOLL + 0.1, d.max() * 0.95, "Soll 500 g", color=GRAU, fontsize=11)
    ax.text(500.5, d.max() * 0.45, f"P(μ < 500 g | Daten) = {zahl(p500 * 100, 1)} %\n"
            f"P(μ < 498 g | Daten) = {zahl(p498 * 100, 0)} %", color=VIOLETT, fontsize=12, fontweight="semibold")
    ax.set_ylim(0, 0.75)
    # informativer Prior aus der Einrichtung: N(500; 1 g)
    tau = 1.0
    prec = 1 / tau**2 + N_ABF / S_ABF**2
    m_post = (SOLL / tau**2 + N_ABF * XQ_ABF / S_ABF**2) / prec
    sd_post = np.sqrt(1 / prec)
    ax.plot(m, stats.norm.pdf(m, m_post, sd_post), color=CYAN, lw=2, ls="--",
            label=f"Prior „eingestellt auf 500 ± 1 g“: P(μ < 500) = {zahl(stats.norm.cdf(SOLL, m_post, sd_post) * 100, 0)} %")
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    ax.set_xlabel("wahrer Mittelwert μ in g")
    ax.legend(loc="upper left", fontsize=10.5)
    ax.set_title("Aussage über die Hypothese", loc="left", fontsize=13)
    achsen_komma(ax, y=False)
    fig.tight_layout()
    speichern(fig, "f15_abfuell_bayes")
    return p500, p498, stats.norm.cdf(SOLL, m_post, sd_post), m_post, sd_post


def f16_vergleich():
    se = S_ABF / np.sqrt(N_ABF)
    fig, axs = plt.subplots(1, 2, figsize=(13, 4.2), sharex=True)
    m = np.linspace(492, 504.5, 800)
    ax = axs[0]
    d = stats.t.pdf((m - SOLL) / se, N_ABF - 1) / se
    ax.plot(m, d, color=GRAU, lw=2.2)
    ax.fill_between(m, d, where=m <= XQ_ABF, color=ROT_HELL, lw=0)
    ax.axvline(XQ_ABF, color=VIOLETT, lw=2.4)
    ax.text(XQ_ABF - 0.15, d.max() * 0.9, "unsere Daten\nx̄ = 497,8", ha="right", color=VIOLETT, fontsize=12)
    ax.text(SOLL + 1.3, d.max() * 0.75, "angenommen:\nμ = 500 g", color=GRAU, fontsize=12)
    ax.text(492.2, d.max() * 0.25, "p = 2,3 %", color=ROT, fontsize=15, fontweight="semibold")
    ax.set_title("Frequentistisch: P(Daten so extrem | H₀)", loc="left")
    ax.set_xlabel("möglicher Stichprobenmittelwert x̄  (die Daten variieren)")
    ax = axs[1]
    d = stats.t.pdf((m - XQ_ABF) / se, N_ABF - 1) / se
    ax.plot(m, d, color=VIOLETT, lw=2.4)
    ax.fill_between(m, d, where=m < SOLL, color=VIOLETT_HELL, lw=0)
    ax.axvline(SOLL, color=GRAU, ls="--", lw=1.4)
    ax.text(SOLL + 0.15, d.max() * 0.9, "Soll 500 g", color=GRAU, fontsize=12)
    ax.text(492.2, d.max() * 0.6, "P(μ < 500 | Daten)\n= 97,7 %", color=VIOLETT, fontsize=15,
            fontweight="semibold")
    ax.set_title("Bayesianisch: P(Hypothese | Daten)", loc="left")
    ax.set_xlabel("möglicher wahrer Mittelwert μ  (die Hypothese variiert)")
    for ax in axs:
        ax.set_yticks([])
        ax.spines["left"].set_visible(False)
        achsen_komma(ax, y=False)
    fig.tight_layout()
    speichern(fig, "f16_vergleich")


ORTE = ["Jacken-\ntasche", "Schlüssel-\nbrett", "Schreib-\ntisch", "Auto", "Küche", "ganz\nwoanders"]
PRIOR_ORT = np.array([0.35, 0.25, 0.15, 0.10, 0.10, 0.05])
FUND_ORT = np.array([0.90, 0.99, 0.60, 0.70, 0.80, 0.10])   # P(finde ihn | er ist dort, ich suche dort)


def schluessel_update(prior, ort):
    post = prior.copy()
    post[ort] *= 1 - FUND_ORT[ort]
    return post / post.sum()


def f17_schluessel():
    schritte = [("Vorher (Gewohnheit)", PRIOR_ORT, None)]
    p1 = schluessel_update(PRIOR_ORT, 0)
    schritte.append(("Jackentasche: nicht gefunden", p1, 0))
    p2 = schluessel_update(p1, 1)
    schritte.append(("Schlüsselbrett: nicht gefunden", p2, 1))
    fig, axs = plt.subplots(1, 3, figsize=(13, 4.3), sharey=True)
    x = np.arange(len(ORTE))
    for ax, (titel, p, gesucht) in zip(axs, schritte):
        farben = [VIOLETT] * len(ORTE)
        nutzen = p * FUND_ORT
        farben[int(np.argmax(nutzen))] = CYAN
        if gesucht is not None:
            farben[gesucht] = GRAU_HELL
        ax.bar(x, p, color=farben)
        for xi, pi in zip(x, p):
            ax.text(xi, pi + 0.01, f"{pi * 100:.0f} %", ha="center", fontsize=11)
        ax.set_xticks(x)
        ax.set_xticklabels(ORTE, fontsize=9.5)
        ax.set_title(titel, loc="left", fontsize=13)
        ax.yaxis.set_major_formatter(FuncFormatter(prozent))
    axs[0].set_ylabel("P(Schlüssel ist dort)")
    fig.text(0.5, -0.02, "Cyan: dort lohnt das Suchen als Nächstes am meisten "
             "(Wahrscheinlichkeit × Chance, ihn dort beim Suchen auch zu entdecken).", ha="center",
             color=GRAU, fontsize=12)
    fig.tight_layout()
    speichern(fig, "f17_schluessel")
    return p1, p2


def f18_quelle():
    fig, axs = plt.subplots(1, 2, figsize=(13, 4.3), gridspec_kw={"width_ratios": [1, 1.1]})
    ax = axs[0]
    pr = np.linspace(0.001, 0.999, 400)
    for lr, f, name in ((1, GRAU, "BF 1: Quelle sagt nichts"), (2, CYAN_HELL, "BF 2: Boulevard, Forum"),
                        (4, CYAN, "BF 4: seriöse Zeitung"), (20, VIOLETT, "BF 20: Fachstudie, repliziert")):
        ax.plot(pr, pr * lr / (pr * lr + 1 - pr), color=f, lw=2.3, label=name)
    ax.xaxis.set_major_formatter(FuncFormatter(prozent))
    ax.yaxis.set_major_formatter(FuncFormatter(prozent))
    ax.set_xlabel("Prior: Wie plausibel war die Behauptung vorher?")
    ax.set_ylabel("Posterior: nachdem die Quelle sie bestätigt")
    ax.legend(loc="lower right", fontsize=11)
    ax.set_title("Eine Quelle bewegt den Glauben – je nach Qualität", loc="left", fontsize=13)
    ax = axs[1]
    prior = 0.3
    odds = prior / (1 - prior)
    stufen = [("Vorher", odds), ("+ Quelle A\n(BF 4)", odds * 4), ("+ Quelle B,\nunabhängig (BF 4)", odds * 16),
              ("statt dessen: B hat\nvon A abgeschrieben", odds * 4)]
    werte = [o / (1 + o) for _, o in stufen]
    farben = [GRAU, CYAN, VIOLETT, ROT_HELL]
    ax.bar(range(4), werte, color=farben, width=0.65)
    for i, w in enumerate(werte):
        ax.text(i, w + 0.02, f"{w * 100:.0f} %", ha="center", fontsize=13, fontweight="semibold")
    ax.set_xticks(range(4))
    ax.set_xticklabels([s for s, _ in stufen], fontsize=10)
    ax.set_ylim(0, 1.05)
    ax.yaxis.set_major_formatter(FuncFormatter(prozent))
    ax.set_ylabel("P(Behauptung stimmt)")
    ax.set_title("Zwei Quellen sind nur zwei Belege, wenn sie unabhängig sind", loc="left", fontsize=13)
    fig.tight_layout()
    speichern(fig, "f18_quelle")


def main():
    print("Grafiken:")
    f01_wuerfel()
    f02_zgs()
    f03_se_ablesen()
    f04_wurzel_n()
    f05_test_wuerfel()
    f06_t_vs_z()
    f07_muenze_test()
    x = abfuelldaten()
    with open(os.path.join(DATEN, "abfuellung.csv"), "w") as fh:
        fh.write("packung,gewicht_g\n")
        for i, v in enumerate(x, 1):
            fh.write(f"{i},{v:.1f}\n")
    print(f"  material/LE06/abfuellung.csv: x̄ = {x.mean():.2f}, s = {x.std(ddof=1):.2f}")
    t, p = stats.ttest_1samp(x, SOLL, alternative="less")
    print(f"  t-Test (einseitig) mit den Daten: t = {t:.3f}, p = {p:.4f}")
    f08_abfuell_daten(x)
    f09_abfuell_test()
    anteil = f10_welten()
    print(f"  Simulation: Anteil t <= t_beob = {anteil:.4f}")
    f11_bayes_flaeche()
    f12_muenze_pfade()
    f13_muenze_beta()
    f14_wuerfel_bayes()
    print("  Abfüllung Bayes (P<500, P<498, P<500 mit Prior, m_post, sd_post):", f15_abfuell_bayes(x))
    f16_vergleich()
    print("  Schlüssel:", [np.round(p, 3) for p in f17_schluessel()])
    f18_quelle()


if __name__ == "__main__":
    main()
