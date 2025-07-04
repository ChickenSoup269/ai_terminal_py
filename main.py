import os
import time
from InquirerPy import inquirer
from pyfiglet import Figlet
from dotenv import load_dotenv
from colorama import Fore, init
from terminaltexteffects.effects import effect_rain
import google.generativeai as genai
from datetime import datetime

# Init
init(autoreset=True)
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=API_KEY)

# Hiển thị tiêu đề bằng hiệu ứng terminal-text-effects
def print_banner():
    os.system("cls" if os.name == "nt" else "clear")
    fig = Figlet(font='big')
    ascii_text = fig.renderText("Gemini AI")
    
    # Hiệu ứng chữ (có thể đổi typewriter thành wave, shake, jitter, bounce...)
    effect = effect_rain.Rain(ascii_text)
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
    model = genai.GenerativeModel("gemini-2.0-flash")
    chat = model.start_chat(history=[])

    while True:
        user_input = input(Fore.GREEN + f"👤 Bạn [{datetime.now().strftime('%H:%M')}]: ")
        if user_input.lower() in ["exit", "quit", "thoat"]:
            print(Fore.YELLOW + "👋 Kết thúc.")
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
            {"name": "Mặc định (Cyan)", "value": Fore.CYAN},
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
    while True:
        print_banner()
        choice = inquirer.select(
            message="🎮 Chọn một tuỳ chọn bằng ↑ ↓ và Enter:",
            choices=[
                {"name": "▶️ Bắt đầu trò chuyện", "value": "chat"},
                {"name": "📜 Xem lịch sử", "value": "history"},
                {"name": "🎨 Cài đặt giao diện", "value": "settings"},
                {"name": "❌ Thoát", "value": "exit"},
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
