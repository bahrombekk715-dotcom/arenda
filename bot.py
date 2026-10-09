import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    Message, InlineKeyboardMarkup, InlineKeyboardButton,
    WebAppInfo, CallbackQuery, ReplyKeyboardMarkup,
    KeyboardButton, ReplyKeyboardRemove
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from dotenv import load_dotenv
from database import (
    init_db, add_user, get_user, update_user_phone, is_admin,
    add_scooter, get_all_scooters_admin, add_document,
    add_payment, get_user_rentals, get_rental_payments
)

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv('BOT_TOKEN')
WEBAPP_URL = os.getenv('WEBAPP_URL', 'http://localhost:5000')

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()

# States
class AddScooter(StatesGroup):
    name = State()
    model = State()
    price_weekly = State()
    price_monthly = State()
    image = State()

class UploadDocs(StatesGroup):
    waiting_rental_id = State()
    waiting_passport = State()
    waiting_photo = State()
    waiting_video = State()

class AddPayment(StatesGroup):
    waiting_user_id = State()
    waiting_amount = State()

# Asosiy menyu
async def send_main_menu(message: Message, user_id: int, full_name: str, user_is_admin: bool):
    """Foydalanuvchiga asosiy menyuni yuborish"""
    catalog_url = f"{WEBAPP_URL}?user_id={user_id}"

    buttons = [
        [InlineKeyboardButton(text="🛴 Skuterlarni ko'rish", web_app=WebAppInfo(url=catalog_url))]
    ]

    if user_is_admin:
        buttons.append([InlineKeyboardButton(text="👨‍💼 Admin Panel", callback_data="admin_panel")])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    role_badge = "👨‍💼 Admin" if user_is_admin else "🌟 Mijoz"
    text = (
        f"👋 Salom, <b>{full_name}</b>! ({role_badge})\n\n"
        f"🛴 <b>Skuter Ijarasi</b> xizmatiga xush kelibsiz!\n"
        f"Haftalik va oylik skuter ijarasi.\n\n"
        f"Quyidagi tugmani bosing:"
    )

    await message.answer(text, reply_markup=keyboard, parse_mode='HTML')

# Admin panel
async def send_admin_panel(callback: CallbackQuery):
    """Admin panel menyusi"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Skuter qo'shish", callback_data="add_scooter")],
        [InlineKeyboardButton(text="📋 Skuterlar ro'yxati", callback_data="list_scooters")],
        [InlineKeyboardButton(text="📄 Hujjat qabul qilish", callback_data="accept_docs")],
        [InlineKeyboardButton(text="💰 To'lov kiritish", callback_data="add_payment")],
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_main")]
    ])

    await callback.message.edit_text(
        "👨‍💼 <b>Admin Panel</b>\n\nKerakli bo'limni tanlang:",
        reply_markup=keyboard,
        parse_mode='HTML'
    )

@router.message(CommandStart())
async def cmd_start(message: Message):
    try:
        user = message.from_user
        db_user = await get_user(user.id)
        user_is_admin = await is_admin(user.id)

        # Telefon raqam yo'q bo'lsa so'raymiz
        if not db_user or not db_user['phone']:
            await add_user(user.id, user.username or '', user.full_name)

            contact_keyboard = ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text="📱 Telefon raqamni yuborish", request_contact=True)]],
                resize_keyboard=True,
                one_time_keyboard=True
            )

            await message.answer(
                f"👋 Assalomu alaykum, <b>{user.full_name}</b>!\n\n"
                f"🛴 <b>Skuter Ijarasi</b> tizimiga xush kelibsiz!\n\n"
                f"Davom etish uchun <b>telefon raqamingizni yuboring</b>.\n\n"
                f"👇 Pastdagi tugmani bosing:",
                reply_markup=contact_keyboard,
                parse_mode='HTML'
            )
            return

        await add_user(user.id, user.username or '', user.full_name)
        await send_main_menu(message, user.id, user.full_name, user_is_admin)

    except Exception as e:
        logger.error(f"Start command error: {e}")
        await message.answer("❌ Xatolik yuz berdi. Qaytadan /start bosing.")

@router.message(F.contact)
async def handle_contact(message: Message):
    try:
        contact = message.contact
        phone = contact.phone_number.strip()
        if not phone.startswith('+'):
            phone = '+' + phone

        user = message.from_user
        await update_user_phone(user.id, phone)

        await message.answer(
            f"✅ <b>Raqamingiz qabul qilindi:</b> <code>{phone}</code>\n"
            f"Endi tizimdan foydalanishingiz mumkin! 🚀",
            reply_markup=ReplyKeyboardRemove(),
            parse_mode='HTML'
        )

        user_is_admin = await is_admin(user.id)
        await send_main_menu(message, user.id, user.full_name, user_is_admin)

    except Exception as e:
        logger.error(f"Contact handling error: {e}")
        await message.answer("❌ Telefon raqamini saqlashda xatolik yuz berdi.")

# Admin callbacks
@router.callback_query(F.data == "admin_panel")
async def admin_panel_handler(callback: CallbackQuery):
    if not await is_admin(callback.from_user.id):
        await callback.answer("❌ Sizda admin huquqi yo'q!", show_alert=True)
        return
    await send_admin_panel(callback)

@router.callback_query(F.data == "back_to_main")
async def back_to_main(callback: CallbackQuery):
    user = callback.from_user
    user_is_admin = await is_admin(user.id)

    catalog_url = f"{WEBAPP_URL}?user_id={user.id}"
    buttons = [[InlineKeyboardButton(text="🛴 Skuterlarni ko'rish", web_app=WebAppInfo(url=catalog_url))]]

    if user_is_admin:
        buttons.append([InlineKeyboardButton(text="👨‍💼 Admin Panel", callback_data="admin_panel")])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    await callback.message.edit_text(
        f"👋 Salom, <b>{user.full_name}</b>!\n\n🛴 <b>Skuter Ijarasi</b>",
        reply_markup=keyboard,
        parse_mode='HTML'
    )

# Skuter qo'shish
@router.callback_query(F.data == "add_scooter")
async def add_scooter_start(callback: CallbackQuery, state: FSMContext):
    if not await is_admin(callback.from_user.id):
        await callback.answer("❌ Sizda admin huquqi yo'q!", show_alert=True)
        return

    await state.set_state(AddScooter.name)
    await callback.message.answer("📝 Skuter nomini kiriting:")
    await callback.answer()

@router.message(AddScooter.name)
async def scooter_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(AddScooter.model)
    await message.answer("📝 Skuter modelini kiriting:")

@router.message(AddScooter.model)
async def scooter_model(message: Message, state: FSMContext):
    await state.update_data(model=message.text)
    await state.set_state(AddScooter.price_weekly)
    await message.answer("💰 Haftalik narxini kiriting (faqat raqam):")

@router.message(AddScooter.price_weekly)
async def scooter_weekly(message: Message, state: FSMContext):
    try:
        price = float(message.text)
        await state.update_data(price_weekly=price)
        await state.set_state(AddScooter.price_monthly)
        await message.answer("💰 Oylik narxini kiriting (faqat raqam):")
    except:
        await message.answer("❌ Iltimos faqat raqam kiriting!")

@router.message(AddScooter.price_monthly)
async def scooter_monthly(message: Message, state: FSMContext):
    try:
        price = float(message.text)
        await state.update_data(price_monthly=price)
        await state.set_state(AddScooter.image)

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⏩ O'tkazib yuborish", callback_data="skip_image")]
        ])
        await message.answer("📸 Skuter rasmini yuboring (yoki o'tkazing):", reply_markup=keyboard)
    except:
        await message.answer("❌ Iltimos faqat raqam kiriting!")

@router.callback_query(F.data == "skip_image")
async def skip_scooter_image(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    scooter_id = await add_scooter(
        data['name'],
        data['model'],
        data['price_weekly'],
        data['price_monthly']
    )

    await state.clear()
    await callback.message.answer(
        f"✅ Skuter muvaffaqiyatli qo'shildi!\n\n"
        f"📋 <b>{data['name']}</b>\n"
        f"🏷 Model: {data['model']}\n"
        f"💰 Haftalik: {data['price_weekly']:,.0f} so'm\n"
        f"💰 Oylik: {data['price_monthly']:,.0f} so'm",
        parse_mode='HTML'
    )
    await callback.answer()

@router.message(AddScooter.image, F.photo)
async def scooter_image(message: Message, state: FSMContext):
    data = await state.get_data()
    photo_id = message.photo[-1].file_id

    scooter_id = await add_scooter(
        data['name'],
        data['model'],
        data['price_weekly'],
        data['price_monthly'],
        photo_id
    )

    await state.clear()
    await message.answer(
        f"✅ Skuter muvaffaqiyatli qo'shildi!\n\n"
        f"📋 <b>{data['name']}</b>\n"
        f"🏷 Model: {data['model']}\n"
        f"💰 Haftalik: {data['price_weekly']:,.0f} so'm\n"
        f"💰 Oylik: {data['price_monthly']:,.0f} so'm",
        parse_mode='HTML'
    )

# Skuterlar ro'yxati
@router.callback_query(F.data == "list_scooters")
async def list_scooters(callback: CallbackQuery):
    if not await is_admin(callback.from_user.id):
        await callback.answer("❌ Sizda admin huquqi yo'q!", show_alert=True)
        return

    scooters = await get_all_scooters_admin()

    if not scooters:
        await callback.message.answer("📋 Skuterlar ro'yxati bo'sh")
        await callback.answer()
        return

    text = "📋 <b>Barcha skuterlar:</b>\n\n"
    for s in scooters:
        status_emoji = "✅" if s['status'] == 'available' else "🔴"
        text += (
            f"{status_emoji} <b>{s['name']}</b> ({s['model']})\n"
            f"   💰 Haftalik: {s['price_weekly']:,.0f} so'm\n"
            f"   💰 Oylik: {s['price_monthly']:,.0f} so'm\n"
            f"   📊 Status: {s['status']}\n\n"
        )

    await callback.message.answer(text, parse_mode='HTML')
    await callback.answer()

# Hujjat qabul qilish
@router.callback_query(F.data == "accept_docs")
async def accept_docs_start(callback: CallbackQuery, state: FSMContext):
    if not await is_admin(callback.from_user.id):
        await callback.answer("❌ Sizda admin huquqi yo'q!", show_alert=True)
        return

    await state.set_state(UploadDocs.waiting_rental_id)
    await callback.message.answer(
        "📄 <b>Hujjat qabul qilish</b>\n\n"
        "Userning Telegram ID sini kiriting:",
        parse_mode='HTML'
    )
    await callback.answer()

@router.message(UploadDocs.waiting_rental_id)
async def get_rental_id(message: Message, state: FSMContext):
    try:
        user_id = int(message.text)
        user = await get_user(user_id)

        if not user:
            await message.answer("❌ Bunday user topilmadi!")
            return

        rentals = await get_user_rentals(user_id, active_only=True)

        if not rentals:
            await message.answer("❌ Bu userda faol ijara yo'q!")
            return

        await state.update_data(rental_id=rentals[0]['id'], user_id=user_id)
        await state.set_state(UploadDocs.waiting_passport)
        await message.answer(
            f"✅ User topildi: {user['full_name']}\n\n"
            f"📄 Endi pasport rasmini yuboring:"
        )
    except:
        await message.answer("❌ Iltimos to'g'ri Telegram ID kiriting!")

@router.message(UploadDocs.waiting_passport, F.photo)
async def get_passport(message: Message, state: FSMContext):
    data = await state.get_data()
    photo_id = message.photo[-1].file_id

    await add_document(data['user_id'], data['rental_id'], 'passport', photo_id)
    await state.set_state(UploadDocs.waiting_photo)
    await message.answer("✅ Pasport saqlandi!\n\n📸 Endi shaxsiy foto yuboring:")

@router.message(UploadDocs.waiting_photo, F.photo)
async def get_photo(message: Message, state: FSMContext):
    data = await state.get_data()
    photo_id = message.photo[-1].file_id

    await add_document(data['user_id'], data['rental_id'], 'photo', photo_id)
    await state.set_state(UploadDocs.waiting_video)
    await message.answer("✅ Foto saqlandi!\n\n🎥 Endi skuter bilan video yuboring:")

@router.message(UploadDocs.waiting_video, F.video)
async def get_video(message: Message, state: FSMContext):
    data = await state.get_data()
    video_id = message.video.file_id

    await add_document(data['user_id'], data['rental_id'], 'video', video_id)
    await state.clear()
    await message.answer(
        "✅ Barcha hujjatlar muvaffaqiyatli saqlandi!\n\n"
        "📋 Pasport ✅\n"
        "📸 Foto ✅\n"
        "🎥 Video ✅"
    )

# To'lov kiritish
@router.callback_query(F.data == "add_payment")
async def add_payment_start(callback: CallbackQuery, state: FSMContext):
    if not await is_admin(callback.from_user.id):
        await callback.answer("❌ Sizda admin huquqi yo'q!", show_alert=True)
        return

    await state.set_state(AddPayment.waiting_user_id)
    await callback.message.answer(
        "💰 <b>To'lov kiritish</b>\n\n"
        "Userning Telegram ID sini kiriting:",
        parse_mode='HTML'
    )
    await callback.answer()

@router.message(AddPayment.waiting_user_id)
async def payment_get_user(message: Message, state: FSMContext):
    try:
        user_id = int(message.text)
        user = await get_user(user_id)

        if not user:
            await message.answer("❌ Bunday user topilmadi!")
            return

        rentals = await get_user_rentals(user_id, active_only=True)

        if not rentals:
            await message.answer("❌ Bu userda faol ijara yo'q!")
            return

        await state.update_data(rental_id=rentals[0]['id'], user_id=user_id)
        await state.set_state(AddPayment.waiting_amount)
        await message.answer(
            f"✅ User: {user['full_name']}\n"
            f"🛴 Skuter: {rentals[0]['scooter_name']}\n\n"
            f"💰 To'lov summasini kiriting:"
        )
    except:
        await message.answer("❌ Iltimos to'g'ri Telegram ID kiriting!")

@router.message(AddPayment.waiting_amount)
async def payment_amount(message: Message, state: FSMContext):
    try:
        amount = float(message.text)
        data = await state.get_data()

        await add_payment(data['rental_id'], amount)
        await state.clear()

        # Userga xabar yuboramiz
        await bot.send_message(
            data['user_id'],
            f"✅ <b>To'lovingiz qabul qilindi!</b>\n\n"
            f"💰 Summa: {amount:,.0f} so'm\n"
            f"📅 Sana: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M')}",
            parse_mode='HTML'
        )

        await message.answer(
            f"✅ To'lov muvaffaqiyatli kiritildi!\n"
            f"💰 Summa: {amount:,.0f} so'm\n\n"
            f"User xabardor qilindi!"
        )
    except:
        await message.answer("❌ Iltimos to'g'ri summa kiriting!")

@router.message(F.text)
async def handle_text(message: Message):
    user = message.from_user
    user_is_admin = await is_admin(user.id)
    await send_main_menu(message, user.id, user.full_name, user_is_admin)

async def main():
    await init_db()
    dp.include_router(router)

    logger.info("🚀 Telegram bot ishga tushdi!")
    logger.info(f"📱 Web App URL: {WEBAPP_URL}")

    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
