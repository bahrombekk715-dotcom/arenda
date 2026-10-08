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

        await db.execute('''
            CREATE TABLE IF NOT EXISTS scooters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                model TEXT,
                price_weekly REAL,
                price_monthly REAL,
                status TEXT DEFAULT 'available',
                image_url TEXT
            )
        ''')

        await db.execute('''
            CREATE TABLE IF NOT EXISTS rentals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                scooter_id INTEGER,
                rental_type TEXT,
                start_date TEXT,
                end_date TEXT,
                total_price REAL,
                status TEXT DEFAULT 'active',
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                FOREIGN KEY (scooter_id) REFERENCES scooters (id)
            )
        ''')

        await db.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                rental_id INTEGER,
                doc_type TEXT,
                file_id TEXT,
                upload_date TEXT,
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                FOREIGN KEY (rental_id) REFERENCES rentals (id)
            )
        ''')

        await db.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rental_id INTEGER,
                amount REAL,
                payment_date TEXT,
                next_payment_date TEXT,
                status TEXT DEFAULT 'pending',
                FOREIGN KEY (rental_id) REFERENCES rentals (id)
            )
        ''')

        await db.commit()

async def add_user(user_id: int, username: str, full_name: str, phone: str = None):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            INSERT OR REPLACE INTO users (user_id, username, full_name, phone, registration_date)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, username, full_name, phone, datetime.now().isoformat()))
        await db.commit()

async def get_user(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT * FROM users WHERE user_id = ?', (user_id,)) as cursor:
            return await cursor.fetchone()

async def add_scooter(name: str, model: str, price_weekly: float, price_monthly: float, image_url: str = None):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute('''
            INSERT INTO scooters (name, model, price_weekly, price_monthly, image_url)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, model, price_weekly, price_monthly, image_url))
        await db.commit()
        return cursor.lastrowid

async def get_all_scooters():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT * FROM scooters WHERE status = "available"') as cursor:
            return await cursor.fetchall()

async def get_all_scooters_admin():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT * FROM scooters ORDER BY id DESC') as cursor:
            return await cursor.fetchall()

async def get_scooter(scooter_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT * FROM scooters WHERE id = ?', (scooter_id,)) as cursor:
            return await cursor.fetchone()

async def create_rental(user_id: int, scooter_id: int, rental_type: str, total_price: float):
    async with aiosqlite.connect(DB_PATH) as db:
        start_date = datetime.now()
        if rental_type == 'weekly':
            end_date = start_date + timedelta(days=7)
        else:
            end_date = start_date + timedelta(days=30)

        cursor = await db.execute('''
            INSERT INTO rentals (user_id, scooter_id, rental_type, start_date, end_date, total_price)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, scooter_id, rental_type, start_date.isoformat(), end_date.isoformat(), total_price))

        await db.execute('UPDATE scooters SET status = "rented" WHERE id = ?', (scooter_id,))
        await db.commit()
        return cursor.lastrowid

async def add_document(user_id: int, rental_id: int, doc_type: str, file_id: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            INSERT INTO documents (user_id, rental_id, doc_type, file_id, upload_date)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, rental_id, doc_type, file_id, datetime.now().isoformat()))
        await db.commit()

async def get_user_rentals(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('''
            SELECT r.*, s.name as scooter_name, s.model
            FROM rentals r
            JOIN scooters s ON r.scooter_id = s.id
            WHERE r.user_id = ? AND r.status = "active"
        ''', (user_id,)) as cursor:
            return await cursor.fetchall()

async def get_all_rentals():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('''
            SELECT r.*, s.name as scooter_name, s.model, u.full_name, u.username
            FROM rentals r
            JOIN scooters s ON r.scooter_id = s.id
            JOIN users u ON r.user_id = u.user_id
            WHERE r.status = "active"
            ORDER BY r.start_date DESC
        ''') as cursor:
            return await cursor.fetchall()

async def get_rental_documents(rental_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT * FROM documents WHERE rental_id = ?', (rental_id,)) as cursor:
            return await cursor.fetchall()

async def add_payment(rental_id: int, amount: float):
    async with aiosqlite.connect(DB_PATH) as db:
        payment_date = datetime.now()
        async with db.execute('SELECT rental_type FROM rentals WHERE id = ?', (rental_id,)) as cursor:
            rental = await cursor.fetchone()
            if rental:
                if rental[0] == 'weekly':
                    next_payment = payment_date + timedelta(days=7)
                else:
                    next_payment = payment_date + timedelta(days=30)

                await db.execute('''
                    INSERT INTO payments (rental_id, amount, payment_date, next_payment_date, status)
                    VALUES (?, ?, ?, ?, ?)
                ''', (rental_id, amount, payment_date.isoformat(), next_payment.isoformat(), 'paid'))
                await db.commit()

async def get_rental_payments(rental_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            'SELECT * FROM payments WHERE rental_id = ? ORDER BY payment_date DESC',
            (rental_id,)
        ) as cursor:
            return await cursor.fetchall()

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
