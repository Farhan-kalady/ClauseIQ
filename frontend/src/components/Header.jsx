import React from 'react';

export default function Header({ activeTab, setActiveTab, healthInfo }) {
  return (
    <header className="navbar">
      <div className="nav-container">
        <div className="logo-group">
          <div className="logo-icon">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
              <polyline points="14 2 14 8 20 8" />
              <line x1="16" y1="13" x2="8" y2="13" />
              <line x1="16" y1="17" x2="8" y2="17" />
              <polyline points="10 9 9 9 8 9" />
            </svg>
          </div>
          <div className="logo-text">
            <div style={{ display: 'flex', alignItems: 'center' }}>
              <h1>ClauseIQ</h1>
              <span className="logo-badge">Sprint 3</span>
            </div>
            <p style={{ fontSize: '0.725rem', color: 'var(--text-muted)' }}>
              CUAD v1 Legal Intelligence System
            </p>
          </div>
        </div>

        <nav className="nav-tabs">
          <button
            className={`nav-tab-btn ${activeTab === 'classify' ? 'active' : ''}`}
            onClick={() => setActiveTab('classify')}
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
              <line x1="9" y1="3" x2="9" y2="21"/>
            </svg>
            Classification
          </button>
          <button
            className={`nav-tab-btn ${activeTab === 'search' ? 'active' : ''}`}
            onClick={() => setActiveTab('search')}
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="11" cy="11" r="8"/>
              <line x1="21" y1="21" x2="16.65" y2="16.65"/>
            </svg>
            Clause Search
          </button>
        </nav>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          {healthInfo ? (
            <div className={`status-pill ${healthInfo.model_loaded ? '' : 'error'}`} title={healthInfo.supabase_connected ? 'Supabase Connected' : 'Local Mode (Supabase Offline)'}>
              <span className="status-dot"></span>
              <span>{healthInfo.model_loaded ? 'Model Ready' : 'Loading Model'}</span>
              {healthInfo.supabase_connected && (
                <span style={{ fontSize: '0.65rem', opacity: 0.8 }}>• DB Active</span>
              )}
            </div>
          ) : (
            <div className="status-pill error">
              <span className="status-dot"></span>
              <span>Backend Offline</span>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
