import React, { useState, useEffect } from 'react';

export default function Header({ activeTab, setActiveTab, healthInfo, theme, onToggleTheme }) {
  const [showTooltip, setShowTooltip] = useState(false);

  const isOffline = healthInfo === null;
  const isInitializing = healthInfo && !healthInfo.model_loaded;
  const isReady = healthInfo && healthInfo.model_loaded;

  return (
    <header className="navbar" role="banner">
      <div className="nav-container">
        {/* Brand Logo & Wordmark */}
        <div className="logo-group" tabIndex={0} aria-label="ClauseIQ Home">
          <div className="logo-icon-gradient">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
              <polyline points="14 2 14 8 20 8" />
              {/* Highlighted clause line */}
              <line x1="8" y1="13" x2="16" y2="13" stroke="#FEF08A" strokeWidth="2.8" />
              <line x1="8" y1="17" x2="14" y2="17" />
            </svg>
          </div>
          <div className="logo-text">
            <span className="logo-wordmark">Clause<span className="logo-iq-gradient">IQ</span></span>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="nav-tabs-segmented" role="tablist" aria-label="Main Navigation">
          <button
            type="button"
            role="tab"
            aria-selected={activeTab === 'classify'}
            className={`nav-segmented-btn ${activeTab === 'classify' ? 'active' : ''}`}
            onClick={() => setActiveTab('classify')}
          >
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
              <polyline points="14 2 14 8 20 8" />
              <line x1="16" y1="13" x2="8" y2="13" />
              <line x1="16" y1="17" x2="8" y2="17" />
            </svg>
            <span>Classify</span>
          </button>
          <button
            type="button"
            role="tab"
            aria-selected={activeTab === 'search'}
            className={`nav-segmented-btn ${activeTab === 'search' ? 'active' : ''}`}
            onClick={() => setActiveTab('search')}
          >
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
              <circle cx="11" cy="11" r="8" />
              <line x1="21" y1="21" x2="16.65" y2="16.65" />
            </svg>
            <span>Search</span>
          </button>
        </nav>

        {/* Right Section: Status Pill & Theme Toggle */}
        <div className="header-right">
          {/* Status Pill with Tooltip */}
          <div
            className="status-pill-container"
            onMouseEnter={() => setShowTooltip(true)}
            onMouseLeave={() => setShowTooltip(false)}
            onFocus={() => setShowTooltip(true)}
            onBlur={() => setShowTooltip(false)}
            tabIndex={0}
            role="status"
            aria-label={isReady ? 'System Ready' : (isInitializing ? 'System Initializing' : 'System Offline')}
          >
            <div className={`status-pill ${isReady ? 'status-ready' : (isInitializing ? 'status-init' : 'status-offline')}`}>
              <span className={`status-dot ${isInitializing ? 'dot-pulse' : ''}`}></span>
              <span className="status-label">
                {isReady ? 'System Ready' : (isInitializing ? 'System Initializing' : 'System Offline')}
              </span>
            </div>

            {/* Status Tooltip */}
            {showTooltip && (
              <div className="status-tooltip" role="tooltip">
                <div className="tooltip-title">System Status</div>
                <div className="tooltip-row">
                  <span className="tooltip-label">Model:</span>
                  <span className="tooltip-val">{healthInfo?.model_name || (isOffline ? 'Unavailable' : 'Loading')}</span>
                </div>
                <div className="tooltip-row">
                  <span className="tooltip-label">Search Index:</span>
                  <span className="tooltip-val">{healthInfo?.search_index_size ? `${healthInfo.search_index_size} clauses` : (isOffline ? 'Unavailable' : 'Loading')}</span>
                </div>
                <div className="tooltip-row">
                  <span className="tooltip-label">Database:</span>
                  <span className="tooltip-val">{healthInfo?.supabase_connected ? 'Connected' : 'Offline / Standalone'}</span>
                </div>
              </div>
            )}
          </div>

          {/* Theme Toggle Button */}
          <button
            type="button"
            className="btn-theme-toggle"
            onClick={onToggleTheme}
            title={theme === 'dark' ? 'Switch to Light theme' : 'Switch to Dark theme'}
            aria-label="Toggle visual theme"
          >
            {theme === 'dark' ? (
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                <circle cx="12" cy="12" r="5" />
                <line x1="12" y1="1" x2="12" y2="3" />
                <line x1="12" y1="21" x2="12" y2="23" />
                <line x1="4.22" y1="4.22" x2="5.64" y2="5.64" />
                <line x1="18.36" y1="18.36" x2="19.78" y2="19.78" />
                <line x1="1" y1="12" x2="3" y2="12" />
                <line x1="21" y1="12" x2="23" y2="12" />
                <line x1="4.22" y1="19.78" x2="5.64" y2="18.36" />
                <line x1="18.36" y1="5.64" x2="19.78" y2="4.22" />
              </svg>
            ) : (
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
              </svg>
            )}
          </button>
        </div>
      </div>
    </header>
  );
}
