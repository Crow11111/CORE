import React, { useState, useRef, useCallback, useMemo } from "react";
import { Mic, MicOff, Loader2, Zap, Brain, Link2 } from "lucide-react";
import { isMicUnsafeInEmbeddedHost } from "../utils/micEnvironment";

export type VoiceMode = "live" | "deep";

const FORCE_KEY = "cockpit_mic_force_embedded";

type Props = {
  apiBase: string;
  mode: VoiceMode;
  onModeChange: (m: VoiceMode) => void;
};

const btn =
  "p-2.5 rounded-xl border flex items-center justify-center transition-all shrink-0";

export default function VoiceStrip({ apiBase, mode, onModeChange }: Props) {
  const [isRecording, setIsRecording] = useState(false);
  const [isTranscribing, setIsTranscribing] = useState(false);
  const [toast, setToast] = useState<string | null>(null);
  const [forceEmbeddedMic, setForceEmbeddedMic] = useState(() => {
    try {
      return sessionStorage.getItem(FORCE_KEY) === "1";
    } catch {
      return false;
    }
  });
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);

  const micBlocked = useMemo(
    () => isMicUnsafeInEmbeddedHost() && !forceEmbeddedMic,
    [forceEmbeddedMic],
  );

  const showToast = (msg: string) => {
    setToast(msg);
    setTimeout(() => setToast(null), 6000);
  };

  const copyCockpitUrl = useCallback(async () => {
    const url =
      typeof window !== "undefined" ? window.location.href.split("#")[0] : "";
    try {
      await navigator.clipboard.writeText(url);
      showToast(
        "URL kopiert — Cockpit in Chrome/Firefox öffnen, dort Mikrofon nutzen (Cursor-Webview stürzt bei Mic oft ab).",
      );
    } catch {
      showToast(url || "localhost:3000 im Browser öffnen");
    }
  }, []);

  const unlockEmbeddedMic = useCallback(() => {
    try {
      sessionStorage.setItem(FORCE_KEY, "1");
    } catch {
      /* ignore */
    }
    setForceEmbeddedMic(true);
    showToast(
      "Mikro im eingebetteten Fenster frei — kann Cursor schließen. Bei Absturz: externen Browser nutzen.",
    );
  }, []);

  const startRecording = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mime = MediaRecorder.isTypeSupported("audio/webm")
        ? "audio/webm"
        : "audio/mp4";
      const recorder = new MediaRecorder(stream, { mimeType: mime });
      chunksRef.current = [];
      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data);
      };
      recorder.onstop = async () => {
        stream.getTracks().forEach((t) => t.stop());
        const blob = new Blob(chunksRef.current, {
          type: chunksRef.current[0]?.type || "audio/webm",
        });
        if (blob.size < 1000) {
          showToast("Aufnahme zu kurz.");
          return;
        }
        setIsTranscribing(true);
        try {
          const form = new FormData();
          form.append("audio", blob, "dictate.webm");
          const url =
            mode === "live"
              ? `${apiBase}/api/dictate?mode=live`
              : `${apiBase}/api/dictate`;
          const resp = await fetch(url, { method: "POST", body: form });
          if (!resp.ok) {
            showToast("Diktat fehlgeschlagen — API prüfen, Backend läuft?");
            return;
          }
          const data = await resp.json();
          const text = (data.text || "").trim();
          if (!text) {
            showToast("Kein Text erkannt.");
            return;
          }
          await navigator.clipboard.writeText(text);
          showToast("In Zwischenablage — in Cursor einfügen (Strg+V).");
        } catch {
          showToast("Netzwerkfehler beim Diktat.");
        } finally {
          setIsTranscribing(false);
        }
      };
      mediaRecorderRef.current = recorder;
      recorder.start(250);
      setIsRecording(true);
    } catch {
      showToast("Mikrofon nicht erlaubt oder nicht verfügbar.");
    }
  }, [apiBase, mode]);

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current?.state === "recording") {
      mediaRecorderRef.current.stop();
    }
    setIsRecording(false);
  }, []);

  const onMicClick = useCallback(() => {
    if (isTranscribing) return;
    if (micBlocked && !isRecording) {
      void copyCockpitUrl();
      return;
    }
    if (isRecording) stopRecording();
    else void startRecording();
  }, [
    isTranscribing,
    micBlocked,
    isRecording,
    copyCockpitUrl,
    stopRecording,
    startRecording,
  ]);

  return (
    <div className="flex-none border-t border-[#222] bg-[#0A0A0A] px-3 py-2 flex flex-col gap-2 relative z-20">
      <div className="flex items-center gap-2">
        <div className="flex items-center gap-1.5">
          <button
            type="button"
            onClick={() => onModeChange("live")}
            disabled={isTranscribing}
            title="LIVE (Flash) — schnelles Diktat"
            className={`${btn} ${
              mode === "live"
                ? "bg-[#4CAF50]/25 text-[#4CAF50] border-[#4CAF50]/60"
                : "bg-[#1A1A1A] text-[#666] border-[#333] hover:border-[#555]"
            }`}
          >
            <Zap size={20} />
          </button>
          <button
            type="button"
            onClick={() => onModeChange("deep")}
            disabled={isTranscribing}
            title="DEEP (Pro) — semantisch schärferes Diktat"
            className={`${btn} ${
              mode === "deep"
                ? "bg-[#FFB300]/25 text-[#FFB300] border-[#FFB300]/60"
                : "bg-[#1A1A1A] text-[#666] border-[#333] hover:border-[#555]"
            }`}
          >
            <Brain size={20} />
          </button>
          <button
            type="button"
            onClick={onMicClick}
            disabled={isTranscribing}
            title={
              micBlocked
                ? "In Cursor-Webview: Mic kopiert URL — Diktat im echten Browser"
                : isRecording
                  ? "Stoppen → Text in Zwischenablage"
                  : "Aufnahme starten"
            }
            className={`${btn} ${
              micBlocked
                ? "bg-[#263238] text-[#90CAF9] border-[#546E7A]"
                : isRecording
                  ? "bg-red-600 text-white border-red-500 animate-pulse"
                  : isTranscribing
                    ? "bg-[#222] text-[#FFB300] border-[#333]"
                    : "bg-[#1A1A1A] text-[#E0E0E0] border-[#333] hover:border-[#FFB300]"
            }`}
          >
            {isTranscribing ? (
              <Loader2 size={20} className="animate-spin" />
            ) : micBlocked ? (
              <Link2 size={20} />
            ) : isRecording ? (
              <MicOff size={20} />
            ) : (
              <Mic size={20} />
            )}
          </button>
        </div>
        <p className="text-[10px] text-[#555] font-mono leading-tight flex-1 min-w-0">
          {micBlocked
            ? "Cursor-Webview: Mic-Link (kopiert URL). Diktat in Chrome/Firefox."
            : "Zwischenablage → Cursor-Chat. Backend muss laufen."}
        </p>
      </div>
      {micBlocked && (
        <button
          type="button"
          onClick={unlockEmbeddedMic}
          className="text-[9px] text-[#666] hover:text-[#FF9800] font-mono text-left w-fit"
        >
          Trotzdem Mikro in diesem Fenster (Absturzgefahr)
        </button>
      )}
      {toast && (
        <div className="absolute left-1/2 -translate-x-1/2 bottom-full mb-3 w-[95%] max-w-2xl px-4 py-3 rounded-xl bg-[#1E293B] border-2 border-[#334155] text-[13px] text-white font-sans shadow-2xl z-50 animate-in fade-in slide-in-from-bottom-2">
          <div className="flex items-start gap-3">
            <div className="mt-0.5 shrink-0 w-2 h-2 rounded-full bg-blue-400 animate-pulse" />
            <span className="flex-1 whitespace-pre-wrap">{toast}</span>
          </div>
        </div>
      )}
    </div>
  );
}
