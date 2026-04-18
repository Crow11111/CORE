# MASTERPLAN: FIX OMEGA BACKEND (CRASH-LOOP)

**Vektor:** 2210 | **Delta:** 0.049 | **Status:** PENDING O2 AUDIT

## 1. ZIEL
Das native OMEGA-Backend auf dem VPS (`omega-backend.service`, Port 32800) befindet sich in einem Crash-Loop (ModuleNotFoundError: `google.genai`, `langchain_ollama`, etc.).
Das Ziel ist die Wiederherstellung der Funktionalität, sodass der Dienst stabil läuft ("active (running)") und Kongs Routing-Ziele wieder erreichbar sind.

## 2. DELEGATION (Der 3-Instanzen-Workflow)
Der Orchestrator (A) führt keine Shell-Befehle aus. Er plant.
Der Auditor (O2) prüft den Plan blind.
Der Worker (Infra Surgeon) führt aus.
Der Auditor (O2) prüft die finale Telemetrie zur Endabnahme.

## 3. ABLAUFPLAN FÜR DEN WORKER (Infra Surgeon)
1. **Diagnose-Schleife:**
   - SSH auf den VPS (mit dem Key aus `.env`).
   - Lese das Log: `journalctl -u omega-backend -n 30 --no-pager`.
   - Identifiziere das exakte Modul, das im `ModuleNotFoundError` bemängelt wird.
2. **Reparatur (Installation):**
   - Installiere das fehlende Paket zwingend in der virtuellen Umgebung: `/opt/omega-backend/.venv/bin/pip install <paketname>`.
3. **Neustart & Verifikation:**
   - Starte den Service neu: `systemctl restart omega-backend`.
   - Warte 3 Sekunden.
   - Prüfe erneut das Log (`journalctl`). Falls ein *weiteres* Paket fehlt, wiederhole Schritt 2.
4. **Beweissicherung (Worst-Case-Primat):**
   - Sobald das Backend oben bleibt, generiere den Telemetrie-Beweis: `systemctl status omega-backend --no-pager`.
   - Der Output MUSS `Active: active (running)` enthalten.

## 4. VETO-TRAPS (Für O2 zur finalen Freigabe)
- **Veto**, wenn der Worker einfach "fertig" meldet, ohne den Output von `systemctl status` als Beweis vorzulegen.
- **Veto**, wenn der Status weiterhin `activating (auto-restart)` oder `failed` zeigt.
- **Veto**, wenn der Worker versucht, Pakete global statt im `.venv` zu installieren.