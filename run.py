import asyncio
import threading
import logging
import sys
import os
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_webapp():
    """Flask web app ni alohida thread'da ishga tushirish"""
    from webapp import app
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

async def main():
    load_dotenv()

    # Database'ni ishga tushirish
    from database import init_db
    await init_db()
    logger.info("✅ Database ishga tushdi")

    # Bot'ni sozlash
    from bot import bot, dp, router, WEBAPP_URL
    dp.include_router(router)

    # Web app'ni alohida thread'da ishga tushirish
    webapp_thread = threading.Thread(target=run_webapp, daemon=True)
    webapp_thread.start()
    logger.info(f"✅ Web app ishga tushdi: {WEBAPP_URL}")

    # Eslatma xizmatini ishga tushirish
    from reminder import ReminderService
    reminder_service = ReminderService(bot)
    reminder_service.start()
    logger.info("✅ Eslatma xizmati ishga tushdi")

    logger.info("🚀 Telegram bot ishga tushdi!")
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Tizim to'xtatildi")
        sys.exit(0)
