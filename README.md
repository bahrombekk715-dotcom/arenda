# 🛴 Skuter Ijarasi - Telegram Bot

Zamonaviy va soddalashtirilgan telegram bot skuter ijarasi xizmati uchun. Qora fon bilan chiroyli web app!

## ✨ Xususiyatlar

### 👤 Userlar uchun:
- 🛴 **Zamonaviy web app** - qora fon bilan chiroyli dizayn
- 📅 **Haftalik/Oylik ijara** - qulay narxlar
- 💰 **To'lovlarni ko'rish** - qancha to'langan, qancha qolgan
- 📊 **Ijaralar tarixi** - barcha ijaralarni ko'rish

### 👨‍💼 Admin uchun:
- ➕ **Skuter qo'shish** - nom, model, narxlar, rasm
- 📄 **Hujjat qabul qilish** - pasport, foto, video
- 💰 **To'lov kiritish** - userga to'lov qabul qilish
- 📋 **Skuterlar ro'yxati** - barcha skuterlarni ko'rish

## 🚀 Render.com'ga deploy qilish

### 1️⃣ GitHub'ga yuklash

```bash
cd /home/bahrom/arenda
git add .
git commit -m "Skuter ijara bot tayyor"
git push origin main
```

### 2️⃣ Render.com'da sozlash

1. [render.com](https://render.com) ga kiring
2. **New +** → **Web Service**
3. GitHub repositoriyangizni ulang
4. Sozlamalar:
   - **Name:** `arenda-bot` (yoki o'zingizga yoqqan nom)
   - **Environment:** `Docker`
   - **Instance Type:** `Free` (yoki `Starter` - $7/oy)

5. **Environment Variables** qo'shing:
   ```
   BOT_TOKEN=your_bot_token_from_botfather
   ADMIN_IDS=your_telegram_id
   WEBAPP_URL=https://arenda-bot.onrender.com
   SECRET_KEY=any_random_string_12345
   PORT=5000
   ```

6. **Create Web Service** tugmasini bosing

### 3️⃣ WEBAPP_URL ni yangilash

Deploy tugagach:
1. Render URL ni oling (masalan: `https://arenda-bot.onrender.com`)
2. Environment Variables'da `WEBAPP_URL` ni yangilang
3. **Manual Deploy** → **Deploy latest commit**

## 💻 Lokal test qilish

```bash
# Virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Paketlarni o'rnatish
pip install -r requirements.txt

# .env faylini sozlash
cp .env.example .env
# .env faylini tahrirlang

# Ishga tushirish
python run.py
```

## 📋 Admin ID ni olish

1. [@userinfobot](https://t.me/userinfobot) ga o'ting
2. `/start` yuboring
3. Sizning ID raqamingizni ko'rsatadi

## 🎯 Qanday ishlaydi?

### Admin:

1. `/start` - Botni ishga tushirish
2. **Admin Panel** tugmasi
3. **Skuter qo'shish** - nom, model, haftalik/oylik narx, rasm
4. **Hujjat qabul qilish** - user ID kiritib, pasport/foto/video qabul qilish
5. **To'lov kiritish** - user ID kiritib, to'lov summasini kiritish

### User:

1. `/start` - Telefon raqam yuborish
2. **Skuterlarni ko'rish** - Web app ochiladi
3. Skuterni tanlash va **Haftalik** yoki **Oylik** tugmasini bosish
4. Ijarani tasdiqlash
5. **Ijaralarim** - qaysi skuterni olgani, qancha to'lov qilgani ko'rinadi

## 🗄️ Database strukturasi

- **users** - Foydalanuvchilar
- **scooters** - Skuterlar
- **rentals** - Ijaralar
- **documents** - Hujjatlar (pasport, foto, video)
- **payments** - To'lovlar

## 🎨 Dizayn

- 🌑 **Qora fon** - zamonaviy gradient
- 💎 **Zamonaviy UI** - chiroyli kartochkalar
- 📱 **Responsive** - barcha qurilmalarda ishlaydi
- ⚡ **Tez** - Telegram Web App

## 🔒 Xavfsizlik

- ✅ Environment variables
- ✅ Admin ID tekshiruvi
- ✅ Telefon raqam autentifikatsiyasi

## 📦 Texnologiyalar

- **Python 3.11**
- **aiogram 3.7.0** - Telegram Bot
- **Flask 3.0.3** - Web App
- **SQLite** - Database
- **Docker** - Containerization

## 🐛 Muammolar

### Bot ishlamayapti:
- `BOT_TOKEN` to'g'ri ekanligini tekshiring
- Render logs'ni ko'ring

### Web app ochilmayapti:
- `WEBAPP_URL` to'g'ri sozlanganligini tekshiring
- Render deploy muvaffaqiyatli bo'lganligini ko'ring

## 📞 Qo'llab-quvvatlash

Muammolar yoki savollar bo'lsa GitHub issues'da yozing.

---

**Muvaffaqiyatli ishlar! 🚀**

Made with ❤️ by Claude Code
