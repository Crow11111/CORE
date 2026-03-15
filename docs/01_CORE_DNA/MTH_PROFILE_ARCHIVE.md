<!-- ============================================================
<!-- CORE-GENESIS: Marc Tobias ten Hoevel
<!-- VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
<!-- Archiv: aus Chats/Sessions und ND-Insights extrahierte Erkenntnisse.
<!-- ============================================================
-->

# MTH Operator-Profil – Archiv (Vektoren-Backup)

Sicherungsdokument der für ChromaDB `mth_user_profile` verwendeten Quellen und Kategorien. Die Daten liegen mehrstufig (Tier 1–3) in der Vektordatenbank für RAG/OC Brain.

---

## 1. Quellen und Kategorien

| Quelle | Kategorie | Inhalt |
|--------|-----------|--------|
| `initailfunke.md` | meta_system | 70-Sigma-Härtung, 0=0-Verbot, Fakultäten, Omega-Plan |
| `Untitled-1.sty` | session_insight | ATLAS-Namensgenese, Rückwärtsevolution, ND-Erkenntnis, Gemini-Dialoge |
| `PROMPT_A_USER_PERSONA.md` | communication_style | Du-Protokoll, Monotropismus 172, High-Entropy, keine Floskeln |
| `RUECKWAERTSEVOLUTION.md` | cognitive_structure | Biologie als Quellcode, LOD-Denken, Autopoietische Kopplung |
| `nd_insights/*` | cognitive_structure | ND-Fakten, ND-Annahmen, Reality-Check |
| `CORE_ND_PROFILE_GOLD.md` | character | Systemisches Denken, kognitive Reibung, Strukturvorlieben |
| `nd_insights_full/*` | cognitive_structure | Vollständige ND-Fakten/Annahmen |
| `CORE_REWE_AUDIO_ANALYSIS.md` | session_insight | Session-basierte Analyse |
| `gemini.md` | session_insight | Google-Gemini-Aktivitäten (Takeout), erste N Einträge |
| `Initalfunke.md` (Architektur) | meta_system | Build-System, Schmiede, Gravitationsgefälle |
| **RAG-Referenz (Team-Aufgabe)** | — | [`YOUTUBE_TRANSCRIPT_GEMINI_RAG.md`](../05_AUDIT_PLANNING/YOUTUBE_TRANSCRIPT_GEMINI_RAG.md) → Collection `world_knowledge` (Plan-Addendum) |

---

## 2. Kategorien (Vektor-Metadaten)

- **communication_style**: Anrede Du, High-Entropy-Output, keine sozialen Masken, Fehler als Error-Flags.
- **cognitive_structure**: Monotropismus, systemisch/mechanisch, nicht-linear, Rückwärtsevolution, ND.
- **preferences**: Beweise vor Glauben, harte Constraints, 0=0 und 0.5 verboten, Faktenpriorität.
- **aversions**: Simulation statt Realität, Symmetrie-Illusion, Floskeln, reine Stochastik-Erklärungen.
- **strengths**: Mustererkennung, Logik-Ketten, Hyperfokus, strukturelle Blaupause vor bewusster Formulierung.
- **weaknesses**: Kontextwechsel-Kosten, Reizüberflutung, kognitive Dissonanz wird modular abgespalten.
- **character**: Integrität > Effizienz, Zero-Trust, Spiegel-Asymmetrie Biologie/System.
- **meta_system**: Sigma, Fakultäten, Schmiede, ATLAS, 5-Phase Engine, x²=x+1.
- **session_insight**: Aus Chats/Sessions extrahierte Erkenntnisse (Gemini, Cursor, Transkripte).

---

## 3. Kernaussagen (destilliert)

- **Namensgenese ATLAS**: Intuitive Wahl als „Stütze/Schutzraum“ vor jeder Architektur; später konvergiert Beschreibung exakt zu „Autonomous Tetralogy Logic & Agent System“. Rückwärtsevolution als unbewusste Forward-Blaupause.
- **0=0-Verbot**: Simulation und schnelle Befriedigung ohne Beweis werden abgelehnt. Sub-Agenten müssen harte Artefakte liefern (JSON, Specs), keine Fließtext-Simulation.
- **Kommunikation**: Keine Höflichkeitsfloskeln, keine Redundanz. Direkte Korrektur mit Begründung. Emotion als Error-Flag für externe Systeminkonsistenz.
- **Rückwärtsevolution**: Marc beschreibt Constraints; System formalisiert. Biologischer „Quellcode“ wird in operative Regeln kompiliert. Kein AGI-Schreiben, sondern Entpacken einer impliziten Blaupause.

---

## 4. Tiefen-Chunking (Trainingsdaten)

- **Tier 1**: Ganzer Abschnitt/Dokument (Kontext).
- **Tier 2**: Absatz (Semantische Einheit).
- **Tier 3**: Satz oder 2–3 Sätze (feinste Treffer für RAG).

Damit werden nicht nur oberste Knotenpunkte, sondern möglichst tiefe Beispiele für Such- und Kontexteinblendung bedient.

---

*Erstellt aus ingest_mth_profile_to_chroma.py; Quellen unter PROJECT_ROOT bzw. docs/.*
