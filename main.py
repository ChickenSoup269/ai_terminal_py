import os
import time
from datetime import datetime
import google.generativeai as genai
from dotenv import load_dotenv
from colorama import init, Fore, Style
from tabulate import tabulate

# Khởi động colorama
init(autoreset=True)

# Hàm gõ từng ký tự
def type_effect(text, delay=0.02):
    for char in text:
        print(char, end="", flush=True)
        time.sleep(delay)
    print()

# Hàm in bảng nếu phát hiện có định dạng Markdown
def try_print_table(text):
    lines = text.strip().splitlines()
    table_lines = [line for line in lines if "|" in line]

    if len(table_lines) >= 2 and "---" in table_lines[1]:
        headers = [h.strip() for h in table_lines[0].split("|")[1:-1]]
        rows = [
            [cell.strip() for cell in row.split("|")[1:-1]]
            for row in table_lines[2:]
        ]
        print(f"{Fore.YELLOW}\n📊 Bảng dữ liệu:")
        print(tabulate(rows, headers=headers, tablefmt="grid"))
        return True
    return False

# Load API key từ .env
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=API_KEY)

# Khởi tạo mô hình + chat session
model = genai.GenerativeModel("gemini-2.0-flash")
chat = model.start_chat(history=[])

print(f"{Fore.CYAN}🤖 Gemini Chat - Nhập 'exit' để thoát")
print(f"{Fore.CYAN}{'-'*50}")

while True:
    user_input = input(f"{Fore.GREEN}👤 Bạn [{datetime.now().strftime('%H:%M')}]: {Style.RESET_ALL}")
    if user_input.lower() in ["exit", "quit"]:
        print(f"{Fore.YELLOW}🚪 Đã thoát.")
        break

    try:
        print(f"{Fore.MAGENTA}🤖 Gemini đang trả lời...", end="\r", flush=True)
        response = chat.send_message(user_input)

        now = datetime.now().strftime('%H:%M')
        content = response.text.strip()

        print(f"\n{Fore.BLUE}{'-'*40}")
        print(f"{Fore.GREEN}👤 Bạn [{now}]: {user_input}")
        print(f"{Fore.BLUE}{'-'*40}")
        print(f"{Fore.CYAN}🤖 Gemini [{now}]:", end=" ")

        # Nếu là bảng, in bảng; nếu không, dùng type_effect
        if not try_print_table(content):
            type_effect(content)

        print(f"{Fore.BLUE}{'-'*40}\n")

    except Exception as e:
        print(f"{Fore.RED}⚠️ Lỗi: {e}")
