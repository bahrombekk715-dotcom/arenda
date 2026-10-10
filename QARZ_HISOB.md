# 💰 Qarz Hisob-Kitob Tizimi

## 📊 Matematik Formula

### Kunlik to'lov hisobi:
```
Kunlik to'lov = Haftalik to'lov ÷ 7
```

### Qarz summasi hisobi:
```
Qarz = Kechikkan kunlar × Kunlik to'lov
```

## 🧮 Hisoblash Misollari

### Misol 1: 500,000 so'm haftalik
```
Haftalik to'lov: 500,000 so'm
Kunlik to'lov: 500,000 ÷ 7 = 71,428.57 ≈ 71,429 so'm

Agar 1 kun kechiksa:
  Qarz = 1 × 71,429 = 71,429 so'm

Agar 5 kun kechiksa:
  Qarz = 5 × 71,429 = 357,145 so'm

Agar 10 kun kechiksa:
  Qarz = 10 × 71,429 = 714,290 so'm
```

### Misol 2: 300,000 so'm haftalik
```
Haftalik to'lov: 300,000 so'm
Kunlik to'lov: 300,000 ÷ 7 = 42,857.14 ≈ 42,857 so'm

Agar 3 kun kechiksa:
  Qarz = 3 × 42,857 = 128,571 so'm

Agar 7 kun kechiksa:
  Qarz = 7 × 42,857 = 300,000 so'm (1 haftalik)
```

### Misol 3: 700,000 so'm haftalik
```
Haftalik to'lov: 700,000 so'm
Kunlik to'lov: 700,000 ÷ 7 = 100,000 so'm

Agar 2 kun kechiksa:
  Qarz = 2 × 100,000 = 200,000 so'm

Agar 14 kun kechiksa:
  Qarz = 14 × 100,000 = 1,400,000 so'm (2 haftalik)
```

## 📅 Qachongacha pul yetadi?

### Hisoblash:
```
To'langan hafta soni = Jami to'langan ÷ Haftalik to'lov
Pul yetadigan sana = Boshlangan sana + To'langan hafta soni
```

### Misol:
```
Boshlangan sana: 01.10.2026
Haftalik to'lov: 500,000 so'm
Jami to'langan: 1,500,000 so'm

To'langan hafta: 1,500,000 ÷ 500,000 = 3 hafta
Pul yetadigan sana: 01.10.2026 + 21 kun = 22.10.2026

Agar bugun 25.10.2026 bo'lsa:
  Kechikkan kunlar: 25 - 22 = 3 kun
  Qarz: 3 × 71,429 = 214,287 so'm
```

## 🎨 Botdagi Ko'rinish

### ✅ Vaqtida to'langan (Yashil):
```
✅ Pulingiz yetadi: 15.11.2026
   Qolgan kunlar: 5 kun
   Keyingi to'lov: 15.11.2026
```

### ⏰ 3 kun va kamroq qolgan (Sariq):
```
⏰ Pulingiz yetadi: 12.10.2026
   Qolgan kunlar: 2 kun
   Keyingi to'lov: 12.10.2026
```

### 🚨 Kechikkan (Qizil):
```
🚨 TO'LOV KECHIKKAN!
   Kechikkan kunlar: 5 kun
   Qarz summasi: 357,145 so'm
   Har kuni 71,429 so'mdan qarz oshib bormoqda
```

## 💡 Qarz Oshishi

Har kechikkan kun uchun avtomatik qarz hisoblanadi va to'planib boradi:

```
1-kun:   71,429 so'm
2-kun:  142,858 so'm
3-kun:  214,287 so'm
4-kun:  285,716 so'm
5-kun:  357,145 so'm
...
7-kun:  500,000 so'm (1 haftalik to'lov)
14-kun: 1,000,000 so'm (2 haftalik to'lov)
```

## 🔄 To'lov Kiritilganda

Yangi to'lov kiritilganda:
1. Jami to'langan summa oshadi
2. Pul yetadigan sana qayta hisoblanadi
3. Qarz summasi qayta hisoblanadi (kamayadi yoki 0 ga tushadi)

### Misol:
```
Holat: 5 kun kechikkan, qarz 357,145 so'm
To'lov: 500,000 so'm kiritildi

Yangi holat:
  - Qarz to'landi (357,145 so'm)
  - Qolgan pul: 142,855 so'm
  - Yangi pul yetadigan sana: Bugun + 2 kun
```

## ⚙️ Kodda Qanday Ishlaydi?

```python
# 1. Kunlik to'lovni hisoblash
daily_rate = weekly_payment / 7.0

# 2. Kechikkan kunlarni topish
overdue_days = (hozir - pul_yetgan_sana).days

# 3. Qarzni hisoblash
debt_amount = overdue_days * daily_rate

# 4. Yaxlitlash (tiyinlarsiz)
debt_amount = round(debt_amount, 0)
```

---

**Eslatma:** Barcha hisob-kitoblar O'zbekiston vaqti (UTC+5) bo'yicha amalga oshiriladi.
