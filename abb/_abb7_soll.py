"""Erzeugt Abbildung 7 (BPMN-Modell des Soll-Prozesses) als SVG und gleicht die
Layoutdaten der BPMN-Quelldateien an.

Aufruf im Ordner abb/:   python3 _abb7_soll.py
Danach:                  rsvg-convert -f pdf -o abb7-bpmn-soll.pdf abb7-bpmn-soll.svg

Kompaktes Layout mit grosser Schrift, damit die Beschriftungen auf der
Querformatseite lesbar bleiben. Aendert sich eine Task-Bezeichnung, muss sie
auch im Fliesstext und in der Tabelle der Entscheidungsknoten angepasst werden.
"""
import re

try:
    from PIL import ImageFont
    _FONT = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
    def breite(text, size):
        return ImageFont.truetype(_FONT, size).getlength(text)
except Exception:                      # ohne Pillow: grobe Schaetzung
    def breite(text, size):
        return len(text) * size * 0.52

BREITE, HOEHE = 1990, 824             # Hoehe begrenzt: die Querformatseite fasst bei voller Breite rund 10 cm
FT, FL, FK = 17, 15, 15                # Task-, Beschriftungs-, Kantenschrift
W, H = 136, 92                         # Standard-Task
Y_KI, Y_KI2, Y_FL, Y_FL2, Y_SL = 232, 340, 484, 604, 739

svg = []
shapes = {}                            # id -> (x, y, w, h) fuer die BPMN-DI
edges = {}                             # id -> Wegpunkte


def text(x, y, s, anker="middle", size=FL, extra=""):
    svg.append(f'<text x="{x}" y="{y}" text-anchor="{anker}" font-size="{size}"{extra}>{s}</text>')


def zeilen(x, y, lines, anker="middle", size=FL, abstand=None):
    abstand = abstand or round(size * 1.2)
    for i, s in enumerate(lines):
        text(x, y + i * abstand, s, anker, size)


GEAR = ('<g transform="translate({x},{y})" stroke="#000" stroke-width="1.3" fill="white"><circle r="6"/><circle r="2.5"/>'
        '<line x1="6" y1="0" x2="8.5" y2="0"/><line x1="4.24" y1="4.24" x2="6.01" y2="6.01"/>'
        '<line x1="0" y1="6" x2="0" y2="8.5"/><line x1="-4.24" y1="4.24" x2="-6.01" y2="6.01"/>'
        '<line x1="-6" y1="0" x2="-8.5" y2="0"/><line x1="-4.24" y1="-4.24" x2="-6.01" y2="-6.01"/>'
        '<line x1="0" y1="-6" x2="0" y2="-8.5"/><line x1="4.24" y1="-4.24" x2="6.01" y2="-6.01"/></g>')
PERSON = ('<g transform="translate({x},{y})" stroke="#000" stroke-width="1.3" fill="white">'
          '<circle cy="-4" r="3.5"/><path d="M-7,8 a7,7 0 0 1 14,0"/></g>')
BRIEF = ('<g transform="translate({x},{y})" stroke="#000" stroke-width="1.2" fill="white">'
         '<rect x="-8" y="-5.5" width="16" height="11"/><path d="M-8,-5.5 L0,1 L8,-5.5"/></g>')


def task(i, cx, cy, lines, art, w=W, h=H):
    x, y = cx - w / 2, cy - h / 2
    for s in lines:
        assert breite(s, FT) <= w - 10, (i, s, breite(s, FT), w)
    svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="white" stroke="#000" stroke-width="1.5"/>')
    svg.append((GEAR if art == "service" else PERSON).format(x=x + 13, y=y + 13))
    abstand = 20
    # Textblock etwas nach unten ruecken, damit er das Symbol oben links nicht beruehrt
    versatz = 7 if (len(lines) <= 3 and h >= 88) else (4 if len(lines) <= 3 else 2)
    y0 = cy - (len(lines) - 1) * abstand / 2 + FT * 0.36 + versatz
    zeilen(cx, round(y0, 1), lines, size=FT, abstand=abstand)
    shapes[i] = (x, y, w, h)


def gateway(i, cx, cy):
    r = 26
    svg.append(f'<polygon points="{cx},{cy - r} {cx + r},{cy} {cx},{cy + r} {cx - r},{cy}" fill="white" stroke="#000" stroke-width="1.5"/>')
    svg.append(f'<path d="M{cx - 11},{cy - 11} L{cx + 11},{cy + 11} M{cx + 11},{cy - 11} L{cx - 11},{cy + 11}" stroke="#000" stroke-width="2"/>')
    shapes[i] = (cx - r, cy - r, 2 * r, 2 * r)


def ereignis(i, cx, cy, art):
    dick = 4 if art == "ende" else 1.5
    svg.append(f'<circle cx="{cx}" cy="{cy}" r="18" fill="white" stroke="#000" stroke-width="{dick}"/>')
    if art == "zwischen":
        svg.append(f'<circle cx="{cx}" cy="{cy}" r="14.5" fill="white" stroke="#000" stroke-width="1.5"/>')
    if art in ("start", "zwischen"):
        svg.append(BRIEF.format(x=cx, y=cy))
    shapes[i] = (cx - 18, cy - 18, 36, 36)


def fluss(i, *p):
    d = " ".join(("M" if k == 0 else "L") + f"{x},{y}" for k, (x, y) in enumerate(p))
    svg.append(f'<path d="{d}" fill="none" stroke="#000" stroke-width="1.5" marker-end="url(#arr)"/>')
    edges[i] = p


def nachricht(i, *p):
    d = " ".join(("M" if k == 0 else "L") + f"{x},{y}" for k, (x, y) in enumerate(p))
    svg.append(f'<path d="{d}" fill="none" stroke="#000" stroke-width="1.5" stroke-dasharray="7,5" marker-end="url(#arro)" marker-start="url(#dot)"/>')
    edges[i] = p


def bahn(i, x, y, w, h, name, kopf, fuellung="white"):
    svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fuellung}" stroke="#000" stroke-width="1.5"/>')
    svg.append(f'<rect x="{x}" y="{y}" width="{kopf}" height="{h}" fill="white" stroke="#000" stroke-width="1.5"/>')
    mx, my = x + kopf / 2, y + h / 2
    text(mx, my + 5, name, size=14, extra=f' transform="rotate(-90 {mx} {my})"')
    shapes[i] = (x, y, w, h)


# ---------------------------------------------------------------- Rahmen
svg.append(f'<rect width="{BREITE}" height="{HOEHE}" fill="white"/>')
svg.append('<defs>'
           '<marker id="arr" markerWidth="10" markerHeight="10" refX="9" refY="5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#000"/></marker>'
           '<marker id="arro" markerWidth="10" markerHeight="10" refX="9" refY="5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="white" stroke="#000"/></marker>'
           '<marker id="dot" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto"><circle cx="4" cy="4" r="3" fill="white" stroke="#000"/></marker>'
           '</defs>')
bahn("P_Anwender", 30, 8, 1930, 70, "Anwender", 32)
bahn("P_IT", 30, 112, 1930, 702, "IT-Serviceorganisation", 33)
bahn("L_KI", 63, 112, 1897, 272, "KI-Assistenzsystem", 32, "#f2f2f2")
bahn("L_FL", 63, 384, 1897, 280, "First-Level-Support", 32)
bahn("L_SL", 63, 664, 1897, 150, "Second-Level-Support", 32)

# ---------------------------------------------------------------- Fluesse (zuerst, damit Knoten darueber liegen)
r, g = 18, 26
fluss("f1", (132 + r, Y_KI), (172, Y_KI))
fluss("f2", (308, Y_KI), (330, Y_KI))
fluss("f3", (466, Y_KI), (488, Y_KI))
fluss("f4", (624, Y_KI), (672 - g, Y_KI))
fluss("f5", (672 + g, Y_KI), (784 - g, Y_KI))
fluss("f6", (672, Y_KI + g), (672, Y_FL - H / 2))
fluss("f7", (784 + g, Y_KI), (832, Y_KI))
fluss("f8", (784, Y_KI + g), (784, 322 - r))
fluss("f9", (968, Y_KI), (1016 - g, Y_KI))
fluss("f10", (1016 + g, Y_KI), (1108 - g, Y_KI))
fluss("f11", (1016, Y_KI + g), (1016, Y_FL - H / 2))
fluss("f12", (1084, Y_FL), (1108, Y_FL), (1108, Y_KI + g))
fluss("f13", (1108 + g, Y_KI), (1156, Y_KI))
fluss("f14", (1292, Y_KI), (1340 - g, Y_KI))
fluss("f15", (1340 + g, Y_KI), (1400, Y_KI))
fluss("f16", (1340, Y_KI + g), (1340, Y_FL - H / 2))
fluss("f17", (1536, Y_KI), (1578 - r, Y_KI))
fluss("f17b", (1578 + r, Y_KI), (1646 - g, Y_KI))
fluss("f18", (1646 + g, Y_KI), (1706, Y_KI))
fluss("f19", (1646, Y_KI + g), (1646, 290), (1380, 290), (1380, Y_FL - H / 2))
fluss("f20", (1866, Y_KI), (1906 - r, Y_KI))
fluss("f21", (1421, Y_FL), (1481 - g, Y_FL))
fluss("f23", (1481 + g, Y_FL), (1718, Y_FL))
fluss("f24", (1481, Y_FL - g), (1481, Y_KI2 + 35))  # T16 ist 70 hoch
fluss("f24b", (1561, Y_KI2), (1600, Y_KI2), (1600, Y_FL2 - H / 2))
fluss("f25", (1600, Y_FL2 + H / 2), (1600, Y_SL - H / 2))
fluss("f26", (1668, Y_SL), (1718, Y_SL))
fluss("f27", (1786, Y_SL - H / 2), (1786, Y_FL + H / 2))
fluss("f28", (1786, Y_FL - H / 2), (1786, Y_KI + H / 2))
fluss("f29", (132 + r, Y_FL), (172, Y_FL))
fluss("f30", (308, Y_FL), (398, Y_FL), (398, Y_KI + H / 2))
fluss("f31", (672, Y_FL + H / 2), (672, Y_FL2 - r))
nachricht("m1", (132, 78), (132, Y_KI - r))
nachricht("m2", (104, 78), (104, Y_FL), (132 - r, Y_FL))
nachricht("m3", (1468, Y_KI - H / 2), (1468, 78))
nachricht("m4", (1578, 78), (1578, Y_KI - r))

# ---------------------------------------------------------------- Knoten
ereignis("S1", 132, Y_KI, "start")
task("T1", 240, Y_KI, ["Meldung", "strukturiert", "erfassen"], "service")
task("T2", 398, Y_KI, ["Anliegen", "erkennen"], "service")
task("T3", 556, Y_KI, ["Auf besondere", "Datenkate-", "gorien prüfen"], "service")
gateway("G1", 672, Y_KI)
gateway("G2", 784, Y_KI)
ereignis("E2", 784, 322, "ende")
task("T4", 900, Y_KI, ["Kategorie und", "Priorität", "vorschlagen"], "service")
gateway("G3", 1016, Y_KI)
gateway("G3m", 1108, Y_KI)
task("T5", 1224, Y_KI, ["Lösungs-", "vorschläge", "generieren"], "service")
gateway("G4", 1340, Y_KI)
task("T6", 1468, Y_KI, ["Self-Service-", "Antwort", "senden"], "service")
ereignis("IE1", 1578, Y_KI, "zwischen")
gateway("G5", 1646, Y_KI)
task("T7", 1786, Y_KI, ["Zusammenfassung", "erzeugen und", "Ticket schließen"], "service", w=160)
ereignis("E1", 1906, Y_KI, "ende")
task("T16", 1481, Y_KI2, ["Übergabe-", "zusammenfassung", "erstellen"], "service", w=160, h=70)

ereignis("S2", 132, Y_FL, "start")
task("T8", 240, Y_FL, ["Meldung im", "Dialog", "erfassen"], "user")
task("T9", 672, Y_FL, ["Ticket manuell", "kategorisieren", "und bearbeiten"], "user")
ereignis("E3", 672, Y_FL2, "ende")
task("T10", 1016, Y_FL, ["Vorschlag", "prüfen und", "korrigieren"], "user")
task("T11", 1353, Y_FL, ["Lösungs-", "vorschlag", "prüfen und", "anwenden"], "user")
gateway("G6", 1481, Y_FL)
task("T12", 1786, Y_FL, ["Lösung", "dokumentieren"], "user")
task("T13", 1600, Y_FL2, ["Ticket an", "Fachgruppe", "zuweisen"], "user")
task("T14", 1600, Y_SL, ["Störung im", "Second Level", "bearbeiten"], "user")
task("T15", 1786, Y_SL, ["Lösung an", "First Level", "zurückmelden"], "user")

# ---------------------------------------------------------------- Beschriftungen
zeilen(672, 140, ["Besondere", "Datenkategorien", "enthalten?"])
text(784, 194, "Incident?")
zeilen(1016, 158, ["Konfidenz", "ausreichend?"])
zeilen(1340, 158, ["Self-Service-fähiger", "Standardfall?"])
zeilen(1570, 158, ["Rückmeldung", "eingegangen"], anker="end")
zeilen(1590, 158, ["Anwender bestätigt", "Behebung?"], anker="start")
zeilen(1481, 536, ["Störung", "behoben?"])
zeilen(112, 298, ["Störungsmeldung", "über Portal oder", "Chat eingegangen"], anker="start", size=14)
zeilen(112, 550, ["Telefonische", "Störungsmeldung", "eingegangen"], anker="start", size=14)
zeilen(1906, 284, ["Incident", "abgeschlossen"], size=14)
zeilen(810, 318, ["An Request-Prozess", "übergeben"], anker="start")
zeilen(698, 600, ["Incident manuell", "abgeschlossen"], anker="start")
text(98, 100, "Telefonkanal", anker="end", size=13)
for x, y, s in [(703, 222, "nein"), (680, 294, "ja"), (812, 222, "ja"), (792, 286, "nein"),
                (1047, 222, "ja"), (1024, 294, "nein"), (1371, 222, "ja"), (1304, 322, "nein"),
                (1677, 222, "ja"), (1654, 280, "nein"), (1513, 474, "ja"), (1489, 436, "nein")]:
    text(x, y, s, anker="start", size=FK)

kopf = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{BREITE}" height="{HOEHE}" viewBox="0 0 {BREITE} {HOEHE}" '
        f'font-family="Arial, Helvetica, sans-serif" font-size="14">')
open("abb7-bpmn-soll.svg", "w", encoding="utf-8").write(kopf + "".join(svg) + "</svg>\n")


# ---------------------------------------------------------------- BPMN-DI angleichen
def zahl(v):
    return ("%.1f" % v).rstrip("0").rstrip(".")


def di_neu():
    out = ['<bpmndi:BPMNDiagram id="Diag"><bpmndi:BPMNPlane id="Plane" bpmnElement="Collab">']
    for i, (x, y, w, h) in shapes.items():
        attr = ' isHorizontal="true"' if i[0] in "PL" else (' isMarkerVisible="true"' if i[0] == "G" else "")
        out.append(f'<bpmndi:BPMNShape id="{i}_di" bpmnElement="{i}"{attr}><dc:Bounds x="{zahl(x)}" y="{zahl(y)}" width="{zahl(w)}" height="{zahl(h)}"/></bpmndi:BPMNShape>')
    for i, p in edges.items():
        out.append(f'<bpmndi:BPMNEdge id="{i}_di" bpmnElement="{i}">' + "".join(f'<di:waypoint x="{zahl(x)}" y="{zahl(y)}"/>' for x, y in p) + '</bpmndi:BPMNEdge>')
    out.append('</bpmndi:BPMNPlane></bpmndi:BPMNDiagram></bpmn:definitions>')
    return "".join(out)


for pfad in ("abb7-bpmn-soll.bpmn", "../doku/abb7-soll.bpmn"):
    try:
        b = open(pfad, encoding="utf-8").read()
    except FileNotFoundError:
        continue
    kopfteil = b.split("<bpmndi:BPMNDiagram", 1)[0]
    ids = set(re.findall(r'<bpmn:(?:\w+) id="([A-Za-z]\w*)"', kopfteil)) - {"Collab", "Proc_IT", "LS"}
    ids = {i for i in ids if not i.startswith("med_")}
    fehlend = ids - set(shapes) - set(edges)
    assert not fehlend, fehlend
    open(pfad, "w", encoding="utf-8").write(kopfteil + di_neu() + "\n")
