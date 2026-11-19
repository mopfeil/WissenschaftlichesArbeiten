#!/usr/bin/env python3
"""Erzeugt das Colab-Notebook material/LE06/ZGS_Test_Bayes.ipynb (LE 6, ipywidgets).

    python3 tools/le06_live_notebook.py
"""
import json
import os

HIER = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ZIEL = os.path.join(HIER, "material", "LE06", "ZGS_Test_Bayes.ipynb")

zellen = []


def md(text):
    zellen.append({"cell_type": "markdown", "metadata": {}, "source": text.strip("\n")})


def code(text):
    zellen.append({"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [],
                   "source": text.strip("\n")})


md("""
# Vom Würfel zum Test – und zurück mit Bayes

Interaktive Begleitung zum Foliensatz **ZGS_Test_Bayes.pptx**. Jede Zelle ausführen
(Umschalt + Enter) und dann an den Schiebereglern drehen.

| Abschnitt | Thema |
|---|---|
| 1 | Zentraler Grenzwertsatz mit fairem und gezinktem Würfel |
| 2 | Standardfehler ablesen, √n-Gesetz |
| 3 | t-Test an der Abfüllanlage (mit Eichrecht) |
| 4 | Was der p-Wert sagt: Simulation vieler Stichproben |
| 5 | Bayes mit der Münze |
| 6 | Bayes mit dem Würfel: Prior und Bayes-Faktor |
| 7 | Bayes-Schätzung des Mittelwerts (Abfüllanlage) |
| 8 | Wo ist mein Schlüssel? |
| 9 | Glaube ich dieser Quelle? |
| 10 | Den Diamanten durchrechnen: welche Spitze bewegt was? |
""")

code("""
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import ipywidgets as widgets
from ipywidgets import interact, fixed
from IPython.display import display, clear_output

plt.rcParams.update({'figure.figsize': (10, 4.5), 'figure.dpi': 110,
                     'axes.spines.top': False, 'axes.spines.right': False})
VIOLETT, VIOLETT_HELL, CYAN, CYAN_HELL = '#6638B6', '#C9B8E8', '#007F9A', '#99DDFD'
ROT, ROT_HELL, GRAU, GRAU_HELL = '#C0392B', '#F2B8B0', '#737373', '#D9D9D9'

AUGEN = np.arange(1, 7)
WUERFEL = {'fair': np.full(6, 1/6),
           'gezinkt (Sechs 25 %)': np.array([.15, .15, .15, .15, .15, .25])}

# Die 20 Packungsgewichte der Abfüllanlage (identisch mit material/LE06/abfuellung.csv)
abfuellung = np.array([499.7, 501.4, 498.0, 494.4, 497.0, 493.8, 500.0, 507.5, 496.8, 496.0,
                       502.5, 501.8, 500.3, 494.2, 499.5, 503.8, 491.7, 497.0, 488.5, 492.1])
print('bereit')
""")

md("""
## 1  Zentraler Grenzwertsatz

Wir ziehen viele Stichproben aus *n* Würfen und tragen jeweils den Mittelwert ein.
Die Kurve ist die Vorhersage des ZGS: Normalverteilung mit Mitte μ und Breite σ/√n.

**Ausprobieren:** n = 1, 2, 5, 30. Was passiert mit Form und Breite? Ab welchem n
kann man fairen und gezinkten Würfel auseinanderhalten?
""")

code("""
def zgs(n=5, wuerfel='fair', stichproben=2000, vergleich=False):
    rng = np.random.default_rng()
    fig, ax = plt.subplots()
    for name, farbe, hell in ((wuerfel, VIOLETT, VIOLETT_HELL),
                              ('fair' if wuerfel != 'fair' else 'gezinkt (Sechs 25 %)', CYAN, CYAN_HELL)):
        if name != wuerfel and not vergleich:
            continue
        p = WUERFEL[name]
        mu = AUGEN @ p
        sigma = np.sqrt(AUGEN**2 @ p - mu**2)
        se = sigma / np.sqrt(n)
        m = rng.choice(AUGEN, size=(stichproben, n), p=p).mean(axis=1)
        kanten = np.arange(0.9, 6.15, 0.2) if n < 30 else np.arange(0.95, 6.1, 0.1)
        ax.hist(m, bins=kanten, density=True, color=hell, alpha=0.75, label=f'{name}: Mittelwerte')
        if n > 1:
            x = np.linspace(1, 6, 400)
            ax.plot(x, stats.norm.pdf(x, mu, se), color=farbe, lw=2.4,
                    label=f'ZGS: N({mu:.2f}; SE = {se:.3f})')
        print(f'{name:22s} μ = {mu:.3f}  σ = {sigma:.3f}  SE = σ/√n = {se:.3f}   '
              f'Streuung der simulierten Mittelwerte: {m.std(ddof=1):.3f}')
    ax.set_xlim(0.8, 6.2)
    ax.set_xlabel('Mittelwert x̄ einer Stichprobe')
    ax.set_yticks([])
    ax.legend(loc='upper left')
    ax.set_title(f'{stichproben} Stichproben zu je n = {n} Würfen')
    plt.show()

interact(zgs, n=widgets.IntSlider(value=5, min=1, max=100, step=1),
         wuerfel=list(WUERFEL), stichproben=widgets.IntSlider(value=2000, min=100, max=20000, step=100),
         vergleich=widgets.Checkbox(value=False, description='beide Würfel'));
""")

md("""
## 2  Standardfehler ablesen

Der Standardfehler ist die Breite der Glocke: vom Gipfel bis zum Wendepunkt.
±1 SE enthält 68 %, ±2 SE 95 % aller Mittelwerte. Für den halben Fehler braucht man vier Mal so viele Würfe.
""")

code("""
def se_ablesen(n=30, sigma=1.71, mu=3.5):
    se = sigma / np.sqrt(n)
    x = np.linspace(mu - 4*se, mu + 4*se, 600)
    y = stats.norm.pdf(x, mu, se)
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(12, 4.2), gridspec_kw={'width_ratios': [1.4, 1]})
    ax.fill_between(x, y, where=abs(x-mu) <= 2*se, color=CYAN_HELL, alpha=.5)
    ax.fill_between(x, y, where=abs(x-mu) <= se, color=CYAN_HELL)
    ax.plot(x, y, color=CYAN, lw=2.4)
    yw = stats.norm.pdf(mu + se, mu, se)
    ax.annotate('', xy=(mu+se, yw), xytext=(mu, yw), arrowprops=dict(arrowstyle='<->', color=VIOLETT, lw=2))
    ax.text(mu + se, yw*1.1, f'  1 SE = {se:.3f}', color=VIOLETT, fontsize=13)
    ax.set_xticks([mu + k*se for k in range(-3, 4)])
    ax.set_xticklabels([f'{mu + k*se:.2f}' for k in range(-3, 4)])
    ax.set_yticks([])
    ax.set_title(f'SE = σ/√n = {sigma}/√{n} = {se:.3f};   95 %: {mu-1.96*se:.2f} bis {mu+1.96*se:.2f}')
    nn = np.arange(1, 401)
    ax2.plot(nn, sigma/np.sqrt(nn), color=VIOLETT, lw=2)
    ax2.plot(n, se, 'o', color=CYAN, ms=9)
    ax2.set_xlabel('n'); ax2.set_ylabel('SE'); ax2.set_title('√n-Gesetz')
    plt.tight_layout(); plt.show()

interact(se_ablesen, n=widgets.IntSlider(value=30, min=1, max=400),
         sigma=widgets.FloatSlider(value=1.71, min=0.1, max=10, step=0.01),
         mu=widgets.FloatSlider(value=3.5, min=0, max=10, step=0.05));
""")

md("""
## 3  t-Test an der Abfüllanlage

Sollwert 500 g. Qualitätskontrolle wiegt 20 Packungen. Füllt die Anlage zu wenig ab?
(H₀: μ = 500 g, H₁: μ < 500 g, einseitig)

Das Eichrecht (Fertigpackungsverordnung, Anlage 3) prüft den Mittelwert mit
x̄ ≥ 500 g − k·s, für n = 20 ist k = 0,640 = t(0,995; 19)/√20 – also ein einseitiger t-Test mit α = 0,5 %.
""")

code("""
x = abfuellung
n, xq, s = len(x), x.mean(), x.std(ddof=1)
se = s / np.sqrt(n)
t, p = stats.ttest_1samp(x, popmean=500, alternative='less')
k = stats.t.ppf(0.995, n-1) / np.sqrt(n)
print(f'n = {n},  x̄ = {xq:.2f} g,  s = {s:.2f} g,  SE = s/√n = {se:.3f} g')
print(f't = ({xq:.2f} − 500) / {se:.3f} = {t:.3f}   (df = {n-1})')
print(f'p (einseitig) = {p:.4f}')
print(f'Eichrecht: k = {k:.3f},  Grenze 500 − k·s = {500 - k*s:.2f} g  → '
      f'{"beanstandet" if xq < 500 - k*s else "nicht beanstandet"}')
""")

md("""
**Interaktiv im Datenraum:** Verschieben Sie Mittelwert, Streuung, Stichprobenumfang und α.
Wann schlägt die interne Qualitätssicherung Alarm, wann das Eichamt?
""")

code("""
def abfuell_test(xq=497.8, s=4.6, n=20, alpha=0.05):
    se = s / np.sqrt(n)
    t = (xq - 500) / se
    p = stats.t.cdf(t, n-1)
    grenze = 500 + stats.t.ppf(alpha, n-1) * se
    eich = 500 - stats.t.ppf(0.995, n-1) / np.sqrt(n) * s
    m = np.linspace(500 - 5*se, 500 + 4*se, 800)
    d = stats.t.pdf((m - 500)/se, n-1) / se
    fig, ax = plt.subplots()
    ax.plot(m, d, color=GRAU, lw=2); ax.fill_between(m, d, color=GRAU_HELL, alpha=.5)
    ax.fill_between(m, d, where=m <= xq, color=ROT_HELL)
    ax.axvline(xq, color=VIOLETT, lw=2.6, label=f'x̄ = {xq:.1f} g')
    ax.axvline(grenze, color=CYAN, ls='--', label=f'Grenze α = {alpha:.3f}: {grenze:.2f} g')
    ax.axvline(eich, color=CYAN, ls=':', lw=2, label=f'Eichrecht (α = 0,5 %): {eich:.2f} g')
    ax.set_yticks([]); ax.set_xlabel('Mittelwert von n Packungen in g'); ax.legend(loc='upper right')
    ax.set_title(f'SE = {se:.3f} g,  t = {t:.2f},  p (einseitig) = {p:.4f}  → '
                 f'{"H₀ verwerfen" if p < alpha else "H₀ beibehalten"}')
    plt.show()

interact(abfuell_test, xq=widgets.FloatSlider(value=497.8, min=494, max=501, step=0.1),
         s=widgets.FloatSlider(value=4.6, min=1, max=10, step=0.1), n=widgets.IntSlider(value=20, min=3, max=100),
         alpha=widgets.FloatLogSlider(value=0.05, base=10, min=-3, max=-1, step=0.1, readout_format='.3f'));
""")

md("""
## 4  Was der p-Wert sagt

Wir simulieren eine Welt, in der die Anlage im Mittel genau `wahres_mu` abfüllt, ziehen viele Stichproben
und zählen, wie oft der t-Wert mindestens so extrem ist wie unserer (t = −2,14).

* Mit `wahres_mu = 500` ergibt der Anteil den **p-Wert**: P(Daten so extrem | H₀).
* Mit `wahres_mu = 498` zeigt der Anteil signifikanter Stichproben die **Power** des Tests.
""")

code("""
def welten(wahres_mu=500.0, sigma=4.6, n=20, simulationen=10000, alpha=0.05):
    rng = np.random.default_rng()
    st = rng.normal(wahres_mu, sigma, size=(simulationen, n))
    t = (st.mean(1) - 500) / (st.std(1, ddof=1) / np.sqrt(n))
    t_beob = -2.14
    krit = stats.t.ppf(alpha, n-1)
    fig, ax = plt.subplots()
    kanten = np.linspace(-7, 5, 97)
    h, k = np.histogram(t, kanten); mitte = (k[:-1] + k[1:]) / 2
    ax.bar(mitte, h, width=k[1]-k[0], color=[ROT if v <= t_beob else GRAU_HELL for v in mitte])
    ax.axvline(t_beob, color=VIOLETT, lw=2.4, label='unsere Stichprobe t = −2,14')
    ax.axvline(krit, color=CYAN, ls='--', label=f'kritischer Wert α = {alpha}')
    ax.legend(loc='upper right'); ax.set_xlabel('t-Wert'); ax.set_ylabel('Anzahl')
    ax.set_title(f'Welt mit μ = {wahres_mu} g:  {np.mean(t <= t_beob):.1%} der Stichproben mindestens so extrem,  '
                 f'{np.mean(t <= krit):.1%} signifikant')
    plt.show()

interact(welten, wahres_mu=widgets.FloatSlider(value=500, min=494, max=502, step=0.25),
         sigma=widgets.FloatSlider(value=4.6, min=1, max=10, step=0.1), n=widgets.IntSlider(value=20, min=3, max=100),
         simulationen=widgets.IntSlider(value=10000, min=1000, max=50000, step=1000),
         alpha=widgets.FloatSlider(value=0.05, min=0.005, max=0.2, step=0.005));
""")

md("""
## 5  Bayes mit der Münze

**a) Zwei Hypothesen:** fair (p = 0,5) oder gezinkt (p = `p_gezinkt`). Nach jedem Wurf wird der Posterior
zum neuen Prior. **b) Kontinuierlich:** Wir schätzen die Kopf-Wahrscheinlichkeit p selbst
(Gitter-Bayes mit flachem Prior) und vergleichen mit dem Binomialtest.
""")

code("""
def muenze_pfad(wahre_muenze='gezinkt', p_gezinkt=0.7, prior=0.2, wuerfe=60, pfade=5):
    rng = np.random.default_rng()
    p_wahr = p_gezinkt if wahre_muenze == 'gezinkt' else 0.5
    fig, ax = plt.subplots()
    for j in range(pfade):
        w = rng.random(wuerfe) < p_wahr
        post = [prior]
        for kopf in w:
            lg = p_gezinkt if kopf else 1 - p_gezinkt
            post.append(post[-1]*lg / (post[-1]*lg + (1-post[-1])*0.5))
        ax.plot(post, color=VIOLETT if j == 0 else VIOLETT_HELL, lw=2 if j == 0 else 1.2)
    ax.axhline(prior, color=GRAU, ls=':')
    ax.set_ylim(0, 1); ax.set_xlabel('Anzahl Würfe'); ax.set_ylabel('P(gezinkt | Würfe)')
    ax.set_title(f'Wahrheit: {wahre_muenze}.  Kopf: Faktor {p_gezinkt/0.5:.2f},  Zahl: Faktor {(1-p_gezinkt)/0.5:.2f}')
    plt.show()

interact(muenze_pfad, wahre_muenze=['gezinkt', 'fair'],
         p_gezinkt=widgets.FloatSlider(value=0.7, min=0.55, max=0.95, step=0.05),
         prior=widgets.FloatSlider(value=0.2, min=0.01, max=0.99, step=0.01),
         wuerfe=widgets.IntSlider(value=60, min=10, max=300), pfade=widgets.IntSlider(value=5, min=1, max=20));
""")

code("""
def muenze_p(kopf=61, wuerfe=100):
    kopf = min(kopf, wuerfe)
    p = np.linspace(0.0005, 0.9995, 2000)
    log_post = kopf*np.log(p) + (wuerfe-kopf)*np.log(1-p)        # flacher Prior
    post = np.exp(log_post - log_post.max()); post /= post.sum()
    kum = np.cumsum(post)
    lo, hi = p[np.searchsorted(kum, 0.025)], p[np.searchsorted(kum, 0.975)]
    rechts = post[p > 0.5].sum()
    pwert = stats.binomtest(kopf, wuerfe, 0.5).pvalue
    fig, ax = plt.subplots()
    ax.plot(p, post, color=VIOLETT, lw=2.4)
    ax.fill_between(p, post, where=p > 0.5, color=VIOLETT_HELL)
    ax.axvline(0.5, color=GRAU, ls='--')
    ax.set_yticks([]); ax.set_xlabel('Kopf-Wahrscheinlichkeit p (Hypothese)')
    ax.set_title(f'Bayes: P(p > 0,5 | Daten) = {rechts:.1%},  95 % glaubwürdig: {lo:.2f} bis {hi:.2f}\\n'
                 f'Frequentistisch: Binomialtest gegen p = 0,5:  p-Wert = {pwert:.4f}')
    plt.show()

interact(muenze_p, kopf=widgets.IntSlider(value=61, min=0, max=500), wuerfe=widgets.IntSlider(value=100, min=1, max=500));
""")

md("""
## 6  Bayes mit dem Würfel: Prior und Bayes-Faktor

Wir zählen die Sechsen. Fair: P(6) = 1/6, gezinkt: P(6) = 1/4.
Wie wahrscheinlich ist der Würfel gezinkt – je nachdem, wie häufig gezinkte Würfel überhaupt sind?
""")

code("""
def wuerfel_bayes(sechsen=16, wuerfe=60, prior=0.5):
    sechsen = min(sechsen, wuerfe)
    lf, lg = stats.binom.pmf(sechsen, wuerfe, 1/6), stats.binom.pmf(sechsen, wuerfe, 0.25)
    bf = lg / lf
    post = prior*bf / (prior*bf + 1 - prior)
    pwert = stats.binom.sf(sechsen - 1, wuerfe, 1/6)
    ks = np.arange(0, wuerfe + 1)
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(12, 4))
    ax.bar(ks - .2, stats.binom.pmf(ks, wuerfe, 1/6), .4, color=GRAU, label='fair')
    ax.bar(ks + .2, stats.binom.pmf(ks, wuerfe, .25), .4, color=VIOLETT, label='gezinkt')
    ax.axvline(sechsen, color='k', ls='--'); ax.legend(); ax.set_xlim(0, max(30, wuerfe*.45))
    ax.set_xlabel('Anzahl Sechsen'); ax.set_title(f'Bayes-Faktor = {lg:.4f} / {lf:.4f} = {bf:.2f}')
    ax2.bar(['Prior', 'Posterior'], [prior, post], color=[GRAU, VIOLETT])
    ax2.set_ylim(0, 1); ax2.set_title(f'P(gezinkt): {prior:.0%} → {post:.1%}    (p-Wert einseitig: {pwert:.4f})')
    plt.tight_layout(); plt.show()

interact(wuerfel_bayes, sechsen=widgets.IntSlider(value=16, min=0, max=200),
         wuerfe=widgets.IntSlider(value=60, min=6, max=600), prior=widgets.FloatSlider(value=0.5, min=0.01, max=0.99, step=0.01));
""")

md("""
## 7  Bayes-Schätzung des Mittelwerts (Abfüllanlage)

Gitterverfahren (Grid Approximation) mit den 20 Packungen. Wir testen 2001 Hypothesen für μ zwischen 490 und 510 g und aktualisieren Packung für Packung.
Optional mit Vorwissen aus der Einrichtung der Anlage (Prior um 500 g).
""")

code("""
def mittelwert_bayes(packungen=20, prior='flach', prior_sd=1.0, sigma=4.6):
    mu = np.linspace(490, 510, 2001)
    post = np.ones_like(mu) if prior == 'flach' else stats.norm.pdf(mu, 500, prior_sd)
    post /= post.sum()
    fig, ax = plt.subplots()
    farben = plt.cm.viridis(np.linspace(0, 0.9, 6))
    zeigen = sorted(set([0, 1, 3, 10, packungen]) & set(range(packungen + 1)))
    for i in range(packungen + 1):
        if i in zeigen:
            m = (mu*post).sum(); sd = np.sqrt((mu**2*post).sum() - m**2)
            ax.plot(mu, post, lw=2, color=farben[zeigen.index(i)], label=f'nach {i} Packungen: {m:.2f} ± {sd:.2f} g')
        if i < packungen:
            post = post * stats.norm.pdf(abfuellung[i], mu, sigma)
            post /= post.sum()
    p500, p498 = post[mu < 500].sum(), post[mu < 498].sum()
    ax.axvline(500, color=GRAU, ls='--')
    ax.plot(abfuellung[:packungen], np.zeros(packungen), '|', color='k', ms=14)
    ax.set_xlim(488, 510); ax.set_yticks([]); ax.legend(loc='upper right', fontsize=9)
    ax.set_xlabel('wahrer Mittelwert μ (Hypothese) in g')
    ax.set_title(f'P(μ < 500 g | Daten) = {p500:.1%}     P(μ < 498 g | Daten) = {p498:.1%}')
    plt.show()

interact(mittelwert_bayes, packungen=widgets.IntSlider(value=20, min=0, max=20),
         prior=['flach', 'Einrichtung: N(500; prior_sd)'],
         prior_sd=widgets.FloatSlider(value=1.0, min=0.2, max=5, step=0.1),
         sigma=widgets.FloatSlider(value=4.6, min=1, max=10, step=0.1));
""")

md("""
## 8  Wo ist mein Schlüssel?

Der Schlüssel wird verdeckt nach der Gewohnheit versteckt. Klicken Sie auf einen Ort, um dort nachzusehen.
„Nicht gefunden“ ist auch ein Befund: P(dort) wird mit (1 − Entdeckungschance) multipliziert und alles neu normiert.
""")

code("""
ORTE = ['Jackentasche', 'Schlüsselbrett', 'Schreibtisch', 'Auto', 'Küche', 'ganz woanders']
PRIOR = np.array([.35, .25, .15, .10, .10, .05])
FUND = np.array([.90, .99, .60, .70, .80, .10])
zustand = {}
ausgabe = widgets.Output()

def neuer_fall(_=None):
    zustand.update(post=PRIOR.copy(), ort=np.random.choice(6, p=PRIOR), gefunden=False, suchen=0,
                   text='Neuer Fall: Wo suchen Sie zuerst?')
    zeichne()

def suche(i):
    if zustand['gefunden']:
        return
    zustand['suchen'] += 1
    if zustand['ort'] == i and np.random.rand() < FUND[i]:
        zustand['gefunden'] = True
        zustand['post'] = np.eye(6)[i]
        zustand['text'] = f'Gefunden in: {ORTE[i]} (nach {zustand["suchen"]} Suchen)'
    else:
        p = zustand['post'].copy(); p[i] *= 1 - FUND[i]; zustand['post'] = p / p.sum()
        best = np.argmax(zustand['post'] * FUND)
        zustand['text'] = (f'{ORTE[i]}: nicht gefunden.  Suchen lohnt jetzt am meisten: {ORTE[best]} '
                           f'(P × Entdeckung = {zustand["post"][best]*FUND[best]:.0%})')
    zeichne()

def zeichne():
    with ausgabe:
        clear_output(wait=True)
        fig, ax = plt.subplots(figsize=(10, 3.8))
        farben = [CYAN if zustand['gefunden'] and v == 1 else VIOLETT for v in zustand['post']]
        ax.bar(ORTE, zustand['post'], color=farben)
        for j, v in enumerate(zustand['post']):
            ax.text(j, v + .01, f'{v:.0%}', ha='center')
        ax.set_ylim(0, 1.05); ax.set_ylabel('P(Schlüssel ist dort)'); ax.set_title(zustand['text'])
        plt.show()

knoepfe = [widgets.Button(description=o) for o in ORTE]
for i, b in enumerate(knoepfe):
    b.on_click(lambda _, i=i: suche(i))
reset = widgets.Button(description='Neuer Fall', button_style='warning')
reset.on_click(neuer_fall)
display(widgets.HBox(knoepfe + [reset]), ausgabe)
neuer_fall()
""")

md("""
## 9  Glaube ich dieser Quelle?

Posterior-Chance = Prior-Chance × Bayes-Faktor, mit
Bayes-Faktor = P(Quelle behauptet es | stimmt) / P(Quelle behauptet es | stimmt nicht).
Mehrere *unabhängige* Quellen multiplizieren ihre Bayes-Faktoren; abgeschriebene Quellen zählen nur einmal.
""")

code("""
def quelle(prior=0.3, treffer=0.8, fehlalarm=0.2, quellen=2, unabhaengig=True):
    bf = treffer / fehlalarm
    wirksam = quellen if unabhaengig else min(quellen, 1)
    odds = prior / (1 - prior)
    werte = [prior] + [odds*bf**k / (1 + odds*bf**k) for k in range(1, quellen + 1)]
    if not unabhaengig:
        werte = [prior] + [odds*bf / (1 + odds*bf)] * quellen
    fig, ax = plt.subplots(figsize=(9, 3.8))
    ax.bar(['vorher'] + [f'+ Quelle {k}' for k in range(1, quellen + 1)], werte,
           color=[GRAU] + [VIOLETT if unabhaengig or k == 1 else ROT_HELL for k in range(1, quellen + 1)])
    for j, v in enumerate(werte):
        ax.text(j, v + .02, f'{v:.0%}', ha='center')
    ax.set_ylim(0, 1.1); ax.set_ylabel('P(Behauptung stimmt)')
    ax.set_title(f'Bayes-Faktor je Quelle = {treffer:.2f} / {fehlalarm:.2f} = {bf:.1f};  '
                 f'{"unabhängig" if unabhaengig else "voneinander abgeschrieben"}')
    plt.show()

interact(quelle, prior=widgets.FloatSlider(value=0.3, min=0.01, max=0.99, step=0.01),
         treffer=widgets.FloatSlider(value=0.8, min=0.05, max=1, step=0.05),
         fehlalarm=widgets.FloatSlider(value=0.2, min=0.01, max=1, step=0.01),
         quellen=widgets.IntSlider(value=2, min=1, max=6), unabhaengig=True);
""")

md("""
## 10  Den Diamanten durchrechnen

Drei Spitzen des Diamanten sind konkurrierende Erklärungen für „Trickgruppe behält mehr“:
**Idee** (der Trick hilft), **Gegenteil** (der Trick lenkt ab und schadet), **Weder-noch** (etwas Drittes,
z. B. das zwei Minuten längere Video). Die vierte Spitze, **Sowohl-als-auch**, ist keine eigene Erklärung,
sondern liefert eine Beobachtung, die Idee *und* Gegenteil erwarten.

| Beobachtung | P(B \\| Idee) | P(B \\| Gegenteil) | P(B \\| Weder-noch) |
|---|---|---|---|
| ① Sowohl-als-auch: Trickgruppe staunt mehr | 0,9 | 0,9 | 0,5 |
| ② behält mehr als die kürzere Kontrolle | 0,7 | 0,1 | 0,7 |
| ③ behält mehr als eine gleich lange Kontrolle | 0,7 | 0,1 | 0,2 |

Posterior-Chance = Prior-Chance × Bayes-Faktor. Für jede Erklärung H gilt
BF(H) = P(B | H) / P(B | nicht H); paarweise BF(Idee : Gegenteil) = P(B | Idee) / P(B | Gegenteil).
„nicht beobachtet“ rechnet mit 1 − P. Wählen Sie für jede Beobachtung ein Ergebnis und schauen Sie, welche
Spitze welche Erklärung bewegt. Annahme: Die Beobachtungen sind gegeben die Erklärung unabhängig.
""")

code("""
ERKL = ['Idee', 'Gegenteil', 'Weder-noch']
BEOB = ['① staunt mehr', '② > kürzere Kontrolle', '③ > gleich lange Kontrolle']
LIK = np.array([[.9, .9, .5],
                [.7, .1, .7],
                [.7, .1, .2]])
ERGEBNIS = ['nicht erhoben', 'beobachtet', 'nicht beobachtet']

def diamant(prior_idee=0.25, prior_gegenteil=0.25, b1='beobachtet', b2='beobachtet', b3='beobachtet',
            lik_eigene=False, l1='0.9 0.9 0.5', l2='0.7 0.1 0.7', l3='0.7 0.1 0.2'):
    if prior_idee + prior_gegenteil >= 1:
        print('Prior Idee + Gegenteil muss unter 1 bleiben (Rest = Weder-noch).'); return
    lik = LIK.copy()
    if lik_eigene:
        try:
            lik = np.array([[float(x.replace(',', '.')) for x in z.split()] for z in (l1, l2, l3)])
            assert lik.shape == (3, 3) and ((lik > 0) & (lik < 1)).all()
        except Exception:
            print('Eigene Likelihoods: je Zeile drei Zahlen zwischen 0 und 1, z. B. 0.7 0.1 0.2'); return
    p = np.array([prior_idee, prior_gegenteil, 1 - prior_idee - prior_gegenteil])
    schritte, zeilen = [('Prior', p)], []
    for k, erg in enumerate([b1, b2, b3]):
        if erg == 'nicht erhoben':
            continue
        l = lik[k] if erg == 'beobachtet' else 1 - lik[k]
        bf = np.array([l[j] / ((p @ l - p[j] * l[j]) / (1 - p[j])) for j in range(3)])
        neu = p * l / (p @ l)
        zeilen.append((BEOB[k] + ('' if erg == 'beobachtet' else ' (nein)'), l, bf, p, neu))
        p = neu
        schritte.append((BEOB[k][:1] + ('' if erg == 'beobachtet' else ' nein'), p))

    fig, ax = plt.subplots(figsize=(10, 4))
    breite = 0.26
    for j, (name, farbe) in enumerate(zip(ERKL, [VIOLETT, ROT, GRAU])):
        werte = [s[1][j] for s in schritte]
        x = np.arange(len(schritte)) + (j - 1) * breite
        ax.bar(x, werte, breite, color=farbe, label=name)
        for xi, v in zip(x, werte):
            ax.text(xi, v + .01, f'{v:.0%}', ha='center', fontsize=8)
    ax.set_xticks(np.arange(len(schritte)), [s[0] for s in schritte])
    ax.set_ylim(0, 1.08); ax.set_ylabel('P(Erklärung)'); ax.legend(frameon=False, ncol=3, loc='upper left')
    ax.set_title('Posterior-Chance = Prior-Chance × Bayes-Faktor')
    plt.show()

    for name, l, bf, vor, nach in zeilen:
        print(f'{name}')
        print(f'   P(B | H)          ' + '   '.join(f'{e}: {v:.2f}' for e, v in zip(ERKL, l)))
        print(f'   BF(H gegen Rest)  ' + '   '.join(f'{e}: {v:.2f}' for e, v in zip(ERKL, bf)))
        print(f'   paarweise         Idee : Gegenteil = {l[0]:.2f} / {l[1]:.2f} = {l[0]/l[1]:.2f}'
              f'    Idee : Weder-noch = {l[0]:.2f} / {l[2]:.2f} = {l[0]/l[2]:.2f}')
        cv, cn = vor[0] / (1 - vor[0]), nach[0] / (1 - nach[0])
        print(f'   Rechnung Idee     Chance {cv:.3f} × BF {bf[0]:.2f} = {cn:.3f}  →  P = {nach[0]:.1%}')
        print()

interact(diamant,
         prior_idee=widgets.FloatSlider(value=0.25, min=0.01, max=0.97, step=0.01),
         prior_gegenteil=widgets.FloatSlider(value=0.25, min=0.01, max=0.97, step=0.01),
         b1=widgets.Dropdown(options=ERGEBNIS, value='beobachtet', description='① staunt'),
         b2=widgets.Dropdown(options=ERGEBNIS, value='beobachtet', description='② kürzer'),
         b3=widgets.Dropdown(options=ERGEBNIS, value='beobachtet', description='③ gleich lang'),
         lik_eigene=widgets.Checkbox(value=False, description='eigene Likelihoods'),
         l1=widgets.Text(value='0.9 0.9 0.5', description='① I G W'),
         l2=widgets.Text(value='0.7 0.1 0.7', description='② I G W'),
         l3=widgets.Text(value='0.7 0.1 0.2', description='③ I G W'));
""")

nb = {"cells": zellen, "metadata": {"colab": {"name": "ZGS_Test_Bayes.ipynb"},
                                    "kernelspec": {"name": "python3", "display_name": "Python 3"},
                                    "language_info": {"name": "python"}},
      "nbformat": 4, "nbformat_minor": 0}
for z in nb["cells"]:
    z["source"] = [zeile + "\n" for zeile in z["source"].split("\n")]
    z["source"][-1] = z["source"][-1].rstrip("\n")
with open(ZIEL, "w", encoding="utf-8") as fh:
    json.dump(nb, fh, ensure_ascii=False, indent=1)
print(f"{ZIEL}: {len(zellen)} Zellen")
