-- ==============================================================================
-- VidhiMeet Supabase Database Hardening Script (legacy — superseded)
-- ==============================================================================
-- SUPERSEDED BY: scripts/rls_audit_and_fix.sql
--
-- That script:
--   1. Identifies tables with RLS disabled
--   2. Enables RLS + FORCE ROW LEVEL SECURITY on all 16 tables
--   3. Creates service_role bypass policy (backend never blocked)
--   4. Creates per-user ownership policies scoped to current_app_user_id()
--      (compatible with both Supabase Auth jwt and app's own JWT via
--       SET LOCAL app.current_user_id = '<uuid>')
--   5. Locks out anon role entirely
--   6. Includes PROOF queries (SET ROLE tests) to verify isolation
--
-- Run scripts/rls_audit_and_fix.sql in the Supabase SQL Editor instead.
-- ==============================================================================
-- (Legacy script kept below for reference)

DO $$
DECLARE
    tbl text;
    tables text[] := ARRAY[
        'audit_logs',
        'bookings',
        'draft_comments',
        'drafting_proposals',
        'drafting_requests',
        'lawyer_bank_accounts',
        'lawyer_profiles',
        'messages',
        'password_reset_tokens',
        'platform_feedback',
        'refresh_tokens',
        'reviews',
        'user_consents',
        'users',
        'vouchers',
        'webhook_events'
    ];
BEGIN
    FOREACH tbl IN ARRAY tables LOOP
        -- 1. Ensure Row Level Security is enabled
        EXECUTE format('ALTER TABLE public.%I ENABLE ROW LEVEL SECURITY;', tbl);
        
        -- 2. Drop existing policy if present
        EXECUTE format('DROP POLICY IF EXISTS "service_role_full_access" ON public.%I;', tbl);
        
        -- 3. Create explicit service_role policy (satisfies Supabase Linter 0008)
        IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'service_role') THEN
            EXECUTE format(
                'CREATE POLICY "service_role_full_access" ON public.%I FOR ALL TO service_role USING (true) WITH CHECK (true);',
                tbl
            );
        END IF;
    END LOOP;

    -- 4. Extra Defense-in-Depth: Lock down PostgREST public API roles (anon, authenticated)
    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'anon') AND
       EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'authenticated') THEN
        
        REVOKE ALL ON ALL TABLES IN SCHEMA public FROM anon, authenticated;
        REVOKE ALL ON ALL SEQUENCES IN SCHEMA public FROM anon, authenticated;
        REVOKE ALL ON ALL ROUTINES IN SCHEMA public FROM anon, authenticated;
        
        -- Ensure any newly created tables in the future default to locked down
        ALTER DEFAULT PRIVILEGES IN SCHEMA public REVOKE ALL ON TABLES FROM anon, authenticated;
        ALTER DEFAULT PRIVILEGES IN SCHEMA public REVOKE ALL ON SEQUENCES FROM anon, authenticated;
        ALTER DEFAULT PRIVILEGES IN SCHEMA public REVOKE ALL ON ROUTINES FROM anon, authenticated;
    END IF;
END $$;
