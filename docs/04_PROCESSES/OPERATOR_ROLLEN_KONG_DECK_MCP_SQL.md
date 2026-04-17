# Operator-Rollen: Kong, Deck, MCP, SQL

**Zielgruppe:** Projekt-Manager / Operator ohne Kong-Vorwissen.  
**Leseregel:** Jeder Abschnitt ist in **WER** (Marc / Cursor-Agent / VPS / niemand) und **WAS** (konkrete Aktion) gegliedert.

**Querverweise:** [`infra/vps/kong/README.md`](../../infra/vps/kong/README.md) · [`docs/04_PROCESSES/STATE_MTLS_PROXY_START.md`](STATE_MTLS_PROXY_START.md) · [`infra/vps/kong/kong-deck-reference.yaml`](../../infra/vps/kong/kong-deck-reference.yaml)

---

## 1. Kong in einem Satz

| WER | WAS |
|-----|-----|
| **VPS** | Betreibt **Kong** als **Reverse-Proxy** vor den Containern: von außen z. B. Host-Port **32776** (und benachbarte Ports laut Verkehrsplan) → interne Services/Routen. |
| **Marc / Cursor-Agent** | Verstehen Kong als **einzigen kontrollierten Einstieg** von außen für die abgebildeten Pfade — nicht als Ersatz für direkte Host-Dienste (z. B. systemd-Backend auf anderem Port), die Kong nur **upstream** erreicht. |

---

## 2. Was ist ein „Deck“?

| WER | WAS |
|-----|-----|
| **Repo (YAML)** | Die Datei `infra/vps/kong/kong-deck-reference.yaml` beschreibt den **Soll-Zustand** der Kong-Services und -Routen (deklarativ, versionierbar). |
| **VPS (laufender Kong)** | Der **live** Kong hält Konfiguration in **einer eigenen Datenbank** — unabhängig vom Git-Stand. |
| **Marc / Cursor-Agent** | Ein **Commit ins Repo** ändert den **laufenden** Kong **nicht**. |
| **Marc** (oder **Agent** nur mit nachgewiesenem Zugriff, siehe Rollentabelle) | **„Deck synchronisieren“** = den **Soll** aus dem Repo (oder gleichwertige Deklaration) in die **laufende** Kong-DB übernehmen — z. B. per **deck sync**, **Kong Admin-API** oder **deklarative Config**, je nach eurem Betriebsmodus (Details: Kong-README im Repo). |

---

## 3. Warum `/status` über Kong?

| WER | WAS |
|-----|-----|
| **Marc / Operator-Prozesse** | Nutzen **einen einheitlichen externen Einstieg**: dieselbe URL/Host-Logik wie andere öffentliche Pfade, statt nur Loopback auf dem VPS-Host. |
| **Skripte (z. B. `verify_vps_stack`)** | Können prüfen, ob **Kong die Route tatsächlich kennt** (und ob der Pfad bis zum Backend stimmig ist) — das ist ein **messbarer** Integritätscheck, nicht nur „Backend antwortet lokal“. |
| **VPS** | Terminiert `/status` gemäß Deck/Admin-Konfiguration und leitet zum Omega-Backend-Upstream weiter. |

---

## 4. Rollentabelle (Kurz)

| Aufgabe | WER | WAS |
|---------|-----|-----|
| **Backup vor Infra-/Kong-Änderung** | **Marc** (empfohlen) **oder Cursor-Agent**, wenn SSH/Zugang wie im Projekt üblich vorhanden | `python -m src.scripts.vps_backup_snapshot` ausführen — Snapshot auf dem VPS **vor** riskanten Änderungen (siehe Kong-README und Backup-Plan-Doku). |
| **Secrets in `/etc/default/omega-backend`** | **Nur Marc (Operator)** | Sensible Werte eintragen/pflegen. **Keine** Cursor-Agenten: sie sollen **keine** Produktiv-Secrets erfinden oder ohne explizite Vorgabe schreiben. |
| **`deck sync` / Kong live aktualisieren** | **Marc** **oder** **Cursor-Agent** | **Nur** wenn **Admin-Token** (bzw. autorisierte Kong-Admin-Zugriffe) **und** erreichbarer **VPS-Zugang** (z. B. SSH) **tatsächlich** vorhanden sind — sonst **niemand** remote „aus dem Nichts“. Trennung: **Repo-Änderung** (Agent/Mark) vs. **Live-Anwendung** (nur mit gültigen Credentials und Operator-Abnahme laut README). |
| **Nur Dokumentation ändern** | **Marc / Agent** | Kein `deck sync` nötig; **laufender** Kong bleibt unverändert bis zur bewussten Synchronisation. |

---

## 5. Zertifikate `state_mtls_proxy`

| WER | WAS |
|-----|-----|
| **Marc** | Client-Zertifikate und Keys bereitstellen bzw. an die dokumentierten Pfade legen; bei Bedarf Umgebungsvariablen setzen (ohne Werte in Doku zu wiederholen). |
| **Cursor-Agent** | Kann lokal den Proxy starten/stoppen **wenn** Dateien/Env gesetzt sind — siehe `STATE_MTLS_PROXY_START.md`. |

**Reihenfolge der Auflösung (Client mTLS):** zuerst **mtho-client** (Standarddateien unter `data/certs/`), **Fallback** **cursor** (`cursor.pem` / `cursor.key`), danach explizite Pfade über **`STATE_PROXY_CERT_PEM`**, **`STATE_PROXY_CERT_KEY`**, optional **`STATE_PROXY_CA`**.

**Eingerichtet heißt:** Dateien existieren **und** der VPS akzeptiert dieses Client-Zertifikat für `/core_api` — sonst startet der Proxy zwar, Anfragen scheitern mit **502**.

---

## 6. SQL vs MCP vs Chroma (kurz)

| WER | WAS |
|-----|-----|
| **Backend / Persistenz** | **`record_event`** und vergleichbare Pfade schreiben in **PostgreSQL** (z. B. Tabelle **`omega_events`** — operatives Ereignisprotokoll). |
| **MCP (`read_handbook` u. a.)** | Zuerst Endpunkt **localhost:8049** (State-mTLS-Proxy zum VPS). **Fallback:** lokale Datei unter **`docs/03_INFRASTRUCTURE/handbooks/`** (kein Ersatz für ein sicheres Secret-Depot). |
| **ChromaDB** | **Semantische Suche** / Vektor-Ähnlichkeit über dokumentierte Collections — **kein** Ersatz für operative Secrets, **kein** Pflicht-Handbuch allein; mit SQL/MCP nicht verwechseln. |

---

## 7. Cursor-Agent vs Marc

| WER | WAS |
|-----|-----|
| **Cursor-Agent** | Kann aus **dieser** Entwicklungsumgebung **SSH**, **rsync** und **Python-Skripte** ausführen, **wenn** der Projekt-`.env` die nötigen **nicht-öffentlichen** Zugangsdaten bereitstellt (Schlüssel, Host, …). **Verbot:** Geheimnisse aus `.env` im Chat/Log **ausgeben**. |
| **Marc** | Liefert fehlende Secrets, bestätigt Live-Änderungen an Kong/systemd, trägt `/etc/default/omega-backend` ein. |
| **Cursor-Agent** (**Grenze**) | Kann **keine** echten Geheimnisse **erfunden** liefern und **keine** sicheren Werte **zuverlässig** in **`/etc/default`** auf dem VPS **setzen**, ohne dass **Marc** die Werte vorgibt oder ein sicherer, auditierbarer Kanal existiert. |

---

*Keine Secrets in diesem Dokument — nur Rollen und Abläufe.*
