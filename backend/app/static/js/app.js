// ---------- API helper ----------
const API = {
  async request(method, url, body, isFormData = false) {
    const opts = {
      method,
      credentials: "include",
      headers: {},
    };
    if (body) {
      if (isFormData) {
        opts.body = body;
      } else {
        opts.headers["Content-Type"] = "application/json";
        opts.body = JSON.stringify(body);
      }
    }
    const res = await fetch(url, opts);
    let data = {};
    try { data = await res.json(); } catch (e) { /* non-json response */ }
    if (!res.ok) {
      const err = new Error(data.error || "Something went wrong");
      err.details = data.details;
      err.status = res.status;
      throw err;
    }
    return data;
  },
  get(url) { return this.request("GET", url); },
  post(url, body) { return this.request("POST", url, body); },
  put(url, body) { return this.request("PUT", url, body); },
  del(url) { return this.request("DELETE", url); },
  upload(url, formData) { return this.request("POST", url, formData, true); },
};

// ---------- Toast notifications ----------
function showToast(message, type = "success") {
  let stack = document.querySelector(".toast-stack");
  if (!stack) {
    stack = document.createElement("div");
    stack.className = "toast-stack";
    document.body.appendChild(stack);
  }
  const icons = { success: "bi-check-circle-fill", danger: "bi-x-circle-fill", warning: "bi-exclamation-triangle-fill" };
  const colors = { success: "#10b981", danger: "#ef4444", warning: "#f59e0b" };
  const toast = document.createElement("div");
  toast.setAttribute("role", "status");
  toast.setAttribute("aria-live", "polite");
  toast.style.cssText = `background:#fff;border-left:4px solid ${colors[type] || colors.success};box-shadow:0 8px 24px rgba(15,23,42,.12);border-radius:10px;padding:13px 16px;margin-bottom:10px;min-width:280px;display:flex;align-items:center;gap:10px;font-size:14px;font-weight:500;color:#0f172a;animation:fadeUp .2s ease;`;
  toast.innerHTML = `<i class="bi ${icons[type] || icons.success}" style="color:${colors[type] || colors.success};font-size:17px;"></i><span>${message}</span>`;
  stack.appendChild(toast);
  setTimeout(() => { toast.style.opacity = "0"; toast.style.transition = "opacity .3s"; setTimeout(() => toast.remove(), 300); }, 3500);
}

// ---------- Auth guard for protected pages ----------
async function requireAuth() {
  try {
    const data = await API.get("/api/auth/me");
    return data.user;
  } catch (e) {
    window.location.href = "/";
    return null;
  }
}

async function logoutUser() {
  try { await API.post("/api/auth/logout"); } catch (e) {}
  window.location.href = "/";
}

function initials(name) {
  if (!name) return "U";
  const parts = name.trim().split(" ");
  return (parts[0][0] + (parts[1] ? parts[1][0] : "")).toUpperCase();
}

function formatMoney(amount) {
  return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" }).format(amount || 0);
}

function formatDate(dateStr) {
  if (!dateStr) return "—";
  const d = new Date(dateStr + "T00:00:00");
  return d.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
}

function monthName(m) {
  return ["", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"][m];
}

function ensureSidebarBackdrop() {
  let backdrop = document.querySelector(".sidebar-backdrop");
  if (!backdrop) {
    backdrop = document.createElement("div");
    backdrop.className = "sidebar-backdrop";
    backdrop.addEventListener("click", closeSidebar);
    document.body.appendChild(backdrop);
  }
  return backdrop;
}

function toggleSidebar() {
  const sidebar = document.querySelector(".sidebar");
  if (!sidebar) return;
  const shouldOpen = !sidebar.classList.contains("open");
  sidebar.classList.toggle("open", shouldOpen);
  ensureSidebarBackdrop().classList.toggle("show", shouldOpen);
  document.body.classList.toggle("sidebar-open", shouldOpen);
}

function closeSidebar() {
  const sidebar = document.querySelector(".sidebar");
  const backdrop = document.querySelector(".sidebar-backdrop");
  if (sidebar) sidebar.classList.remove("open");
  if (backdrop) backdrop.classList.remove("show");
  document.body.classList.remove("sidebar-open");
}

function setLoadingState(isLoading, selector = ".stat-card, .card-surface") {
  document.querySelectorAll(selector).forEach(el => el.classList.toggle("loading-surface", isLoading));
}

// Render shared sidebar user info + highlight active nav link
function initShell(user) {
  const nameEl = document.querySelector("[data-user-name]");
  const emailEl = document.querySelector("[data-user-email]");
  const avatarEl = document.querySelector("[data-user-avatar]");
  if (nameEl) nameEl.textContent = user.full_name;
  if (emailEl) emailEl.textContent = user.email;
  if (avatarEl) avatarEl.textContent = initials(user.full_name);

  const adminLink = document.querySelector("[data-admin-link]");
  if (adminLink) adminLink.style.display = user.role === "admin" ? "flex" : "none";

  const path = window.location.pathname;
  document.querySelectorAll(".sidebar .nav-link[data-path]").forEach(link => {
    if (link.getAttribute("data-path") === path) link.classList.add("active");
    link.addEventListener("click", () => {
      if (window.innerWidth <= 992) closeSidebar();
    });
  });
}

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape") closeSidebar();
});
