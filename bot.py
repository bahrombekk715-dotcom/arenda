import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import CommandStart
from aiogram.types import (
    Message, InlineKeyboardMarkup, InlineKeyboardButton,
    WebAppInfo, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove,
    BotCommand, MenuButtonWebApp
)
from dotenv import load_dotenv
from database import init_db, add_user, get_user, update_user_phone, is_admin

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv('BOT_TOKEN')
WEBAPP_URL = os.getenv('WEBAPP_URL', 'http://localhost:5000')

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    """Start command - foydalanuvchi ro'yxatdan o'tadi"""
    try:
        user = message.from_user
        db_user = await get_user(user.id)
        user_is_admin = await is_admin(user.id)

        # Admin uchun telefon raqam shart emas
        if user_is_admin:
            await add_user(user.id, user.username or '', user.full_name, phone='admin')
            await send_main_menu(message, user.id, user.full_name, user_is_admin)
            return

        # Oddiy user uchun telefon raqam kerak
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
    """Telefon raqamni qabul qilish"""
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

async def send_main_menu(message: Message, user_id: int, full_name: str, user_is_admin: bool):
    """Asosiy menyu"""
    role_badge = "👨‍💼 Admin" if user_is_admin else "🌟 Mijoz"

    if user_is_admin:
        # Admin uchun faqat Admin Panel
        admin_url = f"{WEBAPP_URL}/admin?user_id={user_id}"
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="👨‍💼 Admin Panel", web_app=WebAppInfo(url=admin_url))]]
        )

        text = (
            f"👋 Salom, <b>{full_name}</b>! ({role_badge})\n\n"
            f"🛴 <b>Admin Panel</b>ga xush kelibsiz!\n\n"
            f"Quyidagi tugmani bosing:"
        )

        # Menu button o'rnatish
        try:
            await bot.set_chat_menu_button(
                chat_id=user_id,
                menu_button=MenuButtonWebApp(
                    text="👨‍💼 Admin Panel",
                    web_app=WebAppInfo(url=admin_url)
                )
            )
        except Exception as e:
            logger.error(f"Menu button o'rnatishda xatolik: {e}")
    else:
        # Oddiy user uchun faqat Mening ijaralarim
        my_rentals_url = f"{WEBAPP_URL}/my-rentals?user_id={user_id}"
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="📋 Mening Ijaralarim", web_app=WebAppInfo(url=my_rentals_url))]]
        )

        text = (
            f"👋 Salom, <b>{full_name}</b>! ({role_badge})\n\n"
            f"🛴 <b>Skuter Ijarasi</b> tizimiga xush kelibsiz!\n\n"
            f"Quyidagi tugmani bosing:"
        )

        # Menu button o'rnatish
        try:
            await bot.set_chat_menu_button(
                chat_id=user_id,
                menu_button=MenuButtonWebApp(
                    text="📋 Mening Ijaralarim",
                    web_app=WebAppInfo(url=my_rentals_url)
                )
            )
        except Exception as e:
            logger.error(f"Menu button o'rnatishda xatolik: {e}")

    await message.answer(text, reply_markup=keyboard, parse_mode='HTML')

@router.message(F.text)
async def handle_text(message: Message):
    """Oddiy matn xabarlarni qayta ishlash"""
    user = message.from_user
    user_is_admin = await is_admin(user.id)
    await send_main_menu(message, user.id, user.full_name, user_is_admin)

async def send_notification(user_id: int, message_text: str):
    """Userga bildirishnoma yuborish"""
    try:
        await bot.send_message(user_id, message_text, parse_mode='HTML')
        return True
    except Exception as e:
        logger.error(f"Notification error for user {user_id}: {e}")
        return False

async def main():
    await init_db()
    dp.include_router(router)

    logger.info("🚀 Telegram bot ishga tushdi!")
    logger.info(f"📱 Web App URL: {WEBAPP_URL}")

    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
