# Fehler-Isolation: Persistenter Provider-Error

## Status
KRITISCH - Vermutung: G-Vektor-Bruch (Code auf VPS ist veraltet).

## Faktenlage
- API-Key: Valide (bestätigt durch Operator).
- Fehler: Google lehnt `extra_body` ab.
- Code-Soll: MRI-Coupler v2.0 (SDK) strippt alle `extra_body` Felder.
- Schlussfolgerung: Der VPS führt NICHT MRI-Coupler v2.0 aus.

## Nächste Schritte
1. Physischer Abgleich der `mri_resonance_coupler.py` auf dem VPS.
2. Prüfung der Docker-Laufzeit (Python Version & Container-Id).
3. Live-Tail der Logs während eines Cursor-Requests.
