import React from 'react';

/**
 * StatusBadge component showing:
 * - Deterministic semantic color
 * - Inline SVG icon
 * - Plain language label
 */
export default function StatusBadge({ status }) {
  if (!status) return null;

  const s = status.toLowerCase();

  if (s.includes('high')) {
    return (
      <span className="status-badge badge-high" title="High confidence prediction">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
          <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
          <polyline points="22 4 12 14.01 9 11.01" />
        </svg>
        <span>High confidence</span>
      </span>
    );
  }

  if (s.includes('moderate')) {
    return (
      <span className="status-badge badge-moderate" title="Moderate confidence prediction">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
          <circle cx="12" cy="12" r="10" />
          <path d="M12 14v-4" />
          <path d="m14 14-2-4" />
        </svg>
        <span>Moderate confidence</span>
      </span>
    );
  }

  if (s.includes('low')) {
    return (
      <span className="status-badge badge-low" title="Low confidence - human review required">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
          <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
          <circle cx="12" cy="12" r="3" />
        </svg>
        <span>Low – review required</span>
      </span>
    );
  }

  if (s.includes('scope') || s.includes('outside') || s.includes('out of')) {
    return (
      <span className="status-badge badge-neutral" title="Clause is outside supported category scope">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
          <circle cx="12" cy="12" r="10" />
          <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3" />
          <line x1="12" y1="17" x2="12.01" y2="17" />
        </svg>
        <span>Outside supported categories</span>
      </span>
    );
  }

  return (
    <span className="status-badge badge-neutral">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
        <circle cx="12" cy="12" r="10" />
        <line x1="12" y1="16" x2="12" y2="12" />
        <line x1="12" y1="8" x2="12.01" y2="8" />
      </svg>
      <span>{status}</span>
    </span>
  );
}
