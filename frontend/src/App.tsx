import React, { useState, useEffect, useRef } from "react";
import {
  Box,
  Settings,
  GitBranch,
  AlertTriangle,
  Activity,
  Volume2,
} from "lucide-react";
import HealthBoard from "./components/HealthBoard";
import ElevenLabsBoard from "./components/ElevenLabsBoard";
import LiveTicker from "./components/LiveTicker";
import ThoughtStream from "./components/ThoughtStream";
import VoiceStrip, { type VoiceMode } from "./components/VoiceStrip";
import {
  DEFAULT_TICKER_VISIBILITY,
  TICKER_CATEGORY_IDS,
  TICKER_CATEGORY_META,
  type TickerCategoryId,
} from "./cockpitTickerCategories";
import { motion, AnimatePresence } from "motion/react";
import TelemetryHUD from "./components/TelemetryHUD";
import ZVectorMonitor from "./components/ZVectorMonitor";
import ValidationBuildEngine from "./components/ValidationForge";
import { useTelemetryPolling } from "./hooks/useTelemetryPolling";

type FeedRow = {
  ts: string;
  level: string;
  msg: string;
  src?: string;
  category: TickerCategoryId;
};

export default function App() {
  const [minimalMode, setMinimalMode] = useState(false);
  const [voiceMode, setVoiceMode] = useState<VoiceMode>("live");
  const [isBuildEngineOpen, setIsBuildEngineOpen] = useState(false);
  const [isHealthBoardOpen, setIsHealthBoardOpen] = useState(false);
  const [isElevenLabsBoardOpen, setIsElevenLabsBoardOpen] = useState(false);
  const [tickerVis, setTickerVis] = useState<Record<TickerCategoryId, boolean>>(
    DEFAULT_TICKER_VISIBILITY,
  );
  const [feedLogs, setFeedLogs] = useState<FeedRow[]>([]);
  const [feedOk, setFeedOk] = useState(false);
  const [wsThoughts, setWsThoughts] = useState<string[]>([]);
  const wsRef = useRef<WebSocket | null>(null);

  const apiBase = (
    import.meta.env.VITE_CORE_API_URL || "http://localhost:8000"
  ).replace(/\/$/, "");
  const wsUrl = apiBase.replace(/^http/, "ws") + "/ws";
  const { data: telemetry, connected: telemetryConnected } =
    useTelemetryPolling({ apiBase });

  useEffect(() => {
    let alive = true;
    const pull = async () => {
      try {
        const r = await fetch(`${apiBase}/api/cockpit_feed?limit=400`, {
          signal: AbortSignal.timeout(5000),
        });
        if (!r.ok) {
          if (alive) setFeedOk(false);
          return;
        }
        const data = await r.json();
        if (!alive) return;
        const logs: FeedRow[] = (data.logs || []).map(
          (l: Record<string, unknown>) => ({
            ts: String(l.ts ?? ""),
            level: String(l.level ?? "INFO"),
            msg: String(l.msg ?? ""),
            src: l.src != null ? String(l.src) : undefined,
            category: (l.category as TickerCategoryId) || "core",
          }),
        );
        setFeedLogs(logs);
        setFeedOk(true);
      } catch {
        if (alive) setFeedOk(false);
      }
    };
    pull();
    const t = setInterval(pull, 2000);
    return () => {
      alive = false;
      clearInterval(t);
    };
  }, [apiBase]);

  useEffect(() => {
    let cancelled = false;
    let ws: WebSocket | null = null;
    let reconnectTimer: ReturnType<typeof setTimeout> | undefined;
    const connect = () => {
      if (cancelled) return;
      ws = new WebSocket(wsUrl);
      wsRef.current = ws;
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === "cockpit_thought" && data.text) {
            setWsThoughts((prev) => [...prev, String(data.text)].slice(-80));
          }
        } catch {
          /* ignore */
        }
      };
      ws.onclose = () => {
        if (!cancelled) {
          reconnectTimer = setTimeout(connect, 5000);
        }
      };
    };
    connect();
    return () => {
      cancelled = true;
      if (reconnectTimer) clearTimeout(reconnectTimer);
      ws?.close();
      wsRef.current = null;
    };
  }, [wsUrl]);

  const toggleTickerCat = (id: TickerCategoryId) => {
    setTickerVis((v) => ({ ...v, [id]: !v[id] }));
  };

  return (
    <div className="flex flex-col h-screen bg-[#050505] text-[#E0E0E0] font-sans overflow-hidden">
      <div
        className={`flex-1 flex flex-col mx-auto w-full border-x border-[#222] shadow-[0_0_50px_rgba(0,0,0,0.8)] overflow-hidden ${minimalMode ? "max-w-md" : ""}`}
      >
        <header className="flex-none bg-[#0A0A0A] border-b border-[#333] px-4 py-2 flex flex-wrap items-center justify-between gap-2 z-20 shadow-[0_4px_20px_rgba(0,0,0,0.49)]">
          <div className="flex items-center gap-3">
            <Box size={20} className="text-[#FFB300]" />
            {!minimalMode && (
              <h1 className="text-sm font-mono tracking-[0.2em] uppercase font-bold text-[#E0E0E0]">
                CORE Cockpit
              </h1>
            )}
            <button
              onClick={() => setMinimalMode(!minimalMode)}
              className="px-2 py-0.5 rounded border border-orange-500/40 text-orange-500 font-mono text-[9px] hover:bg-orange-500/10"
            >
              {minimalMode ? "FULL" : "MINIMAL"}
            </button>
            <button
              onClick={() => setIsElevenLabsBoardOpen(true)}
              className="p-1.5 rounded-lg border border-[#333] bg-[#1A1A1A] text-[#A0A0A0] hover:text-[#E0E0E0] hover:border-[#666] transition-all flex items-center gap-2 ml-2"
              title="TTS Studio (ElevenLabs / Gemini Live)"
            >
              <Volume2 size={16} className="text-[#FFB300]" />
            </button>
          </div>

          {!minimalMode && (
            <>
              <div className="flex items-center gap-2 flex-wrap">
                <TelemetryHUD data={telemetry} connected={telemetryConnected} />
                <ZVectorMonitor
                  data={telemetry}
                  connected={telemetryConnected}
                />
              </div>

              <div className="flex items-center gap-2">
                <button
                  onClick={() => setIsHealthBoardOpen(true)}
                  className="p-1.5 rounded-lg border border-[#333] bg-[#1A1A1A] text-[#A0A0A0] hover:text-[#E0E0E0] hover:border-[#666] transition-all flex items-center gap-2"
                  title="Aufnahme & Status"
                >
                  <Activity size={16} />
                </button>
                <button
                  onClick={() => setIsBuildEngineOpen(!isBuildEngineOpen)}
                  className={`p-1.5 rounded-lg border transition-all flex items-center gap-2
                    ${isBuildEngineOpen ? "bg-[#FFB300] text-[#121212] border-[#FFB300]" : "bg-[#1A1A1A] text-[#A0A0A0] border-[#333] hover:text-[#E0E0E0] hover:border-[#666]"}`}
                  title="Build-Engine"
                >
                  <GitBranch size={16} />
                </button>
              </div>
            </>
          )}
        </header>

        <main className="flex-1 flex flex-col min-h-0 overflow-hidden">
          {!minimalMode && (
            <div className="flex-none p-2 border-b border-[#222] bg-[#0A0A0A] flex flex-wrap gap-2">
              {TICKER_CATEGORY_IDS.map((id) => {
                const meta = TICKER_CATEGORY_META[id];
                const active = tickerVis[id];
                return (
                  <label
                    key={id}
                    className={`flex items-center gap-1.5 px-2 py-1 text-[10px] font-mono rounded border cursor-pointer transition-colors ${
                      active
                        ? meta.color + " " + meta.activeBorder
                        : meta.inactive
                    }`}
                  >
                    <input
                      type="checkbox"
                      checked={active}
                      onChange={() => toggleTickerCat(id)}
                      className="w-3 h-3 accent-current bg-transparent border-current cursor-pointer rounded-sm"
                    />
                    {meta.label}
                  </label>
                );
              })}
            </div>
          )}
          {!minimalMode && (
            <div className="flex-1 flex flex-col min-h-0">
              <LiveTicker
                logs={feedLogs}
                feedOk={feedOk}
                className="h-1/2 min-h-0 border-b border-[#222]"
                visibleCategories={tickerVis}
              />
              <ThoughtStream
                logs={feedLogs}
                feedOk={feedOk}
                wsThoughtLines={wsThoughts}
              />
            </div>
          )}
          <div
            className={`${minimalMode ? "flex-1 flex items-center justify-center" : "flex-none"}`}
          >
            <VoiceStrip
              apiBase={apiBase}
              mode={voiceMode}
              onModeChange={setVoiceMode}
            />
          </div>
        </main>

        <ValidationBuildEngine
          isOpen={isBuildEngineOpen}
          onClose={() => setIsBuildEngineOpen(false)}
          isRotating={false}
          onRotate={() => {}}
          logs={[
            {
              id: "1",
              source: "Architekt",
              severity: "info",
              message: "Keine strukturellen Verletzungen in der API-Route.",
            },
            {
              id: "2",
              source: "Sicherheit",
              severity: "warning",
              message:
                'CORS in Produktion ggf. zu offen (allow_origins=["*"]).',
            },
            {
              id: "3",
              source: "Performance",
              severity: "error",
              message: "ChromaDB-Locking bei hoher Last prüfen.",
            },
          ]}
        />

        <HealthBoard
          isOpen={isHealthBoardOpen}
          onClose={() => setIsHealthBoardOpen(false)}
          apiBase={apiBase}
          chatMode={voiceMode === "live" ? "live" : "deep"}
        />

        <ElevenLabsBoard
          isOpen={isElevenLabsBoardOpen}
          onClose={() => setIsElevenLabsBoardOpen(false)}
          apiBase={apiBase}
        />
      </div>
    </div>
  );
}
