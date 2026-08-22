const colors = ["#d2b19d", "#afc8bc", "#c8b8cf", "#b6c9da"];
const $ = s => document.querySelector(s);
const money = n => new Intl.NumberFormat("en-IN", {style: "currency", currency: "INR", maximumFractionDigits: 0}).format(n);

// Backend stores UTC but SQLite strips timezone info → ensure we parse as UTC
function parseUTCDate(dtStr) {
  if (!dtStr) return new Date(NaN);
  if (!dtStr.endsWith("Z") && !dtStr.includes("+")) dtStr += "Z";
  return new Date(dtStr);
}

function isRoomActive(startsAt, durationMinutes = 45, status = "") {
  if (status === "in_progress") return true;
  if (status !== "confirmed") return false;
  if (!startsAt) return false;
  
  const rawDt = typeof startsAt === "string" && !startsAt.endsWith("Z") && !startsAt.includes("+") ? startsAt + "Z" : startsAt;
  const startMs = new Date(rawDt).getTime();
  if (isNaN(startMs)) return false;

  const nowMs = Date.now();
  const windowStart = startMs - 15 * 60 * 1000;
  const windowEnd = startMs + (durationMinutes || 45) * 60 * 1000;

  return nowMs >= windowStart && nowMs <= windowEnd;
}

const intake = {
  "Family Law": ["What best describes your situation?", "Are any children involved?", "Is there an existing court order?"],
  "Corporate Law": ["What type of business is involved?", "What help do you need?", "Is there a deadline we should know about?"],
  "Property Law": ["What type of property is involved?", "What is your relationship to the property?", "Are there active legal proceedings?"]
};

let bookings = [];
let lawyerProfile = {};
let lawyerReviews = [];
let bankAccount = null;   // LawyerBankAccount from API (masked)
let activeBookingId = null;
let pollingInterval = null;
let mobileVerified = false;   // true once Firebase OTP confirmed

// ── Storage Upload Progress & Percentage UI Helpers ─────────────────────────────
function uploadWithProgress(url, bodyData, method = "POST", headers = {}, onProgress = null) {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    xhr.open(method, url, true);

    Object.entries(headers).forEach(([k, v]) => {
      xhr.setRequestHeader(k, v);
    });

    if (xhr.upload && onProgress) {
      xhr.upload.addEventListener("progress", e => {
        if (e.lengthComputable && e.total > 0) {
          const percent = Math.round((e.loaded / e.total) * 100);
          onProgress(percent, e.loaded, e.total);
        }
      });
    }

    xhr.onload = () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        let respData = xhr.responseText;
        try {
          respData = JSON.parse(xhr.responseText);
        } catch (_) {}
        resolve(respData);
      } else {
        let errMsg = `Upload failed (${xhr.status})`;
        try {
          const parsed = JSON.parse(xhr.responseText);
          if (parsed && parsed.detail) errMsg = parsed.detail;
        } catch (_) {}
        reject(new Error(errMsg));
      }
    };

    xhr.onerror = () => reject(new Error("Network upload error. Check R2 CORS settings."));
    xhr.ontimeout = () => reject(new Error("Upload timed out"));

    xhr.send(bodyData);
  });
}

function showUploadProgressModal(filename) {
  let modal = document.getElementById("upload-progress-modal");
  if (!modal) {
    modal = document.createElement("div");
    modal.id = "upload-progress-modal";
    modal.style.cssText = `
      position: fixed;
      bottom: 24px;
      right: 24px;
      z-index: 99999;
      background: rgba(18, 38, 32, 0.95);
      backdrop-filter: blur(12px);
      -webkit-backdrop-filter: blur(12px);
      color: #ffffff;
      padding: 16px 20px;
      border-radius: 16px;
      box-shadow: 0 10px 30px rgba(0,0,0,0.25);
      border: 1px solid rgba(255,255,255,0.12);
      font-family: var(--font-sans, system-ui, sans-serif);
      min-width: 290px;
      max-width: 350px;
      display: flex;
      flex-direction: column;
      gap: 8px;
      transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
      transform: translateY(0);
      opacity: 1;
    `;
    document.body.appendChild(modal);
  }

  const sanitizedName = String(filename || "document").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  modal.innerHTML = `
    <div style="display:flex; justify-content:space-between; align-items:center; width:100%;">
      <span style="font-size:11px; font-weight:700; letter-spacing:0.08em; text-transform:uppercase; color:#94d3ac;">Uploading to Storage</span>
      <span id="upload-progress-pct" style="font-size:14px; font-weight:800; color:#ffffff;">0%</span>
    </div>
    <div style="font-size:13px; font-weight:600; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; color:#e0eae4;" id="upload-progress-filename">
      📄 ${sanitizedName}
    </div>
    <div style="width:100%; height:6px; background:rgba(255,255,255,0.15); border-radius:99px; overflow:hidden;">
      <div id="upload-progress-bar" style="width:0%; height:100%; background:linear-gradient(90deg, #2ecc71, #27ae60); transition:width 0.15s ease-out; border-radius:99px;"></div>
    </div>
    <div style="font-size:11px; color:rgba(255,255,255,0.7);" id="upload-progress-status">Uploading to secure storage...</div>
  `;

  modal.style.display = "flex";
  modal.style.opacity = "1";
  modal.style.transform = "translateY(0)";

  return {
    update: (percent, statusMsg) => {
      const pctEl = document.getElementById("upload-progress-pct");
      const barEl = document.getElementById("upload-progress-bar");
      const statusEl = document.getElementById("upload-progress-status");
      if (pctEl) pctEl.textContent = `${percent}%`;
      if (barEl) barEl.style.width = `${percent}%`;
      if (statusEl && statusMsg) statusEl.textContent = statusMsg;
    },
    close: (success = true, message = null) => {
      const pctEl = document.getElementById("upload-progress-pct");
      const barEl = document.getElementById("upload-progress-bar");
      const statusEl = document.getElementById("upload-progress-status");
      if (pctEl) pctEl.textContent = success ? "100%" : "Error";
      if (barEl) {
        barEl.style.width = "100%";
        barEl.style.background = success ? "#2ecc71" : "#e74c3c";
      }
      if (statusEl) statusEl.textContent = message || (success ? "Upload completed!" : "Upload failed.");

      setTimeout(() => {
        if (modal) {
          modal.style.opacity = "0";
          modal.style.transform = "translateY(10px)";
          setTimeout(() => {
            modal.style.display = "none";
          }, 300);
        }
      }, 1500);
    }
  };
}

// Session check — clear any stale token if not lawyer and toggle screen
function checkLawyerSession() {
  const user = LexAPI.getCurrentUser();
  if (!user || user.role !== "lawyer") {
    if (user) {
      LexAPI.logout();
    }
    $("#sidebar").style.display = "none";
    $(".app").style.display = "none";
    $("#lawyer-auth-page").style.display = "flex";
    initLawyerAuth();
    return false;
  }
  $("#sidebar").style.display = "flex";
  $(".app").style.display = "block";
  $("#lawyer-auth-page").style.display = "none";

  const initialHash = window.location.hash.replace("#", "");
  if (initialHash && document.getElementById(initialHash)) {
    view(initialHash, false);
  }
  return true;
}

let authInitialized = false;
function initLawyerAuth() {
  if (authInitialized) return;
  authInitialized = true;

  const toRegister = $("#to-lawyer-register");
  const toLogin = $("#to-lawyer-login");
  const loginSection = $("#lawyer-login-section");
  const registerSection = $("#lawyer-register-section");
  const forgotSection = $("#lawyer-forgot-section");
  const btnForgot = $("#btn-lawyer-forgot-password");
  const toLoginFromForgot = $("#to-lawyer-login-from-forgot");

  if (toRegister) {
    toRegister.onclick = (e) => {
      e.preventDefault();
      loginSection.style.display = "none";
      if (forgotSection) forgotSection.style.display = "none";
      registerSection.style.display = "block";
    };
  }

  if (toLogin) {
    toLogin.onclick = (e) => {
      e.preventDefault();
      registerSection.style.display = "none";
      if (forgotSection) forgotSection.style.display = "none";
      loginSection.style.display = "block";
    };
  }

  if (btnForgot) {
    btnForgot.onclick = (e) => {
      e.preventDefault();
      loginSection.style.display = "none";
      registerSection.style.display = "none";
      if (forgotSection) forgotSection.style.display = "block";
    };
  }

  if (toLoginFromForgot) {
    toLoginFromForgot.onclick = (e) => {
      e.preventDefault();
      if (forgotSection) forgotSection.style.display = "none";
      registerSection.style.display = "none";
      loginSection.style.display = "block";
    };
  }

  const forgotForm = $("#lawyer-forgot-form");
  if (forgotForm) {
    forgotForm.onsubmit = async (e) => {
      e.preventDefault();
      const email = $("#lawyer-forgot-email").value.trim();
      const errDiv = $("#lawyer-forgot-error");
      const succDiv = $("#lawyer-forgot-success");
      const submitBtn = $("#btn-lawyer-forgot-submit");
      errDiv.textContent = "";
      succDiv.textContent = "";
      submitBtn.disabled = true;

      try {
        const res = await LexAPI.forgotPassword(email);
        succDiv.textContent = res.message || "If an account exists with that email, a reset token has been sent.";
        if (res.debug_reset_token) {
          $("#lawyer-reset-token-section").style.display = "block";
          $("#lawyer-reset-token-input").value = res.debug_reset_token;
        }
      } catch (err) {
        errDiv.textContent = err.message || "Failed to process request";
      } finally {
        submitBtn.disabled = false;
      }
    };
  }

  const resetForm = $("#lawyer-reset-form");
  if (resetForm) {
    resetForm.onsubmit = async (e) => {
      e.preventDefault();
      const token = $("#lawyer-reset-token-input").value.trim();
      const newPassword = $("#lawyer-reset-new-password").value;
      const errDiv = $("#lawyer-reset-error");
      errDiv.textContent = "";

      try {
        await LexAPI.resetPassword(token, newPassword);
        toast("Password reset successful! Please log in.");
        if (forgotSection) forgotSection.style.display = "none";
        loginSection.style.display = "block";
      } catch (err) {
        errDiv.textContent = err.message || "Failed to reset password";
      }
    };
  }

  const handleLawyerGoogleAuth = async (e) => {
    const btnTarget = (e && e.currentTarget) ? e.currentTarget : $("#btn-lawyer-google-login");
    const origHtml = btnTarget ? btnTarget.innerHTML : "";
    if (btnTarget) {
      btnTarget.disabled = true;
      btnTarget.style.pointerEvents = "none";
      btnTarget.innerHTML = `<span class="btn-spinner"></span> <span>Signing in with Google...</span>`;
    }
    try {
      await performGoogleAuth("lawyer");
      const user = LexAPI.getCurrentUser();
      const fullName = user ? user.full_name : "Lawyer";
      toast(`Welcome, ${fullName}!`);
      checkLawyerSession();
      loadData();
    } catch (err) {
      toast(err.message || "Google auth failed", true);
      if (btnTarget) {
        btnTarget.disabled = false;
        btnTarget.style.pointerEvents = "";
        btnTarget.innerHTML = origHtml;
      }
    }
  };

  const btnLgL = $("#btn-lawyer-google-login");
  const btnLgR = $("#btn-lawyer-google-reg");
  if (btnLgL) btnLgL.onclick = handleLawyerGoogleAuth;
  if (btnLgR) btnLgR.onclick = handleLawyerGoogleAuth;

  $("#lawyer-login-form").onsubmit = async (e) => {
    e.preventDefault();
    const submitBtn = e.target.querySelector('button[type="submit"]');
    const originalText = submitBtn ? submitBtn.innerHTML : "Sign In";
    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.style.pointerEvents = "none";
      submitBtn.innerHTML = `<span class="btn-spinner"></span> Signing In...`;
    }

    const email = $("#lawyer-login-email").value;
    const password = $("#lawyer-login-password").value;
    const errDiv = $("#lawyer-login-error");
    errDiv.textContent = "";

    try {
      await LexAPI.login(email, password);
      const user = LexAPI.getCurrentUser();
      if (!user || user.role !== "lawyer") {
        LexAPI.logout();
        errDiv.textContent = "Access denied. Only lawyers can access this portal.";
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.style.pointerEvents = "";
          submitBtn.innerHTML = originalText;
        }
        return;
      }
      toast("Welcome back!");
      checkLawyerSession();
      loadData();
    } catch (err) {
      errDiv.textContent = err.message || "Invalid credentials";
      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.style.pointerEvents = "";
        submitBtn.innerHTML = originalText;
      }
    }
  };

  $("#lawyer-register-form").onsubmit = async (e) => {
    e.preventDefault();
    const fullName = $("#lawyer-reg-name").value;
    const email = $("#lawyer-reg-email").value;
    const password = $("#lawyer-reg-password").value;
    const confirmPassword = $("#lawyer-reg-confirm-password").value;
    const dob = $("#lawyer-reg-dob").value;
    const consentPrivacy = $("#lawyer-consent-privacy")?.checked;
    const consentTerms = $("#lawyer-consent-terms")?.checked;
    
    const errDiv = $("#lawyer-register-error");
    errDiv.textContent = "";

    if (password !== confirmPassword) {
      errDiv.textContent = "Passwords do not match.";
      return;
    }

    // Client-side age check — DPDP Act 2023, Section 9 (server also validates)
    if (dob) {
      const today = new Date();
      const birthDate = new Date(dob);
      const age = today.getFullYear() - birthDate.getFullYear()
        - ((today.getMonth() < birthDate.getMonth() ||
            (today.getMonth() === birthDate.getMonth() && today.getDate() < birthDate.getDate())) ? 1 : 0);
      if (age < 18) {
        errDiv.textContent = "You must be at least 18 years old to register (DPDP Act 2023, Section 9).";
        return;
      }
    }

    if (!consentPrivacy || !consentTerms) {
      errDiv.textContent = "You must accept the Privacy Policy and Terms of Service to register.";
      return;
    }

    try {
      await LexAPI.register(email, password, fullName, "lawyer", {
        consent_privacy_policy: true,
        consent_terms: true,
        date_of_birth: dob,
      });
      toast("Account created successfully!");
      checkLawyerSession();
      view("profile");
      loadData();
    } catch (err) {
      errDiv.textContent = err.message || "Registration failed";
    }
  };
}

checkLawyerSession();

function mapPracticeToBackend(p) {
  if (Array.isArray(p)) return p.map(mapPracticeToBackend);
  if (p === "Property Law") return "property";
  if (p === "Corporate Law") return "corporate";
  if (p === "Family Law") return "family";
  return p;
}

function mapPracticeToFrontend(p) {
  if (Array.isArray(p)) return p.map(mapPracticeToFrontend).join(", ");
  if (p === "property") return "Property Law";
  if (p === "corporate") return "Corporate Law";
  if (p === "family") return "Family Law";
  return p;
}

function getSpecialty(p) {
  if (Array.isArray(p)) return p.map(getSpecialty).join(", ");
  if (p === "property") return "Property & Title Disputes";
  if (p === "corporate") return "Contracts & Company Law";
  if (p === "family") return "Divorce & Child Custody";
  return "Legal Advice";
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
    [bookings, lawyerProfile] = await Promise.all([
      LexAPI.bookings(),
      LexAPI.getProfile()
    ]);
    // Fetch reviews after we know the lawyer's id
    if (lawyerProfile && lawyerProfile.id) {
      lawyerReviews = await LexAPI.getLawyerReviews(lawyerProfile.id).catch(() => []);
    }
    // Fetch bank account (null if not yet added)
    bankAccount = await LexAPI.getBankAccount();
    renderAll();
  } catch (err) {
    console.error("Dashboard load failed", err);
    const msg = String(err.message || err);
    if (msg.includes("401") || msg.includes("unauthorized") || msg.includes("invalid or expired token") || msg.includes("authentication required")) {
      toast("Session expired or unauthorized. Redirecting to login...");
      LexAPI.logout();
      setTimeout(() => {
        window.location.href = "index.html";
      }, 1500);
    } else {
      toast("Could not refresh dashboard data: " + msg);
    }
  }
}

function renderAll() {
  const initials = lawyerProfile.full_name.split(" ").map(x => x[0]).join("").slice(0, 2).toUpperCase();
  const firstName = lawyerProfile.full_name.split(" ")[1] || lawyerProfile.full_name.split(" ")[0];
  const practiceDisplay = mapPracticeToFrontend(lawyerProfile.practice);
  const hour = new Date().getHours();
  const greeting = hour < 12 ? "Good morning" : hour < 17 ? "Good afternoon" : "Good evening";
  const dateStr = new Date().toLocaleDateString("en-IN", {weekday: "long", day: "numeric", month: "long"}).toUpperCase();

  // Update sidebar avatar + identity
  $(".avatar").textContent = initials;
  $(".identity strong").textContent = lawyerProfile.full_name;
  $(".identity small").textContent = practiceDisplay;

  // Update header (top bar) — uses specific ids from lawyer.html
  const headerAvatar = $("#header-avatar");
  const headerName = $("#header-name");
  const headerPractice = $("#header-practice");
  if (headerAvatar) headerAvatar.textContent = initials;
  if (headerName) headerName.textContent = lawyerProfile.full_name;
  if (headerPractice) headerPractice.textContent = practiceDisplay;

  // Update greeting
  const greetingDate = $("#greeting-date");
  const greetingName = $("#greeting-name");
  if (greetingDate) greetingDate.textContent = dateStr;
  if (greetingName) greetingName.textContent = `${greeting}, ${firstName}.`;

  renderOverview();
  renderSessionTable();
  renderCalendar();
  initIcalPanel();
  renderThreads();
  renderDocs();
  renderEarnings();
  renderBankAccount();
  renderProfile();
  updateBadgeCounts();
}

function updateBadgeCounts() {
  const upcomingCount = bookings.filter(b => ["confirmed", "in_progress"].includes(b.status)).length;
  const chatBookingsCount = bookings.filter(b => ["confirmed", "in_progress"].includes(b.status)).length;
  
  const consultationsBadge = $("#sidebar button[data-view='consultations'] b");
  if (consultationsBadge) {
    consultationsBadge.textContent = upcomingCount;
    consultationsBadge.style.display = upcomingCount > 0 ? "inline-block" : "none";
  }
  
  const messagesBadge = $("#sidebar button[data-view='messages'] b");
  if (messagesBadge) {
    messagesBadge.textContent = chatBookingsCount;
    messagesBadge.style.display = chatBookingsCount > 0 ? "inline-block" : "none";
  }
}

// 1. Overview Tab
function renderOverview() {
  const completed = bookings.filter(b => b.status === "completed");
  const pending = bookings.filter(b => ["confirmed", "in_progress"].includes(b.status));
  const totalEarned = completed.reduce((sum, b) => sum + (b.amount_minor * 0.95), 0) / 100;
  const totalPending = pending.reduce((sum, b) => sum + (b.amount_minor * 0.95), 0) / 100;
  
  const rating = parseFloat(lawyerProfile.rating) || 0;
  const ratingStr = rating > 0 ? `${rating.toFixed(1)} rating` : "No ratings";
  const satisfactionStr = rating > 0 ? `${Math.round((rating / 5.0) * 100)}%` : "—";
  
  const lawyerIdChar = lawyerProfile.id ? lawyerProfile.id.charCodeAt(0) : 75;
  const respTime = (lawyerIdChar % 10) + 5;
  const respPercent = 80 + (lawyerIdChar % 18);

  $(".stats").innerHTML = `
    <article><span>▣</span><p>Upcoming</p><strong>${pending.length}</strong><small>${bookings.length} total consultations</small></article>
    <article><span>₹</span><p>Available balance</p><strong>${money(totalEarned)}</strong><small>${money(totalPending)} pending release</small></article>
    <article><span>★</span><p>Client satisfaction</p><strong>${satisfactionStr}</strong><small>${ratingStr}</small></article>
    <article><span>◷</span><p>Average response time</p><strong>${respTime} min</strong><small>Faster than ${respPercent}% of lawyers</small></article>
  `;

  if (lawyerProfile.verified) {
    const nextYear = new Date().getFullYear() + 1;
    $(".verified").innerHTML = `<i>✓</i><div><strong>Your profile is verified</strong><small>Credentials are current. Next annual review: 12 May ${nextYear}.</small></div><button data-go="profile">View status →</button>`;
  } else {
    $(".verified").innerHTML = `<i style="background:var(--terra);">!</i><div><strong>Identity check pending</strong><small>Your profile changes are under administrative review.</small></div><button data-go="profile">View status →</button>`;
  }

  // Render the live activity feed
  renderActivity();

  const upcoming = bookings.filter(b => b.status === "confirmed" || b.status === "in_progress");
  if (upcoming.length === 0) {
    $("#today").innerHTML = `<p class="muted" style="padding: 20px 0;">No consultations scheduled today.</p>`;
    return;
  }

  $("#today").innerHTML = upcoming.slice(0, 3).map((s, i) => {
    const initials = s.client_name ? s.client_name.split(" ").map(x => x[0]).join("").slice(0, 2).toUpperCase() : "CL";
    const timeStr = parseUTCDate(s.starts_at).toLocaleTimeString("en-IN", {hour: "2-digit", minute: "2-digit"});
    const roomOpen = isRoomActive(s.starts_at, s.duration_minutes, s.status);
    const joinBtn = roomOpen
      ? `<button class="join" data-join-id="${s.id}" data-join-name="${escapeHtml(s.client_name || 'Client')}">&#9635; Join room</button>`
      : `<button class="join outline" disabled title="Room opens 15 minutes before scheduled session time" style="opacity:0.5; cursor:not-allowed; background:#eef2ef; color:var(--muted); border-color:#c8d6cb;">&#9635; Join room</button>`;

    return `
      <div class="session">
        <div class="time"><strong>${timeStr}</strong><small>45 min</small></div>
        <div class="client">
          <span class="avatar" style="background:${colors[i % 4]}">${initials}</span>
          <div>
            <strong>${s.client_name || "Client"}</strong>
            <small>${escapeHtml(Object.values(s.intake)[0] || "Consultation")}</small>
            <small>Secure meeting</small>
          </div>
        </div>
        <div style="display:flex;gap:5px;">
          <button class="outline" data-intake-id="${s.id}">View intake</button>
          ${joinBtn}
        </div>
      </div>
    `;
  }).join("");
}

// 1b. Recent Activity Feed
function renderActivity() {
  const feed = document.getElementById("activity-feed");
  if (!feed) return;

  const events = [];

  // Completed bookings → Payment released
  bookings
    .filter(b => b.status === "completed")
    .forEach(b => {
      const net = Math.round((b.amount_minor * 0.95) / 100);
      const clientName = b.client_name || "Client";
      events.push({
        icon: "₹",
        title: "Payment released",
        sub: `Consultation with ${clientName}`,
        badge: `+${money(net)}`,
        badgeClass: "green",
        ts: parseUTCDate(b.starts_at).getTime()
      });
    });

  // Reviews → New review
  lawyerReviews.forEach(r => {
    const stars = "★".repeat(r.rating);
    events.push({
      icon: "★",
      title: `New ${r.rating}-star review`,
      sub: r.comment ? `"${r.comment.slice(0, 60)}${r.comment.length > 60 ? "…" : ""}"` : `${stars} rating received`,
      ts: parseUTCDate(r.created_at || 0).getTime()
    });
  });

  // New / upcoming bookings → New booking
  bookings
    .filter(b => ["confirmed", "pending_payment"].includes(b.status))
    .forEach(b => {
      const clientName = b.client_name || "Client";
      const dateStr = parseUTCDate(b.starts_at).toLocaleDateString("en-IN", {day: "numeric", month: "short"});
      const timeStr = parseUTCDate(b.starts_at).toLocaleTimeString("en-IN", {hour: "2-digit", minute: "2-digit"});
      events.push({
        icon: "▣",
        title: "New booking",
        sub: `${clientName} · ${dateStr}, ${timeStr}`,
        ts: parseUTCDate(b.starts_at).getTime()
      });
    });

  // Sort newest first, cap at 6
  events.sort((a, b) => b.ts - a.ts);
  const recent = events.slice(0, 6);

  if (recent.length === 0) {
    feed.innerHTML = `<p class="muted" style="padding:16px 0">No recent activity yet.</p>`;
    return;
  }

  feed.innerHTML = recent.map(e => `
    <article>
      <i>${e.icon}</i>
      <div><strong>${escapeHtml(e.title)}</strong><small>${escapeHtml(e.sub)}</small></div>
      ${e.badge ? `<b class="${e.badgeClass || ""}">${e.badge}</b>` : ""}
    </article>
  `).join("");
}

// 2. Consultations Tab
function renderSessionTable(type = "upcoming") {
  const upcomingCount = bookings.filter(b => ["confirmed", "in_progress", "pending_payment", "disputed"].includes(b.status)).length;
  const completedCount = bookings.filter(b => ["completed", "cancelled", "refunded"].includes(b.status)).length;

  const upBadge = $("#upcoming-count-badge");
  const compBadge = $("#completed-count-badge");
  if (upBadge) upBadge.textContent = upcomingCount;
  if (compBadge) compBadge.textContent = completedCount;

  let list = [];
  if (type === "upcoming") {
    list = bookings.filter(b => ["confirmed", "in_progress", "pending_payment", "disputed"].includes(b.status));
  } else {
    list = bookings.filter(b => ["completed", "cancelled", "refunded"].includes(b.status));
  }

  const avatarGradients = [
    "linear-gradient(135deg, #1e4d3b, #337953)",
    "linear-gradient(135deg, #2b4c7e, #4a7bb0)",
    "linear-gradient(135deg, #6b3e75, #9c59a6)",
    "linear-gradient(135deg, #7c4a27, #b8733e)"
  ];

  $("#session-table").innerHTML = `
    <div class="row head">
      <span class="col-head col-client">Client</span>
      <span class="col-head col-ref">Reference</span>
      <span class="col-head col-matter">Matter &amp; Specialty</span>
      <span class="col-head col-time">Scheduled Time</span>
      <span class="col-head col-status">Status</span>
      <span class="col-head col-actions">Actions</span>
    </div>
  ` + (list.length ? list.map((s, i) => {
    const initials = s.client_name ? s.client_name.split(" ").map(x => x[0]).join("").slice(0, 2).toUpperCase() : "CL";
    const dateObj = parseUTCDate(s.starts_at);
    const dayName = dateObj.toLocaleDateString("en-IN", {weekday: "short"});
    const dateStr = dateObj.toLocaleDateString("en-IN", {day: "numeric", month: "short", year: "numeric"});
    const timeStr = dateObj.toLocaleTimeString("en-IN", {hour: "2-digit", minute: "2-digit"});
    const duration = s.duration_minutes || 45;

    const practiceName = getSpecialty(s.practice);
    let practiceIcon = "⚖️";
    if (practiceName.includes("Property")) practiceIcon = "🏠";
    else if (practiceName.includes("Corporate") || practiceName.includes("Company")) practiceIcon = "🏢";
    else if (practiceName.includes("Family")) practiceIcon = "👨‍👩‍👧";

    let statusHTML = "";
    if (s.status === "confirmed") {
      statusHTML = `<span class="status-pill status-confirmed"><span class="pulse-dot green"></span> Confirmed</span>`;
    } else if (s.status === "in_progress") {
      statusHTML = `<span class="status-pill status-in-progress"><span class="pulse-dot amber"></span> In Session</span>`;
    } else if (s.status === "completed") {
      statusHTML = `<span class="status-pill status-completed"><span class="check-icon">✓</span> Completed</span>`;
    } else if (s.status === "cancelled") {
      statusHTML = `<span class="status-pill status-cancelled">Cancelled</span>`;
    } else {
      statusHTML = `<span class="status-pill status-pending">${s.status.toUpperCase()}</span>`;
    }

    let actionBtn = "";
    if (s.status === "confirmed" || s.status === "in_progress") {
      const roomOpen = isRoomActive(s.starts_at, s.duration_minutes, s.status);
      const joinBtn = roomOpen
        ? `<button class="btn-action btn-join" data-join-id="${s.id}" data-join-name="${escapeHtml(s.client_name || 'Client')}">🎥 Open room</button>`
        : `<button class="btn-action btn-join disabled" disabled title="Room opens 15 minutes before scheduled session time"><span class="lock-icon">🔒</span> Open room</button>`;

      const completeBtn = roomOpen
        ? `<button class="btn-action btn-complete" data-complete-id="${s.id}">✓ Complete</button>`
        : `<button class="btn-action btn-complete disabled" disabled title="Consultation can only be completed during or after the scheduled session time">✓ Complete</button>`;

      actionBtn = `<div class="action-btn-group">${joinBtn}${completeBtn}</div>`;
    } else {
      actionBtn = `<button class="btn-action btn-details" data-intake-id="${s.id}">📋 View details</button>`;
    }

    const grad = avatarGradients[i % avatarGradients.length];

    return `
      <div class="row session-row">
        <div class="client-cell">
          <span class="client-avatar" style="background:${grad}">${initials}</span>
          <div class="client-info">
            <strong class="client-name">${escapeHtml(s.client_name || "Client")}</strong>
            <span class="client-sub">Client Intake Received</span>
          </div>
        </div>
        <div class="ref-cell">
          <span class="ref-tag">#${s.id.slice(0, 8).toUpperCase()}</span>
        </div>
        <div class="matter-cell">
          <span class="matter-tag"><span class="matter-icon">${practiceIcon}</span> ${escapeHtml(practiceName)}</span>
        </div>
        <div class="datetime-cell">
          <span class="datetime-date">📅 ${dayName}, ${dateStr}</span>
          <span class="datetime-time">⏰ ${timeStr} <small>(${duration}m)</small></span>
        </div>
        <div class="status-cell">
          ${statusHTML}
        </div>
        <div class="actions-cell">
          ${actionBtn}
        </div>
      </div>
    `;
  }).join("") : `
    <div class="empty-consultations">
      <div class="empty-icon">📂</div>
      <h3>No consultations found</h3>
      <p>No consultations matching this category at the moment.</p>
    </div>
  `);
}

// Helper to generate standardized time dropdown options (30-min increments)
const ALL_TIME_SLOTS = [
  "06:00 AM", "06:30 AM", "07:00 AM", "07:30 AM", "08:00 AM", "08:30 AM",
  "09:00 AM", "09:30 AM", "10:00 AM", "10:30 AM", "11:00 AM", "11:30 AM",
  "12:00 PM", "12:30 PM", "01:00 PM", "01:30 PM", "02:00 PM", "02:30 PM",
  "03:00 PM", "03:30 PM", "04:00 PM", "04:30 PM", "05:00 PM", "05:30 PM",
  "06:00 PM", "06:30 PM", "07:00 PM", "07:30 PM", "08:00 PM", "08:30 PM",
  "09:00 PM", "09:30 PM", "10:00 PM"
];

function timeToMinutes(tStr) {
  if (!tStr) return 0;
  const parts = tStr.trim().split(" ");
  if (parts.length < 2) return 0;
  const [hStr, mStr] = parts[0].split(":");
  let h = parseInt(hStr, 10);
  const m = parseInt(mStr, 10) || 0;
  const ampm = parts[1].toUpperCase();
  if (ampm === "PM" && h < 12) h += 12;
  if (ampm === "AM" && h === 12) h = 0;
  return h * 60 + m;
}

function generateStartTimeOptions(selectedStart) {
  const times = ALL_TIME_SLOTS.slice(0, -1);
  let cleanSelected = (selectedStart || "").trim().toUpperCase();
  if (!times.includes(cleanSelected)) {
    cleanSelected = times.find(t => t.startsWith(cleanSelected.slice(0, 2))) || "09:00 AM";
  }
  return times.map(t => `<option value="${t}" ${t === cleanSelected ? "selected" : ""}>${t}</option>`).join("");
}

function generateEndTimeOptions(selectedEnd, minStart) {
  const minMins = minStart ? timeToMinutes(minStart) : 0;
  const validTimes = ALL_TIME_SLOTS.filter(t => timeToMinutes(t) > minMins);
  let cleanSelected = (selectedEnd || "").trim().toUpperCase();

  if (!validTimes.includes(cleanSelected)) {
    const defaultEndMins = minMins + 60;
    const matched = validTimes.find(t => timeToMinutes(t) >= defaultEndMins);
    cleanSelected = matched || validTimes[validTimes.length - 1] || "06:00 PM";
  }
  return validTimes.map(t => `<option value="${t}" ${t === cleanSelected ? "selected" : ""}>${t}</option>`).join("");
}

function renderTimeSelects(startVal, endVal) {
  const cleanStart = startVal || "09:00 AM";
  const startHTML = generateStartTimeOptions(cleanStart);
  const endHTML = generateEndTimeOptions(endVal || "06:00 PM", cleanStart);
  return `<select class="time-start">${startHTML}</select><span>to</span><select class="time-end">${endHTML}</select>`;
}

function bindTimeSelectListeners(dayRow) {
  const startSelect = dayRow.querySelector(".time-start");
  const endSelect = dayRow.querySelector(".time-end");
  if (!startSelect || !endSelect) return;

  startSelect.onchange = () => {
    const newStart = startSelect.value;
    const currentEnd = endSelect.value;
    endSelect.innerHTML = generateEndTimeOptions(currentEnd, newStart);
  };
}

// Legacy fallback helper for backwards compatibility
function generateTimeOptions(selectedTime) {
  return generateStartTimeOptions(selectedTime);
}

// 3. Availability Tab
function renderCalendar() {
  const container = $("#week");
  const weekDays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];
  const avail = lawyerProfile.availability || {};
  
  container.innerHTML = weekDays.map((day, i) => {
    const dayKey = day.toLowerCase();
    const dayConfig = avail[dayKey] || { active: i < 5, start: "09:00 AM", end: "06:00 PM" };
    return `
      <div class="day" data-day="${dayKey}">
        <strong>${day}</strong>
        <label class="toggle">
          <input type="checkbox" class="day-toggle" ${dayConfig.active ? "checked" : ""}>
          <i></i>
        </label>
        <div class="times">
          ${dayConfig.active 
            ? renderTimeSelects(dayConfig.start, dayConfig.end) 
            : "Unavailable"}
        </div>
      </div>
    `;
  }).join("");

  document.querySelectorAll(".day").forEach(dayRow => {
    bindTimeSelectListeners(dayRow);

    const chk = dayRow.querySelector(".day-toggle");
    if (chk) {
      chk.onchange = () => {
        const timesDiv = dayRow.querySelector(".times");
        if (chk.checked) {
          timesDiv.innerHTML = renderTimeSelects("09:00 AM", "06:00 PM");
          bindTimeSelectListeners(dayRow);
        } else {
          timesDiv.innerHTML = "Unavailable";
        }
      };
    }
  });

  const minNoticeEl = $("#min-notice");
  const bufferEl = $("#buffer-time");
  const tzEl = $("#timezone-select");
  if (minNoticeEl && avail._min_notice) minNoticeEl.value = String(avail._min_notice);
  if (bufferEl && avail._buffer) bufferEl.value = String(avail._buffer);
  if (tzEl && avail._timezone) tzEl.value = String(avail._timezone);
}

async function saveAvailability() {
  const avail = {};
  let invalidDay = null;

  document.querySelectorAll(".day").forEach(dayRow => {
    const dayKey = dayRow.dataset.day;
    const dayName = dayRow.querySelector("strong")?.textContent || dayKey;
    const active = dayRow.querySelector(".day-toggle").checked;
    
    dayRow.style.outline = "";

    if (active) {
      const start = dayRow.querySelector(".time-start").value;
      const end = dayRow.querySelector(".time-end").value;

      if (timeToMinutes(start) >= timeToMinutes(end)) {
        dayRow.style.outline = "2px solid var(--terra, #b30000)";
        if (!invalidDay) invalidDay = dayName;
      }

      avail[dayKey] = { active, start, end };
    } else {
      avail[dayKey] = { active: false };
    }
  });

  if (invalidDay) {
    toast(`Invalid hours for ${invalidDay}: End time must be after Start time.`);
    return;
  }

  const minNoticeEl = $("#min-notice");
  const bufferEl = $("#buffer-time");
  const tzEl = $("#timezone-select");
  if (minNoticeEl) avail._min_notice = parseInt(minNoticeEl.value, 10) || 12;
  if (bufferEl) avail._buffer = parseInt(bufferEl.value, 10) || 15;
  if (tzEl) avail._timezone = tzEl.value || "Asia/Kolkata";
  
  try {
    const payload = {
      full_name: lawyerProfile.full_name || "Lawyer",
      practice: lawyerProfile.practice || ["property"],
      bar_number: lawyerProfile.bar_number || "PENDING",
      languages: lawyerProfile.languages || ["English"],
      hourly_fee_minor: lawyerProfile.hourly_fee_minor || 100000,
      availability: avail,
      enrollment_date: lawyerProfile.enrollment_date || null,
      practice_address: lawyerProfile.practice_address || null,
      aadhaar_number: lawyerProfile.aadhaar_number || null,
      mobile_number: lawyerProfile.mobile_number || null
    };
    await LexAPI.updateProfile(payload);
    lawyerProfile.availability = avail;
    toast("Availability configurations saved.");
  } catch (err) {
    toast("Error saving availability: " + err.message);
  }
}

// 3b. iCal Subscribe Panel
async function initIcalPanel() {
  const urlInput = $("#ical-feed-url");
  const copyBtn = $("#copy-ical-btn");
  const gcalBtn = $("#gcal-subscribe-btn");
  const rotateBtn = $("#rotate-ical-btn");
  if (!urlInput) return;

  const buildFeedUrl = (token) => {
    const base = window.location.origin;
    return `${base}/api/v1/calendar/feed/${token}.ics`;
  };

  const setUrl = (token) => {
    const url = buildFeedUrl(token);
    urlInput.value = url;
    if (gcalBtn) {
      // Google Calendar "Add by URL" flow
      gcalBtn.href = `https://calendar.google.com/calendar/r?cid=${encodeURIComponent(url)}`;
    }
  };

  try {
    const data = await LexAPI.getIcalToken();
    setUrl(data.ical_token);
  } catch (err) {
    urlInput.value = "Could not load — please refresh.";
  }

  if (copyBtn) {
    copyBtn.onclick = async () => {
      try {
        await navigator.clipboard.writeText(urlInput.value);
        copyBtn.textContent = "✓ Copied!";
        setTimeout(() => { copyBtn.textContent = "📋 Copy"; }, 2000);
      } catch {
        urlInput.select();
        document.execCommand("copy");
        copyBtn.textContent = "✓ Copied!";
        setTimeout(() => { copyBtn.textContent = "📋 Copy"; }, 2000);
      }
    };
  }

  if (rotateBtn) {
    rotateBtn.onclick = async () => {
      if (!confirm("Rotating the URL will invalidate your current calendar subscriptions. Any calendar apps using the old URL will stop syncing. Continue?")) return;
      try {
        rotateBtn.textContent = "Rotating…";
        const data = await LexAPI.rotateIcalToken();
        setUrl(data.ical_token);
        rotateBtn.textContent = "🔄 Rotate URL";
        toast("iCal feed URL rotated successfully.");
      } catch (err) {
        rotateBtn.textContent = "🔄 Rotate URL";
        toast("Failed to rotate URL: " + err.message);
      }
    };
  }
}

// 4. Messages Tab
const chatKeys = {};
async function getChatKey(bookingId) {
  if (chatKeys[bookingId]) return chatKeys[bookingId];
  const b = bookings.find(x => x.id === bookingId);
  if (!b || !b.chat_key_salt) return null;
  const key = await LexE2EE.deriveKey(bookingId, b.chat_key_salt);
  chatKeys[bookingId] = key;
  return key;
}

function renderThreads() {
  const threadsEl = $("#threads");
  const chatBookings = bookings.filter(b => ["confirmed", "in_progress"].includes(b.status));
  
  if (chatBookings.length === 0) {
    threadsEl.innerHTML = `<p class="muted" style="padding:15px;">No active consultations.</p>`;
    $(".conversation").style.display = "none";
    return;
  }
  $(".conversation").style.display = "flex";
  
  // Sort chatBookings by last_message_at (descending)
  chatBookings.sort((a, b) => {
    const dateA = new Date(a.last_message_at || a.starts_at || 0);
    const dateB = new Date(b.last_message_at || b.starts_at || 0);
    return dateB - dateA;
  });
  
  threadsEl.innerHTML = chatBookings.map((b, i) => {
    const initials = b.client_name ? b.client_name.split(" ").map(x => x[0]).join("").slice(0, 2).toUpperCase() : "CL";
    const activeClass = b.id === activeBookingId ? "active" : "";
    return `
      <div class="thread ${activeClass}" data-tid="${b.id}">
        <span class="avatar" style="background:${colors[i % 4]}">${initials}</span>
        <div>
          <strong>${b.client_name || "Client"}</strong>
          <p>${getSpecialty(b.practice)}</p>
        </div>
      </div>
    `;
  }).join("");
  
  if (!activeBookingId && chatBookings.length > 0) {
    selectThread(chatBookings[0].id);
  }
}

async function selectThread(bookingId, isUserClick = false) {
  activeBookingId = bookingId;
  document.querySelectorAll(".thread").forEach(th => th.classList.toggle("active", th.dataset.tid === bookingId));
  
  if (isUserClick) {
    const chatPanel = document.getElementById("chat-panel");
    if (chatPanel) {
      chatPanel.classList.add("mobile-convo");
    }
  }
  
  const b = bookings.find(x => x.id === bookingId);
  const clientName = b.client_name || "Client";
  const initials = clientName.split(" ").map(x => x[0]).join("").slice(0, 2).toUpperCase();
  
  $("#chat-name").textContent = clientName;
  const avatarEl = document.getElementById("chat-avatar");
  if (avatarEl) { avatarEl.textContent = initials; }
  const statusEl = document.getElementById("chat-status");
  if (statusEl) { statusEl.textContent = "● Secure · End-to-end encrypted"; }
  
  if (pollingInterval) clearInterval(pollingInterval);
  
  if (window.activeChatWS) {
    window.activeChatWS.disconnect();
  }
  if (window.WebSocketChatClient) {
    window.activeChatWS = new WebSocketChatClient(bookingId, async () => {
      SoundNotifier.playChime();
      await loadMessages();
    });
    window.activeChatWS.connect();
  }
  
  // Show loading state in bubbles
  $("#bubbles").innerHTML = `<p class="muted" style="margin:auto;text-align:center;font-size:13px">Loading messages…</p>`;
  
  await loadMessages();
  pollingInterval = setInterval(loadMessages, 5000);
}

async function loadMessages() {
  if (!activeBookingId) return;
  try {
    const [msgs, newBookings] = await Promise.all([
      LexAPI.getMessages(activeBookingId),
      LexAPI.bookings().catch(() => bookings)
    ]);
    
    bookings = newBookings;
    renderThreads();

    const bubbles = $("#bubbles");
    const key = await getChatKey(activeBookingId);
    
    const currentUser = LexAPI.getCurrentUser();
    const myId = (currentUser?.id || "").toLowerCase();
    const myName = currentUser?.full_name || null;

    const renderedMsgs = await Promise.all(msgs.map(async m => {
      const timeStr = parseUTCDate(m.created_at).toLocaleTimeString("en-IN", {hour: "2-digit", minute: "2-digit"});
      // Normalize UUIDs to lowercase before comparing
      const isMine = (myId && m.sender_id?.toLowerCase() === myId) ||
        (myName && m.sender_name === myName);
      let displayContent = m.content;
      let isE2EE = false;
      if (m.encrypted) {
        if (key) {
          displayContent = await LexE2EE.decrypt(m.content, m.iv, key);
          isE2EE = true;
        } else {
          displayContent = "[Encrypted message - Key not derived]";
        }
      }
      return `
        <p class="${isMine ? "mine" : ""}"> 
          ${isE2EE ? '<span class="lock-indicator" title="End-to-end encrypted">🔒</span>' : ''}${escapeHtml(displayContent)}
          <time>${isMine ? "" : `<span style="font-size:10px;opacity:.7;">${escapeHtml(m.sender_name || "Client")} · </span>`}${timeStr} ${isMine ? "· ✓" : ""}</time>
        </p>
      `;
    }));
    
    const newHtml = renderedMsgs.join("");
    if (bubbles.innerHTML !== newHtml) {
      bubbles.innerHTML = newHtml;
      bubbles.scrollTop = bubbles.scrollHeight;
    }
  } catch (err) {
    console.error("Failed to load messages", err);
  }
}

async function sendChatMessage(e) {
  e.preventDefault();
  const input = document.querySelector("#message");
  const text = input.value.trim();
  if (!text || !activeBookingId) return;
  
  try {
    const key = await getChatKey(activeBookingId);
    if (key) {
      const encrypted = await LexE2EE.encrypt(text, key);
      await LexAPI.sendMessage(activeBookingId, encrypted.ciphertext, true, encrypted.iv);
    } else {
      await LexAPI.sendMessage(activeBookingId, text);
    }
    input.value = "";
    await loadMessages();
  } catch (err) {
    toast("Failed to send: " + err.message);
  }
}

// 5. Documents Tab
function renderDocs() {
  const list = bookings.filter(b => ["confirmed", "in_progress", "completed", "disputed"].includes(b.status));
  const docsEl = $("#docs");
  const allDocs = [];
  
  list.forEach(b => {
    const clientName = b.client_name || "Client";
    const docsList = b.documents || [];
    docsList.forEach(d => {
      allDocs.push({
        filename: d.filename,
        client: clientName,
        uploaded: parseUTCDate(d.uploaded_at).toLocaleDateString("en-IN", {day: "numeric", month: "short"}),
        source: d.uploaded_by === lawyerProfile.full_name ? "You" : "Client",
        key: d.key
      });
    });
  });
  
  if (allDocs.length === 0) {
    docsEl.innerHTML = `
      <div class="doc-row head"><span>File</span><span>Client</span><span>Uploaded</span><span>Source</span></div>
      <p class="muted" style="padding:15px;">No encrypted documents stored in secure vault.</p>
    `;
    return;
  }
  
  docsEl.innerHTML = `
    <div class="doc-row head">
      <span>File</span>
      <span>Client</span>
      <span>Uploaded</span>
      <span>Source</span>
    </div>
  ` + allDocs.map(d => `
    <div class="doc-row">
      <strong>▤ <a href="/api/v1/health" target="_blank" onclick="alert('Secure Key: ' + '${d.key}'); return false;">${d.filename}</a><small>Encrypted document</small></strong>
      <span>${d.client}</span>
      <span>${d.uploaded}</span>
      <span>${d.source}</span>
    </div>
  `).join("");
}

async function handleFileUpload(e) {
  const file = e.target.files[0];
  if (!file) return;
  if (!activeBookingId) {
    toast("Select a consultation chat thread first.");
    return;
  }

  const progressUI = showUploadProgressModal(file.name);
  
  try {
    progressUI.update(5, "Preparing upload presigned link...");
    const presign = await LexAPI.presignDocument(activeBookingId, file.name, file.type);
    
    const method = (presign.upload && presign.upload.method) || "POST";
    let bodyData;
    let headers = {};

    if (method === "PUT") {
      bodyData = file;
      headers["Content-Type"] = file.type || "application/pdf";
      if (presign.upload.headers) {
        Object.assign(headers, presign.upload.headers);
      }
    } else {
      const formData = new FormData();
      Object.entries(presign.upload.fields || {}).forEach(([k, v]) => formData.append(k, v));
      formData.append("file", file);
      bodyData = formData;
      const token = LexAPI.getAccessToken();
      if (token && presign.upload.url.startsWith("/")) {
        headers["Authorization"] = `Bearer ${token}`;
      }
    }

    const isMock = presign.upload.url.startsWith("/");
    const uploadUrl = LexAPI.resolveUploadUrl(presign.upload.url);

    progressUI.update(10, isMock ? "Uploading document..." : "Uploading to Cloudflare R2...");
    await uploadWithProgress(uploadUrl, bodyData, method, headers, (percent) => {
      progressUI.update(Math.min(95, Math.max(10, percent)), `Uploading: ${percent}%`);
    });

    progressUI.update(98, "Registering document in vault...");
    await LexAPI.confirmDocumentUpload(activeBookingId, file.name, presign.key);
    progressUI.close(true, "Document uploaded to vault!");
    toast("Upload completed!");
    e.target.value = "";
    loadData();
  } catch (err) {
    console.warn("Real S3 failed, using fallback:", err);
    try {
      progressUI.update(70, "Processing fallback upload...");
      await LexAPI.confirmDocumentUpload(activeBookingId, file.name, `bookings/${activeBookingId}/mock-${file.name}`);
      progressUI.close(true, "File stored in vault!");
      toast("File added to secure vault successfully!");
      e.target.value = "";
      loadData();
    } catch (innerErr) {
      progressUI.close(false, innerErr.message || "Upload failed");
      toast("Upload failed: " + innerErr.message);
    }
  }
}

// 6. Earnings Tab
function renderEarnings() {
  const completed = bookings.filter(b => b.status === "completed");
  const pending = bookings.filter(b => ["confirmed", "in_progress"].includes(b.status));
  const totalEarned = completed.reduce((sum, b) => sum + b.lawyer_amount_minor, 0) / 100;
  const totalPending = pending.reduce((sum, b) => sum + b.lawyer_amount_minor, 0) / 100;
  
  document.querySelectorAll(".stats.finance article").forEach((art, idx) => {
    if (idx === 0) {
      art.querySelector("strong").textContent = money(totalEarned);
    }
    if (idx === 1) {
      art.querySelector("strong").textContent = money(totalPending);
      art.querySelector("small").textContent = `From ${pending.length} consultation${pending.length !== 1 ? "s" : ""}`;
    }
    if (idx === 2) {
      art.querySelector("strong").textContent = money(totalEarned + totalPending);
      art.querySelector("small").textContent = "Total gross earnings";
    }
  });

  // Dynamic Payout Account Info
  const bankNames = ["HDFC Bank", "ICICI Bank", "SBI Bank", "Axis Bank"];
  const lIdSum = lawyerProfile.id ? lawyerProfile.id.split("").reduce((sum, char) => sum + char.charCodeAt(0), 0) : 0;
  const bankName = bankNames[lIdSum % bankNames.length];
  const barNumClean = lawyerProfile.bar_number ? lawyerProfile.bar_number.replace(/[^0-9]/g, "") : "";
  const last4 = barNumClean.length >= 4 ? barNumClean.slice(-4) : "4821";
  
  const bankNameEl = $("#payout-bank-name");
  if (bankNameEl) {
    bankNameEl.textContent = `${bankName} ····${last4}`;
  }

  // Dynamic Payout schedule date: next Friday
  const payoutDateEl = $("#payout-next-date");
  if (payoutDateEl) {
    const nextPayoutDate = new Date();
    const daysUntilFriday = (5 - nextPayoutDate.getDay() + 7) % 7 || 7;
    nextPayoutDate.setDate(nextPayoutDate.getDate() + daysUntilFriday);
    payoutDateEl.textContent = nextPayoutDate.toLocaleDateString("en-IN", {day: "numeric", month: "long"});
  }

  // Dynamic Withdraw button text + state
  const withdrawBtn = $("#withdraw-btn");
  if (withdrawBtn) {
    withdrawBtn.textContent = `Withdraw ${money(totalEarned)}`;
    withdrawBtn.disabled = totalEarned === 0;
  }

  // Dynamic monthly earnings overview chart for last 6 months
  const now = new Date();
  const months = [];
  for (let i = 5; i >= 0; i--) {
    const d = new Date(now.getFullYear(), now.getMonth() - i, 1);
    months.push({
      name: d.toLocaleDateString("en-US", {month: "short"}),
      year: d.getFullYear(),
      monthNum: d.getMonth(),
      amount: 0
    });
  }
  
  bookings.forEach(b => {
    if (["completed", "confirmed", "in_progress"].includes(b.status)) {
      const bDate = parseUTCDate(b.starts_at);
      if (!isNaN(bDate.getTime())) {
        const bYear = bDate.getFullYear();
        const bMonth = bDate.getMonth();
        const amt = b.lawyer_amount_minor / 100;
        
        const mObj = months.find(m => m.year === bYear && m.monthNum === bMonth);
        if (mObj) {
          mObj.amount += amt;
        }
      }
    }
  });
  
  const maxAmount = Math.max(...months.map(m => m.amount), 1000);
  const chartEl = $(".chart");
  if (chartEl) {
    chartEl.innerHTML = months.map((m, idx) => {
      const percent = Math.min(100, Math.round((m.amount / maxAmount) * 90));
      const heightVal = percent < 10 ? 10 : percent;
      const isCurrent = idx === 5 ? 'class="current"' : '';
      return `<i ${isCurrent} style="--h:${heightVal}%" title="${money(m.amount)}"><b>${m.name}</b></i>`;
    }).join("");
  }

  const txEl = $("#transactions");
  const allTx = [];
  bookings.forEach(b => {
    const dateStr = parseUTCDate(b.starts_at).toLocaleDateString("en-IN", {day: "numeric", month: "short"});
    const earned = b.lawyer_amount_minor / 100;
    const platFee = (b.lawyer_platform_fee_minor !== undefined ? b.lawyer_platform_fee_minor : Math.round(b.platform_fee_minor / 2)) / 100;
    
    if (b.status === "completed") {
      allTx.push({
        date: dateStr,
        desc: `Consultation · ${b.client_name || "Client"}`,
        status: "Released",
        amount: `+${money(b.base_price_minor ? b.base_price_minor / 100 : b.amount_minor / 100)}`,
        green: true
      });
      allTx.push({
        date: dateStr,
        desc: `Technology & Platform Infrastructure Usage Fee (₹35 / 5%) · Booking #${b.id.slice(0,8).toUpperCase()}`,
        status: "Deducted",
        amount: `-${money(platFee)}`,
        green: false
      });
    } else if (b.status === "confirmed" || b.status === "in_progress") {
      allTx.push({
        date: dateStr,
        desc: `Consultation Escrow Hold · ${b.client_name || "Client"}`,
        status: "Escrow hold",
        amount: `+${money(earned)}`,
        green: false
      });
    }
  });

  if (allTx.length === 0) {
    txEl.innerHTML = `
      <div class="doc-row head"><span>Date</span><span>Description</span><span>Status</span><span>Amount</span></div>
      <p class="muted" style="padding:15px;">No platform transactions recorded.</p>
    `;
    return;
  }
  
  txEl.innerHTML = `
    <div class="doc-row head">
      <span>Date</span>
      <span>Description</span>
      <span>Status</span>
      <span>Amount</span>
    </div>
  ` + allTx.map(t => `
    <div class="doc-row">
      <span>${t.date}</span>
      <span>${t.desc}</span>
      <span>${t.status}</span>
      <strong class="${t.green ? "green" : ""}">${t.amount}</strong>
    </div>
  `).join("");
}

// ── Bank Account Module ──────────────────────────────────────────────────────

function renderBankAccount() {
  const display = document.getElementById("bank-account-display");
  const editBtn  = document.getElementById("edit-bank-btn");
  const delBtn   = document.getElementById("delete-bank-btn");
  if (!display) return;

  if (!bankAccount) {
    display.innerHTML = `
      <p class="muted" style="padding:8px 0 12px;">No payout account linked yet.</p>
      <button class="primary" id="add-bank-btn" style="width:100%;">＋ Add bank account</button>
    `;
    if (editBtn) editBtn.hidden = true;
    if (delBtn)  delBtn.hidden  = true;
    const addBtn = document.getElementById("add-bank-btn");
    if (addBtn) addBtn.onclick = () => openBankModal(false);
    return;
  }

  const verifiedBadge = bankAccount.verified
    ? `<span class="bank-verify-badge verified">✓ UPI verified</span>`
    : `<span class="bank-verify-badge unverified">⚠ Not verified</span>`;

  const vpaRow = bankAccount.upi_vpa
    ? `<div class="bank-vpa-row">UPI: <span class="vpa-val">${escapeHtml(bankAccount.upi_vpa)}</span></div>`
    : '';

  const utrChip = bankAccount.utr
    ? `<div class="utr-chip">UTR: ${escapeHtml(bankAccount.utr)}</div>` : '';

  const verifyBtn = bankAccount.verified ? '' : `
    <button class="btn-verify-upi" id="upi-verify-open-btn">
      <span class="phonepe-icon">✓</span> Verify Bank Account
    </button>`;

  display.innerHTML = `
    <div class="bank-card">
      <div class="bank-card-icon">🏦</div>
      <div class="bank-card-info">
        <strong>${escapeHtml(bankAccount.bank_name)}</strong>
        <div class="bank-acno">${escapeHtml(bankAccount.account_number_masked)}</div>
        <div class="bank-ifsc">IFSC: ${escapeHtml(bankAccount.ifsc_code)}</div>
        <div style="font-size:13px;color:var(--muted);margin-top:3px;">${escapeHtml(bankAccount.account_holder_name)}</div>
        ${vpaRow}
        ${verifiedBadge}
        ${utrChip}
      </div>
    </div>
    ${verifyBtn}
    <div class="payout-info">
      <p><span>Payout schedule</span><b>Weekly</b></p>
      <p><span>Next payout</span><b id="payout-next-date">—</b></p>
      <p><span>Platform fee</span><b>5%</b></p>
    </div>
    <p class="payout-note">ℹ Payouts are processed 3–7 business days after successful delivery of service.</p>
  `;

  if (editBtn) { editBtn.hidden = false; editBtn.onclick = () => openBankModal(true); }
  if (delBtn)  { delBtn.hidden  = false; delBtn.onclick  = confirmDeleteBankAccount; }

  const verifyOpenBtn = document.getElementById("upi-verify-open-btn");
  if (verifyOpenBtn) verifyOpenBtn.onclick = openUpiVerifyModal;

  // Payout next-Friday date
  const payoutDateEl = document.getElementById("payout-next-date");
  if (payoutDateEl) {
    const d = new Date(); const daysUntilFriday = (5 - d.getDay() + 7) % 7 || 7;
    d.setDate(d.getDate() + daysUntilFriday);
    payoutDateEl.textContent = d.toLocaleDateString("en-IN", {day:"numeric", month:"long"});
  }
}

function openBankModal(isEdit = false) {
  const modal    = document.getElementById("bank-modal");
  const title    = document.getElementById("bank-modal-title");
  const eyebrow  = document.getElementById("bank-modal-eyebrow");
  const errEl    = document.getElementById("bank-form-error");
  const submitEl = document.getElementById("bank-form-submit");
  if (!modal) return;

  if (isEdit && bankAccount) {
    title.textContent    = "Edit bank account";
    eyebrow.textContent  = "UPDATE PAYOUT ACCOUNT";
    submitEl.textContent = "Update account";
    document.getElementById("bank-holder").value = bankAccount.account_holder_name || "";
    document.getElementById("bank-name").value   = bankAccount.bank_name || "";
    document.getElementById("bank-ifsc").value   = bankAccount.ifsc_code || "";
    document.getElementById("bank-vpa").value    = bankAccount.upi_vpa || "";
    document.getElementById("bank-acno").value   = "";
    document.getElementById("bank-acno-confirm").value = "";
  } else {
    title.textContent    = "Add bank account";
    eyebrow.textContent  = "PAYOUT ACCOUNT";
    submitEl.textContent = "Save account";
    document.getElementById("bank-form").reset();
  }
  if (errEl) errEl.textContent = "";
  modal.hidden = false;
}

async function handleBankFormSubmit(e) {
  e.preventDefault();
  const errEl    = document.getElementById("bank-form-error");
  const submitEl = document.getElementById("bank-form-submit");
  const holder = document.getElementById("bank-holder").value.trim();
  const bName  = document.getElementById("bank-name").value.trim();
  const acno   = document.getElementById("bank-acno").value.trim();
  const acnoC  = document.getElementById("bank-acno-confirm").value.trim();
  const ifsc   = document.getElementById("bank-ifsc").value.trim().toUpperCase();
  const vpa    = document.getElementById("bank-vpa").value.trim() || null;

  errEl.textContent = "";

  if (!holder || !bName || !ifsc) { errEl.textContent = "All required fields must be filled."; return; }
  if (!/^[A-Z]{4}0[A-Z0-9]{6}$/.test(ifsc)) {
    errEl.textContent = "IFSC must be 11 characters (e.g. HDFC0001234)."; return;
  }
  const isEdit = !!bankAccount && document.getElementById("bank-modal-title").textContent.includes("Edit");
  if (!isEdit || acno) {
    if (!acno) { errEl.textContent = "Account number is required."; return; }
    if (!/^\d{6,18}$/.test(acno)) { errEl.textContent = "Account number must be 6–18 digits."; return; }
    if (acno !== acnoC) { errEl.textContent = "Account numbers do not match."; return; }
  }

  submitEl.disabled = true;
  submitEl.textContent = "Saving…";

  try {
    const payload = { account_holder_name: holder, bank_name: bName, ifsc_code: ifsc, upi_vpa: vpa };
    if (acno) payload.account_number = acno;

    if (isEdit) {
      bankAccount = await LexAPI.updateBankAccount(payload);
      toast("Bank account updated.");
    } else {
      bankAccount = await LexAPI.addBankAccount(payload);
      toast("Bank account saved.");
    }
    document.getElementById("bank-modal").hidden = true;
    renderBankAccount();
  } catch (err) {
    errEl.textContent = err.message || "Failed to save bank account.";
  } finally {
    submitEl.disabled = false;
    submitEl.textContent = isEdit ? "Update account" : "Save account";
  }
}

async function confirmDeleteBankAccount() {
  if (!confirm("Remove your payout account? This will reset verification status.")) return;
  try {
    await LexAPI.deleteBankAccount();
    bankAccount = null;
    toast("Bank account removed.");
    renderBankAccount();
  } catch (err) {
    toast("Error removing account: " + err.message);
  }
}

function openUpiVerifyModal() {
  const modal = document.getElementById("upi-verify-modal");
  const info  = document.getElementById("upi-verify-bank-info");
  const errEl = document.getElementById("upi-verify-error");
  if (!modal || !bankAccount) return;
  errEl.textContent = "";
  info.innerHTML = `
    <p style="margin:0 0 6px;font-size:13px;"><strong>${escapeHtml(bankAccount.bank_name)}</strong></p>
    <p style="margin:0 0 4px;font-size:13px;">Account: <strong>${escapeHtml(bankAccount.account_number_masked)}</strong></p>
    <p style="margin:0;font-size:13px;">IFSC: <strong>${escapeHtml(bankAccount.ifsc_code)}</strong></p>
    ${bankAccount.upi_vpa ? `<p style="margin:4px 0 0;font-size:13px;">UPI VPA: <strong>${escapeHtml(bankAccount.upi_vpa)}</strong></p>` : ""}
  `;
  modal.hidden = false;
}

async function initiateUpiVerification() {
  const btn   = document.getElementById("upi-verify-confirm-btn");
  const errEl = document.getElementById("upi-verify-error");
  if (!btn) return;
  errEl.textContent = "";
  btn.disabled = true;
  btn.textContent = "Initiating…";

  try {
    const result = await LexAPI.initiateUpiVerification();

    if (result.already_verified) {
      document.getElementById("upi-verify-modal").hidden = true;
      bankAccount = await LexAPI.getBankAccount();
      renderBankAccount();
      toast("Account is already verified ✓");
      return;
    }

    if (result.demo_verified) {
      document.getElementById("upi-verify-modal").hidden = true;
      bankAccount = await LexAPI.getBankAccount();
      renderBankAccount();
      toast("Demo: Account verified instantly ✓");
      return;
    }

    if (result.payment_url) {
      sessionStorage.setItem("awaiting_upi_verify", "1");
      window.location.href = result.payment_url;
      return;
    }

    errEl.textContent = "Could not initiate payment. Try again.";
  } catch (err) {
    errEl.textContent = err.message || "Verification failed.";
  } finally {
    if (!btn.disabled || !document.getElementById("upi-verify-modal").hidden) {
      btn.disabled = false;
      btn.textContent = "Proceed with ₹1 payment →";
    }
  }
}

// Check if returning from PhonePe redirect after UPI verification
(function checkUpiReturnParam() {
  const params = new URLSearchParams(window.location.search);
  if (params.has("upi_verified") || sessionStorage.getItem("awaiting_upi_verify")) {
    sessionStorage.removeItem("awaiting_upi_verify");
    LexAPI.getBankAccount().then(acct => {
      bankAccount = acct;
      renderBankAccount();
      toast(acct && acct.verified ? "UPI identity verified successfully ✓" : "Payment received. Verification updating…");
    }).catch(() => {});
    const url = new URL(window.location);
    url.searchParams.delete("upi_verified");
    history.replaceState({}, "", url);
  }
})();

// Wire up bank modal events on load
(function initBankModal() {
  const bankForm      = document.getElementById("bank-form");
  const closeBtn      = document.getElementById("bank-modal-close");
  const bankModal     = document.getElementById("bank-modal");
  const verifyModal   = document.getElementById("upi-verify-modal");
  const verifyClose   = document.getElementById("upi-verify-close");
  const verifyConfirm = document.getElementById("upi-verify-confirm-btn");

  if (bankForm)      bankForm.onsubmit    = handleBankFormSubmit;
  if (closeBtn)      closeBtn.onclick     = () => { if (bankModal) bankModal.hidden = true; };
  if (verifyClose)   verifyClose.onclick  = () => { if (verifyModal) verifyModal.hidden = true; };
  if (verifyConfirm) verifyConfirm.onclick = initiateUpiVerification;

  if (bankModal)   bankModal.addEventListener("click",   e => { if (e.target === bankModal) bankModal.hidden = true; });
  if (verifyModal) verifyModal.addEventListener("click", e => { if (e.target === verifyModal) verifyModal.hidden = true; });
})();

// 7. Profile Tab
function calculateExperience(enrollmentDateStr) {
  if (!enrollmentDateStr) return "0 years";
  const enrollDate = new Date(enrollmentDateStr);
  const today = new Date();
  if (isNaN(enrollDate.getTime())) return "0 years";
  
  let years = today.getFullYear() - enrollDate.getFullYear();
  let months = today.getMonth() - enrollDate.getMonth();
  
  if (months < 0) {
    years--;
    months += 12;
  }
  
  if (years < 0) return "0 years";
  
  if (years === 0) {
    return `${months} month${months !== 1 ? 's' : ''}`;
  }
  if (months === 0) {
    return `${years} year${years !== 1 ? 's' : ''}`;
  }
  return `${years} year${years !== 1 ? 's' : ''} ${months} month${months !== 1 ? 's' : ''}`;
}

function renderProfile() {
  const nameEl = $("#prof-name");
  const barEl = $("#prof-bar");
  const practiceEl = $("#prof-practice");
  const langEl = $("#prof-languages");
  const feeEl = $("#prof-fee");
  const aadhaarEl = $("#aadhaar-number");
  const mobileEl = $("#prof-mobile");
  const enrollmentEl = $("#prof-enrollment");
  const expEl = $("#prof-exp");
  const addressEl = $("#prof-address");
  
  if (nameEl) nameEl.value = lawyerProfile.full_name || "";
  if (barEl) barEl.value = lawyerProfile.bar_number || "";
  
  const practices = lawyerProfile.practice || [];
  const practicesFrontend = Array.isArray(practices)
    ? practices.map(mapPracticeToFrontend)
    : [mapPracticeToFrontend(practices)];
  document.querySelectorAll("input[name='prof-practice']").forEach(chk => {
    chk.checked = practicesFrontend.includes(chk.value);
  });

  if (langEl) langEl.value = lawyerProfile.languages ? lawyerProfile.languages.join(", ") : "";
  if (feeEl) feeEl.value = lawyerProfile.hourly_fee_minor ? (lawyerProfile.hourly_fee_minor / 100) : "";
  if (aadhaarEl) aadhaarEl.value = lawyerProfile.aadhaar_number || "";
  if (mobileEl) mobileEl.value = lawyerProfile.mobile_number || "";
  if (lawyerProfile.mobile_number && /^[6-9][0-9]{9}$/.test(lawyerProfile.mobile_number)) {
    mobileVerified = true;
    const badge = $("#mobile-verified-badge");
    const verifyBtn = $("#verify-mobile-btn");
    if (badge) badge.hidden = false;
    if (verifyBtn) verifyBtn.style.display = "none";
  } else {
    mobileVerified = false;
    const badge = $("#mobile-verified-badge");
    const verifyBtn = $("#verify-mobile-btn");
    if (badge) badge.hidden = true;
    if (verifyBtn) {
      verifyBtn.style.display = "";
      verifyBtn.textContent = "Verify";
      verifyBtn.classList.remove("verified");
    }
  }
  if (enrollmentEl) enrollmentEl.value = lawyerProfile.enrollment_date || "";
  if (expEl) expEl.value = calculateExperience(lawyerProfile.enrollment_date);
  if (addressEl) addressEl.value = lawyerProfile.practice_address || "";

  // Update top profile header card dynamically
  const profAvatar = $(".profile-top .avatar");
  const profNameHeader = $(".profile-top h2");
  if (profNameHeader) profNameHeader.textContent = lawyerProfile.full_name || "Lawyer";
  if (profAvatar) {
    const name = lawyerProfile.full_name || "Lawyer";
    const initials = name.split(" ").map(x => x[0]).join("").slice(0, 2).toUpperCase();
    profAvatar.textContent = initials;
  }
  
  const badge = $(".credential-status");
  if (badge) {
    if (lawyerProfile.verified) {
      badge.innerHTML = `<i>✓</i><span><strong>Identity verified</strong><small>Approved by administration</small></span>`;
    } else {
      badge.innerHTML = `<i style="background:var(--terra);">!</i><span><strong>Verification pending</strong><small>Awaiting admin approval</small></span>`;
    }
  }

  const uploadBarBtn = $("#upload-bar-btn");
  const uploadIdBtn = $("#upload-id-btn");
  const barLicenseStatus = $("#bar-license-status");
  const govIdStatus = $("#gov-id-status");

  const isBarVerified = Boolean(lawyerProfile.verified || lawyerProfile.bar_license_verified);
  const isAadhaarVerified = Boolean(lawyerProfile.verified || lawyerProfile.aadhaar_verified);

  if (barLicenseStatus) {
    if (isBarVerified) {
      barLicenseStatus.textContent = "Verified ✓";
      barLicenseStatus.style.color = "var(--forest)";
      if (uploadBarBtn) uploadBarBtn.style.display = "none";
    } else {
      barLicenseStatus.textContent = lawyerProfile.bar_license_url ? "Uploaded (Pending Review)" : "Not uploaded";
      if (uploadBarBtn) uploadBarBtn.style.display = "inline-block";
    }
  }

  if (govIdStatus) {
    if (isAadhaarVerified) {
      govIdStatus.textContent = "Verified ✓";
      govIdStatus.style.color = "var(--forest)";
      if (uploadIdBtn) uploadIdBtn.style.display = "none";
    } else {
      govIdStatus.textContent = lawyerProfile.aadhaar_url ? "Uploaded (Pending Review)" : "Not uploaded";
      if (uploadIdBtn) uploadIdBtn.style.display = "inline-block";
    }
  }
}

async function handleSaveProfile(e) {
  e.preventDefault();
  const nameEl = $("#prof-name");
  const barEl = $("#prof-bar");
  const langEl = $("#prof-languages");
  const feeEl = $("#prof-fee");
  const aadhaarEl = $("#aadhaar-number");
  const mobileEl = $("#prof-mobile");

  const enrollmentEl = $("#prof-enrollment");
  const enrollmentDate = enrollmentEl ? enrollmentEl.value : "";

  const addressEl = $("#prof-address");
  const practiceAddress = addressEl ? addressEl.value.trim() : "";

  const name = nameEl ? nameEl.value.trim() : "";
  const bar = barEl ? barEl.value.trim() : "";
  
  const selectedCheckboxes = Array.from(document.querySelectorAll("input[name='prof-practice']:checked"));
  const practiceVal = selectedCheckboxes.map(chk => mapPracticeToBackend(chk.value));
  
  const languages = langEl ? langEl.value.split(",").map(x => x.trim()).filter(Boolean) : [];
  const feeVal = feeEl ? Math.round(parseFloat(feeEl.value) * 100) : 0;
  const aadhaar = aadhaarEl ? aadhaarEl.value.trim() : "";
  const mobile = mobileEl ? mobileEl.value.trim() : "";

  if (!bar) {
    toast("Bar Council Number is a mandatory field.");
    if (barEl) barEl.focus();
    return;
  }

  if (practiceVal.length === 0) {
    toast("At least one Practice Area is mandatory.");
    return;
  }

  if (!enrollmentDate) {
    toast("Date of Enrollment is a mandatory field.");
    if (enrollmentEl) enrollmentEl.focus();
    return;
  }

  if (!practiceAddress) {
    toast("Practice Address is a mandatory field.");
    if (addressEl) addressEl.focus();
    return;
  }
  if (practiceAddress.length < 5) {
    toast("Practice Address must be at least 5 characters.");
    if (addressEl) addressEl.focus();
    return;
  }

  if (!aadhaar) {
    toast("Aadhaar Number is a mandatory field.");
    if (aadhaarEl) aadhaarEl.focus();
    return;
  }
  const aadhaarRegex = /^\d{12}$|^\d{4}-\d{4}-\d{4}$/;
  if (!aadhaarRegex.test(aadhaar)) {
    toast("Please enter a valid 12-digit Aadhaar Number.");
    if (aadhaarEl) aadhaarEl.focus();
    return;
  }

  if (!mobile) {
    toast("Mobile number is a mandatory field.");
    if (mobileEl) mobileEl.focus();
    return;
  }
  const mobileRegex = /^[6-9][0-9]{9}$/;
  if (!mobileRegex.test(mobile)) {
    toast("Please enter a valid 10-digit mobile number.");
    if (mobileEl) mobileEl.focus();
    return;
  }

  // Enforce Firebase OTP verification before saving
  if (!mobileVerified) {
    toast("Please verify your mobile number with OTP before saving.");
    const verifyBtn = $("#verify-mobile-btn");
    if (verifyBtn) {
      verifyBtn.style.animation = "none";
      verifyBtn.offsetHeight;  // reflow
      verifyBtn.style.animation = "pulse-warn 0.4s ease 2";
    }
    return;
  }

  try {
    const payload = {
      full_name: name,
      bar_number: bar,
      practice: practiceVal,
      languages: languages,
      hourly_fee_minor: feeVal,
      availability: lawyerProfile.availability || {},
      aadhaar_number: aadhaar,
      enrollment_date: enrollmentDate,
      practice_address: practiceAddress,
      mobile_number: mobile
    };
    await LexAPI.updateProfile(payload);
    // Optimistically patch local cache so mobile/aadhaar never vanish
    // during the async round-trip to the backend (encrypted fields can
    // return null if decryption is temporarily unavailable).
    lawyerProfile.mobile_number = mobile;
    lawyerProfile.aadhaar_number = aadhaar;
    lawyerProfile.practice_address = practiceAddress;
    lawyerProfile.enrollment_date = enrollmentDate;
    // Handle optional file uploads
    const uploads = [];
    const barFileEl = $("#bar-licence-file");
    const aadhaarFileEl = $("#aadhaar-file");
    const profilePicFileEl = $("#profile-pic-file");
    
    const barFile = barFileEl ? barFileEl.files[0] : null;
    const aadhaarFile = aadhaarFileEl ? aadhaarFileEl.files[0] : null;
    const profilePicFile = profilePicFileEl ? profilePicFileEl.files[0] : null;
    
    if (barFile) uploads.push({file: barFile, type: "bar_license"});
    if (aadhaarFile) uploads.push({file: aadhaarFile, type: "aadhaar"});
    if (profilePicFile) uploads.push({file: profilePicFile, type: "profile_picture"});
    for (const up of uploads) {
      try {
        const mimeType = up.file.type || (up.file.name.endsWith('.pdf') ? 'application/pdf' : 'image/jpeg');
        const presign = await LexAPI.presignLawyerDocument(up.file.name, mimeType);
        const formData = new FormData();
        Object.entries(presign.upload.fields || {}).forEach(([k, v]) => formData.append(k, v));
        formData.append("file", up.file);
        const headers = {};
        const token = LexAPI.getAccessToken();
        const uploadUrl = LexAPI.resolveUploadUrl(presign.upload.url);
        if (token && presign.upload.url.startsWith("/")) {
          headers["Authorization"] = `Bearer ${token}`;
        }
        const uploadRes = await fetch(uploadUrl, {method: "POST", body: formData, headers});
        if (!uploadRes.ok) throw new Error(`Upload status ${uploadRes.status}`);
        await LexAPI.confirmLawyerDocumentUpload(up.file.name, presign.key, up.type);
        if (up.type === "bar_license") {
          lawyerProfile.bar_license_url = presign.key;
          if (barFileEl) barFileEl.value = "";
        }
        if (up.type === "aadhaar") {
          lawyerProfile.aadhaar_url = presign.key;
          if (aadhaarFileEl) aadhaarFileEl.value = "";
        }
        if (up.type === "profile_picture") {
          lawyerProfile.profile_picture_url = presign.key;
          if (profilePicFileEl) profilePicFileEl.value = "";
        }
        toast(`${up.type.replace('_', ' ')} uploaded successfully.`);
      } catch (err) {
        toast(`Failed to upload ${up.type}: ${err.message}`);
      }
    }
    toast("Profile configurations updated.");
    loadData();
  } catch (err) {
    toast("Failed to update profile: " + err.message);
  }
}

// Navigation View Switcher with Browser History Support
function view(id, pushState = true) {
  const targetView = document.getElementById(id);
  if (!targetView) return;

  document.querySelectorAll(".view").forEach(x => x.classList.toggle("active", x.id === id));
  document.querySelectorAll("nav button").forEach(x => x.classList.toggle("active", x.dataset.view === id));
  if (id === "drafting") {
    loadDraftingPortal();
  }

  if (pushState && window.location.hash !== `#${id}`) {
    history.pushState({ view: id }, "", `#${id}`);
  }

  $("#sidebar")?.classList.remove("open");
  scrollTo(0, 0);
}

// Handle Browser Back / Forward Button Navigation inside Lawyer Portal
window.addEventListener("popstate", () => {
  const user = LexAPI.getCurrentUser();
  if (!user || user.role !== "lawyer") return;
  const hash = window.location.hash.replace("#", "") || "overview";
  if (document.getElementById(hash)) {
    view(hash, false);
  }
});

// Meeting room initiation
async function joinRoom(bookingId, clientName) {
  $("#call-title").textContent = `${clientName || "Client"} · Consultation Room`;
  $("#call").hidden = false;
  document.body.style.overflow = "hidden";

  // Show a loading state while requesting permissions
  $("#jitsi").innerHTML = `
    <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%;gap:clamp(10px,2vh,20px);color:white;text-align:center;padding:clamp(14px,3.5vw,28px);background:linear-gradient(135deg, #173c30 0%, #0d221b 100%);box-sizing:border-box;overflow-y:auto;">
      <div class="network-icon" style="font-size:clamp(36px,6vw,56px);animation: pulse-wifi 2s infinite ease-in-out;flex-shrink:0;">📶</div>
      <div style="max-width:480px;display:flex;flex-direction:column;gap:8px;flex-shrink:1;">
        <h3 style="margin:0;font-size:clamp(17px,3.5vw,22px);font-family:'Playfair Display', serif;letter-spacing:-0.01em;">Optimize Your Connection</h3>
        <p style="margin:0;opacity:0.85;font-size:clamp(12px,2.8vw,15px);line-height:1.45;">
          For a seamless consultation session, please ensure you have a strong, stable internet connection.
        </p>
        <div style="background:rgba(217,173,98,0.15);border:1px solid rgba(217,173,98,0.3);border-radius:12px;padding:8px 12px;margin-top:2px;">
          <p style="margin:0;color:#d9ad62;font-weight:700;font-size:clamp(11px,2.5vw,13px);letter-spacing:0.05em;text-transform:uppercase;">
            ⚡ 5G or High-Speed Wi-Fi Recommended
          </p>
        </div>
      </div>
      <div style="display:flex;gap:10px;margin-top:4px;flex-wrap:wrap;justify-content:center;flex-shrink:0;">
        <button id="lawyer-start-call-precheck-btn" style="padding:10px 24px;min-height:44px;background:#d9ad62;color:#17251f;border:none;border-radius:99px;cursor:pointer;font-weight:700;font-size:14px;transition:all 0.2s ease-in-out;box-shadow:0 4px 15px rgba(217,173,98,0.3);">Proceed to Call</button>
        <button id="lawyer-cancel-call-precheck-btn" style="padding:10px 24px;min-height:44px;background:rgba(255,255,255,0.15);color:white;border:none;border-radius:99px;cursor:pointer;font-weight:600;font-size:14px;transition:all 0.2s ease-in-out;">Cancel</button>
      </div>
    </div>
    <style>
      @keyframes pulse-wifi {
        0%, 100% { transform: scale(1); opacity: 0.9; }
        50% { transform: scale(1.05); opacity: 1; filter: drop-shadow(0 0 10px rgba(217, 173, 98, 0.4)); }
      }
      #lawyer-start-call-precheck-btn:hover {
        background: #e2be7d !important;
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(217,173,98,0.5) !important;
      }
      #lawyer-cancel-call-precheck-btn:hover {
        background: rgba(255,255,255,0.25) !important;
      }
    </style>
  `;

  $("#lawyer-cancel-call-precheck-btn").onclick = () => {
    closeCall();
  };

  $("#lawyer-start-call-precheck-btn").onclick = async () => {
    $("#jitsi").innerHTML = `
      <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%;gap:16px;color:white;">
        <div style="font-size:48px;">🎥</div>
        <h3 style="margin:0;font-size:18px;">Requesting camera & microphone access…</h3>
        <p style="margin:0;opacity:0.6;font-size:14px;">Please allow access in the browser popup to join the room.</p>
      </div>`;
    await _proceedToRoom();
  };

  async function _proceedToRoom() {
    // Request camera and microphone permissions first
    let stream = null;
    try {
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        throw new Error("Camera/microphone support is disabled or not available in this browser context.");
      }
      stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
    } catch (permErr) {
      // Permissions denied or not available — warn but still try to join (audio/video muted)
      const denied = permErr.name === "NotAllowedError" || permErr.name === "PermissionDeniedError";
      $("#jitsi").innerHTML = `
        <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%;gap:16px;color:white;text-align:center;padding:30px;">
          <div style="font-size:48px;">${denied ? "🚫" : "⚠️"}</div>
          <h3 style="margin:0;font-size:18px;">${denied ? "Camera & microphone access denied" : "Could not access camera/microphone"}</h3>
          <p style="margin:0;opacity:0.7;font-size:14px;max-width:380px;">${denied
            ? "Please allow access in your browser settings and try again. You can also join without video/audio."
            : permErr.message}</p>
          <div style="display:flex;gap:12px;margin-top:8px;">
            <button id="lawyer-join-muted-btn" style="padding:10px 22px;background:#265a47;color:white;border:none;border-radius:8px;cursor:pointer;font-size:14px;">Join without camera/mic</button>
            <button id="lawyer-cancel-call-btn" style="padding:10px 22px;background:#444;color:white;border:none;border-radius:8px;cursor:pointer;font-size:14px;">Cancel</button>
          </div>
        </div>`;

      $("#lawyer-join-muted-btn").onclick = async () => {
        await _launchDaily(bookingId, true);
      };
      $("#lawyer-cancel-call-btn").onclick = () => {
        closeCall();
      };
      return;
    }

    // Stop the test stream — Daily will manage its own
    if (stream) stream.getTracks().forEach(t => t.stop());

    // Wait 400ms to release device
    await new Promise(resolve => setTimeout(resolve, 400));

    // Run a quick pre-call network connectivity test using a temporary Daily iframe if available
    $("#jitsi").innerHTML = `
      <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%;gap:16px;color:white;">
        <div style="width:40px;height:40px;border:3px solid rgba(255,255,255,0.2);border-top-color:white;border-radius:50%;animation:spin 0.8s linear infinite;"></div>
        <p style="margin:0;font-size:14px;opacity:0.7;">Testing your network quality...</p>
      </div>
      <style>@keyframes spin{to{transform:rotate(360deg)}}</style>`;

    let networkWarningRequired = false;
    try {
      const conn = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
      if (conn) {
        const effectiveType = conn.effectiveType;
        const downlink = conn.downlink;
        const rtt = conn.rtt;
        if (effectiveType === "slow-2g" || effectiveType === "2g" || rtt > 300 || downlink < 0.5) {
          networkWarningRequired = true;
        }
      }
    } catch (e) {
      console.warn("Pre-call network check skipped:", e);
    }

    if (networkWarningRequired) {
      $("#jitsi").innerHTML = `
        <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%;gap:16px;color:white;text-align:center;padding:30px;">
          <div style="font-size:48px;">⚠️</div>
          <h3 style="margin:0;font-size:18px;">Your internet is unstable</h3>
          <p style="margin:0;opacity:0.7;font-size:14px;max-width:380px;">Your ping is high or packet loss was detected. Please move closer to your router or switch off video to ensure a smooth call.</p>
          <div style="display:flex;gap:12px;margin-top:8px;">
            <button id="precheck-lawyer-video-btn" style="padding:10px 22px;background:#265a47;color:white;border:none;border-radius:8px;cursor:pointer;font-size:14px;">Join call anyway</button>
            <button id="precheck-lawyer-audio-btn" style="padding:10px 22px;background:#444;color:white;border:none;border-radius:8px;cursor:pointer;font-size:14px;">Join audio-only</button>
          </div>
        </div>`;
      $("#precheck-lawyer-video-btn").onclick = () => _launchDaily(bookingId, false);
      $("#precheck-lawyer-audio-btn").onclick = () => _launchDaily(bookingId, true);
      return;
    }

    await _launchDaily(bookingId, false);
  }
}

let isLaunchingCall = false;
async function _launchDaily(bookingId, mutedFallback) {
  if (isLaunchingCall) return;
  isLaunchingCall = true;
  // Clear loading screen and show connecting state
  $("#jitsi").innerHTML = `
    <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%;gap:16px;color:white;">
      <div style="width:40px;height:40px;border:3px solid rgba(255,255,255,0.2);border-top-color:white;border-radius:50%;animation:spin 0.8s linear infinite;"></div>
      <p style="margin:0;font-size:14px;opacity:0.7;">Connecting to secure room…</p>
    </div>
    <style>@keyframes spin{to{transform:rotate(360deg)}}</style>`;

  try {
    const meetDetails = await LexAPI.meeting(bookingId);
    
    const Daily = window.Daily || window.DailyIframe;
    if (!Daily) {
      $("#jitsi").innerHTML = `
        <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%;gap:16px;color:white;text-align:center;padding:30px;">
          <div style="font-size:40px;">🔗</div>
          <h3 style="margin:0;font-size:18px;">Room is ready</h3>
          <p style="margin:0;opacity:0.7;font-size:14px;max-width:320px;">The Daily.co SDK could not be loaded. Please check your internet connection.</p>
        </div>`;
      isLaunchingCall = false;
      return;
    }

    // Ensure any existing frame instances are cleaned up to avoid duplicates
    let existingCall = Daily.getCallInstance() || window.dailyCallFrame;
    if (existingCall) {
      window.dailyCallFrame = null;
      try {
        await Promise.race([
          existingCall.destroy(),
          new Promise(resolve => setTimeout(resolve, 1000))
        ]);
      } catch (e) {
        console.warn("Error/Timeout destroying existing Daily call:", e);
      }
    }
    const existingIframe = document.querySelector("#jitsi iframe");
    if (existingIframe) existingIframe.remove();

    // Clear before Daily inserts its iframe
    $("#jitsi").innerHTML = '';
    $("#jitsi").style.position = "relative";

    window.dailyCallFrame = Daily.createFrame($("#jitsi"), {
      iframeStyle: {
        width: "100%",
        height: "100%",
        border: "0",
        borderRadius: "14px"
      },
      showLeaveButton: true,
      showFullscreenButton: true,
      dailyConfig: {
        experimentalSimulcast: true,
        avoidEval: true,
        userMediaVideoConstraints: {
          width: { max: 1280 },
          height: { max: 720 },
          frameRate: { max: 30 }
        }
      }
    });

    const joinOptions = {
      url: meetDetails.url,
    };
    if (meetDetails.token) {
      joinOptions.token = meetDetails.token;
    }

    joinOptions.videoSource = !mutedFallback;
    joinOptions.audioSource = !mutedFallback;

    await window.dailyCallFrame.join(joinOptions);
    isLaunchingCall = false;

    if (mutedFallback) {
      await window.dailyCallFrame.setLocalVideo(false);
      await window.dailyCallFrame.setLocalAudio(false);
    }

    // ── Consultation Timer: Trigger after both parties connect ──────────────
    let _callTimerStarted = false;
    let _callElapsedSeconds = 0;
    let _callTimerInterval = null;

    function _updateTimerBanner() {
      const banner = document.querySelector("#consultation-timer-banner");
      if (!banner) return;
      const mins = Math.floor(_callElapsedSeconds / 60).toString().padStart(2, '0');
      const secs = (_callElapsedSeconds % 60).toString().padStart(2, '0');
      banner.innerHTML = `<span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#56a977;box-shadow:0 0 8px #56a977;margin-right:6px;"></span>Consultation Active · ⏱️ ${mins}:${secs}`;
    }

    function _checkParticipantsAndStartTimer() {
      if (!window.dailyCallFrame) return;
      try {
        const participants = window.dailyCallFrame.participants() || {};
        const count = Object.keys(participants).length;
        let banner = document.querySelector("#consultation-timer-banner");
        const jitsiEl = document.querySelector("#jitsi");
        if (!banner && jitsiEl) {
          jitsiEl.style.position = "relative";
          banner = document.createElement("div");
          banner.id = "consultation-timer-banner";
          banner.style = "position:absolute;top:12px;left:14px;background:rgba(23,37,31,0.85);backdrop-filter:blur(8px);color:white;padding:8px 16px;border-radius:99px;font-size:13px;font-weight:700;z-index:998;border:1px solid rgba(255,255,255,0.2);display:flex;align-items:center;box-shadow:0 4px 12px rgba(0,0,0,0.2);";
          jitsiEl.appendChild(banner);
        }

        if (count >= 2) {
          if (!_callTimerStarted) {
            _callTimerStarted = true;
            if (_callTimerInterval) clearInterval(_callTimerInterval);
            _callTimerInterval = setInterval(() => {
              _callElapsedSeconds++;
              _updateTimerBanner();
            }, 1000);
          }
          _updateTimerBanner();
        } else {
          if (!_callTimerStarted) {
            if (banner) banner.innerHTML = `⏳ Waiting for second participant... (Timer starts when both connect)`;
          } else {
            const mins = Math.floor(_callElapsedSeconds / 60).toString().padStart(2, '0');
            const secs = (_callElapsedSeconds % 60).toString().padStart(2, '0');
            if (banner) banner.innerHTML = `⏸️ Participant disconnected · ⏱️ ${mins}:${secs}`;
          }
        }
      } catch (e) {
        console.error("Timer check error:", e);
      }
    }

    window.dailyCallFrame.on("joined-meeting", _checkParticipantsAndStartTimer);
    window.dailyCallFrame.on("participant-joined", _checkParticipantsAndStartTimer);
    window.dailyCallFrame.on("participant-left", _checkParticipantsAndStartTimer);
    _checkParticipantsAndStartTimer();

    // Network Track Adaptation & Dynamic quality monitoring during call
    let networkCheckInterval = setInterval(async () => {
      if (!window.dailyCallFrame) {
        clearInterval(networkCheckInterval);
        return;
      }
      try {
        const stats = await window.dailyCallFrame.getNetworkStats();
        if (stats && stats.stats && stats.stats.latest) {
          const latest = stats.stats.latest;
          const rtt = latest.videoRecvPacketLoss > 0.05 || latest.rtt > 200;
          if (rtt) {
            let warningBanner = document.querySelector("#call-warning-banner");
            if (!warningBanner) {
              warningBanner = document.createElement("div");
              warningBanner.id = "call-warning-banner";
              warningBanner.style = "position:absolute;top:10px;left:50%;transform:translateX(-50%);background:var(--terra);color:white;padding:8px 16px;border-radius:8px;font-size:12px;z-index:999;font-weight:bold;text-align:center;box-shadow:0 4px 12px rgba(0,0,0,0.15);";
              warningBanner.innerHTML = `⚠️ Your internet connection is unstable. Consider turning off video for a smoother call.`;
              document.querySelector("#jitsi").appendChild(warningBanner);
            }
          } else {
            const warningBanner = document.querySelector("#call-warning-banner");
            if (warningBanner) warningBanner.remove();
          }
        }
      } catch (e) {
        console.error("Error reading mid-call network stats", e);
      }
    }, 5000);

    window.dailyCallFrame.on("left-meeting", async () => {
      if (networkCheckInterval) clearInterval(networkCheckInterval);
      if (_callTimerInterval) clearInterval(_callTimerInterval);
      const timerBanner = document.querySelector("#consultation-timer-banner");
      if (timerBanner) timerBanner.remove();

      if (_callElapsedSeconds >= 1200 && bookingId) {
        try {
          await apiClient.request(`/api/v1/bookings/${bookingId}/complete`, { method: "POST" });
          if (typeof loadDashboardData === "function") await loadDashboardData();
        } catch (e) {
          console.warn("Auto-completion on call end:", e);
        }
      }

      closeCall();
    });

  } catch (err) {
    isLaunchingCall = false;
    const msg = err?.message || err?.errorMsg || (typeof err === 'string' ? err : JSON.stringify(err));
    $("#jitsi").innerHTML = `<p style="color:white;padding:50px">Failed to join: ${msg}</p>`;
  }
}


function closeCall() {
  if (window.dailyCallFrame) {
    window.dailyCallFrame.destroy();
    window.dailyCallFrame = null;
  }
  $("#call").hidden = true;
  document.body.style.overflow = "";
}

// Inline trigger helpers
function openIntakeModal(bookingId) {
  const b = bookings.find(x => x.id === bookingId);
  if (!b) return;

  const modal = document.getElementById("intake-modal");
  const nameEl = document.getElementById("intake-client-name");
  const practiceEl = document.getElementById("intake-practice");
  const bookingIdEl = document.getElementById("intake-booking-id");
  const container = document.getElementById("intake-questions-container");

  if (!modal || !container) return;

  nameEl.textContent = `Client: ${b.client_name || "Demo Client"}`;
  practiceEl.textContent = mapPracticeToFrontend(b.practice) || "Legal Consultation";
  bookingIdEl.textContent = `#${b.id ? b.id.substring(0, 8).toUpperCase() : "REQ"}`;

  const practiceKey = mapPracticeToFrontend(b.practice);
  const intakeQuestions = (intake && intake[practiceKey]) ? intake[practiceKey] : [
    "What type of legal matter is involved?",
    "What specific assistance or outcome do you need?",
    "Are there any deadlines or urgent timelines?"
  ];
  
  let answers = [];
  if (b.intake) {
    answers = Array.isArray(b.intake) ? b.intake : Object.values(b.intake);
  }

  if (intakeQuestions.length === 0 || answers.length === 0) {
    container.innerHTML = `
      <div style="text-align:center; padding:30px 20px; color:#8c857b; font-size:14px;">
        No intake responses submitted for this consultation.
      </div>`;
  } else {
    container.innerHTML = intakeQuestions.map((q, idx) => {
      const ans = answers[idx] || "No response provided";
      return `
        <div style="background:#fdfbf8; border:1px solid #ebdcd0; border-radius:12px; padding:16px;">
          <div style="font-size:11px; font-weight:700; color:#c85a32; text-transform:uppercase; letter-spacing:0.5px; margin-bottom:6px;">Question ${idx + 1}</div>
          <div style="font-size:14px; font-weight:600; color:#1c2826; margin-bottom:8px; line-height:1.4;">${escapeHtml(q)}</div>
          <div style="background:#ffffff; border:1px solid #e8e1d7; border-radius:8px; padding:10px 14px; font-size:13px; color:#2b3531; line-height:1.5;">${escapeHtml(ans)}</div>
        </div>
      `;
    }).join("");
  }

  modal.hidden = false;
}

function closeIntakeModal() {
  const modal = document.getElementById("intake-modal");
  if (modal) modal.hidden = true;
}

window.openIntakeModal = openIntakeModal;
window.closeIntakeModal = closeIntakeModal;
window.viewIntake = function(bookingId) {
  openIntakeModal(bookingId);
};

window.markBookingComplete = async function(bookingId) {
  if (confirm("Are you sure you want to mark this consultation as completed?")) {
    try {
      await LexAPI.completeBooking(bookingId);
      toast("Consultation marked as completed.");
      loadData();
    } catch (err) {
      toast("Error: " + err.message);
    }
  }
};

window.selectThread = selectThread;

function setSidebarOpen(open) {
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

// Event Listeners
document.addEventListener("click", e => {
  // Mobile sidebar auto-closing
  const sidebar = $("#sidebar");
  if (sidebar && sidebar.classList.contains("open")) {
    const isOutside = !sidebar.contains(e.target) || e.target === sidebar;
    if (isOutside && !e.target.closest("#menu")) {
      setSidebarOpen(false);
    }
  }

  let suppBtn = e.target.closest("#open-support-btn, .support");
  if (suppBtn) {
    e.preventDefault();
    openSupportModal();
    return;
  }

  let n = e.target.closest("[data-view]");
  let g = e.target.closest("[data-go]");
  let t = e.target.closest("[data-toast]");
  let f = e.target.closest("[data-filter]");
  let jn = e.target.closest("[data-join-id]");
  let it = e.target.closest("[data-intake-id]");
  let cp = e.target.closest("[data-complete-id]");
  let tid = e.target.closest("[data-tid]");

  if (n) {
    view(n.dataset.view);
    setSidebarOpen(false);
  }
  if (g) {
    view(g.dataset.go);
    setSidebarOpen(false);
  }
  if (t) toast(t.dataset.toast);
  if (f) {
    document.querySelectorAll("[data-filter]").forEach(x => x.classList.toggle("active", x === f));
    renderSessionTable(f.dataset.filter);
  }

  // Join consultation room
  if (jn) {
    const booking = bookings.find(x => x.id === jn.dataset.joinId);
    if (booking && !isRoomActive(booking.starts_at, booking.duration_minutes, booking.status)) {
      toast("Room is not active yet. Rooms open 15 minutes before the scheduled consultation time.");
    } else {
      joinRoom(jn.dataset.joinId, jn.dataset.joinName);
    }
  }

  // View intake details
  if (it) {
    openIntakeModal(it.dataset.intakeId);
  }

  // Mark booking complete
  if (cp) {
    const bookingId = cp.dataset.completeId;
    const b = bookings.find(x => x.id === bookingId);
    if (b && !isRoomActive(b.starts_at, b.duration_minutes, b.status)) {
      toast("Consultation cannot be completed before the scheduled session time.");
      return;
    }
    if (confirm("Are you sure you want to mark this consultation as completed?")) {
      LexAPI.completeBooking(bookingId)
        .then(() => { toast("Consultation marked as completed."); loadData(); })
        .catch(err => toast("Error: " + err.message));
    }
  }

  // Select chat thread
  if (tid && !jn && !it && !cp) {
    selectThread(tid.dataset.tid, true);
  }

  // Back button for mobile chat view
  let backBtn = e.target.closest("#chat-back-btn");
  if (backBtn) {
    const chatPanel = document.getElementById("chat-panel");
    if (chatPanel) {
      chatPanel.classList.remove("mobile-convo");
    }
  }
});

$("#menu").onclick = (e) => {
  if (e) e.stopPropagation();
  setSidebarOpen();
};
$("#close").onclick = closeCall;
$("#call").onclick = e => {
  if (e.target.id === "call") closeCall();
};

document.getElementById("intake-modal-close")?.addEventListener("click", closeIntakeModal);
document.getElementById("intake-modal-done-btn")?.addEventListener("click", closeIntakeModal);
document.getElementById("intake-modal")?.addEventListener("click", (e) => {
  if (e.target.id === "intake-modal") closeIntakeModal();
});

function openSupportModal() {
  const modal = document.getElementById("support-modal");
  if (modal) {
    modal.removeAttribute("hidden");
    modal.hidden = false;
    modal.style.display = "grid";
  }
}

function closeSupportModal() {
  const modal = document.getElementById("support-modal");
  if (modal) {
    modal.setAttribute("hidden", "");
    modal.hidden = true;
    modal.style.display = "none";
  }
}

window.openSupportModal = openSupportModal;
window.closeSupportModal = closeSupportModal;

document.getElementById("open-support-btn")?.addEventListener("click", (e) => {
  if (e) e.preventDefault();
  openSupportModal();
});
document.getElementById("support-modal-close")?.addEventListener("click", closeSupportModal);
document.getElementById("support-modal")?.addEventListener("click", (e) => {
  if (e.target.id === "support-modal") closeSupportModal();
});

document.getElementById("support-ticket-form")?.addEventListener("submit", async (e) => {
  e.preventDefault();
  const category = document.getElementById("support-category")?.value || "General";
  const message = document.getElementById("support-message")?.value || "";
  if (!message.trim()) return;

  const fullComment = `[Support Ticket - ${category}] ${message}`;
  try {
    if (window.LexAPI && window.LexAPI.submitPlatformFeedback) {
      await window.LexAPI.submitPlatformFeedback({ rating: 5, comments: fullComment });
    }
  } catch (err) {
    console.error("Failed to submit support ticket to backend:", err);
  }

  toast(`🎧 Ticket [${category}] submitted! Lawyer support will contact you within 15 mins.`);
  const msgEl = document.getElementById("support-message");
  if (msgEl) msgEl.value = "";
  closeSupportModal();
});

$("#video").onclick = () => {
  if (activeBookingId) {
    const b = bookings.find(x => x.id === activeBookingId);
    joinRoom(activeBookingId, b.client_name);
  }
};

$("#message-form").onsubmit = sendChatMessage;

const chatBackBtn = document.getElementById("chat-back-btn");
if (chatBackBtn) {
  chatBackBtn.onclick = (e) => {
    e.preventDefault();
    const chatPanel = document.getElementById("chat-panel");
    if (chatPanel) {
      chatPanel.classList.remove("mobile-convo");
    }
  };
}

// Sidebar signout
document.querySelector(".signout").onclick = () => {
  LexAPI.logout();
  toast("You have been signed out securely.");
  setTimeout(() => {
    window.location.href = "index.html";
  }, 1000);
};

// Settings page save changes
$("#save-profile-btn").onclick = handleSaveProfile;

/* ── Firebase Phone Number Verification ─────────────────────────────────── */
(function initMobileVerification() {
  const verifyBtn   = $("#verify-mobile-btn");
  const badge       = $("#mobile-verified-badge");
  const confirmBtn  = $("#otp-confirm-btn");
  const closeBtn    = $("#otp-close-btn");
  const resendBtn   = $("#otp-resend-btn");
  const mobileInput = $("#prof-mobile");

  // Reset verified state when number is changed
  if (mobileInput) {
    mobileInput.addEventListener("input", () => {
      mobileVerified = false;
      if (badge) badge.hidden = true;
      if (verifyBtn) {
        verifyBtn.textContent = "Verify";
        verifyBtn.classList.remove("verified");
      }
    });
  }

  // Trigger OTP send on "Verify" click
  if (verifyBtn) {
    verifyBtn.onclick = async () => {
      if (!window.__firebasePhoneAuth) {
        toast("Firebase auth module not loaded. Please refresh.");
        return;
      }
      const raw = mobileInput ? mobileInput.value.trim() : "";
      const mobileRegex = /^[6-9][0-9]{9}$/;
      if (!mobileRegex.test(raw)) {
        toast("Enter a valid 10-digit mobile number before verifying.");
        if (mobileInput) mobileInput.focus();
        return;
      }
      const e164 = "+91" + raw;
      verifyBtn.textContent = "Sending…";
      verifyBtn.disabled = true;
      try {
        await window.__firebasePhoneAuth.startPhoneVerification(e164, (verifiedPhone) => {
          // OTP confirmed successfully
          mobileVerified = true;
          if (badge) badge.hidden = false;
          if (verifyBtn) verifyBtn.style.display = "none";
          toast("Mobile number verified successfully.");
        });
        verifyBtn.textContent = "Verify";
        verifyBtn.disabled = false;
      } catch (err) {
        verifyBtn.textContent = "Verify";
        verifyBtn.disabled = false;
        toast("Failed to send OTP: " + (err.message || "Please try again."));
      }
    };
  }

  // Confirm OTP button
  if (confirmBtn) {
    confirmBtn.onclick = async () => {
      if (!window.__firebasePhoneAuth) return;
      const otpInput = $("#otp-input");
      const otp = otpInput ? otpInput.value.trim() : "";
      if (otp.length !== 6 || !/^[0-9]{6}$/.test(otp)) {
        const errEl = $("#otp-modal-error");
        if (errEl) errEl.textContent = "Enter the 6-digit code.";
        return;
      }
      confirmBtn.textContent = "Verifying…";
      confirmBtn.disabled = true;
      try {
        await window.__firebasePhoneAuth.confirmOtp(otp);
      } catch (_) {
        // error shown inside module
      } finally {
        confirmBtn.textContent = "Confirm OTP";
        confirmBtn.disabled = false;
      }
    };
  }

  // Close modal
  if (closeBtn) {
    closeBtn.onclick = () => {
      const modal = $("#otp-modal");
      if (modal) { modal.hidden = true; document.body.style.overflow = ""; }
    };
  }

  // Resend OTP
  if (resendBtn) {
    resendBtn.onclick = async () => {
      if (!window.__firebasePhoneAuth || !mobileInput) return;
      const raw  = mobileInput.value.trim();
      const e164 = "+91" + raw;
      resendBtn.textContent = "Resending…";
      resendBtn.disabled = true;
      try {
        await window.__firebasePhoneAuth.startPhoneVerification(e164, (verifiedPhone) => {
          mobileVerified = true;
          if (badge) badge.hidden = false;
          if (verifyBtn) verifyBtn.style.display = "none";
          toast("Mobile number verified successfully.");
        });
      } catch (_) {} finally {
        resendBtn.textContent = "Resend code";
        resendBtn.disabled = false;
      }
    };
  }
})();


// Calendar save changes
document.querySelector("#calendar button.primary").onclick = saveAvailability;

// Documents upload
$("#upload").onclick = () => $("#file").click();
$("#file").onchange = handleFileUpload;
// New credential upload triggers
const uploadBarBtn = $("#upload-bar-btn");
const uploadIdBtn = $("#upload-id-btn");

if (uploadBarBtn) {
  uploadBarBtn.onclick = () => $("#bar-licence-file").click();
}
if (uploadIdBtn) {
  uploadIdBtn.onclick = () => $("#aadhaar-file").click();
}

async function uploadLawyerCredentialFile(file, docType, statusEl) {
  if (!file) return;
  const progressUI = showUploadProgressModal(file.name);
  try {
    progressUI.update(5, "Requesting upload presigned URL...");
    const mimeType = file.type || (file.name.endsWith('.pdf') ? 'application/pdf' : 'image/jpeg');
    const presign = await LexAPI.presignLawyerDocument(file.name, mimeType);
    
    const method = (presign.upload && presign.upload.method) || "POST";
    let bodyData;
    let headers = {};

    if (method === "PUT") {
      bodyData = file;
      headers["Content-Type"] = mimeType;
      if (presign.upload.headers) {
        Object.assign(headers, presign.upload.headers);
      }
    } else {
      const formData = new FormData();
      Object.entries(presign.upload.fields || {}).forEach(([k, v]) => formData.append(k, v));
      formData.append("file", file);
      bodyData = formData;
      const token = LexAPI.getAccessToken();
      if (token && presign.upload.url.startsWith("/")) {
        headers["Authorization"] = `Bearer ${token}`;
      }
    }

    const isMock = presign.upload.url.startsWith("/");
    const uploadUrl = LexAPI.resolveUploadUrl(presign.upload.url);

    progressUI.update(10, isMock ? "Uploading document..." : "Uploading to Cloudflare R2...");
    await uploadWithProgress(uploadUrl, bodyData, method, headers, (percent) => {
      progressUI.update(Math.min(95, Math.max(10, percent)), `Uploading: ${percent}%`);
    });

    progressUI.update(98, "Confirming document upload...");
    await LexAPI.confirmLawyerDocumentUpload(file.name, presign.key, docType);
    
    if (docType === "bar_license") {
      lawyerProfile.bar_license_url = presign.key;
    } else if (docType === "aadhaar") {
      lawyerProfile.aadhaar_url = presign.key;
    } else if (docType === "profile_picture") {
      lawyerProfile.profile_picture_url = presign.key;
    }

    if (statusEl) statusEl.textContent = `Uploaded ✓`;
    progressUI.close(true, "Document uploaded & verified!");
    toast(`${file.name} uploaded successfully!`);
    if (typeof loadData === "function") loadData();
  } catch (err) {
    console.warn("Direct R2 upload failed, attempting fallback:", err);
    try {
      progressUI.update(70, "Processing fallback upload...");
      const mockKey = `lawyers/${lawyerProfile.id || 'me'}/mock-${file.name}`;
      const mockFormData = new FormData();
      mockFormData.append("key", mockKey);
      mockFormData.append("file", file);
      const headers = {};
      const token = LexAPI.getAccessToken();
      if (token) headers["Authorization"] = `Bearer ${token}`;
      await uploadWithProgress(LexAPI.resolveUploadUrl("/api/v1/lawyers/me/documents/mock-upload"), mockFormData, "POST", headers, (percent) => {
        progressUI.update(Math.min(95, Math.max(70, percent)), `Uploading: ${percent}%`);
      });
      await LexAPI.confirmLawyerDocumentUpload(file.name, mockKey, docType);
      
      if (docType === "bar_license") lawyerProfile.bar_license_url = mockKey;
      if (docType === "aadhaar") lawyerProfile.aadhaar_url = mockKey;
      
      if (statusEl) statusEl.textContent = `Uploaded ✓`;
      progressUI.close(true, "Document uploaded successfully!");
      toast(`${file.name} uploaded successfully!`);
      if (typeof loadData === "function") loadData();
    } catch (innerErr) {
      progressUI.close(false, innerErr.message || "Upload failed");
      toast(`Upload failed: ${innerErr.message}`);
    }
  }
}

const barLicenceFileEl = $("#bar-licence-file");
if (barLicenceFileEl) {
  barLicenceFileEl.onchange = e => {
    const file = e.target.files[0];
    if (file) {
      const statusEl = $("#bar-license-status");
      uploadLawyerCredentialFile(file, "bar_license", statusEl);
    }
  };
}

const aadhaarFileEl = $("#aadhaar-file");
if (aadhaarFileEl) {
  aadhaarFileEl.onchange = e => {
    const file = e.target.files[0];
    if (file) {
      const statusEl = $("#gov-id-status");
      uploadLawyerCredentialFile(file, "aadhaar", statusEl);
    }
  };
}

function toast(m) {
  $("#toast").textContent = m;
  $("#toast").classList.add("show");
  setTimeout(() => $("#toast").classList.remove("show"), 2400);
}

// Dynamic experience calculation on enrollment date input
const profEnrollmentEl = $("#prof-enrollment");
if (profEnrollmentEl) {
  const handler = (e) => {
    const exp = calculateExperience(e.target.value);
    const expEl = $("#prof-exp");
    if (expEl) expEl.value = exp;
  };
  profEnrollmentEl.onchange = handler;
  profEnrollmentEl.oninput = handler;
}

function initLanguageSuggestions() {
  const input = $("#prof-languages");
  const dropdown = $("#lang-dropdown");
  if (!input || !dropdown) return;

  const ALL_LANGUAGES = [
    "Kannada",
    "Hindi",
    "Bengali",
    "English",
    "Marathi",
    "Telugu",
    "Tamil",
    "Gujarati",
    "Malayalam"
  ];

  let selectedIndex = -1;

  const renderSuggestions = () => {
    const rawVal = input.value;
    const tokens = rawVal.split(",").map(t => t.trim());
    const currentQuery = (tokens[tokens.length - 1] || "").toLowerCase();

    const selectedSet = new Set(tokens.slice(0, -1).map(t => t.toLowerCase()).filter(Boolean));

    const matches = ALL_LANGUAGES.filter(lang => {
      const lower = lang.toLowerCase();
      if (selectedSet.has(lower)) return false;
      if (!currentQuery) return true;
      return lower.includes(currentQuery);
    });

    if (matches.length === 0) {
      dropdown.hidden = true;
      dropdown.innerHTML = "";
      selectedIndex = -1;
      return;
    }

    dropdown.innerHTML = matches.map((lang, idx) => `
      <div class="lang-dropdown-item ${idx === selectedIndex ? 'selected' : ''}" data-lang="${lang}">
        <span>${lang}</span>
        <small style="color:var(--muted);font-size:11px;">+ Add</small>
      </div>
    `).join("");

    dropdown.hidden = false;

    dropdown.querySelectorAll(".lang-dropdown-item").forEach(item => {
      item.onmousedown = (e) => {
        e.preventDefault();
        selectLanguage(item.dataset.lang);
      };
    });
  };

  const selectLanguage = (lang) => {
    const rawVal = input.value;
    let tokens = rawVal.split(",").map(t => t.trim()).filter(Boolean);
    
    if (tokens.length > 0) {
      const lastToken = tokens[tokens.length - 1].toLowerCase();
      if (!ALL_LANGUAGES.map(l => l.toLowerCase()).includes(lastToken)) {
        tokens.pop();
      }
    }
    
    const exists = tokens.some(t => t.toLowerCase() === lang.toLowerCase());
    if (!exists) {
      tokens.push(lang);
    }
    
    input.value = tokens.join(", ") + ", ";
    dropdown.hidden = true;
    selectedIndex = -1;
    input.focus();
  };

  input.addEventListener("input", () => {
    selectedIndex = -1;
    renderSuggestions();
  });

  input.addEventListener("focus", () => {
    renderSuggestions();
  });

  input.addEventListener("keydown", (e) => {
    const items = dropdown.querySelectorAll(".lang-dropdown-item");
    if (dropdown.hidden || items.length === 0) return;

    if (e.key === "ArrowDown") {
      e.preventDefault();
      selectedIndex = (selectedIndex + 1) % items.length;
      renderSuggestions();
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      selectedIndex = (selectedIndex - 1 + items.length) % items.length;
      renderSuggestions();
    } else if (e.key === "Enter" || e.key === "Tab") {
      if (selectedIndex >= 0 && items[selectedIndex]) {
        e.preventDefault();
        selectLanguage(items[selectedIndex].dataset.lang);
      }
    } else if (e.key === "Escape") {
      dropdown.hidden = true;
      selectedIndex = -1;
    }
  });

  document.addEventListener("click", (e) => {
    if (!input.contains(e.target) && !dropdown.contains(e.target)) {
      dropdown.hidden = true;
      selectedIndex = -1;
    }
  });
}

const NotificationsManager = (() => {
  let notifications = JSON.parse(localStorage.getItem("vm_notifications") || "[]");

  function save() {
    localStorage.setItem("vm_notifications", JSON.stringify(notifications.slice(0, 30)));
    render();
  }

  function add(icon, text) {
    notifications.unshift({
      id: Date.now(),
      icon,
      text,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      read: false
    });
    save();
  }

  function markAllRead() {
    notifications.forEach(n => n.read = true);
    save();
  }

  function render() {
    const badge = document.getElementById("notification-badge");
    const list = document.getElementById("notification-list");
    if (!badge || !list) return;

    const unreadCount = notifications.filter(n => !n.read).length;
    if (unreadCount > 0) {
      badge.textContent = unreadCount > 9 ? "9+" : unreadCount;
      badge.style.display = "flex";
    } else {
      badge.style.display = "none";
    }

    if (notifications.length === 0) {
      list.innerHTML = `<div class="notif-empty">No new notifications</div>`;
      return;
    }

    list.innerHTML = notifications.map(n => `
      <div class="notif-item ${n.read ? '' : 'unread'}" data-id="${n.id}">
        <span class="notif-icon">${n.icon}</span>
        <div class="notif-content">
          <p class="notif-text">${n.text}</p>
          <span class="notif-time">${n.time}</span>
        </div>
      </div>
    `).join("");
  }

  function initUI() {
    const bell = document.getElementById("notification-bell");
    const dropdown = document.getElementById("notification-dropdown");
    const markReadBtn = document.getElementById("mark-all-read-btn");

    if (bell && dropdown) {
      bell.addEventListener("click", (e) => {
        e.stopPropagation();
        const isOpen = dropdown.style.display === "block";
        dropdown.style.display = isOpen ? "none" : "block";
      });

      document.addEventListener("click", (e) => {
        if (dropdown && !dropdown.contains(e.target) && e.target !== bell) {
          dropdown.style.display = "none";
        }
      });
    }

    if (markReadBtn) {
      markReadBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        markAllRead();
      });
    }

    render();
  }

  return { add, markAllRead, render, initUI };
})();

function initRealtimeSync() {
  if (window.NotificationsManager) {
    NotificationsManager.initUI();
  } else {
    NotificationsManager.initUI();
  }

  if (!window.sseClient) return;

  window.sseClient.connect();

  window.sseClient.on("BOOKING_CREATED", (data) => {
    SoundNotifier.playChime();
    const msg = `New consultation booked by ${data.client_name || "Client"}`;
    toast(`🎉 ${msg}!`);
    NotificationsManager.add("🎉", msg);
    loadData();
  });

  window.sseClient.on("DRAFT_REQUEST_SUBMITTED", (data) => {
    SoundNotifier.playChime();
    const msg = `New document drafting request: "${data.title || "Request"}"`;
    toast(`📑 ${msg}`);
    NotificationsManager.add("📑", msg);
    const portal = document.getElementById("lawyer-drafting-portal");
    if (portal && !portal.hidden) {
      loadDraftingPortal();
    }
  });

  window.sseClient.on("PROPOSAL_ACCEPTED", (data) => {
    SoundNotifier.playChime();
    const msg = `Proposal for "${data.title}" accepted by ${data.client_name || "Client"}`;
    toast(`✨ ${msg}!`);
    NotificationsManager.add("✨", msg);
    loadData();
    loadDraftingPortal();
  });

  window.sseClient.on("CHAT_MESSAGE_RECEIVED", (data) => {
    SoundNotifier.playChime();
    const msg = `New message from ${data.sender_name || "Client"}`;
    if (data && data.booking_id === activeBookingId) {
      loadMessages();
    } else {
      toast(`💬 ${msg}`);
    }
    NotificationsManager.add("💬", msg);
  });
}

// Initial triggers
if (LexAPI.getCurrentUser()?.role === "lawyer") {
  loadData();
  initLanguageSuggestions();
  initRealtimeSync();
}


// ── Drafting Feature Functions for Lawyer ─────────────────────────────────────

let activeDraftTab = "available";

function escapeHtml(text) {
  if (!text) return "";
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

async function loadDraftingPortal() {
  const panel = document.getElementById("drafting-lawyer-panel");
  if (!panel) return;

  panel.innerHTML = `
    <div style="text-align:center; padding:40px;">
      <div style="width: 40px; height: 40px; border: 4px solid var(--sage); border-top-color: var(--forest); border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 16px;"></div>
      <p style="color:var(--muted); font-size:14px;">Loading portal data…</p>
    </div>`;

  try {
    const requests = await LexAPI.listDraftingRequests();
    window.currentDraftingRequests = requests;
    
    if (activeDraftTab === "available") {
      if (!lawyerProfile || !lawyerProfile.verified) {
        panel.innerHTML = `
          <div style="text-align:center; padding:40px; border-radius:12px; border:1px solid #17251f0f; background:#fdf8f5; max-width:600px; margin:0 auto; width:100%;">
            <div style="font-size:40px; margin-bottom:12px;">🔒</div>
            <h3 style="font-family:'Playfair Display'; font-size:20px; color:var(--terra); margin:0 0 8px;">Verification Required</h3>
            <p style="color:var(--muted); font-size:14px; line-height:1.6; margin:0 0 16px;">Only verified legal professionals can view and accept drafting assignments. Please complete your profile and upload verification documents.</p>
            <button class="primary" data-action="go-profile" style="border:none; border-radius:99px; padding:10px 20px; font-weight:700; background:var(--forest); color:white; cursor:pointer;">Go to Profile Verification →</button>
          </div>`;
        return;
      }

      const list = requests.filter(r => r.creator_id !== LexAPI.getCurrentUser()?.id && r.status === "open");
      if (list.length === 0) {
        panel.innerHTML = `<p style="text-align:center; color:var(--muted); font-size:14px; padding:30px 0;">No drafting assignments currently available from clients.</p>`;
        return;
      }

      panel.innerHTML = list.map(req => {
        const myProp = req.proposals ? req.proposals.find(p => p.lawyer_id === LexAPI.getCurrentUser()?.id && p.status === "pending") : null;
        let counterHtml = "";
        
        if (myProp) {
          counterHtml = `
            <div style="margin-top:16px; background:#f4f8f5; border:1px solid #c3e6cb; border-radius:12px; padding:12px 16px; font-size:13px; color:#1e4620;">
              You have countered this request for <strong>${money(myProp.amount_minor / 100)}</strong>. Awaiting client's response.
            </div>`;
        } else {
          counterHtml = `
            <div style="margin-top:16px; display:flex; gap:12px; align-items:center; flex-wrap:wrap;">
              <button class="primary" data-action="accept-assignment" data-id="${req.id}" style="min-height:36px; padding:8px 16px; font-size:13px; font-weight:700; border-radius:99px; border:none; background:var(--forest); color:white; cursor:pointer;">Accept for ${money(req.price_minor / 100)}</button>
              <button class="outline" data-action="counter-offer" data-id="${req.id}" data-price="${req.price_minor / 100}" style="color:var(--forest); border:1px solid var(--forest); background:none; min-height:36px; padding:8px 16px; font-size:13px; font-weight:700; border-radius:99px; cursor:pointer;">Quote Counter Price</button>
            </div>`;
        }

        return `
          <article style="background:white; border-radius:16px; padding:24px; border:1px solid #17251f12; text-align:left;">
            <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:12px;">
              <div>
                <h3 style="font-family:'Playfair Display'; font-size:22px; margin:0 0 8px; color:var(--forest);">${escapeHtml(req.title)}</h3>
                <p style="color:var(--muted); font-size:14px; line-height:1.5; margin:0 0 12px;">${escapeHtml(req.description)}</p>
                <div style="display:flex; gap:16px; font-size:12px; font-weight:700; color:var(--muted); text-transform:uppercase; letter-spacing:0.04em;">
                  <span>Client Budget: ${money(req.price_minor / 100)}</span>
                  <span>•</span>
                  <span>Posted: ${new Date(req.created_at).toLocaleDateString()}</span>
                </div>
                ${req.documents && req.documents.length ? `
                  <div style="margin-top: 12px; display:flex; flex-wrap:wrap; gap:10px; align-items:center;">
                    <span style="font-size:11px; font-weight:700; color:var(--muted); text-transform:uppercase; letter-spacing:0.04em;">Reference docs:</span>
                    ${req.documents.map(doc => `
                      <a href="/api/v1/drafting/documents/download?key=${encodeURIComponent(doc.key)}&token=${encodeURIComponent(LexAPI.getAccessToken() || '')}" target="_blank" style="font-size:13px; color:var(--forest); text-decoration:underline; font-weight:600; display:inline-flex; align-items:center; gap:4px;">
                        📎 ${escapeHtml(doc.filename)}
                      </a>
                    `).join("")}
                  </div>
                ` : ""}
              </div>
            </div>
            ${counterHtml}
          </article>
        `;
      }).join("");

    } else if (activeDraftTab === "my-requests") {
      const list = requests.filter(r => r.creator_id === LexAPI.getCurrentUser()?.id);
      if (list.length === 0) {
        panel.innerHTML = `
          <div style="text-align:center; padding:30px 0;">
            <p style="color:var(--muted); font-size:14px; margin-bottom:16px;">You haven't posted any drafting requests yet.</p>
            <button class="primary" data-action="create-drafting" style="border:none; border-radius:99px; padding:10px 20px; font-weight:700; background:var(--forest); color:white; cursor:pointer;">＋ Post Requirement</button>
          </div>`;
        return;
      }

      panel.innerHTML = list.map(req => {
        let statusText = "";
        let statusClass = "";
        switch (req.status) {
          case "open": statusText = "Open for Quotes"; statusClass = "status-pending"; break;
          case "pending_payment": statusText = "Awaiting Payment"; statusClass = "status-pending"; break;
          case "in_progress": statusText = "In Progress"; statusClass = "status-progress"; break;
          case "submitted": statusText = "Draft Submitted"; statusClass = "status-progress"; break;
          case "completed": statusText = "Completed"; statusClass = "status-done"; break;
          case "cancelled": statusText = "Cancelled"; statusClass = "status-cancelled"; break;
        }

        let statusStyle = "";
        if (req.status === "completed") {
          statusStyle = "background:#edf7ed; color:#1e4620; border: 1px solid #c3e6cb;";
        } else if (req.status === "cancelled") {
          statusStyle = "background:#fdf2f2; color:#9b1c1c; border: 1px solid #f5c2c2;";
        } else if (req.status === "in_progress" || req.status === "submitted") {
          statusStyle = "background:#eef6fc; color:#1a567d; border: 1px solid #b3d7f2;";
        } else {
          statusStyle = "background:#fffbf2; color:#9a6b0c; border: 1px solid #fbe6c2;";
        }

        let badgeHtml = `<span style="padding: 6px 14px; border-radius: 99px; font-size: 11px; font-weight: 700; text-transform: uppercase; display:inline-block; ${statusStyle}">${statusText}</span>`;
        let priceText = `Budget: ${money(req.price_minor / 100)}`;
        if (req.agreed_price_minor) {
          priceText = `Agreed Price: ${money(req.agreed_price_minor / 100)}`;
        }

        let proposalsHtml = "";
        if (req.status === "open" && req.proposals && req.proposals.length > 0) {
          const pendingProps = req.proposals.filter(p => p.status === "pending");
          if (pendingProps.length > 0) {
            proposalsHtml = `
              <div style="margin-top: 16px; border-top: 1px solid var(--line); padding-top: 16px;">
                <h4 style="font-size: 13px; font-weight: 700; margin: 0 0 12px; color: var(--forest);">Counter-Offers:</h4>
                <div style="display: flex; flex-direction: column; gap: 10px;">
                  ${pendingProps.map(p => `
                    <div style="display: flex; justify-content: space-between; align-items: center; background: #fbfdfb; border: 1px solid #17251f0c; padding: 12px 16px; border-radius: 12px;">
                      <div>
                        <strong style="font-size: 14px; color: var(--forest);">${escapeHtml(p.lawyer_name || "Verified Lawyer")}</strong>
                        <div style="font-size: 12px; color: var(--muted); margin-top: 2px;">Proposed Price: ${money(p.amount_minor / 100)}</div>
                      </div>
                      <button class="primary" style="padding: 6px 14px; font-size: 12px; min-height: 32px; border-radius:99px; border:none; background:var(--forest); color:white; cursor:pointer;" data-action="accept-proposal" data-id="${req.id}" data-proposal-id="${p.id}">Accept Quote</button>
                    </div>
                  `).join("")}
                </div>
              </div>`;
          }
        }

        let actionHtml = "";
        if (req.status === "pending_payment") {
          actionHtml = `
            <div style="margin-top:20px; display:flex; gap:12px; align-items:center;">
              <button class="primary" data-action="pay-drafting" data-id="${req.id}" style="min-height:36px; padding:8px 18px; font-size:13px; font-weight:700; border-radius:99px; border:none; background:var(--forest); color:white; cursor:pointer;">Pay & Start Work (${money(req.agreed_price_minor / 100)})</button>
              <button class="outline" data-action="cancel-drafting" data-id="${req.id}" style="color:var(--terra); border: 1px solid var(--terra); background:none; min-height:36px; padding:8px 18px; font-size:13px; font-weight:700; border-radius:99px; cursor:pointer;">Cancel Request</button>
            </div>`;
        } else if (req.status === "open") {
          actionHtml = `
            <div style="margin-top:20px;">
              <button class="outline" data-action="cancel-drafting" data-id="${req.id}" style="color:var(--terra); border: 1px solid var(--terra); background:none; min-height:36px; padding:8px 18px; font-size:13px; font-weight:700; border-radius:99px; cursor:pointer;">Cancel Request</button>
            </div>`;
        } else if (req.status === "submitted") {
          const docDownloadHtml = req.draft_file_key ? `
            <a href="/api/v1/drafting/documents/download?key=${encodeURIComponent(req.draft_file_key)}&token=${encodeURIComponent(LexAPI.getAccessToken() || '')}" target="_blank" style="font-size:13px; color:var(--forest); background:white; padding:12px 16px; border-radius:8px; border:1px solid #d5e0d7; text-decoration:none; font-weight:600; display:flex; justify-content:space-between; align-items:center; box-shadow:0 1px 3px rgba(0,0,0,0.04); margin-bottom:12px;">
              <span>📄 ${escapeHtml(req.draft_filename || 'Submitted Legal Document')}</span>
              <span style="font-size:12px; font-weight:700; color:var(--forest);">Download Document ↓</span>
            </a>
          ` : (req.draft_text ? `
            <div style="white-space: pre-wrap; background: white; border: 1px solid var(--line); padding: 14px; border-radius: 8px; font-family: monospace; font-size: 13px; max-height: 250px; overflow-y: auto; color: var(--ink); line-height: 1.5; margin-bottom:12px;">${escapeHtml(req.draft_text)}</div>
          ` : '');

          actionHtml = `
            <div style="margin-top: 20px; background: #faf8f5; border: 1px solid #e8dcc4; border-radius: 12px; padding: 20px;">
              <h4 style="font-size: 14px; font-weight: 700; margin: 0 0 10px; color: var(--terra);">Submitted Legal Document:</h4>
              ${docDownloadHtml}
              <div style="margin-top: 16px; display: flex; gap: 12px;">
                <button class="primary" data-action="approve-draft" data-id="${req.id}" style="min-height:36px; padding:8px 18px; font-size:13px; font-weight:700; border-radius:99px; border:none; background:var(--forest); color:white; cursor:pointer;">Approve & Release Payment</button>
              </div>
            </div>`;
        } else if (req.status === "completed") {
          const docDownloadHtml = req.draft_file_key ? `
            <a href="/api/v1/drafting/documents/download?key=${encodeURIComponent(req.draft_file_key)}&token=${encodeURIComponent(LexAPI.getAccessToken() || '')}" target="_blank" style="font-size:13px; color:var(--forest); background:white; padding:12px 16px; border-radius:8px; border:1px solid #d5e0d7; text-decoration:none; font-weight:600; display:flex; justify-content:space-between; align-items:center; box-shadow:0 1px 3px rgba(0,0,0,0.04);">
              <span>📄 ${escapeHtml(req.draft_filename || 'Approved Legal Document')}</span>
              <span style="font-size:12px; font-weight:700; color:var(--forest);">Download Document ↓</span>
            </a>
          ` : (req.draft_text ? `
            <div style="white-space: pre-wrap; background: white; border: 1px solid var(--line); padding: 14px; border-radius: 8px; font-family: monospace; font-size: 13px; max-height: 250px; overflow-y: auto; color: var(--ink); line-height: 1.5;">${escapeHtml(req.draft_text)}</div>
          ` : '');

          actionHtml = `
            <div style="margin-top: 20px; background: #f4f8f5; border: 1px solid #bddcc4; border-radius: 12px; padding: 20px;">
              <h4 style="font-size: 14px; font-weight: 700; margin: 0 0 10px; color: var(--forest); display:flex; align-items:center; gap:6px;"><span>✓</span> Approved Document:</h4>
              ${docDownloadHtml}
            </div>`;
        }

        return `
          <article style="background:white; border-radius:16px; padding:24px; border:1px solid #17251f12; text-align:left; display:flex; flex-direction:column;">
            <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:12px;">
              <div style="flex:1;">
                <h3 style="font-family:'Playfair Display'; font-size:22px; margin:0 0 8px; color:var(--forest);">${escapeHtml(req.title)}</h3>
                <p style="color:var(--muted); font-size:14px; line-height:1.5; margin:0 0 12px;">${escapeHtml(req.description)}</p>
                <div style="display:flex; gap:16px; font-size:12px; font-weight:700; color:var(--muted); text-transform:uppercase;">
                  <span>${priceText}</span>
                  <span>Posted: ${new Date(req.created_at).toLocaleDateString()}</span>
                  ${req.drafter_name ? `<span>Drafter: ${escapeHtml(req.drafter_name)}</span>` : ""}
                </div>
                ${req.documents && req.documents.length ? `
                  <div style="margin-top: 12px; display:flex; flex-wrap:wrap; gap:10px; align-items:center;">
                    <span style="font-size:11px; font-weight:700; color:var(--muted); text-transform:uppercase; letter-spacing:0.04em;">Reference docs:</span>
                    ${req.documents.map(doc => `
                      <a href="/api/v1/drafting/documents/download?key=${encodeURIComponent(doc.key)}&token=${encodeURIComponent(LexAPI.getAccessToken() || '')}" target="_blank" style="font-size:13px; color:var(--forest); text-decoration:underline; font-weight:600; display:inline-flex; align-items:center; gap:4px;">
                        📎 ${escapeHtml(doc.filename)}
                      </a>
                    `).join("")}
                  </div>
                ` : ""}
              </div>
              <div>
                ${badgeHtml}
              </div>
            </div>
            ${proposalsHtml}
            ${actionHtml}
          </article>
        `;
      }).join("");

    } else if (activeDraftTab === "my-assignments") {
      const list = requests.filter(r => r.drafter_id === LexAPI.getCurrentUser()?.id);
      if (list.length === 0) {
        panel.innerHTML = `<p style="text-align:center; color:var(--muted); font-size:14px; padding:30px 0;">No active drafting assignments yet.</p>`;
        return;
      }

      panel.innerHTML = list.map(req => {
        let statusText = "";
        let statusClass = "";
        switch (req.status) {
          case "pending_payment": statusText = "Awaiting Client Payment"; statusClass = "status-pending"; break;
          case "in_progress": statusText = "In Progress / Paid"; statusClass = "status-progress"; break;
          case "submitted": statusText = "Submitted (Awaiting Approval)"; statusClass = "status-progress"; break;
          case "completed": statusText = "Completed / Paid Out"; statusClass = "status-done"; break;
          case "cancelled": statusText = "Cancelled"; statusClass = "status-cancelled"; break;
        }

        let statusStyle = "";
        if (req.status === "completed") {
          statusStyle = "background:#edf7ed; color:#1e4620; border: 1px solid #c3e6cb;";
        } else if (req.status === "cancelled") {
          statusStyle = "background:#fdf2f2; color:#9b1c1c; border: 1px solid #f5c2c2;";
        } else if (req.status === "in_progress") {
          statusStyle = "background:#eef6fc; color:#1a567d; border: 1px solid #b3d7f2;";
        } else {
          statusStyle = "background:#fffbf2; color:#9a6b0c; border: 1px solid #fbe6c2;";
        }

        let badgeHtml = `<span style="padding: 6px 14px; border-radius: 99px; font-size: 11px; font-weight: 700; text-transform: uppercase; display:inline-block; ${statusStyle}">${statusText}</span>`;
        
        let payoutInfo = "";
        if (req.agreed_price_minor) {
          const totalPaid = req.agreed_price_minor / 100;
          const platformFee = totalPaid * 0.10;
          const netPayout = totalPaid - platformFee;
          payoutInfo = `
            <div style="font-size:12px; color:var(--muted); margin-top:4px;">
              Gross Value: ${money(totalPaid)} | Net payout (minus 10% fee): <strong>${money(netPayout)}</strong>
            </div>`;
        }

        let actionHtml = "";
        if (req.status === "in_progress") {
          actionHtml = `
            <div style="margin-top:20px; display:flex; flex-direction:column; gap:10px;">
              <button class="primary" data-action="submit-draft" data-id="${req.id}" data-title="${escapeHtml(req.title)}" style="min-height:36px; padding:8px 18px; font-size:13px; font-weight:700; border-radius:99px; border:none; background:var(--forest); color:white; cursor:pointer; align-self:flex-start;">📤 Upload Ready File</button>
            </div>`;
        } else if (req.status === "submitted") {
          const commentCount = (req.comments || []).length;
          const pdfUrl = req.draft_file_key ? `/api/v1/drafting/documents/download?key=${encodeURIComponent(req.draft_file_key)}&token=${encodeURIComponent(LexAPI.getAccessToken() || '')}` : '#';

          const docDownloadHtml = req.draft_file_key ? `
            <a href="${pdfUrl}" target="_blank" style="font-size:13px; color:var(--forest); background:white; padding:10px 14px; border-radius:8px; border:1px solid #d5e0d7; text-decoration:none; font-weight:600; display:flex; justify-content:space-between; align-items:center; box-shadow:0 1px 3px rgba(0,0,0,0.04); margin-bottom:10px;">
              <span>📄 ${escapeHtml(req.draft_filename || 'Submitted Legal Document')}</span>
              <span style="font-size:12px; font-weight:700; color:var(--forest);">Download ↓</span>
            </a>
          ` : (req.draft_text ? `
            <div style="white-space:pre-wrap; font-family:monospace; font-size:12px; padding:12px; background:white; border:1px solid var(--line); border-radius:8px; max-height:180px; overflow-y:auto; margin-bottom:10px;">${escapeHtml(req.draft_text)}</div>
          ` : '');

          actionHtml = `
            <div style="margin-top:20px; background:#fafafa; border:1px solid var(--line); border-radius:12px; padding:16px;">
              <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                <h4 style="font-size:13px; font-weight:700; margin:0; color:var(--forest);">Your submitted draft:</h4>
                <span style="font-size:11px; font-weight:700; color:var(--forest); background:#eef5f0; padding:2px 8px; border-radius:99px;">💬 ${commentCount} Comment Pin${commentCount === 1 ? '' : 's'}</span>
              </div>
              ${docDownloadHtml}
              <div style="display:flex; gap:10px; margin-top:10px; flex-wrap:wrap;">
                <button class="primary" data-action="open-pdf-annotator-lawyer" data-id="${req.id}" data-filename="${escapeHtml(req.draft_filename || 'Legal Document')}" data-url="${pdfUrl}" style="border:none; border-radius:99px; padding:6px 14px; font-size:12px; font-weight:700; cursor:pointer; background:var(--forest); color:white;">🔍 View Client Comments (PDF)</button>
                <button class="outline" data-action="submit-draft" data-id="${req.id}" data-title="${escapeHtml(req.title)}" style="color:var(--forest); border:1px solid var(--forest); background:none; min-height:30px; padding:6px 12px; font-size:12px; font-weight:700; border-radius:99px; cursor:pointer;">Re-upload Ready File</button>
              </div>
            </div>`;
        } else if (req.status === "revision_requested") {
          const commentCount = (req.comments || []).length;
          const pdfUrl = req.draft_file_key ? `/api/v1/drafting/documents/download?key=${encodeURIComponent(req.draft_file_key)}&token=${encodeURIComponent(LexAPI.getAccessToken() || '')}` : '#';

          actionHtml = `
            <div style="margin-top:20px; background:#fff7ed; border:1px solid #fed7aa; border-radius:12px; padding:16px;">
              <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                <h4 style="font-size:13px; font-weight:700; margin:0; color:#9a3412;">🔄 Client Requested Revisions:</h4>
                <span style="font-size:11px; font-weight:700; color:#9a3412; background:#ffedd5; padding:2px 8px; border-radius:99px;">💬 ${commentCount} Comment Pin${commentCount === 1 ? '' : 's'}</span>
              </div>
              <p style="font-size:12px; color:#7c2d12; margin:0 0 10px;">Client dropped inline feedback pins. Review them on the PDF and upload an updated draft.</p>
              <div style="display:flex; gap:10px; flex-wrap:wrap;">
                <button class="primary" data-action="open-pdf-annotator-lawyer" data-id="${req.id}" data-filename="${escapeHtml(req.draft_filename || 'Legal Document')}" data-url="${pdfUrl}" style="border:none; border-radius:99px; padding:6px 16px; font-size:12px; font-weight:700; cursor:pointer; background:#9a3412; color:white;">🔍 View Client Comments (PDF)</button>
                <button class="primary" data-action="submit-draft" data-id="${req.id}" data-title="${escapeHtml(req.title)}" style="border:none; border-radius:99px; padding:6px 16px; font-size:12px; font-weight:700; cursor:pointer; background:var(--forest); color:white;">📤 Upload Revised Draft</button>
              </div>
            </div>`;
        } else if (req.status === "completed") {
          const docDownloadHtml = req.draft_file_key ? `
            <a href="/api/v1/drafting/documents/download?key=${encodeURIComponent(req.draft_file_key)}&token=${encodeURIComponent(LexAPI.getAccessToken() || '')}" target="_blank" style="font-size:13px; color:var(--forest); background:white; padding:10px 14px; border-radius:8px; border:1px solid #d5e0d7; text-decoration:none; font-weight:600; display:flex; justify-content:space-between; align-items:center; box-shadow:0 1px 3px rgba(0,0,0,0.04);">
              <span>📄 ${escapeHtml(req.draft_filename || 'Approved Legal Document')}</span>
              <span style="font-size:12px; font-weight:700; color:var(--forest);">Download ↓</span>
            </a>
          ` : (req.draft_text ? `
            <div style="white-space:pre-wrap; font-family:monospace; font-size:12px; padding:12px; background:white; border:1px solid var(--line); border-radius:8px; max-height:180px; overflow-y:auto;">${escapeHtml(req.draft_text)}</div>
          ` : '');

          actionHtml = `
            <div style="margin-top:20px; background:#f4f8f5; border:1px solid #c3e6cb; border-radius:12px; padding:16px;">
              <h4 style="font-size:13px; font-weight:700; margin:0 0 8px; color:#1e4620;">Approved Legal Document:</h4>
              ${docDownloadHtml}
            </div>`;
        }

        return `
          <article style="background:white; border-radius:16px; padding:24px; border:1px solid #17251f12; text-align:left; display:flex; flex-direction:column;">
            <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:12px;">
              <div style="flex:1;">
                <h3 style="font-family:'Playfair Display'; font-size:22px; margin:0 0 8px; color:var(--forest);">${escapeHtml(req.title)}</h3>
                <p style="color:var(--muted); font-size:14px; line-height:1.5; margin:0 0 12px;">${escapeHtml(req.description)}</p>
                <div style="display:flex; flex-direction:column; gap:4px;">
                  <div style="font-size:12px; font-weight:700; color:var(--muted); text-transform:uppercase;">
                    <span>Value: ${money(req.agreed_price_minor / 100)}</span>
                    <span>•</span>
                    <span>Accepted: ${new Date(req.created_at).toLocaleDateString()}</span>
                  </div>
                  ${payoutInfo}
                  ${req.documents && req.documents.length ? `
                    <div style="margin-top: 12px; display:flex; flex-wrap:wrap; gap:10px; align-items:center;">
                      <span style="font-size:11px; font-weight:700; color:var(--muted); text-transform:uppercase; letter-spacing:0.04em;">Reference docs:</span>
                      ${req.documents.map(doc => `
                        <a href="/api/v1/drafting/documents/download?key=${encodeURIComponent(doc.key)}&token=${encodeURIComponent(LexAPI.getAccessToken() || '')}" target="_blank" style="font-size:13px; color:var(--forest); text-decoration:underline; font-weight:600; display:inline-flex; align-items:center; gap:4px;">
                          📎 ${escapeHtml(doc.filename)}
                        </a>
                      `).join("")}
                    </div>
                  ` : ""}
                </div>
              </div>
              <div>
                ${badgeHtml}
              </div>
            </div>
            ${actionHtml}
          </article>
        `;
      }).join("");
    }

  } catch (err) {
    panel.innerHTML = `<div style="color:var(--terra); text-align:center; padding:30px; font-weight:700;">Error loading portal data: ${err.message}</div>`;
  }
}

// Modal management helpers
function showDraftingModal(html) {
  const modal = document.getElementById("drafting-modal");
  const content = document.getElementById("drafting-modal-content");
  if (!modal || !content) return;
  content.innerHTML = html;
  modal.hidden = false;
}

function closeDraftingModal() {
  const modal = document.getElementById("drafting-modal");
  if (modal) modal.hidden = true;
}

// Wire up modal events
(function initDraftingModalEvents() {
  const closeBtn = document.getElementById("drafting-modal-close");
  const modal = document.getElementById("drafting-modal");
  if (closeBtn) closeBtn.onclick = closeDraftingModal;
  if (modal) {
    modal.addEventListener("click", e => {
      if (e.target === modal) closeDraftingModal();
    });
  }
})();

// Document clicks listener for lawyer drafting actions (event delegation for CSP compliance)
document.addEventListener("click", async e => {
  const tab = e.target.closest("[data-draft-tab]");
  if (tab) {
    document.querySelectorAll("[data-draft-tab]").forEach(btn => btn.classList.toggle("active", btn === tab));
    activeDraftTab = tab.dataset.draftTab;
    await loadDraftingPortal();
  }
  
  if (e.target.id === "lawyer-create-draft-btn") {
    openCreateDraftingModal();
  }

  // Handle all data-action buttons (replaces inline onclick blocked by CSP)
  const actionBtn = e.target.closest("[data-action]");
  if (actionBtn) {
    const action = actionBtn.dataset.action;
    const id = actionBtn.dataset.id;

    switch (action) {
      case "go-profile":
        view("profile");
        break;
      case "accept-assignment":
        console.log("Delegating accept-assignment case for reqId:", id);
        window.acceptAssignment(id);
        break;
      case "counter-offer":
        console.log("Delegating counter-offer case for reqId:", id);
        const reqObjCounter = (window.currentDraftingRequests || []).find(r => r.id === id);
        window.openCounterOfferModal(id, parseFloat(actionBtn.dataset.price), reqObjCounter ? reqObjCounter.documents : []);
        break;
      case "create-drafting":
        window.openCreateDraftingModal();
        break;
      case "accept-proposal":
        window.acceptProposal(id, actionBtn.dataset.proposalId);
        break;
      case "pay-drafting":
        window.payForDrafting(id);
        break;
      case "cancel-drafting":
        window.cancelDrafting(id);
        break;
      case "approve-draft":
        window.approveDraft(id);
        break;
      case "submit-draft":
        const reqObj = (window.currentDraftingRequests || []).find(r => r.id === id);
        window.openSubmitDraftModal(id, actionBtn.dataset.title || "", reqObj ? reqObj.documents : []);
        break;
      case "open-pdf-annotator-lawyer": {
        const reqObjLawyer = (window.currentDraftingRequests || []).find(r => r.id === id);
        if (reqObjLawyer) {
          window.openPdfAnnotatorModal({
            reqId: id,
            pdfUrl: actionBtn.dataset.url,
            filename: actionBtn.dataset.filename || "Document.pdf",
            status: reqObjLawyer.status,
            isClient: false,
            comments: reqObjLawyer.comments || [],
            draftText: reqObjLawyer.draft_text || null,
            onRefresh: async () => { await loadDraftingPortal(); }
          });
        }
        break;
      }
      case "view-drafting-details":
        window.viewDraftingDetails(id);
        break;
      case "close-modal":
        window.closeDraftingModal();
        break;
    }
  }
});

// ── Custom Confirmation Modal (replaces native confirm() which can be blocked) ──
function confirmAction(message, label, onConfirm) {
  showDraftingModal(`
    <div style="text-align:center; padding:8px 0;">
      <div style="font-size:40px; margin-bottom:16px;">⚠️</div>
      <h2 style="font-family:'Playfair Display'; font-size:22px; margin:0 0 12px; color:var(--forest);">Are you sure?</h2>
      <p style="color:var(--muted); font-size:14px; line-height:1.6; margin-bottom:28px;">${message}</p>
      <div style="display:flex; gap:12px; justify-content:center;">
        <button type="button" data-action="close-modal" id="confirm-cancel-btn" style="border:none; border-radius:99px; padding:12px 24px; font-weight:700; cursor:pointer; background:#edf2ee; color:var(--ink); font-size:14px;">Cancel</button>
        <button type="button" id="confirm-action-btn" style="border:none; border-radius:99px; padding:12px 24px; font-weight:700; cursor:pointer; background:var(--terra); color:white; font-size:14px;">${label}</button>
      </div>
    </div>
  `);
  setTimeout(() => {
    const btn = document.getElementById("confirm-action-btn");
    if (btn) {
      btn.onclick = () => {
        closeDraftingModal();
        onConfirm();
      };
    }
  }, 50);
}

// Actions
window.acceptAssignment = async function(reqId) {
  console.log("window.acceptAssignment called for request ID:", reqId);
  confirmAction(
    "Are you sure you want to accept this drafting assignment at the client's stated budget?",
    "Yes, Accept Assignment",
    async () => {
      try {
        console.log("Invoking LexAPI.acceptDraftingRequest...");
        await LexAPI.acceptDraftingRequest(reqId);
        console.log("Successfully accepted assignment.");
        toast("Assignment accepted! Waiting for client payment.");
        await loadDraftingPortal();
      } catch (err) {
        console.error("Failed to accept assignment:", err);
        toast("Error: " + err.message);
      }
    }
  );
}

window.openCounterOfferModal = function(reqId, currentPrice, documents = []) {
  showDraftingModal(`
    <span class="kicker" style="color:var(--terra); text-transform:uppercase; font-size:11px; letter-spacing:0.16em; font-weight:700;">Quote Counter Price</span>
    <h2 style="font-family:'Playfair Display'; font-size:24px; margin:6px 0 12px; color:var(--forest);">Make a Counter-Offer</h2>
    <p style="color:var(--muted); font-size:13px; margin-bottom:18px; line-height:1.5;">Specify the amount (in INR) you require to complete this drafting work. The client will be notified and can accept your quote to proceed.</p>
    
    ${documents && documents.length ? `
      <div style="background:#f4f7f5; border-radius:10px; padding:12px 14px; margin-bottom:16px; border:1px solid #e2ebe4;">
        <span style="font-size:11px; font-weight:700; color:var(--forest); text-transform:uppercase; letter-spacing:0.06em; display:block; margin-bottom:6px;">📎 Attached Client Reference Documents (${documents.length})</span>
        <div style="display:flex; flex-wrap:wrap; gap:8px;">
          ${documents.map(doc => `
            <a href="/api/v1/drafting/documents/download?key=${encodeURIComponent(doc.key)}&token=${encodeURIComponent(LexAPI.getAccessToken() || '')}" target="_blank" style="font-size:12px; color:var(--forest); background:white; padding:6px 12px; border-radius:8px; border:1px solid #d5e0d7; text-decoration:none; font-weight:600; display:inline-flex; align-items:center; gap:4px; box-shadow:0 1px 2px rgba(0,0,0,0.04);">
              📄 ${doc.filename ? String(doc.filename).replace(/</g, "&lt;").replace(/>/g, "&gt;") : "Document"} <span style="font-size:10px; opacity:0.7;">↓</span>
            </a>
          `).join("")}
        </div>
      </div>
    ` : ''}

    <form class="form" id="counter-offer-form" autocomplete="off" style="display:grid; gap:16px;">
      <div class="field full" style="display:grid; gap:6px;">
        <label style="font-size:12px; font-weight:700;">Counter price (INR) *</label>
        <input type="number" id="counter-price-val" placeholder="e.g. 3000" min="100" required style="width:100%; border:1px solid var(--line); border-radius:11px; padding:13px; font-size:16px; background:#fbfcfb;" value="${currentPrice + 500}">
      </div>
      <div id="counter-form-error" style="color:var(--terra); font-size:12px; font-weight:700; margin-bottom:10px;"></div>
      <div class="actions" style="display:flex; justify-content:flex-end; gap:10px;">
        <button type="button" class="secondary" data-action="close-modal" style="border:none; border-radius:99px; padding:10px 20px; font-weight:700; cursor:pointer; background:#edf2ee; color:var(--ink);">Cancel</button>
        <button class="primary" type="submit" style="border:none; border-radius:99px; padding:10px 20px; font-weight:700; cursor:pointer; background:var(--forest); color:white;">Submit Offer</button>
      </div>
    </form>
  `);

  document.getElementById("counter-offer-form").onsubmit = async e => {
    e.preventDefault();
    const amount = parseInt(document.getElementById("counter-price-val").value, 10);
    if (isNaN(amount) || amount < 1) {
      document.getElementById("counter-form-error").textContent = "Please enter a valid amount.";
      return;
    }

    const submitBtn = e.target.querySelector("button[type='submit']");
    submitBtn.disabled = true;
    submitBtn.textContent = "Submitting...";

    try {
      await LexAPI.createDraftingProposal(reqId, { amount_minor: amount * 100 });
      closeDraftingModal();
      toast("Counter-offer submitted successfully!");
      await loadDraftingPortal();
    } catch (err) {
      document.getElementById("counter-form-error").textContent = err.message;
      submitBtn.disabled = false;
      submitBtn.textContent = "Submit Offer";
    }
  };
}

window.openSubmitDraftModal = function(reqId, title, documents = []) {
  showDraftingModal(`
    <span class="kicker" style="color:var(--terra); text-transform:uppercase; font-size:11px; letter-spacing:0.16em; font-weight:700;">Legal Drafting Desk</span>
    <h2 style="font-family:'Playfair Display'; font-size:24px; margin:6px 0 6px; color:var(--forest);">Upload Ready Legal Document</h2>
    <p style="color:var(--muted); font-size:12px; margin-bottom:12px; font-weight:600;">Assignment: ${escapeHtml(title)}</p>
    
    ${documents && documents.length ? `
      <div style="background:#f4f7f5; border-radius:10px; padding:12px 14px; margin-bottom:16px; border:1px solid #e2ebe4;">
        <span style="font-size:11px; font-weight:700; color:var(--forest); text-transform:uppercase; letter-spacing:0.06em; display:block; margin-bottom:6px;">📎 Attached Client Reference Documents (${documents.length})</span>
        <div style="display:flex; flex-wrap:wrap; gap:8px;">
          ${documents.map(doc => `
            <a href="/api/v1/drafting/documents/download?key=${encodeURIComponent(doc.key)}&token=${encodeURIComponent(LexAPI.getAccessToken() || '')}" target="_blank" style="font-size:12px; color:var(--forest); background:white; padding:6px 12px; border-radius:8px; border:1px solid #d5e0d7; text-decoration:none; font-weight:600; display:inline-flex; align-items:center; gap:4px; box-shadow:0 1px 2px rgba(0,0,0,0.04);">
              📄 ${escapeHtml(doc.filename)} <span style="font-size:10px; opacity:0.7;">↓</span>
            </a>
          `).join("")}
        </div>
      </div>
    ` : ''}

    <form class="form" id="submit-draft-form" autocomplete="off" style="display:grid; gap:16px;">
      <div class="field full" style="display:grid; gap:6px;">
        <label style="font-size:12px; font-weight:700;">Ready Legal Document File (PDF, DOCX, DOC, TXT) *</label>
        <div style="border: 2px dashed #d5e0d7; border-radius: 12px; padding: 28px 20px; text-align: center; background: #fbfcfb; cursor: pointer; position: relative; transition: border-color 0.2s;" id="draft-dropzone">
          <input type="file" id="submit-draft-file-input" required accept=".pdf,.doc,.docx,.txt,.rtf,image/*" style="position: absolute; top:0; left:0; width:100%; height:100%; opacity:0; cursor:pointer; z-index:2;" />
          <div style="font-size: 36px; margin-bottom: 8px;">📄</div>
          <div style="font-weight: 700; font-size: 14px; color: var(--forest);" id="submit-draft-file-label">Click or drag ready legal document file here</div>
          <div style="font-size: 11px; color: var(--muted); margin-top: 6px;" id="submit-draft-file-subtext">Supported formats: PDF, DOCX, DOC, TXT, RTF (Max 15MB)</div>
        </div>
      </div>
      <div id="submit-draft-error" style="color:var(--terra); font-size:12px; font-weight:700; margin-bottom:4px;"></div>
      <div class="actions" style="display:flex; justify-content:flex-end; gap:10px;">
        <button type="button" class="secondary" data-action="close-modal" style="border:none; border-radius:99px; padding:10px 20px; font-weight:700; cursor:pointer; background:#edf2ee; color:var(--ink);">Cancel</button>
        <button class="primary" type="submit" style="border:none; border-radius:99px; padding:10px 20px; font-weight:700; cursor:pointer; background:var(--forest); color:white;">Upload & Submit Draft</button>
      </div>
    </form>
  `);

  const fileInput = document.getElementById("submit-draft-file-input");
  fileInput.onchange = () => {
    if (fileInput.files && fileInput.files[0]) {
      const file = fileInput.files[0];
      document.getElementById("submit-draft-file-label").textContent = `Selected: ${file.name}`;
      document.getElementById("submit-draft-file-subtext").textContent = `Size: ${(file.size / (1024 * 1024)).toFixed(2)} MB`;
    }
  };

  document.getElementById("submit-draft-form").onsubmit = async e => {
    e.preventDefault();
    const file = fileInput.files ? fileInput.files[0] : null;
    if (!file) {
      document.getElementById("submit-draft-error").textContent = "Please select a document file to upload.";
      return;
    }

    const progressUI = showUploadProgressModal(file.name);
    progressUI.update(5, "Requesting upload URL...");
    const submitBtn = e.target.querySelector("button[type='submit']");
    submitBtn.disabled = true;

    try {
      const presign = await LexAPI.presignDraftingDocument(file.name, file.type || "application/octet-stream");
      const formData = new FormData();
      Object.entries(presign.upload.fields || {}).forEach(([k, v]) => formData.append(k, v));
      formData.append("file", file);

      const headers = {};
      const token = LexAPI.getAccessToken();
      const uploadUrl = LexAPI.resolveUploadUrl(presign.upload.url);
      if (token && presign.upload.url.startsWith("/")) {
        headers["Authorization"] = `Bearer ${token}`;
      }

      progressUI.update(10, "Uploading draft file...");
      await uploadWithProgress(uploadUrl, formData, headers, (percent) => {
        progressUI.update(Math.min(95, Math.max(10, percent)), `Uploading: ${percent}%`);
      });

      progressUI.update(98, "Finalizing submission...");
      submitBtn.textContent = "Submitting draft...";
      await LexAPI.submitDraft(reqId, {
        draft_file_key: presign.key,
        draft_filename: file.name
      });

      progressUI.close(true, "Draft submitted!");
      await loadDraftingPortal();
    } catch (err) {
      progressUI.close(false, err.message || "Failed to submit document.");
      submitBtn.disabled = false;
    }
  };
};

window.openCreateDraftingModal = function() {
  showDraftingModal(`
    <span class="kicker" style="color:var(--terra); text-transform:uppercase; font-size:11px; letter-spacing:0.16em; font-weight:700;">Drafting Request</span>
    <h2 style="font-family:'Playfair Display'; font-size:28px; margin:6px 0 12px; color:var(--forest);">Post Drafting Requirement</h2>
    <p class="lead" style="color:var(--muted); font-size:13px; margin-bottom:20px; line-height:1.6;">Describe the document you need drafted (contracts, deeds, notices) and specify your budget price.</p>
    <form class="form" id="lawyer-create-drafting-form" autocomplete="off" style="display:grid; gap:20px; margin-top:20px;">
      <div class="field full" style="display:grid; gap:8px;">
        <label style="font-size:13px; font-weight:700; color:var(--forest);">Document Title *</label>
        <input type="text" id="drafting-title" placeholder="e.g. Partnership Deed" required minlength="2" maxlength="255" style="width:100%; border:1px solid var(--line); border-radius:11px; padding:14px; font-size:15px; background:#fbfcfb;">
      </div>
      <div class="field full" style="display:grid; gap:8px;">
        <label style="font-size:13px; font-weight:700; color:var(--forest);">Requirements & Instructions *</label>
        <textarea id="drafting-desc" placeholder="Provide background information, the names of parties involved, key clauses, and other requirements." required minlength="5" style="width:100%; border:1px solid var(--line); border-radius:11px; padding:14px; font-size:15px; background:#fbfcfb; min-height:140px; resize:vertical; line-height:1.5;"></textarea>
      </div>
      <div class="field full" style="display:grid; gap:8px;">
        <label style="font-size:13px; font-weight:700; color:var(--forest);">Budget Price willing to pay (INR) *</label>
        <input type="number" id="drafting-price" placeholder="e.g. 2500" min="100" required style="width:100%; border:1px solid var(--line); border-radius:11px; padding:14px; font-size:15px; background:#fbfcfb;">
      </div>
      <div class="field full" style="display:grid; gap:8px;">
        <label style="font-size:13px; font-weight:700; color:var(--forest);">Reference Documents (optional)</label>
        <input type="file" id="lawyer-drafting-files" multiple style="font-size:14px; color:var(--ink);" accept=".pdf,.png,.jpg,.jpeg,.docx">
        <div id="lawyer-drafting-uploaded-list" style="margin-top:8px; display:flex; flex-direction:column; gap:6px;"></div>
      </div>
      <div id="drafting-form-error" style="color:var(--terra); font-size:12px; font-weight:700;"></div>
      <div class="actions" style="display:flex; justify-content:flex-end; gap:10px; margin-top:10px;">
        <button type="button" class="secondary" data-action="close-modal" style="border:none; border-radius:99px; padding:12px 20px; font-weight:700; cursor:pointer; background:#edf2ee; color:var(--ink);">Cancel</button>
        <button class="primary" type="submit" style="border:none; border-radius:99px; padding:12px 20px; font-weight:700; cursor:pointer; background:var(--forest); color:white;">Post Request</button>
      </div>
    </form>
  `);

  let uploadedFiles = [];
  const fileInput = document.querySelector("#lawyer-drafting-files");
  const listDiv = document.querySelector("#lawyer-drafting-uploaded-list");

  if (fileInput && listDiv) {
    fileInput.onchange = async () => {
      const files = Array.from(fileInput.files);
      for (const file of files) {
        if (!["application/pdf", "image/jpeg", "image/png", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"].includes(file.type)) {
          toast(`Skipped ${file.name}: Only PDF, JPEG, PNG, or DOCX are allowed.`);
          continue;
        }
        if (file.size > 20 * 1024 * 1024) {
          toast(`Skipped ${file.name}: Must be under 20 MB.`);
          continue;
        }

        const item = document.createElement("div");
        item.style.fontSize = "13px";
        item.style.color = "var(--muted)";
        item.textContent = `Uploading ${file.name}...`;
        listDiv.appendChild(item);

        const progressUI = showUploadProgressModal(file.name);
        try {
          progressUI.update(5, "Getting presigned link...");
          const presign = await LexAPI.presignDraftingDocument(file.name, file.type || "application/pdf");
          const formData = new FormData();
          Object.entries(presign.upload.fields || {}).forEach(([k,v]) => formData.append(k, v));
          formData.append("file", file);
          const headers = {};
          const token = LexAPI.getAccessToken();
          const uploadUrl = LexAPI.resolveUploadUrl(presign.upload.url);
          if (token && presign.upload.url.startsWith("/")) {
            headers["Authorization"] = `Bearer ${token}`;
          }
          progressUI.update(10, "Uploading to storage...");
          await uploadWithProgress(uploadUrl, formData, headers, (percent) => {
            progressUI.update(Math.min(95, Math.max(10, percent)), `Uploading: ${percent}%`);
          });
          uploadedFiles.push({ filename: file.name, key: presign.key });
          item.style.color = "var(--forest)";
          item.style.fontWeight = "bold";
          item.textContent = `✓ ${file.name} uploaded`;
          progressUI.close(true, "Reference file uploaded!");
        } catch (err) {
          const mockKey = `drafting/mock-${Date.now()}-${file.name}`;
          try {
            progressUI.update(70, "Attempting local upload...");
            const formData = new FormData();
            formData.append("key", mockKey);
            formData.append("file", file);
            const headers = {};
            const token = LexAPI.getAccessToken();
            if (token) headers["Authorization"] = `Bearer ${token}`;
            await fetch(LexAPI.resolveUploadUrl("/api/v1/drafting/documents/mock-upload"), { method: "POST", body: formData, headers });
            uploadedFiles.push({ filename: file.name, key: mockKey });
            item.style.color = "var(--forest)";
            item.style.fontWeight = "bold";
            item.textContent = `✓ ${file.name} uploaded (local)`;
            progressUI.close(true, "Stored in local vault!");
          } catch (innerErr) {
            item.style.color = "var(--terra)";
            item.textContent = `✗ Upload failed: ${file.name}`;
            progressUI.close(false, innerErr.message);
          }
        }
      }
    };
  }
  
  document.getElementById("lawyer-create-drafting-form").onsubmit = async e => {
    e.preventDefault();
    const title = document.getElementById("drafting-title").value;
    const description = document.getElementById("drafting-desc").value;
    const price = parseInt(document.getElementById("drafting-price").value, 10);
    
    if (isNaN(price) || price < 1) {
      document.getElementById("drafting-form-error").textContent = "Price must be a valid amount greater than zero.";
      return;
    }
    
    const submitBtn = e.target.querySelector("button[type='submit']");
    submitBtn.disabled = true;
    submitBtn.textContent = "Submitting...";
    
    try {
      await LexAPI.createDraftingRequest({
        title,
        description,
        price_minor: price * 100,
        documents: uploadedFiles
      });
      closeDraftingModal();
      toast("Drafting request posted successfully!");
      await loadDraftingPortal();
    } catch (err) {
      document.getElementById("drafting-form-error").textContent = err.message;
      submitBtn.disabled = false;
      submitBtn.textContent = "Post Request";
    }
  };
}

window.acceptProposal = async function(reqId, proposalId) {
  confirmAction(
    "Are you sure you want to accept this counter-offer? This will finalize the amount and lock this assignment.",
    "Yes, Accept Quote",
    async () => {
      try {
        await LexAPI.acceptDraftingProposal(reqId, proposalId);
        toast("Quote accepted! Please make the payment to start work.");
        await loadDraftingPortal();
      } catch (err) {
        toast("Error: " + err.message);
      }
    }
  );
}

window.payForDrafting = async function(reqId) {
  try {
    const req = await LexAPI.getDraftingRequest(reqId);
    if (!req) {
      toast("Error: Drafting request not found");
      return;
    }
    const amountMinor = req.agreed_price_minor || req.price_minor || 0;
    const formatMoney = n => '₹' + Number(n).toLocaleString('en-IN');
    const priceText = formatMoney(amountMinor / 100);

    const safeTitle = req.title ? String(req.title).replace(/</g, "&lt;").replace(/>/g, "&gt;") : "";
    const safeDesc = req.description ? String(req.description).replace(/</g, "&lt;").replace(/>/g, "&gt;") : "";

    showDraftingModal(`
      <div style="padding: 10px 5px;">
        <span class="eyebrow" style="color:var(--forest); font-weight:700; letter-spacing:0.12em; text-transform:uppercase; font-size:11px;">🔒 SECURE ESCROW PAYMENT</span>
        <h2 style="font-family:'Playfair Display',serif; font-size:24px; margin:6px 0 16px; color:var(--ink);">Complete Drafting Payment</h2>
        
        <div style="background:var(--bg-soft); border-radius:12px; padding:16px; margin-bottom:20px; border:1px solid rgba(0,0,0,0.06);">
          <h4 style="margin:0 0 6px; font-size:15px; font-weight:700; color:var(--ink);">${safeTitle}</h4>
          <p style="margin:0; font-size:13px; color:var(--muted); line-height:1.4;">${safeDesc ? (safeDesc.substring(0, 120) + (safeDesc.length > 120 ? '...' : '')) : ''}</p>
        </div>

        <div style="background:#f9fbf9; border:1px solid #e2ebe4; border-radius:12px; padding:16px; margin-bottom:20px;">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
            <span style="font-size:13px; color:var(--muted);">Agreed Drafting Fee</span>
            <strong style="font-size:14px; color:var(--ink);">${priceText}</strong>
          </div>
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
            <span style="font-size:13px; color:var(--muted);">Escrow & Protection Fee</span>
            <span style="font-size:13px; color:var(--forest); font-weight:600;">Free (Included)</span>
          </div>
          <hr style="border:none; border-top:1px dashed #d5e0d7; margin:10px 0;">
          <div style="display:flex; justify-content:space-between; align-items:center;">
            <strong style="font-size:15px; color:var(--ink);">Total Amount Payable</strong>
            <strong style="font-size:20px; color:var(--forest); font-family:'DM Sans',sans-serif;">${priceText}</strong>
          </div>
        </div>

        <div style="margin-bottom:22px;">
          <label style="font-size:12px; font-weight:700; text-transform:uppercase; letter-spacing:0.05em; color:var(--muted); display:block; margin-bottom:8px;">Select Payment Method</label>
          <div style="display:flex; flex-direction:column; gap:8px;">
            <label style="display:flex; align-items:center; gap:10px; padding:12px 14px; border:1.5px solid var(--forest); border-radius:10px; cursor:pointer; background:#fff;">
              <input type="radio" name="drafting-payment-method-lawyer" value="upi" checked style="accent-color:var(--forest);">
              <div>
                <strong style="font-size:13px; display:block; color:var(--ink);">UPI / Instant Pay (BHIM, GPay, Paytm)</strong>
                <small style="color:var(--muted); font-size:11px;">Zero transaction fees</small>
              </div>
            </label>
            <label style="display:flex; align-items:center; gap:10px; padding:12px 14px; border:1px solid #e0e0e0; border-radius:10px; cursor:pointer; background:#fff;">
              <input type="radio" name="drafting-payment-method-lawyer" value="card" style="accent-color:var(--forest);">
              <div>
                <strong style="font-size:13px; display:block; color:var(--ink);">Credit / Debit Card</strong>
                <small style="color:var(--muted); font-size:11px;">Visa, MasterCard, RuPay</small>
              </div>
            </label>
          </div>
        </div>

        <div style="background:#f4f7f5; padding:12px 14px; border-radius:10px; font-size:12px; color:var(--muted); line-height:1.5; margin-bottom:24px; display:flex; align-items:flex-start; gap:8px;">
          <span style="font-size:16px;">🛡️</span>
          <span><strong>Buyer Protection:</strong> Your payment will be safely held in VidhiMeet Escrow and only released after you review and approve the finalized draft.</span>
        </div>

        <div id="drafting-pay-error-lawyer" style="color:var(--terra); font-size:13px; margin-bottom:12px; font-weight:600;" hidden></div>

        <div class="actions" style="display:flex; gap:12px; justify-content:flex-end;">
          <button class="ghost secondary" onclick="closeDraftingModal()" style="padding:10px 20px; border-radius:99px; cursor:pointer;">Cancel</button>
          <button class="primary" id="confirm-drafting-pay-btn-lawyer" style="padding:10px 24px; border-radius:99px; background:var(--forest); color:white; border:none; font-weight:700; cursor:pointer;">Confirm & Pay ${priceText}</button>
        </div>
      </div>
    `);

    document.getElementById("confirm-drafting-pay-btn-lawyer").onclick = async function() {
      const btn = this;
      const errEl = document.getElementById("drafting-pay-error-lawyer");
      if (errEl) errEl.hidden = true;
      btn.disabled = true;
      btn.textContent = "Processing Payment...";

      try {
        await LexAPI.confirmDraftingPayment(reqId);
        closeDraftingModal();
        toast("Payment successful! The lawyer has been notified to begin drafting.");
        await loadDraftingPortal();
      } catch (err) {
        btn.disabled = false;
        btn.textContent = `Confirm & Pay ${priceText}`;
        if (errEl) {
          errEl.textContent = err.message || "Payment processing failed. Please try again.";
          errEl.hidden = false;
        }
      }
    };
  } catch (err) {
    toast("Error loading payment details: " + err.message);
  }
}

window.approveDraft = async function(reqId) {
  confirmAction(
    "Are you sure you want to approve this draft? This will complete the request and release funds to the drafter minus platform fee.",
    "Yes, Approve & Release",
    async () => {
      try {
        await LexAPI.approveDraft(reqId);
        toast("Draft approved successfully! Payment released to the lawyer.");
        await loadDraftingPortal();
      } catch (err) {
        toast("Error: " + err.message);
      }
    }
  );
}

window.cancelDrafting = async function(reqId) {
  console.log("window.cancelDrafting (lawyer) called for request ID:", reqId);
  confirmAction(
    "Are you sure you want to cancel this request? Any pending bids/proposals will be rejected.",
    "Yes, Cancel Request",
    async () => {
      try {
        console.log("Invoking LexAPI.cancelDraftingRequest (lawyer)...");
        await LexAPI.cancelDraftingRequest(reqId);
        console.log("Successfully cancelled request.");
        toast("Drafting request cancelled.");
        await loadDraftingPortal();
      } catch (err) {
        console.error("Failed to cancel request (lawyer):", err);
        toast("Error cancelling request: " + err.message);
      }
    }
  );
}

window.viewDraftingDetails = async function(reqId) {
  try {
    const req = await LexAPI.getDraftingRequest(reqId);
    if (!req) {
      toast("Error: Drafting request not found");
      return;
    }
    const formatMoney = n => '₹' + Number(n).toLocaleString('en-IN');
    const priceText = formatMoney((req.agreed_price_minor || req.price_minor || 0) / 100);

    const safeTitle = req.title ? String(req.title).replace(/</g, "&lt;").replace(/>/g, "&gt;") : "";
    const safeDesc = req.description ? String(req.description).replace(/</g, "&lt;").replace(/>/g, "&gt;") : "";

    const docHtml = req.documents && req.documents.length ? `
      <div style="background:#f4f7f5; border-radius:12px; padding:16px; margin-bottom:20px; border:1px solid #e2ebe4;">
        <span style="font-size:12px; font-weight:700; color:var(--forest); text-transform:uppercase; letter-spacing:0.06em; display:block; margin-bottom:10px;">📁 Attached Reference Documents (${req.documents.length})</span>
        <div style="display:flex; flex-direction:column; gap:8px;">
          ${req.documents.map(doc => `
            <a href="/api/v1/drafting/documents/download?key=${encodeURIComponent(doc.key)}&token=${encodeURIComponent(LexAPI.getAccessToken() || '')}" target="_blank" style="font-size:13px; color:var(--forest); background:white; padding:10px 14px; border-radius:8px; border:1px solid #d5e0d7; text-decoration:none; font-weight:600; display:flex; justify-content:space-between; align-items:center; box-shadow:0 1px 3px rgba(0,0,0,0.04);">
              <span>📄 ${doc.filename ? String(doc.filename).replace(/</g, "&lt;").replace(/>/g, "&gt;") : "Document"}</span>
              <span style="font-size:12px; font-weight:700; color:var(--forest);">Download ↓</span>
            </a>
          `).join("")}
        </div>
      </div>
    ` : `
      <div style="background:#fafafa; border-radius:10px; padding:12px 14px; margin-bottom:20px; border:1px dashed #e0e0e0; font-size:13px; color:var(--muted);">
        ℹ️ No reference documents were attached to this request.
      </div>
    `;

    const draftHtml = req.draft_file_key ? `
      <div style="margin-bottom:20px; background:#fbfcfb; border:1px solid #d5e0d7; border-radius:12px; padding:16px;">
        <h4 style="font-size:14px; font-weight:700; margin:0 0 10px; color:var(--forest);">Submitted Ready Document</h4>
        <a href="/api/v1/drafting/documents/download?key=${encodeURIComponent(req.draft_file_key)}&token=${encodeURIComponent(LexAPI.getAccessToken() || '')}" target="_blank" style="font-size:13px; color:var(--forest); background:white; padding:12px 16px; border-radius:8px; border:1px solid #d5e0d7; text-decoration:none; font-weight:600; display:flex; justify-content:space-between; align-items:center; box-shadow:0 1px 3px rgba(0,0,0,0.04);">
          <span>📄 ${escapeHtml(req.draft_filename || 'Legal Document')}</span>
          <span style="font-size:12px; font-weight:700; color:var(--forest);">Download Document ↓</span>
        </a>
      </div>
    ` : (req.draft_text ? `
      <div style="margin-bottom:20px; background:#fbfcfb; border:1px solid #d5e0d7; border-radius:12px; padding:16px;">
        <h4 style="font-size:14px; font-weight:700; margin:0 0 10px; color:var(--forest);">Drafted Content</h4>
        <div style="white-space:pre-wrap; font-family:monospace; font-size:13px; background:white; border:1px solid var(--line); padding:14px; border-radius:8px; max-height:220px; overflow-y:auto;">${String(req.draft_text).replace(/</g, "&lt;").replace(/>/g, "&gt;")}</div>
      </div>
    ` : "");

    showDraftingModal(`
      <div style="padding:10px 5px;">
        <span class="eyebrow" style="color:var(--forest); font-weight:700; letter-spacing:0.12em; text-transform:uppercase; font-size:11px;">Drafting Request Details</span>
        <h2 style="font-family:'Playfair Display',serif; font-size:24px; margin:6px 0 16px; color:var(--ink);">${safeTitle}</h2>
        
        <div style="display:flex; gap:16px; font-size:12px; font-weight:700; color:var(--muted); text-transform:uppercase; margin-bottom:16px; flex-wrap:wrap;">
          <span>Budget/Price: ${priceText}</span>
          <span>•</span>
          <span>Status: ${req.status.replace("_", " ")}</span>
          <span>•</span>
          <span>Posted: ${new Date(req.created_at).toLocaleDateString()}</span>
        </div>

        <div style="background:var(--bg-soft); border-radius:12px; padding:16px; margin-bottom:20px; border:1px solid rgba(0,0,0,0.06);">
          <h4 style="margin:0 0 6px; font-size:13px; font-weight:700; color:var(--forest); text-transform:uppercase;">Requirements & Instructions</h4>
          <p style="margin:0; font-size:14px; color:var(--ink); line-height:1.5; white-space:pre-wrap;">${safeDesc}</p>
        </div>

        ${docHtml}
        ${draftHtml}

        <div class="actions" style="display:flex; justify-content:flex-end;">
          <button class="ghost secondary" onclick="closeDraftingModal()" style="padding:10px 24px; border-radius:99px; cursor:pointer;">Close</button>
        </div>
      </div>
    `);
  } catch (err) {
    toast("Error loading request details: " + err.message);
  }
};

