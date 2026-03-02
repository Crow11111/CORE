---
name: risk-assessment
description: Risiko-Checkliste und Auditor-Einschaltung für Schicht-2-Planung
---

# Risk Assessment

## Typische Risiken nach Aufgabentyp

| Aufgabentyp | Risiken |
|-------------|---------|
| **Infrastruktur** | Downtime, Datenverlust, Abhängigkeiten |
| **API** | Breaking Changes, Rate Limits, Auth-Lücken |
| **DB** | Migration-Fehler, Lock-Konflikte, Dateninkonsistenz |
| **Frontend** | UX-Regression, Accessibility, Performance |
| **Security** | Token-Leak, Injection, fehlende Validierung |

## Checkliste: Was kann schiefgehen?

- [ ] Externe Abhängigkeiten (APIs, Services) verfügbar?
- [ ] Breaking Changes für bestehende Clients?
- [ ] Sensible Daten (Keys, PII) exponiert?
- [ ] ND-Belastung (Reizüberflutung, kognitive Last)?
- [ ] Token-Budget ausreichend für Rollback/Retry?

## Wann Auditor einschalten?

| Situation | Auditor |
|-----------|---------|
| Auth, Tokens, PII | security-expert |
| Architektur-Entscheidung, Konflikt | osmium-judge |
| UI/UX, Workflow | nd-analyst, virtual-marc |
| Kosten, Ethik | universal-board |
| Unsicher bei Risiko | osmium-judge (Finale Review) |
