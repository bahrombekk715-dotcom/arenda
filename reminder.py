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
            from database import get_all_active_rentals_with_info

            rentals = await get_all_active_rentals_with_info()
            logger.info(f"To'lov eslatmalari tekshirilmoqda: {len(rentals)} ta aktiv ijara")

            for rental in rentals:
                # Kechikkan to'lovlar uchun har kuni xabar
                if rental.get('overdue_days', 0) > 0:
                    await self._send_overdue_notice(
                        rental['user_id'],
                        rental['scooter_name'],
                        rental['overdue_days'],
                        rental['debt_amount']
                    )
                    logger.info(f"Kechikish xabari yuborildi: user_id={rental['user_id']}, kunlar={rental['overdue_days']}")

                # Yaqinlashayotgan to'lov sanasi uchun ogohlantirish
                elif rental.get('status') == 'warning':
                    paid_until = datetime.fromisoformat(rental['paid_until'])
                    days_left = (paid_until - datetime.now()).days

                    if days_left <= 3 and days_left > 0:
                        await self._send_payment_reminder(
                            rental['user_id'],
                            rental['scooter_name'],
                            days_left,
                            rental['weekly_payment']
                        )
                        logger.info(f"Eslatma yuborildi: user_id={rental['user_id']}, qolgan kunlar={days_left}")

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

    async def _send_payment_reminder(self, user_id: int, scooter_name: str, days_left: int, weekly_payment: float):
        """To'lov eslatmasini yuboradi"""
        try:
            icon = "⚠️" if days_left <= 1 else "🔔"

            text = (
                f"{icon} <b>To'lov eslatmasi</b>\n\n"
                f"🛴 Skuter: {scooter_name}\n"
                f"💵 Haftalik to'lov: {weekly_payment:,.0f} so'm\n"
                f"⏰ Qolgan kunlar: {days_left} kun\n\n"
            )

            if days_left <= 1:
                text += "❗️ To'lovni tezda amalga oshiring!"
            else:
                text += "💡 To'lovni vaqtida amalga oshiring."

            await self.bot.send_message(user_id, text, parse_mode='HTML')

        except Exception as e:
            logger.error(f"Eslatma yuborishda xatolik (user {user_id}): {e}")

    async def _send_overdue_notice(self, user_id: int, scooter_name: str, days_overdue: int, debt_amount: float):
        """To'lov kechikishi haqida xabar (har kuni yuboriladi)"""
        try:
            text = (
                f"🚨 <b>To'lov kechikdi!</b>\n\n"
                f"🛴 Skuter: {scooter_name}\n"
                f"⏰ Kechikkan kunlar: {days_overdue} kun\n"
                f"💰 Qarz: {debt_amount:,.0f} so'm\n\n"
                f"📞 Iltimos, tezda to'lovni amalga oshiring yoki admin bilan bog'laning.\n\n"
                f"ℹ️ Har kechikkan kun uchun qarz hisoblanib boradi."
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
