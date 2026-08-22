# Graph Report - VidhiMeet  (2026-08-22)

## Corpus Check
- 84 files · ~98,485 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1219 nodes · 3394 edges · 61 communities (49 shown, 12 thin omitted)
- Extraction: 86% EXTRACTED · 14% INFERRED · 0% AMBIGUOUS · INFERRED: 481 edges (avg confidence: 0.59)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `d885792f`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- main.py
- mr
- je
- lawyer.js
- app.js
- daily-js.js
- main.py
- i
- processEvent
- User
- audit
- toast
- Booking
- sanitize_key
- LawyerGrid
- calendar.py
- check_clock_drift
- 8dcb01bed07f_initial_schema.py
- 9d0be6640444_add_aadhaar_and_profile_picture.py
- i
- ntp_now
- er
- PlatformFeedback
- _e
- T
- 80394484e25e_add_phonepe_transaction_id.py
- bookings.py
- pdf-annotator.js
- NTP Time Synchronization — Compliance Runbook
- LexAPI
- setup_domain_ssl.sh
- firebase-phone-auth.js
- booking_service.py
- Booking
- verify_ntp_compliance
- register
- README.md
- ui-components.js
- test_marketplace.py
- cookie-consent.js
- LawyerProfile
- graphify
- graphify.md
- test_marketplace.py
- calendar.py
- LawyerBankAccount
- Session
- env.py
- test_bank_account.py
- __init__.py
- decode_token
- reset_users.py
- datetime
- Session
- Session

## God Nodes (most connected - your core abstractions)
1. `User` - 134 edges
2. `Role` - 57 edges
3. `audit()` - 55 edges
4. `Practice` - 53 edges
5. `BookingStatus` - 49 edges
6. `LexAPI` - 49 edges
7. `Booking` - 48 edges
8. `DraftingStatus` - 44 edges
9. `ProposalStatus` - 44 edges
10. `LawyerProfile` - 41 edges

## Surprising Connections (you probably didn't know these)
- `test_sanitize_filename()` --calls--> `sanitize_filename()`  [INFERRED]
  tests/test_sanitizer.py → backend/sanitizer.py
- `test_admin_ntp_status_endpoint_accessible_by_admin()` --calls--> `get_db()`  [INFERRED]
  tests/test_ntp.py → backend/db.py
- `get_user_by_email()` --indirect_call--> `User`  [INFERRED]
  tests/test_drafting.py → backend/models.py
- `test_admin_ntp_status_endpoint_accessible_by_admin()` --indirect_call--> `User`  [INFERRED]
  tests/test_ntp.py → backend/models.py
- `test_cancelled_slot_relisting()` --indirect_call--> `User`  [INFERRED]
  tests/test_cancellation.py → backend/models.py

## Import Cycles
- None detected.

## Communities (61 total, 12 thin omitted)

### Community 0 - "main.py"
Cohesion: 0.27
Nodes (3): gt(), qt, re()

### Community 1 - "mr"
Cohesion: 0.06
Nodes (72): $(), openChatModal(), LexE2EE, aadhaarFileEl, ALL_TIME_SLOTS, barLicenceFileEl, bindTimeSelectListeners(), bookings (+64 more)

### Community 2 - "je"
Cohesion: 0.14
Nodes (26): Bt(), ct(), Es(), It(), jt(), k(), Kn(), l() (+18 more)

### Community 3 - "lawyer.js"
Cohesion: 0.07
Nodes (67): doAdminLogin(), checkInactivity(), LexAPI, _attemptReconnect(), backdrop, booking, bookingView(), checkHashRoute() (+59 more)

### Community 4 - "app.js"
Cohesion: 0.13
Nodes (11): ar(), fn(), hn(), ir(), mr, pr(), preprocessEvent(), q() (+3 more)

### Community 5 - "daily-js.js"
Cohesion: 0.11
Nodes (43): $(), auditLogs, checkAdminSession(), colors, decideVerification(), disputes, draftingTransactions, escapeHtml() (+35 more)

### Community 6 - "main.py"
Cohesion: 0.23
Nodes (14): _cutoff(), _ensure_tz(), log_purge_audit(), _now(), purge_expired_bookings(), purge_expired_tokens(), purge_withdrawn_consents(), data_retention_purge.py ----------------------- DPDP Act 2023, Section 8(7) — Da (+6 more)

### Community 8 - "processEvent"
Cohesion: 0.15
Nodes (24): DraftComment, DraftingProposal, DraftingRequest, rate_limit_dependency(), accept_drafting_proposal(), accept_drafting_request(), add_draft_comment(), approve_draft() (+16 more)

### Community 9 - "User"
Cohesion: 0.15
Nodes (16): Sanitize sensitive PII keys and credentials before log rendering., Configure structured JSON logging for production or key-value console logging fo, scrub_sensitive_pii_processor(), setup_logging(), drafting_document_mock_upload(), UploadFile, Perform deep structural payload inspection on document uploads.     Detects embe, scan_document_payload() (+8 more)

### Community 10 - "audit"
Cohesion: 0.07
Nodes (82): Base, BookingStatus, DraftingStatus, PasswordResetToken, Practice, ProposalStatus, str, RefreshToken (+74 more)

### Community 11 - "toast"
Cohesion: 0.33
Nodes (7): bn(), Jn(), N(), sn(), wn(), xe(), yn()

### Community 13 - "sanitize_key"
Cohesion: 0.18
Nodes (3): E2EE, SSEClient, WebSocketChatClient

### Community 14 - "LawyerGrid"
Cohesion: 0.36
Nodes (14): get_user_by_email(), Verify that /api/v1/drafting/documents/mock-upload requires authentication., register_user(), test_7day_auto_approval_window(), test_accept_drafting_request(), test_cancel_drafting_request(), test_counter_proposal_flow(), test_create_drafting_request() (+6 more)

### Community 15 - "calendar.py"
Cohesion: 0.20
Nodes (9): AuditLog, now(), datetime, UserConsent, WebhookEvent, request_erasure(), Reset script: delete ALL users (lawyers, clients, admin) and related data, then, test_dpdpa_consent_enforcement_and_logging() (+1 more)

### Community 16 - "check_clock_drift"
Cohesion: 0.38
Nodes (3): Any, BackgroundTaskManager, Enqueue an async background task safely without blocking request completion.

### Community 17 - "8dcb01bed07f_initial_schema.py"
Cohesion: 0.13
Nodes (14): 🛡️ **Admin Console**, 🛠️ Architecture & Tech Stack, 🔍 **Client Portal & Legal Marketplace**, 🚀 Getting Started, 🌟 Key Features, 💼 **Lawyer Portal**, 📄 License & Legal Notice, Option A: Quickstart with Docker Compose (Recommended) (+6 more)

### Community 18 - "9d0be6640444_add_aadhaar_and_profile_picture.py"
Cohesion: 0.11
Nodes (32): at(), Bo(), Bs(), Ds(), ea(), Fo(), Fs(), Go() (+24 more)

### Community 19 - "i"
Cohesion: 0.12
Nodes (16): Ae(), br, cr(), dn(), ee(), er(), Et(), fe() (+8 more)

### Community 20 - "ntp_now"
Cohesion: 0.05
Nodes (44): get_settings(), Settings, check_clock_drift(), _get_servers(), ntp_now(), ntp_now_ist(), NtpStatus, datetime (+36 more)

### Community 23 - "er"
Cohesion: 0.19
Nodes (23): User, admin_metrics(), get_admin_payouts(), get_audit_logs(), get_ntp_status(), get_platform_feedback(), list_disputes(), list_drafting_transactions() (+15 more)

### Community 26 - "_e"
Cohesion: 0.21
Nodes (11): an(), cn(), _e(), he(), nn(), on(), pe(), qe() (+3 more)

### Community 28 - "T"
Cohesion: 0.23
Nodes (19): attachCommentListEvents(), changePage(), changeZoom(), cleanPdfText(), closeAnnotatorModal(), deleteComment(), highlightCommentInSidebar(), openAddCommentPrompt() (+11 more)

### Community 29 - "80394484e25e_add_phonepe_transaction_id.py"
Cohesion: 0.36
Nodes (7): main(), _print_human(), _query_server(), ntp_sync_check.py ----------------- CERT-In / DPDP NTP Compliance — Standalone c, Query a single NTP server, return structured result dict., Run NTP drift checks. Returns 0 on success, 1 on failure., run_check()

### Community 30 - "bookings.py"
Cohesion: 0.14
Nodes (13): Application-Level Implementation, Cron Job Setup (All Servers), Docker / Container Configuration, Environment Variables, Host OS Configuration (Linux Servers), Incident Response, Indian Government NTP Servers, Option A: chrony (Recommended for production) (+5 more)

### Community 31 - "pdf-annotator.js"
Cohesion: 0.22
Nodes (5): PlatformFeedback, public_stats(), Public endpoint — no auth required. Returns live platform statistics for the hom, Public endpoint allowing users to submit platform feedback., submit_feedback()

### Community 33 - "NTP Time Synchronization — Compliance Runbook"
Cohesion: 0.32
Nodes (7): Verify that SQL injection strings in registration input fields are safely parame, Verify that SQL injection attempt in login payload is rejected harmlessly., Verify that right-to-erasure endpoint executes parameterized ORM delete statemen, register_user(), test_erasure_endpoint_with_sql_characters(), test_sql_injection_in_login_credentials(), test_sql_injection_in_registration_name()

### Community 34 - "LexAPI"
Cohesion: 0.09
Nodes (13): lifespan(), _validate_ws_user_and_booking(), Verify that requests exceeding the auth limit return HTTP 429 with Retry-After h, Verify per-account and per-IP exponential backoff triggers after max free attemp, Verify that rate limit tier thresholds are dynamically configurable via Settings, Verify that 5 rate limit violations trigger a 15-minute 403 IP block., Verify that disabling rate_limit_enabled setting allows requests without limits., test_auth_exponential_backoff() (+5 more)

### Community 37 - "firebase-phone-auth.js"
Cohesion: 0.39
Nodes (6): _clearRecaptcha(), confirmOtp(), _hideOtpModal(), _showModalError(), _showOtpModal(), startPhoneVerification()

### Community 38 - "booking_service.py"
Cohesion: 0.08
Nodes (37): create_access_token(), hash_password(), Revoke a JWT by adding its jti to the revocation blocklist., Hash a raw password using Argon2id (OWASP #1 recommendation)., Verify raw password against stored hash.     Supports Argon2id natively with bac, revoke_jti(), verify_password(), test_dispute_intermediary_shield() (+29 more)

### Community 39 - "Booking"
Cohesion: 0.25
Nodes (3): MarketplaceUser, Locust Performance & Concurrency Load Benchmark Suite for VidhiMeet. Simulates c, HttpUser

### Community 40 - "verify_ntp_compliance"
Cohesion: 0.22
Nodes (12): a(), B(), c(), d(), f(), gn(), or(), p() (+4 more)

### Community 41 - "register"
Cohesion: 0.06
Nodes (37): as(), be(), ce(), de(), dr(), dt(), ft(), g() (+29 more)

### Community 42 - "README.md"
Cohesion: 0.64
Nodes (8): create_confirmed_booking(), register_user(), test_cancelled_slot_relisting(), test_client_cancel_between_2h_and_24h_partial_refund(), test_client_cancel_more_than_24h_full_refund(), test_client_cancel_under_2h_zero_refund(), test_lawyer_cancel_full_refund_plus_voucher(), verify_lawyer()

### Community 44 - "test_marketplace.py"
Cohesion: 0.29
Nodes (6): Verify HTTP exceptions return structured error format., Verify invalid request payloads produce sanitized clean error lists., Verify unhandled 500 exceptions return sanitized public message with request_id, test_http_exception_handling(), test_unhandled_500_error_handling(), test_validation_error_handling()

### Community 45 - "cookie-consent.js"
Cohesion: 0.70
Nodes (4): getSavedConsent(), init(), injectDOM(), saveConsent()

### Community 47 - "LawyerProfile"
Cohesion: 0.09
Nodes (20): get_db(), LawyerProfile, drafting_document_presign(), download_lawyer_document(), get_my_profile(), lawyer_document_confirm(), lawyer_document_mock_upload(), lawyer_document_presign() (+12 more)

### Community 53 - "test_marketplace.py"
Cohesion: 0.33
Nodes (5): End-to-End (E2E) Browser Automation Test Suite for VidhiMeet Marketplace. Valida, Verify static html frontend structure and accessibility elements., Validates basic title and meta assertion logic for frontend marketplace., test_client_portal_markup_integrity(), test_marketplace_page_title()

### Community 54 - "calendar.py"
Cohesion: 0.20
Nodes (19): AsyncSession, LawyerBankAccount, One-per-lawyer bank account for payout and UPI identity verification., add_bank_account(), _bank_account_out(), delete_bank_account(), get_bank_account(), initiate_upi_verification() (+11 more)

### Community 55 - "LawyerBankAccount"
Cohesion: 0.05
Nodes (60): Booking, Message, Review, Voucher, booking_for_participant(), cancel_booking(), cancellation_preview(), complete_booking() (+52 more)

### Community 57 - "env.py"
Cohesion: 0.14
Nodes (14): http_exception_handler(), integrity_exception_handler(), Exception, Request, HTTP Exception Handler:     - Private Layer: Log warning/info with request ID an, Validation Exception Handler:     - Private Layer: Log detailed field errors to, Database Integrity Exception Handler:     - Private Layer: Log full database err, Global Fallback Exception Handler for unexpected server failures (500):     - Pr (+6 more)

### Community 58 - "test_bank_account.py"
Cohesion: 0.12
Nodes (15): Tests for Lawyer Bank Account management and UPI Reverse Penny Drop verification, Adding a second bank account returns 409 Conflict., Verify bank account endpoint marks account verified., Calling /verify without a bank account returns 404., Lawyer can retrieve their bank account., Editing IFSC resets the verified flag., Lawyer can add a bank account; account number is masked in response., Lawyer can delete their bank account. (+7 more)

### Community 60 - "decode_token"
Cohesion: 0.24
Nodes (10): authenticate_stream_user(), Request, Session, Server-Sent Events (SSE) stream endpoint for real-time notifications and UI auto, sse_event_stream(), current_user(), decode_token(), optional_user() (+2 more)

### Community 61 - "reset_users.py"
Cohesion: 0.11
Nodes (20): EncryptedString, ConnectionManager, _save_ws_message(), websocket_chat_endpoint(), decrypt_field(), encrypt_field(), _get_fernet_cipher(), Enforce strict participant boundary isolation (BOLA/IDOR defense). (+12 more)

## Knowledge Gaps
- **67 isolated node(s):** `colors`, `metrics`, `pendingLawyers`, `rejectedLawyers`, `users` (+62 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **12 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `User` connect `er` to `LexAPI`, `booking_service.py`, `processEvent`, `User`, `audit`, `README.md`, `LawyerGrid`, `calendar.py`, `LawyerProfile`, `ntp_now`, `calendar.py`, `LawyerBankAccount`, `decode_token`, `reset_users.py`, `pdf-annotator.js`?**
  _High betweenness centrality (0.057) - this node is a cross-community bridge._
- **Why does `s()` connect `je` to `main.py`, `mr`, `app.js`, `daily-js.js`, `verify_ntp_compliance`, `register`, `toast`, `9d0be6640444_add_aadhaar_and_profile_picture.py`, `i`?**
  _High betweenness centrality (0.046) - this node is a cross-community bridge._
- **Why does `LexAPI` connect `lawyer.js` to `mr`, `T`, `daily-js.js`?**
  _High betweenness centrality (0.035) - this node is a cross-community bridge._
- **Are the 25 inferred relationships involving `User` (e.g. with `lifespan()` and `Base`) actually correct?**
  _`User` has 25 INFERRED edges - model-reasoned connections that need verification._
- **Are the 40 inferred relationships involving `Role` (e.g. with `Base` and `AdminPayoutAccountOut`) actually correct?**
  _`Role` has 40 INFERRED edges - model-reasoned connections that need verification._
- **Are the 42 inferred relationships involving `Practice` (e.g. with `Base` and `AdminPayoutAccountOut`) actually correct?**
  _`Practice` has 42 INFERRED edges - model-reasoned connections that need verification._
- **Are the 40 inferred relationships involving `BookingStatus` (e.g. with `Base` and `AdminPayoutAccountOut`) actually correct?**
  _`BookingStatus` has 40 INFERRED edges - model-reasoned connections that need verification._