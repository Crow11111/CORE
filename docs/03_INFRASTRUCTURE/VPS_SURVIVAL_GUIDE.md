# VPS SURVIVAL GUIDE: DOCKER-NETWORK & DNS (OMEGA V4)

## 1. DAS IP-VERBOT (Axiom 7 Erweiterung)
Hardcodierte IPs wie `172.23.0.x` sind in der `.env` auf dem VPS **STRENGSTENS VERBOTEN**. 
*   **Warum?** Docker vergibt IPs dynamisch. Ein Neustart des Stacks bricht jede Kausalkette, die auf IPs basiert.
*   **Lösung:** Nutze ausschließlich Container-Namen (Service-Namen) als Hostnames.
    *   `CHROMA_HOST=mtho_chroma_state`
    *   `POSTGRES_HOST=mtho_postgres_state`

## 2. DER DOCKER-DNS KURZSCHLUSS
Kong kann einen Dienst nur auflösen, wenn:
1.  Der Dienst im selben Netzwerk wie Kong ist (`omega_internal`).
2.  Der Dienst den Status `Running` (nicht `Restarting`) hat.
3.  Der Upstream in Kong auf den Namen zeigt, nicht auf `localhost` (was in Kong der Kong-Container selbst wäre).

## 3. PORT-BLOCKADE-HEILUNG
Falls `port is already allocated` auftritt:
1.  `docker compose down` im alten UND neuen Verzeichnis.
2.  `fuser -k 8080/tcp` (Radikale Heilung auf dem Host).
3.  Prüfung mit `docker ps`, ob noch inaktive Container mit demselben Mapping existieren.

## 4. DEPENDENCY HANGS
`google-genai` >= 1.0.0 verursacht Backtracking-Hangs. Fixiere auf `0.4.0` oder nutze nur `langchain-google-genai`.
