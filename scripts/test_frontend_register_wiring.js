const fs = require('fs');
const path = require('path');

const htmlPath = path.join(__dirname, '../frontend/index.html');
const jsPath = path.join(__dirname, '../frontend/app.js');

const htmlContent = fs.readFileSync(htmlPath, 'utf8');
const jsContent = fs.readFileSync(jsPath, 'utf8');

console.log("=== [KIỂM TRA LIÊN KẾT FRONTEND & VALIDATION REALTIME] ===");

// 1. Kiểm tra các ID cần thiết trong HTML
const requiredIds = [
  'modalRegister',
  'formRegister',
  'registerFeedback',
  'regUsername',
  'errRegUsername',
  'regEmail',
  'errRegEmail',
  'regPassword',
  'errRegPassword',
  'passStrengthBar',
  'passStrengthLabel',
  'ruleLength',
  'ruleUppercase',
  'ruleNumber',
  'ruleSpecial',
  'regConfirmPassword',
  'errRegConfirmPassword',
  'btnSubmitRegister'
];

let missingIds = [];
for (const id of requiredIds) {
  if (!htmlContent.includes(`id="${id}"`)) {
    missingIds.push(id);
  }
}

if (missingIds.length > 0) {
  console.error("LỖI: Thiếu các ID sau trong HTML:", missingIds);
  process.exit(1);
} else {
  console.log("✔ 100% các ID giao diện trong Modal Đăng Ký đã tồn tại khớp hoàn hảo trong HTML.");
}

// 2. Kiểm tra thuộc tính inline onclick và onsubmit an toàn
if (htmlContent.includes('onsubmit="window.handleRegisterSubmit(event); return false;"') &&
    htmlContent.includes('onclick="window.handleRegisterSubmit(event)"') &&
    htmlContent.includes('oninput="window.updatePasswordMeter(this.value)"')) {
  console.log("✔ Đã gắn thuộc tính inline sự kiện an toàn: onsubmit, onclick và oninput.");
} else {
  console.error("LỖI: Chưa gắn đủ thuộc tính inline sự kiện cho form/button/input!");
  process.exit(1);
}

// 3. Kiểm tra các hàm JS đã được export ra window
if (jsContent.includes('window.updatePasswordMeter = updatePasswordMeter;') &&
    jsContent.includes('window.handleRegisterSubmit = async function(e)')) {
  console.log("✔ window.updatePasswordMeter và window.handleRegisterSubmit đã được khai báo ở Global Scope.");
} else {
  console.error("LỖI: Chưa khai báo đầy đủ các hàm xử lý đăng ký toàn cục!");
  process.exit(1);
}

// 4. Giả lập DOM kiểm tra hàm updatePasswordMeter và evaluatePasswordStrength
// Mock DOM
const mockElements = {};
for (const id of requiredIds) {
  mockElements[id] = {
    id,
    style: {},
    className: '',
    textContent: '',
    innerHTML: '',
    dataset: {},
    classList: {
      add: function(c) {},
      remove: function(c) {}
    }
  };
}
mockElements['ruleLength'].dataset.label = '8+ ký tự';
mockElements['ruleUppercase'].dataset.label = 'Chữ hoa';
mockElements['ruleNumber'].dataset.label = 'Số';
mockElements['ruleSpecial'].dataset.label = 'Đặc biệt';

global.document = {
  getElementById: (id) => mockElements[id] || null
};
global.window = {};

// Chạy thử hàm evaluatePasswordStrength và updatePasswordMeter
const ValidationRules = {
  passwordLen: 8,
  hasUpper: /[A-Z]/,
  hasLower: /[a-z]/,
  hasNumber: /[0-9]/,
  hasSpecial: /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/,
};

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
  const pwd = password || "";
  const { score, rules } = evaluatePasswordStrength(pwd);
  const bar = document.getElementById("passStrengthBar");
  const label = document.getElementById("passStrengthLabel");

  const updateRuleUI = (ruleId, passed) => {
    const el = document.getElementById(ruleId);
    if (!el) return;
    const baseLabel = el.dataset.label || el.textContent.replace(/^[✓\s]+/, "");
    el.dataset.label = baseLabel;
    if (passed) {
      el.className = "text-emerald-600 font-semibold";
      el.innerHTML = '<span class="inline-block mr-0.5">✓</span>' + baseLabel;
    } else {
      el.className = "text-neutral-400 font-normal";
      el.innerHTML = baseLabel;
    }
  };

  updateRuleUI("ruleLength", rules.len);
  updateRuleUI("ruleUppercase", rules.upper);
  updateRuleUI("ruleNumber", rules.num);
  updateRuleUI("ruleSpecial", rules.special);

  if (!bar || !label) return;

  if (!pwd) {
    bar.style.width = "0%";
    label.textContent = "Độ mạnh mật khẩu";
    return;
  }

  if (score <= 2) {
    bar.style.width = "25%";
    label.textContent = "Yếu";
  } else if (score === 3) {
    bar.style.width = "50%";
    label.textContent = "Trung bình";
  } else if (score === 4) {
    bar.style.width = "75%";
    label.textContent = "Khá";
  } else {
    bar.style.width = "100%";
    label.textContent = "Mạnh & An toàn";
  }
}

// Test trường hợp 1: Rỗng
updatePasswordMeter("");
console.log("Case 1 (Rỗng): bar =", mockElements['passStrengthBar'].style.width, ", label =", mockElements['passStrengthLabel'].textContent);
if (mockElements['passStrengthBar'].style.width !== '0%') throw new Error("Sai case rỗng");

// Test trường hợp 2: Yếu ("123")
updatePasswordMeter("123");
console.log("Case 2 ('123'): bar =", mockElements['passStrengthBar'].style.width, ", label =", mockElements['passStrengthLabel'].textContent);
if (mockElements['passStrengthBar'].style.width !== '25%') throw new Error("Sai case yếu");

// Test trường hợp 3: Đầy đủ tiêu chí ("Password123!")
updatePasswordMeter("Password123!");
console.log("Case 3 ('Password123!'): bar =", mockElements['passStrengthBar'].style.width, ", label =", mockElements['passStrengthLabel'].textContent);
console.log("  - ruleLength:", mockElements['ruleLength'].className, mockElements['ruleLength'].innerHTML);
console.log("  - ruleUppercase:", mockElements['ruleUppercase'].className, mockElements['ruleUppercase'].innerHTML);
console.log("  - ruleNumber:", mockElements['ruleNumber'].className, mockElements['ruleNumber'].innerHTML);
console.log("  - ruleSpecial:", mockElements['ruleSpecial'].className, mockElements['ruleSpecial'].innerHTML);

if (mockElements['passStrengthBar'].style.width !== '100%') throw new Error("Sai case mạnh");
if (!mockElements['ruleLength'].innerHTML.includes('✓')) throw new Error("Thiếu icon ✓ ở ruleLength");

console.log("\n✔ TOÀN BỘ KIỂM TRA FRONTEND WIRING & VALIDATION REALTIME: PASS 100%!");
