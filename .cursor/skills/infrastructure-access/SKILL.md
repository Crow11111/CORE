---
name: infrastructure-access
description: (get-infrastructure-pointers) - Konkrete LISP-Methoden für den Zugriff auf VPS, PostgreSQL, ChromaDB und Kong.
disable-model-invocation: true
---

# Infrastructure Access

(defsystem INFRASTRUCTURE-POINTERS
  :vps-host "187.77.68.250"
  
  :ssh-command 
  "ssh -o ConnectTimeout=15 -o BatchMode=yes -i /home/mth/.ssh/id_ed25519_hostinger root@187.77.68.250"
  
  :databases 
  '((:postgresql 
     :container "mtho_postgres_state"
     :query-template "docker exec mtho_postgres_state psql -U atlas_admin -d atlas_state -c '~A'")
    (:chromadb 
     :container "chroma-uvmy-chromadb-1"
     :port 32779
     :heartbeat "curl -s http://187.77.68.250:32779/api/v2/heartbeat"))
  
  :kong-gateway 
  '((:proxy-port 32776)
    (:admin-port 32777))
  
  :mcp-sensors 
  '(:user-omega-state-mcp
    (query_operational_semantic query_canon_semantic)))

(defun verify-infrastructure-state ()
  (run-shell-command "python -m src.scripts.verify_vps_stack"))
