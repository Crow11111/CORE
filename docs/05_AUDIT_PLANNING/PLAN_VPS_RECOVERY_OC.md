# MASTERPLAN: VPS RECOVERY & PATH UNIFICATION (OC ADMIN/BRAIN)

**Vektor:** 2210 | **Delta:** 0.049 | **Status:** PENDING O2 AUDIT

## 1. AUSGANGSLAGE & ZIEL
Durch historische Pfad-Migrationen (`atlas-core` -> `mtho-core` -> `core-core`) wurden auf dem Hostinger-VPS die OpenClaw-Container neu erstellt und an leere Volumes gebunden. Die eigentlichen Nutzdaten (`SOUL.md`, `openclaw.json`) liegen verwaist in einem der alten Ordner.
**Ziel:** Lokalisierung der historischen Daten, Migration nach `/opt/omega-core/`, und Anpassung der Deployment-Skripte auf den neuen kanonischen Standard, bewiesen durch Zero-Trust Telemetrie.

## 2. TEAM-DEFINITION (Das Profil)

### Team-Lead: VPS Recovery Commander
- **Wissen & Skills:** Orchestrierung von SSH-Operationen, Docker-Lifecycle-Management, strikte Einhaltung der Beweislast (Axiom 7).
- **Werkzeuge:** `ssh`, `docker`, `sed`/`grep` (für Code-Anpassungen).
- **Framing:** Du bist paranoid. Du glaubst keinem Skript und keinem Pfad, bis du mit `ls` und `cat` bewiesen hast, dass die Daten dort liegen.
- **Kontext:** `.env` (`OPENCLAW_ADMIN_VPS_HOST`, `VPS_SSH_KEY`), Wiki-Einträge zu Hostinger-Spezifika.

### Specialist 1: Forensic Scout (Daten-Spürhund)
- **Aufgabe:** Verbindet sich per SSH (zwingend mit Identity-File `-i`). Sucht in `/opt/` nach allen Instanzen von `SOUL.md` und `openclaw.json`. Vergleicht Timestamps und Dateigrößen, um das "echte" Gehirn zu identifizieren.

### Specialist 2: Infra Surgeon (Der Migrator)
- **Aufgabe:** Stoppt laufende OC-Container. Verschiebt die identifizierten Nutzdaten exakt nach `/opt/omega-core/openclaw-admin/data/` (bzw. `spine`).
- **Aufgabe 2:** Passt lokal im OMEGA_CORE Workspace alle Deployment-Skripte (speziell `deploy_vps_full_stack.py` und `deploy_openclaw_config_vps.py`) an, sodass sie ab sofort `omega-core` statt `core-core` nutzen.

## 3. SEQUENZIELLER ABLAUF & BEWEISLAST (Worst-Case-Primat)

1. **Schritt 1 (Beweis):** Commander weist Scout an, `/opt/` zu scannen. **Beweis:** Konsolen-Output der gefundenen Dateien mit Timestamps.
2. **Schritt 2 (Sicherung):** Commander weist Surgeon an, Container zu stoppen und Daten nach `/opt/omega-core/` zu verschieben. **Beweis:** `ls -la /opt/omega-core/openclaw-admin/data/workspace/` zeigt das `SOUL.md`.
3. **Schritt 3 (Code-Fix):** Surgeon ersetzt in den Deploy-Skripten `core-core` durch `omega-core`. **Beweis:** `git diff` zeigt die korrekten Ersetzungen.
4. **Schritt 4 (Restart & Telemetrie):** Commander startet die Container auf dem VPS neu (via aktualisiertem Skript). **Beweis:** `docker ps` zeigt die Container `openclaw-admin` und `openclaw-spine` UP.

## 4. VETO-TRAPS
- Falls der SSH-Login scheitert, bricht der Plan sofort ab (kein Raten von Passwörtern).
- Falls keine Altdaten gefunden werden, bricht der Plan ab (es darf kein leeres `/opt/omega-core/` ohne Rücksprache mit dem Operator erzwungen werden).
- Falls die Skripte umgeschrieben werden, bevor die Daten auf dem VPS sicher verschoben wurden, greift das VETO (Verhinderung von neuem Datenverlust).