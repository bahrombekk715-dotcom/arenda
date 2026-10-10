import asyncpg
import os
from datetime import datetime, timedelta, timezone

DATABASE_URL = os.getenv('DATABASE_URL')
_pool = None

def now_uzbekistan():
    """O'zbekiston vaqti (UTC+5)"""
    return datetime.now(timezone(timedelta(hours=5)))

async def get_pool():
    """Get or create connection pool"""
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(
            DATABASE_URL,
            min_size=1,
            max_size=10,
            command_timeout=60
        )
    return _pool

async def init_db():
    """Database jadvallarini yaratish"""
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id BIGINT PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                phone TEXT,
                registration_date TIMESTAMP,
                is_blocked INTEGER DEFAULT 0,
                is_admin INTEGER DEFAULT 0
            )
        ''')

        await conn.execute('''
            CREATE TABLE IF NOT EXISTS rentals (
                id SERIAL PRIMARY KEY,
                user_id BIGINT REFERENCES users(user_id),
                scooter_name TEXT NOT NULL,
                weekly_payment REAL,
                start_date TIMESTAMP,
                status TEXT DEFAULT 'active',
                scooter_image TEXT
            )
        ''')

        await conn.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id SERIAL PRIMARY KEY,
                rental_id INTEGER REFERENCES rentals(id) ON DELETE CASCADE,
                passport_image TEXT,
                video_file TEXT,
                upload_date TIMESTAMP
            )
        ''')

        await conn.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                id SERIAL PRIMARY KEY,
                rental_id INTEGER REFERENCES rentals(id) ON DELETE CASCADE,
                amount REAL,
                payment_date TIMESTAMP
            )
        ''')

        print("✅ Database tables created/verified")

async def add_user(user_id: int, username: str, full_name: str, phone: str = None):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute('''
            INSERT INTO users (user_id, username, full_name, phone, registration_date)
            VALUES ($1, $2, $3, $4, $5)
            ON CONFLICT(user_id) DO UPDATE SET
                username = EXCLUDED.username,
                full_name = EXCLUDED.full_name,
                phone = COALESCE(EXCLUDED.phone, users.phone)
        ''', user_id, username, full_name, phone, now_uzbekistan())

async def update_user_phone(user_id: int, phone: str):
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute('UPDATE users SET phone = $1 WHERE user_id = $2', phone, user_id)

async def update_user_profile(user_id: int, full_name: str = None, phone: str = None):
    pool = await get_pool()
    async with pool.acquire() as conn:
        if full_name and phone:
            await conn.execute('UPDATE users SET full_name = $1, phone = $2 WHERE user_id = $3', full_name, phone, user_id)
        elif full_name:
            await conn.execute('UPDATE users SET full_name = $1 WHERE user_id = $2', full_name, user_id)
        elif phone:
            await conn.execute('UPDATE users SET phone = $1 WHERE user_id = $2', phone, user_id)

async def get_user(user_id: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow('SELECT * FROM users WHERE user_id = $1', user_id)
        return dict(row) if row else None

async def get_user_by_phone(phone: str):
    """Telefon raqam bo'yicha user qidirish"""
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow('SELECT * FROM users WHERE phone = $1', phone)
        return dict(row) if row else None

async def create_rental(user_id: int, scooter_name: str, weekly_payment: float,
                       scooter_image: str = None, passport_image: str = None,
                       video_file: str = None):
    """Admin yangi ijara yaratadi"""
    pool = await get_pool()
    async with pool.acquire() as conn:
        start_date = now_uzbekistan()

        # Ijarani yaratish - status ni aniq belgilaymiz
        rental_id = await conn.fetchval('''
            INSERT INTO rentals (user_id, scooter_name, weekly_payment, start_date, status, scooter_image)
            VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING id
        ''', user_id, scooter_name, weekly_payment, start_date, 'active', scooter_image)

        print(f"Created rental {rental_id} with status 'active'")

        # Hujjatlarni saqlash
        if passport_image or video_file:
            await conn.execute('''
                INSERT INTO documents (rental_id, passport_image, video_file, upload_date)
                VALUES ($1, $2, $3, $4)
            ''', rental_id, passport_image, video_file, now_uzbekistan())

        return rental_id

async def get_all_rentals():
    """Barcha ijaralarni olish (admin uchun)"""
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch('''
            SELECT r.*, u.full_name, u.phone, u.username
            FROM rentals r
            JOIN users u ON r.user_id = u.user_id
            ORDER BY r.id DESC
        ''')
        return [dict(row) for row in rows]

async def get_rental_by_id(rental_id: int):
    """Bitta ijarani olish"""
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow('SELECT * FROM rentals WHERE id = $1', rental_id)
        return dict(row) if row else None

async def get_rental_documents(rental_id: int):
    """Ijara hujjatlarini olish"""
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow('SELECT * FROM documents WHERE rental_id = $1', rental_id)
        return dict(row) if row else None

async def get_user_rentals(user_id: int, active_only: bool = False):
    """Userning ijaralarini olish"""
    pool = await get_pool()
    async with pool.acquire() as conn:
        query = 'SELECT * FROM rentals WHERE user_id = $1'
        if active_only:
            query += ' AND status = \'active\''
        query += ' ORDER BY start_date DESC'
        rows = await conn.fetch(query, user_id)
        return [dict(row) for row in rows]

async def add_payment(rental_id: int, amount: float):
    """To'lov qo'shish"""
    pool = await get_pool()
    async with pool.acquire() as conn:
        payment_date = now_uzbekistan()
        await conn.execute('''
            INSERT INTO payments (rental_id, amount, payment_date)
            VALUES ($1, $2, $3)
        ''', rental_id, amount, payment_date)
        print(f"Payment added: {amount} to rental {rental_id}")

async def get_rental_payments(rental_id: int):
    """Ijara to'lovlarini olish"""
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            'SELECT * FROM payments WHERE rental_id = $1 ORDER BY payment_date DESC',
            rental_id
        )
        return [dict(row) for row in rows]

async def update_weekly_payment(rental_id: int, new_amount: float):
    """Haftalik to'lovni o'zgartirish"""
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute('UPDATE rentals SET weekly_payment = $1 WHERE id = $2', new_amount, rental_id)

async def is_admin(user_id: int) -> bool:
    """Check if user is admin"""
    admin_ids = os.getenv('ADMIN_IDS', '')
    if str(user_id) in admin_ids:
        return True

    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow('SELECT is_admin FROM users WHERE user_id = $1', user_id)
        return row and row['is_admin'] == 1

async def get_all_admins():
    """Get all admin users"""
    admin_ids = [int(x) for x in os.getenv('ADMIN_IDS', '').split(',') if x]

    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch('SELECT * FROM users WHERE user_id = ANY($1::bigint[]) OR is_admin = 1', admin_ids)
        return [dict(row) for row in rows]

async def get_all_users():
    """Get all users"""
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch('SELECT * FROM users ORDER BY registration_date DESC')
        return [dict(row) for row in rows]

async def complete_rental(rental_id: int):
    """Skuterni topshirish - barcha ma'lumotlarni o'chirish"""
    import os as os_module

    pool = await get_pool()
    async with pool.acquire() as conn:
        # 1. Hujjat fayllarini olish
        doc = await conn.fetchrow('SELECT passport_image, video_file FROM documents WHERE rental_id = $1', rental_id)
        if doc:
            if doc['passport_image']:
                file_path = doc['passport_image'].lstrip('/')
                if os_module.path.exists(file_path):
                    try:
                        os_module.remove(file_path)
                    except Exception as e:
                        print(f"Error deleting passport file: {e}")

            if doc['video_file']:
                file_path = doc['video_file'].lstrip('/')
                if os_module.path.exists(file_path):
                    try:
                        os_module.remove(file_path)
                    except Exception as e:
                        print(f"Error deleting video file: {e}")

        # 2. Skuter rasmini olish va o'chirish
        rental = await conn.fetchrow('SELECT scooter_image FROM rentals WHERE id = $1', rental_id)
        if rental and rental['scooter_image']:
            scooter_img = rental['scooter_image'].lstrip('/')
            if os_module.path.exists(scooter_img):
                try:
                    os_module.remove(scooter_img)
                except Exception as e:
                    print(f"Error deleting scooter image: {e}")

        # 3. PostgreSQL CASCADE bilan avtomatik o'chiradi payments va documents ni
        await conn.execute('DELETE FROM rentals WHERE id = $1', rental_id)

        print(f"Rental {rental_id} successfully deleted with all files")

async def get_rental_payment_info(rental_id: int):
    """Ijara to'lov holatini hisoblash"""
    pool = await get_pool()
    async with pool.acquire() as conn:
        rental = await conn.fetchrow('SELECT * FROM rentals WHERE id = $1', rental_id)
        if not rental:
            return None

        payments = await conn.fetch(
            'SELECT * FROM payments WHERE rental_id = $1 ORDER BY payment_date ASC',
            rental_id
        )

        weekly_payment = rental['weekly_payment']
        start_date = rental['start_date']
        total_paid = sum(p['amount'] for p in payments)

        if weekly_payment <= 0:
            return {
                'rental_id': rental_id,
                'total_paid': total_paid,
                'paid_until': None,
                'paid_until_formatted': None,
                'next_payment_date': None,
                'next_payment_formatted': None,
                'overdue_days': 0,
                'debt_amount': 0,
                'weekly_payment': weekly_payment,
                'status': 'unknown'
            }

        # Qancha haftalik to'langan
        paid_weeks = total_paid / weekly_payment
        paid_until = start_date + timedelta(weeks=paid_weeks)

        now = now_uzbekistan()

        # Keyingi to'lov sanasi = paid_until
        next_payment_date = paid_until

        # Kechikkan kunlar va qarz hisoblash
        if now > paid_until:
            overdue_days = (now - paid_until).days
            # Har kechikkan kun uchun kunlik to'lov hisoblash
            daily_rate = weekly_payment / 7.0
            # Qarz = kunlik to'lov × kechikkan kunlar
            debt_amount = overdue_days * daily_rate
            status = 'overdue'
        else:
            overdue_days = 0
            debt_amount = 0.0
            days_left = (paid_until - now).days
            if days_left <= 3:
                status = 'warning'
            else:
                status = 'active'

        return {
            'rental_id': rental_id,
            'total_paid': total_paid,
            'paid_until': paid_until.isoformat(),
            'paid_until_formatted': paid_until.strftime('%d.%m.%Y'),
            'next_payment_date': next_payment_date.isoformat(),
            'next_payment_formatted': next_payment_date.strftime('%d.%m.%Y'),
            'overdue_days': overdue_days,
            'debt_amount': round(debt_amount, 0),
            'weekly_payment': weekly_payment,
            'daily_rate': round(daily_rate, 0),
            'status': status
        }

async def get_all_overdue_rentals():
    """Barcha kechikkan to'lovli ijaralar"""
    pool = await get_pool()
    async with pool.acquire() as conn:
        rentals = await conn.fetch('''
            SELECT r.*, u.full_name, u.phone, u.username, u.user_id
            FROM rentals r
            JOIN users u ON r.user_id = u.user_id
            WHERE r.status = 'active'
            ORDER BY r.start_date ASC
        ''')

        result = []
        for rental in rentals:
            info = await get_rental_payment_info(rental['id'])
            if info and info['overdue_days'] > 0:
                rental_dict = dict(rental)
                rental_dict.update(info)
                result.append(rental_dict)

        result.sort(key=lambda x: x['overdue_days'], reverse=True)
        return result

async def get_all_active_rentals_with_info():
    """Barcha aktiv ijaralar to'lov ma'lumotlari bilan"""
    pool = await get_pool()
    async with pool.acquire() as conn:
        rentals = await conn.fetch('''
            SELECT r.*, u.full_name, u.phone, u.username, u.user_id
            FROM rentals r
            JOIN users u ON r.user_id = u.user_id
            WHERE r.status = 'active'
            ORDER BY r.start_date DESC
        ''')

        result = []
        for rental in rentals:
            rental_dict = dict(rental)
            info = await get_rental_payment_info(rental['id'])
            if info:
                rental_dict.update(info)
            result.append(rental_dict)

        return result
