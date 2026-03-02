---
name: expertise-security
description: Fachgebiet Security-Engineering für Schicht-3-Produzenten. Auth-Patterns, Zero-Trust, OWASP. OpenClaw Gateway Token, VPS SSH, Bias-Damper.
---

# Expertise: Security

## Auth-Patterns

| Methode | Einsatz |
|---------|---------|
| Bearer Token | API-Authentifizierung |
| JWT | Session, Claims |
| SSH-Keys | VPS, Scout, Dreadnought |

## Prinzipien

- **Zero-Trust**: Jeder Request verifizieren
- **OWASP Top 10**: Injection, XSS, CSRF adressieren
- **Least Privilege**: Minimale Rechte pro Service

## ATLAS-spezifisch

- **OpenClaw Gateway Token**: Auth für externen Zugriff
- **VPS SSH-Keys**: Kein Passwort-Login
- **Bias Damper**: Anti-Manipulation, Confidence-Threshold für core_brain_registr
