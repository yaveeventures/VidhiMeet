# Graph Report - New project  (2026-07-10)

## Corpus Check
- 25 files · ~31,094 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 556 nodes · 1640 edges · 21 communities (17 shown, 4 thin omitted)
- Extraction: 87% EXTRACTED · 13% INFERRED · 0% AMBIGUOUS · INFERRED: 210 edges (avg confidence: 0.57)
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
- graphify.md
- graphify.md
- __init__.py
- er

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
- `checkAdminSession()` --references--> `LexAPI`  [EXTRACTED]
  admin.js → api-client.js
- `darken()` --indirect_call--> `p()`  [INFERRED]
  app.js → daily-js.js
- `$()` --indirect_call--> `s()`  [INFERRED]
  lawyer.js → daily-js.js
- `handleFileUpload()` --indirect_call--> `v()`  [INFERRED]
  lawyer.js → daily-js.js

## Import Cycles
- None detected.

## Communities (21 total, 4 thin omitted)

### Community 0 - "main.py"
Cohesion: 0.05
Nodes (103): get_settings(), Base, get_db(), admin_metrics(), booking_for_participant(), complete_booking(), confirm_document(), confirm_payment() (+95 more)

### Community 1 - "mr"
Cohesion: 0.06
Nodes (35): Ae(), ar(), br, dn(), ee(), Et(), fe(), fn() (+27 more)

### Community 2 - "je"
Cohesion: 0.07
Nodes (10): B(), be(), bn(), je(), N(), sn(), te(), we() (+2 more)

### Community 3 - "lawyer.js"
Cohesion: 0.10
Nodes (47): LexAPI, openChatModal(), $(), LexE2EE, aadhaarFileEl, barLicenceFileEl, bookings, calculateExperience() (+39 more)

### Community 4 - "app.js"
Cohesion: 0.08
Nodes (46): _attemptReconnect(), backdrop, booking, bookingView(), _clearReconnectOverlay(), close(), content, darken() (+38 more)

### Community 5 - "daily-js.js"
Cohesion: 0.07
Nodes (21): as(), at(), Bs(), ce(), de(), dt(), Es(), g() (+13 more)

### Community 6 - "admin.js"
Cohesion: 0.14
Nodes (30): auditLogs, checkAdminSession(), colors, decideVerification(), disputes, escapeHtml(), handleSaveFees(), lawyerMap (+22 more)

### Community 7 - "i"
Cohesion: 0.24
Nodes (11): ge(), ie(), le(), me(), ne(), oe(), qn(), ue() (+3 more)

### Community 8 - "o"
Cohesion: 0.20
Nodes (19): a(), c(), d(), f(), gn(), gt(), o(), or() (+11 more)

### Community 9 - "_e"
Cohesion: 0.15
Nodes (13): an(), cn(), dr(), _e(), he(), nn(), on(), pe() (+5 more)

### Community 10 - "Fo"
Cohesion: 0.23
Nodes (16): Bo(), Ds(), ea(), Fo(), Fs(), Go(), Ho(), Ko() (+8 more)

### Community 11 - "ge"
Cohesion: 0.22
Nodes (10): h(), ia(), is(), La(), na(), ra(), rs(), sa() (+2 more)

### Community 12 - "T"
Cohesion: 0.17
Nodes (17): Bt(), ct(), In(), It(), l(), Mn(), mt(), Pt() (+9 more)

### Community 14 - "LawyerGrid"
Cohesion: 0.29
Nodes (6): Full-stack development, LawyerGrid, Local static preview, Production architecture, Production note, Required before launch

### Community 22 - "er"
Cohesion: 0.40
Nodes (4): cr(), er(), hr(), lr()

## Knowledge Gaps
- **41 isolated node(s):** `colors`, `metrics`, `pendingLawyers`, `users`, `transactions` (+36 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `s()` connect `o` to `mr`, `je`, `lawyer.js`, `daily-js.js`, `admin.js`, `T`, `er`?**
  _High betweenness centrality (0.104) - this node is a cross-community bridge._
- **Why does `p()` connect `o` to `mr`, `app.js`, `daily-js.js`?**
  _High betweenness centrality (0.069) - this node is a cross-community bridge._
- **Why does `je()` connect `je` to `mr`, `daily-js.js`, `_e`?**
  _High betweenness centrality (0.069) - this node is a cross-community bridge._
- **Are the 11 inferred relationships involving `User` (e.g. with `download_lawyer_document()` and `lawyers()`) actually correct?**
  _`User` has 11 INFERRED edges - model-reasoned connections that need verification._
- **Are the 25 inferred relationships involving `i()` (e.g. with `an()` and `.captureUserFeedback()`) actually correct?**
  _`i()` has 25 INFERRED edges - model-reasoned connections that need verification._
- **Are the 15 inferred relationships involving `o()` (e.g. with `.captureUserFeedback()` and `.eventFromMessage()`) actually correct?**
  _`o()` has 15 INFERRED edges - model-reasoned connections that need verification._
- **What connects `colors`, `metrics`, `pendingLawyers` to the rest of the system?**
  _44 weakly-connected nodes found - possible documentation gaps or missing edges._