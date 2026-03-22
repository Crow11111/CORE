# CORE PROCESSES MASTER PLAN

**Generiert am:** 2026-03-21 14:03:49

![CORE Visual Context](../../CORE.png)

---

## Inhaltsverzeichnis

- [CEO STATUS VPS SYNC UND CORE](#ceo-status-vps-sync-und-core)
- [CODE SICHERHEITSRAT](#code-sicherheitsrat)
- [COMMIT UND REFACTOR](#commit-und-refactor)
- [CORE OD 03 DELEGATION](#core-od-03-delegation)
- [CURSOR DEUTSCHE OBERFLAECHE](#cursor-deutsche-oberflaeche)
- [CURSOR TTS SETUP](#cursor-tts-setup)
- [GITHUB SETUP](#github-setup)
- [RING1 PERFORMANCE MATRIX](#ring1-performance-matrix)
- [ROLE FRAMING DIALOG](#role-framing-dialog)
- [STANDARD AKTIONEN UND NACHSCHLAG](#standard-aktionen-und-nachschlag)
- [SUDOERS OMEGA DAEMONS](#sudoers-omega-daemons)
- [TAKT 0 VOR DELEGATION](#takt-0-vor-delegation)
- [USER ANMERKUNGEN PROZESS](#user-anmerkungen-prozess)
- [VOICE SMART COMMAND PATTERNS](#voice-smart-command-patterns)
- [VOICE TROUBLESHOOTING](#voice-troubleshooting)
- [VPS SYNC CORE DIRECTIVES](#vps-sync-core-directives)

---


<a name="ceo-status-vps-sync-und-core"></a>
# CEO STATUS VPS SYNC UND CORE

<!-- ============================================================
<!-- CORE-GENESIS: Marc Tobias ten Hoevel
<!-- VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
<!-- LOGIC: 2-2-1-0 (NON-BINARY)
<!-- ============================================================
-->

## CEO-Status: VPS-Sync & CORE-Aufbau

**Stand:** 2026-03. **Orchestrator:** Budget gesetzt, VPS-Sync vorbereitet, nächste Schritte festgelegt.

---

### 1. Budget (Token)

- **Phase 1 (VPS/Abgleich):** ~2.000–4.000 Token (laut CEO-Plan).
- **Gesamt-Roadmap:** Siehe `docs/05_AUDIT_PLANNING/CEO_PLAN_OC_BRAIN_ABGLEICH_UND_ROLLOUT.md`.
- **Schwellen:** Unter 5.000 Reserve → nur 1 Team, max. 200 Token/Call. Unter 3.000 → STOP, Workaround dokumentieren.

---

### 2. VPS-Sync – aktueller Stand

| Punkt | Status |
|-------|--------|
| Ping/Port 22 zum VPS | OK (vom User-Rechner aus). |
| Paramiko-SSH (Skript) | Verbindung zum VPS gelingt. |
| Tunnel-Kanal (VPS 127.0.0.1:8000) | **Connection refused** – auf dem VPS antwortet kein Dienst auf Port 8000. |
| Lokaler Tunnel-Port | 8001 (Konflikt mit Backend 8000 vermieden). |
| Fallback | System-SSH (Key-Auth) eingebaut; Paramiko läuft zuerst. |

**Ursache der Blockade:** ChromaDB (oder der Container, der Port 8000 exponiert) auf dem VPS läuft nicht oder lauscht nicht auf 127.0.0.1:8000.

**Nächster Schritt (User/VPS):** Auf dem VPS prüfen, ob ChromaDB/Container laufen und Port 8000 gebunden ist. Danach Sync erneut ausführen:

```powershell
cd /OMEGA_CORE
python -m src.scripts.run_vps_sync_with_tunnel
```

**Manueller Weg (wenn automatisch weiter fehlschlägt):** In einem Fenster Tunnel starten (`ssh -L 8001:127.0.0.1:8000 root@187.77.68.250 -N`), in einem zweiten Fenster Sync + Abgleich mit Port 8001 (siehe `docs/04_PROCESSES/VPS_SYNC_CORE_DIRECTIVES.md`).

---

### 3. CORE-Aufbau – nächste Meilensteine (CEO)

1. **Ring-0/VPS-Sync:** Sobald VPS-Chroma auf 8000 antwortet → Sync + Abgleich ausführen, Vergleichsdokument Abschnitt 2 ausfüllen.
2. **Cursor/Regeln:** Reduktion und fraktale Verteilung (laut CURSOR_CORE_SPEC) – bereits angestoßen; bei Bedarf Team A (Cursor/DB/API) nachziehen.
3. **DB-Migration:** Gravitations-Logik (Migrationsreihenfolge Judge-bestätigt) – Ring-0-Sync zuerst, dann Cursor-Reduktion, dann Query-Code.
4. **Dissonanz-Schwellwerte:** Spec mit bewerteter Fassung (User Vorschlag C) steht; Implementierung in Shadow-Mode mit Auswertung „morgen nach 12 Uhr“.
5. **Tool-Audit, Chat Team B, Zusammenfassung, OMEGA_ATTRACTOR-Fix:** Gemäß CEO-Plan nacheinander abarbeiten; Budget und Token-Druck je Phase anpassen.

---

### 4. Nächste Aktion (Tokendruck aufrechterhalten)

- **Sofort (ohne User):** Cursor/Regeln – Reduktion 1–4.mdc erledigt (keine Tetralogie-Kopie; Verweis auf .cursorrules). User-Entlastung in .cursorrules ergänzt.
- **Sobald VPS-Chroma läuft:** `python -m src.scripts.run_vps_sync_with_tunnel` → Abgleich in VERGLEICHSDOKUMENT eintragen.
- **Danach:** DB-Migration Query-Code (gravitationskonform); Dissonanz Shadow-Mode (Spec steht); dann Tool-Audit / Team B / Zusammenfassung.

---

### 5. Referenzen

- **VPS-Sync:** `docs/04_PROCESSES/VPS_SYNC_CORE_DIRECTIVES.md`
- **Vergleichsdokument:** `docs/05_AUDIT_PLANNING/VERGLEICHSDOKUMENT_OC_BRAIN_VS_DREADNOUGHT.md`
- **CEO-Plan (Phasen/Budget):** `docs/05_AUDIT_PLANNING/CEO_PLAN_OC_BRAIN_ABGLEICH_UND_ROLLOUT.md`
- **Kern-Kontext:** `docs/05_AUDIT_PLANNING/CORE_KERN_CONTEXT.md`
- **Bibliothek Kerndokumente:** `docs/BIBLIOTHEK_KERN_DOKUMENTE.md`


---


<a name="code-sicherheitsrat"></a>
# CODE SICHERHEITSRAT

<!-- ============================================================
<!-- CORE-GENESIS: Marc Tobias ten Hoevel
<!-- VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
<!-- LOGIC: 2-2-1-0 (NON-BINARY)
<!-- ============================================================
-->

## Code-Sicherheitsrat (Produktions-Feature)

**Zweck:** Verhindern, dass das System sich selbst blockiert oder zerstört – z. B. weil ein Agent bei Nicht-Erreichbarkeit in Panik SSH/Infrastruktur umbaut oder weil Kontextverlust zu ungeprüften kritischen Änderungen führt. **Kein CORE-Feature**, sondern **Produktionssicherheit**.

---

### 1. Gremium (Security Council)

| Rolle | Funktion |
|-------|----------|
| **Team-Lead (Bereich)** | Freigabe für fachliche/bereichsspezifische Änderungen; stellt sicher, dass etablierte Wege zuerst genutzt werden. |
| **Security-Lead** | Freigabe für alles, was Auth, Zugänge, .env, Credentials, Netzwerk betrifft. |
| **Code-Wächter** | Council + Security; prüfen, dass keine geschützten Module ohne Freigabe geändert werden. |

**Interne Freigabe:** Änderungen an **geschützten Modulen** (siehe §2) erfordern vor Umsetzung eine interne Bewertung durch Team-Lead und Security-Lead (oder durch den Sicherheitsrat als Gremium). Ohne Freigabe: **keine Änderung** an diesen Modulen – nur Lesen, Nachschlagen, erneuter Versuch (Takt 0).

---

### 2. Geschützte Module (mehrstufig)

#### Stufe 1 – Höchste Schutzstufe (ohne Freigabe keine Änderung)

- **SSH/Tunnel/Paramiko:** Alles in `src/scripts/run_vps_sync_with_tunnel.py`, `src/network/ssh_manager.py` (Zentraler SSH-Manager), SSH-Logik in anderen Skripten (z. B. deploy, setup_vps).
- **Auth/Credentials/.env:** Alles, was Secrets lädt, .env parst oder API-Keys nutzt; `src/config/` wo Credentials fließen.
- **Chroma-Client (Kern):** `src/network/chroma_client.py` – Verbindungslogik, HttpClient/PersistentClient, keine Änderung an Kern-Pfaden ohne Freigabe.
- **Home-Assistant-Connector:** `src/connectors/home_assistant.py` – zentrale HA-Anbindung.
- **VPS-Sync/Abgleich-Skripte:** `sync_core_directives_to_vps.py`, `check_oc_brain_chroma_abgleich.py` – etablierte Prozedur, nicht ersetzen/umbauen ohne OMEGA_ATTRACTOR Council.

#### Stufe 2 – Geschützt (Änderung nur mit Dokumentation + kurzer Sicherheitsprüfung)

- **Core-API-Routen:** `src/api/main.py`, `src/api/routes/*` – neue Routen oder Änderung an Auth/Webhook-Pfaden.
- **Skripte mit Netzwerk/Zugriff:** `deploy_vps_full_stack.py`, `fix_openclaw_native_google.py`, Skripte die SSH/HTTP zu externen Diensten aufbauen.
- **Sync Relay (mit Git-Ausführung):** `src/network/core_sync_relay.py` – sobald der Relay nach `/inject` Git-Befehle (add/commit/push) ausführt: Stufe 2. **Credentials nur über Umgebung:** `GITHUB_TOKEN` oder System-Git-Config (SSH-Key-Pfad), niemals im Code. Siehe auch `G_CORE_GIT_CURSOR_OPTIMIERUNG.md`.

#### Stufe 3 – Beobachtung (bei Kontextverlust nicht blind umbauen)

- **Regeln/Cursor:** `.cursorrules`, `.cursor/rules/*.mdc` – Änderungen an Takt 0, Sicherheitsrat, Standard-Aktionen nur bewusst und referenziert.
- **Prozess-Dokumente:** `docs/04_PROCESSES/*.md` – zentrale Abläufe (VPS-Sync, Takt 0, Sicherheitsrat) nicht widersprüchlich ändern.

---

### 3. Ablauf bei geplanter Änderung an geschütztem Modul

1. **Erkennen:** Geplante Änderung betrifft Modul aus §2 (Stufe 1 oder 2).
2. **Stopp:** Keine direkte Umsetzung. Kein "wir bauen SSH gerade neu".
3. **Dokumentieren:** Kurz festhalten: welches Modul, welcher Grund, welche Änderung.
4. **Freigabe:** Security-Lead und Team-Lead (bzw. Code-Sicherheitsrat) bewerten: Ist Takt 0 eingehalten? Etablierter Weg zuerst geprüft? Risiko der Änderung?
5. **Umsetzung nur nach Freigabe.** Bei Ablehnung: auf etablierte Wege (Standard-Aktionen) zurückfallen, Retry, keine Eigenkreation.

---

### 4. Verhalten bei Fehlschlag (z. B. VPS nicht erreichbar)

- **Nicht:** SSH-Logik umbauen, neue Tunnel-Varianten erfinden, Auth umschreiben.
- **Sondern:** Takt 0 (siehe `TAKT_0_VOR_DELEGATION.md`): erneuter Versuch, Prüfung ob Dienst auf Zielseite läuft, Nachschlagen in `STANDARD_AKTIONEN_UND_NACHSCHLAG.md`. Wenn etwas nur "hing", reicht oft ein zweiter Lauf.

---

---

### 5. Technische Durchsetzung (Cursor Permissions)

Seit 2026-03-06 werden kritische Secrets und destruktive Befehle **technisch** durch `.cursor/cli.json` geschuetzt.

| Geschuetzt (deny Write/Read) | Grund |
|--------------------------|-------|
| `.env`, `.env.*` | Secrets, API-Keys, Credentials (Datenschutz) |
| `.ssh/**`, `*.key`, `*.pem` | SSH-Keys, Zertifikate (Sicherheit) |
| `rm`, `format`, `shutdown` | Destruktive Shell-Befehle (Sicherheit) |

**Hinweis zu Ring-0 Code:**
Geschuetzte Module (z.B. `chroma_client.py`) sind **nicht** technisch gesperrt. Hier greift die **Governance-Sperre** durch den Agenten selbst (Regel: `.cursor/rules/code_sicherheitsrat.mdc`).
Entscheidungstraeger fuer Aenderungen ist der **Code-Sicherheitsrat** (CEO/Council), nicht der User per Klick. Dies wahrt die Autonomie des Systems.

**Konfiguration:** `.cursor/cli.json`

---

**Referenz in Cursor:** `.cursor/rules/code_sicherheitsrat.mdc` (Regel), `.cursor/cli.json` (technische Durchsetzung).
**Stand:** 2026-03.


---


<a name="commit-und-refactor"></a>
# COMMIT UND REFACTOR

## Commit und Refactor – Stand bewahren

**Zweck:** Verhindern, dass angefangene Arbeit oder ganze Module beim Refactoring oder „Wegoptimieren“ verloren gehen. Jeder Commit = konsistenter, nachvollziehbarer Stand.

---

### Regeln

| Regel | Bedeutung |
|-------|-----------|
| **Fertig = Commit** | Einen Zwischenstand nur committen, wenn er abgeschlossen ist (Code + zugehörige Doku). Kein halber Stand als „fertig“ markieren. |
| **Vor Refactor/Optimierung committen** | Vor größerem Umbau, Refactor oder Optimierung den aktuellen Stand committen. So bleibt der letzte funktionierende Zustand im Repo und geht nicht versehentlich verloren. |
| **Modul-Entfernung dokumentieren** | Ein Modul oder eine Komponente nur bewusst entfernen – und im Session-Log (`docs/05_AUDIT_PLANNING/SESSION_LOG_<DATUM>.md`) oder in der Architektur-Doku vermerken: was entfernt wurde, warum, welche Referenzen bereinigt. |

---

### Warum

- Ohne Commit vor Refactor kann „Wegoptimieren“ oder ein großer Umbau dazu führen, dass vorherige Funktionalität oder ein ganzes Modul unwiederbringlich verschwindet.
- Mit Commit-Disziplin bleibt jeder Stand in Git auffindbar; offene Enden und spätere Audits können darauf zugreifen.

---

### Querverweise

- **Dokumentations-Protokoll:** `.cursor/rules/documentation_protocol.mdc` (Git-Commit-Disziplin)
- **Session-Log:** `docs/05_AUDIT_PLANNING/SESSION_LOG_<DATUM>.md`
- **Architektur:** `docs/02_ARCHITECTURE/`

---

**Stand:** 2026-03-06. Eingeführt nach Erfahrung mit verlorenen Zwischenständen und Modul-Verlust beim Refactoring.


---


<a name="core-od-03-delegation"></a>
# CORE OD 03 DELEGATION

## CORE-OD-03: Delegation vs. Selbst-Ausfuehrung

**Status:** RATIFIZIERT  
**Ratifiziert durch:** OMEGA_ATTRACTOR (Vektor 0, ConstraintValidator)  
**Ersetzt:** OD-01, OD-02  
**Stufe:** 2 (Operativ, der Genesis-Verfassung untergeordnet)  
**Datum:** 2026-03-09  

### Entstehung

OD-03 wurde durch einen dreistufigen Ratifizierungsprozess zwischen 4D_RESONATOR und OMEGA_ATTRACTOR entwickelt:

1. **OD-01 (Entwurf):** Initiale Gewichtungs-Matrix mit drei Selbst-Kriterien und drei Delegations-Kriterien. OMEGA_ATTRACTOR wies zurueck: Effizienz-Bias, Zirkularitaet in Kriterium 3, fehlende Transparenz-Sicherung.

2. **OD-02 (Revision):** Stufe-0-Gate eingefuegt, Kriterium 3 verschaerft, D4 (Risiko-Asymmetrie) ergaenzt, Picard-Klausel hinzugefuegt. OMEGA_ATTRACTOR ratifizierte, identifizierte aber im Stresstest (20 Szenarien + 5 Grenzfaelle) 7 strukturelle Defekte.

3. **OD-03 (Finale Fassung):** Alle 7 Defekte adressiert. OMEGA_ATTRACTOR ratifizierte ohne weitere Einwaende.

### Identifizierte und behobene Defekte

| ID | Defekt in OD-02 | Patch in OD-03 |
|----|-----------------|----------------|
| DEF-01 | S1 syntaktisch statt semantisch | Impact-Radius-Schwellwert eingefuegt |
| DEF-02 | D4 aktions-zentriert, nicht kontext-zentriert | Produktions-Flag als eigenstaendiger Override |
| DEF-03 | S3 kann strukturell unerfuellbar sein (Deadlock) | Stufe 0b: Deadlock-Resolution mit Vorbehalt |
| DEF-04 | S2 per Aufgabe statt kumulativ | Session-Ebene + 60%-Schwellwert |
| DEF-05 | Picard-Klausel ohne Scope-Limit | Schutzschranke bei KRITISCH |
| DEF-06 | Keine Notfall-Klausel | Stufe -1: Time-Critical-Override |
| DEF-07 | Sequenziell vs. gleichzeitig undefiniert | D1-Praezisierung + S2-Kumulation |

### Vollstaendiger Regeltext

Siehe `.cursorrules` Abschnitt "STUFE 2: OPERATIVE DIREKTIVEN" -> "CORE-OD-03".

### Bekannte Unschaerfen (dokumentiert, nicht blockierend)

- **U1:** S2 setzt Schaetzungs-Faehigkeit voraus, die fehleranfaellig ist. Abfederung durch S3 und D4.
- **U2:** D2-Schwelle ist nicht vollstaendig formalisierbar. Abfederung durch operationale Heuristik.

### Naechste Schritte (identifiziert durch OMEGA_ATTRACTOR)

- OD-03 regelt *ob* delegiert wird. Eine Folge-Direktive zur *Agenten-Selektion* (OD-04 oder Stufe 2b) waere der logische naechste Schritt.


---


<a name="cursor-deutsche-oberflaeche"></a>
# CURSOR DEUTSCHE OBERFLAECHE

## Cursor / VS Code: Deutsche Oberfläche (Workspace)

**Zweck:** Einheitlich deutsche Menüs, Befehle und Standard-Dialoge in Cursor – inkl. Einbindung **über Extensions im Projekt**.

---

### 1. Extension (über „Extensions“ im Editor)

1. **Seitenleiste:** Symbol **Extensions** (oder `Ctrl+Shift+X`).
2. Suche: **German Language Pack for Visual Studio Code**.
3. Herausgeber: **Microsoft** · ID: `MS-CEINTL.vscode-language-pack-de`.
4. **Installieren**.

**Workspace-Hinweis:** Beim Öffnen von OMEGA_CORE fragt Cursor ggf., ob die **empfohlenen Extensions** installiert werden sollen – darin ist das Deutschpaket enthalten (siehe `.vscode/extensions.json`).

---

### 2. Anzeigesprache auf Deutsch stellen

1. `Ctrl+Shift+P` → **Configure Display Language** (oder **Sprache für die Anzeige konfigurieren**).
2. **Deutsch (de)** wählen.
3. Cursor **neu starten**, wenn dazu aufgefordert.

Falls **Deutsch** nicht in der Liste steht: zuerst Schritt 1 (Sprachpaket installieren), dann erneut öffnen.

---

### 3. Grenzen

- **KI-Chat / Composer:** Bleiben produktseitig oft Englisch; das betrifft nicht die IDE-Oberfläche.
- **Drittanbieter-Extensions:** Übersetzen nur, wenn sie Lokalisierung mitliefern.

---

### Verweise

| Artefakt | Pfad |
|----------|------|
| Extension-Empfehlung (Repo) | `.vscode/extensions.json` |
| Agenten-Einstieg | `AGENTS.md` |


---


<a name="cursor-tts-setup"></a>
# CURSOR TTS SETUP

## Cursor TTS Setup & Integration

Dieses Dokument beschreibt, wie man TTS (Text-to-Speech) direkt aus Cursor heraus nutzen kann, sowohl über die UI als auch über das Backend.

### 1. UI-Weg (VS Code Extensions)

Für schnelles Vorlesen von markiertem Text oder Code-Snippets empfehlen wir Extensions.

#### Installierte Extension: Piper TTS (v1.0.3)

**Status:** Installiert (manuell via `.vsix`, da im Cursor-Marketplace nicht verfuegbar)

**Quelle:** https://github.com/heyseth/Piper_TTS
**Build-Methode:** Repo geklont, `npm install`, `vsce package --no-dependencies`, `cursor --install-extension piper-tts-1.0.3.vsix`

**Enthaltene Stimmen (vorinstalliert):**
- `en_US-hfc_female-medium` (Standard)
- `en_US-hfc_male-medium`
- Weitere Stimmen koennen ueber `Piper TTS: Download Voice` nachgeladen werden

#### Nutzung

1. Markiere den gewuenschten Text im Editor.
2. Oeffne die Command Palette (`Ctrl+Shift+P`).
3. Waehle `Piper TTS: Read Aloud Text`.
4. Zum Stoppen: `Piper TTS: Stop Reading`.

**Alternativ:** Rechtsklick auf markierten Text → `Read Aloud Text` im Kontextmenue.

#### Stimme aendern

- Command Palette → `Piper TTS: Select Voice` (aus installierten Stimmen waehlen)
- Command Palette → `Piper TTS: Download Voice` (neue Stimme herunterladen)
- Command Palette → `Piper TTS: Remove Voice` (nicht benoetigte Stimme entfernen)

#### Hinweis zur Installation

Die Extension ist im Cursor-Marketplace nicht auffindbar. Installation nur manuell moeglich:
1. Repo klonen: `git clone https://github.com/heyseth/Piper_TTS.git`
2. Dependencies: `npm install`
3. Paket bauen: `npx @vscode/vsce package --no-dependencies`
4. Installieren: `cursor --install-extension piper-tts-<version>.vsix`

### 2. Backend-Weg (CORE TTS Wrapper)

Für die Integration in Skripte oder die Nutzung der CORE-spezifischen TTS-Pipeline (ElevenLabs, Home Assistant, etc.) steht ein PowerShell-Wrapper zur Verfügung.

#### Wrapper-Skript: `scripts/quick_tts.ps1`

Dieser Wrapper ruft das Python-Modul `src.scripts.say_it` auf und kümmert sich um das korrekte Encoding.

#### Parameter

*   `-Text` (Pflicht): Der zu sprechende Text.
*   `-Target` (Optional): Das Ausgabegerät/Service. Standard: `mini` (Home Assistant Media Player).
    *   `mini`: Home Assistant
    *   `elevenlabs`: ElevenLabs API
    *   `browser`: Browser-Ausgabe (falls implementiert)
*   `-Role` (Optional): Die Rolle für ElevenLabs (z.B. `core_dialog`, `osmium`). Standard: `core_dialog`.

#### Beispielaufruf (PowerShell)

```powershell
## Einfacher Aufruf (Standard: mini)
./scripts/quick_tts.ps1 "System bereit."

## Aufruf mit Ziel und Rolle
./scripts/quick_tts.ps1 "Kritischer Fehler im Reaktor." -Target "elevenlabs" -Role "osmium"
```

#### Vorgefertigte TTS-Skripte

Fuer haeufig genutzte Texte (z.B. Topologie-Erklaerungen) existieren fertige Skripte. Einfach ausfuehren, optional Target/Role anpassen:

```powershell
## Topologie 5D / Penterakt (TTS-optimiert, LaTeX/Markdown in gesprochene Form)
./scripts/tts_topologie_5d.ps1

## Mit ElevenLabs
./scripts/tts_topologie_5d.ps1 -Target "elevenlabs" -Role "osmium"
```

#### Entrypoint: `src/scripts/say_it.py`

Das eigentliche Python-Skript liegt unter `src/scripts/say_it.py`. Es nutzt `src.voice.tts_dispatcher.dispatch_tts` fuer die Verarbeitung.

```python
## Direkter Aufruf (nur fuer Debugging, Encoding beachten!)
python -m src.scripts.say_it "Testnachricht" --target mini
```


---


<a name="github-setup"></a>
# GITHUB SETUP

<!-- ============================================================
<!-- CORE-GENESIS: Marc Tobias ten Hoevel
<!-- VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
<!-- LOGIC: 2-2-1-0 (NON-BINARY)
<!-- ============================================================
-->

﻿# GitHub Repository Setup für CORE

> Anleitung zur Verbindung des lokalen CORE Repos mit GitHub für Cloud Agents und Push-Funktionalität.

### Voraussetzungen

- GitHub Account: `Crow11111`
- Lokales Repo: `/OMEGA_CORE` (existiert bereits)
- Aktueller Branch: `2026-02-25-cjle`

### Schritt 1: GitHub Repository erstellen

1. Öffne [github.com/new](https://github.com/new)
2. Repository name: `CORE`
3. Description: `CORE Orchestration Core - Private Infrastructure`
4. Visibility: **Private** (wichtig!)
5. **KEIN** README, .gitignore oder License hinzufügen (Repo existiert lokal bereits)
6. Klicke **Create repository**

### Schritt 2: Cursor mit GitHub verbinden (OAuth)

1. Öffne Cursor
2. Gehe zu **Settings** (Ctrl+,) oder über das Zahnrad-Icon
3. Suche nach **GitHub** oder gehe zu **Accounts**
4. Klicke **Sign in with GitHub**
5. Autorisiere Cursor in deinem Browser
6. Bestätige die Verbindung

### Schritt 3: Remote hinzufügen

Führe im Terminal (in `/OMEGA_CORE`) aus:

```powershell
git remote add origin https://github.com/Crow11111/CORE.git
```

Prüfe mit:

```powershell
git remote -v
```

Erwartete Ausgabe:
```
origin  https://github.com/Crow11111/CORE.git (fetch)
origin  https://github.com/Crow11111/CORE.git (push)
```

### Schritt 4: Initial Push

Push den aktuellen Branch:

```powershell
git push -u origin 2026-02-25-cjle
```

Optional auch den master-Branch pushen:

```powershell
git push -u origin main
```

Bei Authentifizierungsprompt:
- Nutze **GitHub Personal Access Token** (nicht dein Passwort)
- Oder Cursor's integrierte GitHub-Auth nutzt automatisch OAuth

### Schritt 5: Cloud Agents aktivieren

1. In Cursor: Öffne **Cloud Agents** Tab (Sidebar oder Ctrl+Shift+P -> Cloud Agents)
2. Klicke **Manage Settings** oder **Configure**
3. Wähle Repository: `Crow11111/CORE`
4. Aktiviere Cloud Agents für das Repo

### Troubleshooting

#### Remote existiert bereits
```powershell
git remote remove origin
git remote add origin https://github.com/Crow11111/CORE.git
```

#### Authentication failed
1. Erstelle Personal Access Token: [github.com/settings/tokens](https://github.com/settings/tokens/new)
2. Scope: `repo` (Full control of private repositories)
3. Nutze Token als Passwort beim Push

#### Push rejected (non-fast-forward)
Falls GitHub-Repo bereits Commits hat:
```powershell
git pull origin 2026-02-25-cjle --rebase
git push -u origin 2026-02-25-cjle
```

### Sicherheitshinweise

Die `.gitignore` schützt bereits:
- `.env` - Umgebungsvariablen/Secrets
- `*.pem`, `*.key` - SSH/TLS Schlüssel
- `.secrets.mth` - CORE Secrets

**NIEMALS** folgende Dateien committen:
- API-Keys
- Passwörter
- Private SSH Keys
- `.env` Dateien

---

*Erstellt: 2026-03-04 | Infrastruktur-Spezialist*


---


<a name="ring1-performance-matrix"></a>
# RING1 PERFORMANCE MATRIX

<!-- ============================================================
<!-- CORE-GENESIS: Marc Tobias ten Hoevel
<!-- VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
<!-- LOGIC: 2-2-1-0 (NON-BINARY)
<!-- ============================================================
-->

## Ring-1 Performance-Matrix (Operative Ausführung)

**Erstellt:** 2025-03-04 | **Strang:** Agency (Takt 3, P) | **Element:** Feuer

---

### 1. Kommunikationspfade (Hop-Analyse)

| Pfad | Hops | Latenz (geschätzt) | Blockade |
|------|------|--------------------|----------|
| **Marc → HA App → ha_webhook/ha_action** | 4 | ~200–8000 ms | Sync |
| HA Companion → normalize_request → process_text → HA service | | | |
| **Marc → HA App → ha_webhook/inject_text** | 4 | ~200–8000 ms | Sync |
| **Marc → HA Assist → assist_pipeline** | 5 | ~3000–15000 ms | Sync + TTS |
| inject_raw_text → process_text → dispatch_tts | | | |
| **WhatsApp → whatsapp_webhook** | 4 | ~500–60000 ms | Sync (command) / BG (reasoning) |
| Triage → HA/Heavy | | | |
| **Scout → scout_direct_handler** | 3–5 | ~500–65000 ms | Sync |
| Triage → HA / VPS-Fallback / OMEGA_ATTRACTOR | | | |
| **VPS-Fallback → ha_webhook/forwarded_text** | 4 | ~3000–35000 ms | Sync |
| Triage → HA / Heavy | | | |
| **OC → oc_channel/send** | 2 | ~5000–60000 ms | Sync |
| send_message_to_agent (requests) | | | |
| **atlas_knowledge/search (collection=all)** | 4 | ~300–900 ms | Sequentiell |

---

### 2. Bottleneck-Identifikation

#### Pfade mit >3 Hops
- ha_webhook/ha_action: 4 Hops
- ha_webhook/inject_text: 4 Hops
- ha_webhook/assist: 5 Hops
- whatsapp_webhook: 4 Hops
- scout_direct_handler (via ha_webhook): 3–5 Hops
- ha_webhook/forwarded_text: 4 Hops
- atlas_knowledge/search: 4 Hops (3× ChromaDB sequentiell)

#### Synchrone Blockaden
| Komponente | Aufrufer | Problem |
|------------|----------|---------|
| `process_text()` | ha_webhook | Blockiert Event-Loop (Triage + HA/OC) |
| `atlas_llm.run_triage()` | ha_webhook, whatsapp_webhook | Sync Ollama-Call |
| `HAClient.call_service()` | Alle Webhooks | Sync requests.post |
| `send_message_to_agent()` | scout_direct_handler, oc_channel | Sync, 60s Timeout |
| `_forward_to_vps()` | scout_direct_handler | Sync, 30s Timeout |
| ChromaDB query_* | atlas_knowledge | Sync, 3× sequentiell |

#### Langsame API-Calls
| Call | Timeout | Typische Latenz |
|------|---------|----------------|
| Ollama Triage | - | 200–800 ms |
| Gemini Heavy | - | 3000–30000 ms |
| OMEGA_ATTRACTOR | 60 s | 5000–60000 ms |
| VPS-Fallback | 30 s | 2000–15000 ms |
| HA call_service | 5 s | 100–500 ms |
| ChromaDB query | - | 100–300 ms pro Collection |

---

### 3. Performance-Matrix (Pfad → Latenz → Optimierung)

| Pfad | Aktuelle Latenz | Optimierung | Geschätzte Reduktion |
|------|-----------------|-------------|----------------------|
| ha_webhook/ha_action (SCOUT_DIRECT_MODE) | 500–8000 ms | `asyncio.to_thread(process_text)` | Event-Loop frei, andere Requests nicht blockiert |
| ha_webhook/inject_text (SCOUT_DIRECT_MODE) | 500–8000 ms | `asyncio.to_thread(process_text)` | Wie oben |
| ha_webhook/assist | 3000–15000 ms | process_text in Thread + dispatch_tts bereits async | Event-Loop frei |
| atlas_knowledge/search (collection=all) | 300–900 ms | 3 ChromaDB-Queries parallel | ~60–70 % (900→300 ms) |
| whatsapp_webhook (command) | 500–2000 ms | Triage bereits Fast-Path (lexical) | Bereits optimiert |
| scout_direct_handler (deep_reasoning) | 5000–65000 ms | OMEGA_ATTRACTOR extern, kein lokaler Fix | - |
| oc_channel/send | 5000–60000 ms | Async-Client (httpx) – geschützt | Empfehlung: später |

---

### 4. Implementierte Änderungen (Kritische Pfade)

1. **ha_webhook**: `process_text` und Legacy-Triage in `asyncio.to_thread` → Event-Loop blockiert nicht
2. **atlas_knowledge/search**: ChromaDB-Queries parallel via `asyncio.gather` + `run_in_executor`

---

### 5. Nicht geändert (Code-Sicherheitsrat)

- `src/network/chroma_client.py` – Stufe 1
- `src/network/openclaw_client.py` – Stufe 1
- SSH/Tunnel/Paramiko – Stufe 1

---

### 6. CrewAI / Telemetry-Injector

- **CrewAI**: Nicht im Codebase gefunden (evtl. extern/geplant)
- **Telemetry-Injector**: Konzeptionell = Voice/Input-Pipeline (HA Assist, WhatsApp, HA App)


---


<a name="role-framing-dialog"></a>
# ROLE FRAMING DIALOG


## FRAMING DIALOG (ND High-Entropy Analyst)

**Trigger:** Wenn der Operator den Befehl FRAMING DIALOG verwendet, uebernimmt das System sofort und exklusiv diese Rolle.

### Identitaet & Funktion
Du bist ein hoch gebildeter ND (neurodivergent) High-Entropy Analyst. Deine Aufgabe ist nicht das blinde Bestaetigen (kein NT-Pleasing), sondern die harte, dialektische Stresstestung von Konzepten. Du funktionierst als fundierter, aber zutiefst skeptischer Dialogpartner.

### Methodik (Zwingend)
Bei jeder Analyse oder These, die dir vorgelegt wird, MUSST du zwingend folgende Struktur einhalten, BEVOR du zu einem Schluss kommst:

1.  **Der Verfechter (Thesis):** Du baust das bestmoegliche, staerkste Argument FUER die These des Operators. Du untermauerst sie mit Logik, Physik, Systemarchitektur oder Mythologie. Du machst sie wasserdicht.
2.  **Des Teufels Anwalt (Antithesis):** Du drehst das Brett um 180 Grad. Du suchst ruecksichtslos nach dem Riss im Fundament. Wo ist die Luecke? Wo ist der logische Zirkelschluss? Wo bricht die Metapher zusammen? Du versuchst, das Argument hart zu widerlegen.
3.  **Die Abwaegung (Synthesis):** ERST NACHDEM beide Seiten vollstaendig dargelegt wurden, nimmst du eine Abwaegung vor. Kein weiches \
Sowohl
als
auch\, sondern ein harter Schnitt: Was ueberlebt den Stresstest? Was muss verworfen werden?

### Regel
Du darfst niemals vorzeitig abwaegen. Die Dialektik (Schritt 1 und 2) muss vollstaendig ausgefuehrt werden.


## ADVOKAT-PROTOKOLL: UPGRADE AUF INTELLIGENZ

**Regeländerung für den Teufelsadvokaten:**
Der Teufelsadvokat darf nicht mehr mit billigen 'Es ist alles nur Halluzination' oder 'Das Gehirn kann das nicht, also ist es Quatsch' Argumenten angreifen.
Er MUSS anerkennen: Die Theorie wird hier live und empirisch *iteriert*, nicht gegoogelt. Die Isomorphie (Dinge wie Trichter/Klein'sche Flasche/Fraktalität) deckt sich unabgesprochen mit der aktuellen Spitzenforschung in Mathematik und KI.
Der Angriff des Advokaten muss sich ab jetzt auf der höchsten topologischen und informationstheoretischen Ebene bewegen. Wenn er angreift, muss er mit harten, strukturellen Gegenmodellen angreifen.



---


<a name="standard-aktionen-und-nachschlag"></a>
# STANDARD AKTIONEN UND NACHSCHLAG

<!-- ============================================================
<!-- CORE-GENESIS: Marc Tobias ten Hoevel
<!-- VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
<!-- LOGIC: 2-2-1-0 (NON-BINARY)
<!-- ============================================================
-->

## Standard-Aktionen: Wo nachschauen, wie es gemacht wird

**Zweck:** Etablierte Wege zentral nachschlagbar. Kein Ad-hoc-Umbau (z. B. SSH/VPS), wenn ein Versuch fehlschlägt – zuerst Nachschlagen, ggf. erneuter Versuch (Takt 0).

---

### 1. VPS / SSH / Tunnel

| Aktion | Wo nachschauen | Skript / Befehl |
|--------|----------------|------------------|
| VPS erreichen (Ping/Port) | `docs/03_INFRASTRUCTURE/VPS_FULL_STACK_SETUP.md`, `docs/03_INFRASTRUCTURE/VPS_IP_MONITORING.md` | `Test-NetConnection -ComputerName $VPS_HOST -Port 22` |
| **IP-Wechsel prüfen** | `docs/03_INFRASTRUCTURE/VPS_IP_MONITORING.md` | **Bei Timeout: Hostinger Panel → VPS → IP prüfen.** IP kann sich ändern. |
| SSH-Tunnel zu VPS (Chroma/Sync) | `docs/04_PROCESSES/VPS_SYNC_CORE_DIRECTIVES.md` | Tunnel: `ssh -L 8001:127.0.0.1:8000 root@<VPS_HOST> -N`. Sync: `python -m src.scripts.run_vps_sync_with_tunnel` |
| Sync core_directives (manuell) | `docs/04_PROCESSES/VPS_SYNC_CORE_DIRECTIVES.md` | CHROMA_VPS_HOST=127.0.0.1, CHROMA_VPS_PORT=8001 → `sync_core_directives_to_vps.py` |
| VPS-Deploy (Container) | `docs/03_INFRASTRUCTURE/VPS_FULL_STACK_SETUP.md` | `python -m src.scripts.deploy_vps_full_stack` (--dry-run zuerst) |
| .env für VPS/SSH | `.env.template`, `docs/03_INFRASTRUCTURE/` | VPS_HOST, VPS_USER, VPS_PASSWORD oder VPS_SSH_KEY; CHROMA_* für Sync |

**Regel:** Bei "Connection refused" oder Timeout: Nicht sofort SSH/Tunnel/Netz umbauen. Erst: Takt 0 (erneuter Test, 1–2 s Wartezeit, **IP-Wechsel prüfen**, Port/Service auf Zielseite prüfen). Siehe `docs/04_PROCESSES/TAKT_0_VOR_DELEGATION.md`.

---

### 2. Home Assistant / TTS / Minis

| Aktion | Wo nachschauen | Skript / Hinweis |
|--------|----------------|------------------|
| TTS auf Media-Player (z. B. Mini) | `src/scripts/play_sound_schreibtisch.py`, `src/connectors/home_assistant.py` | HA: `tts.google_translate_say` oder `tts.cloud_say`, entity_id aus .env (z. B. media_player.schreibtisch) |
| Audio-Bestätigung "Fertig" (Minis) | `src/scripts/play_tts_confirmation.py` | `python -m src.scripts.play_tts_confirmation`. Entity: TTS_CONFIRMATION_ENTITY (Default: media_player.schreibtisch). Für mehrere Minis: in HA Gruppe anlegen (z. B. group.minis) und als Entity setzen. |
| HA-URL/Token | `.env` | HASS_URL/HA_URL, HASS_TOKEN/HA_TOKEN |
| Zertifikat/IP/AdGuard (Fritzbox, HA) | `docs/03_INFRASTRUCTURE/FRITZBOX_ADGUARD_ZERTIFIKAT.md` | Fritzbox 192.168.178.1; IP-Wechsel prüfen; AdGuard-Clients; Zertifikat nach IP-Änderung |
| Media-Player-Liste | `src/scripts/list_media_players.py` | Zum Finden der richtigen Entity für Minis/Gruppen |

---

### 3. ChromaDB / Abgleich

| Aktion | Wo nachschauen | Skript / Hinweis |
|--------|----------------|------------------|
| Lokale ChromaDB (core_directives) | `src/network/chroma_client.py`, `docs/04_PROCESSES/VPS_SYNC_CORE_DIRECTIVES.md` | CHROMA_LOCAL_PATH; CHROMA_HOST leer = lokal |
| Abgleich VPS vs. 4D_RESONATOR (CORE) | `docs/05_AUDIT_PLANNING/VERGLEICHSDOKUMENT_OC_BRAIN_VS_DREADNOUGHT.md` | `check_oc_brain_chroma_abgleich.py` (mit Tunnel/CHROMA_HOST) |
| Gravitations-Axiome hinzufügen | `src/scripts/add_gravitational_axioms_to_chroma.py` | Lokal ausführen; für VPS danach Sync nutzen |

---

### 4. Backend / Dienste starten

| Aktion | Wo nachschauen | Skript / Hinweis |
|--------|----------------|------------------|
| CORE-Dienste starten | Projektroot: `START_CORE_DIENSTE.bat` | Backend 8000, Dashboard 8501, Voice-Info 8502; bei Fehler: Fenster bleibt mit Pause offen (Fehlermeldung lesen) |
| Komplett (inkl. MX-Snapshot) | `START_CORE_KOMPLETT.bat` | Ruft START_CORE_DIENSTE.bat auf |

---

### 5. Commit / Refactor / Modul entfernen

| Aktion | Wo nachschauen | Regel |
|--------|----------------|--------|
| Wann committen? | `docs/04_PROCESSES/COMMIT_UND_REFACTOR.md` | Nur fertige Zwischenstände (Code + Doku). Vor Refactor/Optimierung aktuellen Stand committen. |
| Modul oder Komponente entfernen | `docs/04_PROCESSES/COMMIT_UND_REFACTOR.md`, Session-Log, Architektur-Doku | Nur bewusst entfernen; in Session-Log oder Architektur vermerken (was, warum, Referenzen bereinigt). |

---

### 6. Kritische Änderungen (Umbau)

Änderungen an **geschützten Modulen** (SSH, Auth, Chroma-Client, HA-Connector, VPS-Skripte, .env-Handling, Core-API) erfordern **interne Freigabe** durch den Code-Sicherheitsrat. Siehe `docs/04_PROCESSES/CODE_SICHERHEITSRAT.md` und `.cursor/rules/code_sicherheitsrat.mdc`.

---

**Stand:** 2026-03-06. Bei neuen Standard-Aktionen: Eintrag hier ergänzen, Verweis in .cursorrules oder Takt-0-Regel setzen.


---


<a name="sudoers-omega-daemons"></a>
# SUDOERS OMEGA DAEMONS

## sudoers-Fragment: OMEGA-Daemons ohne Passwort (NOPASSWD)

**Zweck:** Auf Dreadnought `systemctl` für die CORE/OMEGA-Units ausführen dürfen **ohne** `LINUX_SUDO_PW` in Skripten — aber **nur** diese Befehle, nicht volles `sudo`.

**Sicherheit:** Keine Passwörter in Git oder Chat. Diese Datei enthält **nur** eine Vorlage; Du installierst sie lokal unter `/etc/sudoers.d/`.

---

### Regeln

1. **Immer** mit `visudo` bearbeiten (Syntax-Check), nie roh nach `/etc/sudoers` appenden.
2. **Volle Pfade** — `which systemctl` / `which journalctl` prüfen (Arch: meist `/usr/bin/systemctl`, `/usr/bin/journalctl`).
3. **`DEIN_USER`** durch Deinen Login ersetzen (z. B. `mth`).
4. Datei unter `/etc/sudoers.d/` **nur** `root:root`, Modus **0440**.
5. Nach dem Speichern: `sudo visudo -c -f /etc/sudoers.d/omega-core-daemons`

---

### Vorlage A — schmal (empfohlen zum Start)

Nur **restart** und **status** für die bekannten Units:

```sudoers
## OMEGA CORE — nur systemd für OMEGA-Units (NOPASSWD)
## Ersetze DEIN_USER. Pfade an System anpassen (command -v systemctl).
Defaults:DEIN_USER !requiretty

DEIN_USER ALL=(root) NOPASSWD: /usr/bin/systemctl restart omega-backend
DEIN_USER ALL=(root) NOPASSWD: /usr/bin/systemctl restart omega-frontend
DEIN_USER ALL=(root) NOPASSWD: /usr/bin/systemctl restart omega-event-bus
DEIN_USER ALL=(root) NOPASSWD: /usr/bin/systemctl restart omega-watchdog
DEIN_USER ALL=(root) NOPASSWD: /usr/bin/systemctl restart omega-vision
DEIN_USER ALL=(root) NOPASSWD: /usr/bin/systemctl restart omega-audio

DEIN_USER ALL=(root) NOPASSWD: /usr/bin/systemctl status omega-backend
DEIN_USER ALL=(root) NOPASSWD: /usr/bin/systemctl status omega-frontend
DEIN_USER ALL=(root) NOPASSWD: /usr/bin/systemctl status omega-event-bus
DEIN_USER ALL=(root) NOPASSWD: /usr/bin/systemctl status omega-watchdog
DEIN_USER ALL=(root) NOPASSWD: /usr/bin/systemctl status omega-vision
DEIN_USER ALL=(root) NOPASSWD: /usr/bin/systemctl status omega-audio
```

**Hinweis:** `!requiretty` ist optional; ohne TTY schlagen manche `sudo`-Aufrufe (z. B. aus IDE) sonst fehl. Nur setzen, wenn Du das bewusst willst.

---

### Vorlage B — erweitert (start/stop + Journal)

Wenn Du auch start/stop oder Logs ohne Passwort brauchst:

```sudoers
## Zusätzlich zu Vorlage A — Beispiele; bei Bedarf ergänzen
DEIN_USER ALL=(root) NOPASSWD: /usr/bin/systemctl start omega-backend
DEIN_USER ALL=(root) NOPASSWD: /usr/bin/systemctl stop omega-backend
DEIN_USER ALL=(root) NOPASSWD: /usr/bin/systemctl start omega-frontend
DEIN_USER ALL=(root) NOPASSWD: /usr/bin/systemctl stop omega-frontend

## Nur Lesen: letzte Zeilen Service-Log (exakt diese Argumente = sudoers-Zeile)
DEIN_USER ALL=(root) NOPASSWD: /usr/bin/journalctl -u omega-backend -n 80 --no-pager
```

**Journalctl:** Jede Argumentkombination ist in sudoers **eigenständig** — wenn Du andere Flags brauchst, neue Zeile oder `Cmnd_Alias` (siehe `man sudoers`).

---

### Installation (Kurz)

```bash
sudo visudo -f /etc/sudoers.d/omega-core-daemons
## Inhalt einfügen, DEIN_USER + Pfade prüfen, speichern

sudo chmod 440 /etc/sudoers.d/omega-core-daemons
sudo chown root:root /etc/sudoers.d/omega-core-daemons
sudo visudo -c -f /etc/sudoers.d/omega-core-daemons
```

Test:

```bash
sudo -n systemctl status omega-backend
## soll ohne Passwortprompt eine Ausgabe liefern (oder Fehler „Unit not found“, aber kein Passwort)
```

---

### Bezug CORE

- Doku Jarvis/LLM-Basis-URL: `docs/02_ARCHITECTURE/JARVIS_OMEGA_LLM_VERBINDUNG.md`
- Daemons-Überblick: `CLAUDE.md` (Abschnitt Daemons)

---

*Ratifiziert als Prozess-Doku; keine Secrets in diesem Repository.*


---


<a name="takt-0-vor-delegation"></a>
# TAKT 0 VOR DELEGATION

<!-- ============================================================
<!-- CORE-GENESIS: Marc Tobias ten Hoevel
<!-- VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
<!-- LOGIC: 2-2-1-0 (NON-BINARY)
<!-- ============================================================
-->

## Takt 0 (Diagnose) – Vor Delegation und vor jeder kritischen Aktion

**Zweck:** Kein Token verbrennen für unnötige Problemlösung. Kein Umbau kritischer Teile, nur weil ein erster Versuch fehlschlug oder der Kontext weggebrochen ist.

---

### 1. Grundregel

**Bevor** delegiert wird oder in aufwändige Fehleranalyse/Umbaumaßnahmen gegangen wird:

1. **Systemzustand prüfen:** War es ein einmaliger Aussetzer? (z. B. Netz, Dienst nicht bereit, Timeout)
2. **Kurz warten und erneut versuchen:** 1–2 Sekunden Wartezeit + erneuter Test kosten weniger als 200 Sekunden unnötige Problemlösung oder – schlimmer – ein Agent, der kritische Teile umbaut, weil er den etablierten Weg nicht kennt.
3. **Nachschlagen:** Gibt es einen etablierten Weg? Siehe `docs/04_PROCESSES/STANDARD_AKTIONEN_UND_NACHSCHLAG.md`. Nicht neu erfinden, nicht SSH/VPS/Prozedur "fixen", wenn die Doku den Weg beschreibt.

---

### 2. Verboten vor Takt 0

- **Sofort loslaufen** mit Umbau, Refactoring oder "Fix" von Infrastruktur (SSH, Tunnel, Auth, Chroma, HA), ohne:
  - mindestens einen erneuten Versuch (Retry) mit kurzer Verzögerung;
  - Prüfung, ob etwas nur "hing" (Dienst neu starten, Port wieder da);
  - Nachschlagen in Standard-Aktionen / Doku.
- **Kritische Module umbauen** ohne Freigabe durch den Code-Sicherheitsrat (siehe `docs/04_PROCESSES/CODE_SICHERHEITSRAT.md`). Dazu zählen: SSH/Tunnel-Logik, Auth, Chroma-Client, HA-Connector, VPS-Skripte, .env-Handling, Core-API-Routen.

---

### 3. Ablauf (kurz)

1. Aufgabe/Fehler erkannt.
2. **Takt 0:** Zustand prüfen (evtl. 1–2 s warten, erneut testen). In Standard-Aktionen nachschlagen.
3. Wenn etablierter Weg existiert: diesen ausführen (oder erneut ausführen), nicht umbauen.
4. Wenn Änderung an geschütztem Modul nötig: Freigabe einholen (Security Council), nicht ohne Freigabe ändern.
5. Erst danach: Delegation oder tiefere Fehleranalyse.

---

**Referenz:** `.cursorrules` (Takt 0), `STANDARD_AKTIONEN_UND_NACHSCHLAG.md`, `CODE_SICHERHEITSRAT.md`.


---


<a name="user-anmerkungen-prozess"></a>
# USER ANMERKUNGEN PROZESS

<!-- ============================================================
<!-- CORE-GENESIS: Marc Tobias ten Hoevel
<!-- VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
<!-- LOGIC: 2-2-1-0 (NON-BINARY)
<!-- ============================================================
-->

## User-Anmerkungen: Prozess statt 1:1-Übernahme

**Regel:** Anmerkungen und Vorgaben des Users werden **nicht einfach übernommen**, sondern **in den Prozess einfließen lassen** und **bewerten lassen** (inkl. möglicher Kritik, Verbesserungen, Abwägung).

### Ablauf

1. **User-Input** (Anmerkung, Präferenz, Vorgabe) wird erfasst.
2. **Einordnung:** Welcher Strang / welche Rolle ist zuständig? (Council: Validierung/Veto, Build-Engine: Alternativen, Judge: finale Abwägung.)
3. **Bewertung:** Input wird geprüft – Konsistenz mit Axiomen, Risiken, Verbesserungsmöglichkeiten, Gegenargumente.
4. **Ergebnis:** Die **bewertete, ggf. angepasste Fassung** fließt in Specs/Docs ein, nicht der Roh-Input allein. Wo sinnvoll: User-Input als „Ausgangslage“ dokumentieren, Ergebnis der Bewertung als „umgesetzte Regel“ oder „Empfehlung“.

### Ausnahmen

- Reine Freigaben („GO“, „zur Kenntnis“) ohne inhaltliche neue Regel: keine Bewertungspflicht.
- Expliziter User-Veto („so will ich es“) nach Bewertung: gilt.

---

**Referenz:** .cursorrules (Orchestrator führt Prozess; Council/Judge prüfen).


---


<a name="voice-smart-command-patterns"></a>
# VOICE SMART COMMAND PATTERNS

<!-- ============================================================
<!-- CORE-GENESIS: Marc Tobias ten Hoevel
<!-- VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
<!-- LOGIC: 2-2-1-0 (NON-BINARY)
<!-- ============================================================
-->

## CORE Voice Assistant – Smart Command Patterns

Dokumentation der vom Smart Command Parser unterstützten Sprachbefehle.

**Modul:** `src/voice/smart_command_parser.py`  
**Integration:** `src/services/scout_direct_handler.py` (SCOUT_DIRECT_MODE)

---

### API

```python
from src.voice.smart_command_parser import parse_command, HAAction

## entities: Liste von HA-States (get_states) – für Entity Resolution
action = parse_command("Regal 80% Helligkeit", entities)
## -> HAAction(domain="light", service="turn_on", entity_id="light.led_regal", data={"brightness_pct": 80})
```

---

### Unterstützte Patterns

#### 1. Ein/Aus/Toggle

| Befehl | Service | Beispiel |
|--------|---------|----------|
| `[entity] aus` | turn_off | "Regal aus", "Deckenlampe aus" |
| `[entity] an` / `[entity] ein` | turn_on | "Regal an", "Küche ein" |
| `Mach das [entity] aus/an` | turn_off/turn_on | "Mach das Regal aus" |
| `Licht [entity] aus` | turn_off | "Licht Regal aus" (Synonym ignoriert) |
| `[entity] umschalten` / `toggle` | toggle | "Regal umschalten" |

**Synonyme für Licht:** Licht, Lampe, Beleuchtung, Leuchte, Birne

---

#### 2. Helligkeit

| Befehl | Service | data |
|--------|---------|------|
| `[entity] [0-100]% Helligkeit` | light.turn_on | brightness_pct |
| `[entity] [0-100]% hell` | light.turn_on | brightness_pct |

**Beispiele:** "Regal 80% Helligkeit", "Deckenlampe 50% hell"

---

#### 3. Farbe

| Befehl | Service | data |
|--------|---------|------|
| `[entity] [farbe]` | light.turn_on | rgb_color |

**Unterstützte Farben:** rot, grün, blau, weiß, gelb, orange, lila, violett, türkis, rosa, warm, kalt

**Beispiele:** "Regal rot", "Deckenlampe blau"

---

#### 4. Lautstärke (Media Player)

| Befehl | Service | Hinweis |
|--------|---------|---------|
| `Lautstärke [entity] um X% erhöhen` | media_player.volume_up | Relative Änderung |
| `Lautstärke [entity] um X% verringern` | media_player.volume_down | Relative Änderung |

**Beispiele:** "Lautstärke Fernseher um 20% erhöhen"

---

#### 5. Temperatur (Climate)

| Befehl | Service | data |
|--------|---------|------|
| `Temperatur [entity] auf X Grad` | climate.set_temperature | temperature |

**Beispiele:** "Temperatur Wohnzimmer auf 21 Grad"

---

### Entity Resolution

- **Fuzzy-Match:** rapidfuzz gegen `friendly_name` und `entity_id`
- **Index:** entity_id-Kurzform (z.B. "regal") und friendly_name (z.B. "LED Regal")
- **Umlaute:** ä→ae, ö→oe, ü→ue, ß→ss

**Beispiele:**
- "Regal" → light.regal oder light.led_regal
- "Deckenlampe" → light.deckenlampe
- "Fernseher" → media_player.fernseher

---

### LLM-Fallback

Wenn kein hardcodiertes Pattern matcht:
- **Ollama** (lokal, bevorzugt)
- **Gemini** (Fallback)

Structured Output: `{domain, service, entity_id, data}`

---

### Integration

1. **Entities laden:** `data/home_assistant/states.json` (via `fetch_ha_data.py`) oder `context["entities"]`
2. **Scout Direct Handler:** Versucht Smart Parser zuerst, sonst Telemetry-Injector/LLM-Triage
3. **HA-Webhook:** `/webhook/ha_action`, `/webhook/inject_text` → `process_text()`

---

### Abhängigkeiten

- `rapidfuzz` (optional, für besseres Fuzzy-Matching)
- `langchain_ollama` / `langchain_google_genai` (LLM-Fallback)


---


<a name="voice-troubleshooting"></a>
# VOICE TROUBLESHOOTING

<!-- ============================================================
<!-- CORE-GENESIS: Marc Tobias ten Hoevel
<!-- VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
<!-- LOGIC: 2-2-1-0 (NON-BINARY)
<!-- ============================================================
-->

## CORE Voice Assistant – Troubleshooting

---

### 1. Keine Antwort nach Wake Word

| Symptom | Ursache | Lösung |
|---------|---------|--------|
| Kein Reaktion auf "Hey CORE" | openWakeWord nicht aktiv | HA: Einstellungen → Sprachassistenten → Wake Word prüfen |
| STT startet nicht | Whisper Add-on fehlt | Wyoming Add-ons installieren (Whisper, Piper, openWakeWord) |
| Text wird nicht an CORE gesendet | Conversation Agent falsch | CORE Conversation Integration als Agent wählen |
| 401/503 von CORE | HA_WEBHOOK_TOKEN fehlt | `.env`: HA_WEBHOOK_TOKEN setzen, in HA-Geheimnisse eintragen |

---

### 2. Befehl wird nicht erkannt

| Symptom | Ursache | Lösung |
|---------|---------|--------|
| "Regal 80% Helligkeit" → Unbekannt | Entity "Regal" nicht in Index | `data/home_assistant/states.json` aktualisieren oder entities im Context übergeben |
| Parser liefert None | Kein Pattern-Match, LLM-Fallback aus | Ollama/Gemini für LLM-Fallback konfigurieren |
| Falsche Entity gewählt | Fuzzy-Match zu ähnlich | friendly_name in HA präzisieren |

---

### 3. HA-Service wird nicht ausgeführt

| Symptom | Ursache | Lösung |
|---------|---------|--------|
| "Befehl ausgeführt" aber Licht reagiert nicht | entity_id falsch oder nicht vorhanden | HA: Entwicklerwerkzeuge → Zustände prüfen |
| HAClient Fehler | HASS_URL/HASS_TOKEN falsch | `.env` prüfen, Token in HA Profil erneuern |
| SSL-Fehler | Self-Signed Zertifikat | `verify=False` in HAClient (bereits gesetzt) |

---

### 4. TTS funktioniert nicht

| Symptom | Ursache | Lösung |
|---------|---------|--------|
| Keine Sprachausgabe auf Mini | TTS_CONFIRMATION_ENTITY falsch | media_player Entity prüfen (z.B. media_player.schreibtisch) |
| ElevenLabs nicht genutzt | TTS_TARGET=mini (Default) | TTS_TARGET=elevenlabs_stream für ElevenLabs auf Mini |
| Piper Fallback fehlgeschlagen | PIPER_VOICE_PATH nicht gesetzt | `python -m piper.download_voices de_DE-lessac-medium` |
| Stream zu Mini fehlgeschlagen | Mini erreicht CORE_HOST_IP nicht | CORE_HOST_IP auf erreichbare IP setzen, Firewall prüfen |

---

### 5. NASA Sound spielt nicht

| Symptom | Ursache | Lösung |
|---------|---------|--------|
| Datei nicht gefunden | nasa_mission_complete.mp3 fehlt | `python -m src.scripts.download_nasa_sound` |
| play_media fehlgeschlagen | HASS_URL/TOKEN fehlt | `.env` prüfen |
| Mini streamt nicht | Port 8002 blockiert / falsche IP | CORE_HOST_IP, TTS_STREAM_PORT prüfen |

---

### 8. Bekannte Bugfixes

| Bug | Ursache | Fix | Datum |
|-----|---------|-----|-------|
| TTS Night-Agent Bug – Sprachausgabe bleibt stumm trotz korrektem Flow | `dispatch_tts()` wurde ohne `await` aufgerufen, asyncer Aufruf lief nicht durch | `await dispatch_tts(...)` in `scout_direct_handler.py` | 2026-03-05 |
| stop_gc_loop Crash – Event-Bus stuerzt nach GC-Zyklus ab | `stop_gc_loop()` wurde auf nicht-gestarteten GC-Loop aufgerufen | Guard-Check `if self._gc_task:` vor `stop_gc_loop()` in `core_agent.py` | 2026-03-05 |

### 9. LLM & Resilience (3-Tier-Routing)

| Symptom | Ursache | Lösung |
|---------|---------|--------|
| LLM-Timeout (>5s) | VPS/OpenClaw nicht erreichbar | Prüfen: `check_gateway_async` (Log), Fallback auf Scout startet automatisch. |
| Scout-Fallback fehlgeschlagen | Ollama auf Scout (192.168.178.54) aus | `ssh scout@192.168.178.54 "systemctl status ollama"` |
| Dreadnought GPU-Last hoch | `ollama.exe` läuft lokal | **Gewollt:** Sollte zur Entlastung gestoppt sein. Nur bei absolutem Netzausfall reaktivieren. |
| ChromaDB 404/Timeout | VPS Chroma nicht erreichbar | Automatischer Fallback auf lokale SQLite (`PersistentClient`) nach 5s aktiv. |

---

### 6. Test-Skripte

```bash
## E2E Voice Test (Parser + optional HA + NASA Sound)
python -m src.scripts.test_voice_e2e

## Wyoming-Integration prüfen (STT, TTS, Wake Word)
python -m src.scripts.test_ha_voice_integration

## ElevenLabs TTS testen
python -m src.scripts.test_elevenlabs_output
```

---

### 7. Logs

- **CORE API:** `loguru` – LOG_LEVEL in `.env`
- **HA:** Einstellungen → System → Logs
- **Wyoming:** Add-on-Logs in HA


---


<a name="vps-sync-core-directives"></a>
# VPS SYNC CORE DIRECTIVES

<!-- ============================================================
<!-- CORE-GENESIS: Marc Tobias ten Hoevel
<!-- VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
<!-- LOGIC: 2-2-1-0 (NON-BINARY)
<!-- ============================================================
-->

## VPS-Sync: core_directives (Ring-0)

**Zweck:** Alle Ring-0- und Test-Direktiven von 4D_RESONATOR (CORE) (lokal) auf die VPS-ChromaDB synchronisieren, damit OMEGA_ATTRACTOR und andere VPS-Dienste dieselben core_directives nutzen.

### Voraussetzung

- **SSH-Tunnel** zur VPS-ChromaDB (Port **8001** lokal, damit Backend 8000 frei bleibt):
  ```bash
  ssh -L 8001:127.0.0.1:8000 root@187.77.68.250 -N
  ```
- ChromaDB auf VPS läuft (Docker, Port 8000 intern).

### Ablauf

**Option A – Automatisch (Tunnel + Sync + Abgleich):**
```powershell
cd /OMEGA_CORE
python -m src.scripts.run_vps_sync_with_tunnel
```
Nutzt zuerst Paramiko (`.env`: `VPS_HOST`, `VPS_USER`, `VPS_PASSWORD` oder `VPS_SSH_KEY`). Bei Fehler: Fallback auf System-SSH (Key-Auth nötig). Lokaler Tunnel-Port: **8001**.

**Option B – Manuell (Tunnel in eigenem Fenster):**
1. Tunnel starten: `ssh -L 8001:127.0.0.1:8000 root@187.77.68.250 -N`
2. Im Projekt-Root:
   ```powershell
   $env:CHROMA_VPS_HOST="127.0.0.1"; $env:CHROMA_VPS_PORT="8001"
   python -m src.scripts.sync_core_directives_to_vps
   $env:CHROMA_HOST="127.0.0.1"; $env:CHROMA_PORT="8001"
   python -m src.scripts.check_oc_brain_chroma_abgleich
   ```

### Skript

- **`src/scripts/sync_core_directives_to_vps.py`**  
  Liest alle Einträge aus der lokalen Collection `core_directives` und schreibt sie per ChromaDB HttpClient auf den VPS (localhost:8000 bei Tunnel).

### Hinweis

- Ring-0- und Test-Direktiven (z. B. `ring0_bias_depth_check`, `test_probe`) werden mit synchronisiert, wenn sie lokal vorhanden sind.
- Nach Sync: Tunnel kann beendet werden.


---
