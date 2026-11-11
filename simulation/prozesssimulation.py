"""
Monte-Carlo-Simulation des Ist- und Soll-Prozesses im First-Level-Support
(Abbildung 5 und Abbildung 7 der Arbeit).

Jedes simulierte Ticket durchlaeuft die Pfade des jeweiligen BPMN-Modells.
Alle Zeiten in Minuten Arbeitszeit. Bearbeitungszeiten sind dreiecksverteilt
(Minimum, haeufigster Wert, Maximum), Wartezeiten exponentialverteilt.

Herkunft der Parameter (siehe HERKUNFT und parameter.csv):
  KALIBRIERT  automatisch so bestimmt, dass das Ist-Modell die Benchmarks
              aus Tabelle 1 trifft (Netto-FCR 74 %, MTTR 8,40 Arbeitsstunden)
  LITERATUR   an einem Wert aus den Quellen der Arbeit ausgerichtet
  INTERVIEW   Platzhalter, durch Ergebnis der Experteninterviews zu ersetzen
  ANNAHME     Platzhalter, durch Ticketsystem-Auswertung oder Begruendung
              zu ersetzen

Aufruf:  python3 prozesssimulation.py
Ausgabe: ergebnisse.csv, sensitivitaet.csv, breakeven.csv, robustheit.csv,
         parameter.csv, ergebnistabelle.tex
"""
import csv
import random
import statistics
from copy import deepcopy

N_TICKETS = 100_000
SEED = 42

# Kalibrierziele aus Tabelle 1 der Arbeit (Rumburg 2011, 2018)
ZIEL_FCR_NETTO = 0.74
ZIEL_MTTR_H = 8.40

# --------------------------------------------------------------------------
# PARAMETER
# --------------------------------------------------------------------------
BASIS = {
    # --- gilt fuer Ist und Soll -------------------------------------------
    "p_telefon": 0.40,            # Anteil telefonischer Meldungen
    "warte_agent": 30,            # mittlere Wartezeit bis ein Agent ein Ticket aufnimmt (Portal/Chat/Mail)
    "warte_telefon": (1, 2, 5),   # Warteschleife Telefon
    "p_loesbar_fl": 0.70,         # Anteil der Stoerungen, die im First Level grundsaetzlich loesbar sind
    "loesung_anwenden": (5, 10, 30),
    "p_erfolg_1": 0.92,           # Loesungsversuch gelingt beim ersten Mal
    "p_erfolg_2": 0.50,           # zweiter Versuch gelingt
    "warte_second_level": 360,    # mittlere Wartezeit im Second Level  -> wird KALIBRIERT
    "arbeit_second_level": (20, 45, 120),
    "warte_rueckfrage": 120,      # mittlere Wartezeit auf Antwort bei asynchroner Rueckfrage
    "warte_pingpong": 240,        # mittlere Verzoegerung durch Fehlzuweisung

    # --- Ist-Prozess ------------------------------------------------------
    "ist_erfassen": (3, 5, 10),
    "ist_p_unvollstaendig": 0.20, # Meldung unvollstaendig -> Rueckfrage
    "ist_kategorisieren": (1, 2, 4),
    "ist_p_fehlkategorie": 0.15,  # INTERVIEW Frage 5
    "ist_erstdiagnose": (5, 10, 25),
    "ist_p_wissenstreffer": 0.85, # Stichwortsuche findet vorhandene Loesung -> wird KALIBRIERT
    "ist_p_doku_lueckenhaft": 0.40,
    "ist_dokumentieren": (2, 3, 6),

    # --- Soll-Prozess -----------------------------------------------------
    "soll_dialog": (2, 3, 6),             # KI-Dialog Portal/Chat (Anwenderzeit, keine Agentenzeit)
    "soll_p_art9": 0.02,                  # Treffer besondere Datenkategorien -> manueller Pfad
    "soll_p_konfidenz_hoch": 0.65,        # Anteil Kategorievorschlaege oberhalb der Schwelle 0,90
    "soll_p_fehl_oberhalb": 0.05,         # Fehlerquote oberhalb der Schwelle (unbemerkt)
    "soll_p_fehl_nach_pruefung": 0.08,    # Fehlerquote, wenn der Agent unterhalb der Schwelle wirklich prueft
    "soll_p_fehl_ungeprueft": 0.30,       # Fehlerquote unterhalb der Schwelle ohne echte Pruefung
    "soll_p_durchwinken": 0.20,           # Agent uebernimmt unsicheren Vorschlag ungeprueft -- INTERVIEW Frage 12
    "soll_vorschlag_pruefen": (0.5, 1, 2),
    "soll_telefon_selfservice": False,    # Telefonfaelle gehen nicht in den Self-Service (in Abb. 7 nachziehen)
    "soll_p_selfservice": 0.35,           # Anteil der FL-loesbaren Portal/Chat-Faelle im Positivkatalog -- INTERVIEW Frage 9
    "soll_selfservice_dauer": (3, 5, 15), # Anwender fuehrt Anleitung aus
    "soll_p_selfservice_erfolg": 0.70,    # Anwender bestaetigt Behebung
    "soll_erstdiagnose": (4, 8, 17),      # mit Loesungsvorschlag (RAG); LITERATUR: ca. 13 % kuerzere Loesungsarbeit
    "soll_p_wissenstreffer": 0.96,        # bedeutungsbasierter Abruf
    "soll_p_doku_lueckenhaft": 0.10,      # mit Uebergabezusammenfassung
    "soll_dokumentieren": (1, 2, 4),

    # --- Umrechnung Ticketvolumen pro Agent -------------------------------
    "produktive_min_monat": 21 * 8 * 60 * 0.60,  # 21 Tage, 8 h, 60 % ticketbezogen
}

HERKUNFT = {
    "ist_p_wissenstreffer": "KALIBRIERT auf Netto-FCR 74 % (Rumburg 2011)",
    "warte_second_level": "KALIBRIERT auf MTTR 8,40 Arbeitsstunden (Rumburg 2018)",
    "soll_p_selfservice": "LITERATUR: Basisfall ergibt Self-Service-Quote nahe 10,4 % (Rumburg 2013); INTERVIEW Frage 9",
    "soll_erstdiagnose": "LITERATUR: +15 % geloeste Faelle je Stunde (Brynjolfsson/Li/Raymond 2025) = ca. 13 % weniger Zeit fuer Diagnose und Loesung",
    "ist_p_fehlkategorie": "INTERVIEW Frage 5",
    "soll_p_durchwinken": "INTERVIEW Frage 12",
    "soll_telefon_selfservice": "MODELLENTSCHEIDUNG, in Abb. 7 nachzuziehen",
}

# Szenarien: Abweichungen vom Basisfall fuer den Soll-Prozess
SZENARIEN = {
    "pessimistisch": {
        "soll_p_konfidenz_hoch": 0.45, "soll_p_fehl_oberhalb": 0.08,
        "soll_p_durchwinken": 0.40,
        "soll_p_selfservice": 0.15, "soll_p_selfservice_erfolg": 0.55,
        "soll_erstdiagnose": (5, 10, 22), "soll_p_wissenstreffer": 0.93,
        "soll_p_doku_lueckenhaft": 0.20,
    },
    "Basis": {},
    "optimistisch": {
        "soll_p_konfidenz_hoch": 0.80, "soll_p_fehl_oberhalb": 0.03,
        "soll_p_durchwinken": 0.10,
        "soll_p_selfservice": 0.55, "soll_p_selfservice_erfolg": 0.80,
        "soll_erstdiagnose": (3, 6, 13), "soll_p_wissenstreffer": 0.98,
        "soll_p_doku_lueckenhaft": 0.05,
    },
}

# Sensitivitaetsanalyse: je Parameter ein niedriger und ein hoher Wert
SENSITIVITAET = {
    "p_telefon": (0.20, 0.60),
    "soll_p_selfservice": (0.15, 0.55),
    "soll_p_selfservice_erfolg": (0.50, 0.90),
    "soll_p_konfidenz_hoch": (0.40, 0.90),
    "soll_p_durchwinken": (0.00, 0.60),
    "soll_p_fehl_oberhalb": (0.02, 0.12),
    "soll_p_wissenstreffer": (0.92, 0.99),
    "soll_p_doku_lueckenhaft": (0.05, 0.30),
}


# --------------------------------------------------------------------------
# Simulation
# --------------------------------------------------------------------------
class Sim:
    def __init__(self, p, seed):
        self.p = p
        self.r = random.Random(seed)

    def tri(self, key):
        lo, mode, hi = self.p[key]
        return self.r.triangular(lo, hi, mode)

    def exp(self, key):
        return self.r.expovariate(1.0 / self.p[key])

    def ja(self, key):
        return self.r.random() < self.p[key]

    # gemeinsamer Teil: Loesungsversuch im First Level, sonst Eskalation
    def bearbeiten(self, t, a, kontakte, telefon, loesbar, p_treffer, fehlkat,
                   p_doku, k_diag, k_doku):
        d = self.tri(k_diag)
        t += d; a += d
        geloest_fl = False
        erstloesung = False
        if loesbar and self.r.random() < self.p[p_treffer]:
            d = self.tri("loesung_anwenden")
            t += d; a += d
            if self.ja("p_erfolg_1"):
                geloest_fl = True
                erstloesung = kontakte == 1
            else:                                   # Ruecksprung zur Erstdiagnose
                kontakte += 1
                if not telefon:
                    t += self.exp("warte_rueckfrage")
                d = self.tri(k_diag) + self.tri("loesung_anwenden")
                t += d; a += d
                geloest_fl = self.ja("p_erfolg_2")
        if not geloest_fl:                          # funktionale Eskalation
            t += self.exp("warte_second_level")
            if fehlkat:
                t += self.exp("warte_pingpong")
            if self.r.random() < self.p[p_doku]:
                t += self.exp("warte_rueckfrage")
            t += self.tri("arbeit_second_level")
        d = self.tri(k_doku)
        t += d; a += d
        return t, a, geloest_fl, erstloesung

    def ist(self, telefon=None, loesbar=None, wartet_schon=False):
        if telefon is None:
            telefon = self.ja("p_telefon")
        if loesbar is None:
            loesbar = self.ja("p_loesbar_fl")
        t = a = 0.0
        kontakte = 1
        if not wartet_schon:
            t += self.tri("warte_telefon") if telefon else self.exp("warte_agent")
        d = self.tri("ist_erfassen")
        t += d; a += d
        if self.ja("ist_p_unvollstaendig"):
            if telefon:
                d = self.r.triangular(1, 4, 2)
                t += d; a += d
            else:
                t += self.exp("warte_rueckfrage")
                d = self.r.triangular(2, 5, 3)
                t += d; a += d
                kontakte += 1
        d = self.tri("ist_kategorisieren")
        t += d; a += d
        fehlkat = self.ja("ist_p_fehlkategorie")
        t, a, fl, fcr = self.bearbeiten(t, a, kontakte, telefon, loesbar,
                                        "ist_p_wissenstreffer", fehlkat,
                                        "ist_p_doku_lueckenhaft",
                                        "ist_erstdiagnose", "ist_dokumentieren")
        return dict(t=t, a=a, fl=fl, fcr=fcr, selfservice=False, agent=True,
                    loesbar=loesbar)

    def soll(self):
        telefon = self.ja("p_telefon")
        loesbar = self.ja("p_loesbar_fl")
        t = a = 0.0
        kontakte = 1
        if telefon:                                 # Agent erfasst im Dialog
            t += self.tri("warte_telefon")
            d = self.tri("ist_erfassen")
            t += d; a += d
        else:                                       # KI-Dialog, Rueckfragen synchron
            t += self.tri("soll_dialog")
        if self.ja("soll_p_art9"):                  # manueller Pfad wie im Ist
            r = self.ist(telefon=telefon, loesbar=loesbar, wartet_schon=telefon)
            r["t"] += t; r["a"] += a
            return r
        hoch = self.ja("soll_p_konfidenz_hoch")
        # Self-Service nur fuer Faelle des Positivkatalogs
        kanal_ok = (not telefon) or self.p["soll_telefon_selfservice"]
        if kanal_ok and loesbar and self.ja("soll_p_selfservice"):
            t += self.tri("soll_selfservice_dauer")
            if self.ja("soll_p_selfservice_erfolg"):
                return dict(t=t, a=0.0, fl=True, fcr=True, selfservice=True,
                            agent=False, loesbar=loesbar)
            kontakte += 1
        if not telefon:
            t += self.exp("warte_agent")
        if hoch:                                    # Human-on-the-Loop
            fehlkat = self.ja("soll_p_fehl_oberhalb")
        elif self.ja("soll_p_durchwinken"):         # Pruefung findet faktisch nicht statt
            fehlkat = self.ja("soll_p_fehl_ungeprueft")
        else:                                       # Human-in-the-Loop
            d = self.tri("soll_vorschlag_pruefen")
            t += d; a += d
            fehlkat = self.ja("soll_p_fehl_nach_pruefung")
        t, a, fl, fcr = self.bearbeiten(t, a, kontakte, telefon, loesbar,
                                        "soll_p_wissenstreffer", fehlkat,
                                        "soll_p_doku_lueckenhaft",
                                        "soll_erstdiagnose", "soll_dokumentieren")
        return dict(t=t, a=a, fl=fl, fcr=fcr, selfservice=False, agent=True,
                    loesbar=loesbar)


def kennzahlen(p, modus, n=N_TICKETS, seed=SEED):
    s = Sim(p, seed)
    lauf = s.ist if modus == "ist" else s.soll
    tickets = [lauf() for _ in range(n)]
    zeiten = [x["t"] for x in tickets]
    agent = [x for x in tickets if x["agent"]]
    loesbar = [x for x in tickets if x["loesbar"]]
    a_mittel = statistics.fmean(x["a"] for x in tickets)
    a_agent = statistics.fmean(x["a"] for x in agent)
    return {
        "MTTR_h": statistics.fmean(zeiten) / 60,
        "Median_h": statistics.median(zeiten) / 60,
        "FCR_netto": statistics.fmean(x["fcr"] for x in loesbar),
        "FCR_brutto": statistics.fmean(x["fcr"] for x in tickets),
        "FCR_netto_Agentenkanal": statistics.fmean(x["fcr"] for x in agent if x["loesbar"]),
        "FLR": statistics.fmean(x["fl"] for x in tickets),
        "SelfService": statistics.fmean(x["selfservice"] for x in tickets),
        "Agentenmin_je_Ticket": a_mittel,
        "Agentenmin_je_Agententicket": a_agent,
        "Tickets_je_Agent_Monat": p["produktive_min_monat"] / a_mittel,
    }


def bisektion(p, key, lo, hi, ziel, kennzahl, steigend=True, n=40_000):
    """Sucht den Wert von p[key], bei dem die Ist-Kennzahl das Ziel trifft."""
    for _ in range(18):
        mid = (lo + hi) / 2
        p[key] = mid
        wert = kennzahlen(p, "ist", n=n)[kennzahl]
        if (wert < ziel) == steigend:
            lo = mid
        else:
            hi = mid
    p[key] = round((lo + hi) / 2, 3 if hi <= 1 else 0)
    return p[key]


def kalibrieren(p):
    """Ist-Modell an die Benchmarks aus Tabelle 1 anpassen.
    Freie Parameter: Trefferquote der Stichwortsuche (-> Netto-FCR) und
    mittlere Wartezeit im Second Level (-> MTTR)."""
    bisektion(p, "ist_p_wissenstreffer", 0.50, 1.00, ZIEL_FCR_NETTO, "FCR_netto")
    bisektion(p, "warte_second_level", 60, 3000, ZIEL_MTTR_H, "MTTR_h")
    return p


# --------------------------------------------------------------------------
# Break-even-Analyse
# --------------------------------------------------------------------------
# Kostenannahmen fuer das Break-even-Volumen (ANNAHMEN, organisationsspezifisch)
KOSTEN = {
    "agent_euro_je_min": 0.75,        # Vollkosten Agent, entspricht 45 Euro je Stunde
    "ki_euro_je_ticket": 0.05,        # laufende Modellkosten je Ticket
    "fixkosten_monat": (5_000, 10_000, 20_000),  # Betrieb, Pflege, umgelegte Einfuehrung
}

# Parameter, fuer die der Kippwert gesucht wird: (Untergrenze, Obergrenze)
KIPPWERTE = {
    "soll_p_wissenstreffer": (0.50, 1.00),
    "soll_p_fehl_oberhalb": (0.00, 1.00),
    "soll_p_durchwinken": (0.00, 1.00),
    "soll_p_doku_lueckenhaft": (0.00, 1.00),
    "soll_p_selfservice": (0.00, 1.00),
}


def kippwert(par, lo, hi, ziel, kennzahl, n=40_000):
    """Wert des Soll-Parameters, bei dem die Soll-Kennzahl den Ist-Wert erreicht.
    Gibt None zurueck, wenn das Soll im gesamten Bereich besser bleibt."""
    def diff(v):
        p = deepcopy(BASIS); p[par] = v
        return kennzahlen(p, "soll", n=n)[kennzahl] - ziel
    d_lo, d_hi = diff(lo), diff(hi)
    if d_lo < 0 and d_hi < 0:
        return None
    if d_lo > 0 and d_hi > 0:
        return "nie besser"
    for _ in range(14):
        mid = (lo + hi) / 2
        if (diff(mid) < 0) == (d_lo < 0):
            lo = mid
        else:
            hi = mid
    return round((lo + hi) / 2, 3)


def breakeven(ist_k):
    with open("breakeven.csv", "w", newline="") as f:
        w = csv.writer(f)

        # 1) Kippwerte: ab wann verschwindet der Vorteil gegenueber dem Ist?
        print("\nKippwerte (Soll Basis, je ein Parameter veraendert)")
        w.writerow(["Teil 1: Kippwerte"])
        w.writerow(["Parameter", "Basiswert", "Kippwert MTTR", "Kippwert Agentenminuten"])
        for par, (lo, hi) in KIPPWERTE.items():
            k_mttr = kippwert(par, lo, hi, ist_k["MTTR_h"], "MTTR_h")
            k_min = kippwert(par, lo, hi, ist_k["Agentenmin_je_Ticket"], "Agentenmin_je_Ticket")
            txt = lambda x: "kein Kippwert (Soll immer besser)" if x is None else x
            w.writerow([par, BASIS[par], txt(k_mttr), txt(k_min)])
            print(f"  {par:28} Basis {BASIS[par]:<5} MTTR: {txt(k_mttr)}   Agentenmin.: {txt(k_min)}")

        # 2) Wirkung in Abhaengigkeit von der Fehlzuweisungsquote im Ist
        print("\nVorteil in Abhaengigkeit von der Fehlkategorisierung im Ist (ohne Neukalibrierung)")
        w.writerow([])
        w.writerow(["Teil 2: Fehlkategorisierung im Ist"])
        w.writerow(["ist_p_fehlkategorie", "MTTR_Ist_h", "MTTR_Soll_h", "Vorteil_h", "Vorteil_Prozent"])
        soll = kennzahlen(BASIS, "soll")
        for v in (0.05, 0.10, 0.15, 0.20, 0.30):
            p = deepcopy(BASIS); p["ist_p_fehlkategorie"] = v
            i = kennzahlen(p, "ist")
            d = i["MTTR_h"] - soll["MTTR_h"]
            w.writerow([v, round(i["MTTR_h"], 2), round(soll["MTTR_h"], 2),
                        round(d, 2), round(d / i["MTTR_h"] * 100, 1)])
            print(f"  Ist-Fehlquote {v:.2f}: MTTR Ist {i['MTTR_h']:.2f} h, Soll {soll['MTTR_h']:.2f} h, Vorteil {d:.2f} h ({d / i['MTTR_h'] * 100:.1f} %)")

        # 3) Break-even-Ticketvolumen je Monat
        print("\nBreak-even-Volumen (Tickets je Monat)")
        w.writerow([])
        w.writerow(["Teil 3: Break-even-Ticketvolumen je Monat"])
        w.writerow(["Szenario", "Ersparnis_Agentenmin_je_Ticket", "Ersparnis_Euro_je_Ticket"]
                   + [f"Fixkosten_{x}_Euro" for x in KOSTEN["fixkosten_monat"]])
        for name, abw in SZENARIEN.items():
            p = deepcopy(BASIS); p.update(abw)
            k = kennzahlen(p, "soll")
            minuten = ist_k["Agentenmin_je_Ticket"] - k["Agentenmin_je_Ticket"]
            euro = minuten * KOSTEN["agent_euro_je_min"] - KOSTEN["ki_euro_je_ticket"]
            vol = [round(x / euro) for x in KOSTEN["fixkosten_monat"]]
            w.writerow([name, round(minuten, 1), round(euro, 2)] + vol)
            print(f"  {name:14} Ersparnis {minuten:5.1f} min = {euro:5.2f} Euro je Ticket -> Volumen {vol}")


# --------------------------------------------------------------------------
# Robustheitsanalyse
# --------------------------------------------------------------------------
# Alle als Annahme gesetzten Groessen variieren gleichzeitig und unabhaengig.
# Die beiden kalibrierten Parameter bleiben fest.
ROBUST_LAEUFE = 300
ROBUST_FEST = {"ist_p_wissenstreffer", "warte_second_level",
               "produktive_min_monat", "soll_telefon_selfservice"}
ROBUST_TREFFER = (0.85, 0.99)   # Spanne fuer die Trefferquote des Abrufs


def zufallsparameter(r):
    p = deepcopy(BASIS)
    for k, v in BASIS.items():
        if k in ROBUST_FEST:
            continue
        if k == "soll_p_wissenstreffer":
            p[k] = r.uniform(*ROBUST_TREFFER)
        elif isinstance(v, tuple):                 # Bearbeitungszeit: +/- 30 %
            f = r.uniform(0.7, 1.3)
            p[k] = tuple(x * f for x in v)
        elif k.startswith("warte_"):               # Wartezeit: +/- 50 %
            p[k] = v * r.uniform(0.5, 1.5)
        else:                                      # Wahrscheinlichkeit: kleinere Seite +/- 50 %
            f = r.uniform(0.5, 1.5)
            p[k] = v * f if v <= 0.5 else 1 - (1 - v) * f
    return p


def quantil(werte, q):
    w = sorted(werte)
    return w[min(len(w) - 1, int(q * len(w)))]


def robustheit(n=20_000):
    r = random.Random(SEED + 1)
    d_mttr, d_min = [], []
    for i in range(ROBUST_LAEUFE):
        p = zufallsparameter(r)
        ist = kennzahlen(p, "ist", n=n, seed=SEED + i)
        soll = kennzahlen(p, "soll", n=n, seed=SEED + i)
        d_mttr.append(1 - soll["MTTR_h"] / ist["MTTR_h"])
        d_min.append(1 - soll["Agentenmin_je_Ticket"] / ist["Agentenmin_je_Ticket"])
    zeilen = [
        ("Anteil Kombinationen mit kuerzerer MTTR im Soll", sum(x > 0 for x in d_mttr) / len(d_mttr)),
        ("Anteil Kombinationen mit weniger Agentenminuten im Soll", sum(x > 0 for x in d_min) / len(d_min)),
        ("MTTR-Rueckgang 5. Perzentil", quantil(d_mttr, 0.05)),
        ("MTTR-Rueckgang Median", quantil(d_mttr, 0.50)),
        ("MTTR-Rueckgang 95. Perzentil", quantil(d_mttr, 0.95)),
        ("Agentenminuten-Rueckgang 5. Perzentil", quantil(d_min, 0.05)),
        ("Agentenminuten-Rueckgang Median", quantil(d_min, 0.50)),
        ("Agentenminuten-Rueckgang 95. Perzentil", quantil(d_min, 0.95)),
    ]
    print("\nRobustheitsanalyse (%d Parameterkombinationen)" % ROBUST_LAEUFE)
    with open("robustheit.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Groesse", "Wert"])
        for name, wert in zeilen:
            w.writerow([name, round(wert, 4)])
            print(f"  {name:55} {wert * 100:6.1f} %")


def main():
    kalibrieren(BASIS)
    print("Kalibriert: ist_p_wissenstreffer = %.3f, warte_second_level = %.0f min"
          % (BASIS["ist_p_wissenstreffer"], BASIS["warte_second_level"]))

    zeilen = [("Ist", kennzahlen(BASIS, "ist"))]
    for name, abw in SZENARIEN.items():
        p = deepcopy(BASIS); p.update(abw)
        zeilen.append((f"Soll {name}", kennzahlen(p, "soll")))

    spalten = list(zeilen[0][1].keys())
    with open("ergebnisse.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Szenario"] + spalten)
        for name, k in zeilen:
            w.writerow([name] + [round(k[s], 4) for s in spalten])
    for s in spalten:
        print(f"{s:30}" + "".join(f"{k[s]:12.3f}" for _, k in zeilen))

    # Plausibilitaetscheck gegen Brynjolfsson et al. (+15 % Faelle je Stunde)
    ist_k, soll_k = zeilen[0][1], zeilen[2][1]
    print("\nProduktivitaet im Agenten-Kanal (Faelle je Stunde), Soll Basis gegen Ist: %+.1f %%"
          % ((ist_k["Agentenmin_je_Agententicket"] / soll_k["Agentenmin_je_Agententicket"] - 1) * 100))

    # Parameterliste mit Herkunft
    with open("parameter.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Parameter", "Wert", "Herkunft"])
        for k, v in BASIS.items():
            w.writerow([k, v, HERKUNFT.get(k, "ANNAHME")])

    # Sensitivitaet (Soll, Basisfall, je ein Parameter veraendert)
    basis_soll = kennzahlen(BASIS, "soll")
    with open("sensitivitaet.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Parameter", "Wert", "MTTR_h", "Delta_MTTR_h",
                    "Agentenmin_je_Ticket", "Delta_Agentenmin"])
        print("\nSensitivitaet (Soll Basis: MTTR %.2f h, %.2f Agentenmin.)"
              % (basis_soll["MTTR_h"], basis_soll["Agentenmin_je_Ticket"]))
        for par, werte in SENSITIVITAET.items():
            for v in werte:
                p = deepcopy(BASIS); p[par] = v
                k = kennzahlen(p, "soll")
                w.writerow([par, v, round(k["MTTR_h"], 3),
                            round(k["MTTR_h"] - basis_soll["MTTR_h"], 3),
                            round(k["Agentenmin_je_Ticket"], 3),
                            round(k["Agentenmin_je_Ticket"] - basis_soll["Agentenmin_je_Ticket"], 3)])
                print(f"  {par:28} = {v:<5} MTTR {k['MTTR_h']:5.2f} h   Agentenmin. {k['Agentenmin_je_Ticket']:5.2f}")

    breakeven(zeilen[0][1])
    robustheit()

    # LaTeX-Tabelle
    def pct(x): return f"{x*100:.1f}".replace(".", ",") + r"\,\%"
    def num(x, d=2): return f"{x:.{d}f}".replace(".", ",")
    with open("ergebnistabelle.tex", "w") as f:
        f.write("\\begin{tabular}{lrrrr}\n\\hline\n")
        f.write("Kennzahl & " + " & ".join(n for n, _ in zeilen) + " \\\\\n\\hline\n")
        zeilen_def = [
            ("MTTR (Arbeitsstunden)", lambda k: num(k["MTTR_h"])),
            ("FCR netto, prozessweit", lambda k: pct(k["FCR_netto"])),
            ("FCR netto, Agenten-Kanal", lambda k: pct(k["FCR_netto_Agentenkanal"])),
            ("FLR", lambda k: pct(k["FLR"])),
            ("Self-Service-Quote", lambda k: pct(k["SelfService"])),
            ("Agentenminuten je Ticket", lambda k: num(k["Agentenmin_je_Ticket"], 1)),
            ("Tickets je Agent und Monat", lambda k: num(k["Tickets_je_Agent_Monat"], 0)),
        ]
        for titel, fn in zeilen_def:
            f.write(titel + " & " + " & ".join(fn(k) for _, k in zeilen) + " \\\\\n")
        f.write("\\hline\n\\end{tabular}\n")


if __name__ == "__main__":
    main()
