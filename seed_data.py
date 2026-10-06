"""
Test ma'lumotlarni qo'shish uchun skript
Bu skript bilan siz test skuterlarni avtomatik qo'shishingiz mumkin
"""
import asyncio
from database import init_db, add_scooter

async def seed_database():
    """Test skuterlarni qo'shish"""
    print("🌱 Ma'lumotlar bazasini to'ldirish boshlandi...")

    await init_db()

    # Test skuterlar
    test_scooters = [
        {
            "name": "Xiaomi M365",
            "model": "2024 Pro",
            "price_weekly": 150000,
            "price_monthly": 500000,
            "image_url": None
        },
        {
            "name": "Ninebot ES2",
            "model": "Standard",
            "price_weekly": 120000,
            "price_monthly": 400000,
            "image_url": None
        },
        {
            "name": "Kugoo S1",
            "model": "Pro",
            "price_weekly": 100000,
            "price_monthly": 350000,
            "image_url": None
        },
        {
            "name": "Xiaomi Pro 2",
            "model": "Premium",
            "price_weekly": 200000,
            "price_monthly": 650000,
            "image_url": None
        },
        {
            "name": "Segway Max",
            "model": "G30",
            "price_weekly": 180000,
            "price_monthly": 600000,
            "image_url": None
        }
    ]

    for scooter in test_scooters:
        scooter_id = await add_scooter(**scooter)
        print(f"✅ Qo'shildi: {scooter['name']} (ID: {scooter_id})")

    print(f"\n🎉 {len(test_scooters)} ta test skuter muvaffaqiyatli qo'shildi!")
    print("🚀 Endi botni ishga tushirishingiz mumkin: python bot.py")

if __name__ == "__main__":
    asyncio.run(seed_database())
