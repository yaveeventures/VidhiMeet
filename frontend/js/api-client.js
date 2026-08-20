const LexAPI = (() => {
  const getBaseUrl = () => {
    const custom = window.API_BASE_URL || window.ENV_API_BASE_URL;
    if (custom) return custom.replace(/\/+$/, "") + "/api/v1";
    return "/api/v1";
  };
  let accessToken = sessionStorage.getItem("lex_access_token") || localStorage.getItem("lex_access_token");
  
  let isRefreshing = false;
  let refreshSubscribers = [];
  const eventSubscribers = new Map();
  const cache = new Map(); // key -> {data, timestamp, ttl}

  function subscribeTokenRefresh(cb) {
    refreshSubscribers.push(cb);
  }

  function onRefreshed(token) {
    refreshSubscribers.forEach(cb => cb(token));
    refreshSubscribers = [];
  }

  function emit(event, data) {
    const subs = eventSubscribers.get(event);
    if (subs) {
      subs.forEach(cb => {
        try { cb(data); } catch (e) { console.error(`Error in subscriber for ${event}:`, e); }
      });
    }
  }

  async function request(path, options = {}) {
    if (!accessToken) {
      accessToken = sessionStorage.getItem("lex_access_token") || localStorage.getItem("lex_access_token");
    }
    const headers = {
      "Content-Type": "application/json",
      "ngrok-skip-browser-warning": "true",
      ...(options.headers || {})
    };
    if (accessToken) headers.Authorization = `Bearer ${accessToken}`;
    let response = await fetch(getBaseUrl() + path, {...options, headers});
    
    if (response.status === 401 && path !== "/auth/login" && path !== "/auth/refresh") {
      const refreshToken = localStorage.getItem("lex_refresh_token");
      if (refreshToken) {
        let retryToken = null;
        if (!isRefreshing) {
          isRefreshing = true;
          try {
            const refreshResp = await fetch(getBaseUrl() + "/auth/refresh", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ refresh_token: refreshToken })
            });
            if (refreshResp.ok) {
              const tokens = await refreshResp.json();
              accessToken = tokens.access_token;
              sessionStorage.setItem("lex_access_token", accessToken);
              localStorage.setItem("lex_access_token", accessToken);
              localStorage.setItem("lex_refresh_token", tokens.refresh_token);
              isRefreshing = false;
              retryToken = accessToken;
              onRefreshed(accessToken);
            } else {
              isRefreshing = false;
              onRefreshed(null);
              LexAPI.logout();
              return response;
            }
          } catch (err) {
            isRefreshing = false;
            onRefreshed(null);
            LexAPI.logout();
            throw err;
          }
        } else {
          retryToken = await new Promise(resolve => {
            subscribeTokenRefresh(token => resolve(token));
          });
        }
        
        if (retryToken) {
          headers.Authorization = `Bearer ${retryToken}`;
          response = await fetch(getBaseUrl() + path, {...options, headers});
        }
      }
    }

    if (!response.ok) {
      const body = await response.json().catch(() => ({detail: "Request failed"}));
      const rawDetail = body.detail || body.message || (body.errors ? JSON.stringify(body.errors) : null) || `Request failed (${response.status})`;
      const errorMsg = typeof rawDetail === "string" ? rawDetail : JSON.stringify(rawDetail);
      emit("error", { path, error: errorMsg });
      throw new Error(errorMsg);
    }
    return response.status === 204 ? null : response.json();
  }

  // Cache Helper
  async function cachedRequest(path, ttlMs = 15000) {
    const now = Date.now();
    if (cache.has(path)) {
      const entry = cache.get(path);
      if (now - entry.timestamp < entry.ttl) {
        return entry.data;
      }
    }
    const data = await request(path);
    cache.set(path, { data, timestamp: now, ttl: ttlMs });
    return data;
  }

  return {
    subscribe(event, callback) {
      if (!eventSubscribers.has(event)) eventSubscribers.set(event, new Set());
      eventSubscribers.get(event).add(callback);
      return () => eventSubscribers.get(event).delete(callback);
    },
    invalidateCache(prefix = "") {
      for (const key of cache.keys()) {
        if (key.startsWith(prefix)) cache.delete(key);
      }
    },
    async login(email, password) {
      const tokens = await request("/auth/login", {method:"POST", body:JSON.stringify({email,password})});
      accessToken = tokens.access_token;
      sessionStorage.setItem("lex_access_token", accessToken);
      localStorage.setItem("lex_access_token", accessToken);
      localStorage.setItem("lex_refresh_token", tokens.refresh_token);
      emit("auth:change", { authenticated: true, user: this.getCurrentUser() });
      return tokens;
    },
    async googleLogin(payload) {
      const tokens = await request("/auth/google", {
        method: "POST",
        body: JSON.stringify(payload)
      });
      accessToken = tokens.access_token;
      sessionStorage.setItem("lex_access_token", accessToken);
      localStorage.setItem("lex_access_token", accessToken);
      localStorage.setItem("lex_refresh_token", tokens.refresh_token);
      emit("auth:change", { authenticated: true, user: this.getCurrentUser() });
      return tokens;
    },
    async health() {
      return request("/health");
    },
    async register(email, password, fullName, role, extra = {}) {
      const tokens = await request("/auth/register", {
        method: "POST", 
        body: JSON.stringify({email, password, full_name: fullName, role, ...extra})
      });
      accessToken = tokens.access_token;
      sessionStorage.setItem("lex_access_token", accessToken);
      localStorage.setItem("lex_access_token", accessToken);
      localStorage.setItem("lex_refresh_token", tokens.refresh_token);
      emit("auth:change", { authenticated: true, user: this.getCurrentUser() });
      return tokens;
    },
    logout() {
      accessToken = null;
      sessionStorage.removeItem("lex_access_token");
      localStorage.removeItem("lex_access_token");
      localStorage.removeItem("lex_refresh_token");
      cache.clear();
      emit("auth:change", { authenticated: false, user: null });
    },
    getCurrentUser() {
      if (!accessToken) {
        accessToken = sessionStorage.getItem("lex_access_token") || localStorage.getItem("lex_access_token");
      }
      if (!accessToken) return null;
      try {
        const base64Url = accessToken.split('.')[1];
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        const pad = base64.length % 4;
        const padded = pad ? base64 + "=".repeat(4 - pad) : base64;
        const payload = JSON.parse(atob(padded));
        const fullName = payload.full_name || payload.name || localStorage.getItem("lex_user_name") || null;
        if (fullName) localStorage.setItem("lex_user_name", fullName);
        const role = payload.role ? String(payload.role).toLowerCase() : null;
        return { id: payload.sub, role: role, full_name: fullName };
      } catch (e) {
        console.error("JWT decoding failed:", e);
        return null;
      }
    },
    publicStats: () => fetch("/api/v1/public/stats").then(r => r.json()).catch(() => null),
    lawyers: filters => cachedRequest(`/lawyers?${new URLSearchParams(filters || {})}`, 10000),
    getProfile: () => request("/lawyers/me"),
    updateProfile: payload => {
      LexAPI.invalidateCache("/lawyers");
      return request("/lawyers/me", {method: "PUT", body: JSON.stringify(payload)});
    },
    bookings: () => request("/bookings"),
    createBooking: async payload => {
      const res = await request("/bookings", {method:"POST",body:JSON.stringify(payload)});
      emit("booking:created", res);
      return res;
    },
    meeting: id => request(`/bookings/${id}/meeting-token`, {method:"POST"}),
    completeBooking: id => request(`/bookings/${id}/complete`, {method:"POST"}),
    disputeBooking: (id, payload) => request(`/bookings/${id}/dispute`, {method:"POST", body: payload ? JSON.stringify(payload) : null}),
    confirmPayment: id => request(`/bookings/${id}/confirm-payment`, {method:"POST"}),
    getCancellationPreview: id => request(`/bookings/${id}/cancellation-preview`),
    cancelBooking: (id, reason) => request(`/bookings/${id}/cancel`, {method:"POST", body: JSON.stringify({reason})}),
    
    // Messages
    getMessages: id => request(`/bookings/${id}/messages`),
    sendMessage: (id, content, encrypted = false, iv = null) => request(`/bookings/${id}/messages`, {method:"POST", body:JSON.stringify({content, encrypted, iv})}),
    
    // Documents
    presignDocument: (id, filename, contentType) => request(`/bookings/${id}/documents/presign?filename=${encodeURIComponent(filename)}&content_type=${encodeURIComponent(contentType)}`, {method:"POST"}),
    confirmDocumentUpload: (id, filename, key) => request(`/bookings/${id}/documents/confirm?filename=${encodeURIComponent(filename)}&key=${encodeURIComponent(key)}`, {method:"POST"}),
    presignLawyerDocument: (filename, contentType) => request(`/lawyers/me/documents/presign?filename=${encodeURIComponent(filename)}&content_type=${encodeURIComponent(contentType)}`, {method:"POST"}),
    confirmLawyerDocumentUpload: (filename, key, docType) => request(`/lawyers/me/documents/confirm?filename=${encodeURIComponent(filename)}&key=${encodeURIComponent(key)}&doc_type=${encodeURIComponent(docType)}`, {method:"POST"}),

    // Admin Console
    metrics: () => request("/admin/metrics"),
    getPendingLawyers: () => request("/admin/lawyers/pending"),
    getRejectedLawyers: () => request("/admin/lawyers/rejected"),
    getAdminUsers: () => request("/admin/users"),
    toggleUserActive: (id, active) => request(`/admin/users/${id}/active?active=${active}`, {method:"PATCH"}),
    getAdminTransactions: () => request("/admin/transactions"),
    getAdminDraftingTransactions: () => request("/admin/drafting-transactions"),
    getDisputes: () => request("/admin/disputes"),
    resolveDispute: (id, outcome, strikeLawyer = false) => request(`/admin/bookings/${id}/resolve?outcome=${outcome}&strike_lawyer=${strikeLawyer}`, {method:"PATCH"}),

    getAuditLogs: () => request("/admin/audit-logs"),
    updatePlatformFee: fee => request(`/admin/config/fees?default_fee=${fee}`, {method:"POST"}),
    verifyLawyer: (id, approved) => request(`/admin/lawyers/${id}/verification?approved=${approved}`, {method:"PATCH"}),
    getAdminPayouts: () => request("/admin/payouts"),
    getPlatformFeedback: () => request("/admin/feedback"),
    submitPlatformFeedback: (payload) => request("/public/feedback", {method:"POST", body:JSON.stringify(payload)}),
    
    // Reviews
    submitReview: (bookingId, rating, comment) => request(`/bookings/${bookingId}/review`, {method:"POST", body:JSON.stringify({rating, comment})}),
    getBookingReview: bookingId => request(`/bookings/${bookingId}/review`).catch(() => null),
    getLawyerReviews: lawyerId => request(`/lawyers/${lawyerId}/reviews`),

    // Bank Account & UPI Verification
    getBankAccount: () => request("/lawyers/me/bank-account").catch(e => {
      const msg = String(e.message || "").toLowerCase();
      if (msg.includes("404") || msg.includes("not found") || msg.includes("no bank account")) return null;
      return Promise.reject(e);
    }),
    addBankAccount: payload => request("/lawyers/me/bank-account", {method:"POST", body:JSON.stringify(payload)}),
    updateBankAccount: payload => request("/lawyers/me/bank-account", {method:"PUT", body:JSON.stringify(payload)}),
    deleteBankAccount: () => request("/lawyers/me/bank-account", {method:"DELETE"}),
    initiateUpiVerification: () => request("/lawyers/me/bank-account/verify", {method:"POST"}),

    // Drafting Features
    listDraftingRequests: () => request("/drafting"),
    getDraftingRequest: id => request(`/drafting/${id}`),
    createDraftingRequest: payload => request("/drafting", {method: "POST", body: JSON.stringify(payload)}),
    acceptDraftingRequest: id => request(`/drafting/${id}/accept`, {method: "POST"}),
    createDraftingProposal: (id, payload) => request(`/drafting/${id}/proposals`, {method: "POST", body: JSON.stringify(payload)}),
    acceptDraftingProposal: (id, proposalId) => request(`/drafting/${id}/proposals/${proposalId}/accept`, {method: "POST"}),
    confirmDraftingPayment: id => request(`/drafting/${id}/confirm-payment`, {method: "POST"}),
    submitDraft: (id, payload) => request(`/drafting/${id}/submit`, {method: "POST", body: JSON.stringify(typeof payload === "string" ? {draft_text: payload} : payload)}),
    approveDraft: id => request(`/drafting/${id}/approve`, {method: "POST"}),
    cancelDraftingRequest: id => request(`/drafting/${id}/cancel`, {method: "POST"}),
    presignDraftingDocument: (filename, contentType) => request(`/drafting/documents/presign?filename=${encodeURIComponent(filename)}&content_type=${encodeURIComponent(contentType)}`, {method:"POST"}),
    getDraftComments: id => request(`/drafting/${id}/comments`),
    addDraftComment: (id, payload) => request(`/drafting/${id}/comments`, {method: "POST", body: JSON.stringify(payload)}),
    deleteDraftComment: (id, commentId) => request(`/drafting/${id}/comments/${commentId}`, {method: "DELETE"}),
    requestDraftRevisions: id => request(`/drafting/${id}/request-revisions`, {method: "POST"}),

    // Calendar Integration
    getIcalToken: () => request("/calendar/token"),
    rotateIcalToken: () => request("/calendar/token/rotate", {method: "POST"}),
    // getBookingIcs triggers a download via anchor — no fetch needed
    // Use downloadBookingIcs(bookingId) helper defined in app.js

    authenticated: () => Boolean(accessToken),
    getAccessToken: () => accessToken
  };
})();

// ── Inactivity Timeout System ────────────────────────────────────────────────
(() => {
  const INACTIVITY_LIMIT = 14 * 60 * 1000;
  const TOTAL_LIMIT = 15 * 60 * 1000;

  let lastActivityTime = Date.now();
  let warningActive = false;

  function resetTimer() {
    if (!warningActive) lastActivityTime = Date.now();
  }

  function checkInactivity() {
    if (!LexAPI.authenticated()) return;
    if (window.dailyCallFrame && typeof window.dailyCallFrame.destroy === "function") {
      lastActivityTime = Date.now();
      return;
    }

    const elapsed = Date.now() - lastActivityTime;
    if (elapsed >= TOTAL_LIMIT) {
      LexAPI.logout();
      window.location.href = "index.html";
    }
  }

  ["mousemove", "mousedown", "keydown", "click", "touchstart"].forEach(evt => {
    window.addEventListener(evt, resetTimer, { passive: true });
  });

  setInterval(checkInactivity, 2000);
})();
