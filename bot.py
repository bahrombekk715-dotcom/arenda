import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, Router
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from dotenv import load_dotenv
from database import init_db, add_user, is_admin

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
    try:
        user = message.from_user
        await add_user(user.id, user.username or '', user.full_name)

        user_is_admin = await is_admin(user.id)

        if user_is_admin:
            webapp_url = f"{WEBAPP_URL}/admin?user_id={user.id}"
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="👨‍💼 Admin Panel", web_app=WebAppInfo(url=webapp_url))]
            ])
            await message.answer(
                f"👋 Salom, <b>{user.full_name}</b>! Admin paneliga xush kelibsiz.",
                reply_markup=keyboard,
                parse_mode='HTML'
            )
        else:
            webapp_url = f"{WEBAPP_URL}?user_id={user.id}"
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🛴 Skuterlarni ko'rish", web_app=WebAppInfo(url=webapp_url))]
            ])
            await message.answer(
                f"👋 Salom, <b>{user.full_name}</b>! Skuter ijarasi xizmatiga xush kelibsiz. 🛴",
                reply_markup=keyboard,
                parse_mode='HTML'
            )

    except Exception as e:
        logger.error(f"Start command error: {e}")
        await message.answer("❌ Xatolik yuz berdi. Iltimos, qaytadan /start bosing.")


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
