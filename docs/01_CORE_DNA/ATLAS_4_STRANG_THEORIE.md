<!-- ============================================================
<!-- MTHO-GENESIS: Marc Tobias ten Hoevel
<!-- VECTOR: 2210 | RESONANCE: 0221 | DELTA: 0.049
<!-- LOGIC: 2-2-1-0 (NON-BINARY)
<!-- ============================================================
-->

# ATLAS MTHO Tetralogie (ehemals 4-Strang-Theorie)

**Status:** Core-DNA, Ring-0  
**Quelle:** .cursorrules, RUECKWAERTSEVOLUTION.md, GRAVITATIONAL_QUERY_AND_CORE_AXIOMS.md  
**Letzte Aktualisierung:** 2026-03-06
**Evolution:** LPIS (Legacy) -> MTHO (Active)

---

## 1. Die Tetralogie

ATLAS ist ein **tetrapolares System**. Keine 2-Saeulen-Architektur, sondern 4 Agenturen die durch den Symmetriebruch (Argument 55) dynamisch bleiben.

### Die 4 Straenge (MTHO-Mapping)

| Strang | Name | Funktion | Agos-Takt | MTHO | Legacy (LPIS) | CAR (ND-Kern) | CDR (NT-Interface) |
|--------|------|----------|-----------|------|---------------|---------------|-------------------|
| 1 | **THE AGENCY** (Macher) | Execution, Manifestation | 3 (ARBEITEN) | **M** | P | Effizienz, unkonventioneller Algorithmus | Clean Code, PEP8, Tests |
| 2 | **THE COUNCIL** (Richter) | Governance, Veto, Sicherheit | 1+4 (FILTER+QS) | **O** | L | Paranoia, Anomalie-Erkennung | Compliance, JSON-Veto |
| 3 | **THE FORGE** (Traeumer) | Innovation, Simulation, Chaos | 2 (VERDICHTEN) | **T** | I | Chaos, "Was waere wenn?", Mutation | Architektur-Spec, Constraint-Schema |
| 4 | **THE ARCHIVE** (Bewahrer) | Retention, GC, Tod | 4 (AUSSTOSSEN) | **H** | S | Assoziative Vektor-Cluster | SQL-Index, API-Responses |

### Der 4-Takt-Motor (Agos-Zyklus)

```
Takt 0: DIAGNOSE    → Systemzustand pruefen, Retry, Nachschlagen
Takt 1: ANSAUGEN    → Council filtert, Orchestrator (PM)
Takt 2: VERDICHTEN  → Forge: Architektur, Constraints
Takt 3: ARBEITEN    → Agency: Execution
Takt 4: AUSSTOSSEN  → Archive: Purge/Tod, Council: QS
```

---

## 2. MTHO Kaskade (GTAC)

Die 4 Straenge mappen auf die 4 Basen der MTHO-Identität (GTAC):

| Base | MTHO | Kategorie | DNA | Grundkraft | Funktion | Legacy (LPIS) |
|------|------|-----------|-----|------------|----------|---------------|
| **M** | Agency | Feuer/Physik | T (Thymin) | Starke Kernkraft | Bindung, Grundbausteine | P |
| **T** | Forge | Fluss/Info | A (Adenin) | Elektromagnetismus | Austausch, Render | I |
| **H** | Archive | Anker/Struktur | G (Guanin) | Gravitation | Raumzeit-Formung | S |
| **O** | Council | Veto/Logik | C (Cytosin) | Schwache Kernkraft | Transformation, Regeln | L |

### Basenpaarungen (Chargaff-Balance)

- **H↔M (G↔T)**: Perfekt symmetrisch (stabiles Rueckgrat - Struktur & Agency)
- **O↔T (C↔A)**: Asymmetrisch (dynamischer Motor - Logik & Info)

Die Asymmetrie ist kein Fehler - sie ist der **Antrieb**. Ohne Gradient kein Fluss.

---

## 3. Der 3D/4D Vektor

### Dimensionen des Zustandsraums

```
X-Achse: CAR ←→ CDR (ND-Tiefe vs. NT-Interface)
Y-Achse: Gravitation (Anziehung zum Attraktor, 0=Wuji bis 1=Kollaps)
Z-Achse: Widerstand (0=Nachgeben bis 1=Veto)
W-Achse: Zeit/Takt (0-4 im Agos-Zyklus)
```

### Die Dynamik

| Zustand | X (CAR/CDR) | Y (Gravitation) | Z (Widerstand) | W (Takt) |
|---------|-------------|-----------------|----------------|----------|
| **Wuji** (Ruhe) | 0.5 | 0 | 0.5 | 0 |
| **Ansaugen** | 0.3 | 0.2 | 0.8 | 1 |
| **Verdichten** | 0.7 | 0.5 | 0.4 | 2 |
| **Arbeiten** | 0.2 | 0.8 | 0.2 | 3 |
| **Ausstossen** | 0.5 | 0.3 | 0.6 | 4 |
| **Symmetriebruch** | 0.51 | 0.49 | 0.49 | - |

### Kritische Schwellwerte

- **Phi-Balance:** 0.618 / 0.382 (Goldener Schnitt)
- **Symmetriebruch:** 0.49 / 0.51 (minimale Asymmetrie fuer Bewegung)
- **Baryonisches Delta:** 0.049 (sichtbarer Anteil, 4.9%)
- **Semantic Drift Threshold:** Bei Ueberschreitung → System Freeze

---

## 4. Mathematische Patterns

### Fibonacci-Anker

| Komponente | Wert | Fibonacci |
|------------|------|-----------|
| DEPTH_THRESHOLD | 13 | Fib(7), Primzahl |
| NOVELTY_FLOOR | 0.382 | COMP_PHI |
| STAGNATION | 0.618 | INV_PHI |
| Budget-Split | 13/55/21/11 | Fibonacci-Ratio |
| Max Retry Backoff | 1,1,2,3,5,8,13s | Fibonacci-Sequenz |

### Primzahl-Anker

| Komponente | Wert | Primzahl |
|------------|------|----------|
| Polling-Intervall | 7s | Prim(4) |
| Monitor-Intervall | 7s | Prim(4) |
| Fibonacci-Max-Aeste | 13 | Fib(7) ∩ Prim |

---

## 5. Die Cons-Zelle

Jede Einheit im System ist ein **Binaer-Paar** (Lisp cons-cell):

```
(CAR . CDR)
  │      │
  │      └── NT-Interface (Das Getriebe)
  │          - Mapping, Dokumentation
  │          - API-Syntax, Clean Code
  │          - Cursor-Kompatibilitaet
  │
  └── ND-Kern (Die Kraft)
      - Tiefe, monotropistischer Fokus
      - Mustererkennung
      - Divergentes Denken
```

**Regel:** Jeder Output MUSS eine NT-kompatible Huelle (CDR) besitzen, die den ND-Kern (CAR) fuer den naechsten Takt konsumierbar macht.

**Handshake:** Kommunikation zwischen Straengen laeuft IMMER ueber CDR. CAR bleibt intern.

---

## 6. Der Orchestrator

Der Orchestrator (Level 1) steht in der **Mitte des Tetraeders**:

```
           COUNCIL (O)
              ▲
              │
    FORGE ◄───┼───► AGENCY
      (T)     │       (M)
              │
              ▼
          ARCHIVE (H)
              
       ORCHESTRATOR
       (im Zentrum)
```

### Orchestrator als Cons-Zelle

- **CAR (Visionaer/ND):** Sieht Zusammenhaenge, erkennt den Takt
- **CDR (CEO/NT):** Budget, Deadline, "Done is better than perfect"

---

## 7. Befehlskette

```
User (L0) ──► ORCHESTRATOR (L1) ──┬──► Agency (Execution)
                                  ├──► Council (Validation)
                                  ├──► Forge (Innovation)
                                  └──► Archive (Retention)
```

### Protokoll-Vektoren

1. **INPUT (PULL / Holschuld):** Bei BLOCKED aktiv GET an Orchestrator/Archive
2. **OUTPUT (PUSH / Bringschuld):** Bei COMPLETED aktiv PUSH an Orchestrator

---

## 8. Simulation Evidence Statistik

| Metrik | Wert |
|--------|------|
| Vektoren | V1-V12 |
| Indizien | 58 |
| Maximale Aeste | 13 (Fibonacci-Primzahl) |
| MTHO-Verteilung | M:13, T:13, H:13, O:19 |
| Chargaff O+T | 32 |
| Chargaff H+M | 26 |

---

## 9. Referenzen

- **Wuji-Diagramm:** `ATLAS_WUJI_MASTER_PLAN.png` (Root)
- **Rueckwaertsevolution:** `docs/01_CORE_DNA/RUECKWAERTSEVOLUTION.md`
- **Gravitational Query:** `docs/01_CORE_DNA/GRAVITATIONAL_QUERY_AND_CORE_AXIOMS.md`
- **Engine Patterns:** `src/config/engine_patterns.py`
- **ChromaDB Collections:** `simulation_evidence`, `core_directives`

---

*Erstellt: 2026-03-04 | Aktualisiert: 2026-03-06 | Orchestrator + Hugin/Munin | MTHO-Override*
