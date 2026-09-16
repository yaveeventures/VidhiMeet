"""enforce_rls_service_role_policies

Revision ID: 9a86c98e523c
Revises: 9b17288bd3cf
Create Date: 2026-09-16 11:13:02.124748
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '9a86c98e523c'
down_revision: Union[str, None] = '9b17288bd3cf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TABLES = [
    "audit_logs",
    "bookings",
    "draft_comments",
    "drafting_proposals",
    "drafting_requests",
    "lawyer_bank_accounts",
    "lawyer_profiles",
    "messages",
    "password_reset_tokens",
    "platform_feedback",
    "refresh_tokens",
    "reviews",
    "user_consents",
    "users",
    "vouchers",
    "webhook_events",
]


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return

    # Enable RLS and create service_role full access policy on all tables
    # and revoke public PostgREST roles (anon, authenticated)
    op.execute(
        """
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
            EXECUTE format('ALTER TABLE public.%I ENABLE ROW LEVEL SECURITY', tbl);
            EXECUTE format('DROP POLICY IF EXISTS "service_role_full_access" ON public.%I', tbl);
            IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'service_role') THEN
                EXECUTE format('CREATE POLICY "service_role_full_access" ON public.%I FOR ALL TO service_role USING (true) WITH CHECK (true)', tbl);
            END IF;
        END LOOP;

        IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'anon') AND
           EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'authenticated') THEN
            REVOKE ALL ON ALL TABLES IN SCHEMA public FROM anon, authenticated;
            REVOKE ALL ON ALL SEQUENCES IN SCHEMA public FROM anon, authenticated;
            REVOKE ALL ON ALL ROUTINES IN SCHEMA public FROM anon, authenticated;
            ALTER DEFAULT PRIVILEGES IN SCHEMA public REVOKE ALL ON TABLES FROM anon, authenticated;
            ALTER DEFAULT PRIVILEGES IN SCHEMA public REVOKE ALL ON SEQUENCES FROM anon, authenticated;
            ALTER DEFAULT PRIVILEGES IN SCHEMA public REVOKE ALL ON ROUTINES FROM anon, authenticated;
        END IF;
    END $$;
    """
    )


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return

    op.execute(
        """
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
            EXECUTE format('DROP POLICY IF EXISTS "service_role_full_access" ON public.%I', tbl);
            EXECUTE format('ALTER TABLE public.%I DISABLE ROW LEVEL SECURITY', tbl);
        END LOOP;
    END $$;
    """
    )

