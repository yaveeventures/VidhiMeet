# Graph Report - New project  (2026-07-20)

## Corpus Check
- 31 files · ~46,590 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 675 nodes · 2057 edges · 24 communities (20 shown, 4 thin omitted)
- Extraction: 84% EXTRACTED · 16% INFERRED · 0% AMBIGUOUS · INFERRED: 319 edges (avg confidence: 0.57)
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
- Booking

## God Nodes (most connected - your core abstractions)
1. `User` - 75 edges
2. `LexAPI` - 40 edges
3. `je()` - 39 edges
4. `audit()` - 36 edges
5. `Practice` - 35 edges
6. `i()` - 34 edges
7. `o()` - 32 edges
8. `mr` - 32 edges
9. `Role` - 31 edges
10. `LawyerProfile` - 31 edges

## Surprising Connections (you probably didn't know these)
- `$()` --indirect_call--> `s()`  [INFERRED]
  admin.js → daily-js.js
- `checkAdminSession()` --references--> `LexAPI`  [EXTRACTED]
  admin.js → api-client.js
- `darken()` --indirect_call--> `p()`  [INFERRED]
  app.js → daily-js.js
- `get_user_by_email()` --indirect_call--> `User`  [INFERRED]
  tests/test_drafting.py → backend/models.py
- `verify_lawyer()` --indirect_call--> `LawyerProfile`  [INFERRED]
  tests/test_drafting.py → backend/models.py

## Import Cycles
- None detected.

## Communities (24 total, 4 thin omitted)

### Community 0 - "main.py"
Cohesion: 0.05
Nodes (104): get_db(), accept_drafting_proposal(), accept_drafting_request(), add_bank_account(), admin_metrics(), approve_draft(), _bank_account_out(), booking_for_participant() (+96 more)

### Community 1 - "mr"
Cohesion: 0.10
Nodes (12): Ae(), ar(), br, ir(), kr(), mr, pr(), q() (+4 more)

### Community 2 - "je"
Cohesion: 0.05
Nodes (22): an(), B(), be(), bn(), cn(), _e(), he(), je() (+14 more)

### Community 3 - "lawyer.js"
Cohesion: 0.08
Nodes (54): openChatModal(), $(), LexE2EE, aadhaarFileEl, barLicenceFileEl, bookings, calculateExperience(), chatBackBtn (+46 more)

### Community 4 - "app.js"
Cohesion: 0.08
Nodes (57): checkInactivity(), checkSessionOnForeground(), initInactivityTracker(), LexAPI, logoutDueToInactivity(), resetTimer(), _attemptReconnect(), backdrop (+49 more)

### Community 5 - "daily-js.js"
Cohesion: 0.07
Nodes (28): as(), cr(), dr(), dt(), er(), g(), ge(), hr() (+20 more)

### Community 6 - "admin.js"
Cohesion: 0.14
Nodes (32): auditLogs, checkAdminSession(), colors, decideVerification(), disputes, escapeHtml(), handleSaveFees(), lawyerMap (+24 more)

### Community 7 - "i"
Cohesion: 0.19
Nodes (20): Bo(), Ds(), ea(), Fo(), Fs(), Go(), Ho(), Ko() (+12 more)

### Community 8 - "o"
Cohesion: 0.15
Nodes (24): a(), Bt(), c(), d(), ee(), f(), gn(), gt() (+16 more)

### Community 9 - "_e"
Cohesion: 0.20
Nodes (12): ce(), de(), fn(), ft(), hn(), ht(), J(), ke() (+4 more)

### Community 10 - "Fo"
Cohesion: 0.09
Nodes (55): get_settings(), Settings, Base, BookingStatus, DraftingStatus, EncryptedString, now(), Practice (+47 more)

### Community 12 - "T"
Cohesion: 0.17
Nodes (24): at(), Bs(), ct(), dn(), Es(), Et(), fe(), i() (+16 more)

### Community 13 - "Settings"
Cohesion: 0.19
Nodes (12): h(), ia(), is(), La(), na(), ra(), rs(), sa() (+4 more)

### Community 14 - "LawyerGrid"
Cohesion: 0.29
Nodes (6): Full-stack development, LawyerGrid, Local static preview, Production architecture, Production note, Required before launch

### Community 16 - "T"
Cohesion: 0.39
Nodes (6): _clearRecaptcha(), confirmOtp(), _hideOtpModal(), _showModalError(), _showOtpModal(), startPhoneVerification()

### Community 22 - "Booking"
Cohesion: 0.12
Nodes (15): Tests for Lawyer Bank Account management and UPI Reverse Penny Drop verification, Adding a second bank account returns 409 Conflict., In demo mode (no PhonePe creds), verify auto-verifies the account., Calling /verify without a bank account returns 404., Lawyer can retrieve their bank account., Editing IFSC resets the verified flag., Lawyer can add a bank account; account number is masked in response., Lawyer can delete their bank account. (+7 more)

## Knowledge Gaps
- **42 isolated node(s):** `colors`, `metrics`, `pendingLawyers`, `users`, `transactions` (+37 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `s()` connect `o` to `je`, `lawyer.js`, `daily-js.js`, `admin.js`, `i`, `_e`, `T`, `Settings`?**
  _High betweenness centrality (0.078) - this node is a cross-community bridge._
- **Why does `LexAPI` connect `app.js` to `lawyer.js`, `admin.js`?**
  _High betweenness centrality (0.053) - this node is a cross-community bridge._
- **Why does `je()` connect `je` to `daily-js.js`?**
  _High betweenness centrality (0.049) - this node is a cross-community bridge._
- **Are the 15 inferred relationships involving `User` (e.g. with `download_lawyer_document()` and `lawyers()`) actually correct?**
  _`User` has 15 INFERRED edges - model-reasoned connections that need verification._
- **What connects `colors`, `metrics`, `pendingLawyers` to the rest of the system?**
  _59 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `main.py` be split into smaller, more focused modules?**
  _Cohesion score 0.0500738188976378 - nodes in this community are weakly interconnected._
- **Should `mr` be split into smaller, more focused modules?**
  _Cohesion score 0.1 - nodes in this community are weakly interconnected._