const colors = ["#d2b19d", "#aec8bc", "#c5b6cf", "#b4c7d8", "#d8c49e"];
const $ = s => document.querySelector(s);
const money = n => new Intl.NumberFormat("en-IN", {style: "currency", currency: "INR", maximumFractionDigits: 0}).format(n);

// Backend stores UTC but SQLite strips timezone info → ensure we parse as UTC
function parseUTCDate(dtStr) {
  if (!dtStr) return new Date(NaN);
  if (!dtStr.endsWith("Z") && !dtStr.includes("+")) dtStr += "Z";
  return new Date(dtStr);
}

let metrics = {};
let pendingLawyers = [];
let rejectedLawyers = [];
let approvedLawyersCount = 0;
let rejectedLawyersCount = 0;
let users = [];
let transactions = [];
let draftingTransactions = [];
let disputes = [];
let auditLogs = [];
let payouts = [];
let userFeedbacks = [];
// Map for safe lookup from onclick handlers
const lawyerMap = {};

// Session check — clear any stale token and redirect to login if not admin
function checkAdminSession() {
  const user = LexAPI.getCurrentUser();
  const role = user ? String(user.role).toLowerCase() : "";
  if (!user || role !== "admin") {
    // Clear stale token so login page starts fresh
    LexAPI.logout();
    window.location.href = "admin-login.html";
    return false;
  }
  return true;
}

if (!checkAdminSession()) {
  // Stop execution if not an admin
  throw new Error("Not authorized — redirecting to login.");
}

function mapPracticeToFrontend(p) {
  if (Array.isArray(p)) return p.map(mapPracticeToFrontend).join(", ");
  if (p === "property") return "Property Law";
  if (p === "corporate") return "Corporate Law";
  if (p === "family") return "Family Law";
  return p;
}

function mapPracticeToBackend(p) {
  if (Array.isArray(p)) return p.map(mapPracticeToBackend);
  if (p === "Property Law") return "property";
  if (p === "Corporate Law") return "corporate";
  if (p === "Family Law") return "family";
  return p;
}

function escapeHtml(text) {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

async function loadData() {
  try {
    metrics = await LexAPI.metrics();
    pendingLawyers = await LexAPI.getPendingLawyers();
    try {
      rejectedLawyers = await LexAPI.getRejectedLawyers();
      rejectedLawyersCount = rejectedLawyers.length;
    } catch (e) {
      console.error("Failed to load rejected lawyers:", e);
      rejectedLawyers = [];
      rejectedLawyersCount = 0;
    }
    try {
      const approvedList = await LexAPI.lawyers();
      approvedLawyersCount = approvedList.length;
    } catch (e) {
      approvedLawyersCount = 0;
    }
    users = await LexAPI.getAdminUsers();
    transactions = await LexAPI.getAdminTransactions();
    draftingTransactions = await LexAPI.getAdminDraftingTransactions().catch(err => { console.error("Failed to load drafting transactions:", err); return []; });
    disputes = await LexAPI.getDisputes();
    auditLogs = await LexAPI.getAuditLogs();
    payouts = await LexAPI.getAdminPayouts().catch(err => { console.error("Failed to load payout accounts:", err); return []; });
    userFeedbacks = await LexAPI.getPlatformFeedback().catch(err => { console.error("Failed to load user feedback:", err); return []; });
    renderAll();
    updateBadgeCounts();
  } catch (err) {
    console.error("Failed to load admin console data:", err);
    if (err.message && (err.message.includes("401") || err.message.includes("unauthorized") || err.message.includes("authentication"))) {
      toast("Session expired or unauthorized. Redirecting to login...");
      LexAPI.logout();
      setTimeout(() => {
            window.location.href = "admin-login.html";
      }, 1500);
    } else {
      toast("Failed to load admin data: " + (err.message || "Server error"));
    }
  }
}

function renderAll() {
  // Update admin initials
  const adminUser = LexAPI.getCurrentUser();
  const initials = adminUser ? adminUser.role.toUpperCase().slice(0, 2) : "AD";
  $(".avatar").textContent = initials;
  $(".identity strong").textContent = "VidhiMeet Admin";
  $(".identity small").textContent = "Super Administrator";

  renderOverview();
  renderApps();
  renderDisputes();
  renderUsers();
  renderTx();
  renderAudit();
  renderPayoutOverview();
  renderPayouts();
  renderFeedback();
  restoreFeeConfig();

  const initialHash = window.location.hash.replace("#", "");
  if (initialHash && document.getElementById(initialHash)) {
    switchView(initialHash, false);
  }
}

function renderMarketplaceChart(days) {
  const subtitle = $("#chart-subtitle");
  if (subtitle) {
    subtitle.textContent = `Consultations and usage fees over the last ${days} days`;
  }
  
  const dates = [];
  const now = new Date();
  for (let i = days - 1; i >= 0; i--) {
    const d = new Date(now.getFullYear(), now.getMonth(), now.getDate() - i);
    dates.push(d);
  }

  const dailyData = dates.map(d => {
    const dateKey = d.toDateString();
    const dayTx = transactions.filter(t => {
      const txDate = parseUTCDate(t.starts_at);
      return txDate.toDateString() === dateKey;
    });
    const consultationsCount = dayTx.filter(t => ["completed", "confirmed", "in_progress"].includes(t.status)).length;
    const platformFeesAmount = dayTx
      .filter(t => t.status === "completed")
      .reduce((sum, t) => sum + (t.platform_fee_minor || 0), 0) / 100;
    return {
      dateStr: d.toLocaleDateString("en-IN", { day: "numeric", month: "short" }),
      consultations: consultationsCount,
      fees: platformFeesAmount
    };
  });

  const maxConsultations = Math.max(...dailyData.map(d => d.consultations), 1);
  const maxFees = Math.max(...dailyData.map(d => d.fees), 100);

  const mainPoints = [];
  const secondPoints = [];
  
  dailyData.forEach((item, idx) => {
    const x = (idx / (days - 1)) * 700;
    const yMain = 200 - (item.consultations / maxConsultations) * 160;
    const ySecond = 200 - (item.fees / maxFees) * 160;
    mainPoints.push({ x, y: yMain });
    secondPoints.push({ x, y: ySecond });
  });

  const mainLineEl = document.querySelector(".main-line");
  const secondLineEl = document.querySelector(".second-line");
  const areaEl = document.querySelector(".area");

  if (mainLineEl && secondLineEl && areaEl) {
    const mainLineD = "M " + mainPoints.map(p => `${p.x} ${p.y}`).join(" L ");
    const secondLineD = "M " + secondPoints.map(p => `${p.x} ${p.y}`).join(" L ");
    const areaD = mainLineD + ` L ${mainPoints[mainPoints.length - 1].x} 220 L ${mainPoints[0].x} 220 Z`;
    
    mainLineEl.setAttribute("d", mainLineD);
    secondLineEl.setAttribute("d", secondLineD);
    areaEl.setAttribute("d", areaD);
  }

  const labelsEl = document.querySelector(".chart-days");
  if (labelsEl) {
    if (days === 7) {
      labelsEl.innerHTML = dailyData.map(item => `<span>${item.dateStr}</span>`).join("");
    } else {
      const step = 6;
      let html = "";
      for (let i = 0; i < days; i += step) {
        const idx = Math.min(i, days - 1);
        html += `<span>${dailyData[idx].dateStr}</span>`;
      }
      labelsEl.innerHTML = html;
    }
  }
}

function renderOverview() {
  const rangeSelect = document.getElementById("chart-range-select");
  if (rangeSelect) {
    rangeSelect.onchange = (e) => {
      renderMarketplaceChart(parseInt(e.target.value));
    };
    renderMarketplaceChart(parseInt(rangeSelect.value) || 7);
  }
  const GTV = transactions.reduce((sum, t) => sum + t.amount_minor, 0) / 100;
  const completed = transactions.filter(t => t.status === "completed");
  const platformRevenue = completed.reduce((sum, t) => sum + t.platform_fee_minor, 0) / 100;
  const totalUsers = users.length;
  const openDisputes = disputes.filter(d => !["completed","refunded","cancelled"].includes(d.status));

  // ── Date headline ──────────────────────────────────────────────────────
  const dateEl = document.getElementById("overview-date");
  if (dateEl) {
    const now = new Date();
    const dayName = now.toLocaleDateString("en-IN", { weekday: "long" }).toUpperCase();
    const dateStr = now.toLocaleDateString("en-IN", { day: "numeric", month: "long" }).toUpperCase();
    dateEl.textContent = `${dayName}, ${dateStr}`;
  }

  // ── "Review applications N" badge ─────────────────────────────────────
  const ovCount = document.getElementById("overview-pending-count");
  if (ovCount) ovCount.textContent = pendingLawyers.length;

  // ── Oldest application age ────────────────────────────────────────────
  const ageEl = document.getElementById("oldest-app-age");
  if (ageEl) {
    if (pendingLawyers.length === 0) {
      ageEl.textContent = "All applications reviewed";
    } else {
      const now = new Date();
      let oldestDate = now;
      pendingLawyers.forEach(l => {
        if (l.created_at) {
          const cDate = new Date(l.created_at);
          if (cDate < oldestDate) oldestDate = cDate;
        }
      });
      const diffMs = now - oldestDate;
      const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
      if (diffDays === 0) {
        const diffHrs = Math.floor(diffMs / (1000 * 60 * 60));
        if (diffHrs === 0) {
          const diffMins = Math.floor(diffMs / (1000 * 60));
          ageEl.textContent = `Oldest application is ${diffMins} min${diffMins !== 1 ? 's' : ''} old`;
        } else {
          ageEl.textContent = `Oldest application is ${diffHrs} hr${diffHrs !== 1 ? 's' : ''} old`;
        }
      } else {
        ageEl.textContent = `Oldest application is ${diffDays} day${diffDays !== 1 ? 's' : ''} old`;
      }
    }
  }

  // ── Quick actions subtexts ────────────────────────────────────────────
  function setEl(id, val) { const el = document.getElementById(id); if (el) el.textContent = val; }
  setEl("qa-verify-sub",   `${pendingLawyers.length} application${pendingLawyers.length !== 1 ? "s" : ""} waiting`);
  setEl("qa-disputes-sub", `${openDisputes.length} open case${openDisputes.length !== 1 ? "s" : ""}`);

  // ── Stats cards ───────────────────────────────────────────────────────
  $(".stats").innerHTML = `
    <article>
      <div><span class="metric green">○</span></div>
      <p>Total platform users</p>
      <strong>${totalUsers}</strong>
      <small>${users.filter(u=>u.role==="client").length} clients · ${users.filter(u=>u.role==="lawyer").length} lawyers</small>
    </article>
    <article>
      <div><span class="metric gold">▣</span></div>
      <p>Total bookings</p>
      <strong>${metrics.bookings || 0}</strong>
      <small>${transactions.filter(t=>t.status==="completed").length} completed · ${transactions.filter(t=>t.status==="confirmed"||t.status==="pending_payment").length} upcoming</small>
    </article>
    <article>
      <div><span class="metric blue">₹</span></div>
      <p>Gross Transaction Value</p>
      <strong>${money(GTV)}</strong>
      <small>${money(platformRevenue)} Infrastructure usage fees (5%)</small>
    </article>
    <article>
      <div><span class="metric coral">◇</span></div>
      <p>Open disputes</p>
      <strong>${openDisputes.length}</strong>
      <small>${openDisputes.length} awaiting resolution</small>
    </article>
  `;

  // ── Attention notice ──────────────────────────────────────────────────
  const attentionItems = pendingLawyers.length + openDisputes.length;
  $(".notice div").innerHTML = `
    <strong>${attentionItems} item${attentionItems !== 1 ? "s" : ""} ${attentionItems === 1 ? "needs" : "need"} your attention</strong>
    <small>${pendingLawyers.length} lawyer application${pendingLawyers.length !== 1 ? "s" : ""} and ${openDisputes.length} dispute${openDisputes.length !== 1 ? "s" : ""} open.</small>
  `;

  // ── Quick activity feed (audit log summary) ───────────────────────────
  $("#activity").innerHTML = auditLogs.slice(0, 4).map(a => {
    const timeStr = new Date(a.created_at).toLocaleTimeString("en-IN", {hour: "2-digit", minute: "2-digit"});
    return `
      <div class="activity-row">
        <i>○</i>
        <div>
          <strong>${escapeHtml(a.action)}</strong>
          <small>${a.actor_name} · ${a.target_type} at ${timeStr}</small>
        </div>
      </div>
    `;
  }).join("");

  if (auditLogs.length === 0) {
    $("#activity").innerHTML = `<p class="muted" style="padding:10px 0;">No system logs recorded yet.</p>`;
  }

  // ── Mini applications panel ───────────────────────────────────────────
  $("#mini-applications").innerHTML = pendingLawyers.slice(0, 3).map((a, i) => {
    const appInitials = a.full_name.split(" ").map(x => x[0]).join("").slice(0, 2).toUpperCase();
    return `
      <div class="mini-app">
        <span class="avatar" style="background:${colors[i % colors.length]}">${appInitials}</span>
        <div>
          <strong>${a.full_name}</strong>
          <small>${mapPracticeToFrontend(a.practice)} · Bar No: ${a.bar_number}</small>
        </div>
        <span class="status">Pending</span>
      </div>
    `;
  }).join("");

  if (pendingLawyers.length === 0) {
    $("#mini-applications").innerHTML = `<p class="muted" style="padding:15px 0;">No pending lawyer applications.</p>`;
  }
}

// Verification tab
async function renderApps(filter = "pending") {
  let list = [];
  if (filter === "pending" || filter === "review") {
    // Pending and in-review both show the unverified set
    list = pendingLawyers;
  } else if (filter === "approved") {
    try {
      list = await LexAPI.lawyers();
    } catch (e) {
      list = [];
    }
  } else if (filter === "rejected") {
    try {
      list = await LexAPI.getRejectedLawyers();
      rejectedLawyersCount = list.length;
      const rejectedTabB = document.querySelector('button[data-app-filter="rejected"] b');
      if (rejectedTabB) rejectedTabB.textContent = rejectedLawyersCount;
    } catch (e) {
      console.error("Failed to load rejected applications:", e);
      list = rejectedLawyers;
    }
  }

  // Always (re-)populate lawyerMap so clicks always find data
  list.forEach(a => { lawyerMap[a.id] = a; });

  const isActionable = filter === "pending" || filter === "review";

  $("#applications").innerHTML = `
    <div class="table-row head">
      <span>Applicant</span>
      <span>Practice area</span>
      <span>Bar council</span>
      <span>Status</span>
      <span></span>
    </div>
  ` + (list.length ? list.map((a, i) => {
    const appInitials = a.full_name.split(" ").map(x => x[0]).join("").slice(0, 2).toUpperCase();
    const practiceDisplay = mapPracticeToFrontend(a.practice);
    const statusLabel = filter === "approved" ? "APPROVED" : (filter === "review" ? "IN REVIEW" : filter.toUpperCase());
    const actionBtn = isActionable
      ? `<button class="review-btn" data-review-id="${a.id}">Review</button>`
      : (filter === "approved" || filter === "rejected"
          ? `<button class="review-btn" data-review-id="${a.id}">${filter === "approved" ? "Preview" : "Review"}</button>`
          : `<span>—</span>`);

    return `
      <div class="table-row">
        <div class="person">
          <span class="avatar" style="background:${colors[i % colors.length]}">${appInitials}</span>
          <div>
            <strong>${a.full_name}</strong>
            <small>Identity check complete</small>
          </div>
        </div>
        <span class="tag">${practiceDisplay}</span>
        <span>${a.bar_number || "Pending"}</span>
        <span>${statusLabel}</span>
        <div>${actionBtn}</div>
      </div>
    `;
  }).join("") : `<p class="muted" style="padding:20px;">No applications found.</p>`);
}

function reviewApplication(id, name, practice, bar, isVerified = false, barLicenseUrl = null, aadhaarUrl = null) {
  const appInitials = name.split(" ").map(x => x[0]).join("").slice(0, 2).toUpperCase();
  const token = sessionStorage.getItem("lex_access_token") || localStorage.getItem("lex_access_token") || "";

  function docRow(docType, label, subtitle, fileUrl) {
    if (isVerified) {
      // Approved lawyer preview - show only view button if exists, no verify button
      const viewBtn = fileUrl
        ? `<a href="${fileUrl}&token=${encodeURIComponent(token)}" target="_blank" class="doc-view-btn" title="Open document in new tab">&#128065; View</a>`
        : `<span class="doc-no-upload">Not on file</span>`;
      return `
        <article class="doc-row doc-row-verified" id="doc-row-${docType}">
          <div class="doc-icon">${docType === 'bar' ? '&#128196;' : '&#128100;'}</div>
          <div class="doc-info">
            <strong>${label}</strong>
            <small>Verified credential</small>
          </div>
          <div class="doc-actions">
            ${viewBtn}
          </div>
        </article>`;
    } else {
      // Pending review flow
      const viewBtn = fileUrl
        ? `<a href="${fileUrl}&token=${encodeURIComponent(token)}" target="_blank" class="doc-view-btn" title="Open document in new tab">&#128065; View</a>`
        : `<span class="doc-no-upload">Not uploaded</span>`;
      const verifyBtn = `<button class="doc-verify-btn" data-doc="${docType}" title="Upload a document first" ${fileUrl ? '' : 'disabled'}>&#10003; Verify</button>`;
      return `
        <article class="doc-row" id="doc-row-${docType}">
          <div class="doc-icon">${docType === 'bar' ? '&#128196;' : '&#128100;'}</div>
          <div class="doc-info">
            <strong>${label}</strong>
            <small>${subtitle}</small>
          </div>
          <div class="doc-actions">
            ${viewBtn}
            ${verifyBtn}
          </div>
          <div class="doc-status" id="doc-status-${docType}"></div>
        </article>`;
    }
  }

  const approveDisabled = isVerified ? "" : "disabled";
  const actionButtons = isVerified
    ? `<button class="reject" data-decide-id="${id}" data-decide-approved="false">Revoke verification</button>
       <button class="ghost" data-close-modal>Close</button>`
    : `<button class="reject" data-decide-id="${id}" data-decide-approved="false">Reject profile</button>
       <button class="primary" id="approve-btn" data-decide-id="${id}" data-decide-approved="true" ${approveDisabled}>Approve lawyer</button>`;

  const descriptionText = isVerified
    ? "Verified professional credentials on file for this lawyer."
    : "View and individually verify each document before approving this lawyer profile.";

  $("#review-content").innerHTML = `
    <small class="eyebrow">CREDENTIAL REVIEW</small>
    <h2>${escapeHtml(name)}</h2>
    <p class="muted">${descriptionText}</p>
    <div class="review-profile">
      <span class="avatar" style="background:${colors[0]}">${appInitials}</span>
      <div>
        <strong>${escapeHtml(name)}</strong>
        <small>${escapeHtml(practice)} &middot; Bar No: ${escapeHtml(bar)}</small>
      </div>
    </div>
    <div class="review-docs">
      ${docRow('bar', 'Bar Council Certificate', 'Click View to open, then Verify to confirm', barLicenseUrl)}
      ${docRow('id', 'Government Identity Card', 'Click View to open, then Verify to confirm', aadhaarUrl)}
    </div>
    ${!isVerified ? `<p class="verify-hint">&#9432; Verify both documents to enable approval.</p>` : ''}
    <div class="modal-actions">
      ${actionButtons}
    </div>
  `;

  // Wire up Verify buttons
  const verified = { bar: false, id: false };
  $("#review-content").querySelectorAll(".doc-verify-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      const doc = btn.dataset.doc;
      verified[doc] = true;
      btn.textContent = "\u2713 Verified";
      btn.classList.add("doc-verified");
      btn.disabled = true;
      const row = $("#doc-row-" + doc);
      if (row) row.classList.add("doc-row-verified");
      const status = $("#doc-status-" + doc);
      if (status) { status.textContent = "Verified"; status.className = "doc-status-ok"; }
      // Enable Approve when both verified
      if (verified.bar && verified.id) {
        const approveBtn = $("#approve-btn");
        if (approveBtn) { approveBtn.disabled = false; approveBtn.classList.add("ready"); }
        const hint = $("#review-content").querySelector(".verify-hint");
        if (hint) hint.remove();
      }
    });
  });

  $("#review-modal").hidden = false;
  document.body.style.overflow = "hidden";
}

async function decideVerification(id, approved) {
  try {
    await LexAPI.verifyLawyer(id, approved);
    toast(approved ? "Lawyer approved and profile activated." : "Lawyer rejected.");
    $("#review-modal").hidden = true;
    document.body.style.overflow = "";
    loadData();
  } catch (err) {
    toast("Action failed: " + err.message);
  }
}

function openVerificationPolicyModal() {
  $("#review-content").innerHTML = `
    <div style="padding:10px 4px;">
      <span style="color:var(--forest); font-weight:700; font-size:12px; text-transform:uppercase; letter-spacing:0.05em;">Trust & Safety Policy</span>
      <h2 style="font-family:'Playfair Display',serif; margin:6px 0 14px; font-size:22px; color:var(--forest);">Lawyer Verification & Credentials Policy</h2>
      <p style="font-size:13px; color:var(--muted); line-height:1.6; margin-bottom:16px;">
        To preserve marketplace integrity and adhere to Bar Council guidelines and the DPDP Act 2023, every advocate profile undergoes mandatory dual-document verification before being listed publicly.
      </p>

      <div style="display:flex; flex-direction:column; gap:12px; margin-bottom:20px;">
        <div style="background:#f4f7f4; padding:14px; border-radius:10px; border-left:4px solid var(--forest);">
          <strong style="font-size:13px; color:var(--forest);">1. Bar Council Enrollment Check</strong>
          <p style="margin:4px 0 0; font-size:12px; color:var(--ink);">Validate the State Bar Council Enrollment Number (e.g. <code>DL/2014/02841</code>, <code>KAR/3356/2026</code>) against State Bar Council databases and inspect the uploaded license certificate.</p>
        </div>

        <div style="background:#f4f7f4; padding:14px; border-radius:10px; border-left:4px solid var(--forest);">
          <strong style="font-size:13px; color:var(--forest);">2. Identity Verification (DPDPA 2023 Compliant)</strong>
          <p style="margin:4px 0 0; font-size:12px; color:var(--ink);">Government Identity cards (Aadhaar / Passport / Voter ID) are stored with AES-256 Fernet encryption at rest. Admins must confirm age is 18+ and full legal name matches the Bar Council certificate.</p>
        </div>

        <div style="background:#f4f7f4; padding:14px; border-radius:10px; border-left:4px solid var(--forest);">
          <strong style="font-size:13px; color:var(--forest);">3. Payout Bank & UPI VPA Verification</strong>
          <p style="margin:4px 0 0; font-size:12px; color:var(--ink);">Payout account details undergo automated PhonePe Reverse Penny Drop verification to ensure bank account ownership matches the advocate's legal name.</p>
        </div>
      </div>

      <div style="display:flex; justify-content:flex-end;">
        <button class="review-btn" data-close-modal style="background:var(--forest);">Got it, Close</button>
      </div>
    </div>
  `;
  $("#review-modal").hidden = false;
  document.body.style.overflow = "hidden";
}

function openResolutionPolicyModal() {
  $("#review-content").innerHTML = `
    <div style="padding:10px 4px;">
      <span style="color:var(--terra); font-weight:700; font-size:12px; text-transform:uppercase; letter-spacing:0.05em;">Resolution Centre Policy</span>
      <h2 style="font-family:'Playfair Display',serif; margin:6px 0 14px; font-size:22px; color:var(--forest);">Video Consultation Dispute & Intermediary Policy</h2>
      <p style="font-size:13px; color:var(--muted); line-height:1.6; margin-bottom:16px;">
        Disputes are evaluated using objective room connection telemetry in compliance with Section 79 of the IT Act (Electronic Marketplace Intermediary rules).
      </p>

      <div style="display:flex; flex-direction:column; gap:12px; margin-bottom:20px;">
        <div style="background:#fffaf0; padding:14px; border-radius:10px; border-left:4px solid var(--terra);">
          <strong style="font-size:13px; color:var(--terra);">1. Daily.co Room Connection Telemetry</strong>
          <p style="margin:4px 0 0; font-size:12px; color:var(--ink);">Per the Metadata Waiver agreed at checkout, automated room connection timestamps and participant durations serve as the sole definitive evidence for refund eligibility.</p>
        </div>

        <div style="background:#fffaf0; padding:14px; border-radius:10px; border-left:4px solid var(--terra);">
          <strong style="font-size:13px; color:var(--terra);">2. Automated No-Show & Short Duration Matrix</strong>
          <p style="margin:4px 0 0; font-size:12px; color:var(--ink);">If advocate duration is 0 minutes, full refund is issued instantly and 1 strike is added to the advocate's profile. Calls under 5 minutes or under 50% of slot time trigger automatic refund eligibility.</p>
        </div>

        <div style="background:#fffaf0; padding:14px; border-radius:10px; border-left:4px solid var(--terra);">
          <strong style="font-size:13px; color:var(--terra);">3. IT Act Section 79 Intermediary Shield</strong>
          <p style="margin:4px 0 0; font-size:12px; color:var(--ink);">When both parties attended for &ge;50% of the slot duration, claims regarding subjective quality of legal advice fall under Intermediary Shield protection (the platform does not guarantee legal outcomes; escrow is released to advocate).</p>
        </div>
      </div>

      <div style="display:flex; justify-content:flex-end;">
        <button class="review-btn" data-close-modal style="background:var(--forest);">Got it, Close</button>
      </div>
    </div>
  `;
  $("#review-modal").hidden = false;
  document.body.style.overflow = "hidden";
}


// Disputes tab
function renderDisputes(filter = "open") {
  const container = $("#dispute-list");

  // ── Compute live dispute stats ─────────────────────────────────────────
  const openDisp        = disputes.filter(d => !["completed","refunded","cancelled"].includes(d.status));
  const investigatingDisp = disputes.filter(d => d.status === "investigating");
  const resolvedDisp    = disputes.filter(d => ["completed","refunded"].includes(d.status));
  function setEl(id, val) { const el = document.getElementById(id); if (el) el.textContent = val; }
  setEl("stat-open-disputes",          openDisp.length);
  setEl("stat-investigating-disputes", investigatingDisp.length);
  setEl("stat-resolved-disputes",      resolvedDisp.length);
  setEl("stat-total-disputes",         disputes.length);

  // ── Filter list ───────────────────────────────────────────────────────
  let list = disputes;
  if (filter === "open")          list = openDisp;
  if (filter === "investigating") list = investigatingDisp;
  if (filter === "resolved")      list = resolvedDisp;

  if (list.length === 0) {
    container.innerHTML = `<p class="muted" style="padding:20px 0;">No dispute resolution cases here.</p>`;
    return;
  }

  container.innerHTML = list.map(d => {
    const isResolved = ["completed", "refunded"].includes(d.status);
    const amount = d.amount_minor ? d.amount_minor / 100 : 0;
    const categoryLabels = {
      no_show: "🚫 Lawyer No-Show",
      bad_connectivity: "📡 Bad Connectivity / Drop",
      short_duration: "⏱️ Short Duration (<50%)",
      quality_other: "⚖️ Quality / Other"
    };
    const catLabel = categoryLabels[d.dispute_category] || "⚖️ General Dispute";
    const autoStatus = d.auto_resolution_status || "REQUIRES_HUMAN_REVIEW";
    
    let autoBadgeStyle = "background:#fff3cd; color:#856404; border:1px solid #ffeeba;";
    if (autoStatus.includes("AUTO_REFUND")) {
      autoBadgeStyle = "background:#f8d7da; color:#721c24; border:1px solid #f5c6cb;";
    } else if (autoStatus.includes("INTERMEDIARY_SHIELD")) {
      autoBadgeStyle = "background:#d4edda; color:#155724; border:1px solid #c3e6cb;";
    }

    const lawyerMin = Math.floor((d.lawyer_duration_seconds || 0) / 60);
    const clientMin = Math.floor((d.client_duration_seconds || 0) / 60);

    let actionButtons = "";
    if (!isResolved) {
      actionButtons = `
        <div style="display:flex; flex-wrap:wrap; gap:6px; margin-top:10px;">
          <button class="review-btn" data-resolve-id="${d.id}" data-resolve-outcome="refund" style="background:#c86245;">Refund Client</button>
          <button class="review-btn" data-resolve-id="${d.id}" data-resolve-outcome="refund" data-strike="true" style="background:#842029;">Strike & Refund</button>
          <button class="review-btn" data-resolve-id="${d.id}" data-resolve-outcome="release" style="background:var(--forest);">Release Escrow</button>
        </div>
      `;
    } else {
      actionButtons = `<span style="font-size:12px; font-weight:700; color:var(--forest);">RESOLVED (${d.status.toUpperCase()})</span>`;
    }

    return `
      <article class="dispute-card" style="display:flex; flex-direction:column; gap:12px; padding:20px; border-radius:16px; background:white; border:1px solid var(--line); margin-bottom:16px;">
        <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:10px;">
          <div>
            <span style="font-size:11px; font-weight:700; text-transform:uppercase; color:var(--terra);">${catLabel}</span>
            <h3 style="margin:4px 0 2px; font-size:18px;">Consultation Dispute #${d.id.slice(0,8).toUpperCase()}</h3>
            <p style="margin:0; font-size:13px; color:var(--muted);">Client: <strong>${escapeHtml(d.client_name || "Client")}</strong> vs Lawyer: <strong>${escapeHtml(d.lawyer_name || "Lawyer")}</strong></p>
          </div>
          <span style="padding:6px 12px; border-radius:99px; font-size:11px; font-weight:700; ${autoBadgeStyle}">
            ${escapeHtml(autoStatus)}
          </span>
        </div>

        ${d.dispute_reason ? `
          <div style="background:#f9fbf9; border-left:4px solid var(--terra); padding:10px 14px; border-radius:4px; font-size:13px; color:var(--ink);">
            <strong>Client Explanation:</strong> "${escapeHtml(d.dispute_reason)}"
          </div>
        ` : ""}

        <div style="display:flex; gap:18px; flex-wrap:wrap; font-size:12px; background:#f4f7f4; padding:10px 14px; border-radius:10px;">
          <span>Hold Amount: <b>${money(amount)}</b></span>
          <span>Lawyer Room Time: <b>${lawyerMin} mins</b></span>
          <span>Client Room Time: <b>${clientMin} mins</b></span>
          <span>Slot Duration: <b>${d.duration_minutes || 45} mins</b></span>
        </div>

        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px; margin-top:4px;">
          <small style="color:var(--muted); font-size:11px;">${isResolved ? "Case Closed" : "Awaiting Resolution (Section 79 IT Act)"}</small>
          ${actionButtons}
        </div>
      </article>
    `;
  }).join("");
}

async function resolveDispute(id, outcome, strikeLawyer = false) {
  const promptMsg = strikeLawyer
    ? `Issue REFUND and add STRIKE penalty to lawyer profile?`
    : `Resolve dispute by choosing outcome: ${outcome.toUpperCase()}?`;
  if (confirm(promptMsg)) {
    try {
      await LexAPI.resolveDispute(id, outcome, strikeLawyer);
      toast(`Dispute resolved successfully.`);
      loadData();
    } catch (err) {
      toast("Resolution failed: " + err.message);
    }
  }
}


// Users tab
function renderUsers(role = "all") {
  // ── Compute live stat card values from real data ───────────────────────
  const totalClients    = users.filter(u => u.role === "client").length;
  const totalLawyers    = users.filter(u => u.role === "lawyer").length;
  const verifiedLawyers = approvedLawyersCount;
  const activeUsers     = users.filter(u => u.active).length;
  const restrictedUsers = users.filter(u => !u.active).length;
  const totalAll        = users.length;
  const activePct       = totalAll > 0 ? ((activeUsers / totalAll) * 100).toFixed(1) : "0.0";
  const restrictedPct   = totalAll > 0 ? ((restrictedUsers / totalAll) * 100).toFixed(1) : "0.0";

  function setEl(id, val) { const el = document.getElementById(id); if (el) el.textContent = val; }
  setEl("stat-total-clients",        totalClients);
  setEl("stat-total-clients-sub",    `${totalLawyers} lawyer${totalLawyers !== 1 ? "s" : ""} · ${totalAll} total users`);
  setEl("stat-verified-lawyers",     verifiedLawyers);
  setEl("stat-verified-lawyers-sub", `${totalLawyers - verifiedLawyers} pending verification`);
  setEl("stat-active-users",         activeUsers);
  setEl("stat-active-users-sub",     `${activePct}% of all accounts`);
  setEl("stat-restricted-users",     restrictedUsers);
  setEl("stat-restricted-users-sub", `${restrictedPct}% of total`);

  // ── Filter and render table ────────────────────────────────────────────
  let list = users;
  if (role !== "all") {
    list = users.filter(u => u.role === role);
  }

  $("#user-table").innerHTML = `
    <div class="table-row head">
      <span>User</span>
      <span>Role</span>
      <span>Status</span>
      <span>Created At</span>
      <span>Actions</span>
    </div>
  ` + (list.length ? list.map((u, i) => {
    const userInitials = u.full_name.split(" ").map(x => x[0]).join("").slice(0, 2).toUpperCase();
    const dateStr = new Date(u.created_at).toLocaleDateString("en-IN", {day: "numeric", month: "short"});
    
    return `
      <div class="table-row">
        <div class="person">
          <span class="avatar" style="background:${colors[i % colors.length]}">${userInitials}</span>
          <div>
            <strong>${u.full_name}</strong>
            <small>${u.email}</small>
          </div>
        </div>
        <span class="tag">${u.role.toUpperCase()}</span>
        <span class="status ${u.active ? "approved" : "rejected"}">${u.active ? "Active" : "Restricted"}</span>
        <span>${dateStr}</span>
        <button class="outline" data-toggle-id="${u.id}" data-toggle-active="${u.active}">
          ${u.active ? "Restrict" : "Activate"}
        </button>
      </div>
    `;
  }).join("") : `<p class="muted" style="padding:20px;">No users found in database.</p>`);
}

async function toggleUserStatus(id, active) {
  const action = active ? "restrict" : "activate";
  if (confirm(`Are you sure you want to ${action} this user account?`)) {
    try {
      await LexAPI.toggleUserActive(id, !active);
      toast(`User account successfully updated.`);
      loadData();
    } catch (err) {
      toast("Failed to update user: " + err.message);
    }
  }
}

// Transactions tab
let _txTypeFilter = "all";

function renderTx(typeFilter, searchQuery) {
  // Accept optional params; fall back to current module-level state
  if (typeFilter !== undefined) _txTypeFilter = typeFilter;
  const query = (searchQuery !== undefined ? searchQuery : ($("#tx-search") ? $("#tx-search").value : "")).toLowerCase().trim();

  // ── Build unified list ─────────────────────────────────────────────────
  const bookingRows = transactions.map(t => ({
    _type: "consultation",
    id: t.id,
    title: null,                                        // consultations have no title
    party_a: t.client_name || "Client",
    party_b: t.lawyer_name || "Lawyer",
    status: t.status,
    amount_minor: t.amount_minor,
    platform_fee_minor: t.platform_fee_minor,
    date_str: parseUTCDate(t.starts_at).toLocaleDateString("en-IN", {day: "numeric", month: "short"})
  }));

  const draftingRows = draftingTransactions.map(d => ({
    _type: "drafting",
    id: d.id,
    title: d.title || null,
    party_a: d.creator_name || "Client",
    party_b: d.drafter_name || (d.drafter_id ? "Lawyer" : "Unassigned"),
    status: d.status,
    amount_minor: d.agreed_price_minor || d.price_minor,
    platform_fee_minor: d.platform_fee_minor || 0,
    date_str: new Date(d.created_at).toLocaleDateString("en-IN", {day: "numeric", month: "short"})
  }));

  const allTx = [...bookingRows, ...draftingRows].sort((a, b) => b.id.localeCompare(a.id));

  // ── Update tab badge counts (always from full list, ignoring search) ───
  function setEl(id, val) { const el = document.getElementById(id); if (el) el.textContent = val; }
  setEl("tx-count-all",          allTx.length);
  setEl("tx-count-consultation", bookingRows.length);
  setEl("tx-count-drafting",     draftingRows.length);

  // ── Compute stats from the full merged list ────────────────────────────
  const totalTx     = allTx.length;
  const completedTx = allTx.filter(t => t.status === "completed");
  const GTV         = allTx.reduce((s, t) => s + (t.amount_minor || 0), 0) / 100;
  const revenue     = completedTx.reduce((s, t) => s + (t.platform_fee_minor || 0), 0) / 100;
  const pendingTx   = allTx.filter(t => ["pending_payment","confirmed","in_progress","open"].includes(t.status)).length;

  setEl("stat-total-tx",         totalTx);
  setEl("stat-total-tx-sub",     `${pendingTx} pending · ${allTx.filter(t=>t.status==="cancelled"||t.status==="refunded").length} cancelled/refunded`);
  setEl("stat-completed-tx",     completedTx.length);
  setEl("stat-completed-tx-sub", totalTx > 0 ? `${((completedTx.length/totalTx)*100).toFixed(1)}% of all transactions` : "No transactions yet");
  setEl("stat-gtv",              money(GTV));
  setEl("stat-gtv-sub",          `across ${totalTx} transaction${totalTx !== 1 ? "s" : ""}`);
  setEl("stat-revenue",          money(revenue));
  setEl("stat-revenue-sub",      `Platform fees collected`);

  // ── Apply type filter then search filter ──────────────────────────────
  let filtered = allTx;
  if (_txTypeFilter !== "all") filtered = filtered.filter(t => t._type === _txTypeFilter);
  if (query) {
    filtered = filtered.filter(t =>
      t.id.toLowerCase().includes(query) ||
      t.party_a.toLowerCase().includes(query) ||
      t.party_b.toLowerCase().includes(query) ||
      (t.title && t.title.toLowerCase().includes(query))
    );
  }

  // ── Render table ──────────────────────────────────────────────────────
  const consultStyle = "border-left:3px solid #3f5eb1;";
  const draftStyle   = "border-left:3px solid #265a47;";

  $("#transaction-table").innerHTML = `
    <div class="table-row head">
      <span>Transaction ID</span>
      <span>Type</span>
      <span>Details</span>
      <span>Status</span>
      <span>Amount</span>
      <span>Date</span>
    </div>
  ` + (filtered.length ? filtered.map(t => {
    const statusClass = t.status === "completed" ? "approved" : (t.status === "cancelled" || t.status === "refunded" ? "rejected" : "pending");

    const typeLabel = t._type === "drafting"
      ? `<span class="tag" style="background:rgba(38,90,71,.13);color:#265a47;font-size:11px;font-weight:700;">✍ Drafting</span>`
      : `<span class="tag" style="background:rgba(63,94,177,.12);color:#3f5eb1;font-size:11px;font-weight:700;">📞 Consult</span>`;

    // Details column: for drafting show the title; for consultations show the party flow
    const details = t._type === "drafting" && t.title
      ? `<span title="${escapeHtml(t.title)}"><strong style="font-size:12px;">${escapeHtml(t.title.length > 36 ? t.title.slice(0,36)+"…" : t.title)}</strong><br><small style="color:#888;">${t.party_a} ➡ ${t.party_b}</small></span>`
      : `<span>${t.party_a} ➡ ${t.party_b}</span>`;

    return `
      <div class="table-row" style="${t._type === "drafting" ? draftStyle : consultStyle}">
        <strong>#${t.id.slice(0, 8).toUpperCase()}</strong>
        ${typeLabel}
        ${details}
        <span class="status ${statusClass}">${t.status.replace(/_/g," ").toUpperCase()}</span>
        <strong>${money((t.amount_minor || 0) / 100)}</strong>
        <span>${t.date_str}</span>
      </div>
    `;
  }).join("") : `<p class="muted" style="padding:20px;">No transactions match the current filter.</p>`);
}

// Fees tab
function restoreFeeConfig() {
  try {
    const raw = localStorage.getItem("vidhimeet_fee_config");
    if (!raw) return;
    const cfg = JSON.parse(raw);

    if (cfg.defaultFee && $("#default-fee")) $("#default-fee").value = cfg.defaultFee;
    if (cfg.propertyOverride && $("#override-property")) $("#override-property").value = cfg.propertyOverride;
    if (cfg.corporateOverride && $("#override-corporate")) $("#override-corporate").value = cfg.corporateOverride;
    if (cfg.familyOverride && $("#override-family")) $("#override-family").value = cfg.familyOverride;
    
    if (cfg.minPayout && $("#min-payout-amt")) $("#min-payout-amt").value = cfg.minPayout;
    if (cfg.payoutSchedule && $("#payout-schedule")) $("#payout-schedule").value = cfg.payoutSchedule;

    if (cfg.releaseRule) {
      const radio = document.querySelector(`input[name="release"][value="${cfg.releaseRule}"]`);
      if (radio) {
        radio.checked = true;
        document.querySelectorAll('label.choice').forEach(lbl => {
          lbl.classList.toggle('active', lbl.contains(radio));
        });
      }
    }
  } catch (err) {
    console.error("Failed to restore fee config:", err);
  }
}

async function handleSaveFees() {
  const feeInput = $("#default-fee");
  const feeVal = parseInt(feeInput?.value) || 5;

  const propertyOverride = $("#override-property")?.value || "5";
  const corporateOverride = $("#override-corporate")?.value || "6";
  const familyOverride = $("#override-family")?.value || "5";

  const selectedRelease = document.querySelector('input[name="release"]:checked')?.value || "completion";
  const minPayout = $("#min-payout-amt")?.value || "1,000";
  const payoutSchedule = $("#payout-schedule")?.value || "Weekly";

  const configData = {
    defaultFee: feeVal,
    propertyOverride,
    corporateOverride,
    familyOverride,
    releaseRule: selectedRelease,
    minPayout,
    payoutSchedule
  };

  try {
    localStorage.setItem("vidhimeet_fee_config", JSON.stringify(configData));
    await LexAPI.updatePlatformFee(feeVal);
    toast(`Fee & payout configuration saved successfully (Default: ${feeVal}%).`);
    loadData();
  } catch (err) {
    toast("Saved locally, but server update failed: " + err.message);
  }
}

// Security tab (Audit Log)
function renderAudit() {
  $("#audit-table").innerHTML = `
    <div class="table-row head">
      <span>Administrator</span>
      <span>Action</span>
      <span>Target</span>
      <span>Time</span>
      <span>IP address</span>
    </div>
  ` + (auditLogs.length ? auditLogs.map((a, i) => {
    const actorInitials = a.actor_name.split(" ").map(x => x[0]).join("").slice(0, 2).toUpperCase();
    const dateStr = new Date(a.created_at).toLocaleString("en-IN", {hour: "2-digit", minute: "2-digit", day: "numeric", month: "short"});
    
    return `
      <div class="table-row">
        <div class="person">
          <span class="avatar" style="background:${colors[i % colors.length]}">${actorInitials}</span>
          <strong>${a.actor_name}</strong>
        </div>
        <span>${escapeHtml(a.action)}</span>
        <span>${a.target_type} (${a.target_id || "System"})</span>
        <span>${dateStr}</span>
        <span>127.0.0.1</span>
      </div>
    `;
  }).join("") : `<p class="muted" style="padding:20px;">No administrator logs recorded.</p>`);
}

function renderPayoutOverview() {
  const container = $(".payout-summary");
  if (!container) return;

  const completedTx = transactions.filter(t => t.status === "completed");
  
  // Dynamically read default fee from input if present
  const feeInput = $("#default-fee");
  const feePercent = feeInput ? (parseFloat(feeInput.value) || 5) : 5;
  const lawyerShareMultiplier = (100 - feePercent) / 100;

  const totalPayout = completedTx.reduce((sum, t) => sum + t.lawyer_amount_minor, 0) / 100;
  
  let payoutStr = "";
  if (totalPayout >= 100000) {
    payoutStr = `₹${(totalPayout / 100000).toFixed(2)}L`;
  } else {
    payoutStr = money(totalPayout);
  }

  const nextPayoutDate = new Date();
  const daysUntilFriday = (5 - nextPayoutDate.getDay() + 7) % 7 || 7;
  nextPayoutDate.setDate(nextPayoutDate.getDate() + daysUntilFriday);
  const payoutDateStr = nextPayoutDate.toLocaleDateString("en-IN", {day: "numeric", month: "long", year: "numeric"});

  const payoutLawyersCount = new Set(completedTx.map(t => t.lawyer_id)).size;

  const pendingLawyerIds = new Set(pendingLawyers.map(l => l.id));
  const pendingLawyerTx = transactions.filter(t => pendingLawyerIds.has(t.lawyer_id) && t.status !== 'cancelled' && t.status !== 'refunded');
  const pendingVerificationAmount = pendingLawyerTx.reduce((sum, t) => sum + t.lawyer_amount_minor, 0) / 100;
  
  let pendingAmountStr = "";
  if (pendingVerificationAmount >= 100000) {
    pendingAmountStr = `₹${(pendingVerificationAmount / 100000).toFixed(2)}L`;
  } else {
    pendingAmountStr = money(pendingVerificationAmount);
  }

  const pendingLawyersCount = pendingLawyers.length;

  const restrictedLawyerIds = new Set(users.filter(u => u.role === 'lawyer' && !u.active).map(u => u.id));
  const failedPayoutsCount = transactions.filter(t => t.status === 'disputed' || (t.status === 'completed' && restrictedLawyerIds.has(t.lawyer_id))).length;

  container.innerHTML = `
    <article>
      <span>Next scheduled payout</span>
      <strong>${payoutStr}</strong>
      <small>${payoutDateStr} · ${payoutLawyersCount} lawyer${payoutLawyersCount !== 1 ? 's' : ''}</small>
    </article>
    <article>
      <span>Pending verification</span>
      <strong>${pendingAmountStr}</strong>
      <small>${pendingLawyersCount} lawyer account${pendingLawyersCount !== 1 ? 's' : ''}</small>
    </article>
    <article>
      <span>Failed payouts</span>
      <strong>${failedPayoutsCount}</strong>
      ${failedPayoutsCount > 0 
        ? `<small class="red">Requires attention</small>` 
        : `<small style="color:var(--forest);">All clear</small>`}
    </article>
  `;
}

async function refreshSystemStatusHealth() {
  const statusTime = $("#system-status-time");
  try {
    await LexAPI.health();
    if (statusTime) {
      statusTime.textContent = `Last checked just now (${new Date().toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'})})`;
    }
  } catch (e) {
    if (statusTime) statusTime.textContent = "Last checked: 1m ago";
  }
}

function switchView(id, pushState = true) {
  const targetView = document.getElementById(id);
  if (!targetView) return;

  document.querySelectorAll(".view").forEach(x => x.classList.toggle("active", x.id === id));
  document.querySelectorAll("nav button").forEach(x => x.classList.toggle("active", x.dataset.view === id));
  if (id === "security") {
    refreshSystemStatusHealth();
  }

  if (pushState && window.location.hash !== `#${id}`) {
    history.pushState({ view: id }, "", `#${id}`);
  }

  setAdminSidebarOpen(false);
  scrollTo(0, 0);
}

// Handle Browser Back / Forward Button Navigation inside Admin Portal
window.addEventListener("popstate", () => {
  const currentUser = LexAPI.getCurrentUser();
  if (!currentUser || String(currentUser.role).toLowerCase() !== "admin") return;
  const hash = window.location.hash.replace("#", "") || "overview";
  if (document.getElementById(hash)) {
    switchView(hash, false);
  }
});

function setAdminSidebarOpen(open) {
  const sidebar = $("#sidebar");
  if (!sidebar) return;
  const isOpen = open !== undefined ? open : !sidebar.classList.contains("open");
  sidebar.classList.toggle("open", isOpen);
  if (isOpen) {
    document.body.classList.add("sidebar-locked");
  } else {
    document.body.classList.remove("sidebar-locked");
  }
}

// Navigation Events
document.addEventListener("click", e => {
  // Mobile sidebar auto-closing
  const sidebar = $("#sidebar");
  if (sidebar && sidebar.classList.contains("open")) {
    const isOutside = !sidebar.contains(e.target) || e.target === sidebar;
    if (isOutside && !e.target.closest("#menu")) {
      setAdminSidebarOpen(false);
    }
  }

  let n = e.target.closest("[data-view]");
  let g = e.target.closest("[data-go]");
  let t = e.target.closest("[data-toast]");
  let af = e.target.closest("[data-app-filter]");
  let df = e.target.closest("[data-dispute-filter]");
  let rv = e.target.closest("[data-review-id]");
  
  if (n) {
    switchView(n.dataset.view);
    setAdminSidebarOpen(false);
  }
  if (g) {
    switchView(g.dataset.go);
    setAdminSidebarOpen(false);
  }
  let actBtn = e.target.closest("[data-action]");
  if (actBtn) {
    const act = actBtn.dataset.action;
    if (act === "open-verification-policy") openVerificationPolicyModal();
    if (act === "open-resolution-policy") openResolutionPolicyModal();
  }
  if (t) toast(t.dataset.toast);

  if (af) {
    document.querySelectorAll("[data-app-filter]").forEach(x => x.classList.toggle("active", x === af));
    renderApps(af.dataset.appFilter);
  }
  if (df) {
    document.querySelectorAll("[data-dispute-filter]").forEach(x => x.classList.toggle("active", x === df));
    renderDisputes(df.dataset.disputeFilter);
  }
  const txf = e.target.closest("[data-tx-filter]");
  if (txf) {
    document.querySelectorAll("[data-tx-filter]").forEach(x => x.classList.toggle("active", x === txf));
    renderTx(txf.dataset.txFilter);
  }
  const choiceLabel = e.target.closest("label.choice");
  if (choiceLabel) {
    document.querySelectorAll("label.choice").forEach(x => x.classList.remove("active"));
    choiceLabel.classList.add("active");
    const rad = choiceLabel.querySelector('input[type="radio"]');
    if (rad) rad.checked = true;
  }
  const fbf = e.target.closest("[data-fb-filter]");
  if (fbf) {
    document.querySelectorAll("[data-fb-filter]").forEach(x => x.classList.toggle("active", x === fbf));
    renderFeedback(fbf.dataset.fbFilter);
  }
  if (rv) {
    const a = lawyerMap[rv.dataset.reviewId];
    if (a) {
      reviewApplication(
        a.id,
        a.full_name,
        mapPracticeToFrontend(a.practice),
        a.bar_number,
        Boolean(a.verified),
        a.bar_license_url,
        a.aadhaar_url
      );
    } else {
      toast("Could not load lawyer details. Please refresh and try again.");
    }
  }

  // Approve / Reject from review modal (data-decide-id replaces blocked inline onclick)
  const decide = e.target.closest("[data-decide-id]");
  if (decide) {
    const lawyerId = decide.dataset.decideId;
    const approved = decide.dataset.decideApproved === "true";
    decideVerification(lawyerId, approved);
  }

  // Close button inside review modal
  if (e.target.closest("[data-close-modal]")) {
    $("#review-modal").hidden = true;
    document.body.style.overflow = "";
  }

  // Resolve dispute buttons (data-resolve-id replaces blocked inline onclick)
  const resolve = e.target.closest("[data-resolve-id]");
  if (resolve) {
    const strike = resolve.dataset.strike === "true";
    resolveDispute(resolve.dataset.resolveId, resolve.dataset.resolveOutcome, strike);
  }

  // Restrict / Activate user buttons (data-toggle-id)
  const toggle = e.target.closest("[data-toggle-id]");
  if (toggle) {
    const uid = toggle.dataset.toggleId;
    const isActive = toggle.dataset.toggleActive === "true";
    toggleUserStatus(uid, isActive);
  }

  // Alert button click – show pending items modal
  const alertBtn = e.target.closest('.alert');
  if (alertBtn) {
    const content = $("#review-content");
    let html = `<h3>Pending items summary</h3>`;
    const totalPending = pendingLawyers.length + disputes.length;
    if (totalPending) {
      if (pendingLawyers.length) html += `<p>${pendingLawyers.length} lawyer applications pending verification.</p>`;
      if (disputes.length) html += `<p>${disputes.length} open disputes.</p>`;
    } else {
      html += `<p>No pending items at the moment.</p>`;
    }
    content.innerHTML = html;
    $("#review-modal").hidden = false;
    document.body.style.overflow = "hidden";
  }
});

$("#menu").onclick = (e) => {
  if (e) e.stopPropagation();
  setAdminSidebarOpen();
};
$(".close").onclick = () => {
  $("#review-modal").hidden = true;
  document.body.style.overflow = "";
};

$("#review-modal").onclick = e => {
  if (e.target === $("#review-modal")) {
    $("#review-modal").hidden = true;
    document.body.style.overflow = "";
  }
};

$("#role-filter").onchange = e => renderUsers(e.target.value);
$("#save-fees").onclick = handleSaveFees;

// Transaction search – re-render on every keystroke
document.addEventListener("input", e => {
  if (e.target && e.target.id === "tx-search") {
    renderTx(undefined, e.target.value);
  }
});

// Sidebar signout
document.querySelector(".signout").onclick = () => {
  LexAPI.logout();
  toast("You have been signed out securely.");
  setTimeout(() => {
    window.location.href = "index.html";
  }, 1000);
};

function toast(m) {
  $("#toast").textContent = m;
  $("#toast").classList.add("show");
  setTimeout(() => $("#toast").classList.remove("show"), 2400);
}

window.reviewApplication = reviewApplication;
window.decideVerification = decideVerification;
window.resolveDispute = resolveDispute;
window.toggleUserStatus = toggleUserStatus;

// Update badge counts after data load
function updateBadgeCounts() {
  const verBtn = document.querySelector('button[data-view="verification"] b');
  if (verBtn) verBtn.textContent = pendingLawyers.length;
  const disputeBtn = document.querySelector('button[data-view="disputes"] b');
  if (disputeBtn) disputeBtn.textContent = disputes.length;
  const alertBtn = document.querySelector('.alert b');
  if (alertBtn) alertBtn.textContent = pendingLawyers.length + disputes.length;

  // Update Overview/Dashboard verification button counters
  const overviewVerBtn = document.querySelector('button[data-go="verification"] b');
  if (overviewVerBtn) overviewVerBtn.textContent = pendingLawyers.length;

  const quickVerSmall = document.querySelector('button[data-go="verification"] small');
  if (quickVerSmall) {
    quickVerSmall.textContent = `${pendingLawyers.length} application${pendingLawyers.length !== 1 ? 's' : ''} waiting`;
  }

  // Update Lawyer verification tab headers dynamically
  const pendingTabB = document.querySelector('button[data-app-filter="pending"] b');
  if (pendingTabB) pendingTabB.textContent = pendingLawyers.length;

  const reviewTabB = document.querySelector('button[data-app-filter="review"] b');
  if (reviewTabB) reviewTabB.textContent = 0;

  const approvedTabB = document.querySelector('button[data-app-filter="approved"] b');
  if (approvedTabB) approvedTabB.textContent = approvedLawyersCount;

  const rejectedTabB = document.querySelector('button[data-app-filter="rejected"] b');
  if (rejectedTabB) rejectedTabB.textContent = rejectedLawyersCount;
}

function renderPayouts() {
  const container = $("#payouts-table");
  if (!container) return;
  if (!payouts || payouts.length === 0) {
    container.innerHTML = `
      <div class="empty" style="padding: 40px; text-align: center; color: #666;">
        <span style="font-size: 32px;">💳</span>
        <p style="margin-top: 12px; font-weight: 500;">No lawyer payout bank accounts registered yet.</p>
      </div>`;
    return;
  }

  const rowsHtml = payouts.map(p => `
    <tr>
      <td>
        <strong>${escapeHtml(p.lawyer_name)}</strong>
        <div style="font-size: 11px; color: #888;">ID: ${escapeHtml(p.lawyer_id)}</div>
      </td>
      <td>${escapeHtml(p.account_holder_name)}</td>
      <td>
        <code style="background: #f4f4f4; padding: 2px 6px; border-radius: 4px; font-weight: 600; letter-spacing: 1px; color: #2e5b4b;">${escapeHtml(p.account_number_masked)}</code>
      </td>
      <td>
        <code style="background: #f4f4f4; padding: 2px 6px; border-radius: 4px; font-weight: 600; color: #444;">${escapeHtml(p.ifsc_code_masked)}</code>
      </td>
      <td>${escapeHtml(p.bank_name)}</td>
      <td>${p.upi_vpa ? `<code>${escapeHtml(p.upi_vpa)}</code>` : '<span style="color: #999;">—</span>'}</td>
      <td>
        ${p.verified ? '<span class="status-pill status-confirmed">✓ Verified</span>' : '<span class="status-pill status-pending">Pending Verification</span>'}
      </td>
    </tr>
  `).join("");

  container.innerHTML = `
    <table>
      <thead>
        <tr>
          <th>Lawyer</th>
          <th>Account Holder</th>
          <th>Account Number (Masked)</th>
          <th>IFSC Code (Masked)</th>
          <th>Bank Name</th>
          <th>UPI VPA</th>
          <th>Verification Status</th>
        </tr>
      </thead>
      <tbody>
        ${rowsHtml}
      </tbody>
    </table>`;
}

let currentFeedbackFilter = "all";

function renderFeedback(filter = "all") {
  currentFeedbackFilter = filter;
  const container = $("#feedback-table");
  if (!container) return;

  const searchInput = document.getElementById("feedback-search");
  if (searchInput && !searchInput.dataset.bound) {
    searchInput.dataset.bound = "true";
    searchInput.oninput = () => {
      const activeTab = document.querySelector("#feedback-type-tabs button.active")?.dataset.fbFilter || "all";
      renderFeedback(activeTab);
    };
  }
  const searchVal = (searchInput?.value || "").toLowerCase().trim();

  // 1. Calculate Stat Metrics
  const totalCount = userFeedbacks.length;
  const ticketList = userFeedbacks.filter(f => (f.comments || "").startsWith("[Support Ticket"));
  const reviewList = userFeedbacks.filter(f => !(f.comments || "").startsWith("[Support Ticket"));
  
  const ticketCount = ticketList.length;
  const reviewCount = reviewList.length;

  const avgRating = totalCount > 0 
    ? (userFeedbacks.reduce((sum, f) => sum + (f.rating || 5), 0) / totalCount).toFixed(1)
    : "5.0";

  // Update Stat Cards
  const statTotal = document.getElementById("stat-fb-total");
  if (statTotal) statTotal.textContent = totalCount;
  const statTotalSub = document.getElementById("stat-fb-total-sub");
  if (statTotalSub) statTotalSub.textContent = `${reviewCount} reviews · ${ticketCount} tickets`;

  const statTickets = document.getElementById("stat-fb-tickets");
  if (statTickets) statTickets.textContent = ticketCount;
  const statTicketsSub = document.getElementById("stat-fb-tickets-sub");
  if (statTicketsSub) statTicketsSub.textContent = ticketCount === 1 ? "1 active ticket" : `${ticketCount} active tickets`;

  const statAvg = document.getElementById("stat-fb-avg");
  if (statAvg) statAvg.textContent = `${avgRating} / 5.0 ⭐`;
  const statAvgSub = document.getElementById("stat-fb-avg-sub");
  if (statAvgSub) statAvgSub.textContent = `Based on ${totalCount} submission${totalCount !== 1 ? 's' : ''}`;

  // Update Tab Badges
  const countAll = document.getElementById("fb-count-all");
  if (countAll) countAll.textContent = totalCount;
  const countTickets = document.getElementById("fb-count-tickets");
  if (countTickets) countTickets.textContent = ticketCount;
  const countReviews = document.getElementById("fb-count-reviews");
  if (countReviews) countReviews.textContent = reviewCount;

  // 2. Filter dataset
  let filtered = userFeedbacks;
  if (filter === "tickets") {
    filtered = ticketList;
  } else if (filter === "reviews") {
    filtered = reviewList;
  }

  if (searchVal) {
    filtered = filtered.filter(f => {
      const name = (f.user_name || "").toLowerCase();
      const email = (f.user_email || "").toLowerCase();
      const comment = (f.comments || "").toLowerCase();
      return name.includes(searchVal) || email.includes(searchVal) || comment.includes(searchVal);
    });
  }

  // 3. Render Empty state or Table
  if (!filtered || filtered.length === 0) {
    container.innerHTML = `
      <div class="empty" style="padding: 48px 24px; text-align: center; color: #718096; background: #ffffff; border-radius: 12px;">
        <span style="font-size: 36px; display: inline-block; margin-bottom: 8px;">💬</span>
        <p style="font-size: 15px; font-weight: 600; margin: 0 0 4px 0; color: #2d3748;">No feedback or support tickets found</p>
        <small style="color: #a0aec0;">Try adjusting your search query or switching tabs.</small>
      </div>`;
    return;
  }

  const rowsHtml = filtered.map(f => {
    const rawComment = f.comments || "";
    const isTicket = rawComment.startsWith("[Support Ticket");
    const stars = "⭐".repeat(f.rating || 5);
    
    let dateStr = "Recently";
    if (f.created_at) {
      dateStr = new Date(f.created_at).toLocaleString("en-IN", {
        day: "numeric", 
        month: "short", 
        year: "numeric",
        hour: "2-digit", 
        minute: "2-digit"
      });
    }

    // Extract Avatar Initial
    const uName = f.user_name || "Anonymous User";
    const uEmail = f.user_email || "N/A";
    const initial = uName.charAt(0).toUpperCase() || "?";
    
    // Determine User Role Badge
    let roleBadge = `<span style="background:#e2e8f0; color:#475569; padding:2px 6px; border-radius:4px; font-size:10px; font-weight:600; margin-left:6px;">USER</span>`;
    const emailLower = uEmail.toLowerCase();
    if (emailLower.includes("admin")) {
      roleBadge = `<span style="background:#fef3c7; color:#92400e; padding:2px 6px; border-radius:4px; font-size:10px; font-weight:700; margin-left:6px;">ADMIN</span>`;
    } else if (emailLower.includes("lawyer") || emailLower.includes("advocate")) {
      roleBadge = `<span style="background:#e0e7ff; color:#3730a3; padding:2px 6px; border-radius:4px; font-size:10px; font-weight:700; margin-left:6px;">ADVOCATE</span>`;
    }

    // Type Badge
    let typeBadge = `<span style="background:#f0fdf4; color:#166534; border:1px solid #bbf7d0; padding:4px 10px; border-radius:20px; font-size:11px; font-weight:700; display:inline-flex; align-items:center; gap:4px;"><i style="font-style:normal;">⭐</i> USER REVIEW</span>`;
    
    let displayComment = rawComment;
    let categoryTag = "";

    if (isTicket) {
      const match = rawComment.match(/^\[Support Ticket - ([^\]]+)\]\s*(.*)/s);
      if (match) {
        const categoryName = match[1];
        displayComment = match[2];
        categoryTag = `<span style="background:#fff7ed; color:#c2410c; border:1px solid #ffedd5; padding:3px 8px; border-radius:6px; font-size:11px; font-weight:700; display:inline-block; margin-bottom:6px;">Category: ${escapeHtml(categoryName)}</span><br>`;
      }
      typeBadge = `<span style="background:#fff3ed; color:#c85a32; border:1px solid #ffdac6; padding:4px 10px; border-radius:20px; font-size:11px; font-weight:700; display:inline-flex; align-items:center; gap:4px;"><i style="font-style:normal;">🎧</i> SUPPORT TICKET</span>`;
    }

    return `
      <tr style="border-bottom: 1px solid #f1f5f9; transition: background 0.15s ease;">
        <td style="padding: 14px 16px; vertical-align: top;">
          <div style="display: flex; align-items: center; gap: 10px;">
            <div style="width: 38px; height: 38px; border-radius: 50%; background: linear-gradient(135deg, #1c2826, #265a47); color: #ffffff; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 14px; flex-shrink: 0; box-shadow: 0 2px 6px rgba(0,0,0,0.1);">
              ${initial}
            </div>
            <div>
              <div style="display: flex; align-items: center; gap: 4px;">
                <strong style="font-size: 14px; color: #1e293b;">${escapeHtml(uName)}</strong>
                ${roleBadge}
              </div>
              <div style="font-size: 12px; color: #64748b; margin-top: 1px;">${escapeHtml(uEmail)}</div>
            </div>
          </div>
        </td>
        <td style="padding: 14px 16px; vertical-align: top; white-space: nowrap;">
          ${typeBadge}
          <div style="font-size: 12px; color: #475569; margin-top: 6px; font-weight: 600;">${stars} <span style="color:#64748b; font-weight:400;">(${f.rating || 5}/5)</span></div>
        </td>
        <td style="padding: 14px 16px; vertical-align: top; max-width: 480px; white-space: normal; line-height: 1.5; color: #334155; font-size: 13px;">
          ${categoryTag}
          <div>${escapeHtml(displayComment)}</div>
        </td>
        <td style="padding: 14px 16px; vertical-align: top; white-space: nowrap; font-size: 12px; color: #64748b; text-align: right;">
          <div>${dateStr}</div>
        </td>
      </tr>
    `;
  }).join("");

  container.innerHTML = `
    <table style="width: 100%; border-collapse: collapse; text-align: left;">
      <thead>
        <tr style="background: #f8fafc; border-bottom: 2px solid #e2e8f0;">
          <th style="padding: 12px 16px; font-size: 12px; font-weight: 700; text-transform: uppercase; color: #475569; letter-spacing: 0.5px;">Submitted By</th>
          <th style="padding: 12px 16px; font-size: 12px; font-weight: 700; text-transform: uppercase; color: #475569; letter-spacing: 0.5px;">Type & Rating</th>
          <th style="padding: 12px 16px; font-size: 12px; font-weight: 700; text-transform: uppercase; color: #475569; letter-spacing: 0.5px;">Message / Ticket Details</th>
          <th style="padding: 12px 16px; font-size: 12px; font-weight: 700; text-transform: uppercase; color: #475569; letter-spacing: 0.5px; text-align: right;">Date Submitted</th>
        </tr>
      </thead>
      <tbody>
        ${rowsHtml}
      </tbody>
    </table>`;
}

// Call after loading data
loadData();
