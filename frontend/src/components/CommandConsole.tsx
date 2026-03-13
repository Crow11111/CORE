import React, { useState } from "react";
import { Send, Terminal } from "lucide-react";

type Props = {
  onExecute: (cmd: string) => void;
  isProcessing: boolean;
};

export default function CommandConsole({ onExecute, isProcessing }: Props) {
  const [input, setInput] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim() && !isProcessing) {
      onExecute(input);
      setInput("");
    }
  };

  return (
    <div className="w-full bg-[#1A1A1A] border-t border-[#333] p-4 relative z-10 shadow-[0_-10px_40px_rgba(0,0,0,0.49)]">
      <div className="max-w-5xl mx-auto flex items-end gap-4 relative">
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
              isProcessing
                ? "System berechnet..."
                : "Kommando eingeben... (Enter zum Senden, Shift+Enter für neue Zeile)"
            }
            disabled={isProcessing}
            rows={Math.min(10, Math.max(1, input.split("\n").length))}
            className="w-full bg-[#222] border border-[#333] rounded-xl pl-12 pr-12 py-3.5
                     text-[#E0E0E0] placeholder-[#666] focus:outline-none focus:border-[#FFB300]
                     focus:ring-1 focus:ring-[#FFB300] transition-all resize-none font-mono text-sm leading-relaxed
                     disabled:opacity-50 disabled:cursor-not-allowed"
          />

          <button
            type="submit"
            disabled={!input.trim() || isProcessing}
            className="absolute right-2 bottom-2 p-2 rounded-lg
                     bg-[#333] text-[#E0E0E0] hover:bg-[#FFB300] hover:text-[#121212]
                     disabled:opacity-50 disabled:hover:bg-[#333] disabled:hover:text-[#E0E0E0]
                     transition-colors flex items-center justify-center"
          >
            <Send
              size={16}
              className={input.trim() && !isProcessing ? "ml-1" : ""}
            />
          </button>
        </form>
      </div>
    </div>
  );
}
