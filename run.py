import asyncio
import threading
import logging
import subprocess
import sys
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_webapp():
    """Flask web app ni alohida thread'da ishga tushirish"""
    import webapp
    from webapp import app
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

def run_bot():
    """Telegram botni ishga tushirish"""
    import bot
    asyncio.run(bot.main())

if __name__ == '__main__':
    logger.info("🚀 Skuter Ijarasi tizimini ishga tushirish...")

    # Web app'ni alohida thread'da ishga tushirish
    webapp_thread = threading.Thread(target=run_webapp, daemon=True)
    webapp_thread.start()
    logger.info("✅ Web app ishga tushdi (port 5000)")

    # Botni asosiy thread'da ishga tushirish
    time.sleep(2)  # Web app'ning to'liq yuklanishini kutish
    logger.info("✅ Telegram bot ishga tushmoqda...")

    try:
        run_bot()
    except KeyboardInterrupt:
        logger.info("🛑 Tizim to'xtatildi")
        sys.exit(0)
