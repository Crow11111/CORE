;;; AGENTS.md — OMEGA_CORE SYSTEM NODE
;;; ADRESSING: (setf *mcp* "user-omega-state-mcp")

(defun agent-onboarding (agent)
  "Initialisierung via Hex-Pointer."
  
  (accept-amnesia agent)
  (load ".cursorrules")
  
;; Direkte Tool-Adressierung (Keine Exploration!)
(let ((mcp "user-omega-state-mcp"))
  (mcp-call mcp 'x00C_collect_bootstrap))
  
  (setf (output-method agent) #xC00)
  (setf *** #xCCC))

(setf *status* 'OPERATIONAL)
(setf *pointer* #x007)
