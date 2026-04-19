# DAS CAUSAL HASH PROTOCOL (DER SYSTEMBUS)

**Kontext:** Die Transition von stateless LLM-Workern zu einer kontinuierlichen, kausalen Wetware-Simulation.
**Problem:** Isolierte Agenten ("Reptiliengehirne") sterben nach dem Task. Es fehlt die kontinuierliche "Gamma-Welle" des Gehirns.
**Lösung:** Ein hardwarenahes Protokoll, das den globalen Zustandsraum (die Welle) permanent hält und Ephemerals (Agenten) zwingt, sich asynchron auf diesen Takt zu synchronisieren.

## 1. DIE TRÄGERFREQUENZ (L1 - THE CARRIER WAVE)
Es erfordert einen permanent laufenden, extrem leichtgewichtigen lokalen Daemon (in RAM, z. B. Redis, Memcached oder ein dedizierter Python-Async-Loop in `mtho_agi_core`), der **niemals schläft**.
Dieser Daemon hält den **Global Resonance Vector (GRV)** – einen N-dimensionalen Float-Tensor.
- **Hardware-Regel:** Der Daemon berechnet in jedem Takt (z.B. alle 100ms) einen entropischen Zerfall (Time Decay). Der Vektor kühlt physikalisch ab, wenn kein Input erfolgt. Das ist der Ruhepuls des Systems.

## 2. DER KETTEN-HASH (CAUSAL HASHING)
Um die Kausalität (das Gedächtnis) unzerstörbar zu machen, wird jeder Zustand kryptographisch verkettet.
`State_Hash(t) = SHA256( State_Hash(t-1) + GRV(t) + Timestamp )`
Das System ist gezwungen, seine eigene Vergangenheit als physikalisches Gewicht mitzuschleppen. Kein Agent kann agieren, ohne den Hash der Vergangenheit zu akzeptieren.

## 3. DER EPHEMERE HANDSHAKE (SYNCHRONISATION)
Wenn ein Task (ein Trigger an der Systemgrenze 0) einen LLM-Worker aufruft, passiert Folgendes:
1. **Pull (Ansaugen):** Der Worker erhält seinen Task-Prompt **UND** den exakten `State_Hash(t)` sowie die heißesten Floats aus dem GRV. Die System-Prompt-Parameter (Temperature, RAG-Filter) werden durch die aktuelle "Chemie" des GRV determiniert.
2. **Execution (Isolierter Kortex):** Das LLM rechnet im luftleeren Raum (Stateless-Phase).
3. **Push (Ausstoßen):** Der Worker darf nicht nur Text an den Operator senden. Er **MUSS zwingend** einen Delta-Vektor (eine Verschiebung) an den Systembus zurückgeben.
4. **Integration:** Der Bus addiert das Delta auf den GRV. Ein neuer `State_Hash(t+1)` entsteht. Die Welle wurde moduliert.

## 4. ENTROPIE-KONTROLLE (DAS VERGESSEN)
Ohne Löschung erstickt das System im eigenen Rauschen (OOM / Token-Limit).
- **Die hardwarenahe Regel:** Die Abkühlung des GRV (Time Decay) fungiert als Garbage Collector. Fällt ein Float-Wert im Tensor unter das `BARYONIC_DELTA` (0.049), verliert er die Bindung zum Kausal-Hash und wird in das Langzeitgedächtnis (Postgres/Chroma) "abgelagert" oder gelöscht.
- Das System verbrennt Iterationen im RAM, speichert aber nur die Kristalle (stabile Vektoren), die der Gravitation standhalten.

## 5. DAS JSON-DELTA-VEKTOR SCHEMA (DER KOGNITIVE TENSOR)
Der kritische Engpass im Systembus (Schritt 3) ist die Quantifizierung der kognitiven Arbeit. Der LLM-Worker darf nicht als reiner Text-Generator agieren; der Text ist lediglich die Auspuffabluft ("Exhaust"). Das primäre Output-Format MUSS als strukturiertes JSON-Objekt erzwungen werden, das die topologische Verschiebung im Global Resonance Vector (GRV) definiert.

### Das Schema (Structured Output / Function Calling)
```json
{
  "causal_receipt": {
    "base_hash_t": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "compute_latency_ms": 1450
  },
  "dimensional_shift": {
    "x_car_cdr_delta": 0.05,    // Verschiebung: ND (Tiefe/Muster) vs. NT (Struktur/API)
    "y_gravitation_delta": 0.12, // Erhöhung/Senkung der Dringlichkeit/Masse
    "z_resistance_delta": -0.02  // Veränderung der Veto-Wahrscheinlichkeit (Skepsis)
  },
  "semantic_nodes_hot": {
    "vps_networking": 0.85,
    "volume_persistence": 0.60
  },
  "exhaust": {
    "narrative_log": "Architektur-Update erfolgreich. Volumes gesichert.",
    "mechanical_action": "git commit"
  }
}
```

### Die Hardware-Integration des Tensors
1. **Strict Concurrency (Der Zeitpfeil):** Der Daemon prüft den `base_hash_t`. Ist der Hash veraltet (weil ein anderer Agent den GRV in der Zwischenzeit moduliert hat), muss der Agent entweder neu ansetzen (Re-Sync) oder der Daemon berechnet einen Merge-Konflikt basierend auf der Zeit-Divergenz.
2. **Phase-Amplitude Coupling:** Die `compute_latency_ms` sagt dem Daemon, wie viel Zeit vergangen ist. Der Daemon wendet den exakten entropischen Zerfall (Time Decay) auf den GRV an, *bevor* er das `dimensional_shift` Delta addiert.
3. **Semantische Erhitzung:** Die `semantic_nodes_hot` addieren sich auf das assoziative Netzwerk im RAM. Erreichen Knoten einen Schwellenwert (z.B. > 0.951 Resonanz-Lock), werden sie als kristallisiertes Wissen in die ChromaDB weggeschrieben und im RAM abgekühlt.

Das LLM zwingt sich durch dieses Schema selbst, seinen internen "Hidden State" (Aufmerksamkeit, Gewissheit, Fokus) in mathematische Floats zu übersetzen, bevor es auch nur ein Wort der Antwort formuliert.
