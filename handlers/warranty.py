from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import Dispatcher
from aiogram.types import InputFile
from utils.pdf_gen import create_pdf

class WarrantyFSM(StatesGroup):
    waiting_for_model = State()
    waiting_for_serial = State()
    waiting_for_price = State()
    waiting_for_duration = State()

def register_warranty_handlers(dp: Dispatcher):
    dp.register_message_handler(cmd_warranty, commands="warranty", state="*")
    dp.register_message_handler(handle_model, state=WarrantyFSM.waiting_for_model)
    dp.register_message_handler(handle_serial, state=WarrantyFSM.waiting_for_serial)
    dp.register_message_handler(handle_price, state=WarrantyFSM.waiting_for_price)
    dp.register_message_handler(handle_duration, state=WarrantyFSM.waiting_for_duration)

async def cmd_warranty(message: types.Message):
    await message.answer("📱 Введи модель телефону:")
    await WarrantyFSM.waiting_for_model.set()

async def handle_model(message: types.Message, state: FSMContext):
    await state.update_data(model=message.text)
    await message.answer("🔢 Введи серійний номер:")
    await WarrantyFSM.waiting_for_serial.set()

async def handle_serial(message: types.Message, state: FSMContext):
    await state.update_data(serial=message.text)
    await message.answer("💰 Введи ціну в грн:")
    await WarrantyFSM.waiting_for_price.set()

async def handle_price(message: types.Message, state: FSMContext):
    try:
        price = int(message.text.strip())
    except ValueError:
        await message.answer("⚠️ Введи ціну числом!")
        return
    await state.update_data(price=price)
    await message.answer("📆 Введи кількість місяців гарантії (наприклад: 3):")
    await WarrantyFSM.waiting_for_duration.set()

async def handle_duration(message: types.Message, state: FSMContext):
    warranty = message.text.strip()
    data = await state.get_data()

    path = create_pdf(
        model=data["model"],
        serial=data["serial"],
        price=data["price"],
        warranty=warranty
    )

    await message.answer_document(InputFile(path), caption="✅ Гарантійний талон готовий!")
    await state.finish()
