import React from 'react';

export default function Footer() {
  return (
    <footer className="footer">
      <p>
        <strong>ClauseIQ</strong> &bull; MCA Mini Project &bull; Sprint 3: Integration &amp; Deployment
      </p>
      <div className="footer-tags">
        <span className="footer-tag">Classical ML (Logistic Regression)</span>
        <span className="footer-tag">TF-IDF (10,000 N-Gram Features)</span>
        <span className="footer-tag">Cosine Similarity Search</span>
        <span className="footer-tag">CUAD v1 Dataset (12,204 Clauses)</span>
        <span className="footer-tag">FastAPI Backend</span>
        <span className="footer-tag">Supabase PostgreSQL</span>
      </div>
      <p style={{ marginTop: '0.75rem', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
        Deterministic classification and mathematical vector search. Strictly Classical Machine Learning (No generative AI or LLMs).
      </p>
    </footer>
  );
}
