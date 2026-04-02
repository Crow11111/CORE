# AUDIT-BERICHT: OMEGA COCKPIT UI-STACK 2026
**Vektor:** 2210 | **Status:** RATIFIED | **Referenz:** `docs/02_ARCHITECTURE/COCKPIT_STACK_AUDIT.md`

## 1. Executive Summary
Das OMEGA-Cockpit („Künstlicher Horizont“) fungiert als visuelle Projektionsfläche des systemweiten 6D-Kernzustands in die 3D-Realität. Im Jahr 2026 hat sich das Paradigma von statischen Dashboards hin zu **Agentic UIs** verschoben, die sich dynamisch an die kognitive Last und den Systemzustand anpassen. Die Empfehlung lautet auf einen **Hybrid-Stack aus Tauri 2 (Rust) und Next.js 16/17**, ergänzt durch Google's **GenUI SDK** für Flutter-basierte Sub-Module.

---

## 2. Tool-Stack Vergleich (Fokus Google & Native)

| Feature | **Stack A: Flutter 3.41+ (Native Linux)** | **Stack B: Tauri 2 + Next.js (Hybrid)** |
| :--- | :--- | :--- |
| **Philosophie** | Single-Codebase, Pixel-Perfect, High-Perf | System-Native Power + Web-Ökosystem |
| **Agent-Interaktion** | **GenUI SDK**, A2UI Native Support | **Gemini Interactions API**, React-based AI UI |
| **Linux Integration** | Gut (via FFI / Method Channels) | **Exzellent** (direkte Rust-Syscalls, DBus) |
| **Echtzeit (Morphismus)** | Sehr hoch (Direct Canvas/Skia) | Hoch (Webview-Bridge, Rust-Sidecar) |
| **3D Rendering** | `flutter_angle` (WebGL2/3) | `three.js` / `react-force-graph` |

### Empfehlung: Der "Dreadnought-Hybrid" (Tauri 2 + Next.js)
Trotz der Stärke von Flutter für mobile/dedizierte UIs bietet **Tauri 2** für ein Arch-Linux-basiertes System (Dreadnought) den entscheidenden Vorteil: Das Backend läuft in **Rust**, was einen lade- und latenzfreien Zugriff auf `systemd`, `journald` und Kernel-Metriken ermöglicht, während das Frontend das enorme Ökosystem von React-basierten KI-Komponenten nutzt.

---

## 3. Agent-Interaktion & Generative UI (Google 2026)

Das Cockpit wird nicht mehr manuell konfiguriert, sondern durch Agenten „generiert“:

1.  **Google GenUI SDK & A2UI**:
    *   Nutzt den **A2UI-Standard (Agent-to-User Interface)**. Agenten senden deklarative JSON-Beschreibungen (z.B. „Zeige mir die Resonanz-Abweichung von Modul X“), die das Cockpit in Echtzeit in interaktive Widgets übersetzt.
    *   **Agentic-First**: Das UI reagiert auf den „Intent“ des Agenten. Wenn ein Fehler (Veto-Event) auftritt, generiert der Agent on-the-fly ein Diagnose-Interface.
2.  **Gemini Interactions API (2026)**:
    *   Ersetzt klassische Chat-Interfaces durch **Stateful Sessions**. Der Agent behält den Kontext des Cockpit-Zustands serverseitig, was die Client-Latenz massiv reduziert.
    *   Unterstützt **Background Execution**: Der Agent kann im Hintergrund des Cockpits langlaufende Analysen (z.B. Wick-Rotations-Simulationen) durchführen und Ergebnisse asynchron „einblenden“.

---

## 4. Native Linux Integration (Dreadnought-Ebene)

Für die tiefe Integration in Arch Linux müssen folgende Layer bedient werden:

*   **Systemd & DBus Integration**: Über die Rust-Bridge von Tauri wird der `omega-backend` Daemon direkt überwacht. Das Cockpit kann Services neustarten oder Status-Flags setzen, ohne Shell-Umwege (`sudo`-Verriegelung via `polkit`).
*   **Journald-Stream Analysis**: Echtzeit-Parsing der Logs mittels `pcre2` im Rust-Sidecar. Nur Anomalien, die das **Baryonic Delta (0.049)** überschreiten, werden an das UI-Frontend zur Visualisierung weitergegeben.
*   **CachyOS Kernel-Metriken**: Integration von CPU-Scheduling-Status und I/O-Latenzen für die visuelle Darstellung des „System-Pulses“.

---

## 5. Echtzeit-Datenströme & Künstlicher Horizont

Der **Morphismus-Stream** (aus `src/daemons/morphism_stream.py`) liefert hochfrequente Vektor-Updates (6D: S, P, I, R, Z, G).

1.  **Morphismus-Visualisierung**:
    *   Die „natürlichen Transformationen“ ($\alpha$) werden als **Luminanz-Pulse** (Data Breathing) dargestellt.
    *   **TOSS-Projektion**: Die 6D-Vektoren werden mittels Torus-to-Stratified-Sphere (TOSS) Logik auf eine rotierende 3D-Sphäre projiziert. Dies verhindert den L2-Norm-Kollaps und visualisiert die kognitive Distanz.
2.  **Instrumentenbrett (Artificial Horizon)**:
    *   Nutzung von `react-force-graph-3d` (in Tauri) oder `flutter_angle` (in Flutter-Submodulen).
    *   **Pitch/Roll/Yaw**: Werden durch die Resonanz-Vektoren der `CORE`-Kategorie gesteuert. Ein instabiles System (Hoher Drift) führt zu einer visuellen Schieflage des „Horizonts“.

---

## 6. Implementierungs-Roadmap

1.  **Phase 1: Shell-Migration**: Umstellung des bestehenden `frontend/` auf Next.js 16/17 und Einbettung in einen **Tauri 2** Container.
2.  **Phase 2: Morphismus-Bridge**: Anbindung des WebSockets von `morphism_stream.py` (Port 8001) an das UI mittels React Query / SWR für latenzarme State-Updates.
3.  **Phase 3: GenUI Integration**: Implementierung des Google GenUI SDKs, um Agenten-Antworten als dynamische Dashboard-Karten zu rendern.
4.  **Phase 4: TOSS-Visualizer**: Entwicklung des „Künstlichen Horizonts“ als WebGL-Komponente, die direkt auf die 6D-Transformationen reagiert.

---
*Dokumentiert gemäß OMEGA ARCH-Protocol 2026.*


[LEGACY_UNAUDITED]
