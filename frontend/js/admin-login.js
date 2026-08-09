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
  btn.textContent = "Authenticating\u2026";

  try {
    await LexAPI.login(email, password);
    const currentUser = LexAPI.getCurrentUser();
    const role = currentUser ? String(currentUser.role).toLowerCase() : "";

    if (!currentUser || role !== "admin") {
      LexAPI.logout();
      errorEl.textContent = "Access Denied: This portal is restricted to authorized administrators only.";
      errorEl.style.display = "block";
      btn.disabled = false;
      btn.textContent = "Sign In to Admin Console \u2192";
      return;
    }

    window.location.href = "admin.html";
  } catch (err) {
    errorEl.textContent = err.detail || err.message || "Invalid credentials. Please try again.";
    errorEl.style.display = "block";
    btn.disabled = false;
    btn.textContent = "Sign In to Admin Console \u2192";
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
