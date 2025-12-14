import asyncio
import os
import sys
import tempfile
import re

from aiogram import Bot, Dispatcher
from aiogram.types import Message, BotCommand
from aiogram.filters import Command, CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

# ================= CONFIG =================
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN not found in .env")

TIMEOUT_SECONDS = 10   # increased for slow demo code
MAX_OUTPUT_LENGTH = 3000
# ========================================

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# ================= STATES =================
class RunState(StatesGroup):
    waiting_for_code = State()
    waiting_for_input_count = State()
    waiting_for_input = State()
# ========================================

# ================= HELPERS =================
def count_inputs(code: str) -> int:
    return len(re.findall(r"\binput\s*\(", code))


def has_loop(code: str) -> bool:
    return bool(re.search(r"\b(for|while)\b", code))


async def execute_python(code: str, inputs: list[str]) -> str:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as f:
        f.write(code.encode())
        filename = f.name

    try:
        process = await asyncio.create_subprocess_exec(
            sys.executable,
            filename,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdin_data = ("\n".join(inputs) + "\n").encode() if inputs else None

        stdout, stderr = await asyncio.wait_for(
            process.communicate(input=stdin_data),
            timeout=TIMEOUT_SECONDS
        )

        output = (stdout + stderr).decode() or "No output"
        if len(output) > MAX_OUTPUT_LENGTH:
            output = output[:MAX_OUTPUT_LENGTH] + "\n...output truncated"

        return output

    finally:
        os.remove(filename)
# ==========================================

# ================= COMMANDS =================
@dp.message(CommandStart())
async def start_cmd(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "👋 *Welcome!*\n\n"
        "I am a Python Code Runner Bot.\n"
        "I execute Python code safely and collect inputs step-by-step.\n\n"
        "📌 Commands:\n"
        "/run – Run Python code\n"
        "/cancel – Cancel execution\n"
        "/help – How to use",
        parse_mode="Markdown"
    )


@dp.message(Command("help"))
async def help_cmd(message: Message):
    await message.answer(
        "📘 *How it works*\n\n"
        "• Normal input(): inputs are asked automatically\n"
        "• input() inside loops: I ask TOTAL input count\n\n"
        "⏱ Slow programs (sleep / many prints)\n"
        "may timeout for safety.\n\n"
        "Use /cancel anytime.",
        parse_mode="Markdown"
    )


@dp.message(Command("cancel"))
async def cancel_cmd(message: Message, state: FSMContext):
    if await state.get_state() is None:
        await message.answer("❌ Nothing to cancel.")
        return

    await state.clear()
    await message.answer("🚫 Execution cancelled.")


@dp.message(Command("run"))
async def run_cmd(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(RunState.waiting_for_code)
    await message.answer("📝 Please send your Python code:")
# ===========================================

# ================= FSM FLOW =================
@dp.message(RunState.waiting_for_code)
async def receive_code(message: Message, state: FSMContext):
    code = message.text.strip()
    detected_inputs = count_inputs(code)
    loop_present = has_loop(code)

    await state.update_data(
        code=code,
        inputs=[],
        input_count=detected_inputs
    )

    # 🔁 ONLY when loop + input() both exist
    if detected_inputs > 0 and loop_present:
        await state.set_state(RunState.waiting_for_input_count)
        await message.answer(
            "🔁 *Loop with input() detected*\n\n"
            "Your program uses `input()` inside a loop.\n"
            "Please enter the *TOTAL number of inputs* your program will read.\n\n"
            "Example:\n"
            "If loop runs 3 times → enter `3`",
            parse_mode="Markdown"
        )
        return

    # No input at all
    if detected_inputs == 0:
        try:
            await message.answer("▶ Running your program...")
            output = await execute_python(code, [])
            await message.answer(f"✅ Output:\n\n{output}")
        except asyncio.TimeoutError:
            await message.answer(
                "⏱️ *Execution timed out*\n\n"
                "Your program took too long.\n"
                "Possible reasons:\n"
                "• sleep() calls\n"
                "• heavy printing\n"
                "• infinite loops",
                parse_mode="Markdown"
            )
        finally:
            await state.clear()
        return

    # Fixed input count (no loop)
    await state.set_state(RunState.waiting_for_input)
    await message.answer(f"⌨️ Enter input 1 of {detected_inputs}:")


@dp.message(RunState.waiting_for_input_count)
async def receive_input_count(message: Message, state: FSMContext):
    try:
        count = int(message.text.strip())
        if count <= 0:
            raise ValueError
    except ValueError:
        await message.answer("❌ Please enter a valid positive number.")
        return

    await state.update_data(input_count=count)
    await state.set_state(RunState.waiting_for_input)
    await message.answer(
        f"✅ Got it! I will collect {count} inputs.\n\n"
        f"⌨️ Enter input 1 of {count}:"
    )


@dp.message(RunState.waiting_for_input)
async def receive_input(message: Message, state: FSMContext):
    data = await state.get_data()
    inputs = data["inputs"]
    input_count = data["input_count"]

    inputs.append(message.text.strip())
    await state.update_data(inputs=inputs)

    if len(inputs) < input_count:
        await message.answer(f"⌨️ Enter input {len(inputs)+1} of {input_count}:")
    else:
        try:
            await message.answer("▶ Running your program...")
            output = await execute_python(data["code"], inputs)
            await message.answer(f"✅ Output:\n\n{output}")
        except asyncio.TimeoutError:
            await message.answer(
                "⏱️ *Execution timed out*\n\n"
                "Your program took too long to finish.\n"
                "Try reducing sleep or output size.",
                parse_mode="Markdown"
            )
        finally:
            await state.clear()
# ===========================================

# ================= MAIN =================
async def main():
    try:
        await bot.set_my_commands([
            BotCommand(command="start", description="Start the bot"),
            BotCommand(command="run", description="Run Python code"),
            BotCommand(command="cancel", description="Cancel execution"),
            BotCommand(command="help", description="How to use"),
        ])
    except Exception as e:
        print("Menu setup failed:", e)

    print("Bot is running...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
