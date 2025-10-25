export function SpaceCowboyIcon({ className = "w-24 h-24" }: { className?: string }) {
  return (
    <svg viewBox="0 0 200 200" fill="none" xmlns="http://www.w3.org/2000/svg" className={className}>
      {/* Lasso */}
      <path
        d="M140 60 Q160 40, 180 50 Q190 60, 185 75 Q180 90, 165 95 Q150 100, 140 90"
        stroke="currentColor"
        strokeWidth="3"
        fill="none"
        className="text-accent"
        strokeLinecap="round"
      />
      <path d="M140 60 L120 80" stroke="currentColor" strokeWidth="2.5" className="text-accent" strokeLinecap="round" />

      {/* Cowboy Hat */}
      <ellipse cx="80" cy="65" rx="28" ry="8" fill="currentColor" className="text-primary" />
      <path
        d="M60 65 Q65 45, 80 40 Q95 45, 100 65 L95 70 Q80 75, 65 70 Z"
        fill="currentColor"
        className="text-primary"
      />

      {/* Cowboy Head */}
      <circle cx="80" cy="85" r="12" fill="currentColor" className="text-accent" />

      {/* Cowboy Body */}
      <path
        d="M80 97 L80 125"
        stroke="currentColor"
        strokeWidth="8"
        className="text-foreground"
        strokeLinecap="round"
      />

      {/* Arms */}
      <path
        d="M80 105 L95 115"
        stroke="currentColor"
        strokeWidth="5"
        className="text-foreground"
        strokeLinecap="round"
      />
      <path
        d="M80 105 L120 80"
        stroke="currentColor"
        strokeWidth="5"
        className="text-foreground"
        strokeLinecap="round"
      />

      {/* Horse Body */}
      <ellipse cx="75" cy="145" rx="35" ry="20" fill="currentColor" className="text-muted-foreground" />

      {/* Horse Head */}
      <ellipse cx="105" cy="135" rx="12" ry="15" fill="currentColor" className="text-muted-foreground" />
      <path
        d="M110 125 L115 120"
        stroke="currentColor"
        strokeWidth="3"
        className="text-muted-foreground"
        strokeLinecap="round"
      />
      <path
        d="M110 128 L115 128"
        stroke="currentColor"
        strokeWidth="2"
        className="text-muted-foreground"
        strokeLinecap="round"
      />

      {/* Horse Legs */}
      <path
        d="M55 160 L55 180"
        stroke="currentColor"
        strokeWidth="4"
        className="text-muted-foreground"
        strokeLinecap="round"
      />
      <path
        d="M70 160 L70 180"
        stroke="currentColor"
        strokeWidth="4"
        className="text-muted-foreground"
        strokeLinecap="round"
      />
      <path
        d="M85 160 L85 180"
        stroke="currentColor"
        strokeWidth="4"
        className="text-muted-foreground"
        strokeLinecap="round"
      />
      <path
        d="M95 160 L95 180"
        stroke="currentColor"
        strokeWidth="4"
        className="text-muted-foreground"
        strokeLinecap="round"
      />

      {/* Horse Tail */}
      <path
        d="M45 145 Q35 150, 30 160"
        stroke="currentColor"
        strokeWidth="3"
        className="text-muted-foreground"
        strokeLinecap="round"
        fill="none"
      />
    </svg>
  )
}
