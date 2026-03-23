import React, { useState, useRef, useCallback } from "react";
import { Mic, MicOff, Zap, Brain, Loader2 } from "lucide-react";

/**
 * CORE COMPACT COCKPIT
 * Team: UI-PURIST
 * Vektor: 2210 | Delta: 0.049
 */

type Mode = "live" | "deep";

export default function App() {
  const [mode, setMode] = useState<Mode>("live");
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [status, setStatus] = useState<string | null>(null);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);

  const apiBase = (
    import.meta.env.VITE_CORE_API_URL || "http://localhost:8000"
  ).replace(/\/$/, "");

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream, {
        mimeType: MediaRecorder.isTypeSupported("audio/webm")
          ? "audio/webm"
          : "audio/mp4",
      });
      chunksRef.current = [];
      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data);
      };
      recorder.onstop = async () => {
        stream.getTracks().forEach((t) => t.stop());
        const blob = new Blob(chunksRef.current, { type: "audio/webm" });
        if (blob.size < 1000) {
          setStatus("TOO SHORT");
          setTimeout(() => setStatus(null), 2000);
          return;
        }
        await processAudio(blob);
      };
      mediaRecorderRef.current = recorder;
      recorder.start();
      setIsRecording(true);
      setStatus("RECORDING...");
    } catch (err) {
      console.error(err);
      setStatus("MIC ERROR");
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current?.state === "recording") {
      mediaRecorderRef.current.stop();
    }
    setIsRecording(false);
  };

  const processAudio = async (blob: Blob) => {
    setIsProcessing(true);
    setStatus("PROCESSING...");
    try {
      const form = new FormData();
      form.append("audio", blob, "input.webm");
      const url = `${apiBase}/api/dictate?mode=${mode}`;
      const resp = await fetch(url, { method: "POST", body: form });
      if (!resp.ok) throw new Error("API FAIL");
      const data = await resp.json();
      const text = data.text?.trim();
      if (text) {
        await navigator.clipboard.writeText(text);
        setStatus("COPIED!");
      } else {
        setStatus("NO TEXT");
      }
    } catch (err) {
      console.error(err);
      setStatus("API ERROR");
    } finally {
      setIsProcessing(false);
      setTimeout(() => setStatus(null), 3000);
    }
  };

  return (
    <div className="flex flex-col h-full w-full items-center justify-center p-4 bg-black select-none overflow-hidden">
      {/* Brutalist Header */}
      <div className="mb-12 text-center">
        <h1 className="text-4xl font-black tracking-tighter border-b-4 border-white px-2 inline-block mb-1">
          CORE COMPACT
        </h1>
        <div className="text-[10px] font-mono tracking-widest text-[#444] uppercase">
          Vektor: 2210 | \Lambda: 0.049 | System: OMEGA
        </div>
      </div>

      <div className="flex flex-col items-center gap-10 w-full max-w-sm">
        {/* Mode Selectors */}
        <div className="flex gap-4 w-full justify-center">
          <button
            onClick={() => setMode("live")}
            className={`flex items-center gap-2 px-6 py-3 border-4 font-black transition-all ${
              mode === "live"
                ? "bg-white text-black border-white shadow-none translate-x-1 translate-y-1"
                : "bg-black text-white border-white shadow-[4px_4px_0px_white] hover:shadow-[6px_6px_0px_white] hover:-translate-x-1 hover:-translate-y-1"
            }`}
          >
            <Zap size={20} className={mode === "live" ? "fill-black" : "fill-white"} />
            LIVE
          </button>
          <button
            onClick={() => setMode("deep")}
            className={`flex items-center gap-2 px-6 py-3 border-4 font-black transition-all ${
              mode === "deep"
                ? "bg-white text-black border-white shadow-none translate-x-1 translate-y-1"
                : "bg-black text-white border-white shadow-[4px_4px_0px_white] hover:shadow-[6px_6px_0px_white] hover:-translate-x-1 hover:-translate-y-1"
            }`}
          >
            <Brain size={20} className={mode === "deep" ? "fill-black" : "fill-white"} />
            DEEP
          </button>
        </div>

        {/* Big Record Button */}
        <div className="relative">
          <button
            onClick={isRecording ? stopRecording : startRecording}
            disabled={isProcessing}
            className={`w-48 h-48 border-8 flex items-center justify-center transition-all ${
              isRecording
                ? "bg-red-600 border-white animate-pulse shadow-none translate-x-2 translate-y-2"
                : isProcessing
                ? "bg-gray-800 border-gray-600 cursor-not-allowed"
                : "bg-black border-white shadow-[8px_8px_0px_white] hover:shadow-[12px_12px_0px_white] hover:-translate-x-2 hover:-translate-y-2"
            }`}
          >
            {isProcessing ? (
              <Loader2 size={64} className="animate-spin text-white" />
            ) : isRecording ? (
              <MicOff size={64} className="text-white" />
            ) : (
              <Mic size={64} className="text-white" />
            )}
          </button>

          {/* Status Label (Floating) */}
          {status && (
            <div className="absolute -bottom-12 left-1/2 -translate-x-1/2 whitespace-nowrap bg-white text-black font-black px-2 py-1 text-xs uppercase border-2 border-black">
              {status}
            </div>
          )}
        </div>
      </div>

      {/* Footer Info */}
      <div className="mt-16 border-t-2 border-[#222] pt-2 w-full max-w-xs text-center">
        <div className="text-[8px] font-mono text-[#222]">
          UI-PURIST-COCKPIT // v1.0.0-DELTA
        </div>
      </div>
    </div>
  );
}
