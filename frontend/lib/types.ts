export type Severity = "low" | "medium" | "high";

export type PatternType =
  | "roach_motel"
  | "confirmshaming"
  | "hidden_costs"
  | "trick_questions"
  | "disguised_ads"
  | "forced_continuity"
  | "misdirection";

export interface Finding {
  pattern_type: PatternType;
  severity: Severity;
  description: string;
  quoted_ui_text: string;
  statute_name: string;
  statute_excerpt: string;
  statutory_url: string;
  step_name: string;
  screenshot_b64?: string;
}

export interface EnforcementCase {
  case_name: string;
  company: string;
  year: number;
  outcome: string;
  source_url: string;
}

export interface PatternPrecedents {
  pattern_type: PatternType;
  cases: EnforcementCase[];
}

export const PATTERN_LABELS: Record<PatternType, string> = {
  roach_motel: "Roach Motel",
  confirmshaming: "Confirmshaming",
  hidden_costs: "Hidden Costs",
  trick_questions: "Trick Questions",
  disguised_ads: "Disguised Ads",
  forced_continuity: "Forced Continuity",
  misdirection: "Misdirection",
};

export const PATTERN_DESCRIPTIONS: Record<PatternType, string> = {
  roach_motel: "Easy to sign up, deliberately hard to cancel",
  confirmshaming: "Guilt-tripping decline button language",
  hidden_costs: "Fees added late in checkout",
  trick_questions: "Pre-ticked boxes or confusing opt-outs",
  disguised_ads: "Paid content styled as organic content",
  forced_continuity: "Trial-to-paid without clear warning",
  misdirection: "Visual design obscures important info",
};

export const SEVERITY_COLORS: Record<Severity, string> = {
  low: "text-green-400 bg-green-400/10 border-green-400/30",
  medium: "text-amber-400 bg-amber-400/10 border-amber-400/30",
  high: "text-red-400 bg-red-400/10 border-red-400/30",
};

export const SEVERITY_BORDER: Record<Severity, string> = {
  low: "border-green-400/20",
  medium: "border-amber-400/20",
  high: "border-red-400/30",
};

export const SEVERITY_DOT: Record<Severity, string> = {
  low: "bg-green-400",
  medium: "bg-amber-400",
  high: "bg-red-400",
};

export const PATTERN_COLORS: Record<PatternType, string> = {
  roach_motel: "text-purple-400 bg-purple-400/10 border-purple-400/30",
  confirmshaming: "text-orange-400 bg-orange-400/10 border-orange-400/30",
  hidden_costs: "text-red-400 bg-red-400/10 border-red-400/30",
  trick_questions: "text-yellow-400 bg-yellow-400/10 border-yellow-400/30",
  disguised_ads: "text-blue-400 bg-blue-400/10 border-blue-400/30",
  forced_continuity: "text-pink-400 bg-pink-400/10 border-pink-400/30",
  misdirection: "text-cyan-400 bg-cyan-400/10 border-cyan-400/30",
};
