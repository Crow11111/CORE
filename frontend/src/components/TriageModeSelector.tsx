import React, { useState, useEffect } from "react";
import { Cpu, ShieldAlert, Zap } from "lucide-react";

type TriageMode = "NORMAL" | "MAXIMAL_LOKAL" | "OPTIMAL";

interface Props {
  apiBase: string;
}

export default function TriageModeSelector({ apiBase }: Props) {
  const [currentMode, setCurrentMode] = useState<TriageMode>("NORMAL");
  const [isChanging, setIsChanging] = useState(false);

  // Der Token wird aus der .env (VITE_RING0_TOKEN) geladen.
  // Falls nicht vorhanden, Fallback auf leeren String (wird vom Backend abgelehnt).
  const ring0Token = import.meta.env.VITE_RING0_TOKEN || "";

  useEffect(() => {
    let alive = true;
    const fetchMode = async () => {
      try {
        const r = await fetch(`${apiBase}/api/v1/system/triage_mode`);
        if (r.ok) {
          const data = await r.json();
          if (alive) setCurrentMode(data.mode as TriageMode);
        }
      } catch (err) {
        console.error("Failed to fetch triage mode", err);
      }
    };
    fetchMode();
    return () => { alive = false; };
  }, [apiBase]);

  const handleModeChange = async (mode: TriageMode) => {
    if (mode === currentMode) return;
    setIsChanging(true);
    try {
      const response = await fetch(`${apiBase}/api/v1/system/triage_mode`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Ring0-Token": ring0Token,
        },
        body: JSON.stringify({ mode }),
      });
      if (response.ok) {
        setCurrentMode(mode);
      } else {
        const errData = await response.json();
        console.error("Mode change rejected:", errData.detail);
      }
    } catch (err) {
      console.error("Failed to change triage mode", err);
    } finally {
      setIsChanging(false);
    }
  };

  const modes: { id: TriageMode; label: string; icon: React.ReactNode; colorClass: string; activeClass: string }[] = [
    { 
      id: "NORMAL", 
      label: "NORMAL", 
      icon: <ShieldAlert size={12} />, 
      colorClass: "text-blue-400 border-blue-900/30",
      activeClass: "bg-blue-500/10 border-blue-500/50 text-blue-400"
    },
    { 
      id: "MAXIMAL_LOKAL", 
      label: "LOKAL", 
      icon: <Cpu size={12} />, 
      colorClass: "text-green-400 border-green-900/30",
      activeClass: "bg-green-500/10 border-green-500/50 text-green-400"
    },
    { 
      id: "OPTIMAL", 
      label: "OPTIMAL", 
      icon: <Zap size={12} />, 
      colorClass: "text-amber-400 border-amber-900/30",
      activeClass: "bg-amber-500/10 border-amber-500/50 text-amber-400"
    },
  ];

  return (
    <div className="flex items-center gap-1.5 px-2 py-1 bg-[#0A0A0A] rounded-lg border border-[#222] shadow-inner">
      <span className="text-[9px] font-mono text-[#555] uppercase mr-1">Triage</span>
      <div className="flex gap-1">
        {modes.map((m) => (
          <button
            key={m.id}
            disabled={isChanging}
            onClick={() => handleModeChange(m.id)}
            title={`Switch to ${m.id} mode`}
            className={`px-2 py-0.5 rounded border text-[9px] font-mono flex items-center gap-1.5 transition-all duration-200 ${
              currentMode === m.id
                ? m.activeClass
                : `bg-transparent border-transparent text-[#666] hover:text-[#999] hover:bg-[#151515]`
            } ${isChanging ? "opacity-50 cursor-wait" : ""}`}
          >
            {m.icon}
            {m.label}
          </button>
        ))}
      </div>
    </div>
  );
}
