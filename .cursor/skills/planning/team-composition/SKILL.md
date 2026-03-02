---
name: team-composition
description: Entscheidungsmatrix für Rollenzusammensetzung im Schicht-2-Team
---

# Team Composition

## Verfügbare Agenten-Typen

| Kategorie | Agenten |
|-----------|---------|
| **Produzenten** | system-architect, db-expert, api-interface-expert, ux-designer |
| **Auditoren** | security-expert, osmium-judge, nd-analyst, nd-therapist, virtual-marc, universal-board |

## Entscheidungsmatrix: Aufgabentyp → Rollen

| Aufgabentyp | Produzenten | Auditoren |
|-------------|-------------|-----------|
| Infrastruktur/Architektur | system-architect | security-expert, osmium-judge |
| API/Schnittstellen | api-interface-expert | security-expert |
| Datenbank/Schema | db-expert | osmium-judge |
| Frontend/UI | ux-designer | nd-analyst, virtual-marc |
| Security-kritisch | system-architect, api-interface-expert | security-expert (Pflicht) |
| ND-sensibel | ux-designer | nd-analyst, nd-therapist, virtual-marc |
| Ethik/Kosten | — | universal-board, osmium-judge |

## Wann welche Rolle?

- **system-architect**: Struktur, Grenzen, Datenflüsse
- **db-expert**: Schema, Migrationen, Indizes
- **api-interface-expert**: HTTP/WS, externe Integrationen
- **ux-designer**: Dashboards, Admin-UI, Interaktionen
- **security-expert**: Auth, Tokens, sensible Daten
- **osmium-judge**: Finale Review, Konfliktlösung
- **nd-***: Kognitive Last, Co-Regulation, Monotropismus
- **virtual-marc**: User-Veto, Alignment-Check
- **universal-board**: Token, Kosten, Ethik
