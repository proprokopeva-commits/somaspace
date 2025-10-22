import asyncio, logging, os
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from aiogram.filters import CommandStart

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)

PRESENTATION_PATH = "files/Somaspace_HR.pdf"
VIDEO_PATH = "files/masterclass.mp4"
CHANNEL_URL = "https://t.me/your_somaspace_channel"  # ← замени ссылкой на свой канал

def main_menu():
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📄 Скачать презентацию", callback_data="presentation")],
        [InlineKeyboardButton(text="🎥 Посмотреть мастер-класс", callback_data="masterclass")],
        [InlineKeyboardButton(text="🚀 Перейти в канал", callback_data="channel")]
    ])
    return kb

@dp.message(CommandStart())
async def start(m: Message):
    await m.answer(
        "Привет! Я SõmaSpace-бот для HR. За 5 минут — что это и как запустить пилот.\n\nВыберите шаг:",
        reply_markup=main_menu()
    )

@dp.callback_query(F.data == "presentation")
async def send_presentation(c: CallbackQuery):
    if os.path.exists(PRESENTATION_PATH):
        await bot.send_document(c.from_user.id, FSInputFile(PRESENTATION_PATH))
    else:
        await bot.send_message(c.from_user.id, "Файл презентации пока не загружен.")
    await c.answer()

@dp.callback_query(F.data == "masterclass")
async def send_masterclass(c: CallbackQuery):
    if os.path.exists(VIDEO_PATH):
        await bot.send_video(c.from_user.id, FSInputFile(VIDEO_PATH),
                             caption="10 минут: как запустить пилот SõmaSpace без бюрократии.")
    else:
        await bot.send_message(c.from_user.id, "Видео пока не загружено.")
    await c.answer()

@dp.callback_query(F.data == "channel")
async def go_channel(c: CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Открыть канал", url=CHANNEL_URL)]
    ])
    await c.message.answer("Переходите в наш канал:", reply_markup=kb)
    await c.answer()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

