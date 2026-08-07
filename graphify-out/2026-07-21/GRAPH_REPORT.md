# Graph Report - New project  (2026-07-21)

## Corpus Check
- 31 files · ~46,990 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 678 nodes · 2086 edges · 24 communities (21 shown, 3 thin omitted)
- Extraction: 85% EXTRACTED · 15% INFERRED · 0% AMBIGUOUS · INFERRED: 322 edges (avg confidence: 0.58)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- main.py
- mr
- je
- lawyer.js
- app.js
- daily-js.js
- i
- o
- T
- LawyerGrid
- T
- graphify.md
- graphify.md
- __init__.py
- Booking
- er
- models.py
- _e
- T
- test_drafting.py

## God Nodes (most connected - your core abstractions)
1. `User` - 76 edges
2. `LexAPI` - 40 edges
3. `je()` - 39 edges
4. `audit()` - 37 edges
5. `Practice` - 35 edges
6. `i()` - 34 edges
7. `o()` - 32 edges
8. `mr` - 32 edges
9. `Role` - 31 edges
10. `LawyerProfile` - 31 edges

## Surprising Connections (you probably didn't know these)
- `$()` --indirect_call--> `s()`  [INFERRED]
  admin.js → daily-js.js
- `darken()` --indirect_call--> `p()`  [INFERRED]
  app.js → daily-js.js
- `get_user_by_email()` --indirect_call--> `User`  [INFERRED]
  tests/test_drafting.py → backend/models.py
- `verify_lawyer()` --indirect_call--> `LawyerProfile`  [INFERRED]
  tests/test_drafting.py → backend/models.py
- `$()` --indirect_call--> `s()`  [INFERRED]
  lawyer.js → daily-js.js

## Import Cycles
- None detected.

## Communities (24 total, 3 thin omitted)

### Community 0 - "main.py"
Cohesion: 0.05
Nodes (104): get_db(), accept_drafting_proposal(), accept_drafting_request(), add_bank_account(), admin_metrics(), approve_draft(), _bank_account_out(), booking_for_participant() (+96 more)

### Community 1 - "mr"
Cohesion: 0.07
Nodes (19): Ae(), ar(), br, ee(), fn(), ft(), ir(), Kn() (+11 more)

### Community 2 - "je"
Cohesion: 0.09
Nodes (3): B(), je(), we()

### Community 3 - "lawyer.js"
Cohesion: 0.09
Nodes (53): openChatModal(), $(), LexE2EE, aadhaarFileEl, barLicenceFileEl, bookings, calculateExperience(), chatBackBtn (+45 more)

### Community 4 - "app.js"
Cohesion: 0.05
Nodes (90): auditLogs, checkAdminSession(), colors, decideVerification(), disputes, escapeHtml(), handleSaveFees(), lawyerMap (+82 more)

### Community 5 - "daily-js.js"
Cohesion: 0.07
Nodes (27): as(), ce(), cr(), de(), dr(), dt(), er(), g() (+19 more)

### Community 7 - "i"
Cohesion: 0.17
Nodes (22): at(), Bo(), Bs(), Ds(), ea(), Fo(), Fs(), Go() (+14 more)

### Community 8 - "o"
Cohesion: 0.21
Nodes (19): a(), Bt(), c(), d(), f(), gn(), gt(), l() (+11 more)

### Community 12 - "T"
Cohesion: 0.15
Nodes (26): ct(), dn(), Es(), Et(), fe(), i(), It(), J() (+18 more)

### Community 14 - "LawyerGrid"
Cohesion: 0.29
Nodes (6): Full-stack development, LawyerGrid, Local static preview, Production architecture, Production note, Required before launch

### Community 16 - "T"
Cohesion: 0.39
Nodes (6): _clearRecaptcha(), confirmOtp(), _hideOtpModal(), _showModalError(), _showOtpModal(), startPhoneVerification()

### Community 22 - "Booking"
Cohesion: 0.12
Nodes (15): Tests for Lawyer Bank Account management and UPI Reverse Penny Drop verification, Adding a second bank account returns 409 Conflict., In demo mode (no PhonePe creds), verify auto-verifies the account., Calling /verify without a bank account returns 404., Lawyer can retrieve their bank account., Editing IFSC resets the verified flag., Lawyer can add a bank account; account number is masked in response., Lawyer can delete their bank account. (+7 more)

### Community 23 - "er"
Cohesion: 0.14
Nodes (17): be(), bn(), ge(), ie(), le(), me(), N(), ne() (+9 more)

### Community 24 - "models.py"
Cohesion: 0.10
Nodes (47): get_settings(), Settings, Base, BookingStatus, DraftingStatus, EncryptedString, Message, now() (+39 more)

### Community 26 - "_e"
Cohesion: 0.14
Nodes (14): an(), cn(), _e(), he(), In(), nn(), on(), pe() (+6 more)

### Community 28 - "T"
Cohesion: 0.22
Nodes (10): h(), ia(), is(), La(), na(), ra(), rs(), sa() (+2 more)

### Community 30 - "test_drafting.py"
Cohesion: 0.51
Nodes (9): get_user_by_email(), register_user(), test_accept_drafting_request(), test_cancel_drafting_request(), test_counter_proposal_flow(), test_create_drafting_request(), test_list_drafting_requests_visibility(), test_payment_and_draft_submission_and_approval() (+1 more)

## Knowledge Gaps
- **42 isolated node(s):** `colors`, `metrics`, `pendingLawyers`, `users`, `transactions` (+37 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `s()` connect `o` to `lawyer.js`, `app.js`, `daily-js.js`, `i`, `T`, `er`?**
  _High betweenness centrality (0.077) - this node is a cross-community bridge._
- **Why does `LexAPI` connect `app.js` to `lawyer.js`, `T`?**
  _High betweenness centrality (0.053) - this node is a cross-community bridge._
- **Why does `p()` connect `o` to `mr`, `T`, `app.js`, `daily-js.js`?**
  _High betweenness centrality (0.050) - this node is a cross-community bridge._
- **Are the 16 inferred relationships involving `User` (e.g. with `download_lawyer_document()` and `lawyers()`) actually correct?**
  _`User` has 16 INFERRED edges - model-reasoned connections that need verification._
- **What connects `colors`, `metrics`, `pendingLawyers` to the rest of the system?**
  _59 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `main.py` be split into smaller, more focused modules?**
  _Cohesion score 0.052993375828021494 - nodes in this community are weakly interconnected._
- **Should `mr` be split into smaller, more focused modules?**
  _Cohesion score 0.07139079851930195 - nodes in this community are weakly interconnected._