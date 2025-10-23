import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton, BotCommand
from aiogram.filters import CommandStart, Command

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_URL = os.getenv("CHANNEL_URL", "https://t.me/your_channel")
MASTERCLASS_URL = os.getenv("MASTERCLASS_URL", "https://t.me/your_video")

if not BOT_TOKEN or ":" not in BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN отсутствует или некорректен. Задай Service Variable BOT_TOKEN на Railway.")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Память для данных пользователей
user_data = {}

# Главное меню
menu_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📥 Скачать презентацию", callback_data="download_prez")],
    [InlineKeyboardButton(text="🎥 Посмотреть мастер-класс", url=MASTERCLASS_URL)],
    [InlineKeyboardButton(text="📣 Перейти в канал", url=CHANNEL_URL)],
])

async def set_commands():
    cmds = [
        BotCommand(command="start", description="Начать"),
        BotCommand(command="menu", description="Показать меню"),
    ]
    await bot.set_my_commands(cmds)


# --- Диалог сбора данных ---
@dp.message(CommandStart())
async def start_dialog(m: Message):
    user_data[m.from_user.id] = {}
    await m.answer("Привет! 👋\n\nЯ помогу тебе познакомиться с SõmaSpace.\n\nДля начала скажи, как тебя зовут?")
    user_data[m.from_user.id]["step"] = "name"


@dp.message(F.text)
async def collect_data(m: Message):
    uid = m.from_user.id
    if uid not in user_data:
        return await m.answer("Напиши /start, чтобы начать заново.")

    step = user_data[uid].get("step")

    if step == "name":
        user_data[uid]["name"] = m.text.strip()
        user_data[uid]["step"] = "company"
        return await m.answer("Отлично, приятно познакомиться, {0}! 😊\n\nИз какой ты компании?".format(m.text.strip()))

    elif step == "company":
        user_data[uid]["company"] = m.text.strip()
        user_data[uid]["step"] = "email"
        return await m.answer("Спасибо! А теперь оставь, пожалуйста, корпоративную почту — чтобы мы могли прислать материалы.")

    elif step == "email":
        user_data[uid]["email"] = m.text.strip()
        name = user_data[uid]["name"]
        company = user_data[uid]["company"]
        email = user_data[uid]["email"]

        # финальное сообщение
        text = (
            f"✨ Спасибо, {name}!\n\n"
            f"Компания: {company}\n"
            f"Email: {email}\n\n"
            f"Теперь можешь выбрать, что хочешь сделать 👇"
        )

        await m.answer(text, reply_markup=menu_kb)
        user_data.pop(uid, None)  # очищаем временные данные


# --- Обработчик кнопки презентации ---
@dp.callback_query(F.data == "download_prez")
async def on_download_prez(c: CallbackQuery):
    await c.answer()
    path = "files/Somaspace_HR.pdf"
    try:
        doc = FSInputFile(path)
        await bot.send_document(
            chat_id=c.from_user.id,
            document=doc,
            caption="Презентация SõmaSpace для HR 🚀"
        )
    except Exception:
        await bot.send_message(c.from_user.id, "⚠️ Не удалось найти файл презентации. Проверь путь: files/Somaspace_HR.pdf")


@dp.message(Command("menu"))
async def on_menu(m: Message):
    await m.answer("Выбери действие 👇", reply_markup=menu_kb)


async def runner():
    await set_commands()
    while True:
        try:
            await dp.start_polling(bot)
        except Exception as e:
            logging.exception(f"Polling crashed: {e}. Restarting in 5s…")
            await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(runner())
