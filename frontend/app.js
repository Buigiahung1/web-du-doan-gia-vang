// Configuration & State
let API_BASE = location.origin;
let API_ONLINE = false;

const AppState = {
  currentUser: null,
  jwtToken: "",
  currentRole: "USER",
  activeTab: "tabHome",
  predictionHistory: [],
  priceHistoryData: [],
  chartInstances: {},
};

// Client-side Validation RegEx Rules (Mục 3.2)
const ValidationRules = {
  emailRegex: /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/,
  phoneVietnamRegex: /^(03|05|07|08|09)[0-9]{8}$/,
  passwordLen: 8,
  hasUpper: /[A-Z]/,
  hasLower: /[a-z]/,
  hasNumber: /[0-9]/,
  hasSpecial: /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/,
};

// Helper: Toast Notifications
function showToast(message, type = "success") {
  const container = document.getElementById("toastContainer");
  const toast = document.createElement("div");
  const isSuccess = type === "success";
  const isError = type === "error";

  toast.className = `p-3 rounded-lg border text-xs font-medium flex items-center gap-2.5 transition-all duration-300 transform translate-x-10 pointer-events-auto shadow-subtle ${
    isSuccess
      ? "bg-slate-900 border-emerald-500/40 text-emerald-300"
      : isError
        ? "bg-slate-900 border-rose-500/40 text-rose-300"
        : "bg-slate-900 border-brand-gold/40 text-amber-300"
  }`;

  toast.innerHTML = `
        <i class="${isSuccess ? "fa-solid fa-circle-check text-emerald-400" : isError ? "fa-solid fa-circle-exclamation text-rose-400" : "fa-solid fa-circle-info text-brand-gold"} text-xs"></i>
        <span></span>
      `;

  toast.querySelector("span").textContent = message;
  container.appendChild(toast);
  setTimeout(() => toast.classList.remove("translate-x-10"), 10);
  setTimeout(() => {
    toast.classList.add("opacity-0", "translate-x-10");
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

// Modal Helpers
function openModal(modalId) {
  document.getElementById("modalBackdrop").classList.remove("hidden");
  document.getElementById(modalId).classList.remove("hidden");
}

function closeModal(modalId) {
  document.getElementById(modalId).classList.add("hidden");
  const anyOpen = Array.from(
    document.querySelectorAll('[id^="modal"]:not(#modalBackdrop)')
  ).some((el) => !el.classList.contains("hidden"));
  if (!anyOpen) {
    document.getElementById("modalBackdrop").classList.add("hidden");
  }
}

function closeAllModals() {
  document
    .querySelectorAll('[id^="modal"]')
    .forEach((el) => el.classList.add("hidden"));
}

// Tab Navigation Switcher
function switchTab(tabId) {
  document
    .querySelectorAll(".tab-content")
    .forEach((el) => el.classList.add("hidden"));
  const target = document.getElementById(tabId);
  if (target) {
    target.classList.remove("hidden");
    AppState.activeTab = tabId;
  }

  const navMap = {
    tabHome: "navBtnHome",
    tabPrices: "navBtnPrices",
    tabPredict: "navBtnPredict",
    tabHistory: "navBtnHistory",
    tabIntro: "navBtnIntro",
    tabAdmin: "navBtnAdmin",
  };

  document.querySelectorAll(".nav-item").forEach((btn) => {
    btn.classList.remove(
      "bg-slate-800/80",
      "border",
      "border-brand-gold/40",
      "text-brand-gold"
    );
    btn.classList.add("text-brand-textSecondary");
  });

  const activeBtnId = navMap[tabId];
  if (activeBtnId) {
    const btn = document.getElementById(activeBtnId);
    if (btn) {
      btn.classList.add(
        "bg-slate-800/80",
        "border",
        "border-brand-gold/40",
        "text-brand-gold"
      );
      btn.classList.remove("text-brand-textSecondary");
    }
  }

  document.getElementById("mobileNavMenu").classList.add("hidden");

  // Auto-resize charts if visible
  Object.values(AppState.chartInstances).forEach((c) => {
    if (c) c.resize();
  });
  window.scrollTo({ top: 0, behavior: "smooth" });
}

// =========================================================================
// API CLIENT ENGINE (FASTAPI BACKEND CONNECTION)
// =========================================================================
async function apiRequest(endpoint, options = {}) {
  const headers = {
    "Content-Type":
      options.body instanceof URLSearchParams
        ? "application/x-www-form-urlencoded"
        : "application/json",
    ...(options.headers || {}),
  };

  if (AppState.jwtToken) {
    headers["Authorization"] = "Bearer " + AppState.jwtToken;
  }

  const url = API_BASE + endpoint;
  try {
    const res = await fetch(url, { ...options, headers });
    const data = await res.json().catch(() => ({
      message: "Không thể giải mã phản hồi JSON từ máy chủ.",
    }));

    if (!res.ok) {
      const errMsg =
        data.message ||
        data.detail ||
        (data.error && data.error.message) ||
        `Lỗi HTTP ${res.status}`;
      throw new Error(errMsg);
    }

    // Mark backend as online
    setBackendStatus(true);
    return data;
  } catch (err) {
    // If connection refused, mark as offline
    if (
      err.name === "TypeError" ||
      err.message.includes("fetch") ||
      err.message.includes("Failed to fetch")
    ) {
      setBackendStatus(false);
    }
    throw err;
  }
}

function setBackendStatus(online) {
  API_ONLINE = online;
  const dot = document.getElementById("backendStatusDot");
  const text = document.getElementById("backendStatusText");
  const btn = document.getElementById("btnOpenApiConfig");
  const homeTag = document.getElementById("homeApiSyncTag");

  if (online) {
    dot.className = "w-2 h-2 rounded-full bg-emerald-400";
    text.textContent = "API đã kết nối";
    btn.className =
      "inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded text-[11px] font-mono transition border border-emerald-500/30 bg-emerald-950/40 text-emerald-300";
    if (homeTag) {
      homeTag.textContent = "● Đã đồng bộ API";
      homeTag.className = "text-[11px] font-mono text-emerald-400";
    }
  } else {
    dot.className = "w-2 h-2 rounded-full bg-amber-400";
    text.textContent = "API mất kết nối";
    btn.className =
      "inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded text-[11px] font-mono transition border border-amber-600/30 bg-amber-950/40 text-amber-300";
    if (homeTag) {
      homeTag.textContent = "○ Sẵn sàng kết nối khi Backend chạy";
      homeTag.className = "text-[11px] font-mono text-amber-400";
    }
  }
}

// Test API Connection on startup
async function checkBackendConnection() {
  try {
    const res = await apiRequest("/api/health");
    setBackendStatus(true);
    console.log("FastAPI Backend connection verified:", res);
  } catch (e) {
    setBackendStatus(false);
    console.warn(
      "Backend server at " + API_BASE + " not reachable yet:",
      e.message
    );
  }
}

// =========================================================================
// AUTHENTICATION & SESSION MANAGEMENT (Mục 2.7, 3.2)
// =========================================================================
function setAuthSession(user, token) {
  AppState.currentUser = user;
  AppState.jwtToken = token || "";
  AppState.currentRole = (user.role || "USER").toUpperCase();

  try {
    localStorage.setItem("gp_token", AppState.jwtToken);
    localStorage.setItem("gp_user", JSON.stringify(user));
  } catch (e) {
    console.warn(e);
  }

  updateAuthUI();
  showToast(
    `Đăng nhập thành công! Tài khoản: ${user.username} (${AppState.currentRole})`
  );
  loadPredictionHistory(); // Fetch user's history from backend
}

function clearAuthSession() {
  AppState.currentUser = null;
  AppState.predictionHistory = [];
  AppState.jwtToken = "";
  AppState.currentRole = "USER";

  try {
    localStorage.removeItem("gp_token");
    localStorage.removeItem("gp_user");
  } catch (e) {
    console.warn(e);
  }

  updateAuthUI();
  renderHistoryTable();
  switchTab("tabHome");
  showToast("Đã đăng xuất phiên làm việc.");
}

function updateAuthUI() {
  const unauthBlock = document.getElementById("unauthBlock");
  const authBlock = document.getElementById("authBlock");
  const userDropdownPanel = document.getElementById("userDropdownPanel");
  userDropdownPanel.classList.add("hidden");

  const navAdmin = document.getElementById("navBtnAdmin");
  const mNavAdmin = document.getElementById("mNavAdmin");
  const predictNotice = document.getElementById("predictAuthNotice");

  if (AppState.currentUser) {
    unauthBlock.classList.add("hidden");
    authBlock.classList.remove("hidden");

    document.getElementById("userNameDisplay").textContent =
      AppState.currentUser.username || AppState.currentUser.name || "User";
    document.getElementById("userEmailDisplay").textContent =
      AppState.currentUser.email || "user@example.com";
    document.getElementById("userAvatar").textContent = (
      AppState.currentUser.username || "U"
    )
      .charAt(0)
      .toUpperCase();

    const roleBadge = document.getElementById("userRoleBadge");
    if (AppState.currentRole === "ADMIN") {
      roleBadge.textContent = "ADMIN";
      roleBadge.className =
        "text-[9px] uppercase px-1 py-0.2 rounded font-semibold bg-amber-500/20 text-amber-300 border border-amber-600/30";
      navAdmin.classList.remove("hidden");
      mNavAdmin.classList.remove("hidden");
    } else {
      roleBadge.textContent = "USER";
      roleBadge.className =
        "text-[9px] uppercase px-1 py-0.2 rounded font-semibold bg-blue-500/20 text-blue-400";
      navAdmin.classList.add("hidden");
      mNavAdmin.classList.add("hidden");
    }

    if (predictNotice) {
      predictNotice.textContent =
        "Đã xác thực. Kết quả dự báo sẽ được lưu vào lịch sử cá nhân.";
    }
  } else {
    unauthBlock.classList.remove("hidden");
    authBlock.classList.add("hidden");
    navAdmin.classList.add("hidden");
    mNavAdmin.classList.add("hidden");

    if (predictNotice) {
      predictNotice.textContent =
        "Chưa đăng nhập. Có thể dự báo nhưng không lưu lịch sử.";
    }
  }

  // Sync Role Button styling
  const btnRoleUser = document.getElementById("btnRoleUser");
  const btnRoleAdmin = document.getElementById("btnRoleAdmin");
  const mBtnRoleUser = document.getElementById("mBtnRoleUser");
  const mBtnRoleAdmin = document.getElementById("mBtnRoleAdmin");

  if (AppState.currentRole === "ADMIN") {
    btnRoleAdmin.className =
      "px-2 py-0.5 rounded text-[11px] font-semibold bg-amber-500 text-slate-950 transition";
    btnRoleUser.className =
      "px-2 py-0.5 rounded text-[11px] font-semibold text-brand-textSecondary hover:text-white transition";
    mBtnRoleAdmin.className =
      "px-2.5 py-1 text-xs rounded bg-amber-500 text-slate-950 font-bold";
    mBtnRoleUser.className =
      "px-2.5 py-1 text-xs rounded text-brand-textSecondary font-medium";
  } else {
    btnRoleUser.className =
      "px-2 py-0.5 rounded text-[11px] font-semibold bg-brand-gold text-slate-950 transition";
    btnRoleAdmin.className =
      "px-2 py-0.5 rounded text-[11px] font-semibold text-brand-textSecondary hover:text-white transition";
    mBtnRoleUser.className =
      "px-2.5 py-1 text-xs rounded bg-brand-gold text-slate-950 font-bold";
    mBtnRoleAdmin.className =
      "px-2.5 py-1 text-xs rounded text-brand-textSecondary font-medium";
  }
}

// Client-side Password Strength Evaluator (Mục 3.2)
function evaluatePasswordStrength(password) {
  let score = 0;
  const rules = {
    len: password.length >= ValidationRules.passwordLen,
    upper: ValidationRules.hasUpper.test(password),
    lower: ValidationRules.hasLower.test(password),
    num: ValidationRules.hasNumber.test(password),
    special: ValidationRules.hasSpecial.test(password),
  };

  if (rules.len) score++;
  if (rules.upper) score++;
  if (rules.lower) score++;
  if (rules.num) score++;
  if (rules.special) score++;

  return { score, rules };
}

function updatePasswordMeter(password) {
  const { score, rules } = evaluatePasswordStrength(password);
  const bar = document.getElementById("passStrengthBar");
  const label = document.getElementById("passStrengthLabel");

  const updateRuleUI = (ruleId, passed) => {
    const el = document.getElementById(ruleId);
    if (passed) {
      el.className = "flex items-center gap-1 text-brand-profit font-medium";
      el.querySelector("i").className =
        "fa-solid fa-check text-[7px] text-brand-profit";
    } else {
      el.className = "flex items-center gap-1 text-slate-500";
      el.querySelector("i").className =
        "fa-solid fa-circle text-[5px] text-slate-600";
    }
  };

  updateRuleUI("ruleLen", rules.len);
  updateRuleUI("ruleUpper", rules.upper);
  updateRuleUI("ruleNum", rules.num);
  updateRuleUI("ruleSpecial", rules.special);

  if (!password) {
    bar.style.width = "0%";
    label.textContent = "Chưa nhập";
    label.className = "font-bold text-slate-500";
    return;
  }

  if (score <= 2) {
    bar.style.width = "25%";
    bar.className = "h-full transition-all duration-300 bg-rose-500";
    label.textContent = "Yếu";
    label.className = "font-bold text-rose-400";
  } else if (score === 3) {
    bar.style.width = "50%";
    bar.className = "h-full transition-all duration-300 bg-amber-500";
    label.textContent = "Trung bình";
    label.className = "font-bold text-amber-400";
  } else if (score === 4) {
    bar.style.width = "75%";
    bar.className = "h-full transition-all duration-300 bg-yellow-400";
    label.textContent = "Khá";
    label.className = "font-bold text-yellow-300";
  } else {
    bar.style.width = "100%";
    bar.className = "h-full transition-all duration-300 bg-emerald-500";
    label.textContent = "Mạnh & An toàn";
    label.className = "font-bold text-emerald-400";
  }
}

// =========================================================================
// API CALLS: GOLD DATA, PREDICTIONS & HISTORY (Mục 2.1, 2.8)
// =========================================================================
function renderPriceChart(rows) {
  if (typeof Chart === "undefined") return;
  const ctx = document.getElementById("priceChartCanvas");
  if (!ctx) return;
  if (AppState.chartInstances.priceChart)
    AppState.chartInstances.priceChart.destroy();

  AppState.chartInstances.priceChart = new Chart(ctx, {
    type: "line",
    data: {
      labels: rows.map((r) => r.date),
      datasets: [
        {
          label: AppState.unit || "Giá đóng cửa",
          data: rows.map((r) => r.close),
          borderColor: "#C5A059",
          backgroundColor: "rgba(197, 160, 89, 0.05)",
          borderWidth: 2,
          pointRadius: 1,
          tension: 0.2,
          fill: true,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { labels: { color: "#94A3B8", font: { size: 10 } } },
      },
      scales: {
        x: {
          grid: { color: "rgba(255, 255, 255, 0.03)" },
          ticks: { color: "#94A3B8", maxTicksLimit: 8 },
        },
        y: {
          grid: { color: "rgba(255, 255, 255, 0.03)" },
          ticks: {
            color: "#94A3B8",
            callback: (v) => Number(v).toLocaleString("vi-VN"),
          },
        },
      },
    },
  });
}

// =========================================================================
// EVENT LISTENERS & FORM SUBMISSIONS
// =========================================================================
document.addEventListener("DOMContentLoaded", async () => {
  // Verify the saved token; client-side roles cannot establish identity.
  try {
    AppState.jwtToken = localStorage.getItem("gp_token") || "";
    if (AppState.jwtToken) {
      AppState.currentUser = await apiRequest("/api/auth/me");
      AppState.currentRole = AppState.currentUser.role.toUpperCase();
    }
  } catch {
    AppState.currentUser = null;
    AppState.jwtToken = "";
    localStorage.removeItem("gp_token");
    localStorage.removeItem("gp_user");
  }

  updateAuthUI();
  checkBackendConnection();
  loadGoldCurrentAndHistory();
  loadPredictionHistory();

  // Navigation
  document
    .getElementById("navLogoBtn")
    .addEventListener("click", () => switchTab("tabHome"));
  document
    .getElementById("navBtnHome")
    .addEventListener("click", () => switchTab("tabHome"));
  document
    .getElementById("navBtnPrices")
    .addEventListener("click", () => switchTab("tabPrices"));
  document
    .getElementById("navBtnPredict")
    .addEventListener("click", () => switchTab("tabPredict"));
  document
    .getElementById("navBtnHistory")
    .addEventListener("click", () => switchTab("tabHistory"));
  document
    .getElementById("navBtnIntro")
    .addEventListener("click", () => switchTab("tabIntro"));
  document
    .getElementById("navBtnAdmin")
    .addEventListener("click", () => switchTab("tabAdmin"));

  // Mobile Nav
  document
    .getElementById("mNavHome")
    .addEventListener("click", () => switchTab("tabHome"));
  document
    .getElementById("mNavPrices")
    .addEventListener("click", () => switchTab("tabPrices"));
  document
    .getElementById("mNavPredict")
    .addEventListener("click", () => switchTab("tabPredict"));
  document
    .getElementById("mNavHistory")
    .addEventListener("click", () => switchTab("tabHistory"));
  document
    .getElementById("mNavIntro")
    .addEventListener("click", () => switchTab("tabIntro"));
  document
    .getElementById("mNavAdmin")
    .addEventListener("click", () => switchTab("tabAdmin"));

  document
    .getElementById("btnMobileNavToggle")
    .addEventListener("click", () => {
      document.getElementById("mobileNavMenu").classList.toggle("hidden");
    });

  // Hero Buttons
  document
    .getElementById("heroBtnPredict")
    .addEventListener("click", () => switchTab("tabPredict"));
  document
    .getElementById("heroBtnHistory")
    .addEventListener("click", () => switchTab("tabHistory"));
  document
    .getElementById("heroBtnIntro")
    .addEventListener("click", () => switchTab("tabIntro"));
  document
    .getElementById("btnJumpToHistory")
    .addEventListener("click", () => switchTab("tabHistory"));
  document
    .getElementById("btnRefreshGoldData")
    .addEventListener("click", () => {
      loadGoldCurrentAndHistory();
      showToast("Đang làm mới dữ liệu từ API...");
    });
  document.getElementById("btnRefreshHistory").addEventListener("click", () => {
    loadPredictionHistory();
  });
  document
    .getElementById("btnExportCSV")
    .addEventListener("click", exportHistoryToCSV);

  // Roles are supplied by the authenticated server session.
  ["btnRoleUser", "btnRoleAdmin", "mBtnRoleUser", "mBtnRoleAdmin"].forEach(
    (id) => {
      document.getElementById(id).hidden = true;
    }
  );

  // User Menu Dropdown
  document.getElementById("btnUserMenu").addEventListener("click", (e) => {
    e.stopPropagation();
    document.getElementById("userDropdownPanel").classList.toggle("hidden");
  });
  document.addEventListener("click", () => {
    document.getElementById("userDropdownPanel").classList.add("hidden");
  });

  document.getElementById("btnMenuProfile").addEventListener("click", () => {
    if (AppState.currentUser) {
      document.getElementById("profFullName").value =
        AppState.currentUser.full_name || "";
      document.getElementById("profEmail").value =
        AppState.currentUser.email || "";
      document.getElementById("profPhone").value = "";
    }
    openModal("modalProfile");
  });
  document
    .getElementById("btnMenuPassword")
    .addEventListener("click", () => openModal("modalPassword"));
  document
    .getElementById("btnMenuHistory")
    .addEventListener("click", () => switchTab("tabHistory"));
  document
    .getElementById("btnLogout")
    .addEventListener("click", clearAuthSession);

  // Auth Modals Openers & Closers
  document
    .getElementById("btnOpenLogin")
    .addEventListener("click", () => openModal("modalLogin"));
  document
    .getElementById("btnOpenRegister")
    .addEventListener("click", () => openModal("modalRegister"));

  document
    .getElementById("btnCloseLogin")
    .addEventListener("click", () => closeModal("modalLogin"));
  document
    .getElementById("btnCloseRegister")
    .addEventListener("click", () => closeModal("modalRegister"));
  document
    .getElementById("btnCloseProfile")
    .addEventListener("click", () => closeModal("modalProfile"));
  document
    .getElementById("btnClosePassword")
    .addEventListener("click", () => closeModal("modalPassword"));
  document
    .getElementById("btnCloseDetail")
    .addEventListener("click", () => closeModal("modalDetail"));
  document
    .getElementById("btnCloseDetailBottom")
    .addEventListener("click", () => closeModal("modalDetail"));
  document
    .getElementById("modalBackdrop")
    .addEventListener("click", closeAllModals);

  document
    .getElementById("btnSwitchToRegister")
    .addEventListener("click", () => {
      closeModal("modalLogin");
      openModal("modalRegister");
    });
  document.getElementById("btnSwitchToLogin").addEventListener("click", () => {
    closeModal("modalRegister");
    openModal("modalLogin");
  });

  // API Config Modal Handlers
  document.getElementById("btnOpenApiConfig").addEventListener("click", () => {
    document.getElementById("inputApiBaseUrl").value = API_BASE;
    document.getElementById("apiConfigStatus").textContent = API_ONLINE
      ? "Đã kết nối (Online)"
      : "Chưa kết nối (Offline)";
    document.getElementById("apiConfigStatus").className = API_ONLINE
      ? "font-mono text-emerald-400"
      : "font-mono text-rose-400";
    document.getElementById("apiConfigToken").textContent = AppState.jwtToken
      ? AppState.jwtToken.slice(0, 15) + "..."
      : "Chưa có JWT";
    openModal("modalApiConfig");
  });
  document
    .getElementById("btnCloseApiConfig")
    .addEventListener("click", () => closeModal("modalApiConfig"));

  document
    .getElementById("btnTestApiConnection")
    .addEventListener("click", async () => {
      const testUrl = document.getElementById("inputApiBaseUrl").value.trim();
      API_BASE = testUrl;
      const statusEl = document.getElementById("apiConfigStatus");
      statusEl.textContent = "Đang ping...";
      statusEl.className = "font-mono text-amber-400";
      try {
        const res = await apiRequest("/api/health");
        statusEl.textContent = "Thành công (200 OK)";
        statusEl.className = "font-mono text-emerald-400";
        showToast("Kết nối thành công đến FastAPI Backend!");
      } catch (e) {
        statusEl.textContent = "Thất bại: " + e.message;
        statusEl.className = "font-mono text-rose-400";
        showToast("Không thể kết nối đến máy chủ: " + e.message, "error");
      }
    });

  document.getElementById("btnSaveApiConfig").addEventListener("click", () => {
    API_BASE = document.getElementById("inputApiBaseUrl").value.trim();
    closeModal("modalApiConfig");
    showToast("Đã lưu địa chỉ API: " + API_BASE);
    loadGoldCurrentAndHistory();
  });

  // Password Toggles
  const setupToggle = (btnId, inputId) => {
    document.getElementById(btnId).addEventListener("click", () => {
      const input = document.getElementById(inputId);
      const icon = document.getElementById(btnId).querySelector("i");
      if (input.type === "password") {
        input.type = "text";
        icon.className = "fa-solid fa-eye-slash";
      } else {
        input.type = "password";
        icon.className = "fa-solid fa-eye";
      }
    });
  };
  setupToggle("btnToggleLoginPass", "loginPassword");
  setupToggle("btnToggleRegPass", "regPassword");

  document.getElementById("regPassword").addEventListener("input", (e) => {
    updatePasswordMeter(e.target.value);
  });

  // -----------------------------------------------------------------------
  // 1. FORM ĐĂNG NHẬP (KẾT NỐI POST /api/auth/login)
  // -----------------------------------------------------------------------
  document.getElementById("formLogin").addEventListener("submit", async (e) => {
    e.preventDefault();
    const usernameInput = document.getElementById("loginUsername");
    const passInput = document.getElementById("loginPassword");
    const errUser = document.getElementById("errLoginUsername");
    const errPass = document.getElementById("errLoginPassword");
    const btn = document.getElementById("btnSubmitLogin");

    errUser.classList.add("hidden");
    errPass.classList.add("hidden");

    const username = usernameInput.value.trim();
    const password = passInput.value;

    if (!username) {
      errUser.textContent = "Vui lòng nhập tên đăng nhập.";
      errUser.classList.remove("hidden");
      return;
    }
    if (!password) {
      errPass.textContent = "Vui lòng nhập mật khẩu.";
      errPass.classList.remove("hidden");
      return;
    }

    btn.disabled = true;
    btn.textContent = "Đang xác thực qua API...";

    try {
      const res = await apiRequest("/api/auth/login", {
        method: "POST",
        body: new URLSearchParams({ username, password }),
      });
      AppState.jwtToken = res.access_token;
      const user = await apiRequest("/api/auth/me");
      setAuthSession(user, res.access_token);
      closeModal("modalLogin");
    } catch (apiErr) {
      AppState.jwtToken = "";
      errPass.textContent = apiErr.message;
      errPass.classList.remove("hidden");
    } finally {
      btn.disabled = false;
      btn.textContent = "Xác Nhận Đăng Nhập";
    }
  });

  // -----------------------------------------------------------------------
  // 2. FORM ĐĂNG KÝ (KẾT NỐI POST /api/auth/register & REGEX VALIDATION)
  // -----------------------------------------------------------------------
  document
    .getElementById("formRegister")
    .addEventListener("submit", async (e) => {
      e.preventDefault();
      let isValid = true;

      const uInput = document.getElementById("regUsername");
      const eInput = document.getElementById("regEmail");
      const passInput = document.getElementById("regPassword");
      const confInput = document.getElementById("regConfirmPassword");
      const btn = document.getElementById("btnSubmitRegister");

      const errU = document.getElementById("errRegUsername");
      const errE = document.getElementById("errRegEmail");
      const errP = document.getElementById("errRegPhone");
      const errPass = document.getElementById("errRegPassword");
      const errConf = document.getElementById("errRegConfirmPassword");

      [errU, errE, errP, errPass, errConf].forEach((el) =>
        el.classList.add("hidden")
      );

      // Client-side Validation RegEx (Mục 3.2)
      const username = uInput.value.trim();
      if (!username || username.length < 3) {
        errU.textContent = "Tên đăng nhập phải có ít nhất 3 ký tự.";
        errU.classList.remove("hidden");
        isValid = false;
      }

      const email = eInput.value.trim();
      if (!email) {
        errE.textContent = "Vui lòng nhập email.";
        errE.classList.remove("hidden");
        isValid = false;
      } else if (!ValidationRules.emailRegex.test(email)) {
        errE.textContent =
          "Định dạng email không hợp lệ (ví dụ: user@example.com).";
        errE.classList.remove("hidden");
        isValid = false;
      }

      const password = passInput.value;
      const { score, rules } = evaluatePasswordStrength(password);
      if (!password) {
        errPass.textContent = "Vui lòng nhập mật khẩu.";
        errPass.classList.remove("hidden");
        isValid = false;
      } else if (!rules.len) {
        errPass.textContent = "Mật khẩu phải dài ít nhất 8 ký tự.";
        errPass.classList.remove("hidden");
        isValid = false;
      } else if (score < 3) {
        errPass.textContent =
          "Mật khẩu chưa đủ mạnh. Cần kết hợp chữ hoa, chữ số hoặc ký tự đặc biệt.";
        errPass.classList.remove("hidden");
        isValid = false;
      }

      const confirmPass = confInput.value;
      if (!confirmPass) {
        errConf.textContent = "Vui lòng xác nhận mật khẩu.";
        errConf.classList.remove("hidden");
        isValid = false;
      } else if (confirmPass !== password) {
        errConf.textContent = "Mật khẩu xác nhận không trùng khớp.";
        errConf.classList.remove("hidden");
        isValid = false;
      }

      if (!isValid) return;

      btn.disabled = true;
      btn.textContent = "Đang đăng ký qua API...";

      try {
        // GỌI THỰC TẾ API POST /api/auth/register
        const res = await apiRequest("/api/auth/register", {
          method: "POST",
          body: JSON.stringify({ username, email, password }),
        });

        showToast(res.message || "Đăng ký thành công!");
        closeModal("modalRegister");
        openModal("modalLogin");
        document.getElementById("loginUsername").value = username;
      } catch (apiErr) {
        errE.textContent = apiErr.message;
        errE.classList.remove("hidden");
      } finally {
        btn.disabled = false;
        btn.textContent = "Hoàn Tất Đăng Ký Tài Khoản";
      }
    });

  // -----------------------------------------------------------------------
  // 3. THỰC HIỆN DỰ BÁO (KẾT NỐI POST /api/predict)
  // -----------------------------------------------------------------------
  document
    .getElementById("predictionForm")
    .addEventListener("submit", submitPrediction);

  // 4. ADMIN & PROFILE API HANDLERS
  // -----------------------------------------------------------------------
  const consoleLog = document.getElementById("adminConsoleLog");
  const adminTableContainer = document.getElementById("adminTableContainer");

  function createActionBtn(label, extraClass, onClick) {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.textContent = label;
    btn.className = `px-2 py-1 rounded text-[11px] font-medium transition ${extraClass}`;
    btn.addEventListener("click", onClick);
    return btn;
  }

  function renderAdminUsersTable(items) {
    adminTableContainer.textContent = "";
    if (!items || items.length === 0) {
      const empty = document.createElement("p");
      empty.className = "text-xs text-brand-textSecondary";
      empty.textContent = "Chưa có người dùng nào.";
      adminTableContainer.appendChild(empty);
      return;
    }

    const wrap = document.createElement("div");
    wrap.className = "overflow-x-auto border border-brand-border rounded-lg";
    const table = document.createElement("table");
    table.className = "w-full text-left text-xs";

    const thead = document.createElement("thead");
    thead.className = "bg-slate-900/80 text-brand-textSecondary";
    const headRow = document.createElement("tr");
    ["ID", "Username", "Họ tên", "Email", "Role", "Trạng thái", "Thao tác"].forEach(
      (col) => {
        const th = document.createElement("th");
        th.className = "px-3 py-2 font-semibold";
        th.textContent = col;
        headRow.appendChild(th);
      }
    );
    thead.appendChild(headRow);
    table.appendChild(thead);

    const tbody = document.createElement("tbody");
    tbody.className = "divide-y divide-brand-border/60";
    items.forEach((u) => {
      const tr = document.createElement("tr");
      [
        String(u.id),
        u.username || "",
        u.full_name || "—",
        u.email || "—",
        u.role || "user",
        u.is_active ? "Hoạt động" : "Đã khóa",
      ].forEach((val) => {
        const td = document.createElement("td");
        td.className = "px-3 py-2 text-slate-200 whitespace-nowrap";
        td.textContent = val;
        tr.appendChild(td);
      });

      const actionTd = document.createElement("td");
      actionTd.className = "px-3 py-2 flex items-center gap-1.5 whitespace-nowrap";
      const nextRole = u.role === "admin" ? "user" : "admin";
      actionTd.appendChild(
        createActionBtn(
          `Đổi → ${nextRole}`,
          "bg-slate-800 hover:bg-slate-700 text-brand-gold border border-brand-border",
          async () => {
            try {
              const updated = await apiRequest(`/api/admin/users/${u.id}`, {
                method: "PATCH",
                body: JSON.stringify({ role: nextRole }),
              });
              consoleLog.textContent = JSON.stringify(updated, null, 2);
              showToast(`Đã đổi quyền ${u.username} thành ${nextRole}`);
              document.getElementById("btnFetchAdminUsers").click();
            } catch (err) {
              showToast(err.message, "error");
            }
          }
        )
      );
      actionTd.appendChild(
        createActionBtn(
          u.is_active ? "Khóa" : "Mở khóa",
          u.is_active
            ? "bg-rose-950/70 hover:bg-rose-900 text-rose-300 border border-rose-800/60"
            : "bg-emerald-950/70 hover:bg-emerald-900 text-emerald-300 border border-emerald-800/60",
          async () => {
            try {
              const updated = await apiRequest(`/api/admin/users/${u.id}`, {
                method: "PATCH",
                body: JSON.stringify({ is_active: !u.is_active }),
              });
              consoleLog.textContent = JSON.stringify(updated, null, 2);
              showToast(
                `${updated.is_active ? "Đã mở khóa" : "Đã khóa"} ${u.username}`
              );
              document.getElementById("btnFetchAdminUsers").click();
            } catch (err) {
              showToast(err.message, "error");
            }
          }
        )
      );
      tr.appendChild(actionTd);
      tbody.appendChild(tr);
    });
    table.appendChild(tbody);
    wrap.appendChild(table);
    adminTableContainer.appendChild(wrap);
  }

  function renderAdminModelsTable(models) {
    adminTableContainer.textContent = "";
    if (!models || models.length === 0) {
      const empty = document.createElement("p");
      empty.className = "text-xs text-brand-textSecondary";
      empty.textContent = "Chưa có model nào được đăng ký.";
      adminTableContainer.appendChild(empty);
      return;
    }

    const wrap = document.createElement("div");
    wrap.className = "overflow-x-auto border border-brand-border rounded-lg";
    const table = document.createElement("table");
    table.className = "w-full text-left text-xs";

    const thead = document.createElement("thead");
    thead.className = "bg-slate-900/80 text-brand-textSecondary";
    const headRow = document.createElement("tr");
    ["ID", "Tên model", "Thuật toán", "Phiên bản", "Trạng thái", "Thao tác"].forEach(
      (col) => {
        const th = document.createElement("th");
        th.className = "px-3 py-2 font-semibold";
        th.textContent = col;
        headRow.appendChild(th);
      }
    );
    thead.appendChild(headRow);
    table.appendChild(thead);

    const tbody = document.createElement("tbody");
    tbody.className = "divide-y divide-brand-border/60";
    models.forEach((m) => {
      const tr = document.createElement("tr");
      [
        String(m.id),
        m.name || "",
        m.algorithm || "",
        m.version || "",
        m.is_active ? "Đang kích hoạt" : "Tắt",
      ].forEach((val) => {
        const td = document.createElement("td");
        td.className = "px-3 py-2 text-slate-200 whitespace-nowrap";
        td.textContent = val;
        tr.appendChild(td);
      });

      const actionTd = document.createElement("td");
      actionTd.className = "px-3 py-2 whitespace-nowrap";
      if (m.is_active) {
        const badge = document.createElement("span");
        badge.className = "text-[11px] text-emerald-400 font-semibold";
        badge.textContent = "Mặc định";
        actionTd.appendChild(badge);
      } else {
        actionTd.appendChild(
          createActionBtn(
            "Đặt mặc định",
            "bg-brand-gold hover:bg-brand-goldLight text-slate-950 font-semibold",
            async () => {
              try {
                const updated = await apiRequest(`/api/admin/models/${m.id}`, {
                  method: "PATCH",
                  body: JSON.stringify({ is_active: true }),
                });
                consoleLog.textContent = JSON.stringify(updated, null, 2);
                showToast(`Đã kích hoạt model ${m.name}`);
                document.getElementById("btnTestAdminToken").click();
                if (typeof loadGoldCurrentAndHistory === "function") {
                  loadGoldCurrentAndHistory();
                }
              } catch (err) {
                showToast(err.message, "error");
              }
            }
          )
        );
      }
      tr.appendChild(actionTd);
      tbody.appendChild(tr);
    });
    table.appendChild(tbody);
    wrap.appendChild(table);
    adminTableContainer.appendChild(wrap);
  }

  document
    .getElementById("btnFetchAdminUsers")
    .addEventListener("click", async () => {
      consoleLog.textContent = "Đang gọi GET /api/admin/users...";
      try {
        const res = await apiRequest("/api/admin/users");
        consoleLog.textContent = JSON.stringify(res, null, 2);
        renderAdminUsersTable(res.items || []);
        showToast("Tải danh sách users thành công!");
      } catch (e) {
        consoleLog.textContent = `Lỗi: ${e.message}\n(Lưu ý: Chỉ tài khoản có vai trò 'admin' mới được cấp quyền truy cập)`;
        showToast("Lỗi API Admin: " + e.message, "error");
      }
    });

  document
    .getElementById("btnTestAdminToken")
    .addEventListener("click", async () => {
      consoleLog.textContent = "Đang gọi GET /api/admin/models...";
      try {
        const res = await apiRequest("/api/admin/models");
        consoleLog.textContent = JSON.stringify(res, null, 2);
        renderAdminModelsTable(Array.isArray(res) ? res : []);
        showToast("Tải danh sách models thành công!");
      } catch (e) {
        consoleLog.textContent = `Lỗi: ${e.message}`;
        showToast(e.message, "error");
      }
    });

  document
    .getElementById("formAdminAddPrice")
    .addEventListener("submit", async (event) => {
      event.preventDefault();
      const payload = {
        gold_type: document.getElementById("adminPriceType").value,
        date: document.getElementById("adminPriceDate").value,
        open: Number(document.getElementById("adminPriceOpen").value),
        high: Number(document.getElementById("adminPriceHigh").value),
        low: Number(document.getElementById("adminPriceLow").value),
        close: Number(document.getElementById("adminPriceClose").value),
      };
      if (!payload.date || Number.isNaN(payload.close)) {
        showToast("Vui lòng nhập đầy đủ ngày và giá OHLC hợp lệ.", "error");
        return;
      }
      consoleLog.textContent = "Đang gọi POST /api/admin/prices...";
      try {
        const res = await apiRequest("/api/admin/prices", {
          method: "POST",
          body: JSON.stringify(payload),
        });
        consoleLog.textContent = JSON.stringify(res, null, 2);
        showToast("Đã thêm dữ liệu giá vàng!");
        event.target.reset();
        if (typeof loadGoldCurrentAndHistory === "function") {
          loadGoldCurrentAndHistory();
        }
      } catch (e) {
        consoleLog.textContent = `Lỗi: ${e.message}`;
        showToast("Lỗi thêm giá: " + e.message, "error");
      }
    });

  document
    .getElementById("btnCheckHealth")
    .addEventListener("click", async () => {
      consoleLog.textContent = "Đang gọi GET /api/health...";
      try {
        const res = await apiRequest("/api/health");
        consoleLog.textContent = JSON.stringify(res, null, 2);
        showToast(
          res.db ? "Database phản hồi." : "Database chưa sẵn sàng.",
          res.db ? "success" : "error"
        );
      } catch (e) {
        consoleLog.textContent = `Lỗi: ${e.message}`;
        showToast(e.message, "error");
      }
    });

  document
    .getElementById("formProfile")
    .addEventListener("submit", async (event) => {
      event.preventDefault();
      const fullName = document.getElementById("profFullName").value.trim();
      const email = document.getElementById("profEmail").value.trim();
      try {
        const updated = await apiRequest("/api/auth/profile", {
          method: "PATCH",
          body: JSON.stringify({
            full_name: fullName || null,
            email: email || null,
          }),
        });
        AppState.currentUser = updated;
        updateAuthUI();
        closeModal("modalProfile");
        showToast("Cập nhật hồ sơ thành công!");
      } catch (e) {
        showToast("Lỗi cập nhật hồ sơ: " + e.message, "error");
      }
    });

  document
    .getElementById("formChangePassword")
    .addEventListener("submit", async (event) => {
      event.preventDefault();
      const currentPassword = document.getElementById("pwdOld").value;
      const newPassword = document.getElementById("pwdNew").value;
      const confirmPassword = document.getElementById("pwdConfirm").value;

      if (!currentPassword || newPassword.length < 8) {
        showToast(
          "Vui lòng nhập mật khẩu hiện tại và mật khẩu mới tối thiểu 8 ký tự.",
          "error"
        );
        return;
      }
      if (newPassword !== confirmPassword) {
        showToast("Xác nhận mật khẩu mới không khớp.", "error");
        return;
      }

      try {
        const res = await apiRequest("/api/auth/change-password", {
          method: "POST",
          body: JSON.stringify({
            current_password: currentPassword,
            new_password: newPassword,
          }),
        });
        event.target.reset();
        closeModal("modalPassword");
        showToast(res.message || "Đổi mật khẩu thành công!");
      } catch (e) {
        showToast("Lỗi đổi mật khẩu: " + e.message, "error");
      }
    });

  // Filter events on History
  document
    .getElementById("historySearchInput")
    .addEventListener("input", renderHistoryTable);
  document
    .getElementById("filterTrend")
    .addEventListener("change", renderHistoryTable);

  ["btnQuickUserLogin", "btnQuickAdminLogin"].forEach(
    (id) => (document.getElementById(id).hidden = true)
  );
  document.getElementById("chartDependencyNotice").hidden =
    typeof Chart !== "undefined";
});
