# Graph Report - New project  (2026-07-29)

## Corpus Check
- 53 files · ~62,816 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 907 nodes · 2678 edges · 43 communities (35 shown, 8 thin omitted)
- Extraction: 87% EXTRACTED · 13% INFERRED · 0% AMBIGUOUS · INFERRED: 354 edges (avg confidence: 0.58)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- main.py
- mr
- je
- lawyer.js
- app.js
- daily-js.js
- main.py
- i
- o
- Base
- audit
- Session
- T
- qt
- LawyerGrid
- check_clock_drift
- graphify.md
- graphify.md
- __init__.py
- Booking
- er
- models.py
- processEvent
- _e
- auth.py
- T
- test_drafting.py
- pdf-annotator.js
- data_retention_purge.py
- NTP Time Synchronization — Compliance Runbook
- gn
- SlidingWindowRateLimiter
- qt
- firebase-phone-auth.js
- ntp_sync_check.py
- Booking
- br
- get_settings

## God Nodes (most connected - your core abstractions)
1. `User` - 105 edges
2. `audit()` - 49 edges
3. `Role` - 44 edges
4. `LexAPI` - 43 edges
5. `Practice` - 42 edges
6. `je()` - 39 edges
7. `LawyerProfile` - 36 edges
8. `Booking` - 36 edges
9. `BookingStatus` - 35 edges
10. `i()` - 34 edges

## Surprising Connections (you probably didn't know these)
- `test_lawyer_complete_booking_duration_restriction()` --indirect_call--> `User`  [INFERRED]
  tests/test_api.py → backend/models.py
- `test_meeting_token_endpoint()` --indirect_call--> `User`  [INFERRED]
  tests/test_api.py → backend/models.py
- `test_verified_reviews_only()` --indirect_call--> `User`  [INFERRED]
  tests/test_api.py → backend/models.py
- `test_phonepe_verify_webhook_routes_correctly()` --indirect_call--> `User`  [INFERRED]
  tests/test_bank_account.py → backend/models.py
- `test_dpdpa_consent_enforcement_and_logging()` --indirect_call--> `User`  [INFERRED]
  tests/test_compliance.py → backend/models.py

## Import Cycles
- None detected.

## Communities (43 total, 8 thin omitted)

### Community 0 - "main.py"
Cohesion: 0.31
Nodes (10): login(), Session, refresh(), register(), lawyer_document_confirm(), update_my_profile(), audit(), issue_refresh_token() (+2 more)

### Community 1 - "mr"
Cohesion: 0.08
Nodes (65): $(), checkInactivity(), checkSessionOnForeground(), initInactivityTracker(), LexAPI, logoutDueToInactivity(), resetTimer(), openChatModal() (+57 more)

### Community 2 - "je"
Cohesion: 0.05
Nodes (40): as(), be(), Bt(), de(), dr(), dt(), ee(), g() (+32 more)

### Community 3 - "lawyer.js"
Cohesion: 0.08
Nodes (51): _attemptReconnect(), backdrop, booking, bookingView(), checkHashRoute(), _clearReconnectOverlay(), close(), content (+43 more)

### Community 4 - "app.js"
Cohesion: 0.12
Nodes (10): Ae(), ar(), br, fn(), ir(), mr, pr(), q() (+2 more)

### Community 5 - "daily-js.js"
Cohesion: 0.12
Nodes (36): $(), auditLogs, checkAdminSession(), colors, decideVerification(), disputes, draftingTransactions, escapeHtml() (+28 more)

### Community 6 - "main.py"
Cohesion: 0.22
Nodes (19): Message, Review, booking_for_participant(), complete_booking(), confirm_document(), confirm_payment(), create_review(), dispute_booking() (+11 more)

### Community 8 - "o"
Cohesion: 0.13
Nodes (25): Bo(), Ds(), ea(), Fo(), Fs(), Go(), h(), Ho() (+17 more)

### Community 9 - "Base"
Cohesion: 0.17
Nodes (11): get_db(), AuditLog, LawyerProfile, UserConsent, request_erasure(), test_lawyer_complete_booking_duration_restriction(), test_meeting_token_endpoint(), test_verified_reviews_only() (+3 more)

### Community 10 - "audit"
Cohesion: 0.16
Nodes (23): DraftComment, DraftingProposal, DraftingRequest, accept_drafting_proposal(), accept_drafting_request(), add_draft_comment(), approve_draft(), cancel_drafting_request() (+15 more)

### Community 11 - "Session"
Cohesion: 0.25
Nodes (6): Verify that requests exceeding the auth limit return HTTP 429 with Retry-After h, Verify that 5 rate limit violations trigger a 15-minute 403 IP block., Verify that disabling rate_limit_enabled setting allows requests without limits., test_auth_rate_limiting(), test_disabled_rate_limiter_setting(), test_ip_abuse_lockout()

### Community 12 - "T"
Cohesion: 0.13
Nodes (18): B(), bn(), ge(), ie(), Jn(), me(), N(), ne() (+10 more)

### Community 13 - "qt"
Cohesion: 0.14
Nodes (25): at(), Bs(), ct(), dn(), Es(), Et(), fe(), ft() (+17 more)

### Community 14 - "LawyerGrid"
Cohesion: 0.29
Nodes (6): Full-stack development, LawyerGrid, Local static preview, Production architecture, Production note, Required before launch

### Community 16 - "check_clock_drift"
Cohesion: 0.15
Nodes (13): startup(), check_clock_drift(), NtpStatus, Compare the system clock against the first reachable NTP server.      Returns a, Simulated tiny drift (0.05s) must set within_tolerance=True., check_clock_drift() must return a dict with all required NtpStatus keys., within_tolerance must be a boolean., When all NTP servers fail, within_tolerance must be False and server must be 'un (+5 more)

### Community 22 - "Booking"
Cohesion: 0.08
Nodes (34): LawyerBankAccount, One-per-lawyer bank account for payout and UPI identity verification., add_bank_account(), _bank_account_out(), delete_bank_account(), get_bank_account(), initiate_upi_verification(), _mask_account() (+26 more)

### Community 23 - "er"
Cohesion: 0.14
Nodes (13): test_ntp.py ----------- Tests for NTP time synchronization (CERT-In / DPDP compl, GET /api/v1/admin/ntp-status must return 401 without a valid token., ntp_now() must always return a UTC-aware datetime regardless of server state., ntp_now_ist() must return a datetime in IST (UTC+05:30)., When all NTP servers are unreachable, ntp_now() must fall back to system clock g, drift_seconds must be a float., Simulated large drift (10s) must set within_tolerance=False., test_admin_ntp_status_endpoint_requires_auth() (+5 more)

### Community 24 - "models.py"
Cohesion: 0.05
Nodes (82): Base, Request, security_headers_and_rate_limit(), BookingStatus, DraftingStatus, EncryptedString, Practice, ProposalStatus (+74 more)

### Community 25 - "processEvent"
Cohesion: 0.19
Nodes (22): User, admin_metrics(), get_admin_payouts(), get_audit_logs(), get_ntp_status(), list_disputes(), list_drafting_transactions(), list_pending_lawyers() (+14 more)

### Community 26 - "_e"
Cohesion: 0.18
Nodes (11): an(), cn(), _e(), he(), nn(), on(), pe(), qe() (+3 more)

### Community 27 - "auth.py"
Cohesion: 0.29
Nodes (10): _get_servers(), ntp_now(), ntp_now_ist(), datetime, _query_ntp_server(), ntp_time.py ----------- NTP time synchronization for CERT-In and DPDP forensic t, Return the current NPL/NIC-sourced time in Indian Standard Time (UTC+5:30)., Send a single NTP client request to *host* and return the transmit     timestamp (+2 more)

### Community 30 - "test_drafting.py"
Cohesion: 0.36
Nodes (14): get_user_by_email(), Verify that /api/v1/drafting/documents/mock-upload requires authentication., register_user(), test_7day_auto_approval_window(), test_accept_drafting_request(), test_cancel_drafting_request(), test_counter_proposal_flow(), test_create_drafting_request() (+6 more)

### Community 31 - "pdf-annotator.js"
Cohesion: 0.12
Nodes (23): create_access_token(), hash_password(), Verify that booking document presign returns 15-minute expiry (900s)., Verify that drafting document presign returns 15-minute expiry (900s)., Verify that a document access token issued > 15 minutes ago (900s) is rejected w, test_booking_document_presign_expiry(), test_drafting_document_presign_expiry(), test_expired_document_access_link_rejection() (+15 more)

### Community 32 - "data_retention_purge.py"
Cohesion: 0.24
Nodes (16): _cutoff(), _ensure_tz(), log_purge_audit(), _now(), purge_expired_bookings(), purge_expired_tokens(), purge_withdrawn_consents(), datetime (+8 more)

### Community 33 - "NTP Time Synchronization — Compliance Runbook"
Cohesion: 0.13
Nodes (14): Application-Level Implementation, Cron Job Setup (All Servers), Docker / Container Configuration, Environment Variables, Host OS Configuration (Linux Servers), Incident Response, Indian Government NTP Servers, NTP Time Synchronization — Compliance Runbook (+6 more)

### Community 34 - "gn"
Cohesion: 0.18
Nodes (25): a(), c(), ce(), cr(), d(), er(), f(), gn() (+17 more)

### Community 37 - "firebase-phone-auth.js"
Cohesion: 0.39
Nodes (6): _clearRecaptcha(), confirmOtp(), _hideOtpModal(), _showModalError(), _showOtpModal(), startPhoneVerification()

### Community 38 - "ntp_sync_check.py"
Cohesion: 0.36
Nodes (7): main(), _print_human(), _query_server(), ntp_sync_check.py ----------------- CERT-In / DPDP NTP Compliance — Standalone c, Query a single NTP server, return structured result dict., Run NTP drift checks. Returns 0 on success, 1 on failure., run_check()

### Community 39 - "Booking"
Cohesion: 0.14
Nodes (13): Booking, now(), datetime, create_booking(), Request, create_payment_intent(), create_phonepe_payment(), get_jitsi_meeting_details() (+5 more)

### Community 40 - "br"
Cohesion: 0.24
Nodes (15): changePage(), changeZoom(), closeAnnotatorModal(), deleteComment(), highlightCommentInSidebar(), openAddCommentPrompt(), renderAnnotatorModalContent(), renderCommentsList() (+7 more)

## Knowledge Gaps
- **56 isolated node(s):** `colors`, `metrics`, `pendingLawyers`, `users`, `transactions` (+51 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **8 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `User` connect `processEvent` to `main.py`, `main.py`, `Booking`, `Base`, `audit`, `Booking`, `er`, `models.py`, `test_drafting.py`, `pdf-annotator.js`?**
  _High betweenness centrality (0.054) - this node is a cross-community bridge._
- **Why does `LexAPI` connect `mr` to `br`, `lawyer.js`, `daily-js.js`?**
  _High betweenness centrality (0.049) - this node is a cross-community bridge._
- **Why does `s()` connect `gn` to `mr`, `je`, `daily-js.js`, `o`, `T`, `qt`?**
  _High betweenness centrality (0.047) - this node is a cross-community bridge._
- **Are the 16 inferred relationships involving `User` (e.g. with `Base` and `login()`) actually correct?**
  _`User` has 16 INFERRED edges - model-reasoned connections that need verification._
- **Are the 26 inferred relationships involving `Role` (e.g. with `Base` and `AdminPayoutAccountOut`) actually correct?**
  _`Role` has 26 INFERRED edges - model-reasoned connections that need verification._
- **Are the 28 inferred relationships involving `Practice` (e.g. with `Base` and `AdminPayoutAccountOut`) actually correct?**
  _`Practice` has 28 INFERRED edges - model-reasoned connections that need verification._
- **What connects `LawyerGrid backend package.`, `One-per-lawyer bank account for payout and UPI identity verification.`, `ntp_time.py ----------- NTP time synchronization for CERT-In and DPDP forensic t` to the rest of the system?**
  _124 weakly-connected nodes found - possible documentation gaps or missing edges._