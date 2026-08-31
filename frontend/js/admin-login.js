// Admin Login — external script (CSP-safe, no inline scripts)

async function doAdminLogin() {
  const errorEl = document.getElementById("admin-login-error");
  const btn     = document.getElementById("admin-login-btn");
  const email   = document.getElementById("admin-email").value.trim();
  const password = document.getElementById("admin-password").value;

  if (!email || !password) {
    errorEl.textContent = "Please enter your email and password.";
    errorEl.style.display = "block";
    return;
  }

  errorEl.style.display = "none";
  btn.disabled = true;
  btn.style.pointerEvents = "none";
  btn.innerHTML = `<span class="btn-spinner"></span> Authenticating\u2026`;

  try {
    await LexAPI.login(email, password);
    const currentUser = LexAPI.getCurrentUser();
    const role = currentUser ? String(currentUser.role).toLowerCase() : "";

    if (!currentUser || role !== "admin") {
      LexAPI.logout();
      errorEl.textContent = "Access Denied: This portal is restricted to authorized administrators only.";
      errorEl.style.display = "block";
      btn.disabled = false;
      btn.style.pointerEvents = "";
      btn.innerHTML = "Sign In to Admin Console &rarr;";
      return;
    }

    window.location.href = "admin.html";
  } catch (err) {
    let msg = "Invalid credentials. Please try again.";
    if (typeof err === "string") msg = err;
    else if (err && err.detail) msg = typeof err.detail === "string" ? err.detail : JSON.stringify(err.detail);
    else if (err && err.message) msg = err.message;
    errorEl.textContent = msg;
    errorEl.style.display = "block";
    btn.disabled = false;
    btn.style.pointerEvents = "";
    btn.innerHTML = "Sign In to Admin Console &rarr;";
  }
}

document.addEventListener("DOMContentLoaded", function () {
  // Auto-redirect if already logged in as admin
  var user = (typeof LexAPI !== "undefined") ? LexAPI.getCurrentUser() : null;
  if (user && String(user.role).toLowerCase() === "admin") {
    window.location.href = "admin.html";
    return;
  }

  document.getElementById("admin-login-btn").addEventListener("click", doAdminLogin);

  // Enter in password → submit
  document.getElementById("admin-password").addEventListener("keydown", function (e) {
    if (e.key === "Enter") doAdminLogin();
  });

  // Enter in email → move to password
  document.getElementById("admin-email").addEventListener("keydown", function (e) {
    if (e.key === "Enter") document.getElementById("admin-password").focus();
  });
});

// Universal password visibility toggle
document.addEventListener("click", (e) => {
  const btn = e.target.closest(".password-toggle-btn");
  if (!btn) return;
  e.preventDefault();
  const wrap = btn.closest(".password-wrap, .input-wrapper");
  if (!wrap) return;
  const input = wrap.querySelector("input");
  if (!input) return;
  const isPass = input.type === "password";
  input.type = isPass ? "text" : "password";
  const eyeOpen = btn.querySelector(".eye-open");
  const eyeClosed = btn.querySelector(".eye-closed");
  if (eyeOpen && eyeClosed) {
    eyeOpen.style.display = isPass ? "none" : "block";
    eyeClosed.style.display = isPass ? "block" : "none";
  }
  btn.setAttribute("aria-label", isPass ? "Hide password" : "Show password");
  btn.setAttribute("title", isPass ? "Hide password" : "Show password");
});
