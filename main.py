import os
import time
import re
import threading
from InquirerPy import inquirer
from pyfiglet import Figlet
from dotenv import load_dotenv
from colorama import Fore, init
from terminaltexteffects.effects.effect_sweep import Sweep
import google.generativeai as genai
from datetime import datetime
from tabulate import tabulate
from pathlib import Path
from rich.markdown import Markdown
from rich.console import Console
from rich.panel import Panel

console = Console()
response_text = None
response_done = threading.Event()

# Kiểm tra và hỏi API Key nếu chưa có
def check_user_and_api():
    env_path = Path(".env")

    if not env_path.exists():
        with open(env_path, "w") as f:
            pass  # Tạo file nếu chưa có

    load_dotenv()
    current_key = os.getenv("GEMINI_API_KEY")
    current_model = os.getenv("GEMINI_MODEL")
    user_name = os.getenv("USER_NAME")

    # Nếu thiếu bất kỳ biến nào thì hỏi người dùng
    if not current_key or not current_model or not user_name:
        if not user_name:
            user_name = input("🧑 Nhập tên của bạn (nickname): ").strip()
        if not current_key:
            current_key = input("🔑 Nhập API Key của bạn: ").strip()
        if not current_model:
            current_model = input("🤖 Nhập tên model AI (vd: gemini-2.0): ").strip()

        with open(env_path, "a", encoding="utf-8") as f:
            if user_name:
                f.write(f"USER_NAME={user_name}\n")
            if current_key:
                f.write(f"GEMINI_API_KEY={current_key}\n")
            if current_model:
                f.write(f"GEMINI_MODEL={current_model}\n")

        print(Fore.GREEN + "\n✅ Đã lưu thông tin:")
        table = [
            ["USER_NAME", user_name],
            ["GEMINI_API_KEY", current_key[:6] + "..." + current_key[-4:]],
            ["GEMINI_MODEL", current_model],
        ]
        print(tabulate(table, headers=["Biến", "Giá trị"], tablefmt="rounded_grid"))
        print("🔁! Vui lòng chạy lại chương trình để sử dụng.\n")
        time.sleep(1)
        exit()

    load_dotenv()  # Nạp lại nếu vừa ghi thêm


# Chỉ fix hiển thị ** in đậm **
def markdown_to_terminal(text):
    text = re.sub(r"\*\*(.*?)\*\*", r"\033[1m\1\033[0m", text)  # Bold
    text = re.sub(r"\*(.*?)\*", r"\033[3m\1\033[0m", text)      # Italic
    text = re.sub(r"`(.*?)`", r"\033[96m\1\033[0m", text)       # Code style
    return text

# Init
init(autoreset=True)
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = os.getenv("GEMINI_MODEL")
genai.configure(api_key=API_KEY)

# Hiển thị tiêu đề bằng hiệu ứng terminal-text-effects
def print_banner():
    os.system("cls" if os.name == "nt" else "clear")
    fig = Figlet(font='starwars' )
    ascii_text = fig.renderText("GEMINI")
    # Hiệu ứng chữ 
    effect = Sweep(ascii_text)
    with effect.terminal_output() as terminal:
        for frame in effect:
            terminal.print(frame)
    print(Fore.YELLOW + "Phiên bản: 1.1.2 \n")
  
def get_response(chat, user_input):
    global response_text
    response = chat.send_message(user_input)
    response_text = response.text.strip()
    response_done.set()

# Hiệu ứng loading
def loading(msg="Đang tải"):
    def animate():
        dots = ""
        while not response_done.is_set():
            dots += "."
            if len(dots) > 3:
                dots = ""
            print(Fore.YELLOW + f"\r{msg}{dots}   ", end="", flush=True)
            time.sleep(0.4)
        print(" " * 80, end="\r")  # clear line

    threading.Thread(target=animate, daemon=True).start()

# Bắt đầu chat
def start_chat():
    USER_NAME = os.getenv("USER_NAME") or "Bạn"
    model = genai.GenerativeModel(MODEL_NAME)
    chat = model.start_chat(history=[])
    history = []

    while True:
        user_input = input(f"👤 {USER_NAME} ({datetime.now().strftime('%H:%M')}): ")
        if user_input.lower() in ["exit", "quit", "thoat"]:
            confirm_save_history(history)  # Dùng history đúng
            break

        response_done.clear()

        loading("🤖 Gemini đang trả lời")

        t = threading.Thread(target=get_response, args=(chat, user_input))
        t.start()
        t.join()
        response = chat.send_message(user_input)  # Quá trình xử lý dài
        reply_text = response.text.strip()
        formatted_text = markdown_to_terminal(reply_text)

        # In ra bằng rich Panel
        console.print(Panel.fit(
            formatted_text,
            title="🤖 Gemini",
            subtitle=datetime.now().strftime("%H:%M"),
            border_style="cyan"
        ))

        # Lưu lại đoạn chat
        history.append((user_input, reply_text))
        print(Fore.YELLOW + "-" * 50)


# Hàm lưu lịch sử trò chuyện
def confirm_save_history(chat_history):
    confirm = inquirer.confirm(
        message="💾 Bạn có muốn lưu lại cuộc trò chuyện này không?",
        default=True
    ).execute()

    if not confirm:
        print(Fore.YELLOW + "⚠️ Không lưu lịch sử.")
        return

    # Chuẩn bị nội dung để gửi cho Gemini
    content = ""
    for user, ai in chat_history:
        content += f"User: {user}\nGemini: {ai}\n\n"

    # Gửi nội dung để Gemini đặt tiêu đề
    try:
        summary_model = genai.GenerativeModel(MODEL_NAME)
        response = summary_model.generate_content(
            f"Hãy đặt một tiêu đề ngắn gọn cho cuộc trò chuyện sau (dưới 6 từ, không dấu, viết thường, dùng dấu gạch ngang):\n{content}"
        )
        summary = response.text.strip().lower()
        # Xử lý chuỗi cho an toàn tên file
        summary = summary.replace(" ", "-").replace(".", "").replace("?", "").replace("!", "")
        if not summary:
            summary = "chat"
    except Exception as e:
        print(Fore.RED + f"⚠️ Lỗi khi tạo tiêu đề: {e}")
        summary = "chat"

    # Đặt tên file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{summary}_{timestamp}.txt"

    folder = Path("history")
    folder.mkdir(exist_ok=True)

    # Ghi nội dung vào file
    with open(folder / filename, "w", encoding="utf-8") as f:
        f.write(content)

    print(Fore.GREEN + f"✅ Đã lưu lịch sử vào {filename}")



# Hàm show lịch sử trò chuyện
def show_history():
    history_dir = "history/"
    if not os.path.exists(history_dir) or not os.listdir(history_dir):
        print(Fore.YELLOW + "📭 Không có cuộc trò chuyện nào được lưu.")
        input("⏎ Nhấn Enter để quay lại menu...")
        return

    files = [f for f in os.listdir(history_dir) if f.endswith(".txt")]
    
    file_choice = inquirer.select(
        message="📜 Chọn cuộc trò chuyện để xem:",
        choices=files + ["↩️ Quay lại"],
    ).execute()

    if file_choice == "↩️ Quay lại":
        return

    file_path = os.path.join(history_dir, file_choice)
    with open(file_path, "r", encoding="utf-8") as f:
        print(Fore.CYAN + f"\n📄 Nội dung của {file_choice}:\n")
        print(f.read())
        print(Fore.YELLOW + "-" * 50)

    input("⏎ Nhấn Enter để quay lại menu...")


# Cài đặt giao diện
def settings_menu():
    while True:
        setting = inquirer.select(
            message="🎨 Chọn tuỳ chọn cài đặt:",
            choices=[
                {"name": "🎨 Đổi màu theme", "value": "theme"},
                {"name": "🧠 Chuyển chữ sang Binary/Morse", "value": "convert"},
                {"name": "↩️ Quay lại", "value": "back"},
            ],
        ).execute()

        if setting == "theme":
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
            input("⏎ Nhấn Enter để quay lại...")

        elif setting == "convert":
            convert_text_to_figlet()
        elif setting == "back":
            break


# Chuyển đổi chữ thành ASCII art
def convert_text_to_figlet():
    user_text = input(Fore.CYAN + "🔤 Nhập chữ bạn muốn chuyển đổi: ").strip().upper()
    if not user_text:
        print(Fore.RED + "❗ Vui lòng nhập chữ hợp lệ!")
        return

    style = inquirer.select(
        message="🧠 Chọn kiểu chuyển đổi:",
        choices=[
            {"name": "🔡 Morse Code", "value": "morse"},
            {"name": "💻 Binary", "value": "binary"},
            {"name": "↩️ Quay lại", "value": "back"},
        ],
    ).execute()

    if style == "back":
        return

    fig = Figlet(font=style)
    ascii_text = fig.renderText(user_text)
    print(Fore.GREEN + ascii_text)
    input(Fore.YELLOW + "\n⏎ Nhấn Enter để quay lại...")


# Chạy menu chính
def main():
    # Gọi hàm kiểm tra API
    check_user_and_api()
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
