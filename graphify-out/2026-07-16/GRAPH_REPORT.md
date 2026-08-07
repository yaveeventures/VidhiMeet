# Graph Report - New project  (2026-07-15)

## Corpus Check
- 26 files · ~34,540 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 569 nodes · 1665 edges · 23 communities (19 shown, 4 thin omitted)
- Extraction: 87% EXTRACTED · 13% INFERRED · 0% AMBIGUOUS · INFERRED: 213 edges (avg confidence: 0.57)
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
- qt

## God Nodes (most connected - your core abstractions)
1. `User` - 52 edges
2. `je()` - 39 edges
3. `i()` - 34 edges
4. `o()` - 32 edges
5. `mr` - 32 edges
6. `LexAPI` - 30 edges
7. `r()` - 30 edges
8. `setup()` - 29 edges
9. `gn()` - 28 edges
10. `Booking` - 25 edges

## Surprising Connections (you probably didn't know these)
- `$()` --indirect_call--> `s()`  [INFERRED]
  admin.js → daily-js.js
- `darken()` --indirect_call--> `p()`  [INFERRED]
  app.js → daily-js.js
- `$()` --indirect_call--> `s()`  [INFERRED]
  lawyer.js → daily-js.js
- `handleFileUpload()` --indirect_call--> `v()`  [INFERRED]
  lawyer.js → daily-js.js
- `handleSaveProfile()` --indirect_call--> `v()`  [INFERRED]
  lawyer.js → daily-js.js

## Import Cycles
- None detected.

## Communities (23 total, 4 thin omitted)

### Community 0 - "main.py"
Cohesion: 0.05
Nodes (106): get_settings(), Base, get_db(), admin_metrics(), booking_for_participant(), complete_booking(), confirm_document(), confirm_payment() (+98 more)

### Community 1 - "mr"
Cohesion: 0.10
Nodes (15): br, dt(), fn(), ft(), hn(), ht(), ir(), mr (+7 more)

### Community 2 - "je"
Cohesion: 0.07
Nodes (8): B(), bn(), je(), N(), sn(), we(), wn(), xe()

### Community 3 - "lawyer.js"
Cohesion: 0.10
Nodes (47): openChatModal(), $(), LexE2EE, aadhaarFileEl, barLicenceFileEl, bookings, calculateExperience(), chatBackBtn (+39 more)

### Community 4 - "app.js"
Cohesion: 0.08
Nodes (48): checkAdminSession(), LexAPI, _attemptReconnect(), backdrop, booking, bookingView(), _clearReconnectOverlay(), close() (+40 more)

### Community 5 - "daily-js.js"
Cohesion: 0.08
Nodes (21): as(), ce(), de(), dr(), g(), ia(), Jn(), ke() (+13 more)

### Community 6 - "admin.js"
Cohesion: 0.14
Nodes (31): auditLogs, colors, decideVerification(), disputes, escapeHtml(), handleSaveFees(), lawyerMap, loadData() (+23 more)

### Community 7 - "i"
Cohesion: 0.21
Nodes (12): ge(), ie(), le(), me(), ne(), oe(), te(), xn() (+4 more)

### Community 8 - "o"
Cohesion: 0.18
Nodes (20): a(), Bt(), c(), d(), f(), gn(), Kn(), l() (+12 more)

### Community 9 - "_e"
Cohesion: 0.18
Nodes (12): an(), be(), cn(), _e(), he(), nn(), on(), pe() (+4 more)

### Community 10 - "Fo"
Cohesion: 0.20
Nodes (9): ar(), cr(), er(), hr(), kr(), lr(), sr(), Wt() (+1 more)

### Community 11 - "ge"
Cohesion: 0.17
Nodes (22): at(), Bo(), Bs(), Ds(), ea(), Fo(), Fs(), Go() (+14 more)

### Community 12 - "T"
Cohesion: 0.18
Nodes (22): ct(), dn(), Es(), Et(), fe(), i(), In(), It() (+14 more)

### Community 14 - "LawyerGrid"
Cohesion: 0.29
Nodes (6): Full-stack development, LawyerGrid, Local static preview, Production architecture, Production note, Required before launch

### Community 16 - "T"
Cohesion: 0.36
Nodes (8): h(), is(), rs(), sa(), T(), Ua(), v(), va()

### Community 23 - "qt"
Cohesion: 0.14
Nodes (7): Ae(), ee(), gt(), qn(), qt, re(), ue()

## Knowledge Gaps
- **42 isolated node(s):** `colors`, `metrics`, `pendingLawyers`, `users`, `transactions` (+37 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `s()` connect `o` to `mr`, `je`, `lawyer.js`, `daily-js.js`, `admin.js`, `Fo`, `ge`, `T`, `T`, `qt`?**
  _High betweenness centrality (0.104) - this node is a cross-community bridge._
- **Why does `p()` connect `o` to `T`, `app.js`, `daily-js.js`, `qt`?**
  _High betweenness centrality (0.068) - this node is a cross-community bridge._
- **Why does `je()` connect `je` to `_e`, `daily-js.js`?**
  _High betweenness centrality (0.066) - this node is a cross-community bridge._
- **Are the 12 inferred relationships involving `User` (e.g. with `download_lawyer_document()` and `lawyers()`) actually correct?**
  _`User` has 12 INFERRED edges - model-reasoned connections that need verification._
- **Are the 25 inferred relationships involving `i()` (e.g. with `an()` and `.captureUserFeedback()`) actually correct?**
  _`i()` has 25 INFERRED edges - model-reasoned connections that need verification._
- **Are the 15 inferred relationships involving `o()` (e.g. with `.captureUserFeedback()` and `.eventFromMessage()`) actually correct?**
  _`o()` has 15 INFERRED edges - model-reasoned connections that need verification._
- **What connects `colors`, `metrics`, `pendingLawyers` to the rest of the system?**
  _46 weakly-connected nodes found - possible documentation gaps or missing edges._