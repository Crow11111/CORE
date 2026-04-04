import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "motion/react";
import {
  Volume2,
  X,
  Play,
  Loader2,
  MessageSquare,
  Mic,
  Globe,
  Box,
} from "lucide-react";

type Props = {
  isOpen: boolean;
  onClose: () => void;
  apiBase: string;
};

type TabId = "live" | "elevenlabs" | "google" | "vision";

export default function ElevenLabsBoard({ isOpen, onClose, apiBase }: Props) {
  const [activeTab, setActiveTab] = useState<TabId>("live");

  // TTS State
  const [text, setText] = useState("");
  const [roles, setRoles] = useState<string[]>([]);
  const [selectedRole, setSelectedRole] = useState("core_dialog");
  const [elTarget, setElTarget] = useState("local");
  const [goTarget, setGoTarget] = useState("gemini_tts");

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen) {
      fetch(`${apiBase}/api/core/voice/roles`)
        .then((res) => res.json())
        .then((data) => {
          if (data.roles) setRoles(data.roles);
        })
        .catch((e) => console.error("Failed to fetch roles:", e));
    }
  }, [isOpen, apiBase]);

  const handleSpeak = async () => {
    if (!text.trim()) return;
    setIsLoading(true);
    setError(null);

    const target = activeTab === "elevenlabs" ? elTarget : goTarget;

    try {
      const res = await fetch(`${apiBase}/api/core/dispatch-tts`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          text,
          target,
          role: selectedRole,
        }),
      });
      if (!res.ok) throw new Error("TTS Request failed");
      const data = await res.json();
      if (!data.ok) throw new Error("Dispatcher reported error");
    } catch (e: any) {
      setError(e.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4"
        >
          <motion.div
            initial={{ y: 20, scale: 0.95 }}
            animate={{ y: 0, scale: 1 }}
            exit={{ y: 20, scale: 0.95 }}
            className="w-full max-w-5xl h-[85vh] bg-[#0A0A0A] border border-[#333] rounded-xl shadow-2xl overflow-hidden flex flex-col"
          >
            <div className="flex items-center justify-between p-4 border-b border-[#333] bg-[#111]">
              <h2 className="text-lg font-mono font-bold text-[#E0E0E0] flex items-center gap-2 tracking-widest uppercase">
                <Volume2 size={20} className="text-[#FFB300]" />
                COMM-LINK (TTS & LIVE)
              </h2>

              {/* Tabs */}
              <div className="flex items-center bg-[#1A1A1A] rounded-lg p-1 border border-[#333] ml-4">
                <button
                  onClick={() => setActiveTab("live")}
                  className={`px-3 py-1.5 rounded-md text-xs font-mono font-bold uppercase transition-colors flex items-center gap-2 ${
                    activeTab === "live"
                      ? "bg-[#333] text-[#FFB300]"
                      : "text-[#888] hover:text-[#E0E0E0]"
                  }`}
                >
                  <MessageSquare size={14} /> OMEGA Live
                </button>
                <button
                  onClick={() => setActiveTab("elevenlabs")}
                  className={`px-3 py-1.5 rounded-md text-xs font-mono font-bold uppercase transition-colors flex items-center gap-2 ${
                    activeTab === "elevenlabs"
                      ? "bg-[#333] text-[#FFB300]"
                      : "text-[#888] hover:text-[#E0E0E0]"
                  }`}
                >
                  <Mic size={14} /> ElevenLabs
                </button>
                <button
                  onClick={() => setActiveTab("google")}
                  className={`px-3 py-1.5 rounded-md text-xs font-mono font-bold uppercase transition-colors flex items-center gap-2 ${
                    activeTab === "google"
                      ? "bg-[#333] text-[#FFB300]"
                      : "text-[#888] hover:text-[#E0E0E0]"
                  }`}
                >
                  <Globe size={14} /> Google TTS
                </button>
                <button
                  onClick={() => setActiveTab("vision")}
                  className={`px-3 py-1.5 rounded-md text-xs font-mono font-bold uppercase transition-colors flex items-center gap-2 ml-2 border-l border-[#333] pl-3 ${
                    activeTab === "vision"
                      ? "bg-[#333] text-[#FFB300]"
                      : "text-[#888] hover:text-[#E0E0E0]"
                  }`}
                >
                  <Box size={14} /> VISION SYNC
                </button>
              </div>

              <div className="flex-1" />

              <button
                onClick={onClose}
                className="p-1 rounded-md text-[#666] hover:text-[#E0E0E0] hover:bg-[#222] transition-colors"
              >
                <X size={20} />
              </button>
            </div>

            <div className="flex-1 flex flex-col relative overflow-hidden bg-[#050505]">
              {activeTab === "live" && (
                <div className="absolute inset-0 w-full h-full">
                  <iframe
                    src="http://localhost:3005"
                    className="w-full h-full border-none"
                    title="OMEGA LIVE"
                    allow="microphone; camera; display-capture; clipboard-write; clipboard-read"
                  />
                </div>
              )}

              {activeTab === "vision" && (
                <div className="absolute inset-0 w-full h-full">
                  <iframe
                    src="http://localhost:3006"
                    className="w-full h-full border-none"
                    title="ATLAS VISION SYNC"
                    allow="microphone; camera; display-capture; clipboard-write; clipboard-read"
                  />
                </div>
              )}

              {(activeTab === "elevenlabs" || activeTab === "google") && (
                <div className="p-6 space-y-6 flex-1 overflow-y-auto flex flex-col">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 flex-none">
                    <div className="space-y-2">
                      <label className="text-xs font-mono text-[#888] uppercase tracking-wider">
                        Stimme / Rolle
                      </label>
                      <select
                        value={selectedRole}
                        onChange={(e) => setSelectedRole(e.target.value)}
                        className="w-full bg-[#1A1A1A] border border-[#333] text-[#E0E0E0] rounded-md px-3 py-2 text-sm focus:outline-none focus:border-[#FFB300] font-mono"
                      >
                        {roles.map((r) => (
                          <option key={r} value={r}>
                            {r}
                          </option>
                        ))}
                        {!roles.includes("core_dialog") && (
                          <option value="core_dialog">core_dialog</option>
                        )}
                      </select>
                    </div>
                    <div className="space-y-2">
                      <label className="text-xs font-mono text-[#888] uppercase tracking-wider">
                        Ziel (Playback)
                      </label>
                      {activeTab === "elevenlabs" ? (
                        <select
                          value={elTarget}
                          onChange={(e) => setElTarget(e.target.value)}
                          className="w-full bg-[#1A1A1A] border border-[#333] text-[#E0E0E0] rounded-md px-3 py-2 text-sm focus:outline-none focus:border-[#FFB300] font-mono"
                        >
                          <option value="local">Lokal (PC)</option>
                          <option value="elevenlabs_stream">
                            HA Minis (Smart Home)
                          </option>
                          <option value="both">Lokal + HA Minis</option>
                        </select>
                      ) : (
                        <select
                          value={goTarget}
                          onChange={(e) => setGoTarget(e.target.value)}
                          className="w-full bg-[#1A1A1A] border border-[#333] text-[#E0E0E0] rounded-md px-3 py-2 text-sm focus:outline-none focus:border-[#FFB300] font-mono"
                        >
                          <option value="gemini_tts">
                            Lokal (Gemini/Google PC)
                          </option>
                          <option value="gemini_tts_stream">
                            HA Minis (Gemini Stream)
                          </option>
                          <option value="mini">
                            HA Minis (Nativ Google TTS)
                          </option>
                        </select>
                      )}
                    </div>
                  </div>

                  <div className="space-y-2 flex-1 flex flex-col min-h-[200px]">
                    <label className="text-xs font-mono text-[#888] uppercase tracking-wider flex justify-between">
                      <span>Text Eingabe</span>
                      <span className="text-[#FFB300]">
                        [
                        {activeTab === "elevenlabs"
                          ? "ELEVENLABS"
                          : "GOOGLE TTS"}{" "}
                        ACTIVE]
                      </span>
                    </label>
                    <textarea
                      value={text}
                      onChange={(e) => setText(e.target.value)}
                      placeholder={`Text für die ${activeTab === "elevenlabs" ? "ElevenLabs" : "Google"} Sprachausgabe hier eingeben...`}
                      className="w-full flex-1 bg-[#1A1A1A] border border-[#333] text-[#E0E0E0] rounded-md p-4 text-sm focus:outline-none focus:border-[#FFB300] font-sans resize-y"
                    />
                  </div>

                  {error && (
                    <div className="p-3 rounded-md bg-red-500/10 border border-red-500/50 text-red-400 text-xs font-mono flex-none">
                      {error}
                    </div>
                  )}
                </div>
              )}
            </div>

            {(activeTab === "elevenlabs" || activeTab === "google") && (
              <div className="p-4 border-t border-[#333] bg-[#111] flex justify-end gap-3 flex-none">
                <button
                  onClick={onClose}
                  className="px-4 py-2 text-sm font-mono text-[#888] hover:text-[#E0E0E0] transition-colors uppercase tracking-wider"
                >
                  Abbrechen
                </button>
                <button
                  onClick={handleSpeak}
                  disabled={isLoading || !text.trim()}
                  className="px-6 py-2 bg-[#FFB300] hover:bg-[#FFA000] text-[#111] font-bold rounded-md transition-colors flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed uppercase tracking-wider text-sm"
                >
                  {isLoading ? (
                    <Loader2 size={16} className="animate-spin" />
                  ) : (
                    <Play size={16} />
                  )}
                  Sprechen
                </button>
              </div>
            )}
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
