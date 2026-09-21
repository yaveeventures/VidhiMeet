-- ==============================================================================
-- VidhiMeet Supabase Migration: Add Missing Columns to lawyer_bank_accounts
-- Description:
--   Adds RPD verification tracking columns to `lawyer_bank_accounts`
--   to resolve undefined column 500 error during UPI Reverse Penny Drop initiation.
-- ==============================================================================

ALTER TABLE public.lawyer_bank_accounts 
    ADD COLUMN IF NOT EXISTS verification_txn_id VARCHAR(80),
    ADD COLUMN IF NOT EXISTS verification_id VARCHAR(80),
    ADD COLUMN IF NOT EXISTS reference_id VARCHAR(80),
    ADD COLUMN IF NOT EXISTS verification_method VARCHAR(40) DEFAULT 'manual',
    ADD COLUMN IF NOT EXISTS verification_status VARCHAR(30) DEFAULT 'unverified',
    ADD COLUMN IF NOT EXISTS upi_name VARCHAR(255),
    ADD COLUMN IF NOT EXISTS utr VARCHAR(100),
    ADD COLUMN IF NOT EXISTS verified_at TIMESTAMP WITH TIME ZONE;

-- Create index on verification_id for fast status lookups and webhook reconciliation
CREATE INDEX IF NOT EXISTS ix_lawyer_bank_accounts_verification_id 
    ON public.lawyer_bank_accounts (verification_id);
