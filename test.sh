#!/bin/bash

echo "🧪 Skuter Ijarasi Bot - Test"
echo "=============================="
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 topilmadi!"
    exit 1
fi
echo "✅ Python3 topildi: $(python3 --version)"

# Check .env
if [ ! -f .env ]; then
    echo "❌ .env fayli yo'q!"
    echo "💡 Birinchi marta? Setup.md ni o'qing"
    exit 1
fi
echo "✅ .env fayli mavjud"

# Check BOT_TOKEN
source .env
if [ -z "$BOT_TOKEN" ]; then
    echo "❌ BOT_TOKEN sozlanmagan!"
    exit 1
fi
echo "✅ BOT_TOKEN sozlangan"

# Check ADMIN_IDS
if [ -z "$ADMIN_IDS" ]; then
    echo "❌ ADMIN_IDS sozlanmagan!"
    exit 1
fi
echo "✅ ADMIN_IDS sozlangan"

# Install dependencies
echo ""
echo "📦 Dependencies o'rnatilmoqda..."
pip install -q -r requirements.txt
echo "✅ Dependencies o'rnatildi"

# Create data directory
mkdir -p data
echo "✅ Data papkasi yaratildi"

# Seed database
echo ""
echo "🌱 Test ma'lumotlar qo'shilsinmi? (5 ta skuter)"
read -p "Qo'shish uchun 'y' bosing: " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python3 seed_data.py
fi

echo ""
echo "✅ Hammasi tayyor!"
echo ""
echo "🚀 Botni ishga tushirish uchun:"
echo "   ./start.sh"
echo ""
echo "📖 Batafsil ma'lumot:"
echo "   - README.md    - Umumiy ma'lumot"
echo "   - SETUP.md     - Sozlash qo'llanmasi"
echo "   - DEPLOY.md    - Deploy qilish"
echo ""
