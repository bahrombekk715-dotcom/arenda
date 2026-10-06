import os
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database import get_all_rentals, add_payment, get_rental_payments, get_scooter
import aiosqlite

router = Router()
DB_PATH = os.getenv('DATABASE_PATH', 'data/scooter_rental.db')

class PaymentStates(StatesGroup):
    waiting_rental_id = State()
    waiting_amount = State()

def is_admin(user_id: int) -> bool:
    ADMIN_IDS = [int(x) for x in os.getenv('ADMIN_IDS', '').split(',') if x]
    return user_id in ADMIN_IDS

@router.callback_query(F.data == "process_payment")
async def process_payment_start(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Sizda ruxsat yo'q!", show_alert=True)
        return

    rentals = await get_all_rentals()

    if not rentals:
        await callback.answer("❌ Faol ijaralar yo'q", show_alert=True)
        return

    text = "💳 <b>To'lov qabul qilish</b>\n\nIjara ID raqamini kiriting:\n\n"

    for rental in rentals[:10]:
        text += f"🆔 {rental['id']}: {rental['full_name']} - {rental['scooter_name']}\n"

    await state.set_state(PaymentStates.waiting_rental_id)
    await callback.message.answer(text, parse_mode='HTML')
    await callback.answer()

@router.message(PaymentStates.waiting_rental_id)
async def process_rental_id(message: Message, state: FSMContext):
    try:
        rental_id = int(message.text)
        await state.update_data(rental_id=rental_id)
        await state.set_state(PaymentStates.waiting_amount)
        await message.answer("💵 To'lov summasini kiriting (so'mda):")
    except ValueError:
        await message.answer("❌ Iltimos, faqat raqam kiriting!")

@router.message(PaymentStates.waiting_amount)
async def process_payment_amount(message: Message, state: FSMContext):
    try:
        amount = float(message.text)
        data = await state.get_data()
        rental_id = data['rental_id']

        await add_payment(rental_id, amount)

        # Get rental info
        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute('''
                SELECT r.*, s.name as scooter_name, u.user_id, u.full_name
                FROM rentals r
                JOIN scooters s ON r.scooter_id = s.id
                JOIN users u ON r.user_id = u.user_id
                WHERE r.id = ?
            ''', (rental_id,)) as cursor:
                rental = await cursor.fetchone()

        if rental:
            # Notify user
            from bot import bot
            await bot.send_message(
                rental['user_id'],
                f"✅ <b>To'lov qabul qilindi!</b>\n\n"
                f"🛴 Skuter: {rental['scooter_name']}\n"
                f"💵 Summa: {amount:,.0f} so'm\n\n"
                f"Rahmat! Keyingi to'lov sanasini botdan ko'rishingiz mumkin.",
                parse_mode='HTML'
            )

        await message.answer(
            f"✅ To'lov muvaffaqiyatli qabul qilindi!\n\n"
            f"🆔 Ijara ID: {rental_id}\n"
            f"💵 Summa: {amount:,.0f} so'm",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="◀️ Orqaga", callback_data="admin_panel")]
            ])
        )
        await state.clear()

    except ValueError:
        await message.answer("❌ Iltimos, to'g'ri summa kiriting!")
    except Exception as e:
        await message.answer(f"❌ Xatolik: {str(e)}")
        await state.clear()

@router.callback_query(F.data.startswith("return_scooter_"))
async def return_scooter(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Sizda ruxsat yo'q!", show_alert=True)
        return

    rental_id = int(callback.data.split("_")[2])

    async with aiosqlite.connect(DB_PATH) as db:
        # Get rental info
        db.row_factory = aiosqlite.Row
        async with db.execute('''
            SELECT r.*, s.id as scooter_id, s.name as scooter_name
            FROM rentals r
            JOIN scooters s ON r.scooter_id = s.id
            WHERE r.id = ?
        ''', (rental_id,)) as cursor:
            rental = await cursor.fetchone()

        if rental:
            # Mark rental as completed
            await db.execute(
                'UPDATE rentals SET status = "completed" WHERE id = ?',
                (rental_id,)
            )

            # Make scooter available again
            await db.execute(
                'UPDATE scooters SET status = "available" WHERE id = ?',
                (rental['scooter_id'],)
            )

            await db.commit()

            await callback.answer("✅ Skuter qaytarildi!", show_alert=True)
            await callback.message.edit_text(
                f"✅ <b>Skuter qaytarildi</b>\n\n"
                f"🛴 {rental['scooter_name']}\n"
                f"🆔 Ijara ID: {rental_id}\n\n"
                f"Skuter yana ijaraga tayyor!",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="◀️ Admin panel", callback_data="admin_panel")]
                ]),
                parse_mode='HTML'
            )
        else:
            await callback.answer("❌ Ijara topilmadi!", show_alert=True)

@router.callback_query(F.data == "manage_scooters")
async def manage_scooters(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ Sizda ruxsat yo'q!", show_alert=True)
        return

    from database import get_all_scooters
    scooters_data = await get_all_scooters()

    text = "🛴 <b>Skuterlar boshqaruvi</b>\n\n"

    if not scooters_data:
        text += "❌ Skuterlar yo'q"
    else:
        for scooter in scooters_data:
            status_emoji = "✅" if scooter['status'] == 'available' else "🔴"
            text += f"{status_emoji} <b>{scooter['name']}</b> ({scooter['model']})\n"
            text += f"   💵 Haftalik: {scooter['price_weekly']:,.0f} | Oylik: {scooter['price_monthly']:,.0f}\n\n"

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Skuter qo'shish", callback_data="add_scooter")],
        [InlineKeyboardButton(text="◀️ Orqaga", callback_data="admin_panel")]
    ])

    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode='HTML')
    await callback.answer()
