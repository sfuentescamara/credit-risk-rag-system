-- Initialize database for Credit Risk RAG System

-- Create extensions if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create schema
CREATE SCHEMA IF NOT EXISTS credit_risk;

-- Set search path
SET search_path TO credit_risk, public;

-- Create initial tables will be managed by Alembic migrations
-- This file is for initial setup only

-- Grant permissions
GRANT ALL PRIVILEGES ON SCHEMA credit_risk TO postgres;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA credit_risk TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA credit_risk TO postgres;

-- Create application user (if needed in production)
-- CREATE USER credit_risk_app WITH PASSWORD 'change_me_in_production';
-- GRANT CONNECT ON DATABASE credit_risk_db TO credit_risk_app;
-- GRANT USAGE ON SCHEMA credit_risk TO credit_risk_app;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA credit_risk TO credit_risk_app;
