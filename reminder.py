import asyncio
import logging
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from database import get_all_rentals, get_rental_payments
from aiogram import Bot
import os

logger = logging.getLogger(__name__)

class ReminderService:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.scheduler = AsyncIOScheduler()

    def start(self):
        self.scheduler.add_job(
            self.check_payment_reminders,
            CronTrigger(hour=9, minute=0),
            id='payment_reminder',
            name='Kunlik to\'lov eslatmalari'
        )

        self.scheduler.add_job(
            self.check_rental_expiry,
            CronTrigger(hour=10, minute=0),
            id='rental_expiry',
            name='Ijara tugashi eslatmasi'
        )

        self.scheduler.start()
        logger.info("⏰ Eslatma xizmati ishga tushdi")

    async def check_payment_reminders(self):
        """Har kuni ertalab to'lov eslatmalarini yuboradi"""
        try:
            rentals = await get_all_rentals()
            today = datetime.now()

            for rental in rentals:
                payments = await get_rental_payments(rental['id'])

                if payments:
                    last_payment = payments[0]
                    next_payment_date = datetime.fromisoformat(last_payment['next_payment_date'])
                    days_left = (next_payment_date - today).days

                    if days_left == 3:
                        await self._send_payment_reminder(
                            rental['user_id'],
                            rental['scooter_name'],
                            days_left,
                            rental['rental_type']
                        )
                    elif days_left == 1:
                        await self._send_payment_reminder(
                            rental['user_id'],
                            rental['scooter_name'],
                            days_left,
                            rental['rental_type'],
                            urgent=True
                        )
                    elif days_left <= 0:
                        await self._send_overdue_notice(
                            rental['user_id'],
                            rental['scooter_name'],
                            abs(days_left)
                        )

        except Exception as e:
            logger.error(f"To'lov eslatmalarida xatolik: {e}")

    async def check_rental_expiry(self):
        """Ijara tugash sanasini tekshiradi"""
        try:
            rentals = await get_all_rentals()
            today = datetime.now()

            for rental in rentals:
                end_date = datetime.fromisoformat(rental['end_date'])
                days_left = (end_date - today).days

                if days_left == 7:
                    await self._send_expiry_reminder(
                        rental['user_id'],
                        rental['scooter_name'],
                        days_left
                    )
                elif days_left == 1:
                    await self._send_expiry_reminder(
                        rental['user_id'],
                        rental['scooter_name'],
                        days_left,
                        urgent=True
                    )

        except Exception as e:
            logger.error(f"Ijara tugashi eslatmasida xatolik: {e}")

    async def _send_payment_reminder(self, user_id: int, scooter_name: str, days_left: int, rental_type: str, urgent: bool = False):
        """To'lov eslatmasini yuboradi"""
        try:
            icon = "⚠️" if urgent else "🔔"
            rental_text = "haftalik" if rental_type == "weekly" else "oylik"

            text = (
                f"{icon} <b>To'lov eslatmasi</b>\n\n"
                f"🛴 Skuter: {scooter_name}\n"
                f"📅 To'lov turi: {rental_text}\n"
                f"⏰ Qolgan kunlar: {days_left} kun\n\n"
            )

            if urgent:
                text += "❗️ To'lovni ertaga amalga oshiring!"
            else:
                text += "💡 To'lovni vaqtida amalga oshiring."

            await self.bot.send_message(user_id, text, parse_mode='HTML')

        except Exception as e:
            logger.error(f"Eslatma yuborishda xatolik (user {user_id}): {e}")

    async def _send_overdue_notice(self, user_id: int, scooter_name: str, days_overdue: int):
        """To'lov kechikishi haqida xabar"""
        try:
            text = (
                f"🚨 <b>To'lov kechikdi!</b>\n\n"
                f"🛴 Skuter: {scooter_name}\n"
                f"⏰ Kechikkan kunlar: {days_overdue} kun\n\n"
                f"📞 Iltimos, tezda to'lovni amalga oshiring yoki admin bilan bog'laning."
            )

            await self.bot.send_message(user_id, text, parse_mode='HTML')

        except Exception as e:
            logger.error(f"Kechikish xabari yuborishda xatolik (user {user_id}): {e}")

    async def _send_expiry_reminder(self, user_id: int, scooter_name: str, days_left: int, urgent: bool = False):
        """Ijara tugashi haqida xabar"""
        try:
            icon = "⚠️" if urgent else "📅"

            text = (
                f"{icon} <b>Ijara tugashi yaqinlashmoqda</b>\n\n"
                f"🛴 Skuter: {scooter_name}\n"
                f"⏰ Qolgan vaqt: {days_left} kun\n\n"
            )

            if urgent:
                text += "❗️ Ijara ertaga tugaydi. Agar davom ettirmoqchi bo'lsangiz, admin bilan bog'laning."
            else:
                text += "💡 Ijara muddatini uzaytirish uchun admin bilan bog'laning."

            await self.bot.send_message(user_id, text, parse_mode='HTML')

        except Exception as e:
            logger.error(f"Tugash eslatmasi yuborishda xatolik (user {user_id}): {e}")

    def stop(self):
        """Schedulerni to'xtatadi"""
        self.scheduler.shutdown()
        logger.info("⏰ Eslatma xizmati to'xtatildi")
