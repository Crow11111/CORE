import React, { useMemo, useEffect, useRef } from "react";
import type { TickerCategoryId } from "../cockpitTickerCategories";

const THOUGHT_CATEGORIES: TickerCategoryId[] = [
  "core",
  "heuristic",
  "system",
  "ha_crit",
  "ha_warn",
  "host",
];

type Row = {
  ts: string;
  msg: string;
  category: TickerCategoryId;
  level: string;
};

type Props = {
  logs: Row[];
  feedOk: boolean;
  wsThoughtLines?: string[];
};

const catStyle: Partial<Record<TickerCategoryId, string>> = {
  core: "border-l-[#29B6F6] text-[#B3E5FC]",
  heuristic: "border-l-[#FFB300] text-[#FFE082]",
  system: "border-l-[#F44336] text-[#FFCDD2]",
  ha_crit: "border-l-[#FF5722] text-[#FFCCBC]",
  ha_warn: "border-l-[#FFC107] text-[#FFF9C4]",
  host: "border-l-[#78909C] text-[#CFD8DC]",
};

export default function ThoughtStream({
  logs,
  feedOk,
  wsThoughtLines = [],
}: Props) {
  const bottomRef = useRef<HTMLDivElement>(null);

  const rows = useMemo(() => {
    const seen = new Set<string>();
    const out: Row[] = [];
    for (const e of logs) {
      if (!THOUGHT_CATEGORIES.includes(e.category)) continue;
      const k = `${e.ts}|${e.msg}`;
      if (seen.has(k)) continue;
      seen.add(k);
      out.push(e);
    }
    return out.slice(-120);
  }, [logs]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [rows, wsThoughtLines]);

  return (
    <div className="flex flex-col h-1/2 bg-[#0C0C0C] border-t border-[#1A1A1A]">
      <div className="flex-none px-4 py-2 border-b border-[#1A1A1A]">
        <h2 className="text-[11px] font-mono uppercase tracking-[0.15em] text-[#FFB300]">
          Gedanken & Zwischenstände
        </h2>
        <p className="text-[9px] text-[#444] font-mono mt-0.5">
          Kern, Heuristik, Fehler, HA-Alarme, Host — kein Chat, nur Puls.
        </p>
      </div>
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-3 font-mono text-[13px] leading-relaxed">
        {!feedOk && rows.length === 0 && wsThoughtLines.length === 0 && (
          <p className="text-[#555] text-sm">
            Warte auf Backend — wenn der Kern läuft, erscheinen hier Parser-,
            Heuristik- und Systemzeilen.
          </p>
        )}
        {wsThoughtLines.map((line, i) => (
          <div
            key={`ws-${i}`}
            className="pl-4 border-l-2 border-[#7C4DFF] text-[#D1C4E9] whitespace-pre-wrap"
          >
            {line}
          </div>
        ))}
        {rows.map((e, i) => (
          <div
            key={`${e.ts}-${i}`}
            className={`pl-4 border-l-2 ${catStyle[e.category] || "border-l-[#666] text-[#AAA]"}`}
          >
            <span className="text-[10px] text-[#444]">{e.ts}</span>{" "}
            <span className="text-[#666]">[{e.category}]</span>
            <br />
            <span>{e.msg}</span>
          </div>
        ))}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}
