export function Logo({ className = "" }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 40 40"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-label="Dark Pattern Auditor"
      className={className}
    >
      {/* Shield outline */}
      <path
        d="M20 3 L34 9 L34 22 C34 30 27 36 20 38 C13 36 6 30 6 22 L6 9 Z"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinejoin="round"
        fill="none"
      />
      {/* Eye */}
      <ellipse cx="20" cy="21" rx="7" ry="5" stroke="currentColor" strokeWidth="1.5" />
      <circle cx="20" cy="21" r="2.5" fill="currentColor" />
      {/* Strikethrough diagonal — the "audit" / catch */}
      <line
        x1="12"
        y1="13"
        x2="28"
        y2="29"
        stroke="#ef4444"
        strokeWidth="1.5"
        strokeLinecap="round"
      />
    </svg>
  );
}
