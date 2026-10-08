// ClauseIQ Centralized API Service

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

/**
 * Health check
 */
export async function checkHealth() {
  const res = await fetch(`${API_BASE_URL}/health`);
  if (!res.ok) throw new Error(`Health check failed with status: ${res.status}`);
  return await res.json();
}

/**
 * Fetch 41 CUAD legal categories
 */
export async function getCategories() {
  const res = await fetch(`${API_BASE_URL}/categories`);
  if (!res.ok) throw new Error(`Failed to fetch categories: ${res.status}`);
  return await res.json();
}

/**
 * Classify a single clause text
 */
export async function classifyClause(clauseText) {
  const res = await fetch(`${API_BASE_URL}/classify`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ clause_text: clauseText }),
  });

  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.detail || 'Classification failed.');
  }
  return data;
}

/**
 * Upload contract PDF or TXT for multi-clause classification
 */
export async function classifyFile(file) {
  const formData = new FormData();
  formData.append('file', file);

  const res = await fetch(`${API_BASE_URL}/classify/file`, {
    method: 'POST',
    body: formData,
  });

  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.detail || 'File classification failed.');
  }
  return data;
}

/**
 * Semantic Cosine Similarity Clause Search
 */
export async function searchClauses(query, topK = 5, categoryFilter = null, minScore = 0.0) {
  const payload = {
    query,
    top_k: Number(topK),
    category_filter: categoryFilter || null,
    min_score: Number(minScore),
  };

  const res = await fetch(`${API_BASE_URL}/search`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  const data = await res.json();
  if (!res.ok) {
    throw new Error(data.detail || 'Search query failed.');
  }
  return data;
}
