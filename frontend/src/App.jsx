import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import ClassifierView from './components/ClassifierView';
import SearchView from './components/SearchView';
import Footer from './components/Footer';
import { checkHealth } from './api';

export default function App() {
  const [activeTab, setActiveTab] = useState('classify'); // 'classify' | 'search'
  const [healthInfo, setHealthInfo] = useState(null);

  useEffect(() => {
    // Initial health check
    checkHealth()
      .then((data) => setHealthInfo(data))
      .catch((err) => {
        console.warn('API Health Check failed:', err);
        setHealthInfo(null);
      });

    // Periodic poll every 30s
    const timer = setInterval(() => {
      checkHealth()
        .then((data) => setHealthInfo(data))
        .catch(() => setHealthInfo(null));
    }, 30000);

    return () => clearInterval(timer);
  }, []);

  return (
    <div className="app-container">
      <Header
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        healthInfo={healthInfo}
      />

      <main className="main-content">
        {activeTab === 'classify' && <ClassifierView />}
        {activeTab === 'search' && <SearchView />}
      </main>

      <Footer />
    </div>
  );
}
