import React, { useState, useRef, useCallback, useEffect } from "react";
import { motion, AnimatePresence } from "motion/react";
import {
  Activity,
  Mic,
  MicOff,
  Loader2,
  X,
  Copy,
  Check,
  Trash2,
} from "lucide-react";

type StatusData = {
  system?: string;
  event_bus?: { running?: boolean; hass_configured?: boolean };
  agent_pool?: { active?: boolean };
  sync_relay?: { enabled?: boolean; port?: number };
};

type ChatMode = "live" | "deep";

type Props = {
  isOpen: boolean;
  onClose: () => void;
  apiBase: string;
  chatMode?: ChatMode;
};

export default function HealthBoard({ isOpen, onClose, apiBase, chatMode }: Props) {
  const [status, setStatus] = useState<StatusData | null>(null);
  const [statusError, setStatusError] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [isTranscribing, setIsTranscribing] = useState(false);
  const [transcript, setTranscript] = useState<string[]>([]);
  const [statusMsg, setStatusMsg] = useState("Bereit — Klick auf Mikrofon zum Aufnehmen");
  const [copied, setCopied] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);

  const fetchStatus = useCallback(async () => {
    try {
      const r = await fetch(`${apiBase}/status`, { signal: AbortSignal.timeout(4000) });
      if (!r.ok) throw new Error("HTTP " + r.status);
      const d: StatusData = await r.json();
      setStatus(d);
      setStatusError(false);
    } catch {
      setStatus(null);
      setStatusError(true);
    }
  }, [apiBase]);

  useEffect(() => {
    if (!isOpen) return;
    fetchStatus();
    const t = setInterval(fetchStatus, 5000);
    return () => clearInterval(t);
  }, [isOpen, fetchStatus]);

  const startRecording = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream, { mimeType: "audio/webm" });
      chunksRef.current = [];

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data);
      };

      recorder.onstop = async () => {
        stream.getTracks().forEach((t) => t.stop());
        const blob = new Blob(chunksRef.current, { type: "audio/webm" });
        if (blob.size < 1000) {
          setStatusMsg("Aufnahme zu kurz.");
          return;
        }
        setIsTranscribing(true);
        setStatusMsg("Transkribiere…");
        try {
          const form = new FormData();
          form.append("audio", blob, "dictate.webm");
          const resp = await fetch(`${apiBase}/api/dictate`, { method: "POST", body: form });
          if (!resp.ok) throw new Error("Dictate " + resp.status);
          const data = await resp.json();
          if (data.text) {
            setTranscript((prev) => [...prev, data.text]);
            setStatusMsg(`${data.duration_ms} ms — Text übernommen.`);
            try {
              await navigator.clipboard.writeText(data.text);
              setCopied(true);
              setTimeout(() => setCopied(false), 2000);
            } catch {
              /* ignore */
            }
          }
        } catch (err) {
          setStatusMsg("Fehler: " + (err instanceof Error ? err.message : String(err)));
        } finally {
          setIsTranscribing(false);
        }
      };

      mediaRecorderRef.current = recorder;
      recorder.start(250);
      setIsRecording(true);
      setStatusMsg("Aufnahme läuft… Klick zum Stoppen.");
    } catch (err) {
      setStatusMsg("Mikrofon verweigert: " + (err instanceof Error ? err.message : String(err)));
    }
  }, [apiBase]);

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current?.state === "recording") {
      mediaRecorderRef.current.stop();
    }
    setIsRecording(false);
  }, []);

  const toggleRecording = useCallback(() => {
    if (isTranscribing) return;
    if (isRecording) stopRecording();
    else startRecording();
  }, [isRecording, isTranscribing, startRecording, stopRecording]);

  const clearTranscript = useCallback(() => {
    setTranscript([]);
    setStatusMsg("Bereit — Klick auf Mikrofon zum Aufnehmen");
  }, []);

  const copyAll = useCallback(async () => {
    const text = transcript.join("\n");
    if (!text) return;
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      /* ignore */
    }
  }, [transcript]);

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm"
        onClick={onClose}
      >
        <motion.div
          initial={{ scale: 0.95, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.95, opacity: 0 }}
          transition={{ type: "spring", damping: 25, stiffness: 300 }}
          className="w-full max-w-2xl max-h-[85vh] flex flex-col bg-[#1A1A1A] border border-[#333] rounded-xl shadow-2xl overflow-hidden"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="flex-none flex items-center justify-between px-5 py-3 border-b border-[#333] bg-[#0A0A0A]">
            <div className="flex items-center gap-3">
              <Activity size={18} className="text-[#FFB300]" />
              <h2 className="text-sm font-mono font-bold text-[#E0E0E0] uppercase tracking-wider">
                Health Board — Aufnahme
              </h2>
            </div>
            <button
              onClick={onClose}
              className="p-2 rounded-lg text-[#666] hover:text-[#E0E0E0] hover:bg-[#333] transition-colors"
              title="Schließen"
            >
              <X size={18} />
            </button>
          </div>

          {/* Backend-Status */}
          <div className="flex-none flex flex-wrap gap-4 px-5 py-3 bg-[#111] border-b border-[#222] text-xs">
            <div className="flex items-center gap-2">
              <span className="text-[#555]">API</span>
              <span
                className={
                  statusError ? "text-[#F44336]" : status ? "text-[#4CAF50]" : "text-[#666]"
                }
              >
                {statusError ? "OFFLINE" : status ? "OK" : "…"}
              </span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-[#555]">Event-Bus</span>
              <span
                className={
                  status?.event_bus?.running ? "text-[#4CAF50]" : "text-[#666]"
                }
              >
                {status?.event_bus?.running ? "aktiv" : "—"}
              </span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-[#555]">Agent-Pool</span>
              <span
                className={
                  status?.agent_pool?.active ? "text-[#4CAF50]" : "text-[#666]"
                }
              >
                {status?.agent_pool?.active ? "aktiv" : "—"}
              </span>
            </div>
            {chatMode != null && (
              <div className="flex items-center gap-2">
                <span className="text-[#555]">Cockpit-Modus</span>
                <span
                  className={
                    chatMode === "live" ? "text-[#4CAF50]" : "text-[#FFB300]"
                  }
                >
                  {chatMode === "live" ? "LIVE (Flash)" : "DEEP (Pro)"}
                </span>
              </div>
            )}
            <div className="flex items-center gap-2">
              <span className="text-[#555]">Sync-Relay</span>
              <span
                className={
                  status?.sync_relay?.enabled ? "text-[#4CAF50]" : "text-[#666]"
                }
              >
                {status?.sync_relay?.enabled ? `Port ${status?.sync_relay?.port ?? 8049}` : "—"}
              </span>
            </div>
          </div>

          {/* Kennzeichen: Gedanken vs. Antwort (Cursor / Pipeline) */}
          <div className="flex-none px-5 py-2.5 bg-[#0D0D0D] border-b border-[#222] text-[10px] font-mono text-[#888] leading-relaxed">
            <span className="text-[#FFB300] font-bold uppercase tracking-wider mr-2">
              Kennzeichen
            </span>
            <span className="text-[#666]">Gedanken:</span>{" "}
            <code className="text-[#8BC34A]">{"<<<GEDANKEN>>>"}</code>
            …<code className="text-[#8BC34A]">{"<<</GEDANKEN>>>"}</code>
            <span className="text-[#444] mx-2">|</span>
            <span className="text-[#666]">Direktive:</span>{" "}
            <code className="text-[#64B5F6]">{"<<<ANTWORT>>>"}</code>
            …<code className="text-[#64B5F6]">{"<<</ANTWORT>>>"}</code>
            <span className="text-[#444] mx-2">|</span>
            <span className="text-[#555]">Kurz [G] / [A]</span>
          </div>

          {/* Aufnahme-Bereich */}
          <div className="flex-1 flex flex-col min-h-0 p-5 gap-4">
            <div className="flex-1 min-h-[140px] bg-[#111] border border-[#222] rounded-lg p-4 overflow-y-auto font-mono text-sm text-[#ddd] leading-relaxed whitespace-pre-wrap">
              {transcript.length === 0 ? (
                <span className="text-[#444]">
                  Transkript erscheint hier. Gedanken und Direktiven mit den Kennzeichen trennen.
                </span>
              ) : (
                transcript.map((line, i) => (
                  <div key={i} className="mb-2 last:mb-0">
                    {line}
                  </div>
                ))
              )}
            </div>

            <div className="flex-none flex items-center gap-3 flex-wrap">
              <button
                type="button"
                onClick={toggleRecording}
                disabled={isTranscribing}
                className={`flex items-center justify-center w-14 h-14 rounded-full border-2 transition-all shrink-0
                  ${
                    isRecording
                      ? "bg-red-600 border-red-500 text-white animate-pulse"
                      : isTranscribing
                        ? "bg-[#333] border-[#FFB300] text-[#FFB300] cursor-wait"
                        : "bg-[#222] border-[#444] text-[#A0A0A0] hover:border-[#FFB300] hover:text-[#FFB300]"
                  }`}
                title={isRecording ? "Aufnahme stoppen" : "Aufnahme starten (Diktat)"}
              >
                {isTranscribing ? (
                  <Loader2 size={24} className="animate-spin" />
                ) : isRecording ? (
                  <MicOff size={24} />
                ) : (
                  <Mic size={24} />
                )}
              </button>
              <span className="flex-1 min-w-0 text-xs text-[#666] font-mono">
                {statusMsg}
              </span>
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={copyAll}
                  disabled={transcript.length === 0}
                  className="p-2 rounded-lg border border-[#333] text-[#888] hover:text-[#FFB300] hover:border-[#FFB300] disabled:opacity-40 disabled:cursor-not-allowed transition-colors flex items-center gap-1"
                  title="Alles kopieren"
                >
                  {copied ? <Check size={14} /> : <Copy size={14} />}
                  <span className="text-[10px] uppercase">Kopieren</span>
                </button>
                <button
                  type="button"
                  onClick={clearTranscript}
                  className="p-2 rounded-lg border border-[#333] text-[#888] hover:text-[#F44336] hover:border-[#F44336] transition-colors flex items-center gap-1"
                  title="Transkript leeren"
                >
                  <Trash2 size={14} />
                  <span className="text-[10px] uppercase">Leeren</span>
                </button>
              </div>
            </div>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}
