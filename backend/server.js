// 1. Import các thư viện cần thiết
const express = require("express");
const dotenv = require("dotenv");
const cors = require("cors"); // Để cho phép Front-end (Vue) truy cập API
const db = require("./db"); // Import kết nối DB bạn đã tạo
// const courtRoutes = require('./routes/courts'); // Sẽ dùng sau này

// 2. Load biến môi trường từ .env
dotenv.config({ path: "./.env" });

const app = express();
const port = process.env.PORT || 3000;

// 3. Thiết lập Middleware
app.use(cors()); // Cho phép Front-end truy cập (Trong môi trường production cần cấu hình chi tiết hơn)
app.use(express.json()); // Middleware để đọc JSON từ body request (rất quan trọng cho API POST/PUT)

// 4. Định tuyến API Thử nghiệm
app.get("/", (req, res) => {
  res.send("Chào mừng đến với API Đặt Sân Pickleball!");
});

// API thử nghiệm kết nối DB
app.get("/api/test-db", async (req, res) => {
  try {
    // Ví dụ: truy vấn thời gian hiện tại từ PostgreSQL
    const result = await db.query("SELECT NOW() AS now");
    res.status(200).json({
      message: "Kết nối PostgreSQL thành công!",
      timestamp: result.rows[0].now,
    });
  } catch (error) {
    console.error("Lỗi khi truy vấn DB:", error);
    res.status(500).json({
      message: "Lỗi kết nối hoặc truy vấn cơ sở dữ liệu.",
      error: error.message,
    });
  }
});

// 5. Khởi động Server
app.listen(port, () => {
  console.log(`Server đang chạy tại http://localhost:${port}`);
  console.log(`Kiểm tra API tại: http://localhost:${port}/api/test-db`);
});
