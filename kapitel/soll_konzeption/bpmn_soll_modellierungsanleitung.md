# Modellierungsanleitung Abbildung 7 — BPMN-Modell des Soll-Prozesses

**Kein Bestandteil des Arbeitstextes.** Bauanleitung für draw.io, Camunda Modeler
oder bpmn.io. Konsistent zu Abschnitt 4.3.1 und zum Ist-Modell aus Abbildung 5.
Das fertige PDF ersetzt `abbildungen/soll-prozess-bpmn.pdf` unter Beibehaltung
des Dateinamens.

## Pools und Lanes

1. Pool A: „Anwender" (Black-Box-Pool, keine internen Elemente)
2. Pool B: „IT-Serviceorganisation", drei Lanes von oben nach unten:
   - Lane B1: „KI-Assistenzsystem"
   - Lane B2: „First-Level-Support"
   - Lane B3: „Second-Level-Support"

## Elemente in Lane B1 (KI-Assistenzsystem)

3. Nachrichten-Startereignis: „Störungsmeldung eingegangen"
4. Service Task 1: „Meldung strukturiert erfassen"
5. Service Task 2: „Anliegen erkennen"
6. Exklusives Gateway 1: „Incident?"
7. Endereignis A: „An Request-Prozess übergeben" (Nein-Pfad von Gateway 1)
8. Service Task 3: „Kategorie und Priorität vorschlagen"
9. Exklusives Gateway 2: „Konfidenz ausreichend?"
10. Zusammenführendes exklusives Gateway 3 (ohne Beschriftung, führt die Pfade aus Gateway 2 wieder zusammen)
11. Service Task 4: „Lösungsvorschläge generieren"
12. Exklusives Gateway 4: „Self-Service-fähiger Standardfall?"
13. Service Task 5: „Self-Service-Antwort senden"
14. Exklusives Gateway 5: „Anwender bestätigt Behebung?"
15. Service Task 6: „Ticket dokumentieren und schließen"
16. Endereignis B: „Incident abgeschlossen"
17. Service Task 7: „Übergabezusammenfassung erstellen"

## Elemente in Lane B2 (First-Level-Support)

18. User Task 1: „Vorschlag prüfen und korrigieren"
19. User Task 2: „Lösungsvorschlag prüfen und anwenden"
20. Exklusives Gateway 6: „Störung behoben?"
21. User Task 3: „Ticket dokumentieren und schließen"
22. User Task 4: „Ticket an Fachgruppe zuweisen"

## Elemente in Lane B3 (Second-Level-Support)

23. User Task 5: „Störung im Second Level bearbeiten"
24. User Task 6: „Lösung an First Level zurückmelden"

## Sequenzflüsse (in Reihenfolge)

25. Startereignis → Service Task 1 → Service Task 2 → Gateway 1
26. Gateway 1 → Service Task 3 (Beschriftung: „ja, Incident")
27. Gateway 1 → Endereignis A (Beschriftung: „nein, Service Request")
28. Service Task 3 → Gateway 2
29. Gateway 2 → Gateway 3 (Beschriftung: „ja, Konfidenz ≥ Schwellenwert")
30. Gateway 2 → User Task 1 (Beschriftung: „nein, Konfidenz < Schwellenwert"; Lane-Wechsel B1 → B2)
31. User Task 1 → Gateway 3 (Lane-Wechsel B2 → B1)
32. Gateway 3 → Service Task 4 → Gateway 4
33. Gateway 4 → Service Task 5 (Beschriftung: „ja, Standardfall")
34. Gateway 4 → User Task 2 (Beschriftung: „nein"; Lane-Wechsel B1 → B2)
35. Service Task 5 → Gateway 5
36. Gateway 5 → Service Task 6 (Beschriftung: „ja")
37. Gateway 5 → User Task 2 (Beschriftung: „nein oder keine Rückmeldung"; Lane-Wechsel B1 → B2)
38. Service Task 6 → Endereignis B
39. User Task 2 → Gateway 6
40. Gateway 6 → User Task 3 (Beschriftung: „ja")
41. Gateway 6 → Service Task 7 (Beschriftung: „nein"; Lane-Wechsel B2 → B1)
42. User Task 3 → Endereignis B (Lane-Wechsel B2 → B1)
43. Service Task 7 → User Task 4 (Lane-Wechsel B1 → B2)
44. User Task 4 → User Task 5 (Lane-Wechsel B2 → B3)
45. User Task 5 → User Task 6
46. User Task 6 → User Task 3 (Lane-Wechsel B3 → B2)

## Nachrichtenflüsse (gestrichelt, zwischen den Pools)

47. Pool A → Startereignis („Störungsmeldung")
48. Service Task 1 → Pool A und Pool A → Service Task 1 („Rückfrage" / „Ergänzende Angaben")
49. Service Task 5 → Pool A („Self-Service-Antwort")
50. Pool A → Gateway 5 („Bestätigung bzw. Ablehnung")
51. User Task 2 → Pool A („Lösungsanleitung")
52. Service Task 6 → Pool A und User Task 3 → Pool A („Abschlussmeldung")

## Layout- und Konsistenzhinweise

53. Reihenfolge der Lanes nicht ändern; die KI-Lane liegt oben, damit die Übergänge zum First Level nach unten und die zum Anwender-Pool nach oben verlaufen.
54. Service Tasks mit dem Zahnrad-Symbol, User Tasks mit dem Personen-Symbol kennzeichnen; keine allgemeinen Tasks verwenden, da die Unterscheidung die Aussage des Modells trägt.
55. Benennungen exakt aus dieser Liste übernehmen, damit Fließtext, Abbildung und die Tabelle der Entscheidungsknoten übereinstimmen (im gesetzten Dokument Tabelle 2, da die Anhangtabellen nach dem Literaturverzeichnis folgen).
56. Das Endereignis „Incident abgeschlossen" nur einmal anlegen und beide Abschlusspfade darauf führen, damit die Vergleichbarkeit mit Abbildung 5 erhalten bleibt.
57. Keine weiteren Symbole ergänzen (keine Zeitereignisse, Subprozesse oder Datenobjekte), um die Erweiterung des Kernsets auf Service und User Task begrenzt zu halten.
58. Laut Leitfaden Abschnitt 5.7 werden Abbildungen nicht gerahmt. Beim Export aus bpmn.io den umgebenden Rahmen entfernen.
