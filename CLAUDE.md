# Arbeitsanweisungen für dieses Repo

Bachelorarbeit Tim Wehrens, FOM-Vorlage, Synchronisation mit Overleaf.

## Git-Workflow — wichtigste Regel

**Immer direkt auf `master` committen und pushen. Keine Feature-Branches.**

Overleafs Git-Sync kennt keine Branches und zieht ausschließlich den
Default-Branch. Änderungen auf einem Feature-Branch sind in Overleaf
unsichtbar, der Pull-Knopf bietet dort nichts an.

Zugang: Deploy Key mit *Allow write access*, hinterlegt unter
Repo → Settings → Deploy keys. Die Sandbox wird zwischen Sessions
zurückgesetzt, der private Schlüssel ist dann weg — neues Schlüsselpaar
erzeugen und den Public Key neu hinterlegen.

SSH läuft nur über den Proxy:

```
export GIT_SSH_COMMAND="ssh -o ProxyCommand='socat - PROXY:localhost:%h:%p,proxyport=3128'"
```

## Overleaf

- Compiler: **LuaLaTeX**, nicht pdfLaTeX. `\usepackage[utf8]{luainputenc}`
  in `thesis_main.tex` funktioniert nur dort. Magic Comments in Zeile 1–2
  nicht entfernen.
- Nach jedem Pull: **Clear cached files** (Pfeil neben Recompile), dann
  Recompile. Ohne Cache-Reset bleibt die alte `.bbl` liegen und das
  Literaturverzeichnis wirkt leer, obwohl alles korrekt ist.

## Zitieren

- biblatex, `style=verbose-inote`, Backend biber. Bib-Datei:
  `literatur/literatur.bib`, eingebunden über `\addbibresource`.
- Sinngemäß: `\footcite[\vglf][S.~$\bullet$]{Key}`
- Zwei Quellen: `\footcites[\vglf][S.~$\bullet$]{A}[\vglf][S.~$\bullet$]{B}`
- Wörtlich, ohne "Vgl.": `\footcite[][S.~$\bullet$]{Key}`
- Offene Seitenzahl einheitlich als `S.~$\bullet$`, nicht `\textbullet`.
- Keine Quellen erfinden. Fehlt ein Beleg, darauf hinweisen.
- Nie `t`-präfigierte Feldnamen in der .bib (`tauthor`, `ttitle`) — biber
  liest solche Einträge als leer, die Fußnote gibt dann nur den Key aus.

## Umlaute

Der Fließtext nutzt durchgängig LaTeX-Escapes (`\"a`, `{\ss}`). Beibehalten.
`\ss` niemals direkt vor einem Buchstaben (`ma\ssgeblich` wird als
`\ssgeblich` gelesen) — immer `{\ss}`.

## Schreibstil

Siehe Skill `bachelorarbeit-schreibstil`. Kurz: klassisch-akademisch,
unpersönlich, kein "man", Literaturmeinungen im Konjunktiv I, Fließtext in
Absätzen von 4–8 Sätzen, keine Listen im Haupttext, jedes Unterkapitel
endet mit einer Überleitung.

## Verifikation vor dem Push

Die Sandbox hat kein `texlive-lang-german`, kein `biblatex` und kein
`biber`, ein vollständiger Testlauf ist dort nicht möglich. Prüfbar sind:
Klammer- und Umgebungsbalance, dass jeder zitierte Key in der .bib
existiert, dass jedes `\includegraphics`-Ziel vorhanden ist, und ein
Probelauf mit Attrappen für die fehlenden Pakete.

## Leitfaden-Vorgaben (ITM/ING, Version 1.4, März 2024)

Der maßgebliche Leitfaden liegt im Repo unter
`doku/2023_11_14_Leitfaden-ITM-ING_2024l.pdf` und ist vor jeder Formatfrage
dort nachzuschlagen, nicht aus dem Gedächtnis zu beantworten.
Daraus verbindlich:

- **Abbildungen** werden „abweichend von allen anderen Objekten **unter** der
  Abbildung beschriftet" (5.7). `\caption` also hinter `\includegraphics`.
- **Tabellen**: „Der Titel erscheint **über** der Tabelle" (5.6). `\caption`
  vor der `tabular`-Umgebung.
- `floatrow` deshalb **nicht** laden. Das Paket erzwingt eine einheitliche
  Position für alle Floats und doppelt die Beschriftung, sobald `\caption`
  entgegen der Einstellung platziert wird.
- Abbildungen werden **nicht gerahmt** (5.7).
- **Anhang** steht im Nachspann **hinter** dem Quellenverzeichnis (5.1),
  Reihenfolge: Literaturverzeichnis, Internetquellen, ggf. KI-Verzeichnis,
  Anhang, Eigenständigkeitserklärung.
- Die Nummerierung im Anhang erfolgt mit **großen römischen Ziffern** (5.1),
  also `Anhang I`, `Anhang II`. Nicht `Anhang A`.
- Auf den Vermerk **„Eigene Darstellung" ist zu verzichten** (6.2). Eine
  fehlende Quellenangabe bedeutet bereits, dass die Darstellung vom Autor
  stammt. Bei angelehnten Darstellungen dagegen „In Anlehnung an …".
- Die Zitierweise ist ausdrücklich **nicht** festgelegt (6.2: „hier soll kein
  weiterer Standard etabliert werden"), gefordert ist nur Einheitlichkeit.
  `verbose-inote` ist damit zulässig.
- Fußnotenposition (6.2): bezieht sich der Beleg auf **einen Satz**, steht die
  Fußnote **vor** dem Satzpunkt; bezieht er sich auf eine **ganze Passage**,
  hinter dem letzten Punkt des Absatzes.

## Fallstricke, die schon aufgetreten sind

- `\footcite[...]{key}` mit **einem** optionalen Argument: biblatex liest es
  als Postnote, nicht als Vorbemerkung. Das „Vgl." rutscht dann hinter die
  Quelle. Immer beide Argumente setzen: `\footcite[\vglf][o.~S.]{key}`.
- Bei `\footcites` traegt nur der **erste** Beleg eine Vorbemerkung, der
  zweite bekommt `[]`, sonst steht zweimal „Vgl." in einer Fussnote.
- Werke mit identischem Haupttitel (AXELOS Practice Guides, Rumburg „Metric
  of the Month") brauchen ein `shorttitle`, sonst sind die Kurzbelege in den
  Fussnoten nicht unterscheidbar.
- Mehrfachwerke desselben Autors werden im Text ueber **Kurztitel**
  unterschieden, nicht ueber a/b-Suffixe. Quellenzeilen an Abbildungen und
  Tabellen entsprechend.
- arXiv-Preprints als `@misc` fuehren, nicht als `@online`. Sonst landen sie
  im Verzeichnis der Internetquellen statt im Literaturverzeichnis.
- KI-Verzeichnis (`kapitel/ki_verzeichnis.tex`) ist laut Leitfaden 6.2.4
  Pflicht, sobald KI-Werkzeuge eingesetzt wurden, ebenso die Kurzform der
  Prompts. Der Leitfaden sieht die Prompts im **Anhang** vor; auf Wunsch des
  Verfassers stehen sie stattdessen im KI-Verzeichnis. Das ist eine bewusste
  Abweichung, nicht versehentlich — nicht "zurueckkorrigieren".
- Inhaltlich sind Tool-Zeitraeume, Prompt-Daten und -Wortlaute von Tim zu
  vervollstaendigen.

## Verweise auf Abbildungen und Tabellen (Leitfaden 2.3 und 2.4)

- Abbildungen und Tabellen werden **ausnahmslos im Text referenziert**.
- Die Referenz steht **vor** der Grafik oder auf derselben Seite.
- Sie nennt die vollständige Bezeichnung und wird nicht abgekürzt: „Abbildung 3",
  nicht „Abb. 3".
- Sie wird in den Fließtext integriert: „Abbildung 4 zeigt …".
- Erzeugt wird sie über `\autoref{label}`. Dafür sind in der Präambel
  `\figureautorefname` und `\tableautorefname` gesetzt.
- **Nicht** für Abschnittsverweise verwenden: babel-german setzt
  `\subsectionautorefname` auf „Unterabschnitt". Dort weiterhin
  `Abschnitt~\ref{...}` schreiben.

## Abkürzungen (Leitfaden 2.5)

- „So sparsam wie möglich", nur bei echter Notwendigkeit. Eine Abkürzung, die
  nach ihrer Einführung nicht wieder verwendet wird, gehört gestrichen.
- Vor der ersten Verwendung formal einführen: Begriff ausschreiben, Abkürzung
  in Klammern dahinter. Das Verzeichnis ersetzt die Einführung nicht.
- Alphabetisch sortiert.

## Fußnotenposition (Leitfaden 6.2)

- Bezieht sich der Beleg auf **einen Satz**: Fußnote **vor** den Satzpunkt.
- Bezieht er sich auf eine **ganze Passage**: hinter den letzten Punkt des
  Absatzes.
- Praktische Regel im Repo: steht die Fußnote mitten im Absatz, ist sie
  satzbezogen und gehört vor den Punkt; steht sie am Absatzende, bleibt sie
  dahinter.

## Abbildungen

- Die sieben Abbildungen der Arbeit liegen als PDF **und** SVG in `abb/`,
  benannt `abb1-dsrm` bis `abb7-bpmn-soll`. `abbildungen/` enthaelt nur noch
  die Vorlagen-Assets (fomLogo, unterschrift).
- Erzeugt werden sie per Skript (`_abb_lib.py`, `_abb_a.py`, `_abb_b.py`, beim
  Verfasser). Fuer kleine Korrekturen genuegt das SVG in Inkscape oder draw.io.
- **Abbildung 5 und 7** haben ein Seitenverhaeltnis von rund 2,6:1 und stehen
  auf einer Querformatseite:

```latex
\begin{landscape}
\begin{figure}[H]
	\centering
	\includegraphics[width=\linewidth]{abb/abb7-bpmn-soll.pdf}
	\caption[...]{...}
	\label{fig:soll-prozess}
\end{figure}
\end{landscape}
```

  `[H]` ist zwingend, nicht `[p]`. Mit `[p]` bricht der Float aus der
  `landscape`-Umgebung aus, landet ungedreht spaeter im Text und die Seite
  wird nicht rotiert. `pdflscape` und `float` sind dafuer in der Praeambel
  geladen.
- Wenn eine Task-Bezeichnung in Abbildung 5 oder 7 geaendert wird, muss sie an
  drei Stellen mitgeaendert werden: Abbildung, Fliesstext und die Tabelle der
  Entscheidungsknoten.
