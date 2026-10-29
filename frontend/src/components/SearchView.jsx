import React, { useState, useEffect } from 'react';
import { searchClauses, getCategories, getContracts } from '../api';
import { getCategoryClass } from '../utils/categoryColors';
import ConfidenceRing from './ConfidenceRing';
import StatusBadge from './StatusBadge';

const STOP_WORDS = new Set(['the', 'and', 'for', 'with', 'from', 'that', 'this', 'any', 'are', 'all', 'shall', 'will', 'who', 'what', 'which']);

const SAMPLE_QUERIES = [
  'governing law of new york',
  'termination for convenience',
  'limitation of liability',
  'non-compete and non-solicitation',
];

function HighlightedClause({ text, query }) {
  if (!query || !query.trim()) {
    return <span className="clause-serif-text">“{text}”</span>;
  }

  const terms = query
    .trim()
    .split(/\s+/)
    .filter((w) => w.length >= 2)
    .map((w) => w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'));

  if (terms.length === 0) {
    return <span className="clause-serif-text">“{text}”</span>;
  }

  const regex = new RegExp(`(${terms.join('|')})`, 'gi');
  const parts = text.split(regex);

  return (
    <span className="clause-serif-text">
      “
      {parts.map((part, i) =>
        regex.test(part) ? (
          <mark key={i} className="search-highlight">
            {part}
          </mark>
        ) : (
          part
        )
      )}
      ”
    </span>
  );
}

export default function SearchView({ defaultContract = null, onBack }) {
  const [query, setQuery] = useState('');
  const [topK, setTopK] = useState(5);
  const [categoryFilter, setCategoryFilter] = useState('');
  const [categories, setCategories] = useState([]);
  const [contracts, setContracts] = useState(defaultContract ? [defaultContract] : []);
  const [contractId, setContractId] = useState(defaultContract?.id || '');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [searchResults, setSearchResults] = useState(null);
  const [copiedIdx, setCopiedIdx] = useState(null);

  useEffect(() => {
    getCategories()
      .then((data) => setCategories(data.categories || []))
      .catch((err) => console.warn('Could not load categories:', err));
    getContracts()
      .then((data) => {
        const list = Array.isArray(data) ? data : [];
        // Keep the just-uploaded contract selectable even if it isn't persisted yet
        if (defaultContract && !list.some((c) => c.id === defaultContract.id)) list.push(defaultContract);
        list.sort((a, b) => String(b.created_at).localeCompare(String(a.created_at)));
        setContracts(list);
      })
      .catch((err) => console.warn('Could not load contracts:', err));
  }, []);

  const selectedContract = contracts.find((c) => c.id === contractId);

  const handleSearch = async (e) => {
    e?.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const data = await searchClauses(query, topK, categoryFilter || null, 0.0, contractId || null);
      setSearchResults(data);
    } catch (err) {
      setError(err.message || 'Search failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleSampleClick = (sampleQuery) => {
    setQuery(sampleQuery);
  };

  const copyClauseText = (text, idx) => {
    navigator.clipboard.writeText(text);
    setCopiedIdx(idx);
    setTimeout(() => setCopiedIdx(null), 2000);
  };

  // Relevance tier word. Cosine scores stay low for short queries against long clauses,
  // so a clause containing every query keyword counts as strong regardless of the score.
  const getRelevanceLabel = (sim, text) => {
    const terms = query
      .toLowerCase()
      .split(/[^a-z0-9]+/)
      .filter((w) => w.length >= 3 && !STOP_WORDS.has(w));
    const lowerText = (text || '').toLowerCase();
    const covered = terms.filter((t) => lowerText.includes(t.replace(/s$/, ''))).length;
    const coverage = terms.length ? covered / terms.length : 0;

    if (sim >= 0.30 || coverage === 1) return { label: 'Strong match', className: 'rel-strong' };
    if (sim >= 0.15 || coverage >= 0.5) return { label: 'Fair match', className: 'rel-fair' };
    return { label: 'Weak match', className: 'rel-weak' };
  };

  return (
    <div className="view-container">
      {/* Hero Section */}
      {onBack && (
        <button type="button" className="back-link-btn" onClick={onBack}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
            <line x1="19" y1="12" x2="5" y2="12" />
            <polyline points="12 19 5 12 12 5" />
          </svg>
          <span>{defaultContract ? `Back to ${defaultContract.document_name} results` : 'Back to Classify'}</span>
        </button>
      )}

      <div className="hero-section">
        <h1 className="hero-title">
          {selectedContract ? 'Search your contract' : 'Search the CUAD clause library'}
        </h1>
        <p className="hero-subtitle">
          Ask in your own words. Results are ranked by similarity.
        </p>
        <div className="search-scope-pill">
          <span className="scope-dot"></span>
          <span>
            {selectedContract
              ? `Scope: ${selectedContract.document_name} (${selectedContract.total_clauses} clauses)`
              : 'Scope: 12,204 curated CUAD training clauses'}
          </span>
        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <div className="alert alert-error" role="alert">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
            <circle cx="12" cy="12" r="10" />
            <line x1="12" y1="8" x2="12" y2="12" />
            <line x1="12" y1="16" x2="12.01" y2="16" />
          </svg>
          <span>{error}</span>
        </div>
      )}

      {/* Main Search Input Card */}
      <div className="card search-box-card">
        <form onSubmit={handleSearch}>
          <div className="search-bar-row">
            <div className="search-input-wrapper">
              <svg className="search-input-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                <circle cx="11" cy="11" r="8" />
                <line x1="21" y1="21" x2="16.65" y2="16.65" />
              </svg>
              <input
                type="text"
                className="search-large-input"
                placeholder="Ask in your own words, e.g. 'termination for convenience'…"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                aria-label="Search clauses"
              />
              {query && (
                <button
                  type="button"
                  className="btn-clear-search"
                  onClick={() => {
                    setQuery('');
                    setSearchResults(null);
                  }}
                  title="Clear query"
                  aria-label="Clear query"
                >
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                    <line x1="18" y1="6" x2="6" y2="18" />
                    <line x1="6" y1="6" x2="18" y2="18" />
                  </svg>
                </button>
              )}
            </div>

            <button
              type="submit"
              className="btn-primary search-btn-main"
              disabled={loading || !query.trim()}
            >
              {loading ? (
                <>
                  <span className="spinner" aria-hidden="true"></span>
                  <span>Searching…</span>
                </>
              ) : (
                <span>Search</span>
              )}
            </button>
          </div>

          {/* Filters Row */}
          <div className="search-filters-row">
            <div className="filter-item">
              <label htmlFor="search-contract-scope" className="filter-label">
                Search In
              </label>
              <select
                id="search-contract-scope"
                className="select-input"
                value={contractId}
                onChange={(e) => {
                  setContractId(e.target.value);
                  setSearchResults(null);
                }}
              >
                <option value="">CUAD clause library</option>
                {contracts.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.document_name} · {c.total_clauses} clauses · {String(c.created_at).slice(0, 16).replace('T', ' ')}
                  </option>
                ))}
              </select>
            </div>

            <div className="filter-item">
              <label htmlFor="search-cat-filter" className="filter-label">
                Category Filter
              </label>
              <select
                id="search-cat-filter"
                className="select-input"
                value={categoryFilter}
                onChange={(e) => setCategoryFilter(e.target.value)}
              >
                <option value="">All 41 Categories</option>
                {categories.map((cat) => (
                  <option key={cat} value={cat}>
                    {cat}
                  </option>
                ))}
              </select>
            </div>

            <div className="filter-item-sm">
              <label htmlFor="search-top-k" className="filter-label">
                Results Limit
              </label>
              <select
                id="search-top-k"
                className="select-input"
                value={topK}
                onChange={(e) => setTopK(Number(e.target.value))}
              >
                <option value={5}>5 results</option>
                <option value={10}>10 results</option>
                <option value={20}>20 results</option>
              </select>
            </div>
          </div>

          {/* Quick Try Queries */}
          <div className="sample-queries-bar">
            <span className="sample-chips-label">Try:</span>
            <div className="sample-chips-list">
              {SAMPLE_QUERIES.map((sq) => (
                <button
                  key={sq}
                  type="button"
                  className="chip-btn"
                  onClick={() => handleSampleClick(sq)}
                >
                  {sq}
                </button>
              ))}
            </div>
          </div>
        </form>
      </div>

      {/* Loading Skeleton */}
      {loading && (
        <div className="skeleton-container" aria-label="Loading search results" role="status">
          {[1, 2, 3].map((n) => (
            <div key={n} className="skeleton-card">
              <div className="skeleton-line sm" style={{ width: '30%' }}></div>
              <div className="skeleton-line" style={{ width: '90%' }}></div>
              <div className="skeleton-line" style={{ width: '75%' }}></div>
              <div className="skeleton-line sm" style={{ width: '20%' }}></div>
            </div>
          ))}
        </div>
      )}

      {/* Search Results Display */}
      {!loading && searchResults && (
        <div className="results-container" role="region" aria-live="polite">
          <div className="results-summary-bar">
            <h3 className="results-heading">
              Search Results
            </h3>
            <span className="results-count-badge">
              {searchResults.results?.length || 0} {searchResults.results?.length === 1 ? 'clause' : 'clauses'} found
            </span>
          </div>

          {/* Empty State */}
          {(!searchResults.results || searchResults.results.length === 0) ? (
            <div className="empty-state-card">
              <div className="empty-state-icon">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                  <circle cx="11" cy="11" r="8" />
                  <line x1="21" y1="21" x2="16.65" y2="16.65" />
                  <line x1="8" y1="11" x2="14" y2="11" />
                </svg>
              </div>
              <h4 className="empty-state-title">No clauses matched</h4>
              <p className="empty-state-text">
                Try fewer or different keywords, or reset the category filter to search across all 41 categories.
              </p>
            </div>
          ) : (
            <div className="results-list">
              {searchResults.results.map((item, idx) => {
                const sim = Number(item.similarity_score) || 0;
                const simPct = (sim * 100).toFixed(1);
                const rel = getRelevanceLabel(sim, item.clause_text);
                const modelConf = item.classification_confidence;

                return (
                  <div key={idx} className="result-card-item">
                    <div className="result-item-header">
                      <div className="result-item-tags">
                        <span className="rank-tag">#{item.rank || idx + 1}</span>
                        <span className={`category-tag ${getCategoryClass(item.predicted_category)}`}>
                          {item.predicted_category}
                        </span>
                        {item.confidence_status && <StatusBadge status={item.confidence_status} />}
                      </div>

                      {modelConf != null && (
                        <div className="clause-row-right" title="Model confidence: the same score shown on the Classify page">
                          <ConfidenceRing score={Number(modelConf)} status={item.confidence_status} size="sm" />
                          <span className="clause-row-pct">{(Number(modelConf) * 100).toFixed(1)}%</span>
                        </div>
                      )}
                    </div>

                    <div className="result-item-body">
                      <HighlightedClause text={item.clause_text} query={query} />
                    </div>

                    <div className="result-item-footer">
                      <span className="source-contract-name">
                        Source contract: <code>{item.source_contract || 'CUAD Document'}</code>
                        <span className="query-match-note" title="Cosine similarity between your query and this clause; used to rank results">
                          <span className={`relevance-badge ${rel.className}`}>{rel.label}</span>
                          Query match {simPct}%
                        </span>
                      </span>
                      <button
                        type="button"
                        className="btn-text-link"
                        onClick={() => copyClauseText(item.clause_text, idx)}
                      >
                        {copiedIdx === idx ? 'Copied!' : 'Copy clause'}
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
