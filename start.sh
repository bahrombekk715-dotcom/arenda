#!/bin/bash

echo "🚀 Skuter Ijarasi Bot - Ishga tushirish"
echo "======================================"

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env fayli topilmadi!"
    echo "📝 .env.example dan nusxa oling:"
    echo "   cp .env.example .env"
    echo "   nano .env"
    exit 1
fi

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

echo "✅ Environment o'zgaruvchilari yuklandi"

# Check BOT_TOKEN
if [ -z "$BOT_TOKEN" ]; then
    echo "❌ BOT_TOKEN sozlanmagan!"
    exit 1
fi

echo "✅ Bot token topildi"

# Create data directory
mkdir -p data
echo "✅ Data papkasi yaratildi"

# Start both bot and webapp
echo ""
echo "🤖 Bot ishga tushmoqda..."
echo "🌐 Web app ishga tushmoqda..."
echo ""

python bot.py &
BOT_PID=$!

python webapp.py &
WEBAPP_PID=$!

echo "✅ Bot PID: $BOT_PID"
echo "✅ WebApp PID: $WEBAPP_PID"
echo ""
echo "📊 Bot va Web app ishlamoqda!"
echo "🛑 To'xtatish uchun: Ctrl+C"
echo ""

# Wait for both processes
wait $BOT_PID $WEBAPP_PID
