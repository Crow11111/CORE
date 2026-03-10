import React from 'react';
import { motion } from 'motion/react';
import { Activity, GitBranch, Shield, Clock } from 'lucide-react';
import type { TelemetryData } from '../hooks/useTelemetryPolling';

type Props = {
  data: TelemetryData | null;
  connected: boolean;
};

function formatUptime(seconds: number): string {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  if (h > 0) return `${h}h ${m}m`;
  return `${m}m`;
}

export default function TelemetryHUD({ data, connected }: Props) {
  if (!connected || !data) {
    return (
      <div className="flex items-center gap-2 px-3 py-2 bg-[#2A2A2A] border border-[#333] rounded-xl">
        <span className="flex h-2 w-2 rounded-full bg-[#F44336]" />
        <span className="text-[11px] font-mono text-[#666] uppercase">Telemetry offline</span>
      </div>
    );
  }

  const { watchdog, friction_violations, api_uptime_s } = data;
  const latencyOk = watchdog.latency_ms > 0;
  const gitOk = watchdog.git_status === 'SYNCED';

  return (
    <div className="flex flex-wrap items-center gap-2">
      {/* Pulse / Latency */}
      <div className="flex items-center gap-1.5 px-2.5 py-1.5 bg-[#222] border border-[#2A2A2A] rounded-lg">
        <motion.div
          animate={latencyOk ? { scale: [1, 1.3, 1], opacity: [0.7, 1, 0.7] } : {}}
          transition={{ duration: 1.5, repeat: Infinity, ease: 'easeInOut' }}
        >
          <Activity className={`w-3.5 h-3.5 ${latencyOk ? 'text-[#4CAF50]' : 'text-[#F44336]'}`} />
        </motion.div>
        <span className="text-[11px] font-mono text-[#A0A0A0]">
          {latencyOk ? `${watchdog.latency_ms.toFixed(0)}ms` : 'VOID'}
        </span>
      </div>

      {/* Git Status */}
      <div className="flex items-center gap-1.5 px-2.5 py-1.5 bg-[#222] border border-[#2A2A2A] rounded-lg">
        <GitBranch className={`w-3.5 h-3.5 ${gitOk ? 'text-[#4CAF50]' : 'text-[#FFC107]'}`} />
        <span className="text-[11px] font-mono text-[#A0A0A0]">{watchdog.git_status}</span>
      </div>

      {/* Friction */}
      {friction_violations > 0 && (
        <div className="flex items-center gap-1.5 px-2.5 py-1.5 bg-[#2A2020] border border-[#3A2020] rounded-lg">
          <Shield className="w-3.5 h-3.5 text-[#F44336]" />
          <span className="text-[11px] font-mono text-[#F08080]">{friction_violations}</span>
        </div>
      )}

      {/* Uptime */}
      <div className="flex items-center gap-1.5 px-2.5 py-1.5 bg-[#222] border border-[#2A2A2A] rounded-lg">
        <Clock className="w-3.5 h-3.5 text-[#888]" />
        <span className="text-[11px] font-mono text-[#A0A0A0]">{formatUptime(api_uptime_s)}</span>
      </div>

      {/* Mode */}
      <div className="flex items-center gap-1.5 px-2.5 py-1.5 bg-[#222] border border-[#2A2A2A] rounded-lg">
        <span className={`flex h-2 w-2 rounded-full ${
          watchdog.mode === 'WATCH' ? 'bg-[#4CAF50]' : 'bg-[#FFC107]'
        }`} />
        <span className="text-[11px] font-mono text-[#A0A0A0] uppercase">{watchdog.mode}</span>
      </div>
    </div>
  );
}
