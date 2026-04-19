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
