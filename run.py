import asyncio
import threading
import logging
import sys
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_webapp(bot_instance):
    import webapp
    from webapp import app
    webapp.set_bot(bot_instance)
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

async def main():
    from database import init_db
    from aiogram import Bot, Dispatcher, Router
    from aiogram.filters import CommandStart
    from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
    from dotenv import load_dotenv
    import os

    load_dotenv()
    await init_db()

    BOT_TOKEN = os.getenv('BOT_TOKEN')
    WEBAPP_URL = os.getenv('WEBAPP_URL', 'http://localhost:5000')

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    router = Router()

    from database import add_user, is_admin

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
                    reply_markup=keyboard, parse_mode='HTML'
                )
            else:
                webapp_url = f"{WEBAPP_URL}?user_id={user.id}"
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🛴 Skuterlarni ko'rish", web_app=WebAppInfo(url=webapp_url))]
                ])
                await message.answer(
                    f"👋 Salom, <b>{user.full_name}</b>! Skuter ijarasi xizmatiga xush kelibsiz. 🛴",
                    reply_markup=keyboard, parse_mode='HTML'
                )
        except Exception as e:
            logger.error(f"Start: {e}")
            await message.answer("❌ Xatolik yuz berdi. Iltimos, /start bosing.")

    dp.include_router(router)

    # Reminder
    from reminder import ReminderService
    reminder = ReminderService(bot)
    reminder.start()

    # Start webapp thread with bot reference
    webapp_thread = threading.Thread(target=run_webapp, args=(bot,), daemon=True)
    webapp_thread.start()
    logger.info("✅ Web app ishga tushdi (port 5000)")

    logger.info("🚀 Telegram bot ishga tushdi!")
    logger.info(f"📱 Web App URL: {WEBAPP_URL}")

    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Tizim to'xtatildi")
        sys.exit(0)
