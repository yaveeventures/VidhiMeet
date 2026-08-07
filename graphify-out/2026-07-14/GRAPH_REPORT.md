# Graph Report - New project  (2026-07-14)

## Corpus Check
- 26 files · ~31,806 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 560 nodes · 1644 edges · 27 communities (22 shown, 5 thin omitted)
- Extraction: 87% EXTRACTED · 13% INFERRED · 0% AMBIGUOUS · INFERRED: 211 edges (avg confidence: 0.57)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- main.py
- mr
- je
- lawyer.js
- app.js
- daily-js.js
- admin.js
- i
- o
- _e
- Fo
- ge
- T
- Settings
- LawyerGrid
- T
- graphify.md
- graphify.md
- __init__.py
- Practice
- Booking
- register
- current_user
- lawyer_document_mock_upload

## God Nodes (most connected - your core abstractions)
1. `User` - 51 edges
2. `je()` - 39 edges
3. `i()` - 34 edges
4. `o()` - 32 edges
5. `mr` - 32 edges
6. `LexAPI` - 30 edges
7. `r()` - 30 edges
8. `setup()` - 29 edges
9. `gn()` - 28 edges
10. `Practice` - 24 edges

## Surprising Connections (you probably didn't know these)
- `$()` --indirect_call--> `s()`  [INFERRED]
  admin.js → daily-js.js
- `darken()` --indirect_call--> `p()`  [INFERRED]
  app.js → daily-js.js
- `test_meeting_token_endpoint()` --indirect_call--> `User`  [INFERRED]
  tests/test_api.py → backend/models.py
- `test_verified_reviews_only()` --indirect_call--> `User`  [INFERRED]
  tests/test_api.py → backend/models.py
- `test_dpdpa_consent_enforcement_and_logging()` --indirect_call--> `User`  [INFERRED]
  tests/test_compliance.py → backend/models.py

## Import Cycles
- None detected.

## Communities (27 total, 5 thin omitted)

### Community 0 - "main.py"
Cohesion: 0.14
Nodes (39): booking_for_participant(), complete_booking(), confirm_document(), confirm_payment(), dispute_booking(), document_upload(), download_lawyer_document(), get_audit_logs() (+31 more)

### Community 1 - "mr"
Cohesion: 0.14
Nodes (9): Ae(), ar(), br, fn(), hn(), ir(), mr, pr() (+1 more)

### Community 2 - "je"
Cohesion: 0.07
Nodes (10): B(), be(), bn(), je(), N(), sn(), te(), we() (+2 more)

### Community 3 - "lawyer.js"
Cohesion: 0.10
Nodes (49): checkAdminSession(), LexAPI, openChatModal(), $(), k(), LexE2EE, aadhaarFileEl, barLicenceFileEl (+41 more)

### Community 4 - "app.js"
Cohesion: 0.08
Nodes (46): _attemptReconnect(), backdrop, booking, bookingView(), _clearReconnectOverlay(), close(), content, darken() (+38 more)

### Community 5 - "daily-js.js"
Cohesion: 0.06
Nodes (36): as(), ce(), cr(), de(), dt(), er(), ft(), g() (+28 more)

### Community 6 - "admin.js"
Cohesion: 0.15
Nodes (29): auditLogs, colors, decideVerification(), disputes, escapeHtml(), handleSaveFees(), lawyerMap, loadData() (+21 more)

### Community 7 - "i"
Cohesion: 0.21
Nodes (11): ge(), ie(), le(), me(), ne(), oe(), qn(), ue() (+3 more)

### Community 8 - "o"
Cohesion: 0.18
Nodes (20): a(), Bt(), c(), d(), ee(), f(), gn(), gt() (+12 more)

### Community 9 - "_e"
Cohesion: 0.15
Nodes (12): an(), cn(), dr(), _e(), he(), nn(), on(), pe() (+4 more)

### Community 11 - "ge"
Cohesion: 0.17
Nodes (22): at(), Bo(), Bs(), Ds(), ea(), Fo(), Fs(), Go() (+14 more)

### Community 12 - "T"
Cohesion: 0.16
Nodes (23): ct(), dn(), Es(), Et(), fe(), i(), In(), It() (+15 more)

### Community 13 - "Settings"
Cohesion: 0.10
Nodes (23): get_settings(), Settings, Base, get_db(), AuditLog, EncryptedString, Message, now() (+15 more)

### Community 14 - "LawyerGrid"
Cohesion: 0.29
Nodes (6): Full-stack development, LawyerGrid, Local static preview, Production architecture, Production note, Required before launch

### Community 16 - "T"
Cohesion: 0.18
Nodes (10): ia(), is(), La(), q(), sa(), T(), Ua(), v() (+2 more)

### Community 22 - "Practice"
Cohesion: 0.34
Nodes (20): lawyers(), BookingStatus, Practice, Role, AuditLogOut, BookingCreate, BookingOut, LawyerOut (+12 more)

### Community 23 - "Booking"
Cohesion: 0.18
Nodes (9): admin_metrics(), create_booking(), Booking, LawyerProfile, create_payment_intent(), get_daily_meeting_details(), validate_intake(), test_meeting_token_endpoint() (+1 more)

### Community 24 - "register"
Cohesion: 0.36
Nodes (8): login(), refresh_token(), register(), RefreshToken, create_access_token(), verify_password(), issue_refresh_token(), Session

### Community 25 - "current_user"
Cohesion: 0.50
Nodes (4): current_user(), decode_token(), Session, HTTPAuthorizationCredentials

## Knowledge Gaps
- **41 isolated node(s):** `colors`, `metrics`, `pendingLawyers`, `users`, `transactions` (+36 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **5 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `s()` connect `o` to `mr`, `je`, `lawyer.js`, `daily-js.js`, `admin.js`, `ge`, `T`, `T`?**
  _High betweenness centrality (0.103) - this node is a cross-community bridge._
- **Why does `p()` connect `o` to `mr`, `T`, `app.js`, `daily-js.js`?**
  _High betweenness centrality (0.070) - this node is a cross-community bridge._
- **Why does `darken()` connect `app.js` to `o`?**
  _High betweenness centrality (0.068) - this node is a cross-community bridge._
- **Are the 11 inferred relationships involving `User` (e.g. with `download_lawyer_document()` and `lawyers()`) actually correct?**
  _`User` has 11 INFERRED edges - model-reasoned connections that need verification._
- **Are the 25 inferred relationships involving `i()` (e.g. with `an()` and `.captureUserFeedback()`) actually correct?**
  _`i()` has 25 INFERRED edges - model-reasoned connections that need verification._
- **Are the 15 inferred relationships involving `o()` (e.g. with `.captureUserFeedback()` and `.eventFromMessage()`) actually correct?**
  _`o()` has 15 INFERRED edges - model-reasoned connections that need verification._
- **What connects `colors`, `metrics`, `pendingLawyers` to the rest of the system?**
  _44 weakly-connected nodes found - possible documentation gaps or missing edges._