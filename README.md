# 🤖 Gemini CLI Chatbot – Zero X Edition

Một ứng dụng chatbot sử dụng **Gemini AI của Google**, chạy trong **giao diện dòng lệnh** với hiệu ứng như game. Bạn có thể trò chuyện, thay đổi theme, lưu lịch sử và tận hưởng hiệu ứng chữ động cực ngầu!

---

## ✨ Tính năng

- 🎮 Giao diện chọn menu bằng mũi tên `↑ ↓` (InquirerPy)
- 🎨 Đổi theme màu trong cài đặt
- 🧠 Kết nối trực tiếp API Gemini 2.0 Flash
- ⌨️ Hiệu ứng chữ động với `terminal-text-effects`
- 🕘 Hiển thị thời gian từng tin nhắn
- 💾 Hỗ trợ lưu/hiển thị lịch sử trò chuyện

---

## 🧰 Cài đặt

### 1. Clone dự án

```bash
git clone https://github.com/your-username/gemini-cli-chatbot.git
cd gemini-cli-chatbot
```

2. Tạo môi trường ảo (khuyến nghị)

```bash
python -m venv venv
source venv/bin/activate  # Hoặc venv\Scripts\activate trên Windows
```

3. Cài đặt thư viện

```bash
pip install -r requirements.txt
```

4. Tạo file .env trong thư mục gốc, thêm API key của bạn:

```bash
GEMINI_API_KEY=your_gemini_api_key_here
```

Chạy ứng dụng

```bash
python main.py
```

Hình ảnh
