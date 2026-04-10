"use client";

import { useState, useCallback, useRef } from "react";
import { Search, Loader2, AlertCircle, RefreshCw } from "lucide-react";
import { Logo } from "@/components/Logo";
import { StatusStream } from "@/components/StatusStream";
import { FindingCard } from "@/components/FindingCard";
import { SummaryBar } from "@/components/SummaryBar";
import { Finding, PatternPrecedents } from "@/lib/types";

const API_BASE =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

type AuditPhase =
  | "idle"
  | "starting"
  | "streaming"
  | "complete"
  | "error";

export default function Home() {
  const [url, setUrl] = useState("");
  const [phase, setPhase] = useState<AuditPhase>("idle");
  const [statusMessages, setStatusMessages] = useState<string[]>([]);
  const [findings, setFindings] = useState<Finding[]>([]);
  const [precedentsMap, setPrecedentsMap] = useState<
    Record<string, PatternPrecedents>
  >({});
  const [error, setError] = useState<string | null>(null);
  const eventSourceRef = useRef<EventSource | null>(null);

  const addStatus = useCallback((msg: string) => {
    setStatusMessages((prev) => [...prev, msg]);
  }, []);

  const resetState = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
    setStatusMessages([]);
    setFindings([]);
    setPrecedentsMap({});
    setError(null);
    setPhase("idle");
  }, []);

  const startAudit = useCallback(async () => {
    if (!url.trim()) return;
    resetState();
    setPhase("starting");

    try {
      // 1. POST /audit to start the task
      const res = await fetch(`${API_BASE}/audit`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: url.trim() }),
      });

      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail ?? `Server error ${res.status}`);
      }

      const { task_id } = await res.json();
      addStatus(`Audit started (task: ${task_id.slice(0, 8)}…)`);
      setPhase("streaming");

      // 2. Open SSE stream
      const es = new EventSource(`${API_BASE}/audit/${task_id}/stream`);
      eventSourceRef.current = es;

      es.addEventListener("status", (e: MessageEvent) => {
        const data = JSON.parse(e.data);
        addStatus(data.message ?? String(data));
      });

      es.addEventListener("finding", (e: MessageEvent) => {
        const finding: Finding = JSON.parse(e.data);
        setFindings((prev) => [...prev, finding]);
      });

      es.addEventListener("precedents", (e: MessageEvent) => {
        const prec: PatternPrecedents = JSON.parse(e.data);
        setPrecedentsMap((prev) => ({
          ...prev,
          [prec.pattern_type]: prec,
        }));
      });

      es.addEventListener("done", () => {
        es.close();
        eventSourceRef.current = null;
        setPhase("complete");
      });

      es.addEventListener("error", (e: MessageEvent) => {
        try {
          const data = JSON.parse((e as any).data ?? "{}");
          addStatus(`Error: ${data.message ?? "Unknown error"}`);
          setError(data.message ?? "Audit failed");
        } catch {
          // SSE connection error — ignore, "done" will follow
        }
      });

      es.onerror = () => {
        if (eventSourceRef.current?.readyState === EventSource.CLOSED) {
          setPhase((p) => (p === "streaming" ? "complete" : p));
        }
      };
    } catch (err: any) {
      setError(err.message ?? "Failed to start audit");
      setPhase("error");
    }
  }, [url, resetState, addStatus]);

  const isRunning = phase === "starting" || phase === "streaming";
  const showResults = findings.length > 0 || phase === "complete";

  return (
    <div className="min-h-screen bg-[#08090c]">
      {/* Scan line animation while running */}
      {isRunning && <div className="scan-line" />}

      {/* ───────── Header ───────── */}
      <header className="border-b border-white/5 bg-[#0f1117]/80 backdrop-blur-md sticky top-0 z-40">
        <div className="max-w-5xl mx-auto px-6 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Logo className="w-8 h-8 text-indigo-400" />
            <div>
              <h1 className="text-sm font-bold text-slate-100 leading-tight">
                Dark Pattern Auditor
              </h1>
              <p className="text-[10px] text-slate-500 leading-tight">
                FTC &amp; EU Compliance Scanner
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <span className="hidden sm:inline text-[10px] text-slate-600 bg-[#161a23] border border-white/5 px-2 py-1 rounded font-mono">
              sonar-reasoning-pro
            </span>
            <span className="text-[10px] text-slate-600 bg-[#161a23] border border-white/5 px-2 py-1 rounded font-mono">
              Playwright
            </span>
          </div>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-6 py-12 space-y-10">
        {/* ───────── Hero ───────── */}
        <div className="text-center space-y-4 max-w-2xl mx-auto">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-indigo-400/30 bg-indigo-400/5 text-indigo-400 text-xs font-medium">
            <span className="w-1.5 h-1.5 rounded-full bg-indigo-400 animate-pulse" />
            Live browser automation + AI legal analysis
          </div>
          <h2 className="text-3xl font-bold text-slate-100 leading-tight tracking-tight">
            Detect dark patterns.
            <br />
            <span className="text-indigo-400">Cite the law.</span>
          </h2>
          <p className="text-sm text-slate-400 leading-relaxed">
            Playwright navigates your target site through signup, cancellation,
            and cookie consent flows — capturing screenshots at each step.
            Perplexity then classifies findings against live statute text from
            ftc.gov and ec.europa.eu and surfaces real enforcement precedents.
          </p>
        </div>

        {/* ───────── URL Input ───────── */}
        <div className="max-w-2xl mx-auto">
          <div className="flex gap-3">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
              <input
                type="url"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && !isRunning && startAudit()}
                placeholder="https://example.com"
                disabled={isRunning}
                data-testid="input-url"
                className="w-full pl-10 pr-4 py-3 rounded-xl border border-white/10 bg-[#0f1117] text-slate-200 placeholder-slate-600 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500/50 transition-all disabled:opacity-50"
              />
            </div>
            <button
              onClick={isRunning ? undefined : startAudit}
              disabled={isRunning || !url.trim()}
              data-testid="button-audit"
              className="flex items-center gap-2 px-6 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed text-sm font-semibold text-white transition-all active:scale-95"
            >
              {isRunning ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Auditing…
                </>
              ) : (
                <>
                  <Search className="w-4 h-4" />
                  Run Audit
                </>
              )}
            </button>
          </div>

          {/* Quick examples */}
          {phase === "idle" && (
            <div className="mt-3 flex flex-wrap gap-2 items-center">
              <span className="text-[11px] text-slate-600">Try:</span>
              {["amazon.com", "netflix.com", "linkedin.com", "grammarly.com"].map(
                (example) => (
                  <button
                    key={example}
                    onClick={() => setUrl(`https://${example}`)}
                    data-testid={`example-${example}`}
                    className="text-[11px] text-slate-500 hover:text-indigo-400 border border-white/5 hover:border-indigo-400/30 px-2 py-0.5 rounded transition-all"
                  >
                    {example}
                  </button>
                )
              )}
            </div>
          )}
        </div>

        {/* ───────── Error state ───────── */}
        {phase === "error" && error && (
          <div className="max-w-2xl mx-auto rounded-xl border border-red-400/30 bg-red-400/5 p-4 flex items-start gap-3">
            <AlertCircle className="w-4 h-4 text-red-400 flex-shrink-0 mt-0.5" />
            <div>
              <div className="text-sm font-semibold text-red-400 mb-1">
                Audit failed
              </div>
              <p className="text-xs text-slate-400">{error}</p>
              <button
                onClick={resetState}
                className="mt-2 flex items-center gap-1.5 text-xs text-slate-400 hover:text-slate-200 transition-colors"
              >
                <RefreshCw className="w-3 h-3" /> Try again
              </button>
            </div>
          </div>
        )}

        {/* ───────── Live status stream ───────── */}
        {(isRunning || statusMessages.length > 0) && (
          <div className="max-w-2xl mx-auto">
            <StatusStream
              messages={statusMessages}
              isRunning={isRunning}
            />
          </div>
        )}

        {/* ───────── Results ───────── */}
        {showResults && (
          <div className="space-y-6 animate-fade-in">
            {/* Summary bar */}
            <SummaryBar findings={findings} targetUrl={url} />

            {/* Reset button */}
            {phase === "complete" && (
              <div className="flex justify-end">
                <button
                  onClick={resetState}
                  data-testid="button-reset"
                  className="flex items-center gap-1.5 text-xs text-slate-500 hover:text-slate-200 transition-colors"
                >
                  <RefreshCw className="w-3 h-3" /> New Audit
                </button>
              </div>
            )}

            {/* Findings list */}
            {findings.length > 0 ? (
              <div className="space-y-4">
                <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-widest">
                  Findings ({findings.length})
                </h3>
                {findings.map((finding, i) => (
                  <FindingCard
                    key={i}
                    finding={finding}
                    precedents={precedentsMap[finding.pattern_type]}
                    index={i}
                  />
                ))}
              </div>
            ) : phase === "complete" ? (
              <div className="rounded-xl border border-white/5 bg-[#0f1117] p-8 text-center">
                <div className="text-4xl mb-3">✓</div>
                <div className="text-sm font-semibold text-slate-300 mb-1">
                  No dark patterns detected
                </div>
                <p className="text-xs text-slate-500">
                  The crawled flows appear compliant. Note: not all flows
                  could be fully navigated — manual review is recommended.
                </p>
              </div>
            ) : null}
          </div>
        )}

        {/* ───────── About / Legend ───────── */}
        {phase === "idle" && (
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 max-w-3xl mx-auto mt-8">
            {[
              { label: "Roach Motel", color: "text-purple-400", desc: "Hard to cancel" },
              { label: "Confirmshaming", color: "text-orange-400", desc: "Guilt-trip declines" },
              { label: "Hidden Costs", color: "text-red-400", desc: "Late fee disclosure" },
              { label: "Trick Questions", color: "text-yellow-400", desc: "Deceptive checkboxes" },
              { label: "Disguised Ads", color: "text-blue-400", desc: "Ads as content" },
              { label: "Forced Continuity", color: "text-pink-400", desc: "Silent trial-to-paid" },
              { label: "Misdirection", color: "text-cyan-400", desc: "Visual manipulation" },
              {
                label: "7 Patterns",
                color: "text-indigo-400",
                desc: "FTC & EU statute coverage",
              },
            ].map((item) => (
              <div
                key={item.label}
                className="rounded-lg border border-white/5 bg-[#0f1117] p-3 text-center"
              >
                <div className={`text-xs font-semibold mb-0.5 ${item.color}`}>
                  {item.label}
                </div>
                <div className="text-[10px] text-slate-600">{item.desc}</div>
              </div>
            ))}
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-white/5 mt-20">
        <div className="max-w-5xl mx-auto px-6 py-6 flex items-center justify-between text-[11px] text-slate-600">
          <span>Dark Pattern Auditor — research tool only, not legal advice</span>
          <span className="font-mono">Powered by Perplexity sonar-reasoning-pro</span>
        </div>
      </footer>
    </div>
  );
}
