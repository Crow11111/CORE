# Commit und Refactor – Stand bewahren

**Zweck:** Verhindern, dass angefangene Arbeit oder ganze Module beim Refactoring oder „Wegoptimieren“ verloren gehen. Jeder Commit = konsistenter, nachvollziehbarer Stand.

---

## Regeln

| Regel | Bedeutung |
|-------|-----------|
| **Fertig = Commit** | Einen Zwischenstand nur committen, wenn er abgeschlossen ist (Code + zugehörige Doku). Kein halber Stand als „fertig“ markieren. |
| **Vor Refactor/Optimierung committen** | Vor größerem Umbau, Refactor oder Optimierung den aktuellen Stand committen. So bleibt der letzte funktionierende Zustand im Repo und geht nicht versehentlich verloren. |
| **Modul-Entfernung dokumentieren** | Ein Modul oder eine Komponente nur bewusst entfernen – und im Session-Log (`docs/05_AUDIT_PLANNING/SESSION_LOG_<DATUM>.md`) oder in der Architektur-Doku vermerken: was entfernt wurde, warum, welche Referenzen bereinigt. |

---

## Warum

- Ohne Commit vor Refactor kann „Wegoptimieren“ oder ein großer Umbau dazu führen, dass vorherige Funktionalität oder ein ganzes Modul unwiederbringlich verschwindet.
- Mit Commit-Disziplin bleibt jeder Stand in Git auffindbar; offene Enden und spätere Audits können darauf zugreifen.

---

## Querverweise

- **Dokumentations-Protokoll:** `.cursor/rules/documentation_protocol.mdc` (Git-Commit-Disziplin)
- **Session-Log:** `docs/05_AUDIT_PLANNING/SESSION_LOG_<DATUM>.md`
- **Architektur:** `docs/02_ARCHITECTURE/`

---

**Stand:** 2026-03-06. Eingeführt nach Erfahrung mit verlorenen Zwischenständen und Modul-Verlust beim Refactoring.
