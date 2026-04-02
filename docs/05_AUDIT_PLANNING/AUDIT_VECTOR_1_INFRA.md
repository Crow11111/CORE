# AUDIT-VEKTOR 1: Infrastruktur & Zero-Trust für LLM-Agenten

**Ziel:** Ermittle die absoluten Best Practices und härtesten Architektur-Patterns (Stand 2026) zur Absicherung autonomer Multi-Agenten-Systeme auf Infrastruktur-Ebene.

**Fokus-Bereiche:**
1. **Runtime Authorization (Laufzeit-Autorisierung):** Wie wird kryptografisch und architektonisch sichergestellt, dass ein Agent, der dynamisch Tools aufruft, nur genau die Berechtigungen hat, die für den spezifischen Sub-Task nötig sind? (Schutz vor Privilege Escalation durch Prompt Injection / Guardrail Poisoning).
2. **LLM API-Gateways / Firewalls:** Welche Metriken, Filter (DLP, PII-Redaction) und Zugriffs-Kontrollen müssen zwingend auf einem dedizierten Gateway (zwischen Agenten-Logik und LLM-API) liegen?
3. **Container-Isolierung & Data Segregation:** Wenn ein Agent Code ausführt oder auf Datenbanken zugreift, wie sehen die modernsten Isolations-Paradigmen aus (z.B. Micro-VMs, ephemere Container, Network Policies), um den "Blast Radius" bei kompromittierten Agenten auf 0 zu reduzieren?

**Anforderung an den Output:**
Keine Marketing-Texte. Liefere einen dichten, technischen Architekturentwurf oder eine Liste harter Constraints und Konzepte (z.B. ABAC, SPIFFE/SPIRE für Agenten, eBPF-basierte Überwachung), die wir als "OMEGA-Axiome" in unser eigenes System überführen können. Zitiere konkrete Mechanismen.


[LEGACY_UNAUDITED]
