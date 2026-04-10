"use client";

import { useEffect, useRef } from "react";
import { Terminal } from "lucide-react";

interface StatusStreamProps {
  messages: string[];
  isRunning: boolean;
}

export function StatusStream({ messages, isRunning }: StatusStreamProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="rounded-xl border border-white/10 bg-[#0a0c10] overflow-hidden">
      {/* Terminal header */}
      <div className="flex items-center gap-2 px-4 py-2.5 border-b border-white/10 bg-[#0f1117]">
        <div className="flex gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-red-500/60" />
          <span className="w-2.5 h-2.5 rounded-full bg-amber-500/60" />
          <span className="w-2.5 h-2.5 rounded-full bg-green-500/60" />
        </div>
        <div className="flex items-center gap-2 ml-2">
          <Terminal className="w-3 h-3 text-slate-500" />
          <span className="text-[11px] text-slate-500 font-mono">audit — crawler log</span>
        </div>
        {isRunning && (
          <div className="ml-auto flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse" />
            <span className="text-[10px] text-green-400 font-mono">LIVE</span>
          </div>
        )}
      </div>

      {/* Log area */}
      <div
        className="status-log h-48 overflow-y-auto p-4 space-y-1 font-mono text-xs"
        data-testid="status-log"
      >
        {messages.length === 0 ? (
          <span className="text-slate-600">Waiting for audit to start…</span>
        ) : (
          messages.map((msg, i) => (
            <div
              key={i}
              className="flex items-start gap-2 text-slate-400 leading-relaxed"
            >
              <span className="text-slate-600 flex-shrink-0 select-none">
                {String(i + 1).padStart(2, "0")} &gt;
              </span>
              <span className={i === messages.length - 1 ? "text-slate-200" : ""}>
                {msg}
              </span>
            </div>
          ))
        )}
        {isRunning && (
          <div className="flex items-center gap-1.5 text-slate-600">
            <span className="select-none">{String(messages.length + 1).padStart(2, "0")} &gt;</span>
            <span className="inline-block w-2 h-4 bg-indigo-400 animate-pulse ml-1" />
          </div>
        )}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}
