import asyncio
import threading
import logging
import sys
import os
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_webapp(bot_instance):
    import webapp
    from webapp import app
    webapp.set_bot(bot_instance)
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

async def main():
    load_dotenv()
    from database import init_db
    await init_db()

    from bot import bot, dp, router, WEBAPP_URL
    dp.include_router(router)

    from reminder import ReminderService
    reminder = ReminderService(bot)
    reminder.start()

    # Start webapp thread with bot reference
    webapp_thread = threading.Thread(target=run_webapp, args=(bot,), daemon=True)
    webapp_thread.start()
    logger.info(f"✅ Web app ishga tushdi: {WEBAPP_URL}")

    logger.info("🚀 Telegram bot ishga tushdi!")
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Tizim to'xtatildi")
        sys.exit(0)
