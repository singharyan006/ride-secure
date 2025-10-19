-- Migration: add detection-specific columns to violations table for Supabase/Postgres
-- Run this migration against your Supabase/Postgres database.
-- Note: ALTER TABLE ... ADD COLUMN IF NOT EXISTS is supported in Postgres.

BEGIN;

-- Add bounding box columns
ALTER TABLE public.violations
    ADD COLUMN IF NOT EXISTS x1 INTEGER,
    ADD COLUMN IF NOT EXISTS y1 INTEGER,
    ADD COLUMN IF NOT EXISTS x2 INTEGER,
    ADD COLUMN IF NOT EXISTS y2 INTEGER;

-- Add class and tracking fields
ALTER TABLE public.violations
    ADD COLUMN IF NOT EXISTS class_id INTEGER,
    ADD COLUMN IF NOT EXISTS class_name VARCHAR(100),
    ADD COLUMN IF NOT EXISTS track_id VARCHAR(100);

-- Add or rename confidence field if needed
ALTER TABLE public.violations
    ADD COLUMN IF NOT EXISTS confidence_score DOUBLE PRECISION;

-- Ensure license plate and plate_confidence exist (idempotent)
ALTER TABLE public.violations
    ADD COLUMN IF NOT EXISTS license_plate VARCHAR(50),
    ADD COLUMN IF NOT EXISTS plate_confidence DOUBLE PRECISION;

-- Create indexes to speed up common queries
CREATE INDEX IF NOT EXISTS idx_violations_class_name ON public.violations (class_name);
CREATE INDEX IF NOT EXISTS idx_violations_track_id ON public.violations (track_id);
CREATE INDEX IF NOT EXISTS idx_violations_timestamp ON public.violations (timestamp);

COMMIT;

-- Optional: cleanup/verification
-- SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'violations';
