-- =============================================================================
-- VidhiMeet — RLS Audit, Enable & Policy Script
-- =============================================================================
-- ARCHITECTURE NOTE:
--   This app connects to Supabase Postgres using the `service_role` key (bypasses
--   RLS by design). The backend enforces ownership at the application layer via JWT.
--   RLS here provides DEFENSE-IN-DEPTH against:
--     (a) Direct PostgREST / anon API access bypassing the FastAPI backend
--     (b) Accidental `authenticated`-role connections leaking cross-user rows
--     (c) Future client-side Supabase SDK usage without backend mediation
--
--   Because the app issues its OWN JWTs (not Supabase Auth JWTs), `auth.uid()`
--   does NOT resolve the app's user IDs. Instead we use a custom session variable
--   pattern: the app sets `app.current_user_id` via SET LOCAL before each query,
--   and policies read it with current_setting('app.current_user_id', true).
--   The service_role bypass policy ensures the backend is never blocked.
-- =============================================================================

-- -----------------------------------------------------------------------------
-- STEP 1: Identify all public tables with RLS currently DISABLED
-- -----------------------------------------------------------------------------
SELECT
    n.nspname                AS schemaname,
    c.relname                AS tablename,
    c.relrowsecurity         AS rls_enabled,
    c.relforcerowsecurity    AS rls_forced
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE n.nspname = 'public'
  AND c.relkind = 'r'
  AND c.relrowsecurity = false
ORDER BY c.relname;

-- Expected output before this script runs (all 16 tables will appear):
-- audit_logs, bookings, draft_comments, drafting_proposals, drafting_requests,
-- lawyer_bank_accounts, lawyer_profiles, messages, password_reset_tokens,
-- platform_feedback, refresh_tokens, reviews, user_consents, users,
-- vouchers, webhook_events

-- -----------------------------------------------------------------------------
-- STEP 2: Enable RLS + FORCE ROW LEVEL SECURITY on all 16 tables,
--         then drop all stale policies (makes script idempotent)
-- -----------------------------------------------------------------------------
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
        EXECUTE format('ALTER TABLE public.%I ENABLE ROW LEVEL SECURITY;', tbl);
        EXECUTE format('ALTER TABLE public.%I FORCE ROW LEVEL SECURITY;', tbl);  -- blocks table owner too

        -- Drop existing policies so this script can be re-run safely
        EXECUTE format('DROP POLICY IF EXISTS "service_role_full_access" ON public.%I;', tbl);
        EXECUTE format('DROP POLICY IF EXISTS "owner_select"             ON public.%I;', tbl);
        EXECUTE format('DROP POLICY IF EXISTS "owner_insert"             ON public.%I;', tbl);
        EXECUTE format('DROP POLICY IF EXISTS "owner_update"             ON public.%I;', tbl);
        EXECUTE format('DROP POLICY IF EXISTS "owner_delete"             ON public.%I;', tbl);
        EXECUTE format('DROP POLICY IF EXISTS "participant_select"       ON public.%I;', tbl);
        EXECUTE format('DROP POLICY IF EXISTS "public_read"              ON public.%I;', tbl);
    END LOOP;
    RAISE NOTICE 'RLS enabled + FORCE and old policies dropped on all 16 tables.';
END $$;

-- -----------------------------------------------------------------------------
-- STEP 3: service_role bypass policy (backend is NEVER blocked)
-- -----------------------------------------------------------------------------
-- The FastAPI backend connects as service_role. This policy allows full access.
-- Without it, FORCE ROW LEVEL SECURITY would block even the backend.
DO $$
DECLARE
    tbl text;
    tables text[] := ARRAY[
        'audit_logs','bookings','draft_comments','drafting_proposals','drafting_requests',
        'lawyer_bank_accounts','lawyer_profiles','messages','password_reset_tokens',
        'platform_feedback','refresh_tokens','reviews','user_consents','users',
        'vouchers','webhook_events'
    ];
BEGIN
    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'service_role') THEN
        FOREACH tbl IN ARRAY tables LOOP
            EXECUTE format(
                'CREATE POLICY "service_role_full_access" ON public.%I
                 FOR ALL TO service_role
                 USING (true)
                 WITH CHECK (true);',
                tbl
            );
        END LOOP;
        RAISE NOTICE 'service_role bypass policies created on all 16 tables.';
    ELSE
        RAISE NOTICE 'service_role role not found — skipping bypass (not Supabase).';
    END IF;
END $$;

-- -----------------------------------------------------------------------------
-- STEP 4: Helper function — resolves user identity from either auth mechanism
-- -----------------------------------------------------------------------------
-- Supports both:
--   (a) Supabase Auth JWT   → auth.uid()
--   (b) App's own JWT path  → SET LOCAL app.current_user_id = '<uuid>'
CREATE OR REPLACE FUNCTION public.current_app_user_id()
RETURNS text
LANGUAGE sql
STABLE
SECURITY DEFINER
AS $$
    SELECT COALESCE(
        auth.uid()::text,                              -- Supabase Auth JWT (future-proof)
        current_setting('app.current_user_id', true)   -- App custom session variable
    );
$$;

-- -----------------------------------------------------------------------------
-- STEP 5: Per-table, per-user ownership policies (authenticated role)
-- -----------------------------------------------------------------------------

-- ── users ────────────────────────────────────────────────────────────────────
-- Users read/update only their own row. INSERT/DELETE via service_role only.
CREATE POLICY "owner_select" ON public.users
    FOR SELECT TO authenticated
    USING (id = public.current_app_user_id());

CREATE POLICY "owner_update" ON public.users
    FOR UPDATE TO authenticated
    USING (id = public.current_app_user_id())
    WITH CHECK (id = public.current_app_user_id());

-- ── lawyer_profiles ──────────────────────────────────────────────────────────
-- Verified profiles are readable by all authenticated users (public lawyer search).
-- Own (even unverified) profile is always visible to its owner.
CREATE POLICY "public_read" ON public.lawyer_profiles
    FOR SELECT TO authenticated
    USING (verified = true);

CREATE POLICY "owner_select" ON public.lawyer_profiles
    FOR SELECT TO authenticated
    USING (user_id = public.current_app_user_id());

CREATE POLICY "owner_update" ON public.lawyer_profiles
    FOR UPDATE TO authenticated
    USING (user_id = public.current_app_user_id())
    WITH CHECK (user_id = public.current_app_user_id());

-- ── lawyer_bank_accounts ─────────────────────────────────────────────────────
-- Strictly own-only: bank details are highly sensitive (DPDPA).
CREATE POLICY "owner_select" ON public.lawyer_bank_accounts
    FOR SELECT TO authenticated
    USING (user_id = public.current_app_user_id());

CREATE POLICY "owner_insert" ON public.lawyer_bank_accounts
    FOR INSERT TO authenticated
    WITH CHECK (user_id = public.current_app_user_id());

CREATE POLICY "owner_update" ON public.lawyer_bank_accounts
    FOR UPDATE TO authenticated
    USING (user_id = public.current_app_user_id())
    WITH CHECK (user_id = public.current_app_user_id());

CREATE POLICY "owner_delete" ON public.lawyer_bank_accounts
    FOR DELETE TO authenticated
    USING (user_id = public.current_app_user_id());

-- ── bookings ─────────────────────────────────────────────────────────────────
-- Visible only to the booking's client or lawyer (mirrors booking_for_participant).
CREATE POLICY "participant_select" ON public.bookings
    FOR SELECT TO authenticated
    USING (
        client_id = public.current_app_user_id()
        OR lawyer_id = public.current_app_user_id()
    );

-- Clients initiate bookings (client_id must equal caller).
CREATE POLICY "owner_insert" ON public.bookings
    FOR INSERT TO authenticated
    WITH CHECK (client_id = public.current_app_user_id());

-- Status mutations happen via service_role (payment webhooks, admin actions).

-- ── messages ─────────────────────────────────────────────────────────────────
-- Visible only to the booking's participants.
CREATE POLICY "participant_select" ON public.messages
    FOR SELECT TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM public.bookings b
            WHERE b.id = messages.booking_id
              AND (b.client_id = public.current_app_user_id()
                   OR b.lawyer_id = public.current_app_user_id())
        )
    );

CREATE POLICY "owner_insert" ON public.messages
    FOR INSERT TO authenticated
    WITH CHECK (
        sender_id = public.current_app_user_id()
        AND EXISTS (
            SELECT 1 FROM public.bookings b
            WHERE b.id = messages.booking_id
              AND (b.client_id = public.current_app_user_id()
                   OR b.lawyer_id = public.current_app_user_id())
        )
    );

-- ── drafting_requests ────────────────────────────────────────────────────────
-- Creator and assigned drafter see it; OPEN requests visible to all lawyers for bidding.
CREATE POLICY "participant_select" ON public.drafting_requests
    FOR SELECT TO authenticated
    USING (
        creator_id = public.current_app_user_id()
        OR drafter_id = public.current_app_user_id()
        OR status::text IN ('open', 'OPEN')
    );

CREATE POLICY "owner_insert" ON public.drafting_requests
    FOR INSERT TO authenticated
    WITH CHECK (creator_id = public.current_app_user_id());

CREATE POLICY "owner_update" ON public.drafting_requests
    FOR UPDATE TO authenticated
    USING (
        creator_id = public.current_app_user_id()
        OR drafter_id = public.current_app_user_id()
    );

-- ── drafting_proposals ───────────────────────────────────────────────────────
-- Lawyer sees their own proposals; creator sees all proposals on their requests.
CREATE POLICY "participant_select" ON public.drafting_proposals
    FOR SELECT TO authenticated
    USING (
        lawyer_id = public.current_app_user_id()
        OR EXISTS (
            SELECT 1 FROM public.drafting_requests dr
            WHERE dr.id = drafting_proposals.request_id
              AND dr.creator_id = public.current_app_user_id()
        )
    );

CREATE POLICY "owner_insert" ON public.drafting_proposals
    FOR INSERT TO authenticated
    WITH CHECK (lawyer_id = public.current_app_user_id());

-- ── draft_comments ───────────────────────────────────────────────────────────
-- Visible to creator and drafter of the parent request only.
CREATE POLICY "participant_select" ON public.draft_comments
    FOR SELECT TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM public.drafting_requests dr
            WHERE dr.id = draft_comments.request_id
              AND (dr.creator_id = public.current_app_user_id()
                   OR dr.drafter_id = public.current_app_user_id())
        )
    );

CREATE POLICY "owner_insert" ON public.draft_comments
    FOR INSERT TO authenticated
    WITH CHECK (
        user_id = public.current_app_user_id()
        AND EXISTS (
            SELECT 1 FROM public.drafting_requests dr
            WHERE dr.id = draft_comments.request_id
              AND (dr.creator_id = public.current_app_user_id()
                   OR dr.drafter_id = public.current_app_user_id())
        )
    );

CREATE POLICY "owner_delete" ON public.draft_comments
    FOR DELETE TO authenticated
    USING (
        user_id = public.current_app_user_id()
        OR EXISTS (
            SELECT 1 FROM public.drafting_requests dr
            WHERE dr.id = draft_comments.request_id
              AND (dr.creator_id = public.current_app_user_id()
                   OR dr.drafter_id = public.current_app_user_id())
        )
    );

-- ── reviews ──────────────────────────────────────────────────────────────────
-- Public read (lawyer review pages); only the booking client may insert.
CREATE POLICY "public_read" ON public.reviews
    FOR SELECT TO authenticated
    USING (true);

CREATE POLICY "owner_insert" ON public.reviews
    FOR INSERT TO authenticated
    WITH CHECK (client_id = public.current_app_user_id());

-- ── user_consents ────────────────────────────────────────────────────────────
CREATE POLICY "owner_select" ON public.user_consents
    FOR SELECT TO authenticated
    USING (user_id = public.current_app_user_id());

CREATE POLICY "owner_insert" ON public.user_consents
    FOR INSERT TO authenticated
    WITH CHECK (user_id = public.current_app_user_id());

-- ── audit_logs ───────────────────────────────────────────────────────────────
-- Users can read their own audit events (DPDP right to access / transparency).
CREATE POLICY "owner_select" ON public.audit_logs
    FOR SELECT TO authenticated
    USING (actor_id = public.current_app_user_id());

-- ── vouchers ─────────────────────────────────────────────────────────────────
-- Users see vouchers assigned to them, or public promotional vouchers.
CREATE POLICY "owner_select" ON public.vouchers
    FOR SELECT TO authenticated
    USING (
        user_id = public.current_app_user_id()
        OR (user_id IS NULL AND is_promotional = true AND is_active = true)
    );

-- ── platform_feedback ────────────────────────────────────────────────────────
CREATE POLICY "owner_select" ON public.platform_feedback
    FOR SELECT TO authenticated
    USING (user_id = public.current_app_user_id());

CREATE POLICY "owner_insert" ON public.platform_feedback
    FOR INSERT TO authenticated
    WITH CHECK (
        user_id IS NULL                              -- anonymous feedback allowed
        OR user_id = public.current_app_user_id()
    );

-- ── refresh_tokens, password_reset_tokens, webhook_events ───────────────────
-- Backend-only via service_role. No authenticated-role policy → denied by default.
-- (This is intentional: tokens are opaque to the client; webhooks are Cashfree-only.)

-- -----------------------------------------------------------------------------
-- STEP 6: Revoke all schema access from anon role (defense-in-depth)
-- -----------------------------------------------------------------------------
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'anon') THEN
        REVOKE ALL ON ALL TABLES    IN SCHEMA public FROM anon;
        REVOKE ALL ON ALL SEQUENCES IN SCHEMA public FROM anon;
        REVOKE ALL ON ALL ROUTINES  IN SCHEMA public FROM anon;
        ALTER DEFAULT PRIVILEGES IN SCHEMA public REVOKE ALL ON TABLES    FROM anon;
        ALTER DEFAULT PRIVILEGES IN SCHEMA public REVOKE ALL ON SEQUENCES FROM anon;
        ALTER DEFAULT PRIVILEGES IN SCHEMA public REVOKE ALL ON ROUTINES  FROM anon;
        RAISE NOTICE 'anon role fully locked out of public schema.';
    END IF;
END $$;

-- -----------------------------------------------------------------------------
-- STEP 7: Verify — confirm RLS is ON + FORCED for all 16 tables
-- -----------------------------------------------------------------------------
SELECT
    c.relname                AS tablename,
    c.relrowsecurity         AS rls_enabled,
    c.relforcerowsecurity    AS rls_forced
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE n.nspname = 'public'
  AND c.relkind = 'r'
ORDER BY c.relname;
-- Expected: rls_enabled = true, rls_forced = true for all 16 rows

-- -----------------------------------------------------------------------------
-- STEP 8: Policy inventory — list every policy, role, and expression
-- -----------------------------------------------------------------------------
SELECT
    tablename,
    policyname,
    roles::text,
    cmd        AS operation,
    qual       AS using_expr,
    with_check AS check_expr
FROM pg_policies
WHERE schemaname = 'public'
ORDER BY tablename, policyname;

-- -----------------------------------------------------------------------------
-- STEP 9: PROOF — row isolation test as another user
-- -----------------------------------------------------------------------------
-- Replace USER_A_UUID / USER_B_UUID with real UUIDs from your users table.
-- Run this in Supabase SQL Editor (connected as postgres / service_role owner).
-- The SET ROLE switches simulate what an `authenticated`-role connection sees.

-- ── Test 1: User A sees only their own row ───────────────────────────────────
BEGIN;
    SET ROLE authenticated;
    SET LOCAL app.current_user_id = 'USER_A_UUID';   -- ← paste User A UUID here

    -- Must return exactly 1 row
    SELECT id, email, role FROM public.users;

    -- Must return 0 rows (User B's booking is invisible to User A)
    SELECT id, client_id, status
    FROM public.bookings
    WHERE client_id = 'USER_B_UUID';                 -- ← paste User B UUID here

    -- Must return 0 rows (User B's bank account is invisible)
    SELECT id, account_holder_name
    FROM public.lawyer_bank_accounts
    WHERE user_id = 'USER_B_UUID';                   -- ← paste User B UUID here
ROLLBACK;

-- ── Test 2: anon gets permission denied ──────────────────────────────────────
BEGIN;
    SET ROLE anon;
    -- Must raise: ERROR: permission denied for table users
    SELECT id FROM public.users LIMIT 1;
ROLLBACK;

-- ── Test 3: service_role (backend) sees everything ───────────────────────────
BEGIN;
    SET ROLE service_role;
    -- Must return a count (not 0, not error)
    SELECT COUNT(*) AS total_users FROM public.users;
ROLLBACK;

