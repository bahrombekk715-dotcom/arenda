# ⚡ Tezkor Boshlash Qo'llanmasi

## 📋 Talab qilinadigan narsalar

- Python 3.11+
- Telegram Bot Token
- Admin Telegram ID

## 🚀 5 daqiqada ishga tushirish

### 1️⃣ Bot yarating

1. Telegram'da [@BotFather](https://t.me/BotFather) ni oching
2. `/newbot` buyrug'ini yuboring
3. Bot nomini kiriting (masalan: `Skuter Ijarasi`)
4. Username kiriting (masalan: `my_scooter_rental_bot`)
5. Bot tokenini saqlang

### 2️⃣ Admin ID ni oling

1. [@userinfobot](https://t.me/userinfobot) ga o'ting
2. `/start` ni bosing
3. ID raqamingizni ko'chirib oling

### 3️⃣ .env faylini sozlang

```bash
nano .env
```

Quyidagilarni to'ldiring:

```env
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
ADMIN_IDS=123456789
WEBAPP_URL=http://localhost:5000
SECRET_KEY=tasodifiy_kalit_yaratish_kerak
DATABASE_PATH=data/scooter_rental.db
```

### 4️⃣ Ishga tushiring

#### A) Oddiy usul (test):

```bash
./start.sh
```

#### B) Docker bilan:

```bash
docker-compose up -d
```

## ✅ Tekshirish

1. Telegram'da botingizni oching
2. `/start` buyrug'ini yuboring
3. Agar "Admin panel" tugmasi ko'rinsa - hammasi ishlayapti! 🎉

## 🌐 Render.com ga deploy

### 1️⃣ GitHub repository yarating

```bash
git init
git add .
git commit -m "Skuter ijara bot"
git remote add origin https://github.com/username/repo.git
git push -u origin main
```

### 2️⃣ Render.com sozlash

1. [render.com](https://render.com) ga kiring
2. **New +** → **Web Service**
3. GitHub reposini ulang
4. Settings:
   - **Environment:** Docker
   - **Instance Type:** Free (yoki Starter)

### 3️⃣ Environment Variables qo'shing

```
BOT_TOKEN=your_token_here
ADMIN_IDS=your_id_here
WEBAPP_URL=https://your-app.onrender.com
SECRET_KEY=random_secret_key
PORT=5000
```

### 4️⃣ Deploy qiling

**Create Web Service** tugmasini bosing va kutib turing (3-5 daqiqa)

## 🛴 Birinchi skuterni qo'shish

1. Botni oching
2. **Admin panel** → **Skuterlar boshqaruvi**
3. **Skuter qo'shish** ni bosing
4. Ma'lumotlarni kiriting:
   - Nom: `Xiaomi M365`
   - Model: `2024`
   - Haftalik: `150000`
   - Oylik: `500000`
   - Rasm yuklang yoki `/skip`

## 📱 Foydalanuvchi tajribasi

1. User botga `/start` yozadi
2. **🛴 Skuterlar** tugmasini bosadi (Web App ochiladi)
3. Skuterni tanlaydi va ijara turini tanlaydi
4. Pasport, foto, video yuklaydi
5. Admin barcha hujjatlarni ko'radi
6. Admin to'lovni qabul qiladi
7. ✅ Skuter topshiriladi!

## 🔥 Pro maslahatlar

### To'lovlarni kuzatish
- **Admin panel** → **Barcha ijaralar**
- Har bir ijarada to'lov tarixi ko'rinadi
- Avtomatik eslatmalar 3 kun oldin yuboriladi

### Skuter qaytarish
- **Admin panel** → **Barcha ijaralar**
- Kerakli ijarada **Qaytarish** tugmasini bosing
- Skuter avtomatik "mavjud" statusga o'tadi

### Statistikani ko'rish
- **Admin panel** → **Statistika**
- Real-time ma'lumotlar:
  - Jami foydalanuvchilar
  - Faol ijaralar
  - Umumiy daromad

## 🐛 Muammolar?

### Bot ishlamayapti
```bash
# Loglarni tekshiring
docker-compose logs -f bot
```

### Web app ochilmayapti
- `.env` da `WEBAPP_URL` to'g'ri ekanligini tekshiring
- Render.com deploy statusini ko'ring

### Database xatosi
```bash
rm -rf data/
python bot.py  # Avtomatik qayta yaratiladi
```

## 📞 Qo'llab-quvvatlash

Yordam kerakmi?
- 📧 Email: support@example.com
- 💬 Telegram: @yourusername

---

**Omad! 🚀 Savollar bo'lsa so'rang!**
