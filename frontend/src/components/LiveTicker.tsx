import React, { useEffect, useRef, useMemo } from "react";
import type { TickerCategoryId } from "../cockpitTickerCategories";
import { TICKER_CATEGORY_META } from "../cockpitTickerCategories";

type LogEntry = {
  ts: string;
  level: string;
  msg: string;
  src?: string;
  category: TickerCategoryId;
};

type Props = {
  logs: LogEntry[];
  feedOk: boolean;
  className?: string;
  visibleCategories: Record<TickerCategoryId, boolean>;
};

const tagByCategory: Record<TickerCategoryId, string> = {
  ha_sensor: "HA",
  ha_warn: "HA!",
  ha_crit: "HA!!",
  heuristic: "HEUR",
  system: "SYS",
  core: "CORE",
  host: "HOST",
};

export default function LiveTicker({
  logs,
  feedOk,
  className = "",
  visibleCategories,
}: Props) {
  const bottomRef = useRef<HTMLDivElement>(null);

  const lines = useMemo(() => {
    return logs.filter(
      (e) =>
        e.category in TICKER_CATEGORY_META && visibleCategories[e.category]
    );
  }, [logs, visibleCategories]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [lines]);

  return (
    <div
      className={`flex flex-col bg-[#0A0A0A] border-r border-[#222] overflow-hidden ${className}`}
    >
      <div className="flex-none px-3 py-2 border-b border-[#222] flex items-center justify-between gap-2">
        <div className="flex flex-col min-w-0">
          <span className="text-[10px] font-mono uppercase tracking-wider text-[#FFB300]">
            Live-Ticker
          </span>
          <span className="text-[8px] text-[#444] font-mono truncate">
            Rohstrom — Filter oben
          </span>
        </div>
        <span
          className={`h-2 w-2 rounded-full shrink-0 ${
            feedOk ? "bg-[#4CAF50]" : "bg-[#F44336] animate-pulse"
          }`}
          title={feedOk ? "Feed aktiv" : "Kein Feed"}
        />
      </div>
      <div className="flex-1 overflow-y-auto p-2 font-mono text-[10px] leading-relaxed space-y-0.5">
        {!feedOk && lines.length === 0 && (
          <div className="text-[#666] text-[9px] leading-snug px-1">
            Backend nicht erreichbar — API starten (Port 8000) und ggf.
            VITE_CORE_API_URL prüfen.
          </div>
        )}
        {feedOk && lines.length === 0 && (
          <div className="text-[#555] text-[9px] italic px-1">
            Keine Zeilen — mindestens einen Filter aktiv lassen.
          </div>
        )}
        {lines.map((e, i) => {
          const meta = TICKER_CATEGORY_META[e.category];
          const tag = tagByCategory[e.category];
          return (
            <div
              key={`${e.ts}-${i}-${e.msg.slice(0, 20)}`}
              className="flex gap-2 text-[#555]"
            >
              <span className="text-[#333] shrink-0">{e.ts}</span>
              <span
                className={`shrink-0 px-0.5 rounded text-[9px] font-bold ${meta.color}`}
              >
                [{tag}]
              </span>
              <span className="text-[#888] truncate min-w-0">{e.msg}</span>
            </div>
          );
        })}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}
