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
