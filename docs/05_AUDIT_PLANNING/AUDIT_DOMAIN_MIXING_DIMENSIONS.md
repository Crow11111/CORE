# Audit: Vermischung von Domänen / Freiheitsgraden

**Status:** Arbeitsdokument (Review)
**Bezug:** `docs/04_PROCESSES/CANON_REGISTRY_AGENT_BINDUNG.md` §3 (A5 vs. Chroma-Ebene), `.cursor/rules/0_SYSTEM_AXIOMS.mdc` Abgrenzung A5

**Ziel:** Stellen finden, an denen **Resonanz-Axiome**, **Retriever-Metriken**, **Infrastruktur** oder **narrative „Wahrheit“** verknüpft werden — und ob die Grenze **sachlich** passt oder **irreführend** ist.

---

## 1. Klar getrennt (Referenz)

| Ebene | Beispiel | Regelwerk |
|-------|----------|-----------|
| Resonanz-State (A5/A6) | `core_state`, Pacemaker, Trust-Updates | A5/A6, `CrystalGridEngine.apply_operator_query` auf **benannte** Skalen |
| Infrastruktur | Ports, `byte_size`, UUIDs | `int`, Verträge, Live-Checks |
| Embedding-Raum | Chroma-Vektoren, Kosinus-Distanz | **Kein** A5 als „Wahrheitsmetrik“; Zero-Trust bei Treffern |

---

## 2. Hohes Mischungsrisiko (Code)

### 2.1 Chroma-**Distanzen** → `CrystalGridEngine.apply_operator_query`

**Ort:** `src/network/chroma_client.py` — `_apply_crystal_engine_operator`, Aufruf nach `query` u. a. bei `query_session_logs`, `query_core_directives`, `query_simulation_evidence`, weitere Query-Pfade (grep: `result["distances"] = _apply_crystal_engine_operator`).

**Was passiert:** Jede skalare **Abstandsmetrik** aus Chroma (nicht identisch mit „Resonanz-Zustand“ im A5-Sinn) wird durch den **gleichen Operator** wie im Kristall-Logikpfad geschickt.

**Bewertung:** Das ist eine **explizite Kopplung** zweier Räume (Retriever-Metrik ↔ CORE-Operator). Funktional kann es Ranking glätten; **konzeptionell** suggeriert es, Axiom-0-/Gitter-Logik gelte **literal** für Distanzen — was wir in §3 CANON_REGISTRY als **andere Dimension** bezeichnet haben.

**Empfehlung:** Entscheidung dokumentieren: *bewusstes Styling* vs. *echte Semantik*. Optional: Flag `CHROMA_DISTANCE_CRYSTAL_SNAP=0` zum Abschalten / A/B; oder Kommentar „nur UI/Ranking, kein State“.

### 2.2 `snap_to_grid` auf **Sentence-Embeddings**

**Orte:** `add_session_turn`, `ingest_omega_canon_chroma`, `ingest_omega_operational_chroma`, `audit_scout_ollama.py`.

**Bewertung:** Ebenfalls **Vermischung** (E6-Anker-Logik auf Modell-Embeddings). Unbedenklich für **A5-Variablen**, aber **nicht** dasselbe wie `apply_operator_query` auf Trust.

**Empfehlung:** In Modul-Docstrings ein Satz: „Snapping dient Konsistenz im Store, nicht CORE-Resonanz-State.“

### 2.3 `multi_view_client.insert_multi_view` — `score` → `apply_operator_query`

**Ort:** `src/db/multi_view_client.py` (Konvergenz-Score aus Facetten).

**Bewertung:** Hier ist der Score **explizit** als **Resonanz-ähnliche** Größe im Multi-View-Pipeline-Design gedacht — **weniger** falsch als bei rohen Chroma-Distanzen, aber Grenze zu **statistischem** Score aus Embeddings beachten.

**Empfehlung:** `assert_resonance_float` ist konsistent; nur sicherstellen, dass `score` nie direkt aus **reiner** Kosinus-Distanz ohne Definition kommt.

### 2.4 Gravitator: `calculate_resonance` auf Collection-Embeddings

**Ort:** `src/logic_core/gravitator.py`.

**Bewertung:** Routing-Metrik aus Vektorraum — wieder **Retriever-/Topologie-Heuristik**, nicht identisch mit Ticket-11-Trust.

**Empfehlung:** Telemetrie/Tests, ob diese Metrik je mit **benannten** A5-States verwechselt wird (sollte nicht).

---

## 3. Hardware / OS → Resonanz (Grenzfälle)

| Ort | Muster |
|-----|--------|
| `chroma_client._apply_fractal_padding_async` | CPU-Last → `apply_operator_query` → Wartezeit |
| `src/ai/llm_interface.py` | Ähnliche Hardware-Brücke |
| `os_crystal_daemon.py`, `agos_zero_watchdog.py`, `friction_guard.py` | Sensor/Metrik → Snapping |

**Bewertung:** Das ist **bewusst** „physikalische Brücke“ (Metapher + Steuergröße). **Risiko:** Messgröße (0–100 % CPU) wird wie Resonanzskala behandelt — semantisch okay, wenn **nicht** als **A5-Zustand in PG** persistiert ohne Review.

---

## 4. Dokumentation (Anforderung vs. Realität)

### 4.1 `CORE_EICHUNG.md` — Handlungsanweisungen §2 Kennfeld/Schwingung

**Text:** Verknüpft Chroma-Kennfeld, „Schwingung“ bis Δ, und **Axiom 5** (0/1/0.5-Verbot) in **einem** Argumentationsstrang.

**Risiko:** Leser könnte schließen, **A5 gelte für jeden Chroma-Vektor** — widerspricht der präzisierten Abgrenzung in CANON_REGISTRY §3 und `CORE_EICHUNG` §1.2 (neuer Abgrenzungsabsatz).

**Empfehlung:** §2 um einen Satz ergänzen: *A5 bezieht sich auf Resonanz-**Zustandsvariablen** im CORE-Pfad; Chroma bleibt Tensor-/Retrieval-Ebene (siehe CANON_REGISTRY §3).*

### 4.2 Whitepaper / lange DNA-Dokumente

Metaphorische Identifikation Chroma = „Kristall-Engine“ (z. B. unter `docs/01_CORE_DNA/5d/WHITEPAPER/…`). **Wissenschaftlich/Theorie** ≠ **Code-Vertrag**. Für **Implementierer** maßgeblich: CANON + Eichung + dieser Audit.

### 4.3 `ZERO_STATE_FIELD_SCHEMA.md` — `lpis_scores` mit `0.5`

**Kontext:** String-Kodierung `"L:0.5|…"`, nicht A5-State-Variable.

**Empfehlung:** Ein Satz im Schema: Werte sind **Etiketten**, keine CORE-Resonanzfelder.

---

## 5. Bereits gut abgefedert

- **`query_canon_semantic` / `query_operational_semantic` / `query_chromadb`:** `zero_trust_notice` im JSON (kein Fakt ohne Quelle); Text zentral `src/config/chroma_zero_trust_notice.py`.
- **`KERNARBEITER_ORIENTIERUNG.md`:** Soll/Ist, Drift zuerst Vertrag/Live.
- **Pacemaker / temporal_alignment / efference_veto:** arbeiten auf **expliziten** Float-State-Größen mit 0.049-Clamps — **Domäne konsistent** (wenn auch Review auf „Magic Numbers“ sinnvoll).

---

## 6. Nächste Schritte (optional)

1. **CORE_EICHUNG** §2 präzisieren (siehe 4.1).
2. **`chroma_client`:** Policy zu `_apply_crystal_engine_operator` festhalten oder konfigurierbar machen.
3. **Einzeiler** in `ZERO_STATE_FIELD_SCHEMA.md` zu `lpis_scores`.
4. Periodisch: grep `apply_operator_query` / `snap_to_grid` auf **neue** Call-Sites.

---

[REVIEW] Kein PASS/VETO — Liste zur Priorisierung durch Operator/Architect.
