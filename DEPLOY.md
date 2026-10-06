# 🎯 DEPLOY.md - Render.com ga Deploy Qilish

## 📦 Tayyorgarlik

### 1. GitHub Repository yaratish

```bash
cd /home/bahrom/Desktop/code

# Git init
git init
git add .
git commit -m "Initial commit: Professional Scooter Rental Bot"

# GitHub ga push (avval GitHub da repository yarating)
git remote add origin https://github.com/USERNAME/scooter-rental-bot.git
git branch -M main
git push -u origin main
```

## 🚀 Render.com Deploy

### 2. Render.com da Web Service yaratish

1. [render.com](https://render.com) ga kiring (GitHub bilan)
2. Dashboard → **New +** → **Web Service**
3. Repository ni tanlang: `scooter-rental-bot`

### 3. Service sozlamalari

| Setting | Value |
|---------|-------|
| **Name** | `scooter-rental-bot` |
| **Region** | `Frankfurt (EU Central)` yoki eng yaqin |
| **Branch** | `main` |
| **Root Directory** | (bo'sh qoldiring) |
| **Environment** | `Docker` |
| **Instance Type** | `Free` (test) yoki `Starter $7/mo` (production) |

### 4. Environment Variables qo'shish

**Environment** bo'limida quyidagilarni qo'shing:

```env
BOT_TOKEN=7123456789:AAEXAMPLEtokenHEREchangeThis
ADMIN_IDS=123456789,987654321
WEBAPP_URL=https://scooter-rental-bot.onrender.com
SECRET_KEY=your_random_32_character_secret_key_here
PORT=5000
DATABASE_PATH=data/scooter_rental.db
```

⚠️ **Muhim:**
- `BOT_TOKEN` - [@BotFather](https://t.me/BotFather) dan olingan token
- `ADMIN_IDS` - [@userinfobot](https://t.me/userinfobot) dan olingan ID
- `WEBAPP_URL` - Render URL ni to'ldiring (keyinroq)
- `SECRET_KEY` - Tasodifiy 32+ belgilar

### 5. Deploy qilish

1. **Create Web Service** tugmasini bosing
2. Deploy jarayoni boshlanadi (3-5 daqiqa)
3. Loglarni kuzating:
   ```
   ==> Building...
   ==> Deploying...
   ==> Starting...
   ✅ Bot ishga tushdi!
   ⏰ Eslatma xizmati faol
   ```

### 6. WEBAPP_URL ni yangilash

Deploy tugagach:

1. Render URL ni ko'chirib oling (masalan: `https://scooter-rental-bot.onrender.com`)
2. **Environment** bo'limiga o'ting
3. `WEBAPP_URL` ni yangilang
4. **Manual Deploy** → **Deploy latest commit**

## ✅ Tekshirish

### Bot ishlayotganini tekshirish:

1. Telegram'da botingizni oching
2. `/start` buyrug'ini yuboring
3. Javob kelishi kerak: "👋 Assalomu alaykum..."
4. **Admin panel** tugmasi ko'rinishini tekshiring

### Web App tekshirish:

1. **🛴 Skuterlar** tugmasini bosing
2. Web App ochilishi kerak
3. Skuterlar ro'yxati ko'rinishi kerak

## 🔄 Yangilash (Update)

Kodni o'zgartirganingizdan keyin:

```bash
git add .
git commit -m "Update: yangilangan funksiyalar"
git push

# Render avtomatik yangi versiyani deploy qiladi
```

## 📊 Monitoring

### Render Dashboard'da:

- **Logs** - Real-time loglar
- **Metrics** - CPU, Memory, Requests
- **Events** - Deploy tarixi

### Loglarni ko'rish:

```bash
# Render CLI (ixtiyoriy)
render logs -t scooter-rental-bot
```

## 🐛 Muammolarni hal qilish

### Bot javob bermayapti:

1. **Logs** ni tekshiring:
   - `BOT_TOKEN` to'g'rimi?
   - Xatolar bormi?

2. **Environment Variables** ni tekshiring
3. **Restart** tugmasini bosing

### Web App ochilmayapti:

1. `WEBAPP_URL` to'g'ri sozlanganini tekshiring
2. SSL sertifikat faol ekanligini tekshiring
3. Deploy tugaganini kutib turing

### Database xatolari:

1. `data/` papkasi Render da saqlanmaydi (ephemeral)
2. **Disk** qo'shish kerak:
   - Settings → **Disks**
   - **Add Disk**
   - Mount Path: `/app/data`
   - Size: 1GB (Free tier: 0)

## 💾 Persistent Storage (Recommended)

Free tier da disk yo'q. Production uchun:

### PostgreSQL qo'shish:

1. Render Dashboard → **New +** → **PostgreSQL**
2. Name: `scooter-rental-db`
3. Region: Web Service bilan bir xil
4. Instance Type: `Free`

5. Web Service Environment'ga qo'shing:
   ```env
   DATABASE_URL=postgres://...  # PostgreSQL URL
   ```

6. `database.py` da SQLite o'rniga PostgreSQL ishlatish

## 🔐 Xavfsizlik

### Production uchun:

1. **SECRET_KEY** ni yangilang:
   ```python
   import secrets
   print(secrets.token_urlsafe(32))
   ```

2. **HTTPS** ni tekshiring (Render avtomatik)

3. **Environment Variables** ni hech qachon commit qilmang

## 💰 Narxlar (2024)

| Plan | Narx | Xususiyatlar |
|------|------|--------------|
| **Free** | $0 | 750 soat/oy, 0.1 CPU, 512MB RAM |
| **Starter** | $7/mo | Cheksiz, 0.5 CPU, 512MB RAM |
| **Standard** | $25/mo | 1 CPU, 2GB RAM |

## 📈 Scale qilish

Ko'proq foydalanuvchilar uchun:

1. **Starter** yoki **Standard** planga o'tish
2. **Autoscaling** yoqish
3. **CDN** qo'shish (static fayllar uchun)
4. **PostgreSQL** ishlatish

## 🎉 Tayyor!

Sizning botingiz endi 24/7 ishlayapti!

**Bot URL:** `https://t.me/your_bot_username`

---

**Savollar?** README.md ni o'qing yoki issue oching!
