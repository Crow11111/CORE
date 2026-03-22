import React, { useState, useRef, useCallback } from "react";
import { Send, Terminal, Mic, MicOff, Loader2, Zap, Brain } from "lucide-react";

export type ChatMode = "live" | "deep";

type Props = {
  onExecute: (cmd: string) => void;
  isProcessing: boolean;
  mode: ChatMode;
  onModeChange: (mode: ChatMode) => void;
  /** Nach Stopp + Transkription: Text in Zwischenablage + direkt an Chat (ohne Mini-Feld) */
  onVoiceResult?: (text: string) => void;
};

export default function CommandConsole({
  onExecute,
  isProcessing,
  mode,
  onModeChange,
  onVoiceResult,
}: Props) {
  const [input, setInput] = useState("");
  const [isRecording, setIsRecording] = useState(false);
  const [isTranscribing, setIsTranscribing] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);

  const apiBase = (
    import.meta.env.VITE_CORE_API_URL || "http://localhost:8000"
  ).replace(/\/$/, "");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim() && !isProcessing) {
      onExecute(input);
      setInput("");
    }
  };

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

        if (blob.size < 1000) return;

        setIsTranscribing(true);
        try {
          const form = new FormData();
          form.append("audio", blob, "dictate.webm");
          const dictateMode = mode === "live" ? "live" : undefined; // DEEP = Pro (default)
          const url = dictateMode ? `${apiBase}/api/dictate?mode=live` : `${apiBase}/api/dictate`;
          const resp = await fetch(url, {
            method: "POST",
            body: form,
          });

          if (resp.ok) {
            const data = await resp.json();
            const text = (data.text || "").trim();
            if (!text) return;
            if (onVoiceResult) {
              try {
                await navigator.clipboard.writeText(text);
              } catch {
                /* Clipboard optional */
              }
              onVoiceResult(text);
            } else {
              setInput((prev) => (prev ? prev + " " + text : text));
            }
          }
        } catch (err) {
          console.error("[Dictate] Fehler:", err);
        } finally {
          setIsTranscribing(false);
        }
      };

      mediaRecorderRef.current = recorder;
      recorder.start(250);
      setIsRecording(true);
    } catch (err) {
      console.error("[Mic] Zugriff verweigert:", err);
    }
  }, [apiBase, mode, onVoiceResult]);

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current?.state === "recording") {
      mediaRecorderRef.current.stop();
    }
    setIsRecording(false);
  }, []);

  const toggleRecording = useCallback(() => {
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  }, [isRecording, startRecording, stopRecording]);

  return (
    <div className="w-full bg-[#1A1A1A] border-t border-[#333] p-4 relative z-10 shadow-[0_-10px_40px_rgba(0,0,0,0.49)]">
      <div className="max-w-5xl mx-auto flex flex-col gap-3">
        {/* LIVE (Flash) / DEEP (Pro) Toggle */}
        <div className="flex items-center gap-2">
          <span className="text-[10px] font-mono uppercase tracking-wider text-[#666] mr-2">Modus</span>
          <button
            type="button"
            onClick={() => onModeChange("live")}
            className={`flex items-center gap-2 px-3 py-1.5 rounded-lg border font-mono text-xs uppercase transition-all
              ${mode === "live" ? "bg-[#4CAF50] text-[#0A0A0A] border-[#4CAF50]" : "bg-[#1A1A1A] text-[#666] border-[#333] hover:border-[#555]"}`}
            title="Schnelles Hin und Her (Flash)"
          >
            <Zap size={14} />
            LIVE (Flash)
          </button>
          <button
            type="button"
            onClick={() => onModeChange("deep")}
            className={`flex items-center gap-2 px-3 py-1.5 rounded-lg border font-mono text-xs uppercase transition-all
              ${mode === "deep" ? "bg-[#FFB300] text-[#0A0A0A] border-[#FFB300]" : "bg-[#1A1A1A] text-[#666] border-[#333] hover:border-[#555]"}`}
            title="Gedanke mit Enter abschließen, dann Antwort (Pro)"
          >
            <Brain size={14} />
            DEEP (Pro)
          </button>
        </div>

        <div className="flex items-end gap-4 relative">
          <div className="absolute left-4 top-1/2 -translate-y-1/2 text-[#555] pointer-events-none">
            <Terminal size={18} />
          </div>

          <form onSubmit={handleSubmit} className="flex-1 relative">
            <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleSubmit(e);
              }
            }}
            placeholder={
              isTranscribing
                ? "…"
                : isRecording
                  ? "●"
                  : isProcessing
                    ? "…"
                    : mode === "deep"
                      ? "Enter = senden (Pro)"
                      : "Enter / Mic → Chat"
            }
            disabled={isProcessing || isRecording}
            rows={isRecording || isTranscribing ? 1 : Math.min(8, Math.max(2, input.split("\n").length))}
            className="w-full bg-[#222] border border-[#333] rounded-xl pl-12 pr-24 py-3.5
                     text-[#E0E0E0] placeholder-[#666] focus:outline-none focus:border-[#FFB300]
                     focus:ring-1 focus:ring-[#FFB300] transition-all resize-none font-mono text-sm leading-relaxed
                     disabled:opacity-50 disabled:cursor-not-allowed"
          />

          <div className="absolute right-2 bottom-2 flex items-center gap-1">
            <button
              type="button"
              onClick={toggleRecording}
              disabled={isProcessing || isTranscribing}
              className={`p-2 rounded-lg transition-all flex items-center justify-center
                ${
                  isRecording
                    ? "bg-red-600 text-white animate-pulse"
                    : isTranscribing
                      ? "bg-[#333] text-[#FFB300]"
                      : "bg-[#333] text-[#A0A0A0] hover:bg-[#444] hover:text-[#E0E0E0]"
                }
                disabled:opacity-50`}
              title={
                isRecording ? "Aufnahme stoppen" : "Diktieren (Gemini STT)"
              }
            >
              {isTranscribing ? (
                <Loader2 size={16} className="animate-spin" />
              ) : isRecording ? (
                <MicOff size={16} />
              ) : (
                <Mic size={16} />
              )}
            </button>

            <button
              type="submit"
              disabled={!input.trim() || isProcessing}
              className="p-2 rounded-lg
                       bg-[#333] text-[#E0E0E0] hover:bg-[#FFB300] hover:text-[#121212]
                       disabled:opacity-50 disabled:hover:bg-[#333] disabled:hover:text-[#E0E0E0]
                       transition-colors flex items-center justify-center"
            >
              <Send size={16} />
            </button>
          </div>
        </form>
        </div>
      </div>
    </div>
  );
}
