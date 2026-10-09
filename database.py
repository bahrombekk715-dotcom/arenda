import aiosqlite
import os
from datetime import datetime, timedelta

DB_PATH = os.getenv('DATABASE_PATH', 'data/scooter_rental.db')

async def init_db():
    os.makedirs('data', exist_ok=True)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                phone TEXT,
                registration_date TEXT,
                is_blocked INTEGER DEFAULT 0,
                is_admin INTEGER DEFAULT 0
            )
        ''')

        # Scooters table o'chirildi - har safar admin nom yozadi

        await db.execute('''
            CREATE TABLE IF NOT EXISTS rentals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                scooter_name TEXT NOT NULL,
                weekly_payment REAL,
                start_date TEXT,
                status TEXT DEFAULT 'active',
                scooter_image TEXT,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')

        await db.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rental_id INTEGER,
                passport_image TEXT,
                video_file TEXT,
                upload_date TEXT,
                FOREIGN KEY (rental_id) REFERENCES rentals (id)
            )
        ''')

        await db.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rental_id INTEGER,
                amount REAL,
                payment_date TEXT,
                FOREIGN KEY (rental_id) REFERENCES rentals (id)
            )
        ''')

        await db.commit()

async def add_user(user_id: int, username: str, full_name: str, phone: str = None):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            INSERT INTO users (user_id, username, full_name, phone, registration_date)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                username = excluded.username,
                full_name = excluded.full_name,
                phone = COALESCE(excluded.phone, users.phone)
        ''', (user_id, username, full_name, phone, datetime.now().isoformat()))
        await db.commit()

async def update_user_phone(user_id: int, phone: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('UPDATE users SET phone = ? WHERE user_id = ?', (phone, user_id))
        await db.commit()

async def update_user_profile(user_id: int, full_name: str = None, phone: str = None):
    async with aiosqlite.connect(DB_PATH) as db:
        if full_name and phone:
            await db.execute('UPDATE users SET full_name = ?, phone = ? WHERE user_id = ?', (full_name, phone, user_id))
        elif full_name:
            await db.execute('UPDATE users SET full_name = ? WHERE user_id = ?', (full_name, user_id))
        elif phone:
            await db.execute('UPDATE users SET phone = ? WHERE user_id = ?', (phone, user_id))
        await db.commit()

async def get_user_profile_data(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT * FROM users WHERE user_id = ?', (user_id,)) as cursor:
            user = await cursor.fetchone()
        if not user:
            return None

        async with db.execute('''
            SELECT r.*, s.name as scooter_name, s.model, s.image_url
            FROM rentals r
            JOIN scooters s ON r.scooter_id = s.id
            WHERE r.user_id = ?
            ORDER BY r.id DESC
        ''', (user_id,)) as cursor:
            rentals = await cursor.fetchall()

        async with db.execute('''
            SELECT SUM(p.amount) as total_spent
            FROM payments p
            JOIN rentals r ON p.rental_id = r.id
            WHERE r.user_id = ? AND p.status = 'paid'
        ''', (user_id,)) as cursor:
            row = await cursor.fetchone()
            total_spent = (row['total_spent'] if row and row['total_spent'] else 0)

        rental_list = [dict(r) for r in rentals]
        active_count = sum(1 for r in rental_list if r['status'] == 'active')

        return {
            'user': dict(user),
            'rentals': rental_list,
            'stats': {
                'total_rentals': len(rental_list),
                'active_rentals': active_count,
                'completed_rentals': len(rental_list) - active_count,
                'total_spent': total_spent
            }
        }

async def get_user(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT * FROM users WHERE user_id = ?', (user_id,)) as cursor:
            return await cursor.fetchone()

async def get_user_by_phone(phone: str):
    """Telefon raqam bo'yicha user qidirish"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT * FROM users WHERE phone = ?', (phone,)) as cursor:
            return await cursor.fetchone()

async def create_rental(user_id: int, scooter_name: str, weekly_payment: float,
                       scooter_image: str = None, passport_image: str = None,
                       video_file: str = None):
    """Admin yangi ijara yaratadi"""
    async with aiosqlite.connect(DB_PATH) as db:
        start_date = datetime.now()

        # Ijarani yaratish
        cursor = await db.execute('''
            INSERT INTO rentals (user_id, scooter_name, weekly_payment, start_date, scooter_image)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, scooter_name, weekly_payment, start_date.isoformat(), scooter_image))

        rental_id = cursor.lastrowid

        # Hujjatlarni saqlash
        if passport_image or video_file:
            await db.execute('''
                INSERT INTO documents (rental_id, passport_image, video_file, upload_date)
                VALUES (?, ?, ?, ?)
            ''', (rental_id, passport_image, video_file, datetime.now().isoformat()))

        await db.commit()
        return rental_id

async def get_all_rentals():
    """Barcha ijaralarni olish (admin uchun)"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('''
            SELECT r.*, u.full_name, u.phone, u.username
            FROM rentals r
            JOIN users u ON r.user_id = u.user_id
            ORDER BY r.id DESC
        ''') as cursor:
            return await cursor.fetchall()

async def get_rental_by_id(rental_id: int):
    """Bitta ijarani olish"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT * FROM rentals WHERE id = ?', (rental_id,)) as cursor:
            return await cursor.fetchone()

async def get_rental_documents(rental_id: int):
    """Ijara hujjatlarini olish"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT * FROM documents WHERE rental_id = ?', (rental_id,)) as cursor:
            return await cursor.fetchone()

async def get_user_rentals(user_id: int, active_only: bool = False):
    """Userning ijaralarini olish"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        query = 'SELECT * FROM rentals WHERE user_id = ?'
        if active_only:
            query += ' AND status = "active"'
        query += ' ORDER BY start_date DESC'
        async with db.execute(query, (user_id,)) as cursor:
            return await cursor.fetchall()

async def add_payment(rental_id: int, amount: float):
    """To'lov qo'shish"""
    async with aiosqlite.connect(DB_PATH) as db:
        payment_date = datetime.now()
        await db.execute('''
            INSERT INTO payments (rental_id, amount, payment_date)
            VALUES (?, ?, ?)
        ''', (rental_id, amount, payment_date.isoformat()))
        await db.commit()

async def get_rental_payments(rental_id: int):
    """Ijara to'lovlarini olish"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            'SELECT * FROM payments WHERE rental_id = ? ORDER BY payment_date DESC',
            (rental_id,)
        ) as cursor:
            return await cursor.fetchall()

async def update_weekly_payment(rental_id: int, new_amount: float):
    """Haftalik to'lovni o'zgartirish"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('UPDATE rentals SET weekly_payment = ? WHERE id = ?', (new_amount, rental_id))
        await db.commit()

async def get_stats():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row

        async with db.execute('SELECT COUNT(*) as total FROM users') as cursor:
            total_users = (await cursor.fetchone())[0]

        async with db.execute('SELECT COUNT(*) as total FROM scooters') as cursor:
            total_scooters = (await cursor.fetchone())[0]

        async with db.execute('SELECT COUNT(*) as total FROM rentals WHERE status = "active"') as cursor:
            active_rentals = (await cursor.fetchone())[0]

        async with db.execute('SELECT SUM(amount) as total FROM payments WHERE status = "paid"') as cursor:
            total_revenue = (await cursor.fetchone())[0] or 0

        return {
            'total_users': total_users,
            'total_scooters': total_scooters,
            'active_rentals': active_rentals,
            'total_revenue': total_revenue
        }

async def is_admin(user_id: int) -> bool:
    """Check if user is admin"""
    import os
    admin_ids = os.getenv('ADMIN_IDS', '')
    if str(user_id) in admin_ids:
        return True

    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT is_admin FROM users WHERE user_id = ?', (user_id,)) as cursor:
            user = await cursor.fetchone()
            return user and user['is_admin'] == 1

async def get_all_admins():
    """Get all admin users"""
    import os
    admin_ids = [int(x) for x in os.getenv('ADMIN_IDS', '').split(',') if x]

    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        placeholders = ','.join('?' * len(admin_ids))
        query = f'SELECT * FROM users WHERE user_id IN ({placeholders}) OR is_admin = 1'
        async with db.execute(query, admin_ids) as cursor:
            return await cursor.fetchall()

async def update_scooter_status(scooter_id: int, status: str):
    """Update scooter status"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('UPDATE scooters SET status = ? WHERE id = ?', (status, scooter_id))
        await db.commit()

async def delete_scooter(scooter_id: int):
    """Delete scooter"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('DELETE FROM scooters WHERE id = ?', (scooter_id,))
        await db.commit()

async def update_scooter(scooter_id: int, name: str, model: str, price_weekly: float, price_monthly: float, image_url: str = None):
    """Update scooter info"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            UPDATE scooters
            SET name = ?, model = ?, price_weekly = ?, price_monthly = ?, image_url = ?
            WHERE id = ?
        ''', (name, model, price_weekly, price_monthly, image_url, scooter_id))
        await db.commit()

async def get_all_users():
    """Get all users"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT * FROM users ORDER BY registration_date DESC') as cursor:
            return await cursor.fetchall()

async def complete_rental(rental_id: int):
    """Mark rental as completed"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('UPDATE rentals SET status = "completed" WHERE id = ?', (rental_id,))

        # Get scooter_id to update status
        async with db.execute('SELECT scooter_id FROM rentals WHERE id = ?', (rental_id,)) as cursor:
            rental = await cursor.fetchone()
            if rental:
                await db.execute('UPDATE scooters SET status = "available" WHERE id = ?', (rental[0],))

        await db.commit()
