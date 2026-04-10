"use client";

import { Finding, Severity } from "@/lib/types";
import { ShieldAlert, ShieldCheck } from "lucide-react";

interface SummaryBarProps {
  findings: Finding[];
  targetUrl: string;
}

const SEVERITY_COUNT_COLORS: Record<Severity, string> = {
  low: "text-green-400",
  medium: "text-amber-400",
  high: "text-red-400",
};

export function SummaryBar({ findings, targetUrl }: SummaryBarProps) {
  const counts: Record<Severity, number> = { low: 0, medium: 0, high: 0 };
  findings.forEach((f) => counts[f.severity]++);

  const totalHigh = counts.high;
  const hasFindings = findings.length > 0;

  return (
    <div
      className={`rounded-xl border p-5 flex items-center gap-6 ${
        totalHigh > 0
          ? "border-red-400/30 bg-red-400/5"
          : hasFindings
          ? "border-amber-400/20 bg-amber-400/5"
          : "border-green-400/20 bg-green-400/5"
      }`}
      data-testid="summary-bar"
    >
      {/* Icon */}
      <div className="flex-shrink-0">
        {hasFindings ? (
          <ShieldAlert
            className={`w-8 h-8 ${totalHigh > 0 ? "text-red-400" : "text-amber-400"}`}
          />
        ) : (
          <ShieldCheck className="w-8 h-8 text-green-400" />
        )}
      </div>

      {/* Main */}
      <div className="flex-1 min-w-0">
        <div className="text-sm font-semibold text-slate-200 mb-0.5 truncate">
          {hasFindings
            ? `${findings.length} dark pattern${findings.length > 1 ? "s" : ""} detected on ${new URL(targetUrl.startsWith("http") ? targetUrl : "https://" + targetUrl).hostname}`
            : `No dark patterns detected on ${targetUrl}`}
        </div>
        <div className="text-xs text-slate-500">
          {hasFindings
            ? "Patterns classified against live FTC and EU statutes"
            : "Site appears compliant based on crawled flows"}
        </div>
      </div>

      {/* Severity breakdown */}
      {hasFindings && (
        <div className="flex items-center gap-4 flex-shrink-0">
          {(["high", "medium", "low"] as Severity[]).map((sev) => (
            <div key={sev} className="text-center">
              <div className={`text-2xl font-bold tabular-nums ${SEVERITY_COUNT_COLORS[sev]}`}>
                {counts[sev]}
              </div>
              <div className="text-[10px] text-slate-500 uppercase tracking-wider">
                {sev}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
