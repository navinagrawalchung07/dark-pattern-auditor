"use client";

import { useState } from "react";
import {
  Finding,
  PatternPrecedents,
  PATTERN_LABELS,
  PATTERN_COLORS,
  SEVERITY_COLORS,
  SEVERITY_DOT,
  SEVERITY_BORDER,
} from "@/lib/types";
import {
  ExternalLink,
  ChevronDown,
  ChevronUp,
  FileText,
  Scale,
  AlertTriangle,
} from "lucide-react";

interface FindingCardProps {
  finding: Finding;
  precedents?: PatternPrecedents;
  index: number;
}

export function FindingCard({ finding, precedents, index }: FindingCardProps) {
  const [expanded, setExpanded] = useState(false);
  const [screenshotOpen, setScreenshotOpen] = useState(false);

  const patternLabel = PATTERN_LABELS[finding.pattern_type] ?? finding.pattern_type;
  const patternColor = PATTERN_COLORS[finding.pattern_type];
  const severityColor = SEVERITY_COLORS[finding.severity];
  const borderColor = SEVERITY_BORDER[finding.severity];
  const dotColor = SEVERITY_DOT[finding.severity];

  return (
    <div
      data-testid={`finding-card-${index}`}
      className={`rounded-xl border bg-[#0f1117] overflow-hidden animate-slide-up ${borderColor}`}
      style={{ animationDelay: `${index * 60}ms` }}
    >
      {/* Header */}
      <div className="flex items-start gap-4 p-5">
        {/* Screenshot thumbnail */}
        {finding.screenshot_b64 && (
          <button
            onClick={() => setScreenshotOpen(true)}
            data-testid={`screenshot-thumb-${index}`}
            className="flex-shrink-0 w-20 h-14 rounded-lg overflow-hidden border border-white/10 hover:border-white/30 transition-colors group relative"
            title="Click to enlarge screenshot"
          >
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={`data:image/png;base64,${finding.screenshot_b64}`}
              alt={`Screenshot: ${finding.step_name}`}
              className="w-full h-full object-cover group-hover:scale-105 transition-transform"
            />
            <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
              <span className="text-[10px] text-white font-medium">Enlarge</span>
            </div>
          </button>
        )}

        <div className="flex-1 min-w-0">
          {/* Badges row */}
          <div className="flex flex-wrap items-center gap-2 mb-2">
            <span
              className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-semibold border ${patternColor}`}
            >
              {patternLabel}
            </span>
            <span
              className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-semibold border ${severityColor} ${
                finding.severity === "high" ? "badge-high" : ""
              }`}
            >
              <span className={`w-1.5 h-1.5 rounded-full ${dotColor}`} />
              {finding.severity.toUpperCase()}
            </span>
            <span className="text-xs text-slate-500 font-mono">
              {finding.step_name.replace(/_/g, " ")}
            </span>
          </div>

          {/* Description */}
          <p className="text-sm text-slate-300 leading-relaxed">
            {finding.description}
          </p>

          {/* Quoted UI text */}
          {finding.quoted_ui_text && (
            <blockquote className="mt-3 pl-3 border-l-2 border-slate-600 text-xs text-slate-400 font-mono italic leading-relaxed">
              &ldquo;{finding.quoted_ui_text}&rdquo;
            </blockquote>
          )}
        </div>
      </div>

      {/* Statute strip */}
      <div className="px-5 pb-3 flex items-start gap-3">
        <Scale className="w-4 h-4 text-indigo-400 flex-shrink-0 mt-0.5" />
        <div className="min-w-0">
          <div className="text-xs font-semibold text-indigo-400 mb-0.5">
            {finding.statute_name}
          </div>
          {finding.statute_excerpt && (
            <p className="text-xs text-slate-500 leading-relaxed line-clamp-2">
              {finding.statute_excerpt}
            </p>
          )}
          {finding.statutory_url && (
            <a
              href={finding.statutory_url}
              target="_blank"
              rel="noopener noreferrer"
              data-testid={`statute-link-${index}`}
              className="inline-flex items-center gap-1 mt-1 text-[11px] text-indigo-400/70 hover:text-indigo-400 transition-colors"
            >
              View statute <ExternalLink className="w-2.5 h-2.5" />
            </a>
          )}
        </div>
      </div>

      {/* Expandable precedents */}
      {precedents && precedents.cases.length > 0 && (
        <div className="border-t border-white/5">
          <button
            onClick={() => setExpanded(!expanded)}
            data-testid={`expand-precedents-${index}`}
            className="w-full flex items-center justify-between px-5 py-3 text-xs text-slate-400 hover:text-slate-200 hover:bg-white/[0.02] transition-all"
          >
            <span className="flex items-center gap-2">
              <FileText className="w-3.5 h-3.5" />
              {precedents.cases.length} Enforcement Precedent
              {precedents.cases.length > 1 ? "s" : ""}
            </span>
            {expanded ? (
              <ChevronUp className="w-3.5 h-3.5" />
            ) : (
              <ChevronDown className="w-3.5 h-3.5" />
            )}
          </button>

          {expanded && (
            <div className="px-5 pb-4 space-y-3">
              {precedents.cases.map((c, ci) => (
                <div
                  key={ci}
                  data-testid={`precedent-case-${index}-${ci}`}
                  className="rounded-lg bg-[#161a23] border border-white/5 p-3"
                >
                  <div className="flex items-start justify-between gap-3 mb-1">
                    <span className="text-xs font-semibold text-slate-200">
                      {c.case_name}
                    </span>
                    <span className="flex-shrink-0 text-[10px] text-slate-500 font-mono">
                      {c.year}
                    </span>
                  </div>
                  <div className="text-[11px] text-slate-400 mb-1">
                    <span className="text-indigo-400">{c.company}</span>
                  </div>
                  <p className="text-[11px] text-slate-500 leading-relaxed">
                    {c.outcome}
                  </p>
                  {c.source_url && (
                    <a
                      href={c.source_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      data-testid={`case-source-${index}-${ci}`}
                      className="inline-flex items-center gap-1 mt-2 text-[10px] text-indigo-400/70 hover:text-indigo-400 transition-colors"
                    >
                      Source <ExternalLink className="w-2.5 h-2.5" />
                    </a>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Screenshot modal */}
      {screenshotOpen && finding.screenshot_b64 && (
        <div
          className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4"
          onClick={() => setScreenshotOpen(false)}
        >
          <div
            className="max-w-4xl w-full rounded-xl overflow-hidden border border-white/10"
            onClick={(e) => e.stopPropagation()}
          >
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={`data:image/png;base64,${finding.screenshot_b64}`}
              alt={`Screenshot: ${finding.step_name}`}
              className="w-full"
            />
            <div className="bg-[#0f1117] px-4 py-2 flex items-center justify-between">
              <span className="text-xs text-slate-400 font-mono">
                {finding.step_name.replace(/_/g, " ")} — {finding.pattern_type}
              </span>
              <button
                onClick={() => setScreenshotOpen(false)}
                className="text-xs text-slate-500 hover:text-slate-200 transition-colors"
              >
                Close ✕
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
