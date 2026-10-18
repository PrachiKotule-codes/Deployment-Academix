-- LOCAL DEMO SETUP ONLY: this sets the academix_user password to ADMIN to match .env.example.
-- Run as PostgreSQL administrator with: psql -U postgres -h 127.0.0.1 -d postgres -W -f setup_postgres.sql
SELECT 'CREATE ROLE academix_user LOGIN PASSWORD ''ADMIN'''
WHERE NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'academix_user')\gexec
ALTER ROLE academix_user WITH LOGIN PASSWORD 'ADMIN';

-- Create a fresh app database only if it does not already exist.
SELECT format('CREATE DATABASE %I OWNER %I', 'academix_submission', 'academix_user')
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'academix_submission')\gexec

\connect academix_submission
GRANT ALL PRIVILEGES ON DATABASE academix_submission TO academix_user;
GRANT ALL PRIVILEGES ON SCHEMA public TO academix_user;
