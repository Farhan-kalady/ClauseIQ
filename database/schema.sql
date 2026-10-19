-- ==============================================================================
-- ClauseIQ - Supabase PostgreSQL Database Schema
-- Machine Learning-Based Contract Clause Classification and Search System
-- ==============================================================================

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ------------------------------------------------------------------------------
-- 1. Contracts Table (Metadata for uploaded documents)
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS contracts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_name TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- ------------------------------------------------------------------------------
-- 2. Clauses Table (Extracted and classified clauses per contract)
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS clauses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    contract_id UUID NOT NULL REFERENCES contracts(id) ON DELETE CASCADE,
    clause_text TEXT NOT NULL,
    category TEXT NOT NULL,
    confidence_score DOUBLE PRECISION,
    created_at TIMESTAMPTZ DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- ------------------------------------------------------------------------------
-- 3. Classification Logs (Telemetry & audit for /classify endpoint)
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS classification_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    input_text TEXT NOT NULL,
    predicted_category TEXT NOT NULL,
    confidence_score DOUBLE PRECISION,
    document_name TEXT,
    created_at TIMESTAMPTZ DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- ------------------------------------------------------------------------------
-- 4. Search Logs (Telemetry & audit for /search endpoint)
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS search_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    query TEXT NOT NULL,
    category_filter TEXT,
    top_k INTEGER NOT NULL,
    results_count INTEGER NOT NULL,
    created_at TIMESTAMPTZ DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- ------------------------------------------------------------------------------
-- Indexes for High Performance Querying
-- ------------------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_clauses_contract_id ON clauses(contract_id);
CREATE INDEX IF NOT EXISTS idx_clauses_category ON clauses(category);
CREATE INDEX IF NOT EXISTS idx_classification_logs_created_at ON classification_logs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_search_logs_created_at ON search_logs(created_at DESC);

-- ------------------------------------------------------------------------------
-- Row Level Security (RLS) Configuration & Key Architecture
-- ------------------------------------------------------------------------------
-- SECURITY NOTE:
-- - The backend uses SUPABASE_KEY in .env.
-- - For production deployments, SUPABASE_KEY should be a Supabase service_role key
--   which bypasses RLS and protects database access behind the FastAPI server.
-- - The public anon key should have restricted permissions to avoid data scraping.
-- ------------------------------------------------------------------------------
ALTER TABLE contracts ENABLE ROW LEVEL SECURITY;
ALTER TABLE clauses ENABLE ROW LEVEL SECURITY;
ALTER TABLE classification_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE search_logs ENABLE ROW LEVEL SECURITY;

-- Contracts: Allow read access, permit insert by API service
DROP POLICY IF EXISTS "Allow read on contracts" ON contracts;
CREATE POLICY "Allow read on contracts" ON contracts FOR SELECT USING (true);

DROP POLICY IF EXISTS "Allow insert on contracts" ON contracts;
CREATE POLICY "Allow insert on contracts" ON contracts FOR INSERT WITH CHECK (true);

-- Clauses: Allow read access, permit insert by API service
DROP POLICY IF EXISTS "Allow read on clauses" ON clauses;
CREATE POLICY "Allow read on clauses" ON clauses FOR SELECT USING (true);

DROP POLICY IF EXISTS "Allow insert on clauses" ON clauses;
CREATE POLICY "Allow insert on clauses" ON clauses FOR INSERT WITH CHECK (true);

-- Telemetry Logs: Insert allowed, restrict select to prevent public telemetry leakage
DROP POLICY IF EXISTS "Allow insert on classification_logs" ON classification_logs;
CREATE POLICY "Allow insert on classification_logs" ON classification_logs FOR INSERT WITH CHECK (true);

DROP POLICY IF EXISTS "Allow insert on search_logs" ON search_logs;
CREATE POLICY "Allow insert on search_logs" ON search_logs FOR INSERT WITH CHECK (true);

-- Restrict read on telemetry logs to service_role only (or authenticated users)
DROP POLICY IF EXISTS "Allow public read on classification_logs" ON classification_logs;
DROP POLICY IF EXISTS "Allow public read on search_logs" ON search_logs;
CREATE POLICY "Restrict read on classification_logs" ON classification_logs FOR SELECT USING (auth.role() = 'service_role' OR auth.role() = 'authenticated');
CREATE POLICY "Restrict read on search_logs" ON search_logs FOR SELECT USING (auth.role() = 'service_role' OR auth.role() = 'authenticated');
