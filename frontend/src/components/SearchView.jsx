import React, { useState, useEffect } from 'react';
import { searchClauses, getCategories } from '../api';

const SAMPLE_QUERIES = [
  'termination for convenience',
  'governing law of new york',
  'confidentiality obligation duration',
  'limitation of liability and indemnification',
];

export default function SearchView() {
  const [query, setQuery] = useState('');
  const [topK, setTopK] = useState(5);
  const [categoryFilter, setCategoryFilter] = useState('');
  const [categories, setCategories] = useState([]);
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [searchResults, setSearchResults] = useState(null);

  // Load available 41 CUAD categories on mount
  useEffect(() => {
    getCategories()
      .then((data) => setCategories(data.categories || []))
      .catch((err) => console.warn('Could not load categories:', err));
  }, []);

  const handleSearch = async (e) => {
    e?.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const data = await searchClauses(query, topK, categoryFilter || null);
      setSearchResults(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSampleClick = (sampleQuery) => {
    setQuery(sampleQuery);
  };

  return (
    <div>
      <div className="section-header">
        <h2 className="section-title">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ color: 'var(--accent-purple)' }}>
            <circle cx="11" cy="11" r="8"/>
            <line x1="21" y1="21" x2="16.65" y2="16.65"/>
          </svg>
          Intelligent Clause Search
        </h2>
        <p className="section-subtitle">
          Query 12,204 pre-indexed contract clauses using classical TF-IDF Vectorization and Cosine Similarity ranking.
        </p>
      </div>

      {error && (
        <div className="alert alert-error">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
          </svg>
          <span>{error}</span>
        </div>
      )}

      {/* Search Input Card */}
      <div className="glass-card">
        <form onSubmit={handleSearch}>
          <div className="form-group">
            <label className="form-label">
              Search Query
            </label>
            <div style={{ display: 'flex', gap: '0.75rem' }}>
              <input
                type="text"
                className="text-input"
                placeholder="Enter legal terms or clause requirements (e.g., 'termination for convenience')..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
              />
              <button
                type="submit"
                className="btn-primary"
                disabled={loading || !query.trim()}
                style={{ flexShrink: 0 }}
              >
                {loading && <span className="spinner"></span>}
                {loading ? 'Searching...' : 'Search'}
              </button>
            </div>
          </div>

          {/* Quick Query Pills */}
          <div style={{ marginBottom: '1.25rem' }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.4rem' }}>
              Example queries:
            </span>
            <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
              {SAMPLE_QUERIES.map((q) => (
                <button
                  key={q}
                  type="button"
                  className="btn-secondary"
                  style={{ fontSize: '0.75rem', padding: '0.3rem 0.65rem' }}
                  onClick={() => handleSampleClick(q)}
                >
                  {q}
                </button>
              ))}
            </div>
          </div>

          {/* Search Controls (Top-K & Category Filter) */}
          <div className="grid-2" style={{ paddingTop: '0.75rem', borderTop: '1px solid var(--border-color)' }}>
            <div>
              <label className="form-label" style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span>Top Results (k)</span>
                <strong style={{ color: 'var(--accent-cyan)' }}>{topK}</strong>
              </label>
              <input
                type="range"
                min="1"
                max="25"
                value={topK}
                onChange={(e) => setTopK(Number(e.target.value))}
                style={{ width: '100%', accentColor: 'var(--accent-blue)', cursor: 'pointer' }}
              />
            </div>

            <div>
              <label className="form-label">
                Optional Category Filter
              </label>
              <select
                className="select-input"
                value={categoryFilter}
                onChange={(e) => setCategoryFilter(e.target.value)}
              >
                <option value="">All Categories (No filter)</option>
                {categories.map((cat) => (
                  <option key={cat} value={cat}>
                    {cat}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </form>
      </div>

      {/* Results Section */}
      {searchResults && (
        <div style={{ marginTop: '2rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 600 }}>
              Search Results
            </h3>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              Found <strong>{searchResults.total_results}</strong> relevant clauses for &ldquo;{searchResults.query}&rdquo;
            </span>
          </div>

          {searchResults.results.length === 0 ? (
            <div className="glass-card" style={{ textAlign: 'center', padding: '3rem 1.5rem', color: 'var(--text-muted)' }}>
              <p>No matching clauses met the query and filter criteria.</p>
              <span style={{ fontSize: '0.8rem' }}>Try broadening your search term or clearing the category filter.</span>
            </div>
          ) : (
            <div className="search-results-list">
              {searchResults.results.map((item) => (
                <div key={item.rank} className="search-item">
                  <div className="search-item-header">
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                      <span className="search-item-rank">Rank #{item.rank}</span>
                      <span className="category-badge">{item.predicted_category}</span>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
                      <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Cosine Similarity:</span>
                      <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.85rem', fontWeight: 700, color: 'var(--accent-cyan)' }}>
                        {(item.similarity_score * 100).toFixed(1)}%
                      </span>
                    </div>
                  </div>

                  <p className="search-item-text">
                    {item.clause_text}
                  </p>

                  <div className="search-item-footer">
                    <span>
                      Contract Source: <strong style={{ color: 'var(--text-secondary)' }}>{item.source_contract}</strong>
                    </span>
                    {item.true_category && item.true_category !== item.predicted_category && (
                      <span style={{ fontSize: '0.7rem' }}>
                        Annotated Label: {item.true_category}
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
