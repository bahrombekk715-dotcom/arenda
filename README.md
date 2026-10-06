# 🛴 Skuter Ijarasi Telegram Bot

**Zamonaviy va professional telegram bot skuter ijarasi biznesini boshqarish uchun.**

## ✨ Asosiy imkoniyatlar

### 👥 Foydalanuvchilar uchun:
- 🛴 **Web App orqali skuterlarni ko'rish** - chiroyli va zamonaviy interfeys
- 📅 **Haftalik/Oylik ijara** - qulay to'lov rejalari
- 📄 **Hujjat yuklash** - pasport, foto, video
- 💳 **To'lovlarni kuzatish** - real-time monitoring
- 📱 **Telegram ichida ishlash** - qulaylik va tezkor

### 👨‍💼 Adminlar uchun:
- 📊 **Real-time statistika** - foydalanuvchilar, ijaralar, daromad
- 🛴 **Skuter boshqaruvi** - qo'shish, o'zgartirish, status
- 📋 **Barcha ijaralarni ko'rish** - to'liq monitoring
- 📨 **Avtomatik xabarnomalar** - yangi so'rovlar haqida
- 🗂️ **Hujjatlarni ko'rish** - pasport, foto, video

## 🚀 Tezkor boshlash

### 1️⃣ Telegram Bot yaratish

1. [@BotFather](https://t.me/BotFather) ga o'ting
2. `/newbot` buyrug'ini yuboring
3. Bot nomini va username'ini kiriting
4. Bot tokenini oling

### 2️⃣ Fayllarni tayyorlash

```bash
cd /home/bahrom/Desktop/code
cp .env.example .env
```

### 3️⃣ `.env` faylini to'ldiring

```env
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
ADMIN_IDS=123456789,987654321
WEBAPP_URL=https://your-app-name.onrender.com
SECRET_KEY=your_random_secret_key_here_change_this
DATABASE_PATH=data/scooter_rental.db
```

**Admin ID ni qanday olish:**
1. [@userinfobot](https://t.me/userinfobot) ga o'ting
2. `/start` ni yuboring
3. Sizning ID raqamingizni ko'rsatadi

### 4️⃣ Render.com da deploy qilish

#### A) GitHub repository yarating

```bash
cd /home/bahrom/Desktop/code
git init
git add .
git commit -m "Initial commit: Skuter ijara bot"
git branch -M main
git remote add origin https://github.com/username/scooter-bot.git
git push -u origin main
```

#### B) Render.com da sozlash

1. [render.com](https://render.com) ga kiring
2. **New +** → **Web Service**
3. GitHub repositoriyangizni ulang
4. Sozlamalar:
   - **Name:** `scooter-rental-bot`
   - **Environment:** `Docker`
   - **Instance Type:** `Free` (yoki `Starter`)
   
5. **Environment Variables** qo'shing:
   ```
   BOT_TOKEN=your_bot_token
   ADMIN_IDS=your_admin_ids
   WEBAPP_URL=https://scooter-rental-bot.onrender.com
   SECRET_KEY=your_secret_key
   PORT=5000
   ```

6. **Create Web Service** tugmasini bosing

#### C) WEBAPP_URL ni yangilash

1. Deploy tugagach, Render URL ni oling (masalan: `https://scooter-rental-bot.onrender.com`)
2. `.env` faylida `WEBAPP_URL` ni yangilang
3. Render.com da Environment Variables da ham yangilang
4. Redeploy qiling

## 💻 Lokal ishga tushirish (test uchun)

### Docker bilan:

```bash
docker-compose up --build
```

### Docker siz:

```bash
# Virtual environment yaratish
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Paketlarni o'rnatish
pip install -r requirements.txt

# Botni ishga tushirish (terminal 1)
python bot.py

# Web app ni ishga tushirish (terminal 2)
python webapp.py
```

## 📋 Foydalanish

### 1️⃣ Skuter qo'shish (Admin)

1. Botni oching
2. **Admin panel** tugmasini bosing
3. **Skuter qo'shish** ni tanlang
4. Bot sizdan so'raydi:
   - Skuter nomi
   - Modeli
   - Haftalik narx
   - Oylik narx
   - Rasm (ixtiyoriy)

### 2️⃣ Ijara olish (User)

1. **🛴 Skuterlar** tugmasini bosing (Web App ochiladi)
2. Kerakli skuterni tanlang
3. Haftalik yoki oylik ijarani tanlang
4. **Ijarani tasdiqlash** tugmasini bosing
5. Bot sizdan so'raydi:
   - 📄 Pasport rasmi
   - 📸 Shaxsiy foto
   - 🎥 Skuter bilan video

6. ✅ Hujjatlar adminga yuboriladi

### 3️⃣ Statistikani ko'rish (Admin)

1. **Admin panel** → **Statistika**
2. Ko'rasiz:
   - Jami foydalanuvchilar
   - Jami skuterlar
   - Faol ijaralar
   - Umumiy daromad

## 📁 Loyiha strukturasi

```
code/
├── bot.py                 # Telegram bot asosiy fayl
├── webapp.py              # Flask web application
├── database.py            # Ma'lumotlar bazasi funksiyalari
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker konfiguratsiyasi
├── docker-compose.yml    # Docker Compose
├── .env.example          # Environment o'zgaruvchilar namunasi
├── .gitignore           # Git ignore fayli
│
├── templates/           # HTML shablonlar
│   ├── index.html       # Asosiy sahifa (skuterlar ro'yxati)
│   └── rental_detail.html
│
├── static/              # Static fayllar
│   ├── css/
│   │   └── style.css    # Zamonaviy dizayn
│   └── js/
│       └── app.js       # Frontend logika
│
└── data/                # Ma'lumotlar bazasi (avtomatik yaratiladi)
    └── scooter_rental.db
```

## 🗄️ Ma'lumotlar bazasi strukturasi

### Tables:
- **users** - Foydalanuvchilar
- **scooters** - Skuterlar
- **rentals** - Ijaralar
- **documents** - Hujjatlar (pasport, foto, video)
- **payments** - To'lovlar

## 🎨 Dizayn xususiyatlari

- ✨ **Modern UI/UX** - Zamonaviy va chiroyli interfeys
- 📱 **Responsive** - Barcha qurilmalarda ishlaydi
- 🌗 **Light mode** - Yorug' ranglar
- 🎯 **User-friendly** - Qulay va sodda
- ⚡ **Fast** - Tez yuklanadi va ishlaydi

## 🔒 Xavfsizlik

- ✅ Environment variables orqali maxfiy ma'lumotlar
- ✅ Admin ID tekshiruvi
- ✅ Foydalanuvchi autentifikatsiyasi
- ✅ Ma'lumotlar bazasi SQLite (production uchun PostgreSQL tavsiya etiladi)

## 🛠️ Kengaytirish imkoniyatlari

### Qo'shimcha funksiyalar qo'shish:

1. **To'lov tizimlari integratsiyasi**
   - Click
   - Payme
   - Uzum

2. **SMS xabarnomalar**
   - Eskiz.uz
   - PlayMobile

3. **Lokatsiya tracking**
   - GPS monitoring
   - Geo-fencing

4. **Avtomatik eslatmalar**
   - To'lov muddati haqida
   - Ijara tugashi haqida

5. **Statistika va hisobotlar**
   - Kunlik/oylik hisobotlar
   - Export Excel/PDF

## 🐛 Muammolarni hal qilish

### Bot ishlamayapti:
```bash
# Loglarni ko'ring
docker-compose logs -f

# yoki
python bot.py
```

### Web app ochilmayapti:
- WEBAPP_URL to'g'ri sozlanganligini tekshiring
- Render.com deploy muvaffaqiyatli tugaganligini ko'ring

### Ma'lumotlar bazasi xatoligi:
```bash
# data papkasini qayta yarating
rm -rf data/
python bot.py  # Avtomatik yaratiladi
```

## 📞 Yordam va qo'llab-quvvatlash

Muammolar yoki takliflar bo'lsa:
- 📧 Email: support@example.com
- 💬 Telegram: @yourusername
- 🐛 Issues: GitHub repository

## 📜 Litsenziya

MIT License - erkin foydalanish va o'zgartirish mumkin

## 🙏 Credits

- **aiogram** - Telegram Bot framework
- **Flask** - Web framework
- **SQLite** - Database
- **Docker** - Containerization

---

**Muvaffaqiyatli ishlar! 🚀**

Made with ❤️ by Claude Code
