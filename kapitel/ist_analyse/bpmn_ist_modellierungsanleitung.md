# BPMN-Ist-Modell – Modellierungsanleitung (Anhang für den Autor)

Kein Bestandteil des Arbeitstextes. Bauanleitung für draw.io, Camunda Modeler oder bpmn.io.

## Pools und Lanes

- **Pool A:** „Anwender" (Black-Box-Pool, keine internen Elemente)
- **Pool B:** „IT-Serviceorganisation", zwei Lanes:
  - **Lane B1** (oben): „First-Level-Support"
  - **Lane B2** (unten): „Second-Level-Support"

## Elemente in Lane B1 (First-Level-Support)

1. Startereignis (Nachrichten-Startereignis): „Störungsmeldung eingegangen"
2. Task 1: „Ticket erfassen"
3. Task 2: „Ticket kategorisieren"
4. Task 3: „Ticket priorisieren"
5. Task 4: „Erstdiagnose durchführen"
6. Exklusives Gateway 1: „Lösung im First Level möglich?"
7. Task 5: „Lösung anwenden"
8. Exklusives Gateway 2: „Störung behoben?"
9. Task 6: „Ticket dokumentieren und schließen"
10. Endereignis: „Incident abgeschlossen"
11. Task 7: „Ticket an Fachgruppe zuweisen"

## Elemente in Lane B2 (Second-Level-Support)

12. Task 8: „Störung im Second Level bearbeiten"
13. Task 9: „Lösung an First Level zurückmelden"

## Sequenzflüsse (in Reihenfolge)

14. Startereignis → Task 1
15. Task 1 → Task 2 → Task 3 → Task 4
16. Task 4 → Gateway 1
17. Gateway 1 → Task 5 (Beschriftung: „ja")
18. Gateway 1 → Task 7 (Beschriftung: „nein")
19. Task 5 → Gateway 2
20. Gateway 2 → Task 6 (Beschriftung: „ja")
21. Gateway 2 → Task 4 (Beschriftung: „nein"; Rücksprung zur Erstdiagnose)
22. Task 6 → Endereignis
23. Task 7 → Task 8 (Lane-Wechsel B1 → B2)
24. Task 8 → Task 9
25. Task 9 → Task 6 (Lane-Wechsel B2 → B1)

## Nachrichtenflüsse (gestrichelt, zwischen den Pools)

26. Pool A → Startereignis („Störungsmeldung")
27. Task 1 → Pool A und Pool A → Task 1 („Rückfrage" / „Ergänzende Angaben")
28. Task 4 → Pool A und Pool A → Task 4 („Rückfrage zur Diagnose" / „Antwort")
29. Task 5 → Pool A („Lösungsanleitung")
30. Pool A → Gateway 2 bzw. Task 5 („Bestätigung der Behebung")
31. Task 6 → Pool A („Abschlussmeldung")

## Layouthinweise

- Sequenzflüsse durchgängig horizontal von links nach rechts; nur der Rücksprung (Nr. 21) und die Lane-Wechsel (Nr. 23, 25) verlaufen abweichend.
- Pool „Anwender" oberhalb des Pools „IT-Serviceorganisation" platzieren, damit alle Nachrichtenflüsse nach oben zeigen.
- Keine weiteren Symbole (keine Subprozesse, Datenobjekte, Zeitereignisse) ergänzen, um das in Abschnitt 2.3.1 festgelegte Kernset einzuhalten.
