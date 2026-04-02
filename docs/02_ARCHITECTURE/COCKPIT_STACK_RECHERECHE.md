# RECHERECHE-BERICHT: OMEGA COCKPIT UI-STACK 2026
**Vektor:** 2210 | **Status:** RATIFIZIERT | **Team:** Team 1 - AI/UI Expert Group

## 1. Executive Summary
Das OMEGA-Cockpit erfordert einen Paradigmenwechsel von der passiven Datenanzeige (**Dashboard**) hin zur aktiven Systemsteuerung (**Cockpit**). Der Fokus liegt auf "Actionable Intelligence", minimaler Latenz und einer tiefen Integration in die Arch-Linux-Ebene des Dreadnought-Systems.

## 2. Vergleich der Tool-Stacks (2026)

| Feature | **Stack A: Tauri 2 + Next.js** | **Stack B: Iced (Rust Native)** | **Stack C: Next.js + GenAI UI** |
| :--- | :--- | :--- | :--- |
| **Philosophie** | Hybrid (Web-UX + Rust-Power) | Pure Performance (System-Native) | Cloud-Native / Agentic-First |
| **Latenz** | Sehr niedrig (Webview-Bridge) | Nahezu Null (Direct GPU) | Mittel (Netzwerk-Abhängig) |
| **Arch-Integration** | Exzellent (via Rust Bridge) | Absolut (Native syscalls) | Eingeschränkt (via API-Proxy) |
| **Visualisierung** | React-Force-Graph / Sigma.js | Iced-Graph / Custom Shaders | Google Dynamic Layouts |
| **AI-Integration** | Google GenAI SDK (React) | Synaptic-Chroma (Rust) | Google Vertex AI / MCP |

### Stack A: Der "Dreadnought-Hybrid" (Empfehlung)
*   **Technologie:** Tauri 2.0 (Rust Backend) + Next.js 16 (Frontend) + shadcn/ui.
*   **Integration:** Nutzt eine Rust-Bridge für direkten Zugriff auf `systemd`, `journald` und `dbus`.
*   **Vorteil:** Kombiniert das riesige React-Ökosystem (GenAI UI Komponenten) mit der Sicherheit und Geschwindigkeit von Rust.
*   **Eignung:** Perfekt für das "Single Pane of Glass" Konzept, da es lokale Prozesse steuern und gleichzeitig komplexe Web-Visualisierungen rendern kann.

### Stack B: Der "Cybernetic Purist"
*   **Technologie:** Iced (Rust GUI Framework) + `egui_graphs`.
*   **Integration:** Direktes Linken gegen System-Libraries. Keine Node.js-Laufzeit nötig.
*   **Vorteil:** Minimalistischer Footprint, maximale Robustheit (kein CSS/HTML Overhead).
*   **Eignung:** Wenn extreme Performance und minimaler Ressourcenverbrauch (Scout-Ebene) Priorität haben.

### Stack C: Der "Agentic Orchestrator"
*   **Technologie:** Next.js + Google Generative UI SDK.
*   **Integration:** Fokus auf MCP (Model Context Protocol).
*   **Vorteil:** UI generiert sich dynamisch basierend auf dem Prompt ("Generative UI"). Komponenten erscheinen nur, wenn sie für die aktuelle Aufgabe relevant sind.
*   **Eignung:** Ideal für komplexe, unvorhersehbare Workflows, bei denen die KI das Interface on-the-fly anpasst.

## 3. Arch-Linux & System-Integration
Um eine echte "Actionable Intelligence" zu erreichen, muss das Cockpit folgende Schnittstellen bedienen:
*   **systemd-dbus:** Monitoring und Steuerung der `omega-*` Daemons ohne `sudo`-Shell-Umwege.
*   **Journald-Stream:** Echtzeit-Log-Analyse mittels `pcre2` Filtern im Rust-Backend, um nur relevante "Anomalien" an das UI zu senden.
*   **CachyOS Kernel-Metriken:** Integration von `coolercontrol` Daten und CPU-Scheduling-Status für das "Puls"-Monitoring.

## 4. Echtzeit-Vektor-Visualisierung (ChromaDB)
Die Visualisierung von 5D-Vektorräumen erfolgt über:
1.  **Topologische Gitter:** Darstellung von ChromaDB-Knoten als HNSW-Graph (Hierarchical Navigable Small World).
2.  **Resonanz-Animation:** "Data Breathing" – Die Luminanz der Knoten pulsiert im Takt der Zugriffsfrequenz (MRI-Dynamo Isomorphie).
3.  **Bibliothek-Tipp:** `react-force-graph-3d` ermöglicht die Rotation im 5D-Raum (projiziert auf 3D) für die manuelle Inspektion von Vektor-Clustern.

## 5. Google AI UI & Material Trends 2026
*   **Generative UI:** Nutzung von SDKs, die es der Gemini-API erlauben, strukturierte UI-JSON-Payloads zu senden, die im Cockpit sofort als interaktive Widgets (z.B. ein spezialisierter Log-Filter oder ein Prozess-Kill-Button) gerendert werden.
*   **Material 4 "Adaptive":** Interfaces, die nicht nur auf Bildschirmgröße, sondern auf "Kognitive Last" reagieren. Bei hohem Stress (Fehlerraten > Δ) reduziert das UI den Detailgrad und hebt nur noch "Kill-Switches" hervor.

## 6. Empfehlung & Roadmap
**Empfehlung:** **Stack A (Tauri + Next.js + shadcn/ui)**.
Die bestehende React-Basis (`frontend/`) kann schrittweise in einen Tauri-Container migriert werden.

### Roadmap:
1.  **Phase 1:** Migration des `frontend/` zu Next.js 16 und Integration von `Tauri 2`.
2.  **Phase 2:** Implementierung der Rust-Sidecars für `systemctl` Status-Abfragen.
3.  **Phase 3:** Aufbau des "Force-Graph" Moduls for the ChromaDB-Visualisierung.
4.  **Phase 4:** Einführung von "Data Breathing" Animationen via `framer-motion`.


[LEGACY_UNAUDITED]
