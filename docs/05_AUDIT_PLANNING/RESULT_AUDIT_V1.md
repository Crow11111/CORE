# AUDIT-VEKTOR 1: Infrastruktur & Zero-Trust für LLM-Agenten (Architektur-Report 2026)

Das vorliegende Dokument formuliert die systemarchitektonischen Leitplanken und Sicherheitsaxiome für den hochskalierbaren, produktiven Einsatz autonomer Multi-Agenten-Systeme (MAS) auf Basis von Large Language Models (LLMs). Da autonome Agenten nicht lediglich vordefinierte Skripte abarbeiten, sondern durch dynamisches Prompting "Reasoning"-Fähigkeiten nutzen, um zur Laufzeit unvorhergesehene Tool-Ketten aufzurufen [cite: 1], versagen klassische statische Sicherheitsperimeter. Es scheint unumgänglich, dass moderne Architekturen auf feingranulare, ephemere und kryptografisch verifizierbare Zero-Trust-Prinzipien migrieren.

**Wichtige Kernaussagen (Executive Summary):**
*   **Identität und Autorisierung:** Traditionelles RBAC (Role-Based Access Control) ist für autonome Agenten unzureichend. Die Forschung und Standardisierung (IETF-Entwürfe 2026) weisen stark auf kryptografisch verifizierbare "Ghost Tokens" und das Contextual Agent Authorization Mesh (CAAM) hin, um eine feingranulare, temporäre Delegationskette (ReBAC) sicherzustellen [cite: 1, 2].
*   **LLM API-Gateways:** Ein dediziertes Gateway ist zwingend erforderlich, um dynamisches Routing, semantische Data Loss Prevention (DLP) und PII-Redaction (Personally Identifiable Information) zu zentralisieren. Hierbei ist zu beachten, dass reguläre Ausdrücke nicht mehr genügen; NLP-basierte Inspektionen in Echtzeit sind Best Practice [cite: 3, 4].
*   **Isolierung auf Infrastrukturebene:** Der "Blast Radius" kompromittierter Agenten muss durch kurzlebige Micro-VMs (z. B. auf KVM-Basis) oder ephemere Container reduziert werden [cite: 5]. Die Kommunikation mit dem Host-System erfolgt idealerweise strikt über das Model Context Protocol (MCP) und isolierte IPC-Kanäle [cite: 6, 7].
*   **Kernel-Level Observability:** Um die semantische Lücke zwischen der "Absicht" (Intent) eines LLM-Agenten und seinen tatsächlichen Systemaufrufen (Actions) zu schließen, wird in modernen Architekturen eBPF (extended Berkeley Packet Filter) eingesetzt [cite: 8, 9]. Systeme wie AgentSight korrelieren diese Datenströme bei minimalem Performance-Overhead [cite: 10, 11].

Die folgenden Abschnitte detaillieren diese Erkenntnisse in Form eines dichten, akademisch-technischen Architekturentwurfs, der als Grundlage für die "OMEGA-Axiome" Ihres eigenen Systems dienen kann.

## 1. Runtime Authorization (Laufzeit-Autorisierung)

Die Autorisierung von LLM-Agenten unterscheidet sich fundamental von traditioneller Microservice-Autorisierung. Während klassische Workloads einem deterministischen, hart codierten Pfad folgen, interpretieren autonome Agenten natürliche Sprache und entscheiden zur Laufzeit über die Sequenzierung von API-Aufrufen [cite: 1]. Ein Angreifer benötigt keine klassische Code-Injection mehr, sondern kann über Prompt Injections oder Guardrail Poisoning den Agenten dazu bringen, seine legitime Maschinenidentität für böswillige Zwecke zu missbrauchen [cite: 1]. Die Autorisierungsarchitektur muss daher dynamisch, kontextbasiert und streng zweckgebunden (purpose-bound) sein.

### 1.1 Workload Identity via SPIFFE/SPIRE

Der grundlegende Baustein für die Maschinenidentität eines Agenten ist das Secure Production Identity Framework for Everyone (SPIFFE) in Verbindung mit seiner Laufzeitumgebung SPIRE [cite: 1, 12]. Jeder Agenten-Workload erhält eine kryptografisch eindeutige Identität in Form eines SPIFFE Verifiable Identity Document (SVID) [cite: 2]. 

**OMEGA-Axiom 1.1:** *Verbot statischer Credentials.* LLM-Agenten dürfen keine langlebigen API-Keys oder statischen Service Accounts nutzen. Jeder Agenten-Prozess muss über SPIRE attestiert werden und ein rotierendes SVID erhalten, das an seine kryptografische Identität gebunden ist [cite: 1]. Wenn die spezifische Aufgabe (das "Ticket") des Agenten beendet ist, erlischt seine Identität sofort [cite: 1].

### 1.2 Contextual Agent Authorization Mesh (CAAM) und Ghost Tokens

Der IETF-Draft "Contextual Agent Authorization Mesh (CAAM)" aus dem Jahr 2026 definiert den sogenannten "Post-Discovery Authorization Handshake" [cite: 2, 13]. CAAM führt eine Sidecar-basierte Architektur ein, die als Mediator fungiert und Relationship-Based Access Control (ReBAC) sowie "Common Ancestor Constraints" bei der Agent-zu-Agent- (A2A) und Mensch-zu-Agent- (H2A) Kommunikation erzwingt [cite: 2, 14].

CAAM operiert als Bindeglied zwischen der menschlichen Herkunft (IPSIE - Interoperability Profiling for Secure Identity in the Enterprise) und der maschinellen Identität (SPIFFE) [cite: 2]. Der entscheidende Mechanismus hierbei ist die kryptografisch verifizierbare Intent-Propagierung durch Chained JSON Web Signatures (JWS) [cite: 2]. 

Der Ablauf gestaltet sich wie folgt:
1.  **Origination:** Das CAAM-Mesh generiert ein Scope Control Object (SCO), das die Claims `purpose`, `scope_ceiling` und `max_hops` enthält. Dieses SCO wird vom ursprünglichen Identity Provider signiert [cite: 2].
2.  **Propagation:** Bei jedem Hop in einem Multi-Agenten-System fügt das Sidecar des delegierenden Agenten einen `act`-Claim und einen `sub_purpose` hinzu, der den Kontext weiter einschränkt (Narrowed Persona). Das Sidecar signiert das erweiterte SCO mit seinem SPIFFE SVID [cite: 2].
3.  **Ghost Tokens:** Das rohe Delegations-Token (Delegation Token) wird dem Agenten niemals direkt übergeben. Stattdessen synthetisiert das Sidecar im Moment der Nutzung ein kurzlebiges, zweckgebundenes "Ghost Token" (Just-In-Time Scoped Token) [cite: 2].
4.  **Contextual Risk Score (CRS):** Jedem Request innerhalb des Meshs wird ein reeller Wert \( S \) im Intervall \([cite: 6]\) zugewiesen. Dieser Score moduliert die zulässigen Aktionen basierend auf der dynamischen Risikobewertung [cite: 2].

**OMEGA-Axiom 1.2:** *Kryptografische Delegationsketten.* Agenten müssen CAAM-Sidecars (oder äquivalente Architekturen) nutzen. Die Autorisierung bei Tool-Aufrufen muss über Ghost Tokens erfolgen. Bei jedem A2A-Hop muss das empfangende Sidecar die vollständige SVID-Signaturkette (Chained JWS) validieren, bevor ein lokales JIT-Token für den nachgelagerten Tool-Zugriff synthetisiert wird [cite: 2].

### 1.3 Agent Authorization Profile (AAP) für OAuth 2.0

Zusätzlich zu CAAM spezifiziert das "Agent Authorization Profile (AAP) for OAuth 2.0" strukturierte Claims und Validierungsregeln speziell für autonome KI-Agenten in M2M-Szenarien [cite: 15]. AAP erweitert bestehende Standards um die Möglichkeit, Agentenidentität, Aufgabenkontext, operative Einschränkungen, Delegationsketten und Anforderungen an die menschliche Aufsicht (Human-in-the-Loop) berechenbar und auditierbar zu machen [cite: 15].

## 2. LLM API-Gateways / Firewalls

Ein direkter Zugriff von Agentenlogik auf externe LLM-Provider (wie OpenAI, Anthropic) oder interne Modell-Cluster ist ein systemkritisches Anti-Pattern. Ein zentrales Policy-Enforced LLM API-Gateway ist das obligatorische "zentrale Nervensystem" einer sicheren KI-Architektur [cite: 3]. Es abstrahiert die Backend-Komplexität und erzwingt konsistente Sicherheits-, Performance- und Observability-Metriken [cite: 16].

### 2.1 Zwingende Gateway-Architekturkomponenten

Das Gateway agiert als Reverse Proxy und erzwingt Governance-Richtlinien auf Payload-Ebene. Zu den zwingend erforderlichen Schichten gehören:
*   **Unified Access & Authentication:** Zentralisierung des API-Key-Managements. Die Agenten authentifizieren sich am Gateway (z. B. via SPIFFE-Identität), und das Gateway hält die Root-API-Keys der Provider [cite: 3, 4].
*   **Flexible Routing Logic:** Das Gateway implementiert dynamisches Routing. Dies umfasst Header-basiertes Routing (z. B. `X-Model: gpt-4`) sowie inhaltsbasiertes Routing (Content-based routing), bei dem das Gateway den Payload inspiziert (z. B. `"intent": "translate"`) und den Workload dem optimalen Modell zuweist [cite: 16].
*   **Prompt-Firewall (ModelArmor):** Auf dem Gateway liegen Firewalls, die explizit darauf trainiert sind, Prompt Injections (wie P2SQL) und Exfiltrationsversuche am Interaktions-Boundary abzufangen [cite: 17, 18]. 
*   **Smart Caching & Rate Limiting:** Redis-basierte Caching-Schichten reduzieren API-Kosten und Latenzen durch Response-Caching. Zudem schützt serverseitiges Rate-Limiting vor Denial-of-Wallet-Attacken durch "Reasoning Loops" [cite: 4, 9].
*   **Unified Observability:** Konsolidierte Metriken (z. B. via Prometheus und Grafana) und Traces über alle LLM-Dienste hinweg sind essenziell, um End-to-End-Transparenz zu gewährleisten [cite: 4, 16].

### 2.2 Semantisches Data Loss Prevention (DLP) und PII-Redaction

Traditionelle DLP-Tools, die auf simplen regulären Ausdrücken basieren, sind für den Einsatz in Generativer KI insuffizient [cite: 3]. Autonome Agenten können sensible Daten paraphrasieren, zusammenfassen oder übersetzen, wodurch sie Signaturprüfungen entgehen.

**OMEGA-Axiom 2.1:** *AI-Aware Semantic Content Inspection.* Das LLM-API-Gateway muss zwingend ein semantisches NLP-Modell (z. B. basierend auf Microsoft Presidio) integrieren, das Prompts und Outputs in Echtzeit analysiert [cite: 3, 4]. PII (Personally Identifiable Information) muss durch Data Masking und Tokenisierung pseudonymisiert oder vollständig redigiert werden, bevor der Payload das Unternehmensnetzwerk in Richtung eines externen LLM-Providers verlässt [cite: 3, 16].

## 3. Container-Isolierung & Data Segregation

Wenn LLM-Agenten Code generieren und ausführen oder auf Datenbanken zugreifen (sogenannte Computer-Use Agents oder CUA), entsteht ein massiver Risiko-Vektor. Generierte Befehle können syntaktisch korrekt, aber logisch destruktiv sein (z. B. das Ausführen von `rm -rf /` in einem kritischen Pfad) [cite: 19]. Einem Agenten direkten Zugriff auf das Host-OS oder langlaufende Standard-Container zu gewähren, ist ein "Sicherheits-Albtraum" [cite: 6].

### 3.1 Isolations-Paradigmen: Micro-VMs und Ephemere Sandboxen

Die modernste Architektur zur Reduzierung des "Blast Radius" kompromittierter Agenten auf null basiert auf hochgradig ephemeren Micro-VMs oder Firecracker-ähnlichen Sandboxen [cite: 5, 6].

Zwei prominente Architekturmuster aus dem Stand der Technik (2026) veranschaulichen dies:
*   **Kilntainers-Pattern (Isolated Linux Sandboxes):** Ein Model Context Protocol (MCP) Server stellt dedizierte, isolierte Linux-Sandboxen (via Docker, Podman, Modal, E2B oder WebAssembly/WASM) für die Shell-Ausführung zur Verfügung [cite: 6]. 
    *   *Agent Isolation:* Jeder Agent erhält seine eigene dedizierte Sandbox. Es gibt keinen Shared State und keine Cross-Contamination [cite: 6].
    *   *Ephemerality:* Die Sandbox existiert ausschließlich für die Dauer der MCP-Session und wird nach Beendigung automatisch zerstört [cite: 6].
    *   *Secure by Design:* Der LLM-Agent läuft **nicht** innerhalb der Sandbox. Er kommuniziert mit der Sandbox ausschließlich über das strukturierte Model Context Protocol (MCP). Dadurch werden niemals Agenten-API-Keys, Code oder System-Prompts in die Umgebung exportiert, in der eine potenzielle Prompt Injection zur Exfiltration führen könnte [cite: 6].
*   **VoidBox-Pattern (KVM Micro-VMs):** AI-Agent-Workflows laufen innerhalb einer Rust-Runtime in Einweg-KVM-Micro-VMs (Disposable KVM Micro-VMs) [cite: 5].
    *   *Host-Guest IPC:* Die Interprozesskommunikation zwischen dem Host-System und der Agenten-VM erfolgt sicher über `virtio-vsock` unter Verwendung eines bei jedem Boot-Vorgang zufällig generierten Secrets [cite: 5].
    *   *Seccomp-bpf & Limits:* Innerhalb des Gastsystems werden Systemaufrufe durch Seccomp-bpf stark limitiert, Netzwerk-Deny-Listen etabliert und strenge Ressourcen-Limits (CPU/Memory) durchgesetzt [cite: 5].

### 3.2 Fehlertolerantes Sandboxing und Network Policies

Da Voll-VM-Provisionierungen oft zu hohe Startlatenzen aufweisen (und den interaktiven "Think-Act-Observe"-Loop des Agenten unterbrechen) und Standard-Docker-Container kein inhärentes Rollback auf einen vorherigen State erlauben, haben Forscher transaktionale Filesystem-Snapshots (z. B. auf ZFS/Btrfs-Basis) für das Rollback zerstörerischer Befehle validiert [cite: 19]. Experimentelle Testbeds (z. B. auf Proxmox VE) demonstrieren eine 100%ige Erfolgsquote beim Rollback kompromittierter States bei einem marginalen Overhead von 14,5 % pro Transaktion [cite: 19].

Auf Netzwerkebene muss eine strikte Segmentierung erfolgen. Eine bloße VLAN-Trennung reicht nicht aus. Es werden Ethernet VPN (EVPN) mit VXLAN-Kapselung (Virtual eXtensible Local Area Network) und VyOS-Router als VTEPs (VXLAN Tunnel Endpoints) genutzt, um den Agenten-Traffic kryptografisch und physikalisch vom Rest des Data Centers zu isolieren [cite: 19]. KubeArmor wird zudem als Kubernetes-natives Enforcement-Tool (via LSM/eBPF) eingesetzt, um Least-Privilege-Policies für Egress-Verbindungen (Microsegmentation) hart durchzusetzen [cite: 17].

**OMEGA-Axiom 3.1:** *Strikte Separierung von Reasoner und Executor.* Die LLM-Logik (der Reasoner) darf niemals im selben Ausführungskontext laufen wie der generierte Code (der Executor). Der Code muss zwingend in einer ephemeren KVM-Micro-VM oder WASM-Sandbox ausgeführt werden. Die Interaktion zwischen Reasoner und Executor darf ausschließlich über standardisierte, schemabasierte RPC-Protokolle wie das Model Context Protocol (MCP) über `virtio-vsock` stattfinden [cite: 5, 6, 7]. Nach Ausführung der isolierten Sub-Task ist die Sandbox rückstandslos zu terminieren (Ephemeralität).

## 4. Kernel-Level Observability und Zero-Trust Überwachung (eBPF)

Das größte ungelöste Problem bei der Überwachung autonomer Systeme ist der "Semantic Gap" (semantische Lücke): Herkömmliche APM-Tools (Application Performance Monitoring) sehen entweder nur die High-Level-Intention des Agenten (den Prompt) oder nur die Low-Level-Systemaufrufe, können diese aber nicht kausal korrelieren [cite: 9, 20]. Ein Angreifer könnte einen Agenten unbemerkt übernehmen, da Agenten-Aktivitäten von regulären automatisierten Tasks nicht zu unterscheiden sind.

### 4.1 Boundary Tracing via eBPF (AgentSight-Pattern)

Die Lösung für 2026 ist das sogenannte "Boundary Tracing" mittels **eBPF (extended Berkeley Packet Filter)** [cite: 9]. eBPF erlaubt es, direkt im Linux-Kernel sichere, verifizierte Programme auszuführen, ohne den Quellcode der Anwendung ändern zu müssen (Zero-Instrumentation) [cite: 10, 20]. 

Systeme wie AgentSight etablieren eine lückenlose Observability-Kette, indem sie den System-Boundary überwachen, wo Agenten unvermeidlich mit der Außenwelt interagieren [cite: 21].
*   **Intent-Erfassung (Semantic Intent):** Ein eBPF-Programm heftet sich via User-Space Probes (`uprobes`) direkt in die Krypto-Bibliotheken des Agenten (z. B. an `SSL_read` und `SSL_write` in OpenSSL) [cite: 9, 11]. So wird der TLS-verschlüsselte Traffic zwischen Agent und LLM direkt nach der Entschlüsselung im Speicher abgefangen. Dies offenbart den exakten Prompt und die Intention der KI, effizienter als jedes Netzwerk-Packet-Capture [cite: 9, 20].
*   **Action-Erfassung (System Actions):** Ein zweites eBPF-Programm nutzt Kernel Probes (`kprobes`) und Tracepoints (z. B. `sched_process_exec`), um dynamisch kritische Systemaufrufe wie `openat2` (Dateizugriffe), `connect` (Netzwerkverbindungen) und `execve` (Prozessausführungen) zu überwachen [cite: 9, 11].

### 4.2 Multi-Signal Causal Correlation Engine

Die isolierten Datenströme aus dem User-Space (Intents) und Kernel-Space (Actions) werden durch eine hybride Korrelations-Engine im User-Space (oft in Rust implementiert) verknüpft [cite: 9, 11].
Der Korrelationsmechanismus basiert auf drei Pfeilern:
1.  **Prozess-Lineage-Tracking:** Durch die Überwachung von `fork` und `execve` wird ein vollständiger Prozessbaum aufgebaut. Selbst wenn der Agent bösartige Subprozesse ausführt, die reguläre Instrumentierungen umgehen würden, ordnet der Kernel sie dem Agenten-Ursprung zu [cite: 10, 11].
2.  **Temporale Korrelation:** Systemaktionen, die unmittelbar nach einer empfangenen LLM-Antwort erfolgen, werden zeitlich verknüpft [cite: 11].
3.  **Content Matching:** Dateinamen, URLs oder Befehle, die im entschlüsselten LLM-Response vorkommen, werden mit den tatsächlichen Parametern in den Syscalls (z. B. den Argumenten von `execve`) abgeglichen [cite: 11].

Abschließend wird dieser korrelierte Trace an ein sekundäres LLM übergeben ("AI watching AI"), welches als Sicherheitsanalyst fungiert. Dieses sekundäre Modell versteht die Semantik und erkennt komplexe Abweichungen (Anomalien), Prompt Injection-Attacken oder teure "Reasoning Loops", die statische regelbasierte Systeme übersehen würden [cite: 11, 20]. Der Performance-Overhead dieses gesamten eBPF-Setups liegt dabei bei unter 3 % [cite: 9, 10].

**OMEGA-Axiom 4.1:** *Zero-Instrumentation Kernel-Überwachung.* Die Überwachung des Agenten-Verhaltens darf sich nicht auf Application-Layer-Logs verlassen (die von einem kompromittierten Agenten manipuliert werden könnten). Es ist zwingend eine eBPF-basierte Tracing-Architektur (Analog zu AgentSight oder Groundcover) einzusetzen, die TLS-Intents per `uprobe` und System-Actions per `kprobe` abgreift, korreliert und hard-codierte Security-Policies (über Linux Security Modules / LSM) direkt im Kernel durchsetzt [cite: 8, 9, 11].

## 5. Zusammenfassung der Architektur-Constraints (OMEGA-Axiome)

Basierend auf den Analysen lassen sich die absoluten Best Practices (Stand 2026) in folgende überführbare Axiome kondensieren:

1.  **Workload-Identity-Roots:** Jeder Agent besitzt ein kryptografisches SPIFFE SVID. Langlebige API-Credentials sind für Agenten strengstens untersagt [cite: 1, 2].
2.  **CAAM-Sidecar-Mediator:** Die Autorisierung bei H2A- und A2A-Delegationen erfordert ein Sidecar, das Contextual Risk Scores (CRS) berechnet und JWS-signierte Scope Control Objects (SCOs) propagiert. Dem Agenten werden nur hochspezifische Just-In-Time "Ghost Tokens" für den finalen Aufruf präsentiert [cite: 2].
3.  **Zentralisiertes AI-Gateway:** Sämtlicher LLM-Traffic muss durch ein Policy-Enforced Gateway geroutet werden. Dieses übernimmt die semantische (NLP-basierte) PII-Redaction, das Caching und die Prompt-Firewall (ModelArmor) [cite: 3, 4, 17].
4.  **Air-Gapped Execution:** Die Execution-Umgebung (Tool-Nutzung) und die Reasoning-Umgebung (LLM-Logik) sind strikt physisch oder hypervisor-basiert zu trennen. Die Code-Ausführung erfolgt in ephemeren, nach Nutzung terminierten KVM-Micro-VMs (z. B. VoidBox), die mittels `virtio-vsock` und Seccomp-bpf maximal eingeschränkt sind [cite: 5, 6].
5.  **MCP als Kommunikations-Layer:** Agenten kommunizieren mit Datenbanken und Sandboxen standardisiert über das Model Context Protocol (MCP), um N×M-Integrationsrisiken zu eliminieren und den Datenaustausch protokollarisch abzusichern [cite: 7, 22, 23].
6.  **eBPF-Enforcement:** Sicherheitsrichtlinien müssen im Kernel via eBPF und LSM enforced werden. Zur Schließung des Semantic Gaps ist eine Architektur zur Intent-Action-Korrelation zu implementieren, die verschlüsselte Payload-Absichten (`SSL_read`/`write`) mit den zugehörigen Systemaufrufen verknüpft, um Privilege Escalations und unautorisierte Tool-Zugriffe deterministisch in Echtzeit zu stoppen [cite: 8, 9, 11].

**Sources:**
1. [nhimg.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEHnlI8C4A-3zGY1ySZDUX9Lup-wrpHZG4U0Jl5FwY8mwiIkFOtzSywFnL84Hz7HEQWnNruAmcEur6i9B9DGF6MT5-BHzhiZWQzzbE98530sRNjsJUwAkYMzuxf9uVNBKcplhJvXq-rl0cznnQmpXFhY8n-74-FAuEii5-dh6a04f7-pGYlL84=)
2. [ietf.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH92LZ8kSKCkeGF4aKS2-BiDBVicQ0VRUFq2gZW-ttCkyVc5qp_teWgbYF-7rhctjoQylkidXDEgXJxQI5mR8JG49QmUcuKxxfYA61dQZzCdp9_4CIjBe3sAWFYc3e8wdXUQ6dUEEinSLFFAg==)
3. [djimit.nl](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEI4MB9Ps9uXfjSmsbfouIENclKlQYs8VxmM5kKo2DJ0LURmuoL7XdAuDgoSdHQ9pW17uCAZ1bvKbhsykMs9ImVRvKdM6NVOrnqb68RCasuM69437ThfXcO4l1h_h3gdU1-hNNetGYFD-A=)
4. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFYHp9ShsCdtekRfViS_sGneF68RT8O1UcejFCenI8zdNh8vz5bUYFQ2xC53Iuo33XMnXfRtM-aBpwCwJqMU-28061_Jbt7JShb7bQ5jnpAELf4iNKX_QEn9uO0i7vGe94NOQBo)
5. [reddit.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFgJ1smiUlwDKOtWg48u3lYo6AVbc2EcL9hf5DxYCvvYcsXqcMb5qeIH8Br4MnCXqgxc1Ma2J7kbhSZWogosWLcHY8ZQUK1BHpaIYfWTlTHJETu8jAbGl9PnjKGobzEuYTMZ3de7aYINYE6BKvdtz_V_RoZzLbBrYTf8_kY2-1pvp6VzopVrSoHPUdW1GK1)
6. [libraries.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF-v65UMVBpZeMFJTNvnbCQYWV7fN3zV4nCpWFSMS7y1Upk_pWogcVVLgYtsPQmHWVTPr5WbcML3sH_ELuOasCnBIM__8xDfZsnZnxGEoH5CzculajJkYjkHqI=)
7. [wikipedia.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGaUrcqm6JsysKiM1IvwuYfQJFzrowZ3nRqPAhQ_FlHUjGe2mxt88HsWC9PIi53rt8VJnJ6uSpn3KolulU6stWWzYc8t3jWZBndd2fDE_SGDuoYiO89nSYVuuOCZGMb3fkbTPR2OY4PN64=)
8. [eunomia.dev](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHyOyX4id0PBq8_D-IsDCbwkepMdImdPAyrn7Cr2dTNKBQ2M43OWvaxZTJwJLek7J0bSotiyA8AuyVBCAWnQ_pD62-6lOO6x-K1pvA5bC3YRbmR)
9. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGLz03kH8xsZndd2efVdX8fB9I18fr4k_Iavbsup8G7cgHZwUN6j_NlC6lLXM1EGH9nkkIMoxNHQiAotFtlCS9Fz5rtwH-EZXTkkBZSziB4mte729tj4PfI)
10. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH-A_4nOzPdKKYP-AH3YcAPNfBwkkqYwK-Uk-4H9_cFNeWTJomuGzcFnBN6smRxWCKQmKhG80lpfmlVgIqE8Cj4Rqhb380Elm2tezn2slF3kGRVnok0ukV2CoTcRY86)
11. [medium.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFmB1RyC2TbJDNWqHXySzw2QlmEA3hn0XqkcN_k9mcYwew8qVYoxYlNHbWPpHAN4XZ9UEVlfJM2IrCzbFxT7twstFjHaYXxSipQIF9X_OkK9j5BzPL6tzR95hm9rPDMogtb672hEqLAPZowe6WxKlzSeNs3aFseW-mmFkGRMv0ilCi9gRR7mNe_43wN3XCC3SuK5DTmF5sGJkSZvxjOrd7vNe2XMC5kNL5sKlqC-ImuYMmuXNo751o=)
12. [agentictrust.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHOno3y0fqMHqSIrLdpoaTb3DUUMp9WdAnPyjLxJmbKCJuDxf932feFcThej51mWnX2VSb4iU57HJE72wk5DzTip14QKpjtZEgHO-vWETqxQuOd353NqImvtrNq1QOD3zDStWf10r7aFQkojZuMkB_AxsDXsgTsx4prixH_XzskcbCU2QfgciJtLj0n3loXXzoieYGdcWjmcm2WO7hilgHPJ3SIaw==)
13. [ietf.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH1HGSTOfNuGKthEW2ImkMdw7yMGDFr6AeNXbdnM4fkTZ8et8403BaIYn3olM8alFggX7PCVlaE7nQj6pT2nrP-82IaImSt_52kQE-dLQpp8RuUSJ_RcqW0U_R0z6CpbY52A3TcQYHTB6fSgVOzAqU=)
14. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH9wyqZXcBejNRODv7P-o9tsz6xUiFA8W-u9vXU2y0X0c31zRGHwHIPBxiaL9vttPe1lHsSD5QEJYztWrZKtIpCIwQhQEs6DeYVvdCXNhF2AoYIbuH3UZvN0a4cD8VPwWpFXaeHDlX8IsS7R0CQRuEG7XE50fo=)
15. [potaroo.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEvJexyCtfapwizJUmPQ4ObYmtbLVf72NZ96Xf-tWJkO3mPQCvVwrsTIFi_k9aF4qV67jFnMn3FeD14t4sSa3RrPnOYY6hAbZ8sfHckwTdhk_fupYuQdV3h4B8RmGDHAjRJxm6hCPED)
16. [chatnexus.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE5ASvp_gVPu5OYzLEWMo_bcdxnyhBtUqMDXP1UfOGDCWKLrLjfUILS86bp3XUziOZoJb5jAHr1KKOEUsXStqcARTuINwY87ABNcciqDbJ1XYuyvhC9Z2NGSgE7_JquY37rSwYTiBfkgfduW5j2L4mIVVbvuRCq-eAv0MrFgFKz95uetnOtePXvLhmQ1dKE7aoQnpI6oT1-BcAuhfa_Iw==)
17. [accuknox.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQE--yguQCBdjd45Vbwl66Jl0B7XeNChKwuvTo9gNbBOXVmVdHEf7yyG6UubW1ESCy1eJD-kbO2nxSZ2AE_4-D-MRqWfPmH_P-DeJwjT_UvW4u7m-M0Z9fGCZb2ALCMlbs8C74HDEjGJQMIw6Mwi84E9LhCeVPHVnr_U_Qb0JWipiPwWgcT3sGYP)
18. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFQqB99A6L43awjlRzc6HRWzZ1CwAtUihD9DNOiCFJPa-p5ZTmJZMLVAzeWE2hNohdbYe9a7KafqTL9u6xWDPCX-XYovfW3gm2Nfu-8V1hC35wsc7m_85pY)
19. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGaV9KJkww4L5Cj_yl1qsD1lTOX8Hh1mV-pg5PsYJZX5SEHILVLZNQ4tPbUrqvkmyzaTvTTE7c5UXF4tqDUZSTkRrV8pbml1eWLJpo9WumzG8rxeV9zox3l)
20. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHoKwiINuKZSQXAxoGgQEEit9soG6AaY2ZakXvTU8Qwr_mCyGNVmVG8DDZd4bamt11BwXYyLy5HQwirFoHVmf4v06hdR9XRvBcbjUFneZCbWs_1JGO9)
21. [eunomia.dev](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEzCeCrHI90vHpa_xMv75lyVvaDhPmpcV1v5KUHy3mUNS9dF3d3u6usNBDS9b9TOO8KrOVSJmdDP1o4yS_WUT7DcZT9l_HcMxScNkpuOgSLJFLoVzBPIckmNGUquH9d65g4vq5h0oHxj7zvXJIGiX9tt4BlLtQQTiVEhHEa-1FSfzZcNDvKfNEx__Z0SpuuQacR4VFKC72MlkTmoFvqJHQDmJPdxqLHpYbSA7Zakzw8wQ==)
22. [merge.dev](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGCR9tnmm76kNNPQWxC-lQYIVdpwNPrsYRFATpd8WmGu6ktOh8MXq41v3Yl_wTFdXHkfBurIerdlt02MG8eOA063vZR7LZKStztLcWHaD1JLBg281inSKIxNAy3oJDnUwtMW-l560A=)
23. [medium.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHaP9eq0aD7YZGimJ4W9cOWYV71-m08cSMdHrsnZxzs51eGs7dyRBsyCYYiCTpckUG6u4kpz3VGOmjI3ItYOjQqrY271tv_aRYoPwX4JYPy-G0eBl2DU0vqF1QEFUp4UaxmQkljDSPJDLak9lu7Q5ReiX50DBleFQv2lf1ZynG8atkIiZWqB_5YUrYWV9szVAIBMBlBvsMfQNATetn7siU2zRL-tVg=)


[LEGACY_UNAUDITED]
