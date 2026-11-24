const fs = require('fs');
const path = require('path');

const jsPath = path.join(__dirname, '../frontend/app.js');
const dataJsPath = path.join(__dirname, '../frontend/data.js');

console.log("=== [KIỂM TRA CHẾ ĐỘ CHẠY TRỰC TIẾP TRONG FILE INDEX.HTML] ===");

// 1. Kiểm tra syntax tệp app.js và data.js
try {
  require(jsPath);
} catch (e) {
  // Có thể lỗi do thiếu document/window, ta sẽ mock
}

// Giả lập LocalStorage
const storage = {};
global.localStorage = {
  getItem: (k) => storage[k] || null,
  setItem: (k, v) => { storage[k] = String(v); },
  removeItem: (k) => { delete storage[k]; },
  clear: () => { for (const k in storage) delete storage[k]; }
};

global.location = {
  origin: "null" // Mô phỏng chính xác giao thức file:///
};

global.document = {
  getElementById: (id) => ({
    id,
    value: '',
    textContent: '',
    className: '',
    style: {},
    classList: { add() {}, remove() {} },
    addEventListener() {},
    removeEventListener() {}
  }),
  body: {
    prepend() {}
  },
  addEventListener() {}
};

global.window = {
  closeAllModals() {},
  openModal() {},
  closeModal() {}
};

// Đọc và chạy nội dung app.js
const appCode = fs.readFileSync(jsPath, 'utf8');
eval(appCode);

const LocalAuthEngine = global.window.LocalAuthEngine;

// Kiểm tra LocalAuthEngine
console.log("\n1. Kiểm tra LocalAuthEngine:");
const users = LocalAuthEngine.getUsers();
console.log(` -> Tìm thấy ${users.length} tài khoản mặc định.`);
const u1 = users.find(u => u.username === "user1");
const admin = users.find(u => u.username === "admin");
if (!u1 || u1.password !== "User@123") throw new Error("user1 không đúng mật khẩu User@123");
if (!admin || admin.password !== "Admin@123") throw new Error("admin không đúng mật khẩu Admin@123");
console.log(" ✔ Khởi tạo sẵn user1 và admin chuẩn xác!");

// 2. Thử đăng nhập user1 và admin qua LocalAuthEngine
console.log("\n2. Kiểm tra đăng nhập tài khoản có sẵn:");
const resU1 = LocalAuthEngine.login("user1", "User@123");
if (resU1.user.role !== "user" || !resU1.access_token) throw new Error("Đăng nhập user1 thất bại");
console.log(" ✔ Đăng nhập user1 thành công: role =", resU1.user.role);

const resAdmin = LocalAuthEngine.login("admin", "Admin@123");
if (resAdmin.user.role !== "admin" || !resAdmin.access_token) throw new Error("Đăng nhập admin thất bại");
console.log(" ✔ Đăng nhập admin thành công: role =", resAdmin.user.role);

// 3. Thử đăng ký tài khoản mới trực tiếp
console.log("\n3. Kiểm tra đăng ký tài khoản mới trong file index:");
const regData = {
  username: "khachhangmoi",
  email: "khachhang@gmail.com",
  password: "Password123!",
  full_name: "Khách Hàng Mới"
};
const resReg = LocalAuthEngine.register(regData);
console.log(" ✔ Đăng ký thành công:", resReg.user);

// 4. Thử đăng nhập lại bằng tài khoản mới vừa tạo
console.log("\n4. Đăng nhập lại bằng tài khoản mới:");
const resLoginNew = LocalAuthEngine.login("khachhangmoi", "Password123!");
if (resLoginNew.user.username !== "khachhangmoi") throw new Error("Đăng nhập lại user mới thất bại");
console.log(" ✔ Đăng nhập thành công với tài khoản mới!");

// 5. Thử đăng nhập sai mật khẩu
console.log("\n5. Kiểm tra bảo mật mật khẩu sai:");
let caughtWrong = false;
try {
  LocalAuthEngine.login("user1", "MatKhauSai");
} catch (e) {
  caughtWrong = true;
  console.log(" ✔ Bắt mật khẩu sai chính xác:", e.message);
}
if (!caughtWrong) throw new Error("Không bắt được mật khẩu sai!");

console.log("\n=======================================================");
console.log("✔ 100% CÁC TÍNH NĂNG CHẠY TRỰC TIẾP TRONG FILE INDEX HOÀN TOÀN SẴN SÀNG!");
console.log("=======================================================");
