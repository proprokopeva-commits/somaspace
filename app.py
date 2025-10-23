from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import FSInputFile, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from pathlib import Path
import asyncio
import os

# 🔹 Вставь сюда свой токен от BotFather
BOT_TOKEN = "сюда_вставь_свой_токен"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# === Главное меню ===
def get_main_menu():
    buttons = [
        [KeyboardButton(text="📄 Скачать презентацию")],
        [KeyboardButton(text="📚 Полезные материалы")],
        [KeyboardButton(text="💬 Канал для HR и собственников")],
        [KeyboardButton(text="❓ Анонимный вопрос")],
        [KeyboardButton(text="🧾 Обновить профиль"), KeyboardButton(text="🗑 Удалить мои данные")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

# === /start ===
@dp.message(Command("start"))
async def start(message: types.Message):
    text = (
        "Привет! 👋\n\n"
        "Это бот **SõmaSpace** — пространства поддержки для сотрудников и HR.\n\n"
        "Здесь вы можете:\n"
        "📄 Скачать презентацию\n"
        "📚 Посмотреть полезные материалы\n"
        "💬 Перейти в канал для HR и собственников\n\n"
        "Начнём?"
    )
    await message.answer(text, reply_markup=get_main_menu())

# === Скачать презентацию ===
@dp.message(lambda m: m.text == "📄 Скачать презентацию")
async def send_presentation(message: types.Message):
    try:
        base_path = Path(__file__).parent
        file_path = base_path / "files" / "somaspace_HR.pdf"

        if not file_path.exists():
            await message.answer("Файл не найден 😔 Пожалуйста, сообщите нам, чтобы мы исправили это.")
            return

        await message.answer("Загрузка...")
        await bot.send_document(
            chat_id=message.chat.id,
            document=FSInputFile(file_path),
            caption="Вот презентация **SõmaSpace** для HR 📄"
        )
    except Exception as e:
        await message.answer(f"Ошибка при отправке файла: {e}")

# === Полезные материалы ===
@dp.message(lambda m: m.text == "📚 Полезные материалы")
async def materials(message: types.Message):
    text = (
        "Раздел в разработке 💫\n\n"
        "Скоро здесь появятся статьи, карточки и видео, "
        "которые помогут HR и командам заботиться о себе и друг о друге.\n\n"
        "А пока вы можете перейти в наш канал для HR и собственников 👇"
    )
    link_button = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Перейти в канал", url="https://t.me/somaspace_tg")]
        ]
    )
    await message.answer(text, reply_markup=link_button)

# === Канал для HR и собственников ===
@dp.message(lambda m: m.text == "💬 Канал для HR и собственников")
async def go_to_channel(message: types.Message):
    link_button = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Открыть канал SõmaSpace", url="https://t.me/somaspace_tg")]
        ]
    )
    await message.answer(
        "Вот ссылка на наш Telegram
