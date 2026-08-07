# Graph Report - New project  (2026-07-08)

## Corpus Check
- 24 files · ~24,859 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 515 nodes · 1532 edges · 22 communities (18 shown, 4 thin omitted)
- Extraction: 87% EXTRACTED · 13% INFERRED · 0% AMBIGUOUS · INFERRED: 197 edges (avg confidence: 0.55)
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
- setup
- LawyerGrid
- er
- Settings
- graphify.md
- graphify.md
- __init__.py

## God Nodes (most connected - your core abstractions)
1. `User` - 43 edges
2. `je()` - 39 edges
3. `i()` - 34 edges
4. `o()` - 32 edges
5. `mr` - 32 edges
6. `r()` - 30 edges
7. `setup()` - 29 edges
8. `LexAPI` - 28 edges
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

## Communities (22 total, 4 thin omitted)

### Community 0 - "main.py"
Cohesion: 0.07
Nodes (85): get_settings(), Base, get_db(), admin_metrics(), booking_for_participant(), complete_booking(), confirm_document(), confirm_payment() (+77 more)

### Community 1 - "mr"
Cohesion: 0.08
Nodes (15): Ae(), ar(), br, fn(), hn(), ir(), kr(), mr (+7 more)

### Community 2 - "je"
Cohesion: 0.07
Nodes (10): B(), be(), bn(), je(), N(), sn(), te(), we() (+2 more)

### Community 3 - "lawyer.js"
Cohesion: 0.14
Nodes (37): LexAPI, $(), LexE2EE, bookings, chatKeys, checkLawyerSession(), closeCall(), colors (+29 more)

### Community 4 - "app.js"
Cohesion: 0.10
Nodes (38): backdrop, booking, bookingView(), close(), content, darken(), getColorForName(), getSpecialty() (+30 more)

### Community 5 - "daily-js.js"
Cohesion: 0.08
Nodes (21): as(), ce(), de(), dt(), ft(), g(), ht(), ia() (+13 more)

### Community 6 - "admin.js"
Cohesion: 0.14
Nodes (29): auditLogs, checkAdminSession(), colors, decideVerification(), disputes, escapeHtml(), handleSaveFees(), lawyerMap (+21 more)

### Community 7 - "i"
Cohesion: 0.16
Nodes (24): at(), Bs(), ct(), dn(), Es(), Et(), fe(), i() (+16 more)

### Community 8 - "o"
Cohesion: 0.17
Nodes (23): a(), c(), d(), f(), gn(), gt(), l(), o() (+15 more)

### Community 9 - "_e"
Cohesion: 0.15
Nodes (13): an(), cn(), dr(), _e(), he(), nn(), on(), pe() (+5 more)

### Community 10 - "Fo"
Cohesion: 0.23
Nodes (16): Bo(), Ds(), ea(), Fo(), Fs(), Go(), Ho(), Ko() (+8 more)

### Community 11 - "ge"
Cohesion: 0.21
Nodes (11): ge(), ie(), le(), me(), ne(), oe(), qn(), ue() (+3 more)

### Community 12 - "T"
Cohesion: 0.27
Nodes (10): h(), is(), na(), ra(), rs(), sa(), T(), Ua() (+2 more)

### Community 13 - "setup"
Cohesion: 0.29
Nodes (7): Bt(), ee(), Kn(), Mn(), q(), setup(), Vt()

### Community 14 - "LawyerGrid"
Cohesion: 0.29
Nodes (6): Full-stack development, LawyerGrid, Local static preview, Production architecture, Production note, Required before launch

### Community 15 - "er"
Cohesion: 0.33
Nodes (6): cr(), er(), hr(), lr(), xn(), Zn()

## Knowledge Gaps
- **34 isolated node(s):** `colors`, `metrics`, `pendingLawyers`, `users`, `transactions` (+29 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `s()` connect `o` to `mr`, `je`, `lawyer.js`, `daily-js.js`, `admin.js`, `i`, `T`, `setup`, `er`?**
  _High betweenness centrality (0.113) - this node is a cross-community bridge._
- **Why does `je()` connect `je` to `_e`, `daily-js.js`?**
  _High betweenness centrality (0.076) - this node is a cross-community bridge._
- **Why does `p()` connect `o` to `mr`, `app.js`, `daily-js.js`, `i`?**
  _High betweenness centrality (0.064) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `User` (e.g. with `lawyers()` and `login()`) actually correct?**
  _`User` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 25 inferred relationships involving `i()` (e.g. with `an()` and `.captureUserFeedback()`) actually correct?**
  _`i()` has 25 INFERRED edges - model-reasoned connections that need verification._
- **Are the 15 inferred relationships involving `o()` (e.g. with `.captureUserFeedback()` and `.eventFromMessage()`) actually correct?**
  _`o()` has 15 INFERRED edges - model-reasoned connections that need verification._
- **What connects `colors`, `metrics`, `pendingLawyers` to the rest of the system?**
  _36 weakly-connected nodes found - possible documentation gaps or missing edges._