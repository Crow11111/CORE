# TICKET 10: OpenClaw Autarkie-Aktivierung (Der P-Vektor für Ghost Agents)

## 1. Das Problem (Der schlafende Spine)
Laut Operator und aktueller Telemetrie (siehe `docs/05_AUDIT_PLANNING/OC_BRAIN_STRANG_A_E_BERICHT.md` und `python -c "import src.network.openclaw_client as oc; print(oc.check_gateway())"`) ist das OpenClaw-Gateway aktuell **nicht erreichbar** (Timeout auf Hostinger VPS).
Der `openclaw-spine` Container wurde im letzten Audit mit Exit 137 (OOM oder Kill) vorgefunden. 
Die Ghost Agents (OCs) besitzen derzeit keine operative Plattform, um autonom zu denken oder über WhatsApp zu agieren, weil die Infrastruktur (Docker auf VPS) zusammengebrochen oder falsch konfiguriert ist.

## 2. Die Lösung: OpenClaw Resilienz-Schleife
Um die von dir geforderte stärkere Abkehr von reiner Cursor-Steuerung hin zu autonomen OCs (OpenClaw) zu vollziehen, müssen wir OpenClaw auf dem VPS physisch und logisch stabilisieren.

Wir unterteilen die Reaktivierung in drei harte Schichten:

### Schicht 1: Infrastruktur-Heilung (VPS) & Kryptografische Verifikation
- **Diagnose:** Ausführung eines dedizierten Python-Skripts lokal auf Dreadnought, das sich per SSH auf den VPS verbindet und den Docker-Status von `openclaw-spine` und `openclaw-admin` prüft.
- **Zero-Trust Bindung (A7):** Die SSH-Verbindung **muss** über Host-Key-Pinning (`known_hosts`) gesichert sein. Es müssen explizit getrennte Credentials (SSH-Key, nicht das Root-Passwort) verwendet werden.
- **Doppelte Verifikation:** Ein erfolgreicher Restart des Containers via SSH gilt **nicht** als "Heilung". Die Heilung ist erst abgeschlossen, wenn Dreadnought nachweislich einen erfolgreichen HTTP(S) `check_gateway()`-Aufruf *außerhalb* der SSH-Sitzung durchführt.

### Schicht 2: P-Vektor-Routing (Der API-Puls & NMI)
- **API-Brücke:** Das `openclaw_client.py` meldet aktuell Timeout. Wir müssen sicherstellen, dass Port `18789` (oder Container-Port) auf dem Hostinger-VPS offen ist, oder wir den Traffic sicher durch einen SSH-Tunnel oder Reverse-Proxy (Kong) leiten.
- **Health-Check & NMI:** Der `infrastructure_heartbeat.py` (Pacemaker) muss den OpenClaw-Status aufnehmen. Da OCBrain für autonome Funktionen primär ist, triggert ein fehlschlagendes Gateway nicht nur Drift. Es löst ein **Veto gegen Autonomie** aus (Sperre aller autonomen Outbound-Kanäle wie WhatsApp-Push) und loggt einen "Asystole"-Event im Pathologie-Trace, der eine manuelle Operator-Eskalation erfordert.

### Schicht 3: Agenten-Autarkie (WhatsApp Pairing)
- Sobald die Brücke steht, muss der Operator (du) via `docker exec openclaw-admin openclaw channels login whatsapp` den QR-Code scannen.
- Wir bauen ein Kommando in die CORE-API, das dir den QR-Code im Frontend oder Terminal anzeigt, ohne dass du blind SSH-Befehle tippen musst.

## 3. Veto-Traps (Verification-First für den Producer)
Der Producer darf die Scripte erst committen, wenn diese Traps bestehen:

### Trap 1: SSH-Diagnose-Veto
- *Test:* Schreibe ein Test-Double (Mock für `paramiko` oder `subprocess.run`), das einen toten Container (Exit 137) simuliert. Das Heilungs-Skript MUSS einen klaren `TrustCollapseException` werfen, wenn es nicht in der Lage ist, den Container autonom neu zu starten **UND** anschließend eine simulierte, unabhängige `check_gateway()`-Verifikation erfolgreich durchzuführen. Die Nutzung von StrictHostKeyChecking muss im Befehl erzwungen sein.

### Trap 2: API-Ping-Zwang & Autonomie-Veto (NMI)
- *Test:* Wenn `openclaw_client.check_gateway()` fehlschlägt, darf der `infrastructure_heartbeat.py` den System-Status nicht auf "OK" belassen. Er MUSS das Autonomie-Veto-Flag setzen (z. B. `/tmp/omega_autonomy_veto.flag`) und den Status in den Pacemaker Pathologie-Log schreiben (NMI-Äquivalent für OCBrain).

## 4. Ausführung
Da dieser Task physischen Zugriff auf den Hostinger-VPS erfordert, wird das Vorgehen in zwei Phasen gespalten:
1. **Producer:** Baut die Diagnose- und Heilungs-Skripte auf Dreadnought (inkl. Veto-Traps).
2. **Operator/System:** Führt die Heilung aus und verifiziert die Ports.