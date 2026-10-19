import React from 'react';

/**
 * Animated SVG circular confidence ring
 * size: 'lg' (72px) | 'sm' (28px)
 * score: 0.0 to 1.0
 * status: 'High confidence' | 'Moderate confidence' | 'Low confidence' | 'Out of supported category scope'
 */
export default function ConfidenceRing({ score = 0, status = '', size = 'lg' }) {
  const isLarge = size === 'lg';
  const diameter = isLarge ? 72 : 28;
  const strokeWidth = isLarge ? 7 : 3.5;
  const radius = (diameter - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;

  // Clamp score between 0 and 1
  const validScore = Number.isFinite(score) ? Math.max(0, Math.min(1, score)) : 0;
  const strokeDashoffset = circumference * (1 - validScore);
  const percentageText = `${(validScore * 100).toFixed(isLarge ? 1 : 0)}%`;

  // Semantic color selection
  let strokeColor = 'var(--primary)';
  const s = (status || '').toLowerCase();
  if (s.includes('high')) {
    strokeColor = 'var(--success)';
  } else if (s.includes('moderate')) {
    strokeColor = 'var(--primary)';
  } else if (s.includes('low')) {
    strokeColor = 'var(--warning)';
  } else if (s.includes('scope') || s.includes('out')) {
    strokeColor = 'var(--text-muted)';
  }

  return (
    <div
      className={`confidence-ring-container ring-${size}`}
      style={{ width: diameter, height: diameter }}
      title={`Confidence: ${percentageText} (${status || 'Estimated'})`}
      role="img"
      aria-label={`Confidence ${percentageText}, ${status}`}
    >
      <svg
        width={diameter}
        height={diameter}
        viewBox={`0 0 ${diameter} ${diameter}`}
        className="confidence-ring-svg"
      >
        {/* Track circle */}
        <circle
          cx={diameter / 2}
          cy={diameter / 2}
          r={radius}
          fill="none"
          stroke="var(--bg-surface)"
          strokeWidth={strokeWidth}
        />
        {/* Progress ring */}
        <circle
          cx={diameter / 2}
          cy={diameter / 2}
          r={radius}
          fill="none"
          stroke={strokeColor}
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          strokeLinecap="round"
          className="confidence-ring-circle"
          transform={`rotate(-90 ${diameter / 2} ${diameter / 2})`}
        />
      </svg>
      {isLarge && (
        <span className="confidence-ring-text">
          {percentageText}
        </span>
      )}
    </div>
  );
}
