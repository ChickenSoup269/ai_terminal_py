import os
import time
from InquirerPy import inquirer
from pyfiglet import Figlet
from dotenv import load_dotenv
from colorama import Fore, init
from terminaltexteffects.effects.effect_middleout import MiddleOut
import google.generativeai as genai
from datetime import datetime
from pathlib import Path

# Kiểm tra và hỏi API Key nếu chưa có
def check_api_key():
    env_path = Path(".env")

    if not env_path.exists():
        with open(env_path, "w") as f:
            pass  # Tạo file nếu chưa có

    load_dotenv()
    current_key = os.getenv("GEMINI_API_KEY")

    if not current_key:
        print(Fore.CYAN + "🔐 Bạn chưa thiết lập API Key cho Gemini.")
        new_key = input("👉 Nhập API Key của bạn: ").strip()
        model_name = input("🤖 Nhập tên model AI (vd: gemini-2.0): ").strip()

        with open(env_path, "a", encoding="utf-8") as f:
            f.write(f"GEMINI_API_KEY={new_key}\n")
            f.write(f"GEMINI_MODEL={model_name}\n")

        print(Fore.GREEN + "✅ Đã lưu API Key và model vào file .env!\n Vui lòng khởi động lại.")
        time.sleep(1)
        exit()

    # Nạp lại sau khi lưu
    load_dotenv()

# Init
init(autoreset=True)
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = os.getenv("GEMINI_MODEL")
genai.configure(api_key=API_KEY)

# Hiển thị tiêu đề bằng hiệu ứng terminal-text-effects
def print_banner():
    os.system("cls" if os.name == "nt" else "clear")
    fig = Figlet(font='big')
    ascii_text = fig.renderText("Gemini AI")
    
    # Hiệu ứng chữ 
    effect = MiddleOut(ascii_text)
    with effect.terminal_output() as terminal:
        for frame in effect:
            terminal.print(frame)
    print(Fore.YELLOW + "Phiên bản: 1.0.0\n")

# Hiệu ứng loading
def loading(msg="Đang tải", dots=3):
    print(Fore.YELLOW + msg, end="", flush=True)
    for _ in range(dots):
        print(".", end="", flush=True)
        time.sleep(0.3)
    print()

# Trò chuyện
def start_chat():
    model = genai.GenerativeModel(MODEL_NAME)
    chat = model.start_chat(history=[])

    while True:
        user_input = input(Fore.WHITE + f"👤 Bạn ({datetime.now().strftime('%H:%M')}): ")
        if user_input.lower() in ["exit", "quit", "thoat"]:
            print(Fore.RED + "👋 Kết thúc.")
            break

        loading("🤖 Gemini đang trả lời")
        response = chat.send_message(user_input)
        print(Fore.CYAN + f"🤖 Gemini [{datetime.now().strftime('%H:%M')}]:", response.text.strip())
        print(Fore.YELLOW + "-" * 50)

# Cài đặt giao diện
def settings_menu():
    theme = inquirer.select(
        message="🎨 Chọn theme màu:",
        choices=[
            {"name": "Mặc định", "value": Fore.WHITE},
            {"name": "Xanh Dương", "value": Fore.BLUE},
            {"name": "Vàng", "value": Fore.YELLOW},
            {"name": "Xanh Lá", "value": Fore.GREEN},
        ],
    ).execute()
    print(theme + "✅ Đã chọn theme mới!")
    input("⏎ Nhấn Enter để quay lại menu...")

# Xem lịch sử
def show_history():
    print(Fore.YELLOW + "\n📜 Lịch sử trò chuyện:\n")
    if os.path.exists("chat_history.txt"):
        with open("chat_history.txt", "r", encoding="utf-8") as f:
            print(f.read())
    else:
        print("📭 Không có lịch sử.")
    input("⏎ Nhấn Enter để quay lại menu...")

# Chạy menu chính
def main():
    # Gọi hàm kiểm tra API
    check_api_key()
    while True:
        print_banner()
        choice = inquirer.select(
            message="🎮 Chọn một tuỳ chọn bằng ↑ ↓ và Enter:",
            choices=[
                {"name": "Start", "value": "chat"},
                {"name": "History", "value": "history"},
                {"name": "Settings", "value": "settings"},
                {"name": "Exit", "value": "exit"},
            ],
        ).execute()

        if choice == "chat":
            start_chat()
        elif choice == "history":
            show_history()
        elif choice == "settings":
            settings_menu()
        elif choice == "exit":
            print(Fore.RED + "👋 Hẹn gặp lại!")
            break
    

if __name__ == "__main__":
    main()
