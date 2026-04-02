# Detailliertes technisches Design für die Implementierung von SPIFFE/SPIRE JIT Ghost Tokens und Firecracker Micro-VM Isolation für Python-basierte KI-Agenten auf einem Hostinger VPS

Key points:
- Research suggests that integrating Firecracker microVM snapshots with the Model Context Protocol (MCP) over virtio-vsock can enable secure, sub-30ms air-gapped tool execution for AI agents.
- It seems likely that deploying Firecracker on environments traditionally lacking native nested virtualization, such as standard Hostinger KVM VPS instances, can be achieved using advanced hypervisor modifications like the Pagetable Virtual Machine (PVM) framework.
- The evidence leans toward utilizing SPIFFE/SPIRE for Just-In-Time (JIT) ephemeral identity issuance, effectively countering persistent "Ghost Token" vulnerabilities by ensuring credentials are wiped from memory immediately upon microVM suspension.

The deployment of autonomous, Python-based Artificial Intelligence (AI) agents introduces profound security paradigms, particularly when these agents require access to sensitive enterprise tools and code execution capabilities. Allowing Large Language Models (LLMs) to generate and execute arbitrary code natively presents unacceptable risks, necessitating robust sandboxing. 

While containerization offers baseline isolation, it shares the host kernel, leaving systems vulnerable to container escape exploits. Micro-virtualization, specifically utilizing AWS Firecracker, provides hardware-level isolation while maintaining operational efficiency. However, integrating this isolation with modern AI tooling protocols like the Model Context Protocol (MCP) without introducing severe latency bottlenecks remains a complex architectural challenge. 

This report provides an exhaustive, academic analysis of a state-of-the-art 2026 architecture designed to host Python-based AI agents on a Hostinger KVM Virtual Private Server (VPS). It details the precise mechanisms required to achieve air-gapped execution via virtio-vsock, eliminate context bloat using deferred MCP tool loading, and enforce zero-trust identity using SPIFFE/SPIRE JIT tokens.

## 1. Architectural Foundations and Infrastructure Constraints

The foundation of this architecture relies on deploying lightweight virtual machines (microVMs) on top of a commercially available cloud infrastructure, specifically a Kernel-based Virtual Machine (KVM) VPS provided by Hostinger. 

### 1.1 The Nested Virtualization Challenge on Hostinger
Firecracker is an open-source virtual machine monitor (VMM) developed by Amazon Web Services (AWS) that utilizes the Linux KVM to create and manage microVMs [cite: 1, 2]. By design, Firecracker relies on hardware virtualization extensions (Intel VT-x or AMD-V) [cite: 3, 4]. Deploying Firecracker on a bare-metal server natively leverages these extensions; however, deploying it within an existing virtual machine—such as a Hostinger VPS—traditionally requires nested virtualization [cite: 3, 5]. 

Research indicates a divergence in support for this feature. While some advanced deployment orchestrators like Fireactions utilize VPS templates to set up Firecracker on hosting providers [cite: 5], official documentation states that advanced features such as nested virtualization fall outside the intended scope of Hostinger's standard VPS services, as they can impact system stability [cite: 6]. 

### 1.2 The Pagetable Virtual Machine (PVM) Solution for 2026
To resolve the absence of KVM nested virtualization, this architecture leverages the Pagetable Virtual Machine (PVM) framework. Proposed in 2024 by Ant Group and Alibaba Cloud, PVM is a virtualization framework built upon KVM that allows hypervisors like Firecracker to run on regular cloud VMs without the need for hardware extensions or nested virtualization enabled by the vendor [cite: 3]. PVM achieves comparable performance with bare-metal servers, enabling environments like a Hostinger KVM VPS to seamlessly host thousands of Firecracker microVMs [cite: 3]. By applying a streamlined patch to the Firecracker VMM, administrators can bypass the strict KVM hardware extension requirements, making the Hostinger VPS a viable, cost-effective host for air-gapped AI agents [cite: 3, 7].

## 2. Low-Latency Air-Gapped Execution via Firecracker Snapshots

A critical requirement for AI agent user experience is low latency. Standard Firecracker microVMs require approximately 125 milliseconds to 1 second for a cold boot, depending on the kernel and initialization processes [cite: 2, 8]. When an AI agent iteratively calls multiple tools, a 1-second penalty per tool execution destroys the conversational latency expected by users.

### 2.1 MicroVM Snapshotting Mechanics
To mitigate cold-start latency, the architecture relies on Firecracker's snapshotting mechanism. MicroVM snapshotting serializes the complete state of a running microVM—including guest memory, CPU register state (instruction pointer, stack pointer), and emulated hardware device state—saving it to external files [cite: 8, 9].

When a Python agent requests a tool execution, the system does not boot a kernel or run `init`. Instead, Firecracker restores the microVM from a pre-initialized snapshot [cite: 8]. Firecracker creates a `MAP_PRIVATE` mapping of the memory file, resulting in runtime on-demand loading of memory pages with copy-on-write semantics backed by anonymous memory [cite: 9, 10]. From the guest's perspective, time simply skips forward [cite: 8].

### 2.2 Latency Breakdown
Empirical research demonstrates that snapshot restoration reduces execution latency to approximately 28 milliseconds [cite: 8]. The process is highly optimized, ensuring that the AI agent's tool execution environment is ready almost instantaneously.

Table 1 presents a detailed breakdown of the snapshot restoration latency for a standard microVM running a Python environment in 2026.

**Table 1: Firecracker Snapshot Restore Latency Breakdown**

| Execution Phase | Estimated Latency (ms) | Technical Description |
| :--- | :--- | :--- |
| **VMM Startup** | ~5 ms | Spawning the new Firecracker process and loading base configuration. |
| **Memory Mapping** | ~8 ms | Establishing `MAP_PRIVATE` mmap against the guest memory snapshot file. |
| **State Restoration** | ~10 ms | Restoring CPU registers, virtio queues, and serial port state. |
| **vsock Reconnection**| ~5 ms | Re-establishing virtio-vsock connections and signaling readiness. |
| **Total Latency** | **~28 ms** | Total perceived delay before arbitrary Python code execution begins. |

*Data synthesized from microVM benchmarking research [cite: 8].*

To further optimize memory restoration, the architecture employs on-the-fly decompression of memory snapshots using `userfaultfd`. As the VM accesses memory that triggers a page fault, the hypervisor intercepts the request, decompresses the required memory chunks from disk, and fulfills the read dynamically, preventing the need to decompress the entire snapshot upfront [cite: 11].

## 3. The virtio-vsock Air-Gap Implementation

To ensure absolute security, the microVMs must be entirely air-gapped from the host's TCP/IP network stack. Firecracker emulates a minimalist device model consisting of only `virtio-block` (disk), `virtio-net` (network), a serial console, a keyboard controller, and `virtio-vsock` [cite: 8, 12]. In this design, the `virtio-net` device is purposefully omitted. 

### 3.1 Socket Translation Mechanics
Communication between the host (the AI orchestrator) and the guest (the Python agent environment) is achieved exclusively via `virtio-vsock`. This provides a direct, high-bandwidth kernel-to-kernel communication channel that completely bypasses the host's and guest's traditional networking stacks [cite: 8, 13]. 

Firecracker implements the `virtio-vsock` device model by mediating communication between `AF_UNIX` (Unix Domain Sockets) on the host and `AF_VSOCK` sockets within the guest [cite: 13]. To multiplex connections, Firecracker maps guest `AF_VSOCK` ports 1:1 to `AF_UNIX` sockets on the host [cite: 13, 14].

#### Host-Initiated Connection Protocol
When the host orchestrator needs to send an MCP request to the Python agent inside the microVM, the following protocol is executed:
1. The host connects to the `AF_UNIX` socket defined in the Firecracker configuration (e.g., `/path/to/v.sock`) [cite: 13].
2. Upon connection, the host sends a plain-text routing command: `CONNECT <port_num>\n` [cite: 13].
3. Firecracker intercepts this command, validates the port, and forwards the connection to the guest software listening on the corresponding `AF_VSOCK` port [cite: 13, 15].
4. Firecracker replies to the host with an acknowledgment: `OK <assigned_host_port>\n` [cite: 13].

This mechanism eliminates entire classes of network-based vulnerabilities, such as Server-Side Request Forgery (SSRF) and traditional port scanning, as the guest possesses no IP address or routing tables [cite: 8].

## 4. Model Context Protocol (MCP) over vsock

The Model Context Protocol (MCP) is an open standard established in late 2024 by Anthropic that dictates how AI agents interact with external tools, APIs, and file systems [cite: 16, 17]. MCP relies on JSON-RPC 2.0 to standardize remote procedure calls, decoupling the agent's reasoning from the tool's underlying implementation [cite: 18, 19].

### 4.1 JSON-RPC Transport over vsock
Because MCP is inherently transport-agnostic, it can be seamlessly routed over the `virtio-vsock` boundary. This requires a proxy architecture bridging the host's orchestrator and the guest's execution environment [cite: 20, 21].

On the host side, a high-performance proxy written in Rust (e.g., `tokio-vsock` combined with `mcp-proxy-tool`) acts as the intermediary [cite: 20, 22]. The proxy receives standard HTTP or STDIO MCP requests from the LLM framework and translates them into binary streams sent over the `AF_UNIX` socket linked to the Firecracker vsock device [cite: 13, 20].

On the guest side, a lightweight Python daemon utilizing libraries like `fastmcp` listens on the `AF_VSOCK` port [cite: 23, 24]. It decodes the JSON-RPC payload, executes the requested Python function (e.g., data analysis, file manipulation), and serializes the result back through the vsock channel [cite: 18, 23].

**Table 2: MCP JSON-RPC Payload Structure over vsock**

| JSON-RPC Field | Type | Function in Architecture |
| :--- | :--- | :--- |
| `jsonrpc` | String | Must be exactly `"2.0"` to comply with MCP standards [cite: 21]. |
| `id` | String/Number | Unique identifier mapped by the host proxy to track asynchronous tool executions [cite: 18]. |
| `method` | String | Specifies the tool operation, e.g., `"tools/call"` [cite: 21]. |
| `params` | Object | Contains the strictly typed arguments validated by the Python agent (e.g., via Pydantic/Zod) before execution [cite: 21]. |

### 4.2 Eliminating Context Bloat via Deferred Loading (Tool Search)
A severe limitation of early MCP implementations was context window pollution. Connecting to an MCP server historically forced the LLM to load the JSON schemas and descriptions for every available tool—sometimes exceeding 90 tools and consuming upwards of 46,000 tokens—before any useful work began [cite: 25, 26]. This bloat exponentially degraded tool call accuracy and increased latency [cite: 25].

To prevent destroying the user's latency and context limits in this 2026 architecture, we implement Anthropic's "Tool Search" and "Skills" mechanisms [cite: 16, 25]. This feature treats the MCP server not as a static repository of injected prompts, but as a dynamic filesystem [cite: 26]. 

Tools are configured with `deferred_loading = true` [cite: 26]. When the AI agent needs to perform an action, it issues an initial search request to the MCP proxy. The proxy returns only the schemas for the specific subset of tools highly relevant to the current user query [cite: 26]. The agent then writes and executes a specialized Python script within the air-gapped microVM to interface with these specific tools, effectively replacing massive context injection with efficient, on-the-fly code execution [cite: 25, 27].

## 5. Security: SPIFFE/SPIRE and JIT "Ghost Tokens"

While the microVM provides hardware isolation, the tools executing inside the VM often require authenticated access to external databases or APIs (proxied safely back through the host). Managing these credentials introduces the risk of token theft.

### 5.1 The "Ghost Token" Vulnerability Concept
The term "Ghost Token" originally referred to a critical vulnerability (CVE-2026-0012) discovered in Microsoft Entra ID and Google Cloud Platform (GCP) [cite: 28, 29]. In these exploits, an attacker authorized a malicious OAuth application and subsequently placed the app into a "pending deletion" or hidden state [cite: 29, 30]. This effectively removed the application from the user's management dashboard, preventing the user from revoking access [cite: 29, 30]. The attacker retained a "Ghost Token"—a refresh token completely detached from the core identity lifecycle that survived password resets and MFA enforcement, allowing persistent backdoor access [cite: 28, 29].

### 5.2 Reversing the Paradigm: Just-In-Time Ephemeral Identity
In this architectural design, we invert the concept of the Ghost Token from a vulnerability into a defensive mechanism. We implement **Just-In-Time (JIT) Ghost Tokens**: highly ephemeral cryptographic identities that exist solely in the volatile memory of the microVM and vanish entirely—like ghosts—the moment the execution terminates, leaving no trace that could be exploited by persistent shadow IT or sandbox escapes.

This is achieved using the Secure Production Identity Framework for Everyone (SPIFFE) and its runtime environment, SPIRE [cite: 31, 32]. SPIRE acts as a workload identity provider, issuing short-lived, dynamically rotated X.509 certificates or JWTs known as SPIFFE Verifiable Identity Documents (SVIDs) [cite: 31, 32].

#### SPIRE over vsock Architecture
1. **Host-Side Agent**: The SPIRE Server and SPIRE Agent run on the Hostinger VPS host OS [cite: 33, 34]. The agent validates the host's integrity and listens on a Unix Domain Socket for workload attestation requests [cite: 33].
2. **Socket Bridging**: Because the microVM is air-gapped, the host's SPIRE Agent UDS is bridged into the guest VM using a secondary `virtio-vsock` port [cite: 33]. 
3. **Guest-Side Attestation**: Inside the microVM, a modified SPIFFE-helper or a user-space Seccomp agent intercepts `open()` syscalls made by the Python agent when it attempts to access an identity file [cite: 35]. The Seccomp agent proxies this request over the `AF_VSOCK` channel to the host's SPIRE agent [cite: 35].
4. **Attestation and Issuance**: The host SPIRE agent attests the microVM's identity (verifying the VM's PID, cgroup, and execution context) [cite: 32, 35]. If validated, it issues a JIT SVID with a lifespan restricted to mere seconds or minutes [cite: 32].

### 5.3 Memory Wiping on Suspend
To guarantee that these JIT Ghost Tokens cannot be extracted via snapshot cloning or memory scraping, the architecture utilizes the `MADV_WIPEONSUSPEND` memory advice flag [cite: 36]. 

When the Python agent completes its task and Firecracker pauses the VM to take a snapshot, any memory pages marked with `MADV_WIPEONSUSPEND` (which house the SPIRE SVIDs and any cryptographic secrets) are automatically zeroed out and excluded from the snapshot file [cite: 36]. Upon restoration, the VM must request a fresh SVID. This ensures that a compromised snapshot file contains no actionable credentials, fulfilling the promise of true ephemeral ghost tokens [cite: 36].

## 6. Concrete System Architecture for 2026

Synthesizing the components described above, the following outlines the concrete execution flow for an AI agent hosted on a Hostinger KVM VPS utilizing this design in 2026.

1. **User Request Initiation**: A user prompts the AI agent via a web interface to "Analyze the Q3 financial data and update the core database."
2. **Dynamic Tool Search (MCP)**: The LLM queries the host's MCP orchestrator to discover available tools. Utilizing deferred loading, the orchestrator returns only the schemas for `query_db` and `pandas_analysis`, avoiding token limit exhaustion [cite: 26].
3. **MicroVM Restoration**: The host orchestrator identifies a pre-warmed Python 3.12 microVM snapshot. Firecracker maps the memory file (`MAP_PRIVATE`) and restores the CPU state in approximately 28 milliseconds [cite: 8].
4. **JIT Identity Issuance**: The Python agent wakes up and attempts to access the database credentials. The guest Seccomp filter intercepts the call and requests an identity over `virtio-vsock` [cite: 35]. The host SPIRE agent attests the VM and issues a temporary JIT Ghost Token (SVID) valid for 60 seconds [cite: 32, 35].
5. **Air-Gapped Execution**: The LLM sends a JSON-RPC 2.0 payload over the primary `virtio-vsock` channel to the guest's `fastmcp` daemon [cite: 18, 23]. The Python agent executes the data analysis using the requested tools. Since the VM has no `virtio-net` interface, it cannot exfiltrate data directly; all database queries are validated and routed through the host MCP proxy [cite: 8].
6. **Result Propagation and Suspension**: The Python agent serializes the analysis result and returns it via JSON-RPC to the host [cite: 19, 21]. Firecracker immediately suspends the microVM. The `MADV_WIPEONSUSPEND` directive permanently deletes the JIT SVID from RAM [cite: 36]. The microVM state is updated and saved to disk, ready for the next sub-30ms invocation [cite: 37].

## 7. Conclusion

Implementing air-gapped, secure execution environments for AI agents demands a delicate balance between rigorous isolation and low-latency performance. By deploying Firecracker microVMs on a Hostinger KVM VPS—augmented via PVM for nested compatibility—organizations can achieve robust hardware-level sandboxing [cite: 3, 8]. 

The integration of `virtio-vsock` guarantees absolute network isolation, while the Model Context Protocol (MCP) ensures standardized, bidirectional JSON-RPC communication [cite: 13, 38]. Latency is strictly minimized by leveraging Firecracker's sub-30ms snapshot restoration capabilities and Anthropic's deferred tool loading mechanisms, solving the context window bloat problem [cite: 8, 26]. Finally, the novel adaptation of SPIFFE/SPIRE to issue Just-In-Time "Ghost Tokens"—ephemeral identities wiped upon suspension—ensures that even if a microVM is compromised, the blast radius is strictly confined to the milliseconds of its active execution phase [cite: 32, 36]. This architecture represents the pinnacle of secure, performant AI agent deployment for 2026.

**Sources:**
1. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFfvXhWrkJ_EEG3RaXPXVIUw1Wkoj52TFz8mkMIDXYcmYDIg_9rOkRw-gtUqC78k8ftfxflC60GRE_wUk8ffvBdQzhruKxNqPwD092hgXBjXJdZsh1OccjKezyhjg==)
2. [amazon.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHwb1roMnw4-BogzdLThbPbU9QiNtoyKBd9HbHy6KM5-5XKi431rkefpo0Pwk2T_6vk4uMzqoeIQQHhHi3CYvhkQ_oeKXBJ14VkDFMa0C1pxcrzITkVJ-d6JvFTUi2fyywqS9bil8Tntv81B4L1I_E1mxGBdU0NUNI3rJ2GOrXK1d9uRF4a4z-Hlyv5VFqBEzg3qsu0l8JJ)
3. [alexellis.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHnD9nJJfz0NMlL41D6-dNoVUlqUrrwaPVYIYyQPNsewolA0RlqH34oTpaoiBeG97g2uFAQLj2KvtOEcFj5cKY3j6tDDat5eC0R3JLRg79kGgn5DuL8swJhh69fC7zzrKvTWcgTuOLHOI8pJYImdM-BCj0aNm8S00niuT3KoeM9j4_AJ1r1WkgR)
4. [hostinger.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFKmG2XoMN9wVgxvmN2nyVyuVH27nQpBiz0vsU-Jwu7v2Rxq620s6TfQhW1Y47PHThvlHYM-lxhdU7VeN8gT-3vQOz-86eAMoIUdV0Us01P8Dg4CDqOfPEzELBghjNqCjHCLV4DBVj9s1iG5rYONON8GR-CPmQaHLIGqeXp)
5. [hostinger.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGb31r3UAFmhI-K8asMzMcfW_6wQO3nSG-RFa5cJB23J4ShWeC5rf1tmAOi_KMFe-DaX7b2WEgB1u3DNX8oz5ZkgcxcCKII1M_PiMwHdM7g_pzSvzeIMY-cLUpOA4SkBWw=)
6. [hostinger.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHeJPSeVJmvmxLdC_MeZo_X_pTmVAcnYNTSfUg8wo6BAnKwa5-_Uye_IRJfPm60JyQSNnDS_McPToGLga7djQ2sQyk1utkLLehNxgQiUvdevpv6G7z2YephvO_va96IpB7HOaBXeCcvC84F_EOG4lsMK8TtXq0hygiPs0hhxK5bcuBAPEmdNdshdJxdXoN6wF6C)
7. [sourceforge.net](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFzOLj6HvjpQhZb9Znljl_vbnRgVc-aFKI5r4RGUSayXeWwG7Yx6F0iEpyfKJ4ATbyTediT8YFyaDhdeq1JQ2b5qj0g0nfKxAGCyExZT7_6w_Xps7rGZrpOtcuaWdM1tiEKaCTYy2Cq)
8. [dev.to](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHIuuisjr1-YHkkIB9t9CIJNB0-gXzc6HTLzXt4eQBZ4uHKy7-ASo5aATnEeJZQKBvOtjki6INUqW4O-uPRUfiurIgvI9x3yasYhCaTijryKWUzwqTt69UnCe-iIeR3L2k_6RGYCYtf5ymO_wcj1PwZQE_sbRLXMyax42QpiNab58M4PXpoL72TqgBTs2jDhnr0nXz4rw==)
9. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGnymVrF-Hz9WCtSleGvD-dc0L5KtV0XoJq0f2ytHLdr88hUSfEPLCFQhFYyZ9tpCQJ1XYgyoXZM4kP9W_REzlWGD5cpKMCMswPldyfsjhfxeBvlKwQJAt2AOgLe0jx-TU3EUkkrrPcaovyyfsOHKb-m1FUBjQ-N9xPpo6pODJxLnw5NeQb9mu8Z6ERKvI9kN0e7En-DxZ6Zg==)
10. [stanislas.blog](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGU58faajOu7OOK80-vW5rpTKxtyJ7Caf_D9fIYYAnWJxTEjdnukLrqMx5SrPGsDcQAGYVcCHO23aUReWpuc6WOzBAckOzggeoSBXvEbLOEcMouaPQEKjUaO3lADcyvXTE3)
11. [codesandbox.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFtGGU-jBWwxkHnTspmcJoGB6ogWfJKmi61d9wOCvHd0zvuPQnijWr_2FKAfJw0WCxZp2X4KDFqbo01pnFuit-8-sOiaP3D8VeDjVvy6JB8lw3PJJKIntASvbd1LHw7TWogAkXsw3ME-oxfXu-ETkcraB9PVY_MOXW7RJ7Xv85GIaP2PyS_tUGVyrf0_I7LFunkZEEMzp_BSOH1ARvTfd_y)
12. [stackoverflow.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF3Qvigm1b4r62_CI9O1nOO0RcMFXrUk6FRLvTTE4iE4DivJa8dmfatxEh0EoenGy8zHibli8utSdQc1XpvXqYFSSl4TQYBlGR5yNa-RXnnSxfliMQbuCeX-EojJDaGNgaROiiY1yOYn4zDhSv6-0hiCSg8WGo_QGeEP-tN9abtQr5PYPaJr9-SMIQ3bSFFhwV2irQq8OKImTe3IUWBcvdZLFU=)
13. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEGHClaZIf0b2j2ALFLDAIMPy9KM3xmsSoMFK75_tlyMfpbV8H6v9RK2Lbg5cYkc8QaurHyVCWs6xU8Usuzt8X9hwZK_GqhR_hL_f6PdNLrR_i0F4Zm2HWgDHNO71AegCzZUOlPS283eRk_KJvJrbss8AX6V531fHamyZ-NlWwBfQ==)
14. [gitee.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFbslSpHzmKJKRSgRQIvdjhbImHA2OdnW4fgASNWChiGKmrUZ96r-rDkngLI4QEOQVkcl7t9yh0p-8cTYlX2p7c-7vnmEZB_xkL9EKcyNud0wBxEeTPNkZrneCd7WhGSNJS50TlgldMcp666ee4haFjYHnEsQJfSCuzyDRgBhtoZ_LNnmF8hWFl)
15. [github.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHkOqD79DxiPE6_WhqQ21WtH-Ngoi6wMlJs_UGCh-AVIV9We1Rh79ySk_Sojmz6eDOf_tevt6MXogEpEaaExy2bMJV5ptDzPokY6H-PZ0qnrlPHddaWOEVcoOGohem7MauTynpEDLWR_D9EoqGaoh8QNcH45IQT_u4t5mNSDJq15g==)
16. [anthropic.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHmqsr6ZPnV5dG9tEGF22l36YgwS9ltFi_qs5j3ofPRi_lb1ktam7G2xih6bD8s01af7EOqvHotKHK3dEirrQUUtUS-2Icp2xeIF9xPSzXHEmxCgLRf5320QTA77WzxkPtlJ3Kj_rEqnIJYex3BlHUpgt80uUGswryrWbsfnEai4wEDa0I5R0DvHtH95gQgXjBx64jprrKZwNT55BbBCwGOKlKTbKV4)
17. [bytebytego.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG5oaNjgd0Q4z6InN8S5HXMSTxKyETQSr4E2ks0nKcdsf2YmSVZlKZ7JgIoqcNaOpmMWPuqgZkMeuXzC0uTav1D442pJ_cmvFYwlQZPkzErOh1a7XSGKkZyz8r79KUM569-WvPdmWf6tbqOxek4i9jUrltuKA==)
18. [milvus.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHwVUlxFyibtzU2gFWseWtejoODSa_wYsn1_4V57X5AZtauNmmXRfIX6AxKZi6iQueL7fBNammHlWNe_7tQw4tMlUNrLGQHxm1s1EtewHpziSAvyZl-T0G-EJ9uaq27XiBmF8POllWrjF4CrMMCF491ZhSwCrz-sxpcO2QwYTazL3hb2Jn8yCijf8PpDQ==)
19. [stytch.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGMds7sTXFNeCir1izWjpso87d25_1bO4-Rw3EgH6_FCF4xhxf28ItnYTPxYY1dai7OXaDtCfeYodQEPQXkPZoyzEVg0aHSq4_nvnYCQYXe4oDWkITrxrBUdbwmX6RXizuf_Uy8iUFxSVNX1An2jfRoAdE=)
20. [crates.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEbLel1EWBJYAv6hZ59Q2v-Wn2nlrcixumRJvKIUnRYdzpKvREalQkJS5Ut7T50MOKG4JqUyoThocZxUmQQhZrT1UKMIM8ppPworx50DYBb51gFlw9Z8DaSJxifj6Y=)
21. [medium.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHdQyGVblfvb6p6_lN9jaT26ybiwIKGt1fsqlMn-RrqUJwfy3Z1me_s6aM57my-wE0mDXNids6y9LGpIUE687oabNNUCDoOgqiDyg0p1IZgaRuyQA7wLQsehPlIfnqtqVcshefU8lSnmaY_jYh58A8zWwFSKNSA73P2n2nnl-gATXFSOGR0Fm48On8=)
22. [github.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFCbvFKWTSImyB37l7VgWj0JeSXIpq8-MDGE064-tuSRtKpRjrYJzx74m_vXwbp85qDQ1fJMYNG4h_C6E1gwDOk_ouKrTUH-TgBWBK9WdSELBMxEn-nNP3pjSjErJWwkg==)
23. [dev.to](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFUpFWC8ZZGpiUuJZbXc409TsyYBgvvKa9OTyMbcTsgizwHJnN5sKLjvrhvXbI7T4JU_hV1kEM_e97UjviImgBbViwK0xKOHkZCvBZzfkG_XIQfwGwZMz1lAZRDhjlRDaRwOaWBzHIPmOW0HhRbUHo0gNC8b4q4HHOMJiK8rk3nUa00)
24. [medium.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHa0CFkHqVceswFss42KGaURXlfYFSBuPEeoOwvOklbp4oC0QrhHUXtltK3x_d8TBYyLM6j4H8nHWSWz2gGIXPxEgkopoeSgahdJ0AsTGJ73jYKIl1BFVZQnyj3S87c3rlP9M8zgv-JaMU67RcpqPSj26iXOFNfNSL012qqUI5TGnbCjE9DYXmG-toBIYVrqY_hcQwOmGViqIpAlslSP5IWEybyZgPX8B0Fa9uMapR3jYuyR6b7zz3Lwbzq7Bk=)
25. [medium.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGTeDOT8FAp2CyyLAnzha-eHgzRbpBITlLaIx3OdUnxS3XonXc848W89Kk9rIq6rJBAYISfvSrec0U-44PzB0Kt8UFHty1VaZDOvMzYRX9g8xjVjJlm4yfF_j8uS7Xt7uH5drkBXosKLGDbJyfOO7eKJSnkKhUr1UEhtUfcDsV5belzKE0L0GisWA4=)
26. [youtube.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQGmZzsr0kE6Cj5pDMbahu_CxZ528das0piqN4XrFmFvcagh0S8_luJJO2aNl93XZen-sN16JHGanil6pzLbSCHc6Lpp42Zoh9__J-gSBZZMnwg8zmBYs4tglKRkqRYQPVhV)
27. [youtube.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQG8BwgpytZraqkR1CH1FXa8TcA5kOSkRhrnC5O2Wl3IgAFJcnsRlkHOXVqRL-KC5As0bpCJPPBizM3VLn1I8W_DtOjy6qoeWlhe5VNK0H9_2yTOXf0XYxLAMYpH88nkUjx8)
28. [sennovate.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQH6mG0VLvDGjkRmZ6i1v9v8Sd9qJnEXiUDRBrYuJBDyV0255D8QJj00ktJ2G8X-Qg9LxCgYoF87vz0rC7A3iRQ_PAHs4M737mo1O0whurx35mbCGwFUAEb7afUOyyHI92sQ4sGQxIaSIzb3saXvL3bEUA80L0NpGV2d2rly_MMgAMiDEns_0j-tnwLpWJfM3fqXDz8YZeD_4oyLPGO8X3b9FV0PfJ2E)
29. [bleepingcomputer.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFwDsBJeLHedIxyg6gTMOt6ido-3Fle_PZB_GXIUfNtXIV94X4M7c7ssRtHrw12Fb7YMklFB7_WSmHb1XyOu_tFo7sBG5N7YGfLTrc_aQ_7k0q1YjOYVPuxDhdKODkDkBC4rApI3kRKkkx3F-dsMN_QrmRaqqtLCpzj2LJIzTJ6VMlCPhJz-Iq5HFJs2h2FnzZrCKFWoKLpVK7rl6LrxdXe)
30. [astrix.security](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEqenQgkm0DEgd0N29oN5D6SmCpXOb6IeY4Ymh_XO2nXO8F_pfLwC9a_kWiUTM-Qkg0-3gSbOsROarr2uxILzxPtG4VuBAQpOHwbmge2RC5zgsqpklStSM9fq7N1IXQc5QBDtQdO5PvXGApLztzicplRXwk21Fkzjq6yINoauJXMr15_FI8Up1am7-TvzpgKnJhZ_OXL9dvjJwcuJ72w1ROhm1QRbXNUdBsp3kPGZGmJAkEXvofVxee0zBBeliGY3S9E0FbG59-ArsdTDoJ)
31. [solo.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFyMX5s8XoZ4lho9ILDGNLejiXvjIB4rFBu0hldMFjojpi4r50xUUHriQEfpT9BT1fR0ERg3AHap5_MiTdmgyaGR8eVe5fkrahYyZLDqgnCbfMi6wPfogTAZhoyIVoUCFnaHTrPsoc6LTxubOg-AZKvIg==)
32. [spletzer.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQF5ExqfFKtAQqFH7oJc0Cv3PnqQsfCNpIMYhunFGSL6mtus2Lvw-pqYRvulX5bw0Zqz_iJK8olmbe9yrTaMDQ1sjQFn66fS-7TC42kXu70FLQ-fyXIELBBAu0q52wKWcWn9WOI0sPjfD0bhuyu1EnVvGd7Wq_l-Jhy9N766So0T8hE4ymU=)
33. [linuxcontainers.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHcGOdY9h_BV78X1Um3Q1cD0RjZG4b_Kxp8PqPXeY7E6Yeq2l_N55SQdwZuxA5L57S_M86gOdubg_enuyq769DBdB3wb1ai_n6Zm0_HtCgRPkXgKb6hqrjThG9_r3Z8ha0wrIw2yaafgdLcWsZGke9rjiWhzK2OATkEnJdRFJAv3d3JXB-UNqi7fCfagiA=)
34. [spiffe.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFknYHIZTCtxJHWM5yurUcdfW7ESpxpZ_pJOfMLN5-pdABmJqROa5aMbGGim1g_wKpwr6VPJTDo9DGpDy0feqVixWIstikg85fKfBbjmjtBV0j5YkN0X8m9X62sclrDYCCvdOk818Bj9YJaNRM4)
35. [medium.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQEd79A5pSmiJUpST2CZ6IU8FoYl9aOu-1BOMx-3y43_aMSfLiCUrL-OyM9dOH-TPlbFFfD2VLMZl0nRUvvOl59OXuO8-S3ML7dAIyn3sd8gIyW489dNFJ_3Yg3JfFSaR7UGvSKaafRnLfo1-Gpx4jOTqokPeqOfdNP8ymDSWGzDwfjb34-H3-9yafkQ3yWYAAJOswqG5m7wNrQNEj5AXYpr5GKXK-YmIVi0FRY_5VKw_fwjRLz03wjzMFQ=)
36. [arxiv.org](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHd5zyIzq0MiiFI8zZp8Tk_klvz5c4X-cdy79jKFwmCqhgibFOFeR0TwU1cKl0-wZCvAdL9pb5NurCitLl5LQ6_hr_KBqUoIH3wD6WtwbLer7y3OSez4NIXhNn4C5jlGKtMVw==)
37. [fly.io](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFJYXoCDRWCNVmZ3dZW_zWN8VsbJ08-ktl3YuYjyL4HT0qUF3gOqNvM4i3HgmdK6jWuXJc2DGVSpE4PUyRGN_m0IYwsfiV_tccyNm6lICdqaaxoiRIiiX2DeiHLC_s5ca166fY=)
38. [databricks.com](https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQHZW7KXWHfAAIckZMY5BQuOZfWv22V99_eJy9208Vh07TeLG067bPCDdFfNmVhbCH-mJyqwmqsW5AKq269BLOkbIX2JQA_QFqi4J_94SsNu3UrdVTfQ3qfziO6gFbjaQUmU-7rM-6dWxr9Nqq4saGnvhioRjw==)


[LEGACY_UNAUDITED]
