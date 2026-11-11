#!/usr/bin/env python3
"""Erzeugt die Grafiken zu LE 6 (Statistik) als PDF in figures/.

Alle Simulationen haben feste Startwerte, die Grafiken sind also bei jedem
Lauf gleich. Aufruf (System-Python mit numpy, scipy, matplotlib):

    python3 tools/le06_figuren.py

Farben: RWU-Violett und RWU-Cyan (dunkel fuer Linien, hell fuer Flaechen),
Grau fuer Bezugslinien. Schrift: Barlow Semi Condensed aus fonts/.
"""
import glob, os
import numpy as np
from scipy import stats
import matplotlib
matplotlib.use("pdf")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.ticker import FuncFormatter

HIER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HIER, "figures")

for f in glob.glob(os.path.join(HIER, "fonts", "*.otf")):
    font_manager.fontManager.addfont(f)

VIOLETT = "#6638B6"
VIOLETT_HELL = "#C9B8E8"
CYAN = "#007F9A"        # Linien, Text-tauglich auf Weiss
CYAN_HELL = "#99DDFD"   # rwucyan40, nur Flaechen
GRAU = "#737373"
GRAU_HELL = "#D9D9D9"
TINTE = "#222222"

plt.rcParams.update({
    "font.family": "Barlow Semi Condensed",
    "font.size": 11,
    "axes.titlesize": 11,
    "axes.labelsize": 11,
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
    "pdf.fonttype": 3,
})

# Dezimalkomma auf allen Achsen
def komma(x, _pos=None):
    s = f"{x:g}"
    return s.replace(".", ",").replace("-", "−")
KOMMA = FuncFormatter(komma)

def achsen(ax):
    ax.xaxis.set_major_formatter(KOMMA)
    ax.yaxis.set_major_formatter(KOMMA)
    ax.grid(axis="y", color=GRAU_HELL, linewidth=0.6)
    ax.set_axisbelow(True)

def speichern(fig, name):
    fig.savefig(os.path.join(OUT, name), bbox_inches="tight")
    plt.close(fig)
    print("geschrieben:", name)

def pct(x, stellen=0):
    return f"{100*x:.{stellen}f}".replace(".", ",") + " %"

rng = np.random.default_rng(2026)

# ---------------------------------------------------------------------------
# 1  Standardabweichung vs. Standardfehler (Wuerfel)
# ---------------------------------------------------------------------------
def sd_se():
    sigma = np.sqrt(35 / 12)  # SD eines Wuerfelwurfs, 1,71
    fig, (a, b) = plt.subplots(1, 2, figsize=(7.8, 3.3), gridspec_kw={"width_ratios": [1.5, 1], "wspace": 0.55})
    for n, farbe, y in [(1, GRAU, 2), (5, CYAN, 1), (30, VIOLETT, 0)]:
        mittel = rng.integers(1, 7, size=(400, n)).mean(axis=1)
        jitter = y + rng.uniform(-0.28, 0.28, size=mittel.size)
        a.scatter(mittel, jitter, s=6, color=farbe, alpha=0.45, linewidths=0)
        se = sigma / np.sqrt(n)
        a.plot([3.5 - 2 * se, 3.5 + 2 * se], [y + 0.42] * 2, color=farbe, lw=2, solid_capstyle="round")
        txt = "einzelne Würfe" if n == 1 else f"Mittel aus {n} Würfen"
        a.text(7.2, y, txt, va="center", ha="left", color=TINTE, fontsize=10, clip_on=False)
    a.set_yticks([])
    a.spines["left"].set_visible(False)
    a.set_xlim(0.0, 7.0)
    a.set_xticks(range(1, 7))
    a.set_xlabel("Augenzahl bzw. Mittelwert  (Strich: ± 2 Standardfehler)")
    a.set_title("Je 400 Stichproben", loc="left")
    a.xaxis.set_major_formatter(KOMMA)

    ns = np.arange(1, 51)
    b.axhline(sigma, color=GRAU, lw=2)
    b.plot(ns, sigma / np.sqrt(ns), color=VIOLETT, lw=2)
    b.text(50, sigma + 0.08, "Standardabweichung $s$ = 1,71", ha="right", va="bottom", color=TINTE, fontsize=10)
    b.text(18, 0.62, "Standardfehler $s/\\sqrt{n}$", ha="left", color=TINTE, fontsize=10)
    for n in (5, 30):
        b.plot(n, sigma / np.sqrt(n), "o", color=VIOLETT, ms=6, mec="white", mew=1.5)
        b.annotate(komma(round(sigma / np.sqrt(n), 2)), (n, sigma / np.sqrt(n)),
                   xytext=(5, 4), textcoords="offset points", fontsize=9, color=TINTE)
    b.set_ylim(0, 2.1)
    b.set_xlabel("Stichprobengröße $n$")
    b.set_title("Was mit wachsendem $n$ passiert", loc="left")
    achsen(b)
    speichern(fig, "LE06_sd_se.pdf")

# ---------------------------------------------------------------------------
# 2  Zentraler Grenzwertsatz
# ---------------------------------------------------------------------------
def zgs():
    ns = [1, 2, 5, 30]
    fig, axs = plt.subplots(2, 4, figsize=(7.8, 4.3), sharey="row")
    fig.subplots_adjust(left=0.02, right=0.98, top=0.84, bottom=0.07, hspace=0.95, wspace=0.18)
    reps = 20000
    for i, n in enumerate(ns):
        # oben: Wuerfel
        m = rng.integers(1, 7, size=(reps, n)).mean(axis=1)
        ax = axs[0, i]
        werte, zahl = np.unique(m, return_counts=True)
        breite = 0.8 / n if n < 5 else None
        if n < 5:
            ax.bar(werte, zahl / reps, width=breite, color=VIOLETT, edgecolor="white", linewidth=0.5)
        else:
            ax.hist(m, bins=np.arange(0.95, 6.1, 0.1 if n == 30 else 0.2), density=False,
                    weights=np.full(reps, 1 / reps), color=VIOLETT, edgecolor="white", linewidth=0.4)
        ax.set_xlim(0.5, 6.5)
        ax.set_xticks([1, 3.5, 6])
        ax.set_title(f"$n$ = {n}", loc="left")
        # unten: schiefe Verteilung (Exponential, Mittel 30 wie ein Pendelausschlag in mm)
        e = rng.exponential(30, size=(reps, n)).mean(axis=1)
        ax2 = axs[1, i]
        ax2.hist(e, bins=np.linspace(0, 120, 49), weights=np.full(reps, 1 / reps),
                 color=CYAN_HELL, edgecolor="white", linewidth=0.4)
        if n >= 5:
            x = np.linspace(0, 120, 300)
            se = 30 / np.sqrt(n)
            ax2.plot(x, stats.norm.pdf(x, 30, se) * 2.5, color=CYAN, lw=1.8)
        ax2.set_xlim(0, 120)
        ax2.set_xticks([0, 30, 60, 120])
        for a in (ax, ax2):
            a.yaxis.set_visible(False)
            a.spines["left"].set_visible(False)
            a.xaxis.set_major_formatter(KOMMA)
    fig.text(0.02, 0.97, "Mittelwert aus $n$ Würfelwürfen (Grundverteilung: gleichmäßig)",
             fontsize=10.5, color=TINTE, fontweight="semibold", va="top")
    fig.text(0.02, 0.47, "Mittelwert aus $n$ Messungen einer schiefen Verteilung (Mittel 30, z. B. Ausschlag in mm)",
             fontsize=10.5, color=TINTE, fontweight="semibold", va="top")
    axs[1, 3].text(0.98, 0.95, "Linie: Normalverteilung", transform=axs[1, 3].transAxes,
                   ha="right", va="top", fontsize=9, color=CYAN)
    speichern(fig, "LE06_zgs.pdf")

# ---------------------------------------------------------------------------
# 3  Kurs-Pool: Binomialverteilung unter H0 und H1
# ---------------------------------------------------------------------------
def kurspool():
    n, k = 150, 97
    x = np.arange(50, 126)
    p0 = stats.binom.pmf(x, n, 0.5)
    p1 = stats.binom.pmf(x, n, 2 / 3)
    fig, ax = plt.subplots(figsize=(7.8, 3.2))
    ax.bar(x, p0, width=0.8, color=VIOLETT, linewidth=0)
    ax.plot(x, p1, color=CYAN, lw=2, drawstyle="steps-mid")
    ax.axvline(k, color=TINTE, lw=1.2, ls=(0, (3, 2)))
    ax.text(k - 1, p0.max() * 1.22, "Kurs: 97 Gewinne", color=TINTE, fontsize=10, va="bottom", ha="right")
    ax.text(75, p0.max() * 1.04, "wenn $H_0$ stimmt\n(Chance 1/2): um 75", ha="center", va="bottom",
            color=VIOLETT, fontsize=10)
    ax.text(112, p1.max() * 0.9, "wenn Wechseln 2/3 bringt:\num 100", ha="left", va="bottom",
            color=CYAN, fontsize=10)
    pval = 2 * stats.binom.sf(k - 1, n, 0.5)
    ax.annotate(f"rechts von 97 fast keine violette Fläche:\np-Wert ≈ {komma(round(pval, 4))} (zweiseitig)",
                xy=(92, stats.binom.pmf(92, n, .5)), xytext=(104, p0.max() * 0.45),
                fontsize=9.5, color=TINTE, arrowprops=dict(arrowstyle="-", color=GRAU, lw=0.8))
    ax.set_xlabel("Zahl der Gewinne in 150 Wechselrunden")
    ax.set_ylabel("Wahrscheinlichkeit")
    ax.set_ylim(0, p0.max() * 1.4)
    achsen(ax)
    fig.tight_layout()
    speichern(fig, "LE06_kurspool.pdf")

# ---------------------------------------------------------------------------
# 4  Was "95 % Konfidenz" heisst: 40 simulierte Intervalle
# ---------------------------------------------------------------------------
def konfidenz():
    n, p = 150, 2 / 3
    r = np.random.default_rng(7)
    fig, ax = plt.subplots(figsize=(7.8, 3.3))
    treffer = 0
    for i in range(40):
        k = r.binomial(n, p)
        ph = k / n
        se = np.sqrt(ph * (1 - ph) / n)
        lo, hi = ph - 1.96 * se, ph + 1.96 * se
        ok = lo <= p <= hi
        treffer += ok
        farbe = VIOLETT if ok else CYAN
        ax.plot([i, i], [lo, hi], color=farbe, lw=2.2 if not ok else 1.6, solid_capstyle="round")
        ax.plot(i, ph, "o", color=farbe, ms=3.5)
    ax.axhline(p, color=GRAU, lw=1.2)
    ax.text(40.5, p, "wahre\nQuote 2/3", va="center", fontsize=10, color=TINTE)
    ax.set_xlim(-1, 45)
    ax.set_xlabel("40 Kurse, jeder spielt 150 Wechselrunden")
    ax.set_ylabel("Gewinnquote mit 95-%-Intervall")
    ax.set_xticks([])
    ax.set_title(f"{treffer} von 40 Intervallen enthalten den wahren Wert (violett), {40-treffer} nicht (cyan)", loc="left")
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _p: pct(v)))
    ax.grid(axis="y", color=GRAU_HELL, linewidth=0.6)
    ax.set_axisbelow(True)
    fig.tight_layout()
    speichern(fig, "LE06_konfidenz.pdf")

# ---------------------------------------------------------------------------
# 5  Zwei Arten, sich zu irren: alpha, beta, Power
# ---------------------------------------------------------------------------
def fehlerarten():
    d, n = 0.5, 20
    delta = d * np.sqrt(n / 2)
    krit = 1.96
    x = np.linspace(-3.5, 6, 600)
    f0, f1 = stats.norm.pdf(x), stats.norm.pdf(x, delta)
    fig, ax = plt.subplots(figsize=(7.8, 3.1))
    ax.plot(x, f0, color=VIOLETT, lw=2)
    ax.plot(x, f1, color=CYAN, lw=2)
    ax.fill_between(x, f0, where=x >= krit, color=VIOLETT, alpha=0.55, linewidth=0)
    ax.fill_between(x, f1, where=x < krit, color=CYAN_HELL, alpha=0.8, linewidth=0)
    ax.fill_between(x, f1, where=x >= krit, color=CYAN, alpha=0.35, linewidth=0)
    ax.axvline(krit, color=TINTE, lw=1.2, ls=(0, (3, 2)))
    power = stats.norm.sf(krit - delta)
    ax.text(-0.9, 0.43, "$H_0$ stimmt\n(kein Effekt)", ha="center", color=VIOLETT, fontsize=10)
    ax.text(delta + 1.0, 0.43, f"$H_1$ stimmt\n($d$ = 0,5; je {n} Personen)", ha="left", color=CYAN, fontsize=10)
    ax.text(krit, 0.485, "kritischer Wert", fontsize=9.5, color=TINTE, ha="center")
    ax.annotate("$\\alpha$ = 5 %: falscher Alarm", xy=(2.25, 0.015), xytext=(3.9, 0.07),
                fontsize=9.5, color=TINTE, arrowprops=dict(arrowstyle="-", color=GRAU, lw=0.8))
    ax.annotate(f"$\\beta$ = {pct(1-power)}: übersehen", xy=(1.0, 0.12), xytext=(-3.4, 0.2),
                fontsize=9.5, color=TINTE, arrowprops=dict(arrowstyle="-", color=GRAU, lw=0.8))
    ax.annotate(f"Power = {pct(power)}: gefunden", xy=(2.7, 0.2), xytext=(3.9, 0.25),
                fontsize=9.5, color=TINTE, arrowprops=dict(arrowstyle="-", color=GRAU, lw=0.8))
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    ax.set_xlabel("Teststatistik (z. B. $t$)")
    ax.set_ylim(0, 0.52)
    ax.xaxis.set_major_formatter(KOMMA)
    fig.tight_layout()
    speichern(fig, "LE06_fehlerarten.pdf")

# ---------------------------------------------------------------------------
# 6  Wuerfel-Detektive: Treffer bei fairem und gezinktem Wuerfel
# ---------------------------------------------------------------------------
def wuerfel_verteilungen():
    n = 30
    k = np.arange(0, 21)
    f = stats.binom.pmf(k, n, 1 / 6)
    g = stats.binom.pmf(k, n, 1 / 3)
    fig, ax = plt.subplots(figsize=(7.8, 3.1))
    w = 0.4
    ax.bar(k - w / 2, f, width=w, color=[VIOLETT if v >= 10 else VIOLETT_HELL for v in k], linewidth=0, label="fair: Treffer nur bei 6")
    ax.bar(k + w / 2, g, width=w, color=[CYAN if v >= 10 else CYAN_HELL for v in k], linewidth=0, label="gezinkt: Treffer bei 5 und 6")
    ax.axvline(9.5, color=TINTE, lw=1.2, ls=(0, (3, 2)))
    ax.text(9.7, f.max() * 1.03, "ab 10 Treffern: „signifikant“", fontsize=10, color=TINTE)
    ax.text(15.2, 0.10, f"gezinkt erkannt: {pct(stats.binom.sf(9, n, 1/3))}", fontsize=9.5, color=CYAN)
    ax.text(15.2, 0.083, f"fair, aber Alarm: {pct(stats.binom.sf(9, n, 1/6), 1)}", fontsize=9.5, color=VIOLETT)
    ax.set_xticks(range(0, 21, 2))
    ax.set_xlabel("Treffer in 30 Würfen")
    ax.set_ylabel("Wahrscheinlichkeit")
    ax.legend(loc="upper right")
    ax.set_ylim(0, f.max() * 1.18)
    achsen(ax)
    fig.tight_layout()
    speichern(fig, "LE06_wuerfel_verteilungen.pdf")

# ---------------------------------------------------------------------------
# 7  Posterior wandert mit den Daten: P(gezinkt) nach jedem Wurf
# ---------------------------------------------------------------------------
def posterior_pfade():
    r = np.random.default_rng(11)
    fig, ax = plt.subplots(figsize=(7.8, 3.3))
    prior = 1 / 4
    for p, farbe in [(1 / 6, VIOLETT), (1 / 3, CYAN)]:
        for j in range(5):
            treffer = r.random(30) < p
            fak = np.where(treffer, 2.0, 0.8)
            chance = prior * np.concatenate([[1], np.cumprod(fak)])
            post = chance / (1 + chance)
            ax.plot(range(31), post, color=farbe, lw=1.6, alpha=0.9, drawstyle="steps-post")
    ax.axhline(0.2, color=GRAU, lw=1, ls=(0, (1, 2)))
    ax.axhline(0.5, color=GRAU, lw=1)
    ax.text(30.4, 0.2, "Basisrate 20 %", va="center", fontsize=9.5, color=TINTE)
    ax.text(30.4, 0.5, "50 %", va="center", fontsize=9.5, color=TINTE)
    ax.text(1, 0.93, "gezinkte Würfel (cyan)", color=CYAN, fontsize=10)
    ax.text(1, 0.84, "faire Würfel (violett)", color=VIOLETT, fontsize=10)
    ax.set_title("Je 5 simulierte Würfel; Treffer: Chance ×2, kein Treffer: Chance ×0,8", loc="left")
    ax.set_xlim(0, 30)
    ax.set_ylim(0, 1)
    ax.set_xlabel("Zahl der Würfe")
    ax.set_ylabel("$P$(gezinkt)")
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _p: pct(v)))
    ax.xaxis.set_major_formatter(KOMMA)
    ax.grid(axis="y", color=GRAU_HELL, linewidth=0.6)
    ax.set_axisbelow(True)
    fig.tight_layout()
    speichern(fig, "LE06_posterior_pfade.pdf")

# ---------------------------------------------------------------------------
# 8  Posterior fuer eine Quote: Wie oft gewinnt Wechseln?
# ---------------------------------------------------------------------------
def posterior_quote():
    x = np.linspace(0, 1, 500)
    stufen = [(0, 0, "vorher: alles gleich plausibel"), (4, 6, "nach 6 Runden (4 gewonnen)"),
              (16, 24, "nach 24 Runden (16 gewonnen)"), (100, 150, "nach 150 Runden (100 gewonnen)")]
    farben = ["#C9B8E8", "#A487D6", "#8560C6", VIOLETT]
    fig, ax = plt.subplots(figsize=(7.8, 3.3))
    for (k, n, txt), farbe in zip(stufen, farben):
        dens = stats.beta.pdf(x, 1 + k, 1 + n - k)
        ax.plot(x, dens, color=farbe, lw=2)
        i = np.argmax(dens) if n > 0 else 20
        lo, hi = stats.beta.ppf([0.025, 0.975], 1 + k, 1 + n - k)
        lab = txt if n == 0 else f"{txt}\n95 %: {pct(lo)} bis {pct(hi)}"
        if n == 0:
            ax.text(0.03, 1.15, lab, fontsize=9.5, color=TINTE)
        else:
            xt = {6: 0.22, 24: 0.86, 150: 0.86}[n]
            yt = {6: 2.6, 24: 4.6, 150: 9.0}[n]
            ax.annotate(lab, xy=(x[i] + (0.03 if n != 6 else -0.05), dens[i] * 0.75), xytext=(xt, yt),
                        fontsize=9.5, color=TINTE, ha="left" if n != 6 else "right",
                        arrowprops=dict(arrowstyle="-", color=GRAU, lw=0.8))
    ax.axvline(0.5, color=GRAU, lw=1, ls=(0, (1, 2)))
    ax.text(0.5, 10.6, "1/2", ha="center", fontsize=10, color=GRAU)
    ax.axvline(2 / 3, color=GRAU, lw=1, ls=(0, (1, 2)))
    ax.text(2 / 3, 10.6, "2/3", ha="center", fontsize=10, color=GRAU)
    ax.set_xlabel("Gewinnquote beim Wechseln")
    ax.set_ylabel("Glaubwürdigkeit (Dichte)")
    ax.set_yticks([])
    ax.set_ylim(0, 11.2)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _p: pct(v)))
    fig.tight_layout()
    speichern(fig, "LE06_posterior_quote.pdf")


if __name__ == "__main__":
    sd_se()
    zgs()
    kurspool()
    konfidenz()
    fehlerarten()
    wuerfel_verteilungen()
    posterior_pfade()
    posterior_quote()
