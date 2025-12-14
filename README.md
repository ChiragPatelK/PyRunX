# 🐍 Python Code Runner Telegram Bot

A Telegram bot that executes Python code and provides a **terminal-like interactive input experience** directly inside Telegram.

This project is built using **Python** and **aiogram**, with special focus on correctly handling `input()` — including complex cases where `input()` is used inside loops.

---

## 🚀 Features

- ✅ Execute Python code from Telegram
- ✅ Terminal-like **step-by-step input collection**
- ✅ Smart handling of `input()` inside loops
- ✅ Clear user guidance for dynamic input cases
- ✅ Commands: `/start`, `/run`, `/cancel`, `/help`
- ✅ Telegram side menu (≡) support
- ✅ Safe execution with timeout protection
- ✅ Graceful handling of runtime errors
- ✅ Clean project structure (deploy-ready)
- ✅ Portfolio & resume-ready project

---

## 🧠 Input Handling Logic

### 1️⃣ Normal Input
name = input()
age = input()
print(name, age)

The bot automatically detects the number of `input()` calls and asks inputs one by one.

---

### 2️⃣ Input Inside Loops (Dynamic Input)

for i in range(3):
    print(input())

Since the number of inputs cannot be determined statically, the bot clearly asks:

> 🔢 How many inputs will this program need?

After receiving the count, inputs are collected step by step and the program is executed safely.

This approach avoids unsafe execution and ensures correctness.

---

## 📌 Commands

| Command   | Description              |
| --------- | ------------------------ |
| `/start`  | Start the bot            |
| `/run`    | Run Python code          |
| `/cancel` | Cancel current execution |
| `/help`   | Usage instructions       |

---

## 🛡 Safety & Reliability

* ⏱ Execution timeout to prevent infinite or slow-running programs
* ❌ Friendly timeout and runtime error messages
* 🔐 Environment variables used to protect bot token
* 🧹 Temporary files cleaned after execution
* ⚠️ Designed for learning and demo purposes (not a sandboxed VM)

---

## 🛠 Tech Stack

* Python 3.10+
* aiogram (Telegram Bot Framework)
* asyncio
* FSM (Finite State Machine)
* python-dotenv

---

## 📂 Project Structure

PyRunX/

│

├── bot.py

├── requirements.txt

├── .env            # ignored by git

├── .gitignore

├── README.md

└── venv/           # ignored by git


---

## ▶️ Running Locally

1. Clone the repository:

   git clone https://github.com/ChiragPatelK/PyRunX

   cd PyRunX


2. Create a `.env` file:

   BOT_TOKEN=your_telegram_bot_token

3. Install dependencies:

   pip install -r requirements.txt

4. Run the bot:

   python bot.py

---

## 📌 Limitations

* Python code is executed locally (no Docker sandbox)
* Long-running or heavy I/O programs may timeout
* Intended for educational and portfolio use

---

## 🔮 Future Improvements

* Docker-based sandboxing
* Partial output streaming for long programs
* Inline keyboard controls
* Execution history per user

---

## 👨‍💻 Author

**Chirag Patel**
🎓 BCA Student

* GitHub: [https://github.com/ChiragPatelK](https://github.com/ChiragPatelK)
* LinkedIn: [https://www.linkedin.com/in/chirag-patel-65195a393/](https://www.linkedin.com/in/chirag-patel-65195a393/)

---

## 📄 License

This project is open for learning, demo, and portfolio purposes.

