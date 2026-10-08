import React, { useState } from 'react';
import { classifyClause, classifyFile } from '../api';

const SAMPLE_CLAUSES = [
  {
    label: 'Governing Law',
    text: 'This Agreement and any dispute arising from the performance hereof shall be governed by and construed in accordance with the laws of the State of Delaware.',
  },
  {
    label: 'Confidentiality',
    text: 'Each party agrees that all Confidential Information received from the disclosing party will be kept in strict confidence and not disclosed to any third party for five (5) years.',
  },
  {
    label: 'Termination',
    text: 'Either party may terminate this Agreement without cause upon providing thirty (30) days prior written notice to the other party.',
  },
  {
    label: 'Non-Compete',
    text: 'During the term of this Agreement and for a period of twelve (12) months thereafter, Employee shall not directly or indirectly engage in any competitive business activity.',
  },
];

export default function ClassifierView() {
  const [inputMode, setInputMode] = useState('text'); // 'text' | 'file'
  const [clauseText, setClauseText] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // Results
  const [textResult, setTextResult] = useState(null);
  const [docResult, setDocResult] = useState(null);

  const handleClassifyText = async (e) => {
    e?.preventDefault();
    if (!clauseText.trim()) return;

    setLoading(true);
    setError(null);
    setTextResult(null);

    try {
      const data = await classifyClause(clauseText);
      setTextResult(data);
    } catch (err) {
      setError(err.message);
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

    try {
      const data = await classifyFile(selectedFile);
      setDocResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleLoadSample = (sample) => {
    setClauseText(sample.text);
    setTextResult(null);
    setError(null);
  };

  return (
    <div>
      <div className="section-header">
        <h2 className="section-title">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ color: 'var(--accent-blue)' }}>
            <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
            <line x1="9" y1="3" x2="9" y2="21"/>
          </svg>
          Contract Clause Classification
        </h2>
        <p className="section-subtitle">
          Classical ML inference (Logistic Regression + TF-IDF) trained on the 41-class CUAD v1 legal benchmark.
        </p>
      </div>

      {/* Mode Switcher */}
      <div style={{ display: 'flex', gap: '0.75rem', marginBottom: '1.25rem' }}>
        <button
          className={`btn-secondary ${inputMode === 'text' ? 'active' : ''}`}
          style={{
            borderColor: inputMode === 'text' ? 'var(--accent-blue)' : 'var(--border-color)',
            background: inputMode === 'text' ? 'rgba(59, 130, 246, 0.15)' : 'rgba(255, 255, 255, 0.04)',
            color: inputMode === 'text' ? '#60a5fa' : 'var(--text-secondary)'
          }}
          onClick={() => { setInputMode('text'); setError(null); }}
        >
          Paste Clause Text
        </button>
        <button
          className={`btn-secondary ${inputMode === 'file' ? 'active' : ''}`}
          style={{
            borderColor: inputMode === 'file' ? 'var(--accent-blue)' : 'var(--border-color)',
            background: inputMode === 'file' ? 'rgba(59, 130, 246, 0.15)' : 'rgba(255, 255, 255, 0.04)',
            color: inputMode === 'file' ? '#60a5fa' : 'var(--text-secondary)'
          }}
          onClick={() => { setInputMode('file'); setError(null); }}
        >
          Upload Contract Document (PDF / TXT)
        </button>
      </div>

      {error && (
        <div className="alert alert-error">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
          </svg>
          <span>{error}</span>
        </div>
      )}

      {/* Mode A: Direct Text Input */}
      {inputMode === 'text' && (
        <div className="glass-card">
          <form onSubmit={handleClassifyText}>
            <div className="form-group">
              <label className="form-label">
                Legal Clause Text
              </label>
              <textarea
                className="text-area-input"
                placeholder="Paste contract clause here (e.g., 'This Agreement shall be governed by Delaware law...')"
                value={clauseText}
                onChange={(e) => setClauseText(e.target.value)}
                rows={4}
              />
            </div>

            {/* Quick Test Samples */}
            <div style={{ marginBottom: '1.25rem' }}>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.4rem' }}>
                Load benchmark clause sample:
              </span>
              <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                {SAMPLE_CLAUSES.map((s) => (
                  <button
                    key={s.label}
                    type="button"
                    className="btn-secondary"
                    style={{ fontSize: '0.75rem', padding: '0.3rem 0.65rem' }}
                    onClick={() => handleLoadSample(s)}
                  >
                    {s.label}
                  </button>
                ))}
              </div>
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
              {clauseText && (
                <button
                  type="button"
                  className="btn-secondary"
                  onClick={() => { setClauseText(''); setTextResult(null); }}
                >
                  Clear
                </button>
              )}
              <button
                type="submit"
                className="btn-primary"
                disabled={loading || !clauseText.trim()}
              >
                {loading && <span className="spinner"></span>}
                {loading ? 'Classifying...' : 'Classify Clause'}
              </button>
            </div>
          </form>

          {/* Single Clause Result */}
          {textResult && (
            <div className="result-card glass-card" style={{ marginTop: '1.5rem', background: 'rgba(15, 23, 42, 0.9)' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '0.5rem', marginBottom: '1rem' }}>
                <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Classification Result</span>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  Model: <strong style={{ color: 'var(--text-secondary)' }}>{textResult.model_name}</strong>
                </span>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem', marginBottom: '1.25rem' }}>
                <div>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', display: 'block', marginBottom: '0.25rem' }}>
                    Predicted Category
                  </span>
                  <span className="category-badge" style={{ fontSize: '1.1rem', padding: '0.35rem 0.85rem' }}>
                    {textResult.predicted_category}
                  </span>
                </div>

                {textResult.confidence !== null && (
                  <div style={{ minWidth: '180px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginBottom: '0.25rem' }}>
                      <span style={{ color: 'var(--text-secondary)' }}>Confidence (Probability)</span>
                      <span className="confidence-val">{(textResult.confidence * 100).toFixed(1)}%</span>
                    </div>
                    <div className="meter-bar">
                      <div className="meter-fill" style={{ width: `${Math.min(textResult.confidence * 100, 100)}%` }}></div>
                    </div>
                  </div>
                )}
              </div>

              {/* Top-3 Alternatives */}
              {textResult.alternatives && textResult.alternatives.length > 0 && (
                <div>
                  <span style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)' }}>
                    Top Alternative Categories
                  </span>
                  <div className="alternatives-list">
                    {textResult.alternatives.map((alt, i) => (
                      <div key={i} className="alt-item">
                        <span style={{ color: '#cbd5e1' }}>{alt.category}</span>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                          <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                            {(alt.confidence * 100).toFixed(1)}%
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Mode B: Contract Document Upload */}
      {inputMode === 'file' && (
        <div className="glass-card">
          <form onSubmit={handleFileUpload}>
            <div
              className={`dropzone ${selectedFile ? 'active' : ''}`}
              onClick={() => document.getElementById('contract-file-input').click()}
            >
              <input
                id="contract-file-input"
                type="file"
                accept=".pdf,.txt"
                style={{ display: 'none' }}
                onChange={(e) => {
                  if (e.target.files?.[0]) setSelectedFile(e.target.files[0]);
                }}
              />
              <div className="dropzone-icon">📄</div>
              <p className="dropzone-text">
                {selectedFile ? (
                  <strong>Selected: {selectedFile.name} ({(selectedFile.size / 1024).toFixed(1)} KB)</strong>
                ) : (
                  'Click to select or drag and drop a contract document'
                )}
              </p>
              <p className="dropzone-hint">Supported formats: PDF (.pdf) or Plain Text (.txt)</p>
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '1.25rem' }}>
              {selectedFile && (
                <button
                  type="button"
                  className="btn-secondary"
                  onClick={() => { setSelectedFile(null); setDocResult(null); }}
                >
                  Remove File
                </button>
              )}
              <button
                type="submit"
                className="btn-primary"
                disabled={loading || !selectedFile}
              >
                {loading && <span className="spinner"></span>}
                {loading ? 'Extracting & Classifying...' : 'Extract & Classify Document'}
              </button>
            </div>
          </form>

          {/* Document Multi-Clause Results */}
          {docResult && (
            <div className="result-card glass-card" style={{ marginTop: '1.5rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.75rem' }}>
                <div>
                  <h3 style={{ fontSize: '1.1rem', fontWeight: 600 }}>{docResult.document_name}</h3>
                  <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                    Total extracted clauses: <strong>{docResult.total_clauses}</strong>
                  </span>
                </div>
                <span className="logo-badge">Extraction Pipeline Complete</span>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', maxHeight: '550px', overflowY: 'auto', paddingRight: '0.5rem' }}>
                {docResult.clauses.map((item) => (
                  <div key={item.clause_index} style={{ background: 'rgba(0, 0, 0, 0.25)', border: '1px solid var(--border-color)', borderRadius: '10px', padding: '1rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem', flexWrap: 'wrap', gap: '0.5rem' }}>
                      <span style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--accent-purple)' }}>
                        Clause #{item.clause_index}
                      </span>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <span className="category-badge">{item.predicted_category}</span>
                        {item.confidence !== null && (
                          <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.75rem', color: 'var(--accent-cyan)' }}>
                            {(item.confidence * 100).toFixed(1)}%
                          </span>
                        )}
                      </div>
                    </div>
                    <p style={{ fontSize: '0.875rem', color: '#e2e8f0', lineHeight: 1.5 }}>
                      {item.clause_text}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
