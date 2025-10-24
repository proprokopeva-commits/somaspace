from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import (
    FSInputFile, ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton, BotCommand
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from pathlib import Path
import asyncio
import os
import csv
import logging
import sys

# --- Логи ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger("somaspace-bot")

# --- Токен ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set. Add it in Railway → Settings → Variables.")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# === Главное меню ===
def get_main_menu():
    buttons = [
        [KeyboardButton(text="💬 Канал для HR и собственников")],
        [KeyboardButton(text="📄 Скачать презентацию")],
        [KeyboardButton(text="📚 Полезные материалы")],
        [KeyboardButton(text="❓ Анонимный вопрос")],
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

WELCOME_CAPTION = (
    "Привет! 👋\n\n"
    "<b>SõmaSpace</b> — сервис заботы о людях в компаниях.\n"
    "Если вы верите, что здоровая команда начинается с внимания к человеку — вы дома.\n\n"
    "Начните с канала: там истории, практики и примеры внедрения.\n"
    "Или скачайте презентацию — коротко и по делу."
)

NUDGE_TEXT = (
    "🎯 <b>3 шага на неделю:</b>\n"
    "1️⃣ Подпишитесь на канал.\n"
    "2️⃣ Попробуйте одну практику.\n"
    "3️⃣ Напишите <b>Готово</b> — пришлю подборку для старта."
)

# === FSM для сбора контактов ===
class ContactForm(StatesGroup):
    name = State()
    company = State()
    email = State()

def save_user_data(user_id, name, company, email):
    os.makedirs("data", exist_ok=True)
    file_path = "data/users.csv"
    file_exists = os.path.isfile(file_path)
    with open(file_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["user_id", "name", "company", "email"])
        writer.writerow([user_id, name, company, email])
    logger.info("Saved contact: %s, %s, %s", name, company, email)

# === /start ===
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    base_path = Path(__file__).parent
    image_path = base_path / "files" / "start_image.jpg"

    if image_path.exists():
        photo = FSInputFile(image_path)
        await bot.send_photo(
            chat_id=message.chat.id,
            photo=photo,
            caption=WELCOME_CAPTION,
            parse_mode="HTML",
            reply_markup=get_main_menu()
        )
    else:
        await message.answer(WELCOME_CAPTION, parse_mode="HTML", reply_markup=get_main_menu())

    await asyncio.sleep(1.2)
    await message.answer(NUDGE_TEXT, parse_mode="HTML")

# === /menu ===
@dp.message(Command("menu"))
async def menu_cmd(message: types.Message):
    await message.answer("Главное меню 👇", reply_markup=get_main_menu())

# === Канал ===
@dp.message(F.text == "💬 Канал для HR и собственников")
async def open_channel(message: types.Message):
    text = (
        "В канале — коротко и по делу:\n"
        "• как поддерживать людей без бюрократии,\n"
        "• как HR не выгорать,\n"
        "• как руководителям держать баланс между результатом и человеческим.\n\n"
        "<b>Присоединяйтесь 👇</b>"
    )
    link_button = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Перейти в канал SõmaSpace", url="https://t.me/somaspace_tg")]
        ]
    )
    await message.answer(text, parse_mode="HTML", reply_markup=link_button)

# === Скачать презентацию ===
@dp.message(F.text == "📄 Скачать презентацию")
async def send_presentation(message: types.Message):
    try:
        base_path = Path(__file__).parent
        file_path = base_path / "files" / "somaspace_HR.pdf"
        if not file_path.exists():
            await message.answer("Файл не найден 😔 Сообщите нам, пожалуйста.")
            return
        await message.answer("Загрузка…")
        await bot.send_document(
            chat_id=message.chat.id,
            document=FSInputFile(file_path),
            caption="Вот презентация <b>SõmaSpace</b> для HR 📄",
            parse_mode="HTML",
        )
        await message.answer(
            "Если откликнулось — напишите <b>Хочу</b>. Я пришлю 3 шага для мягкого пилота.",
            parse_mode="HTML",
        )
    except Exception:
        logger.exception("Ошибка при отправке презентации")
        await message.answer("Что-то пошло не так 😔 Попробуйте позже.")

# === Полезные материалы ===
@dp.message(F.text == "📚 Полезные материалы")
async def materials(message: types.Message):
    text = (
        "Раздел в разработке 💫\n\n"
        "Скоро здесь появятся статьи, карточки и видео для HR и команд.\n"
        "Пока лучший вход в тему — канал <b>SõmaSpace</b> 👇"
    )
    link_button = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Перейти в канал SõmaSpace", url="https://t.me/somaspace_tg")]
        ]
    )
    await message.answer(text, parse_mode="HTML", reply_markup=link_button)

# === Анонимный вопрос ===
@dp.message(F.text == "❓ Анонимный вопрос")
async def ask_question(message: types.Message):
    await message.answer(
        "Опишите вашу ситуацию (до 500 символов). Мы подскажем первый шаг и тип специалиста.",
        parse_mode="HTML",
    )

@dp.message(F.reply_to_message & F.reply_to_message.text.contains("Опишите вашу ситуацию"))
async def handle_question(message: types.Message):
    logger.info("Anon question: %s", (message.text or '')[:1000])
    await message.answer(
        "Спасибо 🌿 Ответ придёт сюда в течение рабочего дня.\n"
        "Это не консультация, а навигация по первым шагам.",
        parse_mode="HTML",
    )

# === Хочу / Готово — сбор контактов ===
@dp.message(F.text.regexp("^(Хочу|Готово)$"))
async def start_collect(message: types.Message, state: FSMContext):
    await message.answer(
        "Рада, что откликнулось 🌿\n"
        "Мы делаем подборки персонально. Как вас зовут?",
        parse_mode="HTML",
    )
    await state.set_state(ContactForm.name)

@dp.message(ContactForm.name)
async def get_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Из какой вы компании?", parse_mode="HTML")
    await state.set_state(ContactForm.company)

@dp.message(ContactForm.company)
async def get_company(message: types.Message, state: FSMContext):
    await state.update_data(company=message.text)
    await message.answer(
        "Хотите, пришлю подборку на почту? Напишите email или отправьте «Нет».",
        parse_mode="HTML",
    )
    await state.set_state(ContactForm.email)

@dp.message(ContactForm.email)
async def get_email(message: types.Message, state: FSMContext):
    data = await state.get_data()
    name = data.get("name")
    company = data.get("company")
    email = message.text if "@" in message.text else ""
    save_user_data(message.from_user.id, name, company, email)
    await message.answer(
        "Спасибо 🌱 Контакт сохранён.\n\n"
        "В течение дня пришлю материалы для старта. "
        "Если пока не подписаны — загляните в канал 👇",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="Канал SõmaSpace", url="https://t.me/somaspace_tg")]]
        ),
    )
    await state.clear()

# === Запуск ===
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_my_commands([
        BotCommand(command="start", description="Начать"),
        BotCommand(command="menu", description="Главное меню"),
    ])
    logger.info("SõmaSpace bot started ✅")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
