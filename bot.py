import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from data_loader import search_model, get_usd_rate, usd_cache
from utils.pdf_gen import create_pdf
from aiogram.types import InputFile
from handlers.warranty import register_warranty_handlers

API_TOKEN = "8097292310:AAGsi0tjJZoR43JI_kc7tGv6Tp2qz2iQeWQ"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

popular_models = [
    "12", "12 Pro Max", "13", "13 Pro", "13 Pro Max",
    "14", "14 Pro", "14 Pro Max", "15", "15 Pro",
    "15 Pro Max", "16", "16 Pro", "16 Pro Max", "ℹ️ Допомога"
]

popular_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
for i in range(0, len(popular_models), 2):
    popular_keyboard.row(*(KeyboardButton(m) for m in popular_models[i:i+2]))

@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    await message.answer("🔍 Напиши модель (наприклад: 12 Pro Max)", reply_markup=popular_keyboard)

@dp.message_handler(commands=['help'])
async def help_cmd(message: types.Message):
    await message.answer(
        "🛠 Доступні команди:\n"
        "/start — Почати пошук\n"
        "/rate — Поточний курс долара\n"
        "/reload — Перезавантажити курс/дані\n"
        "/warranty — Створити гарантійний талон\n"
        "/help — Показати цю довідку"
    )

@dp.message_handler(lambda m: m.text == "ℹ️ Допомога")
async def help_button(message: types.Message):
    await help_cmd(message)

@dp.message_handler(commands=['rate'])
async def usd_rate_cmd(message: types.Message):
    rate = get_usd_rate()
    await message.answer(f"💱 Поточний курс долара: {rate} грн")

@dp.message_handler(commands=['reload'])
async def reload_data(message: types.Message):
    usd_cache["timestamp"] = 0
    rate = get_usd_rate()
    await message.answer(f"🔁 Дані перезавантажено.\n💱 Актуальний курс: {rate} грн")

@dp.message_handler(lambda message: not message.text.startswith('/'))
async def search(message: types.Message):
    query = message.text.strip()
    results = search_model(query)

    if not results:
        await message.answer("❌ Нічого не знайдено.")
        return

    await message.answer(f"🔎 Знайдено моделей: {len(results)}")
    for item in results:
        serials = item['Серийные номера']
        text = (
            f"📱 <b>{item['Наименование']}</b>\n"
            f"🔢 Серійний: {serials}\n"
            f"💵 Ціна: {item['Розничная']} $\n"
            f"🇺🇦 В гривні: {item['Ціна в грн']} грн"
        )
        await message.answer(text, parse_mode="HTML")

async def set_commands(bot: Bot):
    await bot.set_my_commands([
        types.BotCommand("start", "Почати пошук"),
        types.BotCommand("rate", "Курс долара"),
        types.BotCommand("reload", "Оновити курс"),
        types.BotCommand("warranty", "Гарантійний талон"),
        types.BotCommand("help", "Допомога")
    ])

if __name__ == "__main__":
    async def on_startup(dispatcher):
        register_warranty_handlers(dispatcher)
        await set_commands(bot)

    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
