import React, { useState, useMemo, useEffect } from 'react';
import { classifyClause, classifyFile } from '../api';
import { getCategoryClass } from '../utils/categoryColors';
import ConfidenceRing from './ConfidenceRing';
import StatusBadge from './StatusBadge';

const SAMPLE_CLAUSES = [
  {
    label: 'Governing Law',
    text: 'This Agreement and any dispute arising from the performance hereof shall be governed by and construed in accordance with the laws of the State of Delaware.',
  },
  {
    label: 'Cap On Liability',
    text: "In no event shall either party's aggregate liability arising out of or relating to this Agreement exceed the total fees paid by Customer during the twelve (12) months preceding the claim.",
  },
  {
    label: 'Termination',
    text: 'Either party may terminate this Agreement without cause upon providing thirty (30) days prior written notice to the other party.',
  },
  {
    label: 'Non-Compete',
    text: 'Neither party shall, during the term of this Agreement and for one (1) year after its termination, directly or indirectly engage in or own any interest in any business that competes with the other party in the Territory.',
  },
];

const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10 MB

export default function ClassifierView({ onContractUploaded }) {
  const [inputMode, setInputMode] = useState('text'); // 'text' | 'file'
  const [clauseText, setClauseText] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [copiedCategory, setCopiedCategory] = useState(false);
  const [copiedClauseIdx, setCopiedClauseIdx] = useState(null);

  // Single Result State
  const [textResult, setTextResult] = useState(null);
  const [showAlternatives, setShowAlternatives] = useState(false);

  // Document Result State
  const [docResult, setDocResult] = useState(null);
  const [processingStep, setProcessingStep] = useState(1); // 1: Reading file, 2: Finding clauses, 3: Classifying
  const [categoryFilter, setCategoryFilter] = useState('ALL');
  const [sortOrder, setSortOrder] = useState('highest'); // 'highest' | 'original' | 'lowest'
  const [currentPage, setCurrentPage] = useState(1);
  const [expandedClauses, setExpandedClauses] = useState({});
  const clausesPerPage = 6;

  // Timed 3-step progress strip during document processing
  useEffect(() => {
    let timer1, timer2;
    if (loading && inputMode === 'file') {
      setProcessingStep(1);
      timer1 = setTimeout(() => setProcessingStep(2), 1200);
      timer2 = setTimeout(() => setProcessingStep(3), 2800);
    } else {
      setProcessingStep(1);
    }
    return () => {
      clearTimeout(timer1);
      clearTimeout(timer2);
    };
  }, [loading, inputMode]);

  const handleClassifyText = async (e) => {
    e?.preventDefault();
    if (!clauseText.trim()) return;

    setLoading(true);
    setError(null);
    setTextResult(null);
    setShowAlternatives(false);

    try {
      const data = await classifyClause(clauseText);
      setTextResult(data);
    } catch (err) {
      setError(err.message || 'Classification request failed.');
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e) => {
    e?.preventDefault();
    if (!selectedFile) return;

    setLoading(true);
    setError(null);
    setDocResult(null);
    setCategoryFilter('ALL');
    setSortOrder('highest');
    setCurrentPage(1);

    try {
      const data = await classifyFile(selectedFile);
      setDocResult(data);
      onContractUploaded?.({
        id: data.contract_id,
        document_name: data.document_name,
        total_clauses: data.total_clauses,
        created_at: new Date().toISOString(),
      });
    } catch (err) {
      setError(err.message || 'Document classification failed.');
    } finally {
      setLoading(false);
    }
  };

  const validateAndSetFile = (file) => {
    if (!file) return;
    const ext = file.name.split('.').pop().toLowerCase();
    if (ext !== 'pdf' && ext !== 'txt') {
      setError('Please choose a PDF (.pdf) or text (.txt) file.');
      setSelectedFile(null);
      return;
    }
    if (file.size > MAX_FILE_SIZE) {
      setError('File exceeds maximum allowed size of 10 MB.');
      setSelectedFile(null);
      return;
    }
    setError(null);
    setSelectedFile(file);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndSetFile(e.dataTransfer.files[0]);
    }
  };

  const handleLoadSample = (sample) => {
    setClauseText(sample.text);
    setTextResult(null);
    setError(null);
  };

  const copyToClipboard = (text, isClause = false, idx = null) => {
    if (!text) return;
    navigator.clipboard.writeText(text);
    if (isClause) {
      setCopiedClauseIdx(idx);
      setTimeout(() => setCopiedClauseIdx(null), 2000);
    } else {
      setCopiedCategory(true);
      setTimeout(() => setCopiedCategory(false), 2000);
    }
  };

  const toggleClauseExpand = (idx) => {
    setExpandedClauses((prev) => ({
      ...prev,
      [idx]: !prev[idx],
    }));
  };

  // Helper for numeric confidence
  const getClauseConfidence = (clause) => {
    if (!clause) return 0;
    const val = clause.confidence ?? clause.confidence_score;
    if (typeof val === 'number') return val > 1 ? val / 100 : val;
    if (typeof val === 'string') {
      const parsed = parseFloat(val.replace('%', ''));
      return Number.isFinite(parsed) ? (parsed > 1 ? parsed / 100 : parsed) : 0;
    }
    return 0;
  };

  // Summary statistics for document results
  const summaryStats = useMemo(() => {
    if (!docResult?.clauses) return { high: 0, moderate: 0, low: 0, outOfScope: 0 };
    let high = 0, moderate = 0, low = 0, outOfScope = 0;
    for (const c of docResult.clauses) {
      const s = (c.confidence_status || '').toLowerCase();
      if (s.includes('high')) high++;
      else if (s.includes('moderate')) moderate++;
      else if (s.includes('low')) low++;
      else outOfScope++;
    }
    return { high, moderate, low, outOfScope };
  }, [docResult]);

  // Unique categories in document for filter dropdown
  const uniqueDocCategories = useMemo(() => {
    if (!docResult?.clauses) return [];
    const counts = {};
    for (const c of docResult.clauses) {
      const cat = c.predicted_category || 'Unknown';
      counts[cat] = (counts[cat] || 0) + 1;
    }
    return Object.entries(counts).sort((a, b) => b[1] - a[1]);
  }, [docResult]);

  // Filter and sort document clauses (front-end only)
  const filteredAndSortedClauses = useMemo(() => {
    if (!docResult?.clauses) return [];
    let list = [...docResult.clauses];

    // Filter by category
    if (categoryFilter !== 'ALL') {
      list = list.filter((c) => c.predicted_category === categoryFilter);
    }

    // Sort
    if (sortOrder === 'highest') {
      list.sort((a, b) => getClauseConfidence(b) - getClauseConfidence(a));
    } else if (sortOrder === 'lowest') {
      list.sort((a, b) => getClauseConfidence(a) - getClauseConfidence(b));
    } else {
      list.sort((a, b) => (a.clause_index || 0) - (b.clause_index || 0));
    }

    return list;
  }, [docResult, categoryFilter, sortOrder]);

  const totalFilteredClauses = filteredAndSortedClauses.length;
  const totalPages = Math.ceil(totalFilteredClauses / clausesPerPage) || 1;
  const displayedClauses = filteredAndSortedClauses.slice(
    (currentPage - 1) * clausesPerPage,
    currentPage * clausesPerPage
  );

  return (
    <div className="view-container">
      {/* Hero Section */}
      <div className="hero-section">
        <h1 className="hero-title">Find the clause that matters.</h1>
        <p className="hero-subtitle">
          Classify contract clauses into 41 legal categories in seconds.
        </p>
      </div>

      {/* Segmented Mode Control */}
      <div className="segmented-track" role="tablist" aria-label="Input Mode Switcher">
        <button
          type="button"
          role="tab"
          aria-selected={inputMode === 'text'}
          className={`segment-tab ${inputMode === 'text' ? 'active' : ''}`}
          onClick={() => {
            setInputMode('text');
            setError(null);
          }}
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
            <line x1="17" y1="10" x2="3" y2="10" />
            <line x1="21" y1="6" x2="3" y2="6" />
            <line x1="21" y1="14" x2="3" y2="14" />
            <line x1="17" y1="18" x2="3" y2="18" />
          </svg>
          <span>Paste a clause</span>
        </button>
        <button
          type="button"
          role="tab"
          aria-selected={inputMode === 'file'}
          className={`segment-tab ${inputMode === 'file' ? 'active' : ''}`}
          onClick={() => {
            setInputMode('file');
            setError(null);
          }}
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
            <polyline points="14 2 14 8 20 8" />
            <line x1="12" y1="18" x2="12" y2="12" />
            <polyline points="9 15 12 12 15 15" />
          </svg>
          <span>Upload a contract</span>
        </button>
      </div>

      {/* Inline Alert / Error */}
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

      {/* MODE A: Direct Clause Text Input */}
      {inputMode === 'text' && (
        <div className="card">
          <form onSubmit={handleClassifyText}>
            <div className="form-group">
              <div className="form-label-row">
                <label htmlFor="clause-text-input" className="form-label">
                  Clause text
                </label>
                <span className="char-counter" aria-live="polite">
                  {clauseText.length} characters
                </span>
              </div>
              <textarea
                id="clause-text-input"
                className="clause-textarea"
                placeholder="Paste a contract clause here…"
                value={clauseText}
                onChange={(e) => setClauseText(e.target.value)}
                rows={6}
                aria-required="true"
              />
            </div>

            {/* Quick Example Chips */}
            <div className="sample-chips-row">
              <span className="sample-chips-label">Try an example:</span>
              <div className="sample-chips-list">
                {SAMPLE_CLAUSES.map((sample) => (
                  <button
                    key={sample.label}
                    type="button"
                    className="chip-btn"
                    onClick={() => handleLoadSample(sample)}
                  >
                    {sample.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Form Actions */}
            <div className="form-action-row">
              {clauseText && (
                <button
                  type="button"
                  className="btn-ghost"
                  onClick={() => {
                    setClauseText('');
                    setTextResult(null);
                    setError(null);
                  }}
                >
                  Clear
                </button>
              )}
              <button
                type="submit"
                className="btn-primary"
                disabled={loading || !clauseText.trim()}
              >
                {loading ? (
                  <>
                    <span className="spinner" aria-hidden="true"></span>
                    <span>Classifying…</span>
                  </>
                ) : (
                  <>
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                      <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
                    </svg>
                    <span>Classify clause</span>
                  </>
                )}
              </button>
            </div>
          </form>

          {/* Single Result Card */}
          {textResult && (
            <div className="single-result-card" role="region" aria-live="polite">
              <div className="result-card-header">
                <span className="result-card-kicker">RESULT</span>
                <StatusBadge status={textResult.confidence_status} />
              </div>

              {/* Original Clause Text in Serif */}
              <blockquote className="result-clause-quote">
                “{clauseText.trim()}”
              </blockquote>

              <div className="result-columns-grid">
                {/* Left Column: Category */}
                <div className="result-col-category">
                  <span className="result-col-label">Predicted category</span>
                  <div className={`category-tag category-tag-lg ${getCategoryClass(textResult.predicted_category)}`}>
                    {textResult.predicted_category}
                  </div>
                </div>

                {/* Right Column: Confidence Gauge */}
                <div className="result-col-confidence">
                  <span className="result-col-label">Confidence</span>
                  <div className="confidence-gauge-row">
                    <ConfidenceRing
                      score={textResult.confidence ?? 0}
                      status={textResult.confidence_status}
                      size="lg"
                    />
                    <div className="confidence-gauge-details">
                      <p className="confidence-honesty-note">
                        Estimate from the model – not a guarantee of correctness.
                      </p>
                      {(textResult.confidence ?? 0) < 0.25 && (
                        <p className="confidence-honesty-note scope-hint">
                          Low confidence usually means this clause type is not one of the 41 CUAD
                          categories (e.g. Confidentiality, Indemnification, Force Majeure, Payment
                          Terms are not included), so no category fits well.
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              </div>

              {/* Collapsible Alternatives */}
              {textResult.alternatives && textResult.alternatives.length > 0 && (
                <div className="alternatives-wrapper">
                  <button
                    type="button"
                    className="alternatives-toggle-btn"
                    onClick={() => setShowAlternatives(!showAlternatives)}
                    aria-expanded={showAlternatives}
                  >
                    <span>Other possibilities ({textResult.alternatives.length})</span>
                    <svg
                      width="16"
                      height="16"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      style={{ transform: showAlternatives ? 'rotate(180deg)' : 'none', transition: 'transform 0.2s' }}
                      aria-hidden="true"
                    >
                      <polyline points="6 9 12 15 18 9" />
                    </svg>
                  </button>

                  {showAlternatives && (
                    <div className="alternatives-expanded-list">
                      {textResult.alternatives.map((alt, idx) => {
                        const altScore = alt.confidence || 0;
                        const pctStr = (altScore * 100).toFixed(1);
                        return (
                          <div key={idx} className="alt-item-row">
                            <span className="alt-rank-num">{idx + 2}</span>
                            <span className={`category-tag ${getCategoryClass(alt.category)}`}>
                              {alt.category}
                            </span>
                            <div className="alt-bar-track">
                              <div
                                className="alt-bar-fill"
                                style={{ width: `${Math.min(altScore * 100, 100)}%` }}
                              ></div>
                            </div>
                            <span className="alt-percentage-text">{pctStr}%</span>
                          </div>
                        );
                      })}
                    </div>
                  )}
                </div>
              )}

              {/* Result Footer */}
              <div className="result-card-footer">
                <button
                  type="button"
                  className="btn-copy-category"
                  onClick={() => copyToClipboard(textResult.predicted_category)}
                >
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                    <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
                    <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
                  </svg>
                  <span>{copiedCategory ? 'Copied category!' : 'Copy category'}</span>
                </button>
                <span className="verification-reminder">
                  ⓘ A person should verify this label.
                </span>
              </div>
            </div>
          )}
        </div>
      )}

      {/* MODE B: Upload Contract Document */}
      {inputMode === 'file' && (
        <div className="card">
          <form onSubmit={handleFileUpload}>
            {/* Drag & Drop Zone */}
            <div
              className={`dropzone-box ${isDragging ? 'dragover' : ''}`}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              role="region"
              aria-label="Contract File Dropzone"
            >
              <div className="dropzone-icon-circle">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                  <polyline points="17 8 12 3 7 8" />
                  <line x1="12" y1="3" x2="12" y2="15" />
                </svg>
              </div>
              <h3 className="dropzone-title">Drop your contract here</h3>
              <p className="dropzone-helper">
                or{' '}
                <label htmlFor="file-input-btn" className="browse-link-btn">
                  Browse files
                </label>{' '}
                · PDF or TXT
              </p>
              <p className="dropzone-note">
                Text-based documents up to 10 MB. Scanned image-only PDFs without OCR are not supported.
              </p>
              <input
                id="file-input-btn"
                type="file"
                accept=".pdf,.txt,application/pdf,text/plain"
                onChange={(e) => {
                  if (e.target.files && e.target.files[0]) {
                    validateAndSetFile(e.target.files[0]);
                  }
                }}
                className="hidden-file-input"
              />
            </div>

            {/* Selected File Card */}
            {selectedFile && (
              <div className="selected-file-row">
                <div className="file-info-col">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                    <polyline points="14 2 14 8 20 8" />
                  </svg>
                  <span className="file-name">{selectedFile.name}</span>
                  <span className="file-size">({(selectedFile.size / 1024).toFixed(1)} KB)</span>
                </div>
                <button
                  type="button"
                  className="btn-remove-file"
                  onClick={() => {
                    setSelectedFile(null);
                    setDocResult(null);
                    setError(null);
                  }}
                  title="Remove file"
                  aria-label="Remove selected file"
                >
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                    <line x1="18" y1="6" x2="6" y2="18" />
                    <line x1="6" y1="6" x2="18" y2="18" />
                  </svg>
                  <span>Remove</span>
                </button>
              </div>
            )}

            {/* Submit Action */}
            <div className="form-action-row">
              <button
                type="submit"
                className="btn-primary"
                disabled={loading || !selectedFile}
              >
                {loading ? (
                  <>
                    <span className="spinner" aria-hidden="true"></span>
                    <span>Processing document…</span>
                  </>
                ) : (
                  <>
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                      <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
                    </svg>
                    <span>Extract & classify</span>
                  </>
                )}
              </button>
            </div>
          </form>

          {/* Three-step progress strip during extraction & classification */}
          {loading && (
            <div className="progress-strip-wrapper" role="status" aria-live="polite">
              <div className="progress-strip-header">
                <span>Processing your document…</span>
              </div>
              <div className="progress-steps-row">
                <div className={`step-item ${processingStep >= 1 ? 'active' : ''} ${processingStep > 1 ? 'completed' : ''}`}>
                  <span className="step-num">1</span>
                  <span className="step-label">Reading file</span>
                </div>
                <div className="step-connector"></div>
                <div className={`step-item ${processingStep >= 2 ? 'active' : ''} ${processingStep > 2 ? 'completed' : ''}`}>
                  <span className="step-num">2</span>
                  <span className="step-label">Finding clauses</span>
                </div>
                <div className="step-connector"></div>
                <div className={`step-item ${processingStep >= 3 ? 'active' : ''}`}>
                  <span className="step-num">3</span>
                  <span className="step-label">Classifying</span>
                </div>
              </div>
            </div>
          )}

          {/* Document Classification Results */}
          {docResult && (
            <div className="doc-results-section" role="region" aria-live="polite">
              <div className="doc-results-header">
                <div>
                  <h3 className="doc-results-title">{docResult.document_name}</h3>
                  <p className="doc-results-meta">
                    {docResult.total_clauses} clauses extracted and analyzed
                  </p>
                </div>
              </div>

              {/* Summary Strip per DesignDoc */}
              <div className="summary-strip-card">
                <span className="summary-strip-title">Confidence Breakdown:</span>
                <div className="summary-strip-pills">
                  <span className="summary-pill pill-high">
                    ● High: <strong>{summaryStats.high}</strong>
                  </span>
                  <span className="summary-pill pill-mod">
                    ● Moderate: <strong>{summaryStats.moderate}</strong>
                  </span>
                  <span className="summary-pill pill-low">
                    ● Low / Review: <strong>{summaryStats.low}</strong>
                  </span>
                  {summaryStats.outOfScope > 0 && (
                    <span className="summary-pill pill-neutral">
                      ● Outside scope: <strong>{summaryStats.outOfScope}</strong>
                    </span>
                  )}
                </div>
              </div>

              {/* Filters & Sorting Bar */}
              <div className="doc-filters-bar">
                <div className="filter-group-left">
                  <label htmlFor="filter-cat-select" className="filter-ctrl-label">Filter:</label>
                  <select
                    id="filter-cat-select"
                    className="select-input-sm"
                    value={categoryFilter}
                    onChange={(e) => {
                      setCategoryFilter(e.target.value);
                      setCurrentPage(1);
                    }}
                  >
                    <option value="ALL">All Categories ({docResult.total_clauses})</option>
                    {uniqueDocCategories.map(([cat, cnt]) => (
                      <option key={cat} value={cat}>
                        {cat} ({cnt})
                      </option>
                    ))}
                  </select>
                </div>

                <div className="filter-group-right">
                  <label htmlFor="sort-order-select" className="filter-ctrl-label">Sort:</label>
                  <select
                    id="sort-order-select"
                    className="select-input-sm"
                    value={sortOrder}
                    onChange={(e) => {
                      setSortOrder(e.target.value);
                      setCurrentPage(1);
                    }}
                  >
                    <option value="highest">Highest confidence</option>
                    <option value="original">Document order</option>
                    <option value="lowest">Lowest confidence</option>
                  </select>
                </div>
              </div>

              {/* Clause Rows List */}
              <div className="clause-rows-list">
                {displayedClauses.length === 0 ? (
                  <div className="empty-sub-state">
                    No clauses match the selected category filter.
                  </div>
                ) : (
                  displayedClauses.map((clause, idx) => {
                    const absIdx = clause.clause_index ?? idx + 1;
                    const indexStr = String(absIdx).padStart(2, '0');
                    const confScore = getClauseConfidence(clause);
                    const isExpanded = !!expandedClauses[absIdx];
                    const statusStr = clause.confidence_status || '';
                    const isLow = statusStr.toLowerCase().includes('low');
                    const isScope = statusStr.toLowerCase().includes('scope') || statusStr.toLowerCase().includes('out');

                    return (
                      <div
                        key={absIdx}
                        className={`clause-row-card ${isLow ? 'accent-low' : ''} ${isScope ? 'accent-scope' : ''}`}
                      >
                        {/* Row Header */}
                        <div className="clause-row-header">
                          <div className="clause-row-left">
                            <span className="clause-mono-idx">{indexStr}</span>
                            <span className={`category-tag ${getCategoryClass(clause.predicted_category)}`}>
                              {clause.predicted_category}
                            </span>
                            <StatusBadge status={clause.confidence_status} />
                          </div>

                          <div className="clause-row-right">
                            <ConfidenceRing
                              score={confScore}
                              status={clause.confidence_status}
                              size="sm"
                            />
                            <span className="clause-row-pct">
                              {(confScore * 100).toFixed(1)}%
                            </span>
                          </div>
                        </div>

                        {/* Clause Body in Serif */}
                        <div className="clause-row-body">
                          <p className={`clause-serif-text ${!isExpanded ? 'clamped-two-lines' : ''}`}>
                            “{clause.clause_text}”
                          </p>
                          <div className="clause-row-actions">
                            <button
                              type="button"
                              className="btn-text-link"
                              onClick={() => toggleClauseExpand(absIdx)}
                            >
                              {isExpanded ? 'Less ⌃' : 'More ⌄'}
                            </button>
                            <button
                              type="button"
                              className="btn-text-link"
                              onClick={() => copyToClipboard(clause.clause_text, true, absIdx)}
                            >
                              {copiedClauseIdx === absIdx ? 'Copied clause!' : 'Copy'}
                            </button>
                          </div>
                        </div>

                        {/* In-row Alternatives when expanded */}
                        {isExpanded && clause.alternatives && clause.alternatives.length > 0 && (
                          <div className="row-alternatives-box">
                            <span className="row-alt-title">Alternative predictions:</span>
                            <div className="row-alt-list">
                              {clause.alternatives.map((alt, aIdx) => (
                                <div key={aIdx} className="row-alt-item">
                                  <span className={`category-tag ${getCategoryClass(alt.category)}`}>
                                    {alt.category}
                                  </span>
                                  <span className="row-alt-pct">
                                    {(alt.confidence * 100).toFixed(1)}%
                                  </span>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    );
                  })
                )}
              </div>

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="pagination-bar" role="navigation" aria-label="Clauses Pagination">
                  <span className="pagination-info">
                    Showing {(currentPage - 1) * clausesPerPage + 1}–
                    {Math.min(currentPage * clausesPerPage, totalFilteredClauses)} of {totalFilteredClauses} clauses
                  </span>

                  <div className="pagination-buttons">
                    <button
                      type="button"
                      className="btn-pagination"
                      disabled={currentPage === 1}
                      onClick={() => setCurrentPage((p) => p - 1)}
                    >
                      ‹ Previous
                    </button>

                    {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => (
                      <button
                        key={page}
                        type="button"
                        className={`btn-page-number ${currentPage === page ? 'active' : ''}`}
                        onClick={() => setCurrentPage(page)}
                      >
                        {page}
                      </button>
                    ))}

                    <button
                      type="button"
                      className="btn-pagination"
                      disabled={currentPage === totalPages}
                      onClick={() => setCurrentPage((p) => p + 1)}
                    >
                      Next ›
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
