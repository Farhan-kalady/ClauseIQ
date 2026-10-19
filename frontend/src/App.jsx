import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import OfflineBanner from './components/OfflineBanner';
import ClassifierView from './components/ClassifierView';
import SearchView from './components/SearchView';
import Footer from './components/Footer';
import { checkHealth } from './api';

export default function App() {
  const [activeTab, setActiveTab] = useState('classify'); // 'classify' | 'search'
  const [healthInfo, setHealthInfo] = useState(null);
  const [isRetrying, setIsRetrying] = useState(false);

  // Theme Management
  const [theme, setTheme] = useState(() => {
    const saved = localStorage.getItem('clauseiq-theme');
    if (saved) return saved;
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      return 'dark';
    }
    return 'light';
  });

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('clauseiq-theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme((prev) => (prev === 'dark' ? 'light' : 'dark'));
  };

  const fetchHealth = async () => {
    try {
      const data = await checkHealth();
      setHealthInfo(data);
    } catch (err) {
      console.warn('API Health Check failed:', err);
      setHealthInfo(null);
    }
  };

  useEffect(() => {
    fetchHealth();
    const timer = setInterval(fetchHealth, 30000);
    return () => clearInterval(timer);
  }, []);

  const handleRetryHealth = async () => {
    setIsRetrying(true);
    await fetchHealth();
    setIsRetrying(false);
  };

  return (
    <div className="app-container">
      <Header
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        healthInfo={healthInfo}
        theme={theme}
        onToggleTheme={toggleTheme}
      />

      {/* Offline Banner displayed if backend is unreachable */}
      {healthInfo === null && (
        <OfflineBanner onRetry={handleRetryHealth} isRetrying={isRetrying} />
      )}

      <main className="main-content" id="main-content">
        {activeTab === 'classify' && <ClassifierView />}
        {activeTab === 'search' && <SearchView />}
      </main>

      {/* Mobile Bottom Tab Bar */}
      <nav className="mobile-bottom-nav" aria-label="Mobile Navigation">
        <button
          type="button"
          className={`mobile-nav-btn ${activeTab === 'classify' ? 'active' : ''}`}
          onClick={() => setActiveTab('classify')}
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
            <polyline points="14 2 14 8 20 8" />
            <line x1="16" y1="13" x2="8" y2="13" />
            <line x1="16" y1="17" x2="8" y2="17" />
          </svg>
          <span>Classify</span>
        </button>
        <button
          type="button"
          className={`mobile-nav-btn ${activeTab === 'search' ? 'active' : ''}`}
          onClick={() => setActiveTab('search')}
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
            <circle cx="11" cy="11" r="8" />
            <line x1="21" y1="21" x2="16.65" y2="16.65" />
          </svg>
          <span>Search</span>
        </button>
      </nav>

      <Footer />
    </div>
  );
}
