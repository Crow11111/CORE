# OC Brain Reaktivierung – Ausführungsauftrag (gesamter Plan)

**Bezug:** [OC_BRAIN_REAKTIVIERUNG_PLAN.md](OC_BRAIN_REAKTIVIERUNG_PLAN.md) (vollständiger Plan), [OC_BRAIN_PLAN_ADDENDUM_VIDEO_RAG.md](OC_BRAIN_PLAN_ADDENDUM_VIDEO_RAG.md)
**Prinzip:** Alle Stränge A–E durch Team umsetzen lassen. Orchestrator führt nicht aus. Abnahme nur durch Verifizierung (nichts glauben).

---

## 1. Strang A: OC Brain Diagnose und Reparatur

| Aufgabe | Verantwortung | Nachweis |
|---------|---------------|----------|
| SSH VPS, `openclaw doctor` ausführen, Fehler dokumentieren | Security Expert, System Architect | A2: doctor ohne Fehler |
| Config-Fixes: `python -m src.scripts.deploy_openclaw_config_vps` (Env-Injection) | System Architect | Config auf VPS aktuell |
| OpenClaw-Container neustarten | Networking / Security | Container läuft |
| Browser: Config-Seite zeigt Formular, kein "Schema unavailable" | System Architect / Judge | A1: Formular sichtbar |

---

## 2. Strang B: Lokales LLM auf Hostinger (Ollama)

| Aufgabe | Verantwortung | Nachweis |
|---------|---------------|----------|
| Ollama auf VPS installieren (install.sh), Port 11434 | Networking Expert | A3: Ollama antwortet |
| Modell pullen (z. B. Qwen2.5:14b oder Mistral:7b) | Networking Expert | `ollama list` zeigt Modell |
| OpenClaw Provider-Config um Ollama erweitern (baseUrl localhost:11434) | System Architect | OC kann Ollama ansprechen |

---

## 3. Strang C: MTH-Profil Vektorisierung (ChromaDB)

| Aufgabe | Verantwortung | Nachweis |
|---------|---------------|----------|
| Ingest-Skript ausführen: `python -m src.scripts.ingest_mth_profile_to_chroma` | DB Expert | A4: mth_user_profile >10 Docs |
| YouTube-Transkript in `world_knowledge` einpflegen (Chunking, rag_reference) | DB Expert, System Architect | world_knowledge enthält RAG-Referenz |
| Sicherstellen: `docs/01_CORE_DNA/MTH_PROFILE_ARCHIVE.md` existiert | DB Expert | A7: Datei vorhanden |

---

## 4. Strang D: RAG-Pipeline und OC-Anbindung

| Aufgabe | Verantwortung | Nachweis |
|---------|---------------|----------|
| RAG-Pipeline: Query → ChromaDB → Context → Ollama (bzw. OC) | System Architect, DB Expert | Konfig/Code vorhanden |
| OpenClaw Agent-Config: RAG/Tool/Skill für ChromaDB-Kontext | System Architect | OC nutzt Kontext |
| Test: OC Brain mit MTH-spezifischer Frage ansprechen | System Architect | A5: Chat antwortet mit LLM |

---

## 5. Strang E: WhatsApp-Anbindung

| Aufgabe | Verantwortung | Nachweis |
|---------|---------------|----------|
| WhatsApp: QR generieren (VPS), **du scannst mit Handy** | Team führt Befehl aus; Pairing nur nach deinem Scan | A6: erst nach Scan gepairt |
| Testnachricht @OC senden, Antwort prüfen | Security / Networking | Logs + manueller Test |
| Routing @Core vs @OC prüfen (siehe WHATSAPP_ROUTING_CORE_OC.md) | System Architect | Doku/Config konsistent |

---

## 6. Abnahme und Verifizierung

**Automatisch (Skript):**
Nach Abschluss der Arbeiten aus Projektroot ausführen:

```powershell
cd /OMEGA_CORE
$env:PYTHONIOENCODING="utf-8"
python -m src.scripts.verify_oc_brain_deliverables
```

- **Exit 0 (VERIFY_OK):** Alle maschinell prüfbaren Nachweise erbracht.
- **Exit 1 (VERIFY_FAIL):** Nachbessern, erneut prüfen.

**Intern durch Orchestrator/Team (mit .env – Nutzer bestätigt nicht):**
- A1: OpenClaw-Gateway-Check im Skript (A1-Proxy) + ggf. Browser/API mit Zugangsdaten aus .env.
- A2: SSH VPS mit .env – `openclaw doctor` (z. B. `openclaw_doctor_vps.py`).
- A3: Ollama auf VPS – curl/Request mit Host aus .env.
- A5: Chat/API-Test mit Token aus .env.
- A6: WhatsApp – **Pairing nur nach Scan mit deinem Handy.** QR erzeugen: auf VPS `docker exec openclaw-admin openclaw channels login whatsapp` ausführen, QR im Terminal scannen. Ohne Scan: nicht gepairt.

Orchestrator/Team führt Verifizierung inkl. Browser/API mit .env-Zugang durch. Kein Abnahme ohne Nachweis; Nutzer muss nicht bestätigen.

---

## 7. Referenzen

| Thema | Pfad |
|-------|------|
| Vollständiger Plan | docs/05_AUDIT_PLANNING/OC_BRAIN_REAKTIVIERUNG_PLAN.md |
| ChromaDB Schema | docs/02_ARCHITECTURE/CORE_CHROMADB_SCHEMA.md |
| OpenClaw Config Deploy | src/scripts/deploy_openclaw_config_vps.py (führt Container-Neustart aus) |
| OC Brain RAG Spec | docs/02_ARCHITECTURE/OC_BRAIN_RAG_SPEC.md |
| MTH-Profil Ingest | src/scripts/ingest_mth_profile_to_chroma.py |
| Verifizierung | src/scripts/verify_oc_brain_deliverables.py |
| WhatsApp-Routing | docs/02_ARCHITECTURE/WHATSAPP_ROUTING_CORE_OC.md |
| Video-RAG Addendum | docs/05_AUDIT_PLANNING/OC_BRAIN_PLAN_ADDENDUM_VIDEO_RAG.md |
