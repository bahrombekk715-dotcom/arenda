import asyncio
import logging
import os
import re
from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo,
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
)
from dotenv import load_dotenv
from database import (
    init_db, add_user, get_user, update_user_phone, is_admin
)

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv('BOT_TOKEN')
WEBAPP_URL = os.getenv('WEBAPP_URL', 'http://localhost:5000')

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()

async def send_main_menu(target, user_id: int, full_name: str, user_is_admin: bool):
    """Foydalanuvchiga zamonaviy asosiy menyuni yuborish"""
    catalog_url = f"{WEBAPP_URL}?user_id={user_id}"
    rentals_url = f"{WEBAPP_URL}/my-rentals?user_id={user_id}"
    profile_url = f"{WEBAPP_URL}/profile?user_id={user_id}"

    buttons = [
        [InlineKeyboardButton(text="🛴 Skuterlarni ko'rish", web_app=WebAppInfo(url=catalog_url))],
        [
            InlineKeyboardButton(text="📋 Ijaralarim", web_app=WebAppInfo(url=rentals_url)),
            InlineKeyboardButton(text="👤 Profilim", web_app=WebAppInfo(url=profile_url))
        ]
    ]

    if user_is_admin:
        admin_url = f"{WEBAPP_URL}/admin?user_id={user_id}"
        buttons.insert(0, [InlineKeyboardButton(text="👨‍💼 Admin Panel", web_app=WebAppInfo(url=admin_url))])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    role_badge = "👨‍💼 Admin" if user_is_admin else "🌟 Mijoz"
    text = (
        f"👋 Salom, <b>{full_name}</b>! ({role_badge})\n\n"
        f"🛴 <b>Skuter Ijarasi</b> xizmatiga xush kelibsiz!\n"
        f"Eng qulay shartlarda haftalik va oylik skuter ijarasi.\n\n"
        f"Quyidagi bo'limlardan birini tanlang:"
    )

    if isinstance(target, Message):
        await target.answer(text, reply_markup=keyboard, parse_mode='HTML')
    else:
        await bot.send_message(user_id, text, reply_markup=keyboard, parse_mode='HTML')

@router.message(CommandStart())
async def cmd_start(message: Message):
    try:
        user = message.from_user
        db_user = await get_user(user.id)
        user_is_admin = await is_admin(user.id)

        # Agar foydalanuvchining telefon raqami bo'lmasa -> telefon raqam so'raymiz!
        if not db_user or not db_user['phone']:
            await add_user(user.id, user.username or '', user.full_name)

            contact_keyboard = ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="📱 Telefon raqamni yuborish", request_contact=True)]
                ],
                resize_keyboard=True,
                one_time_keyboard=True
            )

            await message.answer(
                f"👋 Assalomu alaykum, <b>{user.full_name}</b>!\n\n"
                f"🛴 <b>Skuter Ijarasi</b> rasmiy tizimiga xush kelibsiz!\n\n"
                f"Davom etish va skuterlarni ijaraga olish uchun iltimos, <b>telefon raqamingizni yuboring</b>.\n\n"
                f"👇 <i>Pastdagi '📱 Telefon raqamni yuborish' tugmasini bosing:</i>",
                reply_markup=contact_keyboard,
                parse_mode='HTML'
            )
            return

        # Foydalanuvchida telefon raqami allaqachon mavjud
        await add_user(user.id, user.username or '', user.full_name)
        await send_main_menu(message, user.id, user.full_name, user_is_admin)

    except Exception as e:
        logger.error(f"Start command error: {e}")
        await message.answer("❌ Xatolik yuz berdi. Iltimos, qaytadan /start bosing.")

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
            f"✅ <b>Raqamingiz muvaffaqiyatli qabul qilindi:</b> <code>{phone}</code>\n"
            f"Endi tizimdan to'liq foydalanishingiz mumkin! 🚀",
            reply_markup=ReplyKeyboardRemove(),
            parse_mode='HTML'
        )

        user_is_admin = await is_admin(user.id)
        await send_main_menu(message, user.id, user.full_name, user_is_admin)

    except Exception as e:
        logger.error(f"Contact handling error: {e}")
        await message.answer("❌ Telefon raqamini saqlashda xatolik yuz berdi.")

@router.message(Command("profile"))
async def cmd_profile(message: Message):
    try:
        user = message.from_user
        db_user = await get_user(user.id)
        phone = db_user['phone'] if (db_user and db_user['phone']) else "Kiritilmagan"
        profile_url = f"{WEBAPP_URL}/profile?user_id={user.id}"

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="👤 Profilni ochish (Web App)", web_app=WebAppInfo(url=profile_url))]
        ])

        await message.answer(
            f"👤 <b>Foydalanuvchi profili</b>\n\n"
            f"👤 <b>Ism:</b> {user.full_name}\n"
            f"📱 <b>Telefon:</b> {phone}\n"
            f"🆔 <b>Telegram ID:</b> <code>{user.id}</code>\n\n"
            f"Barcha ijaralaringiz va shaxsiy ma'lumotlarni ko'rish uchun quyidagi tugmani bosing:",
            reply_markup=keyboard,
            parse_mode='HTML'
        )
    except Exception as e:
        logger.error(f"Profile cmd error: {e}")

@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "ℹ️ <b>Skuter Ijarasi — Yordam</b>\n\n"
        "🛴 <b>Xizmat haqida:</b>\n"
        "Shahrimizdagi eng qulay va zamonaviy skuterlarni haftalik yoki oylik muddatga ijaraga olishingiz mumkin.\n\n"
        "📌 <b>Mavjud buyruqlar:</b>\n"
        "• /start — Botni ishga tushirish va asosiy menyu\n"
        "• /profile — Shaxsiy profil va ijaralar tarixi\n"
        "• /help — Botdan foydalanish yo'riqnomasi\n\n"
        "📞 Savol va takliflar uchun administrator bilan bog'laning.",
        parse_mode='HTML'
    )

@router.message(F.text)
async def handle_text(message: Message):
    if message.text.startswith('/'):
        return

    clean = re.sub(r'[\s\-\(\)]', '', message.text.strip())
    if re.match(r'^(\+?[0-9]{9,15})$', clean):
        phone = clean
        if not phone.startswith('+'):
            if len(phone) == 9:
                phone = '+998' + phone
            else:
                phone = '+' + phone

        user = message.from_user
        await update_user_phone(user.id, phone)

        await message.answer(
            f"✅ <b>Telefon raqamingiz muvaffaqiyatli saqlandi:</b> <code>{phone}</code>",
            reply_markup=ReplyKeyboardRemove(),
            parse_mode='HTML'
        )

        user_is_admin = await is_admin(user.id)
        await send_main_menu(message, user.id, user.full_name, user_is_admin)
    else:
        db_user = await get_user(message.from_user.id)
        if not db_user or not db_user['phone']:
            contact_keyboard = ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="📱 Telefon raqamni yuborish", request_contact=True)]
                ],
                resize_keyboard=True,
                one_time_keyboard=True
            )
            await message.answer(
                "⚠️ Iltimos, xizmatdan foydalanish uchun quyidagi tugma orqali <b>telefon raqamingizni yuboring</b>:\n"
                "<i>(Yoki +998901234567 shaklida yozing)</i>",
                reply_markup=contact_keyboard,
                parse_mode='HTML'
            )
        else:
            user_is_admin = await is_admin(message.from_user.id)
            await send_main_menu(message, message.from_user.id, message.from_user.full_name, user_is_admin)

async def send_notification(user_id: int, message_text: str):
    try:
        await bot.send_message(user_id, message_text, parse_mode='HTML')
        return True
    except Exception as e:
        logger.error(f"Notification error for user {user_id}: {e}")
        return False

async def send_admin_notification(message_text: str):
    from database import get_all_admins
    admins = await get_all_admins()
    for admin in admins:
        await send_notification(admin['user_id'], message_text)

async def main():
    await init_db()
    dp.include_router(router)

    from reminder import ReminderService
    reminder = ReminderService(bot)
    reminder.start()

    logger.info("🚀 Telegram bot ishga tushdi!")
    logger.info(f"📱 Web App URL: {WEBAPP_URL}")

    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
