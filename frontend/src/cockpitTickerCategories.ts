/** Kategorien fuer /api/cockpit_feed — Toggles unter CORE COCKPIT */

export type TickerCategoryId =
  | "ha_sensor"
  | "ha_warn"
  | "ha_crit"
  | "heuristic"
  | "system"
  | "core"
  | "host";

export const TICKER_CATEGORY_META: Record<
  TickerCategoryId,
  {
    label: string;
    short: string;
    color: string;
    activeBorder: string;
    inactive: string;
  }
> = {
  ha_sensor: {
    label: "HA Sensor (INFO)",
    short: "HA·I",
    color: "bg-[#1B3D2F] text-[#81C784] border-[#4CAF50]/50",
    activeBorder: "border-[#4CAF50]",
    inactive: "opacity-40 border-[#333] text-[#666]",
  },
  ha_warn: {
    label: "HA Warnung",
    short: "HA·W",
    color: "bg-[#3D3319] text-[#FFCA28] border-[#FFC107]/50",
    activeBorder: "border-[#FFC107]",
    inactive: "opacity-40 border-[#333] text-[#666]",
  },
  ha_crit: {
    label: "HA Kritisch",
    short: "HA·K",
    color: "bg-[#3D1F1F] text-[#FF8A65] border-[#FF5722]/50",
    activeBorder: "border-[#FF5722]",
    inactive: "opacity-40 border-[#333] text-[#666]",
  },
  heuristic: {
    label: "Heuristik (WARN)",
    short: "Heur",
    color: "bg-[#3D3510] text-[#FFE082] border-[#FFB300]/50",
    activeBorder: "border-[#FFB300]",
    inactive: "opacity-40 border-[#333] text-[#666]",
  },
  system: {
    label: "System (ERROR)",
    short: "ERR",
    color: "bg-[#3D1515] text-[#EF9A9A] border-[#F44336]/50",
    activeBorder: "border-[#F44336]",
    inactive: "opacity-40 border-[#333] text-[#666]",
  },
  core: {
    label: "CORE / Aktion",
    short: "CORE",
    color: "bg-[#0D2838] text-[#4FC3F7] border-[#29B6F6]/50",
    activeBorder: "border-[#29B6F6]",
    inactive: "opacity-40 border-[#333] text-[#666]",
  },
  host: {
    label: "Host / Linux",
    short: "Host",
    color: "bg-[#252525] text-[#B0BEC5] border-[#78909C]/50",
    activeBorder: "border-[#78909C]",
    inactive: "opacity-40 border-[#333] text-[#666]",
  },
};

export const TICKER_CATEGORY_IDS = Object.keys(
  TICKER_CATEGORY_META,
) as TickerCategoryId[];

/** Standard: alles an — sonst wirkt der Ticker „leer“. */
export const DEFAULT_TICKER_VISIBILITY: Record<TickerCategoryId, boolean> = {
  ha_sensor: false,
  ha_warn: false,
  ha_crit: false,
  heuristic: false,
  system: false,
  core: true,
  host: false,
};
