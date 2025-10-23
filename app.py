from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import (
    FSInputFile, ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton, BotCommand
)
from pathlib import Path
import asyncio
import os
import logging
import sys

# --- Логи в Railway ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger("somaspace-bot")

# --- Токен из окружения ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set. Add it in Railway → Settings → Variables.")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# === Главное меню ===
def get_main_menu():
    buttons = [
        [KeyboardButton(text="📄 Скачать презентацию")],
        [KeyboardButton(text="📚 Полезные материалы")],
        [KeyboardButton(text="💬 Канал для HR и собственников")],
        [KeyboardButton(text="❓ Анонимный вопрос")],
        [KeyboardButton(text="🧾 Обновить профиль"), KeyboardButton(text="🗑 Удалить мои данные")],
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

WELCOME_TEXT = (
    "Привет! 👋\n\n"
    "Это бот **SõmaSpace** — пространства поддержки для сотрудников и HR.\n\n"
    "Здесь вы можете:\n"
    "• 📄 Скачать презентацию\n"
    "• 📚 Посмотреть полезные материалы\n"
    "• 💬 Перейти в канал для HR и собственников\n\n"
    "Начнём?"
)

# === /start и /menu ===
@dp.message(Command("start"))
@dp.message(Command("menu"))
async def cmd_start(message: types.Message):
    await message.answer(WELCOME_TEXT, reply_markup=get_main_menu())

# === «подстраховка»: если пользователь напишет просто "start" ===
@dp.message(F.text.regexp(r"^\s*start\s*$", flags=0))
async def txt_start(message: types.Message):
    await message.answer(WELCOME_TEXT, reply_markup=get_main_menu())

# === Скачать презентацию ===
@dp.message(F.text == "📄 Скачать презентацию")
async def send_presentation(message: types.Message):
    try:
        base_path = Path(__file__).parent
        file_path = base_path / "files" / "somaspace_HR.pdf"

        if not file_path.exists():
            logger.error("PDF not found at %s", file_path)
            await message.answer("Файл не найден 😔 Сообщите нам, пожалуйста. Мы починим.")
            return

        await message.answer("Загрузка…")
        await bot.send_document(
            chat_id=message.chat.id,
            document=FSInputFile(file_path),
            caption="Вот презентация **SõmaSpace** для HR 📄"
        )
    except Exception:
        logger.exception("Failed to send presentation")
        await message.answer("Ошибка при отправке файла. Мы уже смотрим, извините 🙏")

# === Полезные материалы ===
@dp.message(F.text == "📚 Полезные материалы")
async def materials(message: types.Message):
    text = (
        "Раздел в разработке 💫\n\n"
        "Скоро здесь появятся статьи, карточки и видео, которые помогут HR и командам.\n\n"
        "А пока вы можете перейти в наш канал для HR и собственников 👇"
    )
    link_button = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Перейти в канал", url="https://t.me/somaspace_tg")]
        ]
    )
    await message.answer(text, reply_markup=link_button)

# === Канал для HR и собственников ===
@dp.message(F.text == "💬 Канал для HR и собственников")
async def go_to_channel(message: types.Message):
    link_button = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Открыть канал SõmaSpace", url="https://t.me/somaspace_tg")]
        ]
    )
    await message.answer("Вот ссылка на наш Telegram-канал 👇", reply_markup=link_button)

# === Анонимный вопрос ===
@dp.message(F.text == "❓ Анонимный вопрос")
async def ask_question(message: types.Message):
    await message.answer(
        "Опишите вашу ситуацию (до 500 символов). Мы пришлём рекомендацию и подскажем, к какому специалисту обратиться."
    )

# Ответ на анонимный вопрос (упрощённо)
@dp.message(F.reply_to_message & F.reply_to_message.text.contains("Опишите вашу ситуацию"))
async def handle_question(message: types.Message):
    logger.info("Anon question from %s: %s", message.from_user.id, (message.text or "")[:1000])
    await message.answer(
        "Спасибо за ваш вопрос 🌿\n"
        "Ответ придёт сюда в течение рабочего дня.\n"
        "Это не консультация, а навигация по первым шагам."
    )

# === Обновить профиль (заглушка) ===
@dp.message(F.text == "🧾 Обновить профиль")
async def update_profile(message: types.Message):
    await message.answer("Функция обновления профиля появится позже 🌱")

# === Удалить данные (заглушка) ===
@dp.message(F.text == "🗑 Удалить мои данные")
async def delete_data(message: types.Message):
    await message.answer(
        "Все ваши данные будут удалены.\n\n"
        "Пока эта функция не активна. Напишите нам, если нужно удалить информацию."
    )

# === Fallback: неизвестная команда — покажем меню ===
@dp.message(F.text.startswith("/"))
async def unknown_command(message: types.Message):
    await message.answer("Команда не найдена. Открою меню 👇", reply_markup=get_main_menu())

# === Запуск ===
async def main():
    # 1) Сброс вебхука — критично, иначе /start может «молчать»
    await bot.delete_webhook(drop_pending_updates=True)

    # 2) Зарегистрируем команды в клиенте
    await bot.set_my_commands([
        BotCommand(command="start", description="Начать"),
        BotCommand(command="menu", description="Главное меню"),
    ])

    logger.info("Starting SomaSpace bot…")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
