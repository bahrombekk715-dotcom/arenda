import asyncio
import logging
import os
from datetime import datetime
from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
from database import (
    init_db, add_user, get_user, add_scooter, get_all_scooters,
    create_rental, add_document, get_user_rentals, get_all_rentals,
    get_rental_documents, add_payment, get_stats
)
from reminder import ReminderService
import admin_handlers

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_IDS = [int(x) for x in os.getenv('ADMIN_IDS', '').split(',') if x]
WEBAPP_URL = os.getenv('WEBAPP_URL', 'http://localhost:5000')

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
router = Router()

class RentalStates(StatesGroup):
    waiting_passport = State()
    waiting_photo = State()
    waiting_video = State()

class AddScooterStates(StatesGroup):
    waiting_name = State()
    waiting_model = State()
    waiting_price_weekly = State()
    waiting_price_monthly = State()
    waiting_image = State()

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

def get_main_keyboard(user_id: int):
    buttons = [
        [InlineKeyboardButton(text="🛴 Skuterlar", web_app=WebAppInfo(url=f"{WEBAPP_URL}?user_id={user_id}"))],
        [InlineKeyboardButton(text="📋 Mening ijaralarim", callback_data="my_rentals")],
        [InlineKeyboardButton(text="ℹ️ Ma'lumot", callback_data="info")]
    ]

    if is_admin(user_id):
        buttons.append([InlineKeyboardButton(text="👨‍💼 Admin panel", callback_data="admin_panel")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_admin_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Statistika", callback_data="admin_stats")],
        [InlineKeyboardButton(text="🛴 Skuterlar boshqaruvi", callback_data="manage_scooters")],
        [InlineKeyboardButton(text="📋 Barcha ijaralar", callback_data="all_rentals")],
        [InlineKeyboardButton(text="💳 To'lov qabul qilish", callback_data="process_payment")],
        [InlineKeyboardButton(text="◀️ Orqaga", callback_data="back_to_main")]
    ])

@router.message(CommandStart())
async def cmd_start(message: Message):
    try:
        user = message.from_user
        await add_user(user.id, user.username or '', user.full_name)

        welcome_text = f"""👋 Assalomu alaykum, {user.full_name}!

🛴 <b>Skuter ijarasi botiga xush kelibsiz!</b>

Bu bot orqali siz:
✅ Skuterlarni ko'rishingiz
✅ Haftalik yoki oylik ijara olishingiz
✅ To'lovlarni kuzatishingiz mumkin

Davom etish uchun quyidagi tugmalardan foydalaning:"""

        await message.answer(
            welcome_text,
            reply_markup=get_main_keyboard(user.id),
            parse_mode='HTML'
        )
    except Exception as e:
        logger.error(f"Start command error: {e}")
        await message.answer(
            "❌ Xatolik yuz berdi. Iltimos, qaytadan /start bosing.",
            reply_markup=get_main_keyboard(message.from_user.id)
        )

@router.callback_query(F.data == "back_to_main")
async def back_to_main(callback: CallbackQuery):
    await callback.message.edit_text(
        "🏠 Asosiy menyu:",
        reply_markup=get_main_keyboard(callback.from_user.id)
    )
    await callback.answer()

@router.callback_query(F.data == "my_rentals")
async def my_rentals(callback: CallbackQuery):
    user_id = callback.from_user.id
    rentals = await get_user_rentals(user_id)

    if not rentals:
        await callback.answer("❌ Sizda faol ijara yo'q", show_alert=True)
        return

    text = "📋 <b>Sizning ijaralaringiz:</b>\n\n"

    for rental in rentals:
        rental_type = "Haftalik" if rental['rental_type'] == 'weekly' else "Oylik"
        text += f"🛴 <b>{rental['scooter_name']}</b> ({rental['model']})\n"
        text += f"📅 Boshlanish: {rental['start_date'][:10]}\n"
        text += f"📅 Tugash: {rental['end_date'][:10]}\n"
        text += f"💵 To'lov: {rental_type} - {rental['total_price']} so'm\n"
        text += "━━━━━━━━━━━━━━━\n\n"

    back_btn = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Orqaga", callback_data="back_to_main")]
    ])

    await callback.message.edit_text(text, reply_markup=back_btn, parse_mode='HTML')
    await callback.answer()

@router.callback_query(F.data == "info")
async def info(callback: CallbackQuery):
    info_text = """
ℹ️ <b>Bot haqida ma'lumot:</b>

🛴 Bu bot skuter ijarasini boshqarish uchun yaratilgan.

📞 <b>Aloqa:</b>
• Telefon: +998 XX XXX XX XX
• Telegram: @admin

⏰ <b>Ish vaqti:</b>
Har kuni 09:00 - 21:00

💳 <b>To'lov:</b>
• Haftalik ijara
• Oylik ijara
• Naqd/Plastik karta
"""

    back_btn = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Orqaga", callback_data="back_to_main")]
    ])

    await callback.message.edit_text(info_text, reply_markup=back_btn, parse_mode='HTML')
    await callback.answer()

@router.callback_query(F.data == "admin_panel")
async def admin_panel(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Sizda ruxsat yo'q!", show_alert=True)
        return

    await callback.message.edit_text(
        "👨‍💼 <b>Admin panel</b>\n\nKerakli bo'limni tanlang:",
        reply_markup=get_admin_keyboard(),
        parse_mode='HTML'
    )
    await callback.answer()

@router.callback_query(F.data == "admin_stats")
async def admin_stats(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Sizda ruxsat yo'q!", show_alert=True)
        return

    stats = await get_stats()

    stats_text = f"""
📊 <b>Statistika:</b>

👥 Jami foydalanuvchilar: {stats['total_users']}
🛴 Jami skuterlar: {stats['total_scooters']}
📋 Faol ijaralar: {stats['active_rentals']}
💰 Umumiy daromad: {stats['total_revenue']:,.0f} so'm
"""

    back_btn = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Admin panel", callback_data="admin_panel")]
    ])

    await callback.message.edit_text(stats_text, reply_markup=back_btn, parse_mode='HTML')
    await callback.answer()

@router.callback_query(F.data == "add_scooter")
async def add_scooter_start(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Sizda ruxsat yo'q!", show_alert=True)
        return

    await state.set_state(AddScooterStates.waiting_name)
    await callback.message.answer("🛴 Skuter nomini kiriting:")
    await callback.answer()

@router.message(AddScooterStates.waiting_name)
async def process_scooter_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(AddScooterStates.waiting_model)
    await message.answer("📝 Skuter modelini kiriting:")

@router.message(AddScooterStates.waiting_model)
async def process_scooter_model(message: Message, state: FSMContext):
    await state.update_data(model=message.text)
    await state.set_state(AddScooterStates.waiting_price_weekly)
    await message.answer("💵 Haftalik narxni kiriting (so'mda):")

@router.message(AddScooterStates.waiting_price_weekly)
async def process_price_weekly(message: Message, state: FSMContext):
    try:
        price = float(message.text)
        await state.update_data(price_weekly=price)
        await state.set_state(AddScooterStates.waiting_price_monthly)
        await message.answer("💵 Oylik narxni kiriting (so'mda):")
    except ValueError:
        await message.answer("❌ Iltimos, raqam kiriting!")

@router.message(AddScooterStates.waiting_price_monthly)
async def process_price_monthly(message: Message, state: FSMContext):
    try:
        price = float(message.text)
        await state.update_data(price_monthly=price)
        await state.set_state(AddScooterStates.waiting_image)
        await message.answer("📷 Skuter rasmini yuboring (yoki /skip yozing):")
    except ValueError:
        await message.answer("❌ Iltimos, raqam kiriting!")

@router.message(AddScooterStates.waiting_image, F.photo)
async def process_scooter_image(message: Message, state: FSMContext):
    photo = message.photo[-1]
    await state.update_data(image_url=photo.file_id)

    data = await state.get_data()
    scooter_id = await add_scooter(
        data['name'],
        data['model'],
        data['price_weekly'],
        data['price_monthly'],
        data.get('image_url')
    )

    await message.answer(
        f"✅ Skuter muvaffaqiyatli qo'shildi!\n\n"
        f"🛴 Nom: {data['name']}\n"
        f"📝 Model: {data['model']}\n"
        f"💵 Haftalik: {data['price_weekly']} so'm\n"
        f"💵 Oylik: {data['price_monthly']} so'm",
        reply_markup=get_admin_keyboard()
    )
    await state.clear()

@router.message(AddScooterStates.waiting_image, Command("skip"))
async def skip_scooter_image(message: Message, state: FSMContext):
    data = await state.get_data()
    scooter_id = await add_scooter(
        data['name'],
        data['model'],
        data['price_weekly'],
        data['price_monthly'],
        None
    )

    await message.answer(
        f"✅ Skuter muvaffaqiyatli qo'shildi!\n\n"
        f"🛴 Nom: {data['name']}\n"
        f"📝 Model: {data['model']}\n"
        f"💵 Haftalik: {data['price_weekly']} so'm\n"
        f"💵 Oylik: {data['price_monthly']} so'm",
        reply_markup=get_admin_keyboard()
    )
    await state.clear()

@router.callback_query(F.data == "all_rentals")
async def all_rentals(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Sizda ruxsat yo'q!", show_alert=True)
        return

    rentals = await get_all_rentals()

    if not rentals:
        await callback.answer("❌ Faol ijaralar yo'q", show_alert=True)
        return

    text = "📋 <b>Barcha faol ijaralar:</b>\n\n"

    buttons = []
    for idx, rental in enumerate(rentals[:10], 1):
        rental_type = "Haftalik" if rental['rental_type'] == 'weekly' else "Oylik"
        text += f"{idx}. 👤 {rental['full_name']} (@{rental['username'] or 'yo\'q'})\n"
        text += f"   🛴 {rental['scooter_name']} ({rental['model']})\n"
        text += f"   📅 {rental['start_date'][:10]} - {rental['end_date'][:10]}\n"
        text += f"   💵 {rental_type}: {rental['total_price']:,.0f} so'm\n"
        text += f"   🆔 ID: {rental['id']}\n"
        text += "━━━━━━━━━━━━━━━\n\n"

        buttons.append([
            InlineKeyboardButton(
                text=f"🔙 #{idx} Qaytarish",
                callback_data=f"return_scooter_{rental['id']}"
            )
        ])

    buttons.append([InlineKeyboardButton(text="◀️ Admin panel", callback_data="admin_panel")])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode='HTML')
    await callback.answer()

@router.message(F.web_app_data)
async def handle_web_app_data(message: Message, state: FSMContext):
    import json
    data = json.loads(message.web_app_data.data)

    rental_id = await create_rental(
        message.from_user.id,
        data['scooter_id'],
        data['rental_type'],
        data['price']
    )

    await state.update_data(rental_id=rental_id, scooter_name=data['scooter_name'])
    await state.set_state(RentalStates.waiting_passport)

    await message.answer(
        f"✅ Ijara so'rovi qabul qilindi!\n\n"
        f"🛴 Skuter: {data['scooter_name']}\n"
        f"💵 Narx: {data['price']:,.0f} so'm\n\n"
        f"📄 Iltimos, pasport rasmini yuboring:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_rental")]
        ])
    )

@router.message(RentalStates.waiting_passport, F.photo)
async def process_passport(message: Message, state: FSMContext):
    data = await state.get_data()
    rental_id = data['rental_id']

    await add_document(message.from_user.id, rental_id, 'passport', message.photo[-1].file_id)
    await state.set_state(RentalStates.waiting_photo)

    await message.answer(
        "✅ Pasport qabul qilindi!\n\n"
        "📸 Endi o'zingizning rasmingizni yuboring:"
    )

@router.message(RentalStates.waiting_photo, F.photo)
async def process_photo(message: Message, state: FSMContext):
    data = await state.get_data()
    rental_id = data['rental_id']

    await add_document(message.from_user.id, rental_id, 'photo', message.photo[-1].file_id)
    await state.set_state(RentalStates.waiting_video)

    await message.answer(
        "✅ Rasm qabul qilindi!\n\n"
        "🎥 Oxirgi qadam: Skuter bilan video yuboring (maksimal 1 daqiqa):"
    )

@router.message(RentalStates.waiting_video, F.video)
async def process_video(message: Message, state: FSMContext):
    data = await state.get_data()
    rental_id = data['rental_id']
    scooter_name = data['scooter_name']

    await add_document(message.from_user.id, rental_id, 'video', message.video.file_id)
    await add_payment(rental_id, 0)

    await message.answer(
        "🎉 <b>Barcha hujjatlar qabul qilindi!</b>\n\n"
        f"✅ Ijara tasdiqlandi: {scooter_name}\n\n"
        "📞 Tez orada admin siz bilan bog'lanadi.\n"
        "💳 To'lovni amalga oshirganingizdan so'ng skuter topshiriladi.",
        reply_markup=get_main_keyboard(message.from_user.id),
        parse_mode='HTML'
    )

    for admin_id in ADMIN_IDS:
        try:
            user = message.from_user
            docs = await get_rental_documents(rental_id)

            text = (
                f"🔔 <b>Yangi ijara so'rovi!</b>\n\n"
                f"👤 Foydalanuvchi: {user.full_name}\n"
                f"📱 Username: @{user.username or 'yo\'q'}\n"
                f"🛴 Skuter: {scooter_name}\n"
                f"🆔 Ijara ID: {rental_id}"
            )

            await bot.send_message(admin_id, text, parse_mode='HTML')

            for doc in docs:
                if doc['doc_type'] == 'passport':
                    await bot.send_photo(admin_id, doc['file_id'], caption="📄 Pasport")
                elif doc['doc_type'] == 'photo':
                    await bot.send_photo(admin_id, doc['file_id'], caption="📸 Shaxsiy rasm")
                elif doc['doc_type'] == 'video':
                    await bot.send_video(admin_id, doc['file_id'], caption="🎥 Skuter bilan video")
        except Exception as e:
            logger.error(f"Adminga xabar yuborishda xato: {e}")

    await state.clear()

@router.callback_query(F.data == "cancel_rental")
async def cancel_rental(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "❌ Ijara bekor qilindi.",
        reply_markup=get_main_keyboard(callback.from_user.id)
    )
    await callback.answer()

async def main():
    await init_db()
    dp.include_router(router)
    dp.include_router(admin_handlers.router)

    # Start reminder service
    reminder_service = ReminderService(bot)
    reminder_service.start()

    logger.info("🚀 Bot ishga tushdi!")
    logger.info("⏰ Eslatma xizmati faol")

    try:
        await dp.start_polling(bot)
    finally:
        reminder_service.stop()

if __name__ == '__main__':
    asyncio.run(main())
